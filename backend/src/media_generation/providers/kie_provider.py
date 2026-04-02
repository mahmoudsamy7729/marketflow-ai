from __future__ import annotations

import json
from typing import Any

import httpx

from src.config import settings
from src.media_generation import exceptions


class KieProvider:
    CREATE_TASK_PATH = "/api/v1/jobs/createTask"
    RECORD_INFO_PATH = "/api/v1/jobs/recordInfo"

    def _ensure_configured(self) -> None:
        if not settings.kie_api_key or not settings.kie_base_url or not settings.kie_callback_url:
            raise exceptions.MediaGenerationConfigurationError()

    async def create_image_task(self, *, prompt: str, channel: str) -> str:
        self._ensure_configured()
        payload = {
            "model": settings.kie_image_model,
            "callBackUrl": settings.kie_callback_url,
            "input": {
                "prompt": prompt,
                "image_input": [],
                "aspect_ratio": self._aspect_ratio_for_channel(channel),
                "resolution": "1K",
                "output_format": "png",
            },
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{settings.kie_base_url}{self.CREATE_TASK_PATH}",
                    headers={
                        "Authorization": f"Bearer {settings.kie_api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise exceptions.MediaGenerationSubmissionFailed() from exc

        task_id = self.extract_submit_task_id(result)
        if not task_id:
            raise exceptions.MediaGenerationSubmissionFailed()
        return task_id

    async def get_task_details(self, *, task_id: str) -> dict[str, Any]:
        self._ensure_configured()
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{settings.kie_base_url}{self.RECORD_INFO_PATH}",
                    headers={
                        "Authorization": f"Bearer {settings.kie_api_key}",
                    },
                    params={"taskId": task_id},
                )
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise exceptions.MediaGenerationSubmissionFailed() from exc

    def extract_submit_task_id(self, payload: dict[str, Any]) -> str | None:
        data = payload.get("data")
        candidates = [
            payload.get("taskId"),
            data.get("taskId") if isinstance(data, dict) else None,
        ]
        for candidate in candidates:
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
        return None

    def extract_callback_task_id(self, payload: dict[str, Any]) -> str | None:
        data = payload.get("data")
        candidates = [
            payload.get("taskId"),
            data.get("taskId") if isinstance(data, dict) else None,
        ]
        for candidate in candidates:
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
        return None

    def is_success_callback(self, payload: dict[str, Any]) -> bool:
        code = payload.get("code")
        if code == 200:
            return True
        return bool(self.extract_callback_result_url(payload))

    def is_success_task_details(self, payload: dict[str, Any]) -> bool:
        data = payload.get("data")
        if not isinstance(data, dict):
            return False
        state = str(data.get("state", "")).strip().lower()
        return state == "success"

    def extract_callback_result_url(self, payload: dict[str, Any]) -> str | None:
        data = payload.get("data")
        info = data.get("info") if isinstance(data, dict) and isinstance(data.get("info"), dict) else None
        candidates: list[Any] = []
        if isinstance(data, dict):
            candidates.extend(
                [
                    data.get("result_image_url"),
                    data.get("resultImageUrl"),
                    data.get("result_url"),
                    data.get("resultUrl"),
                    data.get("image_url"),
                    data.get("imageUrl"),
                    data.get("result_urls"),
                    data.get("resultUrls"),
                    data.get("image_urls"),
                    data.get("imageUrls"),
                    data.get("images"),
                ]
            )
        if info is not None:
            candidates.extend(
                [
                    info.get("result_image_url"),
                    info.get("resultImageUrl"),
                    info.get("result_url"),
                    info.get("resultUrl"),
                    info.get("image_url"),
                    info.get("imageUrl"),
                    info.get("result_urls"),
                    info.get("resultUrls"),
                    info.get("image_urls"),
                    info.get("imageUrls"),
                    info.get("images"),
                ]
            )

        for candidate in candidates:
            result = self._extract_first_url(candidate)
            if result:
                return result
        return None

    def extract_callback_error_message(self, payload: dict[str, Any]) -> str | None:
        data = payload.get("data")
        candidates: list[Any] = [
            payload.get("msg"),
            payload.get("message"),
        ]
        if isinstance(data, dict):
            candidates.extend(
                [
                    data.get("msg"),
                    data.get("message"),
                    data.get("error"),
                    data.get("error_message"),
                    data.get("errorMessage"),
                ]
            )

        for candidate in candidates:
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
        return None

    def extract_task_result_url(self, payload: dict[str, Any]) -> str | None:
        data = payload.get("data")
        if not isinstance(data, dict):
            return None

        result_json = data.get("resultJson")
        if isinstance(result_json, str) and result_json.strip():
            try:
                parsed = json.loads(result_json)
            except json.JSONDecodeError:
                parsed = None
            if isinstance(parsed, dict):
                for candidate in (
                    parsed.get("resultUrls"),
                    parsed.get("result_urls"),
                    parsed.get("images"),
                    parsed.get("resultImageUrl"),
                    parsed.get("result_image_url"),
                ):
                    result = self._extract_first_url(candidate)
                    if result:
                        return result

        for candidate in (
            data.get("resultUrls"),
            data.get("result_urls"),
            data.get("images"),
            data.get("resultImageUrl"),
            data.get("result_image_url"),
        ):
            result = self._extract_first_url(candidate)
            if result:
                return result
        return None

    def extract_task_error_message(self, payload: dict[str, Any]) -> str | None:
        data = payload.get("data")
        candidates: list[Any] = [
            payload.get("msg"),
            payload.get("message"),
        ]
        if isinstance(data, dict):
            candidates.extend(
                [
                    data.get("failMsg"),
                    data.get("failCode"),
                    data.get("state"),
                    data.get("message"),
                    data.get("msg"),
                ]
            )

        for candidate in candidates:
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
            if candidate is not None and not isinstance(candidate, (dict, list)):
                rendered = str(candidate).strip()
                if rendered:
                    return rendered
        return None

    def _aspect_ratio_for_channel(self, channel: str) -> str:
        if channel == "instagram":
            return "1:1"
        if channel == "facebook":
            return "auto"
        return "auto"

    def _extract_first_url(self, candidate: Any) -> str | None:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
        if isinstance(candidate, list):
            for item in candidate:
                if isinstance(item, str) and item.strip():
                    return item.strip()
                if isinstance(item, dict):
                    for key in ("url", "image_url", "imageUrl", "result_url", "resultUrl"):
                        value = item.get(key)
                        if isinstance(value, str) and value.strip():
                            return value.strip()
        return None
