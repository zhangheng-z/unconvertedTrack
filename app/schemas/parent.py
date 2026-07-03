from pydantic import BaseModel, Field

from app.schemas.common import OrmModel


class OnboardingProfileRequest(BaseModel):
    open_id: str = Field(min_length=1, max_length=128)
    nickname: str | None = Field(default=None, max_length=80)
    source_channel: str | None = Field(default=None, max_length=80)
    child_age: int = Field(ge=0, le=18)
    child_grade: str = Field(min_length=1, max_length=40)
    concerns: list[str] = Field(default_factory=list, max_length=10)


class OnboardingProfileResponse(OrmModel):
    user_id: int
    child_id: int
    tags: list[str]


class ContentListItem(OrmModel):
    id: int
    title: str
    content_type: str
    subject: str | None
    problem: str | None
    problem_tags: list[str] = Field(default_factory=list)
    cover_url: str | None
    summary: str | None
    next_action: str | None
    unlock_type: str = "free"
    unlock_threshold: int = 0
    is_claimed: bool = False
    is_unlocked: bool = False
    user_share_count: int = 0
    claim_count: int = 0
    share_count: int = 0
    effective_share_count: int = 0
    lead_count: int = 0


class ContentDetail(ContentListItem):
    file_path: str | None
    next_action_url: str | None


class ClaimResponse(BaseModel):
    content_id: int
    claimed: bool
    unlocked: bool


class DownloadResponse(BaseModel):
    content_id: int
    download_url: str


class ShareResponse(BaseModel):
    content_id: int
    share_count: int
    unlocked: bool


class ShareOpenRequest(BaseModel):
    inviter_user_id: int = Field(gt=0)
    source_content_id: int = Field(gt=0)


class ShareOpenResponse(BaseModel):
    recorded: bool


class MyAsset(OrmModel):
    content_id: int
    title: str
    content_type: str
    unlocked: bool
    share_count: int


class InviteSummary(BaseModel):
    invited_count: int
    unlockable_count: int
    display_text: str


class InviteCompleteRequest(BaseModel):
    inviter_user_id: int = Field(gt=0)
    source_content_id: int | None = Field(default=None, gt=0)


class InviteCompleteResponse(BaseModel):
    completed: bool
    invited_count: int


class EventCreateRequest(BaseModel):
    open_id: str = Field(min_length=1, max_length=128)
    event_type: str = Field(min_length=1, max_length=40)
    content_id: int | None = None
    properties: dict = Field(default_factory=dict)


class WechatLoginRequest(BaseModel):
    code: str = Field(min_length=1, max_length=256)
    nickname: str | None = Field(default=None, max_length=80)
    avatar_url: str | None = Field(default=None, max_length=500)


class WechatLoginResponse(BaseModel):
    open_id: str
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    user_id: int
    is_dev_mode: bool
    nickname: str | None = None
    avatar_url: str | None = None


class UserProfileResponse(BaseModel):
    user_id: int
    open_id: str
    nickname: str | None = None
    avatar_url: str | None = None


class UpdateUserProfileRequest(BaseModel):
    nickname: str | None = Field(default=None, max_length=80)
    avatar_url: str | None = Field(default=None, max_length=500)


class AvatarUploadResponse(BaseModel):
    avatar_url: str
