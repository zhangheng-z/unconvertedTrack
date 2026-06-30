from functools import lru_cache
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_database: str = "unconvertedTrack"
    test_mysql_database: str = "unconvertedTrack_test"
    mysql_user: str = "root"
    mysql_password: str = "root"
    mysql_charset: str = "utf8mb4"
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
        user = quote_plus(self.mysql_user)
        password = quote_plus(self.mysql_password)
        database = quote_plus(self.mysql_database)
        return f"mysql+pymysql://{user}:{password}@{self.mysql_host}:{self.mysql_port}/{database}?charset={self.mysql_charset}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
