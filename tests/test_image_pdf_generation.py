from dataclasses import dataclass
from io import BytesIO

from fastapi import FastAPI
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from app.api.admin import router as admin_router
from app.services.llm import LlmMaterialPlanResult
from app.tasks.generators import ImagePdfGenerationAgent, PdfGenerationInput
from app.tasks.generators.types import GenerationStep, MaterialBlock, MaterialPage, MaterialPlan, PdfContentDraft, PdfReferenceProfile, TokenUsage


def png_bytes(width=768, height=1024):
    image = Image.new("RGB", (width, height), "#f7fbff")
    draw = ImageDraw.Draw(image)
    draw.rectangle((32, 32, width - 32, height - 32), outline="#2563eb", width=8)
    draw.rectangle((80, 120, width - 80, 260), fill="#dbeafe")
    draw.text((100, 170), "AI PAGE", fill="#111827")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


class FakePlanGenerator:
    def __init__(self):
        self.plan_requests = []
        self.image_prompts = []

    def generate_material_plan(self, payload, reference, page_count):
        self.plan_requests.append((payload, reference, page_count))
        pages = []
        question_no = 1
        for page_no in range(1, page_count + 1):
            items = []
            for _ in range(2):
                items.append(f"{question_no}. 连续数学题")
                question_no += 1
            pages.append(
                MaterialPage(
                    page_no=page_no,
                    section_title=f"第{page_no}页练习",
                    blocks=[MaterialBlock(type="question", title="连续题目", items=items, answer_space=1)],
                    continued_from=page_no - 1 if page_no > 1 else None,
                    continued_to=page_no + 1 if page_no < page_count else None,
                )
            )
        plan = MaterialPlan(
            material_type="worksheet",
            title=payload.title,
            summary=payload.summary,
            audience=payload.grade or "一年级",
            pages=pages,
            outline=["连续题号", "统一页眉"],
            global_style="A4练习卷",
        )
        return LlmMaterialPlanResult(plan=plan, model="gpt5.5", usage=TokenUsage(prompt_tokens=20, completion_tokens=30, total_tokens=50))

    def generate_pdf_content(self, payload, reference, reference_profile=None, reference_analysis=None):
        raise AssertionError("material plan generation should be used first")

    def generate_image_bytes(self, prompt, size="1024x1536"):
        self.image_prompts.append((prompt, size))
        if size == "1536x1024":
            return png_bytes(1536, 1024), TokenUsage(image_tokens=8, total_tokens=8)
        return png_bytes(1024, 1536), TokenUsage(image_tokens=8, total_tokens=8)


class FallbackGenerator:
    def generate_pdf_content(self, payload, reference, reference_profile=None, reference_analysis=None):
        class Result:
            model = "gpt5.5"
            usage = TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
            draft = PdfContentDraft(
                title="图片PDF识字练习",
                summary="帮助家长判断孩子识字量是否不足。",
                outline=["观察阅读速度", "记录错读字", "安排每日练习"],
                practice_plan=["第1天摸底", "第2天复习", "第3天朗读", "第4天组词"],
                parent_tips=["一次只纠正一个问题", "练习后及时鼓励"],
                next_action="完成5分钟识字测评",
                reference_summary="参考资料用于组织版式。",
            )

        return Result()

    def generate_image_bytes(self, prompt, size="1024x1536"):
        return png_bytes(1024, 1536), TokenUsage(image_tokens=5, total_tokens=5)


class FailingImagePlanGenerator(FakePlanGenerator):
    def generate_image_bytes(self, prompt, size="1024x1536"):
        self.image_prompts.append((prompt, size))
        return None, TokenUsage()


class ReferenceImageGenerator(FakePlanGenerator):
    def __init__(self):
        super().__init__()
        self.reference_calls = []

    def generate_image_with_reference_bytes(self, prompt, reference_image_paths, size="1024x1536"):
        self.reference_calls.append((prompt, reference_image_paths, size))
        return png_bytes(1024, 1536), TokenUsage(image_tokens=9, total_tokens=9)


def test_image_pdf_generation_uses_material_plan_pages(tmp_path):
    generator = FakePlanGenerator()
    agent = ImagePdfGenerationAgent(
        file_root=tmp_path,
        base_url="http://testserver/files",
        content_generator=generator,
    )

    result = agent.generate(
        PdfGenerationInput(
            title="一年级数学连续练习",
            summary="生成一份连续的数学练习资料",
            subject="数学",
            problem="计算能力",
            grade="一年级",
        ),
        page_count=3,
    )

    assert result.page_count == 3
    assert len(result.image_paths) == 3
    assert result.outline == ["连续题号", "统一页眉"]
    assert result.token_usage.total_tokens == 74
    assert result.token_usage.image_tokens == 24
    assert (tmp_path / result.file_path).read_bytes().startswith(b"%PDF")
    assert all((tmp_path / path).exists() for path in result.image_paths)
    assert generator.plan_requests[0][2] == 3
    assert len(generator.image_prompts) == 3
    assert "第 2 页 / 共 3 页" in generator.image_prompts[1][0]
    assert "上一页是第 1 页" in generator.image_prompts[1][0]


def test_image_pdf_generation_can_render_eight_pages(tmp_path):
    agent = ImagePdfGenerationAgent(
        file_root=tmp_path,
        base_url="http://testserver/files",
        content_generator=FakePlanGenerator(),
    )

    result = agent.generate(
        PdfGenerationInput(title="八页练习", summary="生成八页连续资料", subject="数学"),
        page_count=8,
    )

    assert result.page_count == 8
    assert len(result.image_paths) == 8


