import os
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

test_database_path = Path(tempfile.gettempdir()) / "unconvertedTrack_test.db"
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", f"sqlite:///{test_database_path.as_posix()}")
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["WECHAT_APP_ID"] = ""
os.environ["WECHAT_APP_SECRET"] = ""

from app.database import Base, get_db


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine_kwargs = {}
    if TEST_DATABASE_URL.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    else:
        engine_kwargs["pool_pre_ping"] = True
    engine = create_engine(TEST_DATABASE_URL, **engine_kwargs)
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
