from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url_override: str = Field(default="", alias="DATABASE_URL")
    sqlite_database_path: str = "shiqu_data/app.db"
    local_file_base_url: str = "http://localhost:8000/files"
    local_file_root: str = "/shiqu_data/files"
    wechat_app_id: str = ""
    wechat_app_secret: str = ""
    jwt_secret_key: str = "change-me-in-production"
    jwt_expire_days: int = 30
    share_unlock_threshold: int = 1
    ai_topic_window_days: int = 7
    vectorengine_base_url: str = "https://api.vectorengine.ai"
    vectorengine_api_key: str = ""
    ai_text_model: str = "gpt5.5"
    ai_image_model: str = "gpt-image-2"
    ai_generation_timeout: int = 60
    ai_image_generation_timeout: int = 480
    ai_image_pdf_max_pages: int = 12

    @property
    def database_url(self) -> str:
        if self.database_url_override:
            return self.database_url_override
        sqlite_path = self.sqlite_database_path.replace("\\", "/")
        return f"sqlite:///{sqlite_path}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