def test_image_pdf_generation_caps_page_count_from_settings(tmp_path, monkeypatch):
    from app.tasks.generators import image_pdf

    settings = image_pdf.get_settings()
    monkeypatch.setattr(settings, "ai_image_pdf_max_pages", 3)
    generator = FakePlanGenerator()
    agent = ImagePdfGenerationAgent(
        file_root=tmp_path,
        base_url="http://testserver/files",
        content_generator=generator,
    )

    result = agent.generate(
        PdfGenerationInput(title="超长资料", summary="请求超过服务端上限"),
        page_count=8,
    )

    assert result.page_count == 3
    assert generator.plan_requests[0][2] == 3
    assert result.generation_steps[0].metadata["requested_page_count"] == 8
    assert result.generation_steps[0].metadata["max_page_count"] == 3


def test_image_pdf_generation_falls_back_without_material_plan(tmp_path):
    agent = ImagePdfGenerationAgent(
        file_root=tmp_path,
        base_url="http://testserver/files",
        content_generator=FallbackGenerator(),
    )

    result = agent.generate(
        PdfGenerationInput(title="识字练习", summary="每日练习", subject="语文", problem="识字"),
        page_count=2,
    )

    assert result.page_count == 2
    assert result.generation_source == "ai-pages"
    assert result.title == "图片PDF识字练习"


def test_image_pdf_generation_falls_back_to_template_when_ai_page_missing(tmp_path):
    generator = FailingImagePlanGenerator()
    agent = ImagePdfGenerationAgent(
        file_root=tmp_path,
        base_url="http://testserver/files",
        content_generator=generator,
    )

    result = agent.generate(
        PdfGenerationInput(title="AI失败回退", summary="仍然生成连续PDF", subject="数学"),
        page_count=2,
    )

    assert result.page_count == 2
    assert len(result.image_paths) == 2
    assert len(generator.image_prompts) == 2
    assert any(step.step == "ai_page_fallback_1" for step in result.generation_steps)


def test_reference_context_includes_manual_and_pdf_text(tmp_path, monkeypatch):
    reference = tmp_path / "reference.png"
    reference.write_bytes(png_bytes())

    def fake_profile(self, payload):
        return PdfReferenceProfile(text="pdf extracted text", preview_path=str(reference))

    monkeypatch.setattr("app.tasks.generators.pdf.PdfGenerationAgent._reference_profile", fake_profile)
    agent = ImagePdfGenerationAgent(file_root=tmp_path, base_url="http://testserver/files", content_generator=FallbackGenerator())

    text, error, images, layout_prompt = agent._reference_context(
        PdfGenerationInput(
            title="Reference PDF",
            summary="Reference summary",
            reference_text="manual reference",
            reference_file_path="materials/reference.pdf",
            match_reference_style=True,
        )
    )

    assert error is None
    assert "manual reference" in text
    assert "pdf extracted text" in text
    assert images == [str(reference)]
    assert "参考PDF" in layout_prompt


def test_image_pdf_generation_sends_reference_image_when_file_uploaded(tmp_path, monkeypatch):
    reference = tmp_path / "reference.png"
    reference.write_bytes(png_bytes())

    def fake_profile(self, payload):
        if not payload.match_reference_style:
            return None
        return PdfReferenceProfile(text="pdf extracted text", preview_path=str(reference), layout_analysis="two-column worksheet with center divider")

    monkeypatch.setattr("app.tasks.generators.pdf.PdfGenerationAgent._reference_profile", fake_profile)
    generator = ReferenceImageGenerator()
    agent = ImagePdfGenerationAgent(file_root=tmp_path, base_url="http://testserver/files", content_generator=generator)

    result = agent.generate(
        PdfGenerationInput(
            title="Reference image",
            summary="Use uploaded reference",
            reference_file_path="materials/reference.pdf",
            match_reference_style=False,
        ),
        page_count=1,
    )

    assert result.page_count == 1
    assert len(generator.reference_calls) == 1
    assert generator.reference_calls[0][1] == [str(reference)]
    assert generator.plan_requests[0][1] == "pdf extracted text"
    assert "two-column worksheet with center divider" in generator.reference_calls[0][0]


@dataclass
class FakeImagePdfResult:
    title: str = "Image PDF"
    summary: str = "Image summary"
    file_path: str = "materials/ai-generated/image.pdf"
    url: str = "http://testserver/files/materials/ai-generated/image.pdf"
    outline: list[str] = None
    image_paths: list[str] = None
    page_count: int = 2
    generation_source: str = "llm-plan"
    model: str = "gpt5.5"
    token_usage: TokenUsage = None
    generation_error: str | None = None
    request_id: str = "image-request-id"
    generation_steps: list[GenerationStep] = None

    def __post_init__(self):
        self.outline = self.outline or ["Point 1"]
        self.image_paths = self.image_paths or ["materials/ai-generated/images/page-1.png"]
        self.token_usage = self.token_usage or TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=120, image_tokens=0)
        self.generation_steps = self.generation_steps or [
            GenerationStep(step="render_page_1", status="ok", message="test step", duration_ms=12)
        ]


def test_generate_image_pdf_response_serializes_result(monkeypatch):
    from app.api import admin

    class FakeAgent:
        def generate(self, payload, page_count=2):
            return FakeImagePdfResult(page_count=page_count)

    monkeypatch.setattr(admin, "ImagePdfGenerationAgent", lambda: FakeAgent())
    app = FastAPI()
    app.include_router(admin_router)
    response = TestClient(app).post(
        "/admin/ai/generate/image-pdf",
        json={"title": "Image PDF", "summary": "Image summary", "page_count": 3},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["page_count"] == 3
    assert body["image_paths"] == ["materials/ai-generated/images/page-1.png"]
    assert body["token_usage"]["image_tokens"] == 0
    assert body["generation_steps"][0]["step"] == "render_page_1"
