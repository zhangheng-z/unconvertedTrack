from dataclasses import dataclass


@dataclass
class PdfGenerationInput:
    title: str
    summary: str
    subject: str | None = None
    problem: str | None = None
    grade: str | None = None
    target_age_min: int | None = None
    target_age_max: int | None = None
    reference_text: str | None = None
    reference_file_path: str | None = None
    match_reference_style: bool = False
    layout_type: str | None = None
    next_action: str | None = None


@dataclass
class PdfReferenceProfile:
    text: str = ""
    page_count: int | None = None
    content_start_page: int = 1
    page_size: str | None = None
    orientation: str | None = None
    preview_path: str | None = None
    layout_type: str | None = None
    layout_notes: list[str] | None = None


@dataclass
class ReferenceAnalysis:
    content_pattern: str = ""
    writing_style: str = ""
    section_structure: list[str] | None = None
    layout_suggestions: list[str] | None = None
    practice_forms: list[str] | None = None
    avoid_copying: list[str] | None = None

    def to_prompt_text(self) -> str:
        lines = [
            f"内容组织模式：{self.content_pattern or '未识别'}",
            f"写作语气风格：{self.writing_style or '未识别'}",
            f"栏目结构：{'；'.join(self.section_structure or []) or '未识别'}",
            f"版式建议：{'；'.join(self.layout_suggestions or []) or '未识别'}",
            f"练习/任务形式：{'；'.join(self.practice_forms or []) or '未识别'}",
            f"避免直接复制：{'；'.join(self.avoid_copying or []) or '避免复制原文句子、题目和示例'}",
        ]
        return "\n".join(lines)


@dataclass
class GenerationStep:
    step: str
    status: str
    message: str
    duration_ms: int = 0
    metadata: dict | None = None


@dataclass
class PdfContentDraft:
    title: str
    summary: str
    outline: list[str]
    practice_plan: list[str]
    parent_tips: list[str]
    next_action: str
    reference_summary: str = ""
    image_prompt: str = ""


@dataclass
class MaterialBlock:
    type: str
    title: str = ""
    text: str = ""
    items: list[str] | None = None
    options: list[str] | None = None
    answer_space: int = 1


@dataclass
class MaterialPage:
    page_no: int
    section_title: str
    blocks: list[MaterialBlock]
    continued_from: int | None = None
    continued_to: int | None = None


@dataclass
class MaterialPlan:
    material_type: str
    title: str
    summary: str
    audience: str
    pages: list[MaterialPage]
    outline: list[str]
    global_style: str = ""


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    image_tokens: int = 0

    def add(self, other: "TokenUsage") -> None:
        self.prompt_tokens += other.prompt_tokens
        self.completion_tokens += other.completion_tokens
        self.total_tokens += other.total_tokens
        self.image_tokens += other.image_tokens
