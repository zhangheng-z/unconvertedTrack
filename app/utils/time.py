from datetime import datetime
from zoneinfo import ZoneInfo

APP_TIMEZONE = ZoneInfo("Asia/Shanghai")


def now() -> datetime:
    return datetime.now(APP_TIMEZONE).replace(tzinfo=None)

