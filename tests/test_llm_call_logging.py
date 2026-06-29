import json
from io import BytesIO

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.models import AiModelCallLog
from app.services.llm import LlmContentGenerator, LlmGenerationError
from app.tasks.generators import PdfGenerationInput
from app.utils.time import now


class FakeHttpResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def test_llm_material_plan_call_is_logged(db_session, monkeypatch):
    response = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "material_type": "worksheet",
                            "title": "连续练习",
                            "summary": "连续资料",
                            "audience": "一年级",
                            "outline": ["题号连续"],
                            "pages": [
                                {
                                    "page_no": 1,
                                    "section_title": "第一页",
                                    "blocks": [{"type": "question", "title": "练习", "items": ["1. 第一题"]}],
                                }
                            ],
                        },
                        ensure_ascii=False,
                    )
                }
            }
        ],
        "usage": {"prompt_tokens": 11, "completion_tokens": 22, "total_tokens": 33},
    }

    monkeypatch.setattr("app.services.llm.urlopen", lambda request, timeout=None: FakeHttpResponse(response))
    monkeypatch.setattr("app.services.llm.SessionLocal", sessionmaker(bind=db_session.get_bind(), autoflush=False, autocommit=False))
    generator = LlmContentGenerator()
    monkeypatch.setattr(generator.settings, "vectorengine_api_key", "test-key")
    generator.set_trace_context("request-1", "image_pdf_generation")

    result = generator.generate_material_plan(
        PdfGenerationInput(title="连续练习", summary="生成连续资料", subject="数学"),
        reference="参考资料文本",
        page_count=1,
    )

    assert result is not None
    log = db_session.scalar(select(AiModelCallLog))
    assert log is not None
    assert log.request_id == "request-1"
    assert log.task_type == "image_pdf_generation"
    assert log.step_name == "llm_material_plan"
    assert log.status == "success"
    assert "连续练习" in log.prompt_text
    assert "参考资料文本" in log.prompt_text
    assert "连续资料" in log.response_text
    assert log.prompt_tokens == 11
    assert log.completion_tokens == 22
    assert log.total_tokens == 33
    assert log.request_payload["model"] == generator.settings.ai_text_model
    assert log.response_payload["usage"]["total_tokens"] == 33


def test_llm_failed_call_is_logged(db_session, monkeypatch):
    def fail_urlopen(request, timeout=None):
        raise TimeoutError("timeout")

    monkeypatch.setattr("app.services.llm.urlopen", fail_urlopen)
    monkeypatch.setattr("app.services.llm.SessionLocal", sessionmaker(bind=db_session.get_bind(), autoflush=False, autocommit=False))
    generator = LlmContentGenerator()
    monkeypatch.setattr(generator.settings, "vectorengine_api_key", "test-key")
    generator.set_trace_context("request-2", "image_pdf_generation")

    try:
        generator.generate_material_plan(PdfGenerationInput(title="失败", summary="失败"), reference="", page_count=1)
    except LlmGenerationError:
        pass

    log = db_session.scalar(select(AiModelCallLog))
    assert log is not None
    assert log.request_id == "request-2"
    assert log.step_name == "llm_material_plan"
    assert log.status == "failed"
    assert "timeout" in log.error_message


def test_admin_model_call_logs_list_and_detail(client, db_session):
    log = AiModelCallLog(
        request_id="request-ui-1",
        task_type="image_pdf_generation",
        step_name="image_generation",
        provider="vectorengine",
        model="gpt-image-2",
        endpoint="/v1/images/generations",
        request_payload={"prompt": "page 1 prompt", "size": "1024x1536"},
        response_payload={"data": [{"b64_json": "<base64 omitted>"}]},
        prompt_text="page 1 prompt",
        response_text='{"image":"ok"}',
        status="success",
        prompt_tokens=10,
        completion_tokens=0,
        image_tokens=20,
        total_tokens=30,
        started_at=now(),
        finished_at=now(),
        duration_ms=123,
    )
    db_session.add(log)
    db_session.commit()

    listed = client.get("/admin/ai/model-call-logs", params={"request_id": "request-ui-1"})
    assert listed.status_code == 200
    rows = listed.json()
    assert len(rows) == 1
    assert rows[0]["step_name"] == "image_generation"
    assert rows[0]["total_tokens"] == 30

    detail = client.get(f"/admin/ai/model-call-logs/{rows[0]['id']}")
    assert detail.status_code == 200
    payload = detail.json()
    assert payload["prompt_text"] == "page 1 prompt"
    assert payload["request_payload"]["size"] == "1024x1536"
    assert payload["response_payload"]["data"][0]["b64_json"] == "<base64 omitted>"
