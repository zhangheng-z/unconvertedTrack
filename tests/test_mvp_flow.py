from fastapi.testclient import TestClient


def create_and_publish_content(
    client: TestClient,
    unlock_type: str = "free",
    unlock_threshold: int = 0,
    title: str = "一年级识字阅读自测表",
) -> int:
    response = client.post(
        "/admin/contents",
        json={
            "title": title,
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
            "unlock_type": unlock_type,
            "unlock_threshold": unlock_threshold,
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
    assert contents.json()[0]["unlock_type"] == "free"
    assert contents.json()[0]["is_unlocked"] is False
    assert contents.json()[0]["claim_count"] == 0
    assert contents.json()[0]["share_count"] == 0
    assert contents.json()[0]["lead_count"] == 0

    detail = client.get(f"/api/v1/contents/{content_id}", params={"open_id": "parent-001"})
    assert detail.status_code == 200
    assert detail.json()["is_claimed"] is False

    claim = client.post(f"/api/v1/contents/{content_id}/claim", params={"open_id": "parent-001"})
    assert claim.status_code == 200
    assert claim.json()["claimed"] is True
    assert claim.json()["unlocked"] is True

    download = client.post(f"/api/v1/contents/{content_id}/download", params={"open_id": "parent-001"})
    assert download.status_code == 200
    assert download.json()["download_url"].endswith("/materials/reading.pdf")

    share = client.post(f"/api/v1/contents/{content_id}/share", params={"open_id": "parent-001"})
    assert share.status_code == 200
    assert share.json()["unlocked"] is True

    updated_detail = client.get(f"/api/v1/contents/{content_id}", params={"open_id": "parent-001"})
    assert updated_detail.status_code == 200
    assert updated_detail.json()["claim_count"] == 1
    assert updated_detail.json()["share_count"] == 1
    assert updated_detail.json()["lead_count"] == 0

    unsupported_event = client.post(
        "/api/v1/events",
        json={"open_id": "parent-001", "event_type": "filter", "content_id": content_id, "properties": {}},
    )
    assert unsupported_event.status_code == 400

    assets = client.get("/api/v1/me/assets", params={"open_id": "parent-001"})
    assert assets.status_code == 200
    assert assets.json()[0]["content_id"] == content_id

    admin_contents = client.get("/admin/contents")
    assert admin_contents.status_code == 200
    assert admin_contents.json()[0]["claim_count"] == 1
    assert admin_contents.json()[0]["share_count"] == 1
    assert admin_contents.json()[0]["lead_count"] == 0

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


def test_invite_unlock_applies_to_all_invite_contents_for_parent(client: TestClient):
    first_id = create_and_publish_content(client, unlock_type="invite", unlock_threshold=1, title="邀请解锁资料A")
    second_id = create_and_publish_content(client, unlock_type="invite", unlock_threshold=1, title="邀请解锁资料B")
    client.post(
        "/api/v1/onboarding/profile",
        json={"open_id": "parent-invite-a", "child_age": 7, "child_grade": "一年级", "concerns": []},
    )
    client.post(
        "/api/v1/onboarding/profile",
        json={"open_id": "parent-invite-b", "child_age": 7, "child_grade": "一年级", "concerns": []},
    )

    claim_a = client.post(f"/api/v1/contents/{first_id}/claim", params={"open_id": "parent-invite-a"})
    assert claim_a.status_code == 200
    assert claim_a.json()["unlocked"] is False

    share_a = client.post(f"/api/v1/contents/{first_id}/share", params={"open_id": "parent-invite-a"})
    assert share_a.status_code == 200
    assert share_a.json()["unlocked"] is True

    contents_a = client.get("/api/v1/contents", params={"open_id": "parent-invite-a", "age": 7, "grade": "一年级"})
    by_id_a = {item["id"]: item for item in contents_a.json()}
    assert by_id_a[first_id]["is_unlocked"] is True
    assert by_id_a[second_id]["is_unlocked"] is True
    assert by_id_a[second_id]["is_claimed"] is False

    contents_b = client.get("/api/v1/contents", params={"open_id": "parent-invite-b", "age": 7, "grade": "一年级"})
    by_id_b = {item["id"]: item for item in contents_b.json()}
    assert by_id_b[first_id]["is_unlocked"] is False
    assert by_id_b[second_id]["is_unlocked"] is False

    download_second_a = client.post(f"/api/v1/contents/{second_id}/download", params={"open_id": "parent-invite-a"})
    download_second_b = client.post(f"/api/v1/contents/{second_id}/download", params={"open_id": "parent-invite-b"})
    assert download_second_a.status_code == 200
    assert download_second_b.status_code == 403


def test_invite_summary_copy_changes_by_invite_count(client: TestClient):
    content_id = create_and_publish_content(client, unlock_type="invite", unlock_threshold=1)
    client.post(
        "/api/v1/onboarding/profile",
        json={"open_id": "parent-summary", "child_age": 7, "child_grade": "一年级", "concerns": []},
    )
    client.post(f"/api/v1/contents/{content_id}/claim", params={"open_id": "parent-summary"})

    initial = client.get("/api/v1/me/invite-summary", params={"open_id": "parent-summary"})
    assert initial.status_code == 200
    assert initial.json()["invited_count"] == 0
    assert initial.json()["display_text"] == "已邀请0位家长，仅可领取部分免费资料"

    client.post(f"/api/v1/contents/{content_id}/share", params={"open_id": "parent-summary"})
    updated = client.get("/api/v1/me/invite-summary", params={"open_id": "parent-summary"})
    assert updated.status_code == 200
    assert updated.json()["invited_count"] == 1
    assert updated.json()["display_text"] == "已邀请1位家长，可领取全部资料"
