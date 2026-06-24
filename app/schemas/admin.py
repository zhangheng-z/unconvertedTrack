from pydantic import BaseModel, Field

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


class DashboardOverview(BaseModel):
    new_users: int
    active_users: int
    claimed: int
    downloaded: int
    shared: int
    leads: int


class PreferenceItem(BaseModel):
    key: str
    count: int


class PreferenceOverview(BaseModel):
    ages: list[PreferenceItem]
    subjects: list[PreferenceItem]
    problems: list[PreferenceItem]
    content_types: list[PreferenceItem]


class AiTopicSuggestionResponse(OrmModel):
    id: int
    title: str
    target_audience: str
    content_type: str
    reason: str
    source_metrics: dict
    status: str
