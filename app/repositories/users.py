from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Child, User, UserTag


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_open_id(self, open_id: str) -> User | None:
        return self.db.scalar(select(User).where(User.open_id == open_id))

    def get_or_create(
        self,
        open_id: str,
        nickname: str | None = None,
        avatar_url: str | None = None,
        source_channel: str | None = None,
    ) -> User:
        user = self.get_by_open_id(open_id)
        if user is None:
            user = User(open_id=open_id, nickname=nickname, avatar_url=avatar_url, source_channel=source_channel)
            self.db.add(user)
            self.db.flush()
        else:
            if nickname is not None:
                user.nickname = nickname
            if avatar_url is not None:
                user.avatar_url = avatar_url
            if source_channel is not None:
                user.source_channel = source_channel
        return user

    def update_wechat_profile(
        self,
        user: User,
        nickname: str | None = None,
        avatar_url: str | None = None,
    ) -> User:
        if nickname is not None:
            user.nickname = nickname
        if avatar_url is not None:
            user.avatar_url = avatar_url
        self.db.flush()
        return user

    def upsert_profile(
        self,
        open_id: str,
        nickname: str | None,
        source_channel: str | None,
        child_age: int,
        child_grade: str,
        concerns: list[str],
    ) -> tuple[User, Child, list[UserTag]]:
        user = self.get_by_open_id(open_id)
        if user is None:
            user = User(open_id=open_id)
            self.db.add(user)
            self.db.flush()
        user.nickname = nickname
        user.source_channel = source_channel

        child = user.children[0] if user.children else Child(user_id=user.id, age=child_age, grade=child_grade)
        child.age = child_age
        child.grade = child_grade
        self.db.add(child)

        self.db.query(UserTag).filter(UserTag.user_id == user.id).delete()
        tags = [
            UserTag(user_id=user.id, tag_type="age", tag_value=str(child_age)),
            UserTag(user_id=user.id, tag_type="grade", tag_value=child_grade),
        ]
        tags.extend(UserTag(user_id=user.id, tag_type="concern", tag_value=concern) for concern in concerns)
        self.db.add_all(tags)
        self.db.flush()
        return user, child, tags
