from pathlib import Path
from datetime import date
from dataclasses import asdict
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.schemas.admin import (
    AiImagePdfGenerateRequest,
    AiImagePdfGenerateResponse,
    AiModelCallLogDetail,
    AiModelCallLogListItem,
    AiPdfGenerateRequest,
    AiTopicSuggestionResponse,
    AiTopicSuggestionUpsertRequest,
    AdminUserPageResponse,
    ContentAdminResponse,
    ContentCreateRequest,
    ContentUpdateRequest,
    DashboardOverview,
    PreferenceOverview,
    PublishRequest,
    TaxonomyOptionsResponse,
    TaxonomyTagCreateRequest,
    TaxonomyTagResponse,
    TaxonomyTagUpdateRequest,
    TopicRecommendationContext,
)
from app.services.admin import AdminService
from app.tasks.generators import ImagePdfGenerationAgent, PdfGenerationInput

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard/overview", response_model=DashboardOverview)
def dashboard(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return AdminService(db).dashboard(start_date, end_date)


@router.get("/preferences", response_model=PreferenceOverview)
def preferences(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return AdminService(db).preferences(start_date, end_date)


@router.get("/contents", response_model=list[ContentAdminResponse])
def list_admin_contents(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    is_published: bool | None = Query(default=True),
    db: Session = Depends(get_db),
):
    return AdminService(db).list_contents(start_date, end_date, is_published)


@router.get("/users", response_model=AdminUserPageResponse)
def list_admin_users(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=5, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return AdminService(db).user_profiles(start_date, end_date, page, page_size)


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


@router.delete("/contents/{content_id}", status_code=204)
def delete_content(content_id: int, db: Session = Depends(get_db)):
    AdminService(db).delete_content(content_id)


@router.get("/taxonomy-tags", response_model=list[TaxonomyTagResponse])
def list_taxonomy_tags(db: Session = Depends(get_db)):
    return AdminService(db).taxonomy_tags()


@router.get("/taxonomy-options", response_model=TaxonomyOptionsResponse)
def taxonomy_options(db: Session = Depends(get_db)):
    return AdminService(db).taxonomy_options()


@router.post("/taxonomy-tags", response_model=TaxonomyTagResponse)
def create_taxonomy_tag(payload: TaxonomyTagCreateRequest, db: Session = Depends(get_db)):
    return AdminService(db).create_taxonomy_tag(payload)


@router.patch("/taxonomy-tags/{tag_id}", response_model=TaxonomyTagResponse)
def update_taxonomy_tag(tag_id: int, payload: TaxonomyTagUpdateRequest, db: Session = Depends(get_db)):
    return AdminService(db).update_taxonomy_tag(tag_id, payload)


@router.patch("/taxonomy-tags/{tag_type}/{tag_id}", response_model=TaxonomyTagResponse)
def update_taxonomy_tag_by_type(
    tag_type: str,
    tag_id: int,
    payload: TaxonomyTagUpdateRequest,
    db: Session = Depends(get_db),
):
    return AdminService(db).update_taxonomy_tag(tag_id, payload, tag_type)


@router.delete("/taxonomy-tags/{tag_type}/{tag_id}", status_code=204)
def delete_taxonomy_tag(tag_type: str, tag_id: int, db: Session = Depends(get_db)):
    AdminService(db).delete_taxonomy_tag(tag_id, tag_type)


@router.post("/ai/generate/image-pdf", response_model=AiImagePdfGenerateResponse)
def generate_image_pdf_content(payload: AiImagePdfGenerateRequest):
    data = payload.model_dump()
    page_count = data.pop("page_count")
    result = ImagePdfGenerationAgent().generate(PdfGenerationInput(**data), page_count=page_count)
    return AiImagePdfGenerateResponse(
        title=result.title,
        summary=result.summary,
        file_path=result.file_path,
        url=result.url,
        outline=result.outline,
        image_paths=result.image_paths,
        page_count=result.page_count,
        generation_source=result.generation_source,
        model=result.model,
        token_usage=asdict(result.token_usage),
        generation_error=result.generation_error,
        request_id=result.request_id,
        generation_steps=[asdict(step) for step in result.generation_steps],
    )


@router.get("/ai/topic-suggestions", response_model=list[AiTopicSuggestionResponse])
def topic_suggestions(db: Session = Depends(get_db)):
    return AdminService(db).topic_suggestions()


@router.post("/ai/topic-suggestions", response_model=AiTopicSuggestionResponse)
def create_topic_suggestion(payload: AiTopicSuggestionUpsertRequest, db: Session = Depends(get_db)):
    return AdminService(db).create_topic_suggestion(payload)


@router.get("/ai/topic-context", response_model=TopicRecommendationContext)
def topic_context(db: Session = Depends(get_db)):
    return AdminService(db).topic_recommendation_context()


@router.post("/ai/topic-suggestions/generate", response_model=list[AiTopicSuggestionResponse])
def generate_topic_suggestions(db: Session = Depends(get_db)):
    return AdminService(db).generate_ai_topic_suggestions()


@router.patch("/ai/topic-suggestions/{suggestion_id}", response_model=AiTopicSuggestionResponse)
def update_topic_suggestion(suggestion_id: int, payload: AiTopicSuggestionUpsertRequest, db: Session = Depends(get_db)):
    return AdminService(db).update_topic_suggestion(suggestion_id, payload)


@router.delete("/ai/topic-suggestions/{suggestion_id}", status_code=204)
def delete_topic_suggestion(suggestion_id: int, db: Session = Depends(get_db)):
    AdminService(db).delete_topic_suggestion(suggestion_id)


@router.get("/ai/model-call-logs", response_model=list[AiModelCallLogListItem])
def model_call_logs(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    request_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return AdminService(db).list_model_call_logs(start_date, end_date, request_id, status, limit)


@router.get("/ai/model-call-logs/{log_id}", response_model=AiModelCallLogDetail)
def model_call_log_detail(log_id: int, db: Session = Depends(get_db)):
    return AdminService(db).model_call_log_detail(log_id)
