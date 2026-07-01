from pydantic import BaseModel, Field
from datetime import datetime

from app.schemas.common import OrmModel


class ContentCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    content_type: str = Field(min_length=1, max_length=40)
    subject: str | None = Field(default=None, max_length=40)
    problem: str | None = Field(default=None, max_length=80)
    target_age_min: int | None = Field(default=None, ge=0, le=18)
    target_age_max: int | None = Field(default=None, ge=0, le=18)
    grade: str | None = Field(default=None, max_length=40)
    summary: str | None = None
    cover_url: str | None = None
    file_path: str | None = None
    next_action: str | None = Field(default=None, max_length=80)
    next_action_url: str | None = None
    unlock_type: str = Field(default="free", max_length=40)
    unlock_threshold: int = Field(default=0, ge=0, le=100)
    tags: list[str] = Field(default_factory=list)


class ContentUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    content_type: str | None = Field(default=None, min_length=1, max_length=40)
    subject: str | None = Field(default=None, max_length=40)
    problem: str | None = Field(default=None, max_length=80)
    target_age_min: int | None = Field(default=None, ge=0, le=18)
    target_age_max: int | None = Field(default=None, ge=0, le=18)
    grade: str | None = Field(default=None, max_length=40)
    summary: str | None = None
    cover_url: str | None = None
    file_path: str | None = None
    next_action: str | None = Field(default=None, max_length=80)
    next_action_url: str | None = None
    unlock_type: str | None = Field(default=None, max_length=40)
    unlock_threshold: int | None = Field(default=None, ge=0, le=100)
    tags: list[str] | None = None


class PublishRequest(BaseModel):
    is_published: bool


class TaxonomyTagCreateRequest(BaseModel):
    tag_type: str = Field(pattern="^(subject|grade|problem_category|problem)$")
    label: str = Field(min_length=1, max_length=80)
    parent_id: int | None = None
    is_active: bool = True


class TaxonomyTagUpdateRequest(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=80)
    parent_id: int | None = None
    is_active: bool | None = None


class TaxonomyTagResponse(OrmModel):
    id: int
    tag_type: str
    label: str
    parent_id: int | None = None
    is_active: bool
    sort_order: int


class ProblemCategoryOption(BaseModel):
    id: int
    label: str
    problems: list[str] = Field(default_factory=list)


class TaxonomyOptionsResponse(BaseModel):
    subjects: list[str]
    grades: list[str]
    problems: list[str]
    problem_categories: list[ProblemCategoryOption] = Field(default_factory=list)


class AiPdfGenerateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    summary: str = Field(min_length=1)
    subject: str | None = Field(default=None, max_length=40)
    problem: str | None = Field(default=None, max_length=80)
    grade: str | None = Field(default=None, max_length=40)
    target_age_min: int | None = Field(default=None, ge=0, le=18)
    target_age_max: int | None = Field(default=None, ge=0, le=18)
    reference_text: str | None = None
    reference_file_path: str | None = None
    match_reference_style: bool = False
    layout_type: str | None = Field(default=None, pattern="^(knowledge_card|key_notes|choice_training|math_exam)$")
    next_action: str | None = Field(default=None, max_length=80)


class AiImagePdfGenerateRequest(AiPdfGenerateRequest):
    page_count: int = Field(default=2, ge=1)


class AiImagePdfGenerateResponse(BaseModel):
    title: str
    summary: str
    file_path: str
    url: str
    outline: list[str]
    image_paths: list[str]
    page_count: int
    generation_source: str = "llm-image"
    model: str | None = None
    token_usage: dict = Field(default_factory=dict)
    generation_error: str | None = None
    request_id: str = ""
    generation_steps: list[dict] = Field(default_factory=list)


class AiModelCallLogListItem(OrmModel):
    id: int
    request_id: str | None
    task_type: str
    step_name: str
    provider: str
    model: str | None
    status: str
    prompt_tokens: int
    completion_tokens: int
    image_tokens: int
    total_tokens: int
    duration_ms: int
    started_at: datetime
    finished_at: datetime | None


class AiModelCallLogDetail(AiModelCallLogListItem):
    endpoint: str
    http_method: str
    request_payload: dict
    response_payload: dict | None
    prompt_text: str | None
    response_text: str | None
    error_message: str | None
    created_at: datetime


class ContentAdminResponse(OrmModel):
    id: int
    title: str
    content_type: str
    subject: str | None
    problem: str | None
    target_age_min: int | None
    target_age_max: int | None
    grade: str | None
    summary: str | None
    cover_url: str | None
    file_path: str | None
    next_action: str | None
    next_action_url: str | None
    unlock_type: str
    unlock_threshold: int
    is_published: bool
    claim_count: int = 0
    share_count: int = 0
    lead_count: int = 0


class DashboardMetricChange(BaseModel):
    current: int
    previous: int
    percent: float
    direction: str


class DashboardOverview(BaseModel):
    new_users: int
    active_users: int
    claimed: int
    downloaded: int
    shared: int
    leads: int
    changes: dict[str, DashboardMetricChange] = Field(default_factory=dict)


class PreferenceItem(BaseModel):
    key: str
    count: int


class PreferenceOverview(BaseModel):
    ages: list[PreferenceItem]
    subjects: list[PreferenceItem]
    problems: list[PreferenceItem]
    content_types: list[PreferenceItem]


class AdminUserProfileResponse(BaseModel):
    user_id: int
    open_id: str
    nickname: str | None
    avatar_url: str | None = None
    source_channel: str | None
    child_age: int | None
    child_grade: str | None
    tags: list[str] = Field(default_factory=list)
    registered_at: datetime
    last_active_at: datetime | None = None
    claim_count: int = 0
    download_count: int = 0
    share_count: int = 0
    assessment_count: int = 0
    camp_count: int = 0
    lead_count: int = 0
    intent_score: int = 0
    intent_level: str
    recommended_action: str


class AdminUserPageResponse(BaseModel):
    items: list[AdminUserProfileResponse]
    total: int
    page: int
    page_size: int
    recommended: list[AdminUserProfileResponse] = Field(default_factory=list)


class AiTopicSuggestionResponse(OrmModel):
    id: int
    title: str
    target_audience: str
    content_type: str
    reason: str
    source_metrics: dict
    status: str
