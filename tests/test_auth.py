from fastapi.testclient import TestClient


def test_dev_wechat_login_returns_token(client: TestClient):
    response = client.post("/api/v1/auth/wechat-login", json={"code": "dev-code-001", "nickname": "家长"})

    assert response.status_code == 200
    data = response.json()
    assert data["open_id"] == "dev-dev-code-001"
    assert data["access_token"]
    assert data["token_type"] == "Bearer"
    assert data["expires_in"] > 0
    assert data["user_id"] > 0
    assert data["is_dev_mode"] is True


def test_token_allows_me_assets_without_open_id(client: TestClient):
    login = client.post("/api/v1/auth/wechat-login", json={"code": "dev-code-002"}).json()

    response = client.get(
        "/api/v1/me/assets",
        headers={"Authorization": f"Bearer {login['access_token']}"},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_me_assets_requires_login_without_legacy_open_id(client: TestClient):
    response = client.get("/api/v1/me/assets")

    assert response.status_code == 401


def test_can_update_and_read_wechat_profile(client: TestClient):
    login = client.post("/api/v1/auth/wechat-login", json={"code": "dev-code-profile"}).json()
    headers = {"Authorization": f"Bearer {login['access_token']}"}

    update = client.patch(
        "/api/v1/me/profile",
        json={"nickname": "家长A", "avatar_url": "http://localhost:8000/files/avatars/a.jpg"},
        headers=headers,
    )

    assert update.status_code == 200
    assert update.json()["nickname"] == "家长A"
    assert update.json()["avatar_url"] == "http://localhost:8000/files/avatars/a.jpg"

    profile = client.get("/api/v1/me/profile", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["nickname"] == "家长A"
    assert profile.json()["avatar_url"] == "http://localhost:8000/files/avatars/a.jpg"
