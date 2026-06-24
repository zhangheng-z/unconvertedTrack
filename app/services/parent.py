from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import User
from app.repositories.contents import ContentRepository
from app.repositories.users import UserRepository
from app.schemas.parent import (
    ClaimResponse,
    ContentDetail,
    ContentListItem,
    DownloadResponse,
    MyAsset,
    OnboardingProfileRequest,
    OnboardingProfileResponse,
    ShareResponse,
)
from app.services.files import FileStorage


class ParentService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.contents = ContentRepository(db)
        self.files = FileStorage()

    def onboard(self, payload: OnboardingProfileRequest, current_user: User | None = None) -> OnboardingProfileResponse:
        open_id = current_user.open_id if current_user else payload.open_id
        user, child, tags = self.users.upsert_profile(
            open_id=open_id,
            nickname=payload.nickname,
            source_channel=payload.source_channel,
            child_age=payload.child_age,
            child_grade=payload.child_grade,
            concerns=payload.concerns,
        )
        self.contents.record_event(
            event_type="onboarding",
            user_id=user.id,
            child_id=child.id,
            source_channel=payload.source_channel,
            properties={"age": child.age, "grade": child.grade, "concerns": payload.concerns},
        )
        self.db.commit()
        return OnboardingProfileResponse(user_id=user.id, child_id=child.id, tags=[tag.tag_value for tag in tags])

    def list_contents(
        self,
        open_id: str | None,
        age: int | None,
        grade: str | None,
        subject: str | None,
        problem: str | None,
        content_type: str | None,
        sort: str,
        current_user: User | None = None,
    ) -> list[ContentListItem]:
        user = current_user or (self.users.get_by_open_id(open_id) if open_id else None)
        child = user.children[0] if user and user.children else None
        contents = self.contents.list_published(age, grade, subject, problem, content_type, sort)
        if user:
            self.contents.record_event(
                event_type="filter",
                user_id=user.id,
                child_id=child.id if child else None,
                properties={"age": age, "grade": grade, "subject": subject, "problem": problem, "content_type": content_type},
            )
            self.db.commit()
        return [ContentListItem.model_validate(content) for content in contents]

    def detail(self, open_id: str | None, content_id: int, current_user: User | None = None) -> ContentDetail:
        user = current_user or self._require_user(open_id)
        content = self._require_content(content_id, published_only=True)
        child = user.children[0] if user.children else None
        asset = self.contents.get_asset(user.id, content_id)
        self.contents.record_event("click", user.id, child.id if child else None, content_id, properties={"age": child.age if child else None})
        self.db.commit()
        return ContentDetail(
            id=content.id,
            title=content.title,
            content_type=content.content_type,
            subject=content.subject,
            problem=content.problem,
            cover_url=content.cover_url,
            summary=content.summary,
            next_action=content.next_action,
            file_path=content.file_path,
            next_action_url=content.next_action_url,
            is_claimed=asset is not None,
            is_unlocked=bool(asset and asset.unlocked),
        )

    def claim(self, open_id: str | None, content_id: int, current_user: User | None = None) -> ClaimResponse:
        user = current_user or self._require_user(open_id)
        content = self._require_content(content_id, published_only=True)
        child = user.children[0] if user.children else None
        asset = self.contents.claim_asset(user.id, content.id)
        self.contents.record_event("claim", user.id, child.id if child else None, content.id, properties={"age": child.age if child else None})
        self.db.commit()
        return ClaimResponse(content_id=content.id, claimed=True, unlocked=asset.unlocked)

    def download(self, open_id: str | None, content_id: int, current_user: User | None = None) -> DownloadResponse:
        user = current_user or self._require_user(open_id)
        content = self._require_content(content_id, published_only=True)
        child = user.children[0] if user.children else None
        asset = self.contents.claim_asset(user.id, content.id)
        if not asset.unlocked:
            raise HTTPException(status_code=403, detail="content is locked")
        self.contents.record_event("download", user.id, child.id if child else None, content.id, properties={"age": child.age if child else None})
        self.db.commit()
        return DownloadResponse(content_id=content.id, download_url=self.files.download_url(content.file_path))

    def share(self, open_id: str | None, content_id: int, current_user: User | None = None) -> ShareResponse:
        user = current_user or self._require_user(open_id)
        content = self._require_content(content_id, published_only=True)
        child = user.children[0] if user.children else None
        asset = self.contents.claim_asset(user.id, content.id)
        asset.share_count += 1
        if asset.share_count >= get_settings().share_unlock_threshold:
            asset.unlocked = True
        self.contents.record_event("share", user.id, child.id if child else None, content.id, properties={"age": child.age if child else None})
        self.db.commit()
        return ShareResponse(content_id=content.id, share_count=asset.share_count, unlocked=asset.unlocked)

    def my_assets(self, open_id: str | None, current_user: User | None = None) -> list[MyAsset]:
        user = current_user or self._require_user(open_id)
        rows = self.contents.list_assets(user.id)
        return [
            MyAsset(content_id=content.id, title=content.title, content_type=content.content_type, unlocked=asset.unlocked, share_count=asset.share_count)
            for asset, content in rows
        ]

    def record_event(self, open_id: str | None, event_type: str, content_id: int | None, properties: dict, current_user: User | None = None) -> None:
        user = current_user or self._require_user(open_id)
        child = user.children[0] if user.children else None
        self.contents.record_event(event_type, user.id, child.id if child else None, content_id, properties=properties)
        self.db.commit()

    def _require_user(self, open_id: str | None):
        if not open_id:
            raise HTTPException(status_code=401, detail="login required")
        user = self.users.get_by_open_id(open_id)
        if user is None:
            raise HTTPException(status_code=404, detail="user not found")
        return user

    def _require_content(self, content_id: int, published_only: bool = False):
        content = self.contents.get(content_id)
        if content is None or (published_only and not content.is_published):
            raise HTTPException(status_code=404, detail="content not found")
        return content
