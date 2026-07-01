from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text

from app.api.admin import router as admin_router
from app.api.parent import router as parent_router
from app.config import get_settings
from app.database import Base, engine


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "avatar_url" not in columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE users ADD COLUMN avatar_url VARCHAR(500) NULL"))
    content_columns = {column["name"] for column in inspector.get_columns("contents")}
    with engine.begin() as connection:
        if "unlock_type" not in content_columns:
            connection.execute(text("ALTER TABLE contents ADD COLUMN unlock_type VARCHAR(40) NOT NULL DEFAULT 'free'"))
        if "unlock_threshold" not in content_columns:
            connection.execute(text("ALTER TABLE contents ADD COLUMN unlock_threshold INT NOT NULL DEFAULT 0"))
    if "taxonomy_tags" in inspector.get_table_names():
        taxonomy_columns = {column["name"] for column in inspector.get_columns("taxonomy_tags")}
        if "parent_id" not in taxonomy_columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE taxonomy_tags ADD COLUMN parent_id INT NULL"))


def create_app(create_tables: bool = True) -> FastAPI:
    if create_tables:
        init_db()
    app = FastAPI(title="Unconverted User Value MVP", version="0.1.0")
    app.include_router(parent_router)
    app.include_router(admin_router)
    settings = get_settings()
    Path(settings.local_file_root).mkdir(parents=True, exist_ok=True)
    app.mount("/files", StaticFiles(directory=settings.local_file_root), name="files")
    app.mount("/admin-ui", StaticFiles(directory="web/admin", html=True), name="admin-ui")

    @app.get("/")
    def root():
        return RedirectResponse(url="/admin-ui/")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
