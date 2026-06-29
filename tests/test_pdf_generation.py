from pathlib import Path
import shutil
import subprocess

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw
import pytest
from reportlab.pdfgen import canvas

from app.config import get_settings
from app.services.llm import LlmContentStartPageResult
from app.tasks.generators import PdfGenerationAgent, PdfGenerationInput
from app.tasks.generators.types import PdfContentDraft, ReferenceAnalysis, TokenUsage


class FakeLlmGenerator:
    def analyze_reference_pdf(self, payload, reference, reference_profile=None):
        class Result:
            model = "gpt5.5"
            usage = TokenUsage(prompt_tokens=60, completion_tokens=40, total_tokens=100)
            analysis = ReferenceAnalysis(
                content_pattern="diagnosis then practice plan",
                writing_style="parent-facing and action-oriented",
                section_structure=["diagnosis", "practice", "next step"],
                layout_suggestions=["short sections"],
                practice_forms=["daily checklist"],
                avoid_copying=["original examples"],
            )

        return Result()

    def generate_pdf_content(self, payload, reference, reference_profile=None, reference_analysis=None):
        class Result:
            model = "gpt5.5"
            usage = TokenUsage(prompt_tokens=120, completion_tokens=80, total_tokens=200)
            draft = PdfContentDraft(
                title="LLM生成的一年级识字计划",
                summary="这是由大模型生成的简介。",
                outline=["识别当前识字卡点", "安排家庭练习节奏", "引导完成测评"],
                practice_plan=["第1天摸底", "第2天复习旧字", "第3天加入新字"],
                parent_tips=["每次只给一个改进点", "先鼓励再纠错"],
                next_action="完成5分钟识字测评",
                reference_summary="已参考运营提供资料。",
            )

        return Result()

    def generate_image_bytes(self, prompt):
        return None, TokenUsage()


class TemplateOnlyGenerator:
    def analyze_reference_pdf(self, payload, reference, reference_profile=None):
        return None

    def generate_pdf_content(self, payload, reference, reference_profile=None, reference_analysis=None):
        return None

    def generate_image_bytes(self, prompt):
        return None, TokenUsage()


class StartPageGenerator(TemplateOnlyGenerator):
    def __init__(self, page: int):
        self.page = page
        self.page_images = []

    def detect_pdf_content_start_page(self, payload, page_image_paths):
        self.page_images = page_image_paths
        return LlmContentStartPageResult(
            page=self.page,
            reason="page has worksheet content",
            model="gpt5.5",
            usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
        )


def test_reference_pdf_text_skips_probable_toc_first_page(tmp_path):
    path = tmp_path / "reference-with-toc.pdf"
    pdf = canvas.Canvas(str(path))
    pdf.drawString(72, 760, "Contents")
    pdf.drawString(72, 720, "Lesson 1 recognition .... 2")
    pdf.drawString(72, 700, "Lesson 2 practice .... 3")
    pdf.drawString(72, 680, "Lesson 3 review .... 4")
    pdf.showPage()
    pdf.drawString(72, 760, "Real content page")
    pdf.drawString(72, 720, "Daily 10 minute recognition practice plan")
    pdf.save()

    text, start_page = PdfGenerationAgent._read_pdf_text_with_start_page(path)

    assert start_page == 2
    assert "Real content page" in text
    assert "Contents" not in text


def test_reference_pdf_text_skips_probable_cover_first_page(tmp_path):
    path = tmp_path / "reference-with-cover.pdf"
    pdf = canvas.Canvas(str(path))
    pdf.drawString(72, 760, "Grade 1 Chinese")
    pdf.drawString(72, 720, "Workbook Cover")
    pdf.drawString(72, 680, "Worksheet Materials")
    pdf.showPage()
    pdf.drawString(72, 760, "Real content page")
    pdf.drawString(72, 720, "Knowledge point: daily recognition practice")
    pdf.save()

    text, start_page = PdfGenerationAgent._read_pdf_text_with_start_page(path)

    assert start_page == 2
    assert "Real content page" in text
    assert "Workbook Cover" not in text


def test_reference_pdf_text_keeps_normal_first_page(tmp_path):
    path = tmp_path / "reference-without-toc.pdf"
    pdf = canvas.Canvas(str(path))
    pdf.drawString(72, 760, "Reading diagnosis card")
    pdf.drawString(72, 720, "Observe words the child can read independently")
    pdf.showPage()
    pdf.drawString(72, 760, "Second content page")
    pdf.save()

    text, start_page = PdfGenerationAgent._read_pdf_text_with_start_page(path)

    assert start_page == 1
    assert "Reading diagnosis card" in text


