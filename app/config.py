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
    local_file_root: str = "storage/files"
    wechat_app_id: str = ""
    wechat_app_secret: str = ""
    jwt_secret_key: str = "change-me-in-production"
    jwt_expire_days: int = 30
    share_unlock_threshold: int = 1
    ai_topic_window_days: int = 7

    @property
    def database_url(self) -> str:
        user = quote_plus(self.mysql_user)
        password = quote_plus(self.mysql_password)
        database = quote_plus(self.mysql_database)
        return f"mysql+pymysql://{user}:{password}@{self.mysql_host}:{self.mysql_port}/{database}?charset={self.mysql_charset}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
