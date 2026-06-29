from dataclasses import dataclass, field
from io import BytesIO
import logging
import time
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException
from PIL import Image, ImageDraw, ImageFont, ImageStat

from app.config import get_settings
from app.services.llm import LlmContentGenerator, LlmGenerationError
from app.tasks.generators.pdf import PdfGenerationAgent
from app.tasks.generators.types import (
    GenerationStep,
    MaterialBlock,
    MaterialPage,
    MaterialPlan,
    PdfContentDraft,
    PdfGenerationInput,
    TokenUsage,
)


logger = logging.getLogger(__name__)


@dataclass
class ImagePdfGenerationResult:
    title: str
    summary: str
    file_path: str
    url: str
    outline: list[str]
    image_paths: list[str]
    page_count: int
    generation_source: str = "llm-plan"
    model: str | None = None
    token_usage: TokenUsage = field(default_factory=TokenUsage)
    generation_error: str | None = None
    request_id: str = ""
    generation_steps: list[GenerationStep] = field(default_factory=list)


class ImagePdfGenerationAgent:
    page_width = 1240
    page_height = 1754
    margin = 86

    def __init__(
        self,
        file_root: str | Path | None = None,
        base_url: str | None = None,
        content_generator: LlmContentGenerator | None = None,
    ):
        settings = get_settings()
        self.settings = settings
        self.file_root = Path(file_root or settings.local_file_root)
        self.base_url = (base_url or settings.local_file_base_url).rstrip("/")
        self.content_generator = content_generator or LlmContentGenerator()
        self._request_id = ""
        self._steps: list[GenerationStep] = []

    def generate(self, payload: PdfGenerationInput, page_count: int = 2) -> ImagePdfGenerationResult:
        self._request_id = uuid4().hex
        if hasattr(self.content_generator, "set_trace_context"):
            self.content_generator.set_trace_context(self._request_id, "image_pdf_generation")
        self._steps = []
        started_at = time.perf_counter()
        requested_page_count = max(1, int(page_count or 2))
        max_page_count = max(1, int(self.settings.ai_image_pdf_max_pages or 12))
        target_page_count = min(requested_page_count, max_page_count)
        self._record_step(
            "start",
            "ok",
            "开始生成连续图片PDF",
            metadata={
                "title": payload.title,
                "page_count": target_page_count,
                "requested_page_count": requested_page_count,
                "max_page_count": max_page_count,
            },
        )

        if not payload.title.strip() or not payload.summary.strip():
            self._record_step("validate_input", "failed", "标题和简介不能为空")
            raise HTTPException(status_code=400, detail="title and summary are required")
        self._record_step("validate_input", "ok", "输入校验通过")

        reference, reference_error, reference_images = self._timed_step(
            "reference_context",
            "读取参考资料文字和参考预览",
            lambda: self._reference_context(payload),
        )
        plan, source, model, usage, generation_error = self._timed_step(
            "llm_material_plan",
            "生成连续资料页面计划",
            lambda: self._material_plan(payload, reference, target_page_count),
        )
        generation_error = self._merge_error(reference_error, generation_error)
        image_source = "ai-pages" if source.startswith("llm") else source

        image_paths: list[str] = []
        for index, page in enumerate(plan.pages, start=1):
            relative_image = self._timed_step(
                f"generate_page_{index}",
                f"渲染第{index}页连续资料图片",
                lambda page=page, index=index: self._generate_or_render_page(plan, page, target_page_count, index, reference_images, usage),
            )
            self._timed_step(
                f"image_quality_page_{index}",
                f"校验第{index}页图片质量",
                lambda path=relative_image: self._verify_image(path),
            )
            image_paths.append(relative_image)

        relative_pdf = f"materials/ai-generated/{uuid4().hex}.pdf"
        target_pdf = self.file_root / relative_pdf
        self._timed_step("compose_pdf", "将连续页面图片合成为PDF", lambda: self._compose_pdf(image_paths, target_pdf))
        self._timed_step("verify_pdf", "校验生成PDF文件", lambda: self._verify_pdf(target_pdf))
        self._record_step(
            "finish",
            "ok",
            "连续图片PDF生成完成",
            duration_ms=int((time.perf_counter() - started_at) * 1000),
            metadata={
                "file_path": relative_pdf,
                "image_count": len(image_paths),
                "model": model,
                "image_source": image_source,
                "material_type": plan.material_type,
            },
        )

        return ImagePdfGenerationResult(
            title=plan.title,
            summary=plan.summary,
            file_path=relative_pdf,
            url=f"{self.base_url}/{relative_pdf}",
            outline=plan.outline,
            image_paths=image_paths,
            page_count=len(image_paths),
            generation_source=image_source,
            model=model,
            token_usage=usage,
            generation_error=generation_error,
            request_id=self._request_id,
            generation_steps=self._steps,
        )

    @staticmethod
    def _merge_error(*errors: str | None) -> str | None:
        clean = [error for error in errors if error]
        return "; ".join(clean) if clean else None

    def _timed_step(self, step: str, message: str, action):
        started_at = time.perf_counter()
        try:
            result = action()
        except Exception as exc:
            self._record_step(step, "failed", f"{message}失败：{exc}", duration_ms=int((time.perf_counter() - started_at) * 1000))
            raise
        self._record_step(step, "ok", message, duration_ms=int((time.perf_counter() - started_at) * 1000))
        return result

    def _record_step(self, step: str, status: str, message: str, duration_ms: int = 0, metadata: dict | None = None) -> None:
        self._steps.append(GenerationStep(step=step, status=status, message=message, duration_ms=duration_ms, metadata=metadata or {}))
        logger.info(
            "image_pdf_generation request_id=%s step=%s status=%s duration_ms=%s message=%s metadata=%s",
            self._request_id,
            step,
            status,
            duration_ms,
            message,
            metadata or {},
        )

    def _material_plan(self, payload: PdfGenerationInput, reference: str, page_count: int) -> tuple[MaterialPlan, str, str | None, TokenUsage, str | None]:
        try:
            generator = getattr(self.content_generator, "generate_material_plan", None)
            result = generator(payload, reference, page_count) if callable(generator) else None
        except LlmGenerationError as exc:
            result = None
            error = str(exc)
        else:
            error = None
        if result is not None:
            return self._normalize_plan(result.plan, payload, reference, page_count), "llm-plan", result.model, result.usage, None

        draft, source, model, usage, draft_error = self._content_draft(payload, reference)
        return self._fallback_plan(payload, draft, page_count), source, model, usage, self._merge_error(error, draft_error)

    def _content_draft(self, payload: PdfGenerationInput, reference: str) -> tuple[PdfContentDraft, str, str | None, TokenUsage, str | None]:
        try:
            result = self.content_generator.generate_pdf_content(payload, reference, None, None)
        except LlmGenerationError as exc:
            result = None
            error = str(exc)
        else:
            error = None
        helper = PdfGenerationAgent(content_generator=self.content_generator)
        if result is not None:
            return helper._complete_draft(result.draft, payload, reference), "llm-plan", result.model, result.usage, None
        return helper._template_draft(payload, reference), "template-plan", None, TokenUsage(), error

    def _normalize_plan(self, plan: MaterialPlan, payload: PdfGenerationInput, reference: str, page_count: int) -> MaterialPlan:
        fallback = self._fallback_plan(
            payload,
            PdfContentDraft(
                title=plan.title or payload.title,
                summary=plan.summary or payload.summary,
                outline=plan.outline or [],
                practice_plan=[],
                parent_tips=[],
                next_action=payload.next_action or "",
                reference_summary=reference[:180] if reference else "",
            ),
            page_count,
        )
        pages: list[MaterialPage] = []
        for index in range(page_count):
            source = plan.pages[index] if index < len(plan.pages) else fallback.pages[index]
            pages.append(
                MaterialPage(
                    page_no=index + 1,
                    section_title=source.section_title or fallback.pages[index].section_title,
                    blocks=source.blocks or fallback.pages[index].blocks,
                    continued_from=source.continued_from,
                    continued_to=source.continued_to,
                )
            )
        return MaterialPlan(
            material_type=plan.material_type or fallback.material_type,
            title=plan.title or fallback.title,
            summary=plan.summary or fallback.summary,
            audience=plan.audience or fallback.audience,
            pages=pages,
            outline=plan.outline or fallback.outline,
            global_style=plan.global_style or fallback.global_style,
        )

    def _fallback_plan(self, payload: PdfGenerationInput, draft: PdfContentDraft, page_count: int) -> MaterialPlan:
        material_type = self._infer_material_type(payload)
        outline = [item for item in (draft.outline or [draft.summary]) if item]
        pages: list[MaterialPage] = []
        question_no = 1
        for page_no in range(1, page_count + 1):
            blocks: list[MaterialBlock] = []
            if material_type in {"exam_paper", "worksheet"}:
                section = self._section_title_for_page(page_no, page_count)
                questions = []
                for _ in range(4):
                    questions.append(f"{question_no}. {self._question_text(payload, question_no)}")
                    question_no += 1
                blocks.append(MaterialBlock(type="question", title=section, items=questions, answer_space=2))
            elif material_type == "checklist":
                section = f"第{page_no}页 打卡任务"
                source_items = (draft.practice_plan or outline or [draft.summary])[:4]
                blocks.append(MaterialBlock(type="checklist", title=section, items=[f"任务{(page_no - 1) * 4 + i}：{item}" for i, item in enumerate(source_items, start=1)]))
            else:
                section = self._generic_section_title(page_no, page_count)
                blocks.append(MaterialBlock(type="paragraph", title=section, text=draft.summary))
                blocks.append(MaterialBlock(type="list", title="关键内容", items=(outline + draft.practice_plan + draft.parent_tips)[:6]))
                if draft.next_action and page_no == page_count:
                    blocks.append(MaterialBlock(type="note", title="下一步行动", text=draft.next_action))
            pages.append(
                MaterialPage(
                    page_no=page_no,
                    section_title=section,
                    blocks=blocks,
                    continued_from=page_no - 1 if page_no > 1 else None,
                    continued_to=page_no + 1 if page_no < page_count else None,
                )
            )
        return MaterialPlan(
            material_type=material_type,
            title=draft.title,
            summary=draft.summary,
            audience=" / ".join(item for item in [payload.grade, payload.subject] if item) or "小学低年级",
            pages=pages,
            outline=outline[:6],
            global_style="A4连续资料",
        )

    def _reference_context(self, payload: PdfGenerationInput) -> tuple[str, str | None, list[str]]:
        helper = PdfGenerationAgent(file_root=self.file_root, base_url=self.base_url, content_generator=self.content_generator)
        try:
            profile = helper._reference_profile(payload)
            parts = [payload.reference_text.strip()] if payload.reference_text and payload.reference_text.strip() else []
            if profile and profile.text:
                parts.append(profile.text)
            images = []
            if payload.match_reference_style and profile and profile.preview_path:
                images.append(profile.preview_path)
            return "\n".join(parts), None, images
        except Exception as exc:
            return payload.reference_text or "", f"Reference read failed: {exc}", []

    def _reference_text(self, payload: PdfGenerationInput) -> tuple[str, str | None]:
        text, error, _ = self._reference_context(payload)
        return text, error

    def _generate_or_render_page(self, plan: MaterialPlan, page: MaterialPage, page_count: int, page_index: int, reference_images: list[str], usage: TokenUsage) -> str:
        prompt = self._page_image_prompt(plan, page, page_count)
        image_generator = getattr(self.content_generator, "generate_image_bytes", None)
        if not callable(image_generator):
            self._record_step(f"ai_page_fallback_{page_index}", "ok", "AI page generation is unavailable, fallback to template.", metadata={"page_no": page_index})
            return self._render_and_save_page(plan, page, page_count, page_index)
        try:
            if reference_images and hasattr(self.content_generator, "generate_image_with_reference_bytes"):
                image_bytes, image_usage = self.content_generator.generate_image_with_reference_bytes(prompt, reference_images, size=self._image_size(plan))
            else:
                image_bytes, image_usage = image_generator(prompt, size=self._image_size(plan))
        except LlmGenerationError as exc:
            self._record_step(f"ai_page_fallback_{page_index}", "ok", f"AI页面生成失败，回退模板：{exc}", metadata={"page_no": page_index})
            return self._render_and_save_page(plan, page, page_count, page_index)
        usage.add(image_usage)
        if not image_bytes:
            self._record_step(f"ai_page_fallback_{page_index}", "ok", "AI页面生成未返回图片，回退模板", metadata={"page_no": page_index})
            return self._render_and_save_page(plan, page, page_count, page_index)
        return self._save_image(image_bytes, page_index)

    def _render_and_save_page(self, plan: MaterialPlan, page: MaterialPage, page_count: int, page_index: int) -> str:
        image = self._render_page(plan, page, page_count)
        relative = f"materials/ai-generated/images/{uuid4().hex}-page-{page_index}.png"
        target = self.file_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        image.save(target, format="PNG")
        return relative

    def _page_image_prompt(self, plan: MaterialPlan, page: MaterialPage, page_count: int) -> str:
        previous_text = f"上一页是第 {page.continued_from} 页，本页必须自然延续。" if page.continued_from else "本页是第一页，建立整份资料的统一版式。"
        next_text = f"下一页是第 {page.continued_to} 页，本页末尾要保持可延续。" if page.continued_to else "本页是最后一页，需要自然收束。"
        return (
            "请生成一张高清中文教育资料页面图片。\n"
            "这是同一份连续多页资料中的一页，必须严格保持整份资料的连续性。\n"
            "全局规则：\n"
            f"- 资料标题：{plan.title}\n"
            f"- 资料类型：{plan.material_type}\n"
            f"- 适用对象：{plan.audience}\n"
            f"- 页面：第 {page.page_no} 页 / 共 {page_count} 页\n"
            "- 所有页面使用相同页眉、边距、字体风格、配色、题型排版和页脚。\n"
            "- 题号、任务编号、页码必须按本页内容严格绘制，不要自行新增或重排。\n"
            "- 不要新增题目，不要删减题目，不要编造机构、老师、水印或统计数据。\n"
            "- 中文必须清晰可读，不要乱码。\n"
            f"- {previous_text}\n"
            f"- {next_text}\n\n"
            f"本页栏目：{page.section_title}\n"
            f"本页必须包含以下内容：\n{self._page_content_text(page)}"
        )

    @staticmethod
    def _page_content_text(page: MaterialPage) -> str:
        lines = []
        for block in page.blocks:
            if block.title:
                lines.append(f"【{block.title}】")
            if block.text:
                lines.append(block.text)
            for item in block.items or []:
                lines.append(f"- {item}")
            for option in block.options or []:
                lines.append(f"  {option}")
            if block.answer_space:
                lines.append(f"答题/书写空间：{block.answer_space} 行")
        return "\n".join(lines)

    @staticmethod
    def _image_size(plan: MaterialPlan) -> str:
        return "1536x1024" if plan.material_type == "exam_paper" else "1024x1536"

    def _render_page(self, plan: MaterialPlan, page: MaterialPage, page_count: int) -> Image.Image:
        image = Image.new("RGB", (self.page_width, self.page_height), "#ffffff")
        draw = ImageDraw.Draw(image)
        fonts = self._fonts()
        accent = self._accent_color(plan.material_type)
        draw.rectangle((0, 0, self.page_width, 28), fill=accent)
        draw.text((self.margin, 56), plan.title, font=fonts["title"], fill="#111827")
        meta = f"{plan.audience}  |  {plan.material_type.replace('_', ' ')}"
        draw.text((self.margin, 116), meta, font=fonts["small"], fill="#64748b")
        draw.text((self.page_width - self.margin - 120, 116), f"{page.page_no}/{page_count}", font=fonts["small"], fill="#64748b")
        draw.line((self.margin, 154, self.page_width - self.margin, 154), fill="#d7dee8", width=2)

        y = 188
        y = self._draw_section_title(draw, page.section_title, self.margin, y, fonts, accent)
        if page.continued_from:
            y = self._draw_text(draw, f"续第 {page.continued_from} 页", self.margin, y, self.page_width - 2 * self.margin, fonts["small"], "#64748b") + 12
        overflow = False
        for block in page.blocks:
            y = self._draw_block(draw, block, self.margin, y, self.page_width - 2 * self.margin, fonts, accent)
            y += 18
            if y > self.page_height - 150:
                overflow = True
                break
        if page.continued_to:
            draw.text((self.margin, self.page_height - 104), f"下接第 {page.continued_to} 页", font=fonts["small"], fill="#64748b")
        if overflow:
            self._record_step(f"render_warning_page_{page.page_no}", "ok", "内容超出当前页，已截断", metadata={"page_no": page.page_no})
            draw.text((self.margin, self.page_height - 130), "本页内容较多，已按固定页数截断展示。", font=fonts["small"], fill="#b45309")
        footer = f"第 {page.page_no} / {page_count} 页"
        draw.line((self.margin, self.page_height - 72, self.page_width - self.margin, self.page_height - 72), fill="#e2e8f0", width=1)
        draw.text((self.page_width // 2 - 42, self.page_height - 50), footer, font=fonts["small"], fill="#64748b")
        return image

    def _draw_block(self, draw: ImageDraw.ImageDraw, block: MaterialBlock, x: int, y: int, width: int, fonts: dict[str, ImageFont.FreeTypeFont], accent: str) -> int:
        if block.title:
            y = self._draw_text(draw, block.title, x, y, width, fonts["subtitle"], accent) + 10
        if block.text:
            y = self._draw_text(draw, block.text, x, y, width, fonts["body"], "#1f2937") + 10
        items = block.items or []
        if block.type in {"question", "checklist", "list", "table"}:
            for item in items:
                y = self._draw_text(draw, item, x + 8, y, width - 8, fonts["body"], "#111827")
                if block.options:
                    y += 4
                    for option in block.options[:4]:
                        y = self._draw_text(draw, option, x + 38, y, width - 38, fonts["small"], "#374151")
                for _ in range(max(0, block.answer_space)):
                    y += 20
                    draw.line((x + 34, y, x + width, y), fill="#cbd5e1", width=1)
                y += 18
        elif items:
            for item in items:
                y = self._draw_text(draw, f"• {item}", x + 8, y, width - 8, fonts["body"], "#111827") + 8
        return y

    def _draw_section_title(self, draw: ImageDraw.ImageDraw, text: str, x: int, y: int, fonts: dict[str, ImageFont.FreeTypeFont], accent: str) -> int:
        draw.rounded_rectangle((x, y, self.page_width - self.margin, y + 48), radius=10, fill="#f8fafc", outline="#dbe4ef", width=2)
        draw.rectangle((x, y, x + 10, y + 48), fill=accent)
        draw.text((x + 24, y + 9), text, font=fonts["subtitle"], fill="#111827")
        return y + 72

    def _draw_text(self, draw: ImageDraw.ImageDraw, text: str, x: int, y: int, width: int, font: ImageFont.FreeTypeFont, fill: str) -> int:
        for line in self._wrap_text(draw, str(text), font, width):
            draw.text((x, y), line, font=font, fill=fill)
            y += int(font.size * 1.45)
        return y

    @staticmethod
    def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, width: int) -> list[str]:
        lines: list[str] = []
        for raw in str(text).splitlines() or [""]:
            current = ""
            for char in raw:
                test = current + char
                bbox = draw.textbbox((0, 0), test, font=font)
                if bbox[2] - bbox[0] <= width:
                    current = test
                else:
                    if current:
                        lines.append(current)
                    current = char
            if current:
                lines.append(current)
        return lines or [""]

    @staticmethod
    def _accent_color(material_type: str) -> str:
        colors = {
            "exam_paper": "#2563eb",
            "worksheet": "#0f766e",
            "knowledge_card": "#7c3aed",
            "parent_guide": "#16a34a",
            "checklist": "#ea580c",
            "reference_material": "#475569",
        }
        return colors.get(material_type, "#0f766e")

    @staticmethod
    def _font_path() -> str | None:
        candidates = [
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/simsun.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        ]
        for path in candidates:
            if Path(path).exists():
                return path
        return None

    def _fonts(self):
        font_path = self._font_path()
        if not font_path:
            default = ImageFont.load_default()
            return {"title": default, "subtitle": default, "body": default, "small": default}
        return {
            "title": ImageFont.truetype(font_path, 42),
            "subtitle": ImageFont.truetype(font_path, 28),
            "body": ImageFont.truetype(font_path, 24),
            "small": ImageFont.truetype(font_path, 20),
        }

    @staticmethod
    def _infer_material_type(payload: PdfGenerationInput) -> str:
        text = " ".join(str(value or "") for value in [payload.title, payload.summary, payload.subject, payload.problem, payload.layout_type]).lower()
        if any(keyword in text for keyword in ["试卷", "真题", "考试", "exam", "paper"]):
            return "exam_paper"
        if any(keyword in text for keyword in ["练习", "worksheet", "数学", "语文", "英语", "math"]):
            return "worksheet"
        if any(keyword in text for keyword in ["打卡", "清单", "checklist"]):
            return "checklist"
        if any(keyword in text for keyword in ["知识", "速记", "卡"]):
            return "knowledge_card"
        return "parent_guide"

    @staticmethod
    def _section_title_for_page(page_no: int, page_count: int) -> str:
        if page_no == 1:
            return "一、基础题"
        if page_no == page_count:
            return "三、综合应用"
        return "二、能力提升"

    @staticmethod
    def _generic_section_title(page_no: int, page_count: int) -> str:
        if page_no == 1:
            return "核心判断"
        if page_no == page_count:
            return "行动复盘"
        return "连续练习"

    @staticmethod
    def _question_text(payload: PdfGenerationInput, number: int) -> str:
        subject = payload.subject or "学习"
        problem = payload.problem or "能力提升"
        if "数学" in subject or "math" in subject.lower():
            return f"完成第{number}题，写出计算过程。"
        return f"围绕{subject}{problem}完成第{number}个小任务。"

    def _save_image(self, image_bytes: bytes, page_index: int) -> str:
        relative = f"materials/ai-generated/images/{uuid4().hex}-page-{page_index}.png"
        target = self.file_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(BytesIO(image_bytes)) as image:
            image.convert("RGB").save(target, format="PNG")
        return relative

    def _verify_image(self, relative_path: str) -> None:
        target = self.file_root / relative_path
        if not target.exists() or target.stat().st_size == 0:
            raise HTTPException(status_code=500, detail="generated image is missing")
        with Image.open(target).convert("RGB") as image:
            width, height = image.size
            if width < 256 or height < 256:
                raise HTTPException(status_code=500, detail="generated image is too small")
            extrema = ImageStat.Stat(image.resize((32, 32))).extrema
            if all(max(channel) - min(channel) < 8 for channel in extrema):
                raise HTTPException(status_code=500, detail="generated image looks blank")

    def _compose_pdf(self, image_paths: list[str], target: Path) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        images = []
        try:
            for relative in image_paths:
                image = Image.open(self.file_root / relative).convert("RGB")
                images.append(image)
            images[0].save(target, "PDF", save_all=True, append_images=images[1:], resolution=150.0)
        finally:
            for image in images:
                image.close()

    @staticmethod
    def _verify_pdf(target: Path) -> None:
        if not target.exists() or target.stat().st_size == 0:
            raise HTTPException(status_code=500, detail="PDF generation failed")
        if not target.read_bytes().startswith(b"%PDF"):
            raise HTTPException(status_code=500, detail="Generated file is not a PDF")