def test_reference_pdf_text_keeps_short_content_first_page(tmp_path):
    path = tmp_path / "reference-short-content.pdf"
    pdf = canvas.Canvas(str(path))
    pdf.drawString(72, 760, "Reading diagnosis card")
    pdf.drawString(72, 720, "Method: read 3 word groups and circle unknown words")
    pdf.showPage()
    pdf.drawString(72, 760, "Second content page")
    pdf.save()

    text, start_page = PdfGenerationAgent._read_pdf_text_with_start_page(path)

    assert start_page == 1
    assert "Method" in text


def test_reference_profile_uses_llm_selected_content_start_page(tmp_path, monkeypatch):
    file_root = tmp_path / "files"
    reference_dir = file_root / "materials"
    reference_dir.mkdir(parents=True)
    reference = reference_dir / "reference.pdf"
    pdf = canvas.Canvas(str(reference))
    pdf.drawString(72, 760, "Cover page")
    pdf.showPage()
    pdf.drawString(72, 760, "Real worksheet content")
    pdf.drawString(72, 720, "Exercise 1")
    pdf.save()

    preview = tmp_path / "page-1.png"
    _image_page(dense=True).save(preview)
    monkeypatch.setattr(PdfGenerationAgent, "_render_reference_pages_for_detection", staticmethod(lambda target, page_count=4: [preview]))

    generator = StartPageGenerator(page=2)
    agent = PdfGenerationAgent(file_root=file_root, base_url="http://testserver/files", content_generator=generator)

    profile = agent._reference_profile(
        PdfGenerationInput(
            title="New worksheet",
            summary="New summary",
            reference_file_path="materials/reference.pdf",
            match_reference_style=True,
        )
    )

    assert profile.content_start_page == 2
    assert "Real worksheet content" in profile.text
    assert "Cover page" not in profile.text
    assert generator.page_images == [str(preview)]
    assert any("LLM selected content start page 2" in note for note in profile.layout_notes)


def _image_page(width=900, height=1200, dense=False):
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    if dense:
        for y in range(80, height - 80, 42):
            draw.rectangle((70, y, width - 70, y + 12), fill="#222222")
            draw.rectangle((70, y + 18, width - 220, y + 26), fill="#666666")
    else:
        draw.rectangle((260, 360, width - 260, 430), fill="#222222")
        draw.rectangle((330, 470, width - 330, 520), fill="#666666")
    return image


