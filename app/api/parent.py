from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.dependencies.auth import get_current_user, get_optional_user
from app.models import User
from app.repositories.users import UserRepository
from app.schemas.parent import (
    AvatarUploadResponse,
    ClaimResponse,
    ContentDetail,
    ContentListItem,
    DownloadResponse,
    EventCreateRequest,
    InviteCompleteRequest,
    InviteCompleteResponse,
    InviteSummary,
    MyAsset,
    OnboardingProfileRequest,
    OnboardingProfileResponse,
    ShareOpenRequest,
    ShareOpenResponse,
    ShareResponse,
    UpdateUserProfileRequest,
    UserProfileResponse,
    WechatLoginRequest,
    WechatLoginResponse,
)
from app.services.auth import AuthService
from app.services.files import FileStorage
from app.services.parent import ParentService

router = APIRouter(prefix="/api/v1", tags=["parent"])


@router.post("/auth/wechat-login", response_model=WechatLoginResponse)
def wechat_login(payload: WechatLoginRequest, db: Session = Depends(get_db)):
    user, token, expires_in, is_dev_mode = AuthService(db).wechat_login(
        payload.code,
        payload.nickname,
        payload.avatar_url,
    )
    return WechatLoginResponse(
        open_id=user.open_id,
        access_token=token,
        expires_in=expires_in,
        user_id=user.id,
        is_dev_mode=is_dev_mode,
        nickname=user.nickname,
        avatar_url=user.avatar_url,
    )


@router.get("/me/profile", response_model=UserProfileResponse)
def my_profile(current_user: User = Depends(get_current_user)):
    return UserProfileResponse(
        user_id=current_user.id,
        open_id=current_user.open_id,
        nickname=current_user.nickname,
        avatar_url=current_user.avatar_url,
    )


@router.patch("/me/profile", response_model=UserProfileResponse)
def update_my_profile(
    payload: UpdateUserProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = UserRepository(db).update_wechat_profile(
        current_user,
        nickname=payload.nickname,
        avatar_url=payload.avatar_url,
    )
    db.commit()
    return UserProfileResponse(
        user_id=user.id,
        open_id=user.open_id,
        nickname=user.nickname,
        avatar_url=user.avatar_url,
    )


@router.post("/me/avatar", response_model=AvatarUploadResponse)
async def upload_my_avatar(
    avatar: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    suffix = Path(avatar.filename or "").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        suffix = ".jpg"
    relative_path = f"avatars/{uuid4().hex}{suffix}"
    storage_root = Path(get_settings().local_file_root)
    file_path = storage_root / relative_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(await avatar.read())

    avatar_url = FileStorage().download_url(relative_path)
    UserRepository(db).update_wechat_profile(current_user, avatar_url=avatar_url)
    db.commit()
    return AvatarUploadResponse(avatar_url=avatar_url)


@router.post("/onboarding/profile", response_model=OnboardingProfileResponse)
def onboard(
    payload: OnboardingProfileRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    return ParentService(db).onboard(payload, current_user)


@router.get("/contents", response_model=list[ContentListItem])
def list_contents(
    open_id: str | None = None,
    age: int | None = Query(default=None, ge=0, le=18),
    grade: str | None = None,
    subject: str | None = None,
    problem: str | None = None,
    content_type: str | None = None,
    sort: str = "smart",
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    return ParentService(db).list_contents(open_id, age, grade, subject, problem, content_type, sort, current_user)


@router.get("/contents/{content_id}", response_model=ContentDetail)
def content_detail(
    content_id: int,
    open_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    return ParentService(db).detail(open_id, content_id, current_user)


@router.post("/contents/{content_id}/claim", response_model=ClaimResponse)
def claim_content(
    content_id: int,
    open_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    return ParentService(db).claim(open_id, content_id, current_user)


@router.post("/contents/{content_id}/download", response_model=DownloadResponse)
def download_content(
    content_id: int,
    open_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    return ParentService(db).download(open_id, content_id, current_user)


@router.post("/contents/{content_id}/share", response_model=ShareResponse)
def share_content(
    content_id: int,
    open_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    return ParentService(db).share(open_id, content_id, current_user)


@router.post("/shares/open", response_model=ShareOpenResponse)
def record_share_open(payload: ShareOpenRequest, db: Session = Depends(get_db)):
    return ParentService(db).record_share_open(payload)


@router.get("/me/assets", response_model=list[MyAsset])
def my_assets(
    open_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    return ParentService(db).my_assets(open_id, current_user)


@router.get("/me/invite-summary", response_model=InviteSummary)
def invite_summary(
    open_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    return ParentService(db).invite_summary(open_id, current_user)


@router.post("/invites/complete", response_model=InviteCompleteResponse)
def complete_invite(
    payload: InviteCompleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ParentService(db).complete_invite(payload, current_user)


@router.post("/events", status_code=204)
def record_event(
    payload: EventCreateRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    ParentService(db).record_event(payload.open_id, payload.event_type, payload.content_id, payload.properties, current_user)
