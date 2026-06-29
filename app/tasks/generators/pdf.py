from dataclasses import dataclass, field
from pathlib import Path
import logging
import re
import shutil
import subprocess
import time
from uuid import uuid4

from fastapi import HTTPException
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.config import get_settings
from app.services.llm import LlmContentGenerator, LlmGenerationError
from app.tasks.generators.types import GenerationStep, PdfContentDraft, PdfGenerationInput, PdfReferenceProfile, ReferenceAnalysis, TokenUsage


logger = logging.getLogger(__name__)


@dataclass
class PdfQualityReport:
    checked: bool
    page_count: int | None = None
    preview_path: str | None = None
    reference_preview_path: str | None = None
    generated_preview_size: tuple[int, int] | None = None
    reference_preview_size: tuple[int, int] | None = None
    warnings: list[str] = field(default_factory=list)


@dataclass
class PdfGenerationResult:
    title: str
    summary: str
    file_path: str
    url: str
    outline: list[str]
    quality: PdfQualityReport
    generation_source: str = "template"
    model: str | None = None
    token_usage: TokenUsage = field(default_factory=TokenUsage)
    generation_error: str | None = None
    request_id: str = ""
    generation_steps: list[GenerationStep] = field(default_factory=list)


class PdfGenerationAgent:
    def __init__(
        self,
        file_root: str | Path | None = None,
        base_url: str | None = None,
        render_root: str | Path = "tmp/pdfs/render",
        verify_render: bool = True,
        content_generator: LlmContentGenerator | None = None,
    ):
        settings = get_settings()
        self.file_root = Path(file_root or settings.local_file_root)
        self.base_url = (base_url or settings.local_file_base_url).rstrip("/")
        self.render_root = Path(render_root)
        self.verify_render = verify_render
        self.content_generator = content_generator or LlmContentGenerator()
        self._request_id = ""
        self._steps: list[GenerationStep] = []

    def generate(self, payload: PdfGenerationInput) -> PdfGenerationResult:
        self._request_id = uuid4().hex
        if hasattr(self.content_generator, "set_trace_context"):
            self.content_generator.set_trace_context(self._request_id, "pdf_generation")
        self._steps = []
        started_at = time.perf_counter()
        self._record_step("start", "ok", "开始生成PDF", metadata={"title": payload.title, "match_reference_style": payload.match_reference_style})
        self._timed_step("setup_fonts", "注册中文字体", self._setup_fonts)

        if not payload.title.strip() or not payload.summary.strip():
            self._record_step("validate_input", "failed", "标题和简介不能为空")
            raise HTTPException(status_code=400, detail="title and summary are required")
        self._record_step("validate_input", "ok", "输入校验通过")

        reference_profile = self._timed_step("reference_profile", "渲染并分析参考PDF结构", lambda: self._reference_profile(payload))
        reference = self._timed_step("reference_text", "读取参考资料文字", lambda: self._reference_text(payload, reference_profile))
        reference_analysis, reference_usage, reference_error = self._timed_step(
            "llm_reference_analysis",
            "调用大模型分析参考PDF内容与风格",
            lambda: self._reference_analysis(payload, reference, reference_profile),
        )
        draft, source, model, token_usage, generation_error = self._timed_step(
            "llm_content",
            "调用大模型生成结构化内容",
            lambda: self._content_draft(payload, reference, reference_profile, reference_analysis),
        )
        token_usage.add(reference_usage)
        generation_error = self._merge_error(reference_error, generation_error)

        relative_path = f"materials/ai-generated/{uuid4().hex}.pdf"
        target = self.file_root / relative_path
        self._timed_step("render_pdf", "根据版型渲染PDF", lambda: self._write_pdf(target, payload, draft, reference_profile))
        quality = self._timed_step("verify_pdf", "使用pdfinfo/pdftoppm渲染校验PDF", lambda: self._verify_pdf(target))
        self._timed_step("visual_review", "检查生成PDF渲染图并关联参考预览", lambda: self._visual_review(quality, reference_profile))
        self._record_step(
            "finish",
            "ok",
            "PDF生成完成",
            duration_ms=int((time.perf_counter() - started_at) * 1000),
            metadata={"file_path": relative_path, "generation_source": source, "model": model, "layout_type": reference_profile.layout_type if reference_profile else None},
        )
        return PdfGenerationResult(
            title=draft.title,
            summary=draft.summary,
            file_path=relative_path,
            url=f"{self.base_url}/{relative_path}",
            outline=draft.outline,
            quality=quality,
            generation_source=source,
            model=model,
            token_usage=token_usage,
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
            "pdf_generation request_id=%s step=%s status=%s duration_ms=%s message=%s metadata=%s",
            self._request_id,
            step,
            status,
            duration_ms,
            message,
            metadata or {},
        )

    def _reference_analysis(
        self,
        payload: PdfGenerationInput,
        reference: str,
        reference_profile: PdfReferenceProfile | None,
    ) -> tuple[ReferenceAnalysis | None, TokenUsage, str | None]:
        if not payload.match_reference_style:
            return None, TokenUsage(), None
        if not reference and reference_profile is None:
            return None, TokenUsage(), None
        try:
            result = self.content_generator.analyze_reference_pdf(payload, reference, reference_profile)
        except LlmGenerationError as exc:
            return None, TokenUsage(), f"Reference analysis failed: {exc}"
        if result is None:
            return None, TokenUsage(), None
        return result.analysis, result.usage, None

    def _content_draft(
        self,
        payload: PdfGenerationInput,
        reference: str,
        reference_profile: PdfReferenceProfile | None,
        reference_analysis: ReferenceAnalysis | None,
    ) -> tuple[PdfContentDraft, str, str | None, TokenUsage, str | None]:
        try:
            result = self.content_generator.generate_pdf_content(payload, reference, reference_profile, reference_analysis)
        except LlmGenerationError as exc:
            result = None
            error = str(exc)
        else:
            error = None
        if result is not None:
            return self._complete_draft(result.draft, payload, reference), "llm", result.model, result.usage, None
        return self._template_draft(payload, reference), "template", None, TokenUsage(), error

    def _write_pdf(self, target: Path, payload: PdfGenerationInput, draft: PdfContentDraft, reference_profile: PdfReferenceProfile | None = None) -> None:
        self._write_default_pdf(target, payload, draft, reference_profile)

    def _write_default_pdf(self, target: Path, payload: PdfGenerationInput, draft: PdfContentDraft, reference_profile: PdfReferenceProfile | None = None) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        styles = self._styles()
        doc = SimpleDocTemplate(
            str(target),
            pagesize=self._page_size(reference_profile),
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=18 * mm,
            bottomMargin=16 * mm,
            title=draft.title,
        )
        story = [
            Paragraph(draft.title, styles["Title"]),
            Spacer(1, 7 * mm),
            Paragraph("适用对象", styles["Section"]),
            self._audience_table(payload, styles),
            Spacer(1, 5 * mm),
            Paragraph("内容简介", styles["Section"]),
            Paragraph(draft.summary, styles["Body"]),
            Spacer(1, 5 * mm),
            Paragraph("核心要点", styles["Section"]),
            self._bullet_list(draft.outline, styles),
            Spacer(1, 5 * mm),
            Paragraph("7天练习计划", styles["Section"]),
            self._bullet_list(draft.practice_plan, styles),
            Spacer(1, 5 * mm),
            Paragraph("家长陪伴建议", styles["Section"]),
            self._bullet_list(draft.parent_tips, styles),
        ]
        doc.build(story, onFirstPage=self._footer, onLaterPages=self._footer)

    def _verify_pdf(self, target: Path) -> PdfQualityReport:
        if not target.exists() or target.stat().st_size == 0:
            raise HTTPException(status_code=500, detail="PDF generation failed")
        if not target.read_bytes().startswith(b"%PDF"):
            raise HTTPException(status_code=500, detail="Generated file is not a PDF")

        report = PdfQualityReport(checked=False)
        pdfinfo = shutil.which("pdfinfo")
        if pdfinfo:
            result = subprocess.run([pdfinfo, str(target)], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15, check=False)
            if result.returncode != 0:
                report.warnings.append("pdfinfo failed; used pypdf metadata fallback")
                report.page_count = self._read_pdf_page_count(target)
            else:
                report.page_count = self._parse_page_count(result.stdout)
            if not report.page_count:
                raise HTTPException(status_code=500, detail="PDF page count check failed")
            report.checked = True
        else:
            report.page_count = self._read_pdf_page_count(target)
            if report.page_count:
                report.checked = True
                report.warnings.append("pdfinfo is unavailable; used pypdf metadata fallback")
            else:
                report.warnings.append("pdfinfo is unavailable; skipped metadata check")

        pdftoppm = shutil.which("pdftoppm")
        if self.verify_render and pdftoppm:
            self.render_root.mkdir(parents=True, exist_ok=True)
            preview_prefix = self.render_root / f"{target.stem}-preview"
            result = subprocess.run([pdftoppm, "-png", "-f", "1", "-singlefile", str(target), str(preview_prefix)], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30, check=False)
            if result.returncode != 0:
                report.warnings.append("pdftoppm failed; skipped render preview")
            else:
                preview = preview_prefix.with_suffix(".png")
                if not preview.exists() or preview.stat().st_size == 0:
                    report.warnings.append("pdftoppm produced no preview; skipped render preview")
                else:
                    report.preview_path = str(preview)
        elif self.verify_render:
            report.warnings.append("pdftoppm is unavailable; skipped render check")
        return report

    def _visual_review(self, report: PdfQualityReport, reference_profile: PdfReferenceProfile | None) -> None:
        if reference_profile and reference_profile.preview_path:
            report.reference_preview_path = reference_profile.preview_path
            report.reference_preview_size = self._image_size(Path(reference_profile.preview_path))
        if report.preview_path:
            preview = Path(report.preview_path)
            report.generated_preview_size = self._image_size(preview)
            if preview.stat().st_size < 1500:
                report.warnings.append("generated preview is unexpectedly small")
            if self._looks_blank(preview):
                raise HTTPException(status_code=500, detail="PDF visual review failed: rendered page looks blank")
        elif self.verify_render:
            report.warnings.append("generated preview is unavailable; visual review skipped")

    @staticmethod
    def _image_size(path: Path) -> tuple[int, int] | None:
        if not path.exists():
            return None
        try:
            from PIL import Image as PILImage

            with PILImage.open(path) as image:
                return image.size
        except Exception:
            return None

    @staticmethod
    def _looks_blank(path: Path) -> bool:
        try:
            from PIL import Image as PILImage

            with PILImage.open(path).convert("L") as image:
                values = list(image.resize((32, 32)).tobytes())
        except Exception:
            return False
        return bool(values) and max(values) - min(values) < 8

    @staticmethod
    def _parse_page_count(output: str) -> int | None:
        for line in output.splitlines():
            if line.startswith("Pages:"):
                value = line.split(":", 1)[1].strip()
                return int(value) if value.isdigit() else None
        return None

    @staticmethod
    def _read_pdf_page_count(target: Path) -> int | None:
        try:
            from pypdf import PdfReader

            return len(PdfReader(str(target)).pages)
        except Exception:
            return None

    def _template_draft(self, payload: PdfGenerationInput, reference: str) -> PdfContentDraft:
        return PdfContentDraft(
            title=payload.title.strip(),
            summary=payload.summary.strip(),
            outline=self._outline(payload),
            practice_plan=self._practice_plan(payload),
            parent_tips=self._parent_tips(payload),
            next_action=payload.next_action or "完成一次5分钟测评，获得更匹配的提升建议。",
            reference_summary=self._trim(reference, 700) if reference else "",
        )

    def _complete_draft(self, draft: PdfContentDraft, payload: PdfGenerationInput, reference: str) -> PdfContentDraft:
        fallback = self._template_draft(payload, reference)
        return PdfContentDraft(
            title=draft.title or fallback.title,
            summary=draft.summary or fallback.summary,
            outline=draft.outline or fallback.outline,
            practice_plan=draft.practice_plan or fallback.practice_plan,
            parent_tips=draft.parent_tips or fallback.parent_tips,
            next_action=draft.next_action or fallback.next_action,
            reference_summary=draft.reference_summary or fallback.reference_summary,
            image_prompt=draft.image_prompt or fallback.image_prompt,
        )

    @staticmethod
    def _outline(payload: PdfGenerationInput) -> list[str]:
        subject = payload.subject or "学习"
        problem = payload.problem or "当前问题"
        grade = payload.grade or "当前阶段"
        return [
            f"判断{grade}孩子在{subject}{problem}上的真实水平",
            "拆解每天10分钟可执行的家庭练习方法",
            "安排7天循序渐进的训练任务",
            "提示家长陪练中的常见误区和调整方式",
            "引导完成测评或训练营，形成后续跟进",
        ]

    @staticmethod
    def _practice_plan(payload: PdfGenerationInput) -> list[str]:
        problem = payload.problem or "目标能力"
        return [
            f"第1天：轻量摸底，确认{problem}的主要卡点。",
            "第2-3天：每天固定10分钟，先完成一个小任务再反馈。",
            "第4-5天：加入计时或复述，观察稳定性和独立完成度。",
            "第6天：用同类内容复盘，记录明显进步和仍需帮助的点。",
            "第7天：完成测评或训练营报名，进入下一轮个性化提升。",
        ]

    @staticmethod
    def _parent_tips(payload: PdfGenerationInput) -> list[str]:
        subject = payload.subject or "学习"
        return [
            f"不要只看完成数量，更要看孩子在{subject}任务中的主动性和错误类型。",
            "每次练习结束后只给一个具体表扬和一个改进点。",
            "如果连续两天抗拒明显，降低难度并缩短时长。",
        ]

    def _reference_text(self, payload: PdfGenerationInput, reference_profile: PdfReferenceProfile | None = None) -> str:
        parts = [payload.reference_text.strip()] if payload.reference_text and payload.reference_text.strip() else []
        if reference_profile and reference_profile.text:
            parts.append(reference_profile.text)
            return "\n".join(parts)
        if payload.reference_file_path:
            file_text = self._read_reference_file(payload.reference_file_path)
            if file_text:
                parts.append(file_text)
        return "\n".join(parts)

    def _reference_profile(self, payload: PdfGenerationInput) -> PdfReferenceProfile | None:
        if not payload.match_reference_style or not payload.reference_file_path:
            if payload.layout_type:
                return PdfReferenceProfile(layout_type=payload.layout_type, layout_notes=[f"使用手动选择版型：{payload.layout_type}"])
            return None
        target = self._safe_reference_path(payload.reference_file_path)
        if target.suffix.lower() != ".pdf" or not target.exists():
            return None
        fallback_text, fallback_start_page = self._read_pdf_text_with_start_page(target)
        content_start_page, content_start_reason = self._content_start_page_from_llm(payload, target)
        if content_start_page is None:
            text = fallback_text
            content_start_page = fallback_start_page
        else:
            text = self._read_pdf_text_from_start_page(target, content_start_page)
        profile = PdfReferenceProfile(text=text, layout_notes=[], layout_type=payload.layout_type)
        profile.content_start_page = content_start_page
        if content_start_reason:
            profile.layout_notes.append(f"LLM selected content start page {content_start_page}: {content_start_reason}")
        self._fill_pdfinfo(profile, target)
        self._render_reference_preview(profile, target)
        if profile.content_start_page > 1:
            profile.layout_notes.append(f"Skipped probable table-of-contents page; reference starts at page {profile.content_start_page}")
        if profile.orientation:
            profile.layout_notes.append(f"{profile.orientation}排版")
        if profile.layout_type:
            profile.layout_notes.append(f"命中预置版型：{profile.layout_type}")
        if text.count("\n") > 18:
            profile.layout_notes.append("内容分段较多，适合清单/练习页结构")
        return profile

    def _read_reference_file(self, relative_path: str) -> str:
        target = self._safe_reference_path(relative_path)
        if not target.exists():
            return ""
        if target.suffix.lower() in {".txt", ".md"}:
            return target.read_text(encoding="utf-8", errors="ignore")
        if target.suffix.lower() == ".pdf":
            return self._read_pdf_text(target)
        return ""

    def _safe_reference_path(self, relative_path: str) -> Path:
        root = self.file_root.resolve()
        target = (self.file_root / relative_path).resolve()
        if root not in target.parents and target != root:
            raise HTTPException(status_code=400, detail="invalid reference file path")
        return target

    @staticmethod
    def _read_pdf_text(target: Path) -> str:
        text, _ = PdfGenerationAgent._read_pdf_text_with_start_page(target)
        return text

    @staticmethod
    def _read_pdf_text_with_start_page(target: Path) -> tuple[str, int]:
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(target))
            pages = [page.extract_text() or "" for page in reader.pages[:4]]
        except Exception:
            return "", 1
        start_index = 0
        if len(pages) > 1:
            if PdfGenerationAgent._should_skip_first_reference_page(pages[0], pages[1]):
                start_index = 1
            elif PdfGenerationAgent._needs_visual_first_page_detection(pages):
                start_index = PdfGenerationAgent._visual_content_start_index(target)
        return "\n".join(pages[start_index : start_index + 3]), start_index + 1

    @staticmethod
    def _read_pdf_text_from_start_page(target: Path, start_page: int, max_pages: int = 3) -> str:
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(target))
            start_index = max(0, start_page - 1)
            return "\n".join(page.extract_text() or "" for page in reader.pages[start_index : start_index + max_pages])
        except Exception:
            return ""

    def _content_start_page_from_llm(self, payload: PdfGenerationInput, target: Path) -> tuple[int | None, str | None]:
        if not hasattr(self.content_generator, "detect_pdf_content_start_page"):
            return None, None
        previews = self._render_reference_pages_for_detection(target, page_count=4)
        if not previews:
            return None, None
        try:
            result = self.content_generator.detect_pdf_content_start_page(payload, [str(path) for path in previews])
        except LlmGenerationError as exc:
            logger.info("pdf_reference_content_start_page request_id=%s skipped error=%s", self._request_id, exc)
            return None, f"LLM content start page failed: {exc}"
        finally:
            for preview in previews:
                preview.unlink(missing_ok=True)
        if result is None:
            return None, None
        return result.page, result.reason

    @staticmethod
    def _should_skip_first_reference_page(first_page: str, second_page: str) -> bool:
        if not (second_page or "").strip():
            return False
        return PdfGenerationAgent._looks_like_toc_page(first_page) or PdfGenerationAgent._looks_like_cover_page(first_page)

    @staticmethod
    def _needs_visual_first_page_detection(pages: list[str]) -> bool:
        first_two_chars = sum(len("".join(page.split())) for page in pages[:2])
        return len(pages) > 1 and first_two_chars < 30

    @staticmethod
    def _looks_like_toc_page(text: str) -> bool:
        clean = " ".join((text or "").split()).lower()
        if not clean:
            return False
        toc_keywords = (
            "\u76ee\u5f55",
            "\u76ee \u5f55",
            "contents",
            "table of contents",
        )
        if not any(keyword in clean for keyword in toc_keywords):
            return False
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        page_number_lines = sum(1 for line in lines if re.search(r"(\.{2,}|\u2026|\s)\d{1,3}$", line))
        short_heading_lines = sum(1 for line in lines if len(line) <= 40)
        return page_number_lines >= 2 or short_heading_lines >= 6

    @staticmethod
    def _looks_like_cover_page(text: str) -> bool:
        clean = " ".join((text or "").split()).lower()
        if not clean:
            return False
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if len(lines) > 8 or len(clean) > 220:
            return False
        cover_keywords = (
            "\u5c01\u9762",
            "\u5168\u518c",
            "\u4e0a\u518c",
            "\u4e0b\u518c",
            "\u5e74\u7ea7",
            "\u8bed\u6587",
            "\u6570\u5b66",
            "\u82f1\u8bed",
            "\u8d44\u6599",
            "\u8bb2\u4e49",
            "\u7ec3\u4e60",
            "\u4eba\u6559\u7248",
            "cover",
            "workbook",
            "worksheet",
        )
        content_keywords = (
            "\u4f8b\u9898",
            "\u7b54\u6848",
            "\u9009\u62e9",
            "\u586b\u7a7a",
            "\u6b65\u9aa4",
            "\u65b9\u6cd5",
            "\u7ec3\u4e00\u7ec3",
            "\u77e5\u8bc6\u70b9",
            "\u5b57\u8bcd",
            "method",
            "practice",
            "question",
            "answer",
            "exercise",
            "steps",
        )
        keyword_hits = sum(1 for keyword in cover_keywords if keyword in clean)
        has_content_signal = any(keyword in clean for keyword in content_keywords)
        return keyword_hits >= 2 and not has_content_signal

    @staticmethod
    def _visual_content_start_index(target: Path) -> int:
        previews = PdfGenerationAgent._render_reference_pages_for_detection(target, page_count=2)
        if len(previews) < 2:
            return 0
        try:
            first = PdfGenerationAgent._image_layout_features(previews[0])
            second = PdfGenerationAgent._image_layout_features(previews[1])
        finally:
            for preview in previews:
                preview.unlink(missing_ok=True)
        return 1 if PdfGenerationAgent._looks_like_visual_cover_or_toc(first, second) else 0

    @staticmethod
    def _render_reference_pages_for_detection(target: Path, page_count: int = 2) -> list[Path]:
        pdftoppm = shutil.which("pdftoppm")
        if not pdftoppm:
            return []
        output_dir = Path("tmp/pdfs/reference-detect")
        output_dir.mkdir(parents=True, exist_ok=True)
        prefix = output_dir / f"{target.stem}-{uuid4().hex[:8]}"
        result = subprocess.run(
            [pdftoppm, "-png", "-f", "1", "-l", str(page_count), str(target), str(prefix)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
        if result.returncode != 0:
            return []
        return sorted(output_dir.glob(f"{prefix.name}-*.png"))

    @staticmethod
    def _image_layout_features(path: Path) -> dict[str, float]:
        try:
            from PIL import Image as PILImage

            with PILImage.open(path).convert("L") as image:
                image.thumbnail((360, 360))
                width, height = image.size
                pixels = list(image.tobytes())
        except Exception:
            return {"ink_density": 1.0, "bbox_ratio": 1.0, "line_groups": 99.0}
        mask = [value < 245 for value in pixels]
        ink_count = sum(mask)
        if not ink_count:
            return {"ink_density": 0.0, "bbox_ratio": 0.0, "line_groups": 0.0}
        xs = [index % width for index, value in enumerate(mask) if value]
        ys = [index // width for index, value in enumerate(mask) if value]
        bbox_ratio = ((max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1)) / float(width * height)
        row_hits = []
        for y in range(height):
            row = mask[y * width : (y + 1) * width]
            row_hits.append(sum(row) > width * 0.018)
        line_groups = 0
        in_group = False
        for has_ink in row_hits:
            if has_ink and not in_group:
                line_groups += 1
                in_group = True
            elif not has_ink:
                in_group = False
        return {
            "ink_density": ink_count / float(width * height),
            "bbox_ratio": bbox_ratio,
            "line_groups": float(line_groups),
        }

    @staticmethod
    def _looks_like_visual_cover_or_toc(first: dict[str, float], second: dict[str, float]) -> bool:
        first_sparse = first["ink_density"] < 0.075 and first["line_groups"] <= 12
        second_dense = second["ink_density"] > max(0.055, first["ink_density"] * 1.35) or second["line_groups"] >= first["line_groups"] + 6
        first_compact = first["bbox_ratio"] < 0.72
        second_content_like = second["bbox_ratio"] > first["bbox_ratio"] + 0.08 or second["line_groups"] >= 10
        return first_sparse and second_dense and (first_compact or second_content_like)

    def _fill_pdfinfo(self, profile: PdfReferenceProfile, target: Path) -> None:
        pdfinfo = shutil.which("pdfinfo")
        if not pdfinfo:
            profile.layout_notes.append("无法读取pdfinfo元数据")
            return
        result = subprocess.run([pdfinfo, str(target)], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15, check=False)
        if result.returncode != 0:
            profile.layout_notes.append("pdfinfo读取失败")
            return
        width = height = None
        for line in result.stdout.splitlines():
            if line.startswith("Pages:"):
                value = line.split(":", 1)[1].strip()
                profile.page_count = int(value) if value.isdigit() else None
            if line.startswith("Page size:"):
                profile.page_size = line.split(":", 1)[1].strip()
                parts = profile.page_size.split()
                if len(parts) >= 3:
                    try:
                        width = float(parts[0])
                        height = float(parts[2])
                    except ValueError:
                        pass
        if width and height:
            profile.orientation = "横版" if width > height else "竖版"

    def _render_reference_preview(self, profile: PdfReferenceProfile, target: Path) -> None:
        pdftoppm = shutil.which("pdftoppm")
        if not pdftoppm:
            profile.layout_notes.append("无法渲染参考PDF预览")
            return
        self.render_root.mkdir(parents=True, exist_ok=True)
        preview_prefix = self.render_root / f"reference-{target.stem}-{uuid4().hex[:8]}"
        preview_page = max(1, profile.content_start_page)
        result = subprocess.run([pdftoppm, "-png", "-f", str(preview_page), "-singlefile", str(target), str(preview_prefix)], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30, check=False)
        preview = preview_prefix.with_suffix(".png")
        if result.returncode == 0 and preview.exists() and preview.stat().st_size > 0:
            profile.preview_path = str(preview)
            profile.layout_notes.append(f"Rendered reference PDF page {preview_page} for layout comparison")
            profile.layout_notes.append("已渲染参考PDF第一页用于版式对照")

    @staticmethod
    def _page_size(reference_profile: PdfReferenceProfile | None):
        if reference_profile and reference_profile.orientation == "横版":
            return landscape(A4)
        return A4

    @staticmethod
    def _setup_fonts() -> None:
        if "AdminCN" in pdfmetrics.getRegisteredFontNames():
            return
        candidates = [
            Path("C:/Windows/Fonts/simhei.ttf"),
            Path("C:/Windows/Fonts/simsun.ttc"),
            Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
            Path("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"),
        ]
        for path in candidates:
            if path.exists():
                pdfmetrics.registerFont(TTFont("AdminCN", str(path)))
                return
        raise HTTPException(status_code=500, detail="Chinese font not found for PDF generation")

    @staticmethod
    def _styles() -> dict[str, ParagraphStyle]:
        base = getSampleStyleSheet()
        return {
            "Title": ParagraphStyle("AdminTitle", parent=base["Title"], fontName="AdminCN", fontSize=22, leading=30, textColor=colors.HexColor("#0f172a"), spaceAfter=8),
            "Section": ParagraphStyle("AdminSection", parent=base["Heading2"], fontName="AdminCN", fontSize=14, leading=20, textColor=colors.HexColor("#0aa34f"), spaceBefore=3, spaceAfter=7),
            "Body": ParagraphStyle("AdminBody", parent=base["BodyText"], fontName="AdminCN", fontSize=10.5, leading=18, textColor=colors.HexColor("#24324b")),
        }

    @staticmethod
    def _audience_table(payload: PdfGenerationInput, styles: dict[str, ParagraphStyle]) -> Table:
        age = ""
        if payload.target_age_min is not None and payload.target_age_max is not None:
            age = f"{payload.target_age_min}-{payload.target_age_max}岁"
        elif payload.target_age_min is not None:
            age = f"{payload.target_age_min}岁起"
        data = [["年级", payload.grade or "未指定", "年龄", age or "未指定"], ["学科", payload.subject or "未指定", "问题", payload.problem or "未指定"]]
        table = Table([[Paragraph(str(cell), styles["Body"]) for cell in row] for row in data], colWidths=[26 * mm, 55 * mm, 26 * mm, 55 * mm])
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f5fbf7")), ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dbe7df")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
        return table

    @staticmethod
    def _bullet_list(items: list[str], styles: dict[str, ParagraphStyle]) -> ListFlowable:
        return ListFlowable([ListItem(Paragraph(item, styles["Body"]), bulletColor=colors.HexColor("#0aa34f")) for item in items], bulletType="bullet", leftIndent=14)

    @staticmethod
    def _footer(canvas, doc) -> None:
        canvas.saveState()
        canvas.setFont("AdminCN", 8)
        canvas.setFillColor(colors.HexColor("#94a3b8"))
        canvas.drawRightString(doc.pagesize[0] - 18 * mm, 10 * mm, f"第 {doc.page} 页")
        canvas.restoreState()

    @staticmethod
    def _trim(text: str, limit: int) -> str:
        clean = " ".join(text.split())
        return clean if len(clean) <= limit else f"{clean[:limit]}..."