def _usable_command(name):
    command = shutil.which(name)
    if not command:
        return False
    result = subprocess.run([command, "-v"], capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    return result.returncode == 0


def test_image_only_reference_pdf_skips_sparse_cover_page(tmp_path):
    if not _usable_command("pdftoppm"):
        pytest.skip("pdftoppm is unavailable")
    path = tmp_path / "image-only-reference.pdf"
    cover = _image_page(dense=False)
    content = _image_page(dense=True)
    cover.save(path, "PDF", save_all=True, append_images=[content], resolution=150.0)

    text, start_page = PdfGenerationAgent._read_pdf_text_with_start_page(path)

    assert text.strip() == ""
    assert start_page == 2


def test_image_only_reference_pdf_keeps_dense_first_page(tmp_path):
    if not _usable_command("pdftoppm"):
        pytest.skip("pdftoppm is unavailable")
    path = tmp_path / "image-only-content.pdf"
    first = _image_page(dense=True)
    second = _image_page(dense=True)
    first.save(path, "PDF", save_all=True, append_images=[second], resolution=150.0)

    _, start_page = PdfGenerationAgent._read_pdf_text_with_start_page(path)

    assert start_page == 1


def test_pdf_generation_agent_creates_pdf(tmp_path):
    agent = PdfGenerationAgent(
        file_root=tmp_path,
        base_url="http://testserver/files",
        render_root=tmp_path / "render",
        content_generator=TemplateOnlyGenerator(),
    )

    result = agent.generate(
        PdfGenerationInput(
            title="一年级识字提升计划",
            summary="帮助家长判断孩子识字量，并安排每天10分钟练习。",
            subject="语文",
            problem="识字少",
            grade="一年级",
            target_age_min=7,
            target_age_max=8,
            reference_text="参考资料：每天先复习旧字，再加入少量新字。",
            next_action="5分钟识字测评",
        )
    )

    pdf_path = tmp_path / result.file_path
    assert result.file_path.startswith("materials/ai-generated/")
    assert result.url.endswith(result.file_path)
    assert len(result.outline) >= 3
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0
    assert pdf_path.read_bytes().startswith(b"%PDF")
    if shutil.which("pdfinfo"):
        assert result.quality.checked is True
        assert result.quality.page_count and result.quality.page_count > 0
    if result.quality.preview_path:
        assert Path(result.quality.preview_path).exists()


def test_pdf_generation_agent_uses_llm_content(tmp_path):
    agent = PdfGenerationAgent(
        file_root=tmp_path,
        base_url="http://testserver/files",
        render_root=tmp_path / "render",
        content_generator=FakeLlmGenerator(),
    )

    result = agent.generate(
        PdfGenerationInput(
            title="原始标题",
            summary="原始简介",
            subject="语文",
            problem="识字少",
            grade="一年级",
            target_age_min=7,
            target_age_max=8,
        )
    )

    assert result.title == "LLM生成的一年级识字计划"
    assert result.generation_source == "llm"
    assert result.model == "gpt5.5"
    assert result.outline == ["识别当前识字卡点", "安排家庭练习节奏", "引导完成测评"]
    assert result.token_usage.prompt_tokens == 120
    assert result.token_usage.completion_tokens == 80
    assert result.token_usage.total_tokens == 200


def test_pdf_generation_agent_can_match_reference_pdf_style(tmp_path):
    agent = PdfGenerationAgent(
        file_root=tmp_path,
        base_url="http://testserver/files",
        render_root=tmp_path / "render",
        content_generator=TemplateOnlyGenerator(),
    )
    reference = agent.generate(
        PdfGenerationInput(
            title="参考识字资料",
            summary="参考资料简介。",
            subject="语文",
            problem="识字少",
            grade="一年级",
            target_age_min=7,
            target_age_max=8,
        )
    )

    result = agent.generate(
        PdfGenerationInput(
            title="仿参考结构的新资料",
            summary="根据参考资料结构生成的新内容。",
            subject="语文",
            problem="识字少",
            grade="一年级",
            target_age_min=7,
            target_age_max=8,
            reference_file_path=reference.file_path,
            match_reference_style=True,
        )
    )

    pdf_path = tmp_path / result.file_path
    assert pdf_path.exists()
    assert pdf_path.read_bytes().startswith(b"%PDF")


def disabled_admin_generate_pdf_can_publish_to_content_pool(client: TestClient, tmp_path, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "local_file_root", str(tmp_path))
    monkeypatch.setattr(settings, "local_file_base_url", "http://testserver/files")

    generate = client.post(
        "/admin/ai/generate/image-pdf",
        json={
            "title": "一年级识字提升计划",
            "summary": "帮助家长判断孩子识字量，并安排每天10分钟练习。",
            "subject": "语文",
            "problem": "识字少",
            "grade": "一年级",
            "target_age_min": 7,
            "target_age_max": 8,
            "reference_text": "参考资料：每天先复习旧字，再加入少量新字。",
            "next_action": "5分钟识字测评",
        },
    )
    assert generate.status_code == 200
    generated = generate.json()
    assert Path(tmp_path / generated["file_path"]).exists()

    create = client.post(
        "/admin/contents",
        json={
            "title": generated["title"],
            "content_type": "pdf",
            "subject": "语文",
            "problem": "识字少",
            "target_age_min": 7,
            "target_age_max": 8,
            "grade": "一年级",
            "summary": generated["summary"],
            "file_path": generated["file_path"],
            "next_action": "5分钟识字测评",
            "tags": ["语文", "一年级", "PDF"],
        },
    )
    assert create.status_code == 200
    content_id = create.json()["id"]

    publish = client.patch(f"/admin/contents/{content_id}/publish", json={"is_published": True})
    assert publish.status_code == 200

    contents = client.get("/admin/contents")
    assert contents.status_code == 200
    assert contents.json()[0]["file_path"] == generated["file_path"]


def test_admin_contents_default_excludes_review_drafts(client: TestClient):
    draft = client.post(
        "/admin/contents",
        json={
            "title": "AI生成待审核资料",
            "content_type": "pdf",
            "subject": "语文",
            "problem": "识字少",
            "summary": "先进入素材审核。",
            "file_path": "materials/ai-generated/draft.pdf",
            "tags": ["AI生成"],
        },
    )
    assert draft.status_code == 200

    published_contents = client.get("/admin/contents")
    assert published_contents.status_code == 200
    assert published_contents.json() == []

    review_contents = client.get("/admin/contents", params={"is_published": False})
    assert review_contents.status_code == 200
    assert review_contents.json()[0]["title"] == "AI生成待审核资料"
