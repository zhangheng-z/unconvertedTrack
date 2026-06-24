from app.config import get_settings


class FileStorage:
    def download_url(self, file_path: str | None) -> str:
        if not file_path:
            return ""
        if file_path.startswith(("http://", "https://")):
            return file_path
        base_url = get_settings().local_file_base_url.rstrip("/")
        return f"{base_url}/{file_path.lstrip('/')}"
