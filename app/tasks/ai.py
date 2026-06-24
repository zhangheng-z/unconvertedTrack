from sqlalchemy.orm import Session

from app.services.admin import AdminService


def generate_topic_suggestions(db: Session) -> None:
    AdminService(db).generate_topic_suggestions()

