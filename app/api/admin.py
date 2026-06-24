from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.schemas.admin import (
    AiTopicSuggestionResponse,
    ContentAdminResponse,
    ContentCreateRequest,
    ContentUpdateRequest,
    DashboardOverview,
    PreferenceOverview,
    PublishRequest,
)
from app.services.admin import AdminService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard/overview", response_model=DashboardOverview)
def dashboard(db: Session = Depends(get_db)):
    return AdminService(db).dashboard()


@router.get("/preferences", response_model=PreferenceOverview)
def preferences(db: Session = Depends(get_db)):
    return AdminService(db).preferences()


@router.get("/contents", response_model=list[ContentAdminResponse])
def list_admin_contents(db: Session = Depends(get_db)):
    return AdminService(db).list_contents()


@router.post("/contents", response_model=ContentAdminResponse)
def create_content(payload: ContentCreateRequest, db: Session = Depends(get_db)):
    return AdminService(db).create_content(payload)


@router.post("/files")
def upload_file(file: UploadFile = File(...)):
    settings = get_settings()
    suffix = Path(file.filename or "").suffix.lower()
    safe_name = f"{uuid4().hex}{suffix}"
    relative_path = f"materials/{safe_name}"
    target = Path(settings.local_file_root) / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as output:
        output.write(file.file.read())
    return {
        "file_path": relative_path,
        "url": f"{settings.local_file_base_url.rstrip('/')}/{relative_path}",
    }


@router.patch("/contents/{content_id}", response_model=ContentAdminResponse)
def update_content(content_id: int, payload: ContentUpdateRequest, db: Session = Depends(get_db)):
    return AdminService(db).update_content(content_id, payload)


@router.patch("/contents/{content_id}/publish", response_model=ContentAdminResponse)
def publish_content(content_id: int, payload: PublishRequest, db: Session = Depends(get_db)):
    return AdminService(db).publish_content(content_id, payload.is_published)


@router.get("/ai/topic-suggestions", response_model=list[AiTopicSuggestionResponse])
def topic_suggestions(db: Session = Depends(get_db)):
    return AdminService(db).topic_suggestions()
