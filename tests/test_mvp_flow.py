from fastapi.testclient import TestClient


def create_and_publish_content(client: TestClient) -> int:
    response = client.post(
        "/admin/contents",
        json={
            "title": "一年级识字阅读自测表",
            "content_type": "pdf",
            "subject": "语文",
            "problem": "识字阅读",
            "target_age_min": 6,
            "target_age_max": 8,
            "grade": "一年级",
            "summary": "识字阅读资料",
            "file_path": "materials/reading.pdf",
            "next_action": "测评",
            "next_action_url": "/assessment/reading",
            "tags": ["语文", "一年级"],
        },
    )
    assert response.status_code == 200
    content_id = response.json()["id"]
    publish = client.patch(f"/admin/contents/{content_id}/publish", json={"is_published": True})
    assert publish.status_code == 200
    return content_id


def test_parent_mvp_loop_and_admin_metrics(client: TestClient):
    content_id = create_and_publish_content(client)

    onboard = client.post(
        "/api/v1/onboarding/profile",
        json={
            "open_id": "parent-001",
            "nickname": "家长A",
            "source_channel": "douyin",
            "child_age": 7,
            "child_grade": "一年级",
            "concerns": ["识字阅读"],
        },
    )
    assert onboard.status_code == 200
    assert "识字阅读" in onboard.json()["tags"]

    contents = client.get("/api/v1/contents", params={"open_id": "parent-001", "age": 7, "grade": "一年级", "subject": "语文"})
    assert contents.status_code == 200
    assert [item["id"] for item in contents.json()] == [content_id]

    detail = client.get(f"/api/v1/contents/{content_id}", params={"open_id": "parent-001"})
    assert detail.status_code == 200
    assert detail.json()["is_claimed"] is False

    claim = client.post(f"/api/v1/contents/{content_id}/claim", params={"open_id": "parent-001"})
    assert claim.status_code == 200
    assert claim.json()["claimed"] is True

    download = client.post(f"/api/v1/contents/{content_id}/download", params={"open_id": "parent-001"})
    assert download.status_code == 200
    assert download.json()["download_url"].endswith("/materials/reading.pdf")

    share = client.post(f"/api/v1/contents/{content_id}/share", params={"open_id": "parent-001"})
    assert share.status_code == 200
    assert share.json()["unlocked"] is True

    assets = client.get("/api/v1/me/assets", params={"open_id": "parent-001"})
    assert assets.status_code == 200
    assert assets.json()[0]["content_id"] == content_id

    dashboard = client.get("/admin/dashboard/overview")
    assert dashboard.status_code == 200
    assert dashboard.json()["claimed"] == 1
    assert dashboard.json()["downloaded"] == 1
    assert dashboard.json()["shared"] == 1


def test_ai_topic_suggestion_uses_recent_preferences(client: TestClient):
    content_id = create_and_publish_content(client)
    client.post(
        "/api/v1/onboarding/profile",
        json={
            "open_id": "parent-002",
            "child_age": 7,
            "child_grade": "一年级",
            "concerns": ["识字阅读"],
        },
    )
    client.get(f"/api/v1/contents/{content_id}", params={"open_id": "parent-002"})
    client.post(f"/api/v1/contents/{content_id}/claim", params={"open_id": "parent-002"})

    response = client.get("/admin/ai/topic-suggestions")
    assert response.status_code == 200
    suggestions = response.json()
    assert suggestions
    assert "语文" in suggestions[0]["title"]
    assert suggestions[0]["status"] == "draft"


def test_claim_is_idempotent(client: TestClient):
    content_id = create_and_publish_content(client)
    client.post(
        "/api/v1/onboarding/profile",
        json={"open_id": "parent-003", "child_age": 7, "child_grade": "一年级", "concerns": []},
    )

    first = client.post(f"/api/v1/contents/{content_id}/claim", params={"open_id": "parent-003"})
    second = client.post(f"/api/v1/contents/{content_id}/claim", params={"open_id": "parent-003"})

    assert first.status_code == 200
    assert second.status_code == 200
    assets = client.get("/api/v1/me/assets", params={"open_id": "parent-003"}).json()
    assert len(assets) == 1

