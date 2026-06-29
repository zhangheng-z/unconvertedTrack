from dataclasses import dataclass
import json
import logging
from base64 import b64decode, b64encode
import mimetypes
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4

from app.config import get_settings
from app.database import SessionLocal
from app.repositories.ai import AiRepository
from app.utils.time import now


logger = logging.getLogger(__name__)


class LlmGenerationError(RuntimeError):
    pass


@dataclass
class LlmGenerationResult:
    draft: object
    model: str
    usage: object


@dataclass
class LlmReferenceAnalysisResult:
    analysis: object
    model: str
    usage: object


@dataclass
class LlmContentStartPageResult:
    page: int
    reason: str
    model: str
    usage: object


@dataclass
class LlmMaterialPlanResult:
    plan: object
    model: str
    usage: object


class LlmContentGenerator:
    def __init__(self):
        self.settings = get_settings()
        self.trace_request_id: str | None = None
        self.trace_task_type = "unknown"

    def set_trace_context(self, request_id: str | None = None, task_type: str = "unknown") -> None:
        self.trace_request_id = request_id
        self.trace_task_type = task_type

    def analyze_reference_pdf(self, payload, reference: str, reference_profile=None) -> LlmReferenceAnalysisResult | None:
        if not self.settings.vectorengine_api_key:
            logger.info("llm_reference_analysis skipped reason=no_vectorengine_api_key model=%s", self.settings.ai_text_model)
            return None
        if not (reference or "").strip() and reference_profile is None:
            logger.info("llm_reference_analysis skipped reason=no_reference_content model=%s", self.settings.ai_text_model)
            return None

        logger.info(
            "llm_reference_analysis start provider=vectorengine base_url=%s model=%s reference_chars=%s has_reference_profile=%s",
            self._base_url(),
            self.settings.ai_text_model,
            len(reference or ""),
            reference_profile is not None,
        )
        body = {
            "model": self.settings.ai_text_model,
            "messages": [
                {"role": "system", "content": self._reference_analysis_system_prompt()},
                {"role": "user", "content": self._reference_analysis_prompt(payload, reference, reference_profile)},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        response = self._post_json("/chat/completions", body, step_name="llm_reference_analysis")
        content = response["choices"][0]["message"]["content"]
        usage = self._usage(response.get("usage"))
        logger.info(
            "llm_reference_analysis success model=%s prompt_tokens=%s completion_tokens=%s total_tokens=%s",
            self.settings.ai_text_model,
            usage.prompt_tokens,
            usage.completion_tokens,
            usage.total_tokens,
        )
        return LlmReferenceAnalysisResult(
            analysis=self._parse_reference_analysis(content),
            model=self.settings.ai_text_model,
            usage=usage,
        )

    def detect_pdf_content_start_page(self, payload, page_image_paths: list[str]) -> LlmContentStartPageResult | None:
        if not self.settings.vectorengine_api_key:
            logger.info("llm_content_start_page skipped reason=no_vectorengine_api_key model=%s", self.settings.ai_text_model)
            return None
        paths = [Path(path) for path in page_image_paths if path and Path(path).exists()]
        if not paths:
            logger.info("llm_content_start_page skipped reason=no_rendered_pages model=%s", self.settings.ai_text_model)
            return None

        content = [{"type": "text", "text": self._content_start_page_prompt(payload, len(paths))}]
        for index, path in enumerate(paths[:4], start=1):
            content.append({"type": "text", "text": f"Page {index}:"})
            content.append({"type": "image_url", "image_url": {"url": self._image_data_url(path)}})

        logger.info("llm_content_start_page start provider=vectorengine model=%s rendered_pages=%s", self.settings.ai_text_model, len(paths))
        body = {
            "model": self.settings.ai_text_model,
            "messages": [
                {"role": "system", "content": "You judge PDF page roles from page images. Return only valid JSON."},
                {"role": "user", "content": content},
            ],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }
        response = self._post_json("/chat/completions", body, timeout=self.settings.ai_generation_timeout, step_name="llm_content_start_page")
        usage = self._usage(response.get("usage"))
        result = self._parse_content_start_page(response["choices"][0]["message"]["content"], len(paths))
        logger.info(
            "llm_content_start_page success model=%s page=%s prompt_tokens=%s completion_tokens=%s total_tokens=%s",
            self.settings.ai_text_model,
            result["page"],
            usage.prompt_tokens,
            usage.completion_tokens,
            usage.total_tokens,
        )
        return LlmContentStartPageResult(
            page=result["page"],
            reason=result["reason"],
            model=self.settings.ai_text_model,
            usage=usage,
        )

    def generate_pdf_content(self, payload, reference: str, reference_profile=None, reference_analysis=None) -> LlmGenerationResult | None:
        if not self.settings.vectorengine_api_key:
            logger.info("llm_generation skipped reason=no_vectorengine_api_key model=%s", self.settings.ai_text_model)
            return None

        logger.info(
            "llm_generation start provider=vectorengine base_url=%s model=%s reference_chars=%s has_reference_profile=%s has_reference_analysis=%s",
            self._base_url(),
            self.settings.ai_text_model,
            len(reference or ""),
            reference_profile is not None,
            reference_analysis is not None,
        )
        body = {
            "model": self.settings.ai_text_model,
            "messages": [
                {"role": "system", "content": self._system_prompt()},
                {"role": "user", "content": self._user_prompt(payload, reference, reference_profile, reference_analysis)},
            ],
            "temperature": 0.6,
            "response_format": {"type": "json_object"},
        }
        response = self._post_json("/chat/completions", body, step_name="llm_generation")
        content = response["choices"][0]["message"]["content"]
        usage = self._usage(response.get("usage"))
        logger.info(
            "llm_generation success model=%s prompt_tokens=%s completion_tokens=%s total_tokens=%s",
            self.settings.ai_text_model,
            usage.prompt_tokens,
            usage.completion_tokens,
            usage.total_tokens,
        )
        return LlmGenerationResult(
            draft=self._parse_pdf_content(content, payload),
            model=self.settings.ai_text_model,
            usage=usage,
        )

    def generate_material_plan(self, payload, reference: str, page_count: int) -> LlmMaterialPlanResult | None:
        if not self.settings.vectorengine_api_key:
            logger.info("llm_material_plan skipped reason=no_vectorengine_api_key model=%s", self.settings.ai_text_model)
            return None

        logger.info(
            "llm_material_plan start provider=vectorengine base_url=%s model=%s reference_chars=%s page_count=%s",
            self._base_url(),
            self.settings.ai_text_model,
            len(reference or ""),
            page_count,
        )
        body = {
            "model": self.settings.ai_text_model,
            "messages": [
                {"role": "system", "content": self._material_plan_system_prompt()},
                {"role": "user", "content": self._material_plan_user_prompt(payload, reference, page_count)},
            ],
            "temperature": 0.45,
            "response_format": {"type": "json_object"},
        }
        response = self._post_json("/chat/completions", body, step_name="llm_material_plan")
        usage = self._usage(response.get("usage"))
        return LlmMaterialPlanResult(
            plan=self._parse_material_plan(response["choices"][0]["message"]["content"], payload, page_count),
            model=self.settings.ai_text_model,
            usage=usage,
        )

    def generate_image_bytes(self, prompt: str, size: str = "1024x1024"):
        from app.tasks.generators.types import TokenUsage

        if not self.settings.vectorengine_api_key or not prompt.strip():
            logger.info("image_generation skipped reason=no_key_or_empty_prompt model=%s", self.settings.ai_image_model)
            return None, TokenUsage()
        logger.info("image_generation start provider=vectorengine model=%s size=%s prompt_chars=%s", self.settings.ai_image_model, size, len(prompt))
        body = {
            "model": self.settings.ai_image_model,
            "prompt": prompt,
            "size": size,
            "n": 1,
        }
        response = self._post_json("/images/generations", body, timeout=self.settings.ai_image_generation_timeout, step_name="image_generation")
        usage = self._usage(response.get("usage"))
        logger.info("image_generation response model=%s image_tokens=%s total_tokens=%s", self.settings.ai_image_model, usage.image_tokens, usage.total_tokens)
        item = response.get("data", [{}])[0]
        if item.get("b64_json"):
            return b64decode(item["b64_json"]), usage
        if item.get("url"):
            try:
                with urlopen(item["url"], timeout=self.settings.ai_image_generation_timeout) as image_response:
                    return image_response.read(), usage
            except (HTTPError, URLError, TimeoutError):
                return None, usage
        return None, usage

    def generate_image_with_reference_bytes(self, prompt: str, reference_image_paths: list[str], size: str = "1024x1024"):
        from app.tasks.generators.types import TokenUsage

        if not self.settings.vectorengine_api_key or not prompt.strip():
            logger.info("image_reference_generation skipped reason=no_key_or_empty_prompt model=%s", self.settings.ai_image_model)
            return None, TokenUsage()
        paths = [Path(path) for path in reference_image_paths if path and Path(path).exists()]
        if not paths:
            raise LlmGenerationError("reference image generation requires at least one rendered reference image")

        logger.info(
            "image_reference_generation start provider=vectorengine model=%s size=%s prompt_chars=%s reference_images=%s",
            self.settings.ai_image_model,
            size,
            len(prompt),
            len(paths),
        )
        fields = {
            "model": self.settings.ai_image_model,
            "prompt": prompt,
            "size": size,
            "n": "1",
        }
        files = [("image", path) for path in paths[:2]]
        response = self._post_multipart("/images/edits", fields, files, timeout=self.settings.ai_image_generation_timeout, step_name="image_reference_generation")
        usage = self._usage(response.get("usage"))
        logger.info("image_reference_generation response model=%s image_tokens=%s total_tokens=%s", self.settings.ai_image_model, usage.image_tokens, usage.total_tokens)
        return self._image_bytes_from_response(response), usage

    def _image_bytes_from_response(self, response: dict) -> bytes | None:
        item = response.get("data", [{}])[0]
        if item.get("b64_json"):
            return b64decode(item["b64_json"])
        if item.get("url"):
            try:
                with urlopen(item["url"], timeout=self.settings.ai_image_generation_timeout) as image_response:
                    return image_response.read()
            except (HTTPError, URLError, TimeoutError):
                return None
        return None

    def _post_json(self, path: str, body: dict, timeout: int | None = None, step_name: str = "llm_request") -> dict:
        url = f"{self._base_url()}{path}"
        started_at = now()
        started_clock = time.perf_counter()
        request = Request(
            url,
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.settings.vectorengine_api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=timeout or self.settings.ai_generation_timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
                self._record_model_call(
                    step_name=step_name,
                    endpoint=path,
                    request_payload=body,
                    response_payload=data,
                    status="success",
                    started_at=started_at,
                    duration_ms=int((time.perf_counter() - started_clock) * 1000),
                )
                return data
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            logger.warning("llm_request failed path=%s status=%s detail=%s", path, exc.code, detail)
            self._record_model_call(
                step_name=step_name,
                endpoint=path,
                request_payload=body,
                response_payload={"http_status": exc.code, "detail": detail},
                status="failed",
                error_message=f"HTTP {exc.code} {detail}",
                started_at=started_at,
                duration_ms=int((time.perf_counter() - started_clock) * 1000),
            )
            raise LlmGenerationError(f"LLM generation failed: HTTP {exc.code} {detail}") from exc
        except (URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
            logger.warning("llm_request failed path=%s error=%s", path, exc)
            self._record_model_call(
                step_name=step_name,
                endpoint=path,
                request_payload=body,
                response_payload=None,
                status="failed",
                error_message=str(exc),
                started_at=started_at,
                duration_ms=int((time.perf_counter() - started_clock) * 1000),
            )
            raise LlmGenerationError(f"LLM generation failed: {exc}") from exc

    def _post_multipart(self, path: str, fields: dict[str, str], files: list[tuple[str, Path]], timeout: int | None = None, step_name: str = "llm_multipart_request") -> dict:
        boundary = f"----codex-{uuid4().hex}"
        started_at = now()
        started_clock = time.perf_counter()
        body = bytearray()
        for name, value in fields.items():
            body.extend(f"--{boundary}\r\n".encode("utf-8"))
            body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"))
            body.extend(str(value).encode("utf-8"))
            body.extend(b"\r\n")
        for name, file_path in files:
            content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
            body.extend(f"--{boundary}\r\n".encode("utf-8"))
            body.extend(f'Content-Disposition: form-data; name="{name}"; filename="{file_path.name}"\r\n'.encode("utf-8"))
            body.extend(f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"))
            body.extend(file_path.read_bytes())
            body.extend(b"\r\n")
        body.extend(f"--{boundary}--\r\n".encode("utf-8"))

        request = Request(
            f"{self._base_url()}{path}",
            data=bytes(body),
            headers={
                "Authorization": f"Bearer {self.settings.vectorengine_api_key}",
                "Content-Type": f"multipart/form-data; boundary={boundary}",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=timeout or self.settings.ai_generation_timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
                self._record_model_call(
                    step_name=step_name,
                    endpoint=path,
                    request_payload={**fields, "files": [str(path) for _, path in files]},
                    response_payload=data,
                    status="success",
                    started_at=started_at,
                    duration_ms=int((time.perf_counter() - started_clock) * 1000),
                )
                return data
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            logger.warning("llm_multipart_request failed path=%s status=%s detail=%s", path, exc.code, detail)
            self._record_model_call(
                step_name=step_name,
                endpoint=path,
                request_payload={**fields, "files": [str(path) for _, path in files]},
                response_payload={"http_status": exc.code, "detail": detail},
                status="failed",
                error_message=f"HTTP {exc.code} {detail}",
                started_at=started_at,
                duration_ms=int((time.perf_counter() - started_clock) * 1000),
            )
            raise LlmGenerationError(f"Reference image generation failed: HTTP {exc.code} {detail}") from exc
        except (URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
            logger.warning("llm_multipart_request failed path=%s error=%s", path, exc)
            self._record_model_call(
                step_name=step_name,
                endpoint=path,
                request_payload={**fields, "files": [str(path) for _, path in files]},
                response_payload=None,
                status="failed",
                error_message=str(exc),
                started_at=started_at,
                duration_ms=int((time.perf_counter() - started_clock) * 1000),
            )
            raise LlmGenerationError(f"Reference image generation failed: {exc}") from exc

    def _record_model_call(
        self,
        step_name: str,
        endpoint: str,
        request_payload: dict,
        response_payload: dict | None,
        status: str,
        started_at,
        duration_ms: int,
        error_message: str | None = None,
    ) -> None:
        try:
            safe_request = self._sanitize_payload(request_payload)
            safe_response = self._sanitize_payload(response_payload) if response_payload is not None else None
            usage = self._usage(response_payload.get("usage") if isinstance(response_payload, dict) else None)
            with SessionLocal() as db:
                AiRepository(db).create_model_call_log(
                    request_id=self.trace_request_id,
                    task_type=self.trace_task_type,
                    step_name=step_name,
                    provider="vectorengine",
                    model=str(request_payload.get("model") or ""),
                    endpoint=endpoint,
                    http_method="POST",
                    request_payload=safe_request,
                    response_payload=safe_response,
                    prompt_text=self._extract_prompt_text(request_payload),
                    response_text=self._extract_response_text(response_payload),
                    status=status,
                    error_message=error_message,
                    prompt_tokens=usage.prompt_tokens,
                    completion_tokens=usage.completion_tokens,
                    image_tokens=usage.image_tokens,
                    total_tokens=usage.total_tokens,
                    started_at=started_at,
                    finished_at=now(),
                    duration_ms=duration_ms,
                )
                db.commit()
        except Exception as exc:
            logger.warning("ai_model_call_log skipped step=%s error=%s", step_name, exc)

    @classmethod
    def _sanitize_payload(cls, value):
        if isinstance(value, dict):
            sanitized = {}
            for key, item in value.items():
                if key in {"b64_json", "image_url"}:
                    sanitized[key] = cls._sanitize_large_value(item)
                else:
                    sanitized[key] = cls._sanitize_payload(item)
            return sanitized
        if isinstance(value, list):
            return [cls._sanitize_payload(item) for item in value]
        if isinstance(value, str):
            return cls._sanitize_large_value(value)
        return value

    @staticmethod
    def _sanitize_large_value(value: str):
        if not isinstance(value, str):
            return value
        if value.startswith("data:image/") or len(value) > 8000:
            return f"<omitted {len(value)} chars>"
        return value

    @staticmethod
    def _extract_prompt_text(payload: dict | None) -> str:
        if not isinstance(payload, dict):
            return ""
        if isinstance(payload.get("prompt"), str):
            return payload["prompt"]
        messages = payload.get("messages")
        if not isinstance(messages, list):
            return ""
        parts = []
        for message in messages:
            if not isinstance(message, dict):
                continue
            role = message.get("role") or "unknown"
            content = message.get("content")
            if isinstance(content, list):
                text = "\n".join(str(item.get("text") or item) for item in content if isinstance(item, dict))
            else:
                text = str(content or "")
            parts.append(f"{role}: {text}")
        return "\n\n".join(parts)

    @staticmethod
    def _extract_response_text(payload: dict | None) -> str:
        if not isinstance(payload, dict):
            return ""
        choices = payload.get("choices")
        if isinstance(choices, list) and choices:
            message = choices[0].get("message") if isinstance(choices[0], dict) else None
            if isinstance(message, dict):
                return str(message.get("content") or "")
        data = payload.get("data")
        if isinstance(data, list) and data:
            return json.dumps(LlmContentGenerator._sanitize_payload(data[0]), ensure_ascii=False)
        return ""

    def _base_url(self) -> str:
        base = self.settings.vectorengine_base_url.rstrip("/")
        return base if base.endswith("/v1") else f"{base}/v1"

    @staticmethod
    def _image_data_url(path: Path) -> str:
        mime = mimetypes.guess_type(path.name)[0] or "image/png"
        return f"data:{mime};base64,{b64encode(path.read_bytes()).decode('ascii')}"

    @staticmethod
    def _content_start_page_prompt(payload, page_count: int) -> str:
        return f"""
你会看到参考 PDF 的前 {page_count} 页截图。请判断第几页开始是可以作为“正文内容版式参考”的页面。

判断标准：
- 跳过封面、目录、版权页、纯广告页、空白页。
- 选择第一张真正包含正文内容、练习题、知识点、讲解、表格、卡片、任务清单或可复用排版结构的页面。
- 如果第 1 页已经是正文内容页，返回 1。
- 只能返回 1 到 {page_count} 之间的整数。

目标新资料：
标题：{getattr(payload, "title", "")}
简介：{getattr(payload, "summary", "")}

返回 JSON：
{{
  "content_start_page": 1,
  "reason": "一句话说明为什么从这一页开始"
}}
""".strip()

    @staticmethod
    def _parse_content_start_page(content: str, max_page: int) -> dict:
        text = content.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:].strip()
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise LlmGenerationError("LLM returned invalid content start page JSON") from exc
        page = int(data.get("content_start_page") or 1)
        page = max(1, min(page, max_page))
        return {"page": page, "reason": str(data.get("reason") or "")}

    @staticmethod
    def _reference_analysis_system_prompt() -> str:
        return (
            "你是教育资料编辑和PDF版式分析专家。"
            "你只分析参考资料的内容组织、栏目结构、写作语气、练习形式和版式规律，"
            "不要复述或改写原文，不要输出Markdown，只输出合法JSON。"
        )

    @staticmethod
    def _system_prompt() -> str:
        return (
            "你是小学低年级教育内容策划专家，面向家长写作。"
            "内容必须具体、温和、可执行，不编造机构、专家和数据。"
            "如果用户提供参考PDF，只参考结构、栏目、题型和版式风格，不逐字复制原文。"
            "只输出合法JSON，不要Markdown，不要代码块。"
        )

    @staticmethod
    def _reference_analysis_prompt(payload, reference: str, reference_profile=None) -> str:
        profile_text = ""
        if reference_profile is not None:
            notes = "；".join(reference_profile.layout_notes or [])
            profile_text = f"""
本地PDF结构信息：
页数：{reference_profile.page_count or "未知"}
页面尺寸：{reference_profile.page_size or "未知"}
方向：{reference_profile.orientation or "未知"}
版式备注：{notes or "未知"}
"""
        return f"""
请分析下面参考PDF/参考资料，用于后续生成“类似风格但不同内容”的新PDF。

目标新PDF：
标题：{payload.title}
简介：{payload.summary}
年级：{payload.grade or "未指定"}
学科：{payload.subject or "未指定"}
问题：{payload.problem or "未指定"}

{profile_text}

参考资料文本，可能来自PDF抽取，可能不完整：
{reference[:7000] if reference else "无"}

必须输出JSON：
{{
  "content_pattern": "参考资料如何展开内容，例如先诊断、再方法、再计划、再转化入口",
  "writing_style": "语气和表达方式，例如面向家长、短句、行动导向",
  "section_structure": ["栏目1", "栏目2", "栏目3"],
  "layout_suggestions": ["版式建议1", "版式建议2"],
  "practice_forms": ["练习形式1", "任务形式2"],
  "avoid_copying": ["不要复制的内容类型1", "不要复制的内容类型2"]
}}
""".strip()

    @staticmethod
    def _user_prompt(payload, reference: str, reference_profile=None, reference_analysis=None) -> str:
        profile_text = ""
        if reference_profile is not None:
            notes = "；".join(reference_profile.layout_notes or [])
            profile_text = f"""
参考PDF本地结构：
页数：{reference_profile.page_count or "未知"}
页面尺寸：{reference_profile.page_size or "未知"}
方向：{reference_profile.orientation or "未知"}
版式特征：{notes or "未知"}
"""
        analysis_text = ""
        if reference_analysis is not None:
            analysis_text = f"""
大模型参考PDF分析结果：
{reference_analysis.to_prompt_text()}

请优先按照这份分析结果生成新内容，保持栏目、语气、练习形式和版式节奏相似，但主题、句子、示例和题目必须重新创作。
"""
        return f"""
请根据以下信息生成一份适合渲染为 2-4 页 PDF 的结构化内容。
标题：{payload.title}
简介：{payload.summary}
年龄：{payload.target_age_min or "未指定"}-{payload.target_age_max or "未指定"}
年级：{payload.grade or "未指定"}
学科：{payload.subject or "未指定"}
问题：{payload.problem or "未指定"}
下一步行动：{payload.next_action or "5分钟测评"}
参考资料：{reference[:5000] if reference else "无"}
{profile_text}
{analysis_text}

必须输出 JSON，字段如下：
{{
  "title": "PDF标题",
  "summary": "80字以内简介",
  "outline": ["3到5条核心要点"],
  "practice_plan": ["5到7条7天计划"],
  "parent_tips": ["3到5条家长建议"],
  "next_action": "下一步行动",
  "reference_summary": "可为空，100字以内",
  "image_prompt": "可为空；如需要配图，给出适合gpt-image-2生成的儿童教育扁平插画提示词"
}}
""".strip()

    @staticmethod
    def _material_plan_system_prompt() -> str:
        return (
            "你是小学教育资料策划编辑。你只输出合法 JSON，不要 Markdown。"
            "你要把用户给出的标题、简介、学科、问题和参考资料，规划成一份连续的多页资料。"
            "资料可以是试卷、练习单、知识卡、家长指南、打卡清单或参考资料改编内容。"
            "不要编造机构、老师、专家和统计数据；不要复制参考资料原文。"
        )

    @staticmethod
    def _material_plan_user_prompt(payload, reference: str, page_count: int) -> str:
        return f"""
请生成一份连续的教育资料页面计划，必须刚好 {page_count} 页。

输入信息：
标题：{payload.title}
简介：{payload.summary}
学科：{payload.subject or "未指定"}
年级：{payload.grade or "未指定"}
重点问题：{payload.problem or "未指定"}
年龄：{payload.target_age_min or "未指定"}-{payload.target_age_max or "未指定"}
下一步行动：{payload.next_action or "5分钟测评"}
参考资料：{reference[:5000] if reference else "无"}

连续性要求：
- pages 数组长度必须等于 {page_count}。
- 这是同一份资料，不能每页重新开始。
- 每页都要有 page_no，从 1 到 {page_count} 连续。
- 页眉标题、资料类型、语气和视觉节奏保持一致。
- 如果是试卷或练习卷，题号必须全局递增，第二页不能从 1 重新开始。
- 如果是清单或打卡表，日期/任务编号必须连续。
- 如果某个栏目跨页，设置 continued_from 或 continued_to。

输出 JSON：
{{
  "material_type": "exam_paper | worksheet | knowledge_card | parent_guide | checklist | reference_material",
  "title": "资料标题",
  "summary": "80字以内简介",
  "audience": "适用对象",
  "global_style": "简短描述整体版式，例如A4练习卷、知识卡、家长指南",
  "outline": ["3到6条资料要点"],
  "pages": [
    {{
      "page_no": 1,
      "section_title": "本页栏目标题",
      "continued_from": null,
      "continued_to": 2,
      "blocks": [
        {{
          "type": "paragraph | list | question | table | checklist | note",
          "title": "块标题，可为空",
          "text": "正文、题干或说明",
          "items": ["列表项、题目步骤、表格行"],
          "options": ["A. 选项", "B. 选项"],
          "answer_space": 1
        }}
      ]
    }}
  ]
}}
""".strip()

    @staticmethod
    def _parse_pdf_content(content: str, payload):
        from app.tasks.generators.types import PdfContentDraft

        text = content.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:].strip()
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise LlmGenerationError("LLM returned invalid JSON") from exc

        return PdfContentDraft(
            title=str(data.get("title") or payload.title),
            summary=str(data.get("summary") or payload.summary),
            outline=LlmContentGenerator._list(data.get("outline")),
            practice_plan=LlmContentGenerator._list(data.get("practice_plan")),
            parent_tips=LlmContentGenerator._list(data.get("parent_tips")),
            next_action=str(data.get("next_action") or payload.next_action or ""),
            reference_summary=str(data.get("reference_summary") or ""),
            image_prompt=str(data.get("image_prompt") or ""),
        )

    @staticmethod
    def _parse_material_plan(content: str, payload, page_count: int):
        from app.tasks.generators.types import MaterialBlock, MaterialPage, MaterialPlan

        text = content.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:].strip()
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise LlmGenerationError("LLM returned invalid material plan JSON") from exc

        pages = []
        for index, page in enumerate(data.get("pages") if isinstance(data.get("pages"), list) else [], start=1):
            if not isinstance(page, dict):
                continue
            blocks = []
            for block in page.get("blocks") if isinstance(page.get("blocks"), list) else []:
                if not isinstance(block, dict):
                    continue
                blocks.append(
                    MaterialBlock(
                        type=str(block.get("type") or "paragraph"),
                        title=str(block.get("title") or ""),
                        text=str(block.get("text") or ""),
                        items=LlmContentGenerator._list(block.get("items")),
                        options=LlmContentGenerator._list(block.get("options")),
                        answer_space=LlmContentGenerator._int(block.get("answer_space"), 0),
                    )
                )
            pages.append(
                MaterialPage(
                    page_no=int(page.get("page_no") or index),
                    section_title=str(page.get("section_title") or f"第{index}页"),
                    blocks=blocks,
                    continued_from=page.get("continued_from") if isinstance(page.get("continued_from"), int) else None,
                    continued_to=page.get("continued_to") if isinstance(page.get("continued_to"), int) else None,
                )
            )

        return MaterialPlan(
            material_type=str(data.get("material_type") or "worksheet"),
            title=str(data.get("title") or payload.title),
            summary=str(data.get("summary") or payload.summary),
            audience=str(data.get("audience") or payload.grade or "小学低年级"),
            pages=pages[:page_count],
            outline=LlmContentGenerator._list(data.get("outline")),
            global_style=str(data.get("global_style") or ""),
        )

    @staticmethod
    def _parse_reference_analysis(content: str):
        from app.tasks.generators.types import ReferenceAnalysis

        text = content.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:].strip()
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise LlmGenerationError("LLM returned invalid reference analysis JSON") from exc

        return ReferenceAnalysis(
            content_pattern=str(data.get("content_pattern") or ""),
            writing_style=str(data.get("writing_style") or ""),
            section_structure=LlmContentGenerator._list(data.get("section_structure")),
            layout_suggestions=LlmContentGenerator._list(data.get("layout_suggestions")),
            practice_forms=LlmContentGenerator._list(data.get("practice_forms")),
            avoid_copying=LlmContentGenerator._list(data.get("avoid_copying")),
        )

    @staticmethod
    def _usage(value):
        from app.tasks.generators.types import TokenUsage

        if not isinstance(value, dict):
            return TokenUsage()
        prompt = int(value.get("prompt_tokens") or value.get("input_tokens") or 0)
        completion = int(value.get("completion_tokens") or value.get("output_tokens") or 0)
        total = int(value.get("total_tokens") or prompt + completion)
        image = int(value.get("image_tokens") or 0)
        return TokenUsage(prompt_tokens=prompt, completion_tokens=completion, total_tokens=total, image_tokens=image)

    @staticmethod
    def _list(value) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item).strip() for item in value if str(item).strip()]

    @staticmethod
    def _int(value, default: int = 0) -> int:
        try:
            return max(0, int(value))
        except (TypeError, ValueError):
            return default
