from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy import select, update

from app.models import ContentEvent, User, UserContentAsset


def auth_header(client: TestClient, code: str) -> dict[str, str]:
    response = client.post("/api/v1/auth/wechat-login", json={"code": code})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


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
    assert updated_detail.json()["effective_share_count"] == 0
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
    assert dashboard.json()["active_users"] == 0
    assert dashboard.json()["claimed"] == 1
    assert dashboard.json()["downloaded"] == 0
    assert dashboard.json()["shared"] == 1


def test_admin_metrics_respect_date_range(client: TestClient, db_session):
    content_id = create_and_publish_content(client)
    client.post(
        "/api/v1/onboarding/profile",
        json={
            "open_id": "parent-date-range",
            "child_age": 7,
            "child_grade": "涓€骞寸骇",
            "concerns": ["璇嗗瓧闃呰"],
        },
    )
    client.post(f"/api/v1/contents/{content_id}/claim", params={"open_id": "parent-date-range"})
    client.post(f"/api/v1/contents/{content_id}/share", params={"open_id": "parent-date-range"})

    outside_range = datetime(2024, 5, 20, 12, 0, 0)
    db_session.execute(update(ContentEvent).values(created_at=outside_range))
    db_session.execute(update(UserContentAsset).values(created_at=outside_range))
    db_session.commit()

    params = {"start_date": "2024-05-28", "end_date": "2024-06-03"}
    dashboard = client.get("/admin/dashboard/overview", params=params)
    assert dashboard.status_code == 200
    assert dashboard.json()["claimed"] == 0
    assert dashboard.json()["shared"] == 0

    contents = client.get("/admin/contents", params=params)
    assert contents.status_code == 200
    assert contents.json()[0]["claim_count"] == 0
    assert contents.json()[0]["share_count"] == 0


def test_admin_user_profiles_include_intent_ranking(client: TestClient, db_session):
    content_id = create_and_publish_content(client)
    client.post(
        "/api/v1/onboarding/profile",
        json={
            "open_id": "parent-high-intent",
            "nickname": "高意向家长",
            "source_channel": "douyin",
            "child_age": 7,
            "child_grade": "一年级",
            "concerns": ["专注力"],
        },
    )
    client.post(
        "/api/v1/onboarding/profile",
        json={
            "open_id": "parent-low-intent",
            "nickname": "普通家长",
            "source_channel": "wechat",
            "child_age": 6,
            "child_grade": "一年级",
            "concerns": ["识字阅读"],
        },
    )
    client.post(f"/api/v1/contents/{content_id}/claim", params={"open_id": "parent-high-intent"})
    client.post(f"/api/v1/contents/{content_id}/download", params={"open_id": "parent-high-intent"})
    client.post(f"/api/v1/contents/{content_id}/share", params={"open_id": "parent-high-intent"})

    high_user_id = db_session.scalar(select(User.id).where(User.open_id == "parent-high-intent"))
    db_session.add(ContentEvent(user_id=high_user_id, event_type="assessment", content_id=content_id, properties={}))
    db_session.add(ContentEvent(user_id=high_user_id, event_type="camp_signup", content_id=content_id, properties={}))
    db_session.commit()

    response = client.get("/admin/users")
    assert response.status_code == 200
    rows = response.json()
    assert rows[0]["open_id"] == "parent-high-intent"
    assert rows[0]["claim_count"] == 1
    assert rows[0]["download_count"] == 1
    assert rows[0]["share_count"] == 1
    assert rows[0]["assessment_count"] == 1
    assert rows[0]["camp_count"] == 1
    assert rows[0]["intent_level"] == "high"
    assert rows[0]["recommended_action"] == "分配顾问跟进"


def test_admin_can_delete_content_with_related_activity(client: TestClient):
    content_id = create_and_publish_content(client)
    client.post(
        "/api/v1/onboarding/profile",
        json={"open_id": "parent-delete-content", "child_age": 7, "child_grade": "一年级", "concerns": []},
    )
    client.post(f"/api/v1/contents/{content_id}/claim", params={"open_id": "parent-delete-content"})
    client.post(f"/api/v1/contents/{content_id}/share", params={"open_id": "parent-delete-content"})

    response = client.delete(f"/admin/contents/{content_id}")
    assert response.status_code == 204

    contents = client.get("/admin/contents")
    assert contents.status_code == 200
    assert contents.json() == []


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


def test_share_does_not_claim_content(client: TestClient):
    content_id = create_and_publish_content(client)
    client.post(
        "/api/v1/onboarding/profile",
        json={"open_id": "parent-share-only", "child_age": 7, "child_grade": "一年级", "concerns": []},
    )

    share = client.post(f"/api/v1/contents/{content_id}/share", params={"open_id": "parent-share-only"})
    assert share.status_code == 200

    detail = client.get(f"/api/v1/contents/{content_id}", params={"open_id": "parent-share-only"})
    assert detail.status_code == 200
    assert detail.json()["is_claimed"] is False
    assert detail.json()["share_count"] == 1
    assert detail.json()["effective_share_count"] == 0

    assets = client.get("/api/v1/me/assets", params={"open_id": "parent-share-only"})
    assert assets.status_code == 200
    assert assets.json() == []


