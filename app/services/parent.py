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
    InviteCompleteRequest,
    InviteCompleteResponse,
    InviteSummary,
    MyAsset,
    OnboardingProfileRequest,
    OnboardingProfileResponse,
    ShareOpenRequest,
    ShareOpenResponse,
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
        _user, child, tags = self.users.upsert_profile(
            open_id=open_id,
            nickname=payload.nickname,
            source_channel=payload.source_channel,
            child_age=payload.child_age,
            child_grade=payload.child_grade,
            concerns=payload.concerns,
        )
        self.db.commit()
        return OnboardingProfileResponse(user_id=child.user_id, child_id=child.id, tags=[tag.tag_value for tag in tags])

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
        contents = self.contents.list_published(age, grade, subject, problem, content_type, sort)
        metrics = self.contents.content_metrics([content.id for content in contents])
        assets = self.contents.assets_for_contents(user.id, [content.id for content in contents]) if user else {}
        invited_count = self.contents.completed_invite_count(user.id) if user else 0
        if user:
            self.contents.unlock_eligible_invite_assets(user.id, invited_count)
            self.db.commit()
        return [
            self._content_list_item(content, metrics.get(content.id, {}), assets.get(content.id), invited_count)
            for content in contents
        ]

    def detail(self, open_id: str | None, content_id: int, current_user: User | None = None) -> ContentDetail:
        user = current_user or self._require_user(open_id)
        content = self._require_content(content_id, published_only=True)
        invited_count = self.contents.completed_invite_count(user.id)
        self.contents.unlock_eligible_invite_assets(user.id, invited_count)
        asset = self.contents.get_asset(user.id, content_id)
        metrics = self.contents.content_metrics([content.id]).get(content.id, {})
        self.db.commit()
        return ContentDetail(
            **self._content_list_item(content, metrics, asset, invited_count).model_dump(),
            file_path=content.file_path,
            next_action_url=content.next_action_url,
        )

    def claim(self, open_id: str | None, content_id: int, current_user: User | None = None) -> ClaimResponse:
        user = current_user or self._require_user(open_id)
        content = self._require_content(content_id, published_only=True)
        child = user.children[0] if user.children else None
        invited_count = self.contents.completed_invite_count(user.id)
        self.contents.unlock_eligible_invite_assets(user.id, invited_count)
        asset = self.contents.claim_asset(
            user.id,
            content.id,
            unlocked=self._is_free_content(content) or self._has_invite_access(content, invited_count),
        )
        self.contents.record_event("claim", user.id, child.id if child else None, content.id, properties={"age": child.age if child else None})
        self.db.commit()
        return ClaimResponse(content_id=content.id, claimed=True, unlocked=asset.unlocked)

    def download(self, open_id: str | None, content_id: int, current_user: User | None = None) -> DownloadResponse:
        user = current_user or self._require_user(open_id)
        content = self._require_content(content_id, published_only=True)
        child = user.children[0] if user.children else None
        invited_count = self.contents.completed_invite_count(user.id)
        self.contents.unlock_eligible_invite_assets(user.id, invited_count)
        has_access = self._is_free_content(content) or self._has_invite_access(content, invited_count)
        asset = self.contents.get_asset(user.id, content.id)
        if asset is None and has_access:
            asset = self.contents.claim_asset(user.id, content.id, unlocked=True)
        if asset is None:
            raise HTTPException(status_code=403, detail="content is locked")
        if not asset.unlocked and has_access:
            asset.unlocked = True
        if not asset.unlocked:
            raise HTTPException(status_code=403, detail="content is locked")
        self.contents.record_event("download", user.id, child.id if child else None, content.id, properties={"age": child.age if child else None})
        self.db.commit()
        return DownloadResponse(content_id=content.id, download_url=self.files.download_url(content.file_path))

    def share(self, open_id: str | None, content_id: int, current_user: User | None = None) -> ShareResponse:
        user = current_user or self._require_user(open_id)
        content = self._require_content(content_id, published_only=True)
        child = user.children[0] if user.children else None
        invited_count = self.contents.completed_invite_count(user.id)
        asset = self.contents.get_asset(user.id, content.id)
        if asset is not None:
            asset.share_count += 1
        self.contents.record_event("share", user.id, child.id if child else None, content.id, properties={"age": child.age if child else None})
        self.db.commit()
        unlocked = bool(asset and asset.unlocked) or self._is_free_content(content) or self._has_invite_access(content, invited_count)
        return ShareResponse(content_id=content.id, share_count=asset.share_count if asset else 0, unlocked=unlocked)

    def record_share_open(self, payload: ShareOpenRequest) -> ShareOpenResponse:
        inviter = self.db.get(User, payload.inviter_user_id)
        content = self._require_content(payload.source_content_id, published_only=True)
        if inviter is None:
            return ShareOpenResponse(recorded=False)
        self.contents.record_event(
            "share",
            inviter.id,
            None,
            content.id,
            properties={"stage": "open"},
        )
        self.db.commit()
        return ShareOpenResponse(recorded=True)

    def complete_invite(self, payload: InviteCompleteRequest, current_user: User) -> InviteCompleteResponse:
        if payload.inviter_user_id == current_user.id:
            invited_count = self.contents.completed_invite_count(current_user.id)
            return InviteCompleteResponse(completed=False, invited_count=invited_count)
        inviter = self.db.get(User, payload.inviter_user_id)
        if inviter is None:
            raise HTTPException(status_code=404, detail="inviter not found")
        completed = self.contents.complete_invite(payload.inviter_user_id, current_user.id, payload.source_content_id)
        invited_count = self.contents.completed_invite_count(payload.inviter_user_id)
        self.contents.unlock_eligible_invite_assets(payload.inviter_user_id, invited_count)
        self.db.commit()
        return InviteCompleteResponse(completed=completed, invited_count=invited_count)

    def my_assets(self, open_id: str | None, current_user: User | None = None) -> list[MyAsset]:
        user = current_user or self._require_user(open_id)
        rows = self.contents.list_assets(user.id)
        metrics = self.contents.content_metrics([content.id for _asset, content in rows])
        return [
            MyAsset(
                content_id=content.id,
                title=content.title,
                content_type=content.content_type,
                unlocked=asset.unlocked,
                share_count=metrics.get(content.id, {}).get("share_count", 0),
            )
            for asset, content in rows
        ]

    def invite_summary(self, open_id: str | None, current_user: User | None = None) -> InviteSummary:
        user = current_user or self._require_user(open_id)
        invited_count = self.contents.completed_invite_count(user.id)
        self.contents.unlock_eligible_invite_assets(user.id, invited_count)
        unlockable_count = self.contents.locked_invite_asset_count(user.id, invited_count)
        self.db.commit()
        if invited_count <= 0:
            display_text = "已邀请0位家长，仅可领取部分免费资料"
        elif unlockable_count > 0:
            display_text = f"已邀请{invited_count}位家长，可解锁{unlockable_count}份高级资料"
        else:
            display_text = f"已邀请{invited_count}位家长，可领取全部资料"
        return InviteSummary(invited_count=invited_count, unlockable_count=unlockable_count, display_text=display_text)

    def record_event(self, open_id: str | None, event_type: str, content_id: int | None, properties: dict, current_user: User | None = None) -> None:
        supported_events = {"claim", "share", "download", "assessment", "assessment_complete", "camp", "camp_signup", "training", "lead"}
        if event_type not in supported_events:
            raise HTTPException(status_code=400, detail="unsupported content event type")
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

    @staticmethod
    def _is_free_content(content) -> bool:
        return (content.unlock_type or "free") == "free"

    @staticmethod
    def _unlock_threshold(content) -> int:
        if (content.unlock_type or "free") == "free":
            return 0
        return content.unlock_threshold or get_settings().share_unlock_threshold

    @classmethod
    def _has_invite_access(cls, content, invited_count: int) -> bool:
        return (content.unlock_type or "free") == "invite" and invited_count >= cls._unlock_threshold(content)

    @classmethod
    def _content_list_item(cls, content, metrics: dict[str, int], asset=None, invited_count: int = 0) -> ContentListItem:
        has_invite_access = cls._has_invite_access(content, invited_count)
        return ContentListItem(
            id=content.id,
            title=content.title,
            content_type=content.content_type,
            subject=content.subject,
            problem=content.problem,
            problem_tags=cls._content_problem_tags(content),
            cover_url=content.cover_url,
            summary=content.summary,
            next_action=content.next_action,
            unlock_type=content.unlock_type or "free",
            unlock_threshold=cls._unlock_threshold(content),
            is_claimed=asset is not None,
            is_unlocked=bool(asset and asset.unlocked) or has_invite_access,
            user_share_count=invited_count if (content.unlock_type or "free") == "invite" else (asset.share_count if asset else 0),
            claim_count=metrics.get("claim_count", 0),
            share_count=metrics.get("share_count", 0),
            effective_share_count=metrics.get("effective_share_count", 0),
            lead_count=metrics.get("lead_count", 0),
        )

    @staticmethod
    def _content_problem_tags(content) -> list[str]:
        values = []
        seen = set()
        for tag in content.tags:
            if tag.tag_type != "problem":
                continue
            value = str(tag.tag_value or "").strip()
            if not value or value in seen:
                continue
            seen.add(value)
            values.append(value)
        if not values and content.problem:
            values.append(content.problem)
        return values
