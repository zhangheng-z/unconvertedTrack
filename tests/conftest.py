import os
from collections.abc import Generator
from urllib.parse import quote_plus

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings

settings = get_settings()
mysql_user = quote_plus(settings.mysql_user)
mysql_password = quote_plus(settings.mysql_password)
mysql_host = settings.mysql_host
mysql_port = settings.mysql_port
mysql_charset = settings.mysql_charset
test_mysql_database = quote_plus(os.getenv("TEST_MYSQL_DATABASE", settings.test_mysql_database))
TEST_DATABASE_URL = (
    f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{test_mysql_database}?charset={mysql_charset}"
)
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from app.database import Base, get_db


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:
        pytest.skip(f"MySQL test database is unavailable. Check MYSQL_USER, MYSQL_PASSWORD and TEST_MYSQL_DATABASE. Detail: {exc}")
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    from app.main import create_app

    app = create_app(create_tables=False)

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