def test_invite_unlock_applies_after_real_invitee_login(client: TestClient):
    first_id = create_and_publish_content(client, unlock_type="invite", unlock_threshold=1, title="邀请解锁资料A")
    second_id = create_and_publish_content(client, unlock_type="invite", unlock_threshold=1, title="邀请解锁资料B")
    inviter_headers = auth_header(client, "parent-invite-a")
    invitee_headers = auth_header(client, "parent-invite-b")

    client.post(
        "/api/v1/onboarding/profile",
        headers=inviter_headers,
        json={"open_id": "unused-a", "child_age": 7, "child_grade": "一年级", "concerns": []},
    )
    client.post(
        "/api/v1/onboarding/profile",
        headers=invitee_headers,
        json={"open_id": "unused-b", "child_age": 7, "child_grade": "一年级", "concerns": []},
    )

    claim_a = client.post(f"/api/v1/contents/{first_id}/claim", headers=inviter_headers)
    assert claim_a.status_code == 200
    assert claim_a.json()["unlocked"] is False

    share_a = client.post(f"/api/v1/contents/{first_id}/share", headers=inviter_headers)
    assert share_a.status_code == 200
    assert share_a.json()["unlocked"] is False

    before_invite = client.get("/api/v1/contents", headers=inviter_headers, params={"age": 7, "grade": "一年级"})
    before_by_id = {item["id"]: item for item in before_invite.json()}
    assert before_by_id[first_id]["is_unlocked"] is False
    assert before_by_id[second_id]["is_unlocked"] is False
    assert before_by_id[first_id]["share_count"] == 1

    inviter_id = client.get("/api/v1/me/profile", headers=inviter_headers).json()["user_id"]
    share_open = client.post(
        "/api/v1/shares/open",
        json={"inviter_user_id": inviter_id, "source_content_id": first_id},
    )
    assert share_open.status_code == 200
    assert share_open.json()["recorded"] is True

    after_open = client.get("/api/v1/contents", headers=inviter_headers, params={"age": 7, "grade": "一年级"})
    after_open_by_id = {item["id"]: item for item in after_open.json()}
    assert after_open_by_id[first_id]["share_count"] == 1
    assert after_open_by_id[first_id]["effective_share_count"] == 0

    complete = client.post(
        "/api/v1/invites/complete",
        headers=invitee_headers,
        json={"inviter_user_id": inviter_id, "source_content_id": first_id},
    )
    assert complete.status_code == 200
    assert complete.json()["completed"] is True
    assert complete.json()["invited_count"] == 1

    contents_a = client.get("/api/v1/contents", headers=inviter_headers, params={"age": 7, "grade": "一年级"})
    by_id_a = {item["id"]: item for item in contents_a.json()}
    assert by_id_a[first_id]["is_unlocked"] is True
    assert by_id_a[first_id]["share_count"] == 1
    assert by_id_a[first_id]["effective_share_count"] == 1
    assert by_id_a[second_id]["is_unlocked"] is True
    assert by_id_a[second_id]["is_claimed"] is False

    contents_b = client.get("/api/v1/contents", headers=invitee_headers, params={"age": 7, "grade": "一年级"})
    by_id_b = {item["id"]: item for item in contents_b.json()}
    assert by_id_b[first_id]["is_unlocked"] is False
    assert by_id_b[second_id]["is_unlocked"] is False

    download_second_a = client.post(f"/api/v1/contents/{second_id}/download", headers=inviter_headers)
    download_second_b = client.post(f"/api/v1/contents/{second_id}/download", headers=invitee_headers)
    assert download_second_a.status_code == 200
    assert download_second_b.status_code == 403


def test_invite_summary_copy_uses_real_invite_count(client: TestClient):
    content_id = create_and_publish_content(client, unlock_type="invite", unlock_threshold=1)
    inviter_headers = auth_header(client, "parent-summary")
    invitee_headers = auth_header(client, "parent-summary-invitee")
    client.post(
        "/api/v1/onboarding/profile",
        headers=inviter_headers,
        json={"open_id": "unused-summary", "child_age": 7, "child_grade": "一年级", "concerns": []},
    )
    client.post(f"/api/v1/contents/{content_id}/claim", headers=inviter_headers)

    initial = client.get("/api/v1/me/invite-summary", headers=inviter_headers)
    assert initial.status_code == 200
    assert initial.json()["invited_count"] == 0
    assert initial.json()["display_text"] == "已邀请0位家长，仅可领取部分免费资料"

    client.post(f"/api/v1/contents/{content_id}/share", headers=inviter_headers)
    after_share = client.get("/api/v1/me/invite-summary", headers=inviter_headers)
    assert after_share.status_code == 200
    assert after_share.json()["invited_count"] == 0

    inviter_id = client.get("/api/v1/me/profile", headers=inviter_headers).json()["user_id"]
    client.post(
        "/api/v1/invites/complete",
        headers=invitee_headers,
        json={"inviter_user_id": inviter_id, "source_content_id": content_id},
    )
    updated = client.get("/api/v1/me/invite-summary", headers=inviter_headers)
    assert updated.status_code == 200
    assert updated.json()["invited_count"] == 1
    assert updated.json()["display_text"] == "已邀请1位家长，可领取全部资料"
