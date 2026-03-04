#!/usr/bin/env python3
"""Provider clients for text-to-image generation."""

from __future__ import annotations

import json
import random
import re
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

from models import API_MODEL_MAP, GenerationRequest, GenerationResult, default_guidance, default_steps, dimensions_for
from token_pool import classify_error

HF_Z_IMAGE_TURBO = "https://luca115-z-image-turbo.hf.space"
HF_Z_IMAGE = "https://mrfakename-z-image.hf.space"
HF_QWEN_IMAGE = "https://mcp-tools-qwen-image-fast.hf.space"
HF_OVIS_IMAGE = "https://aidc-ai-ovis-image-7b.hf.space"
HF_FLUX_SCHNELL = "https://black-forest-labs-flux-1-schnell.hf.space"
HF_Z_NEGATIVE_PROMPT = (
    "worst quality, low quality, JPEG compression artifacts, ugly, incomplete, extra fingers, "
    "poorly drawn hands, poorly drawn face, deformed, disfigured, malformed limbs, fused fingers"
)

GITEE_GENERATE_API_URL = "https://ai.gitee.com/v1/images/generations"
MODELSCOPE_GENERATE_ENDPOINT = "https://api-inference.modelscope.cn/v1/images/generations"
MODELSCOPE_TASK_ENDPOINT = "https://api-inference.modelscope.cn/v1/tasks/{task_id}"
A4F_GENERATE_API_URL = "https://api.a4f.co/v1/images/generations"


@dataclass
class ProviderRequestError(Exception):
    kind: str
    message: str
    status_code: Optional[int] = None
    payload: Optional[Dict[str, Any]] = None

    def __str__(self) -> str:
        return self.message


def generate(
    provider: str,
    model: str,
    request_data: GenerationRequest,
    token: Optional[str],
    timeout: int = 180,
    provider_config: Optional[Dict[str, Any]] = None,
) -> GenerationResult:
    if provider == "huggingface":
        return _generate_huggingface(model, request_data, token, timeout)
    if provider == "gitee":
        return _generate_gitee(model, request_data, token, timeout)
    if provider == "modelscope":
        return _generate_modelscope(model, request_data, token, timeout)
    if provider == "a4f":
        return _generate_a4f(model, request_data, token, timeout)
    if provider == "openai_compatible":
        return _generate_openai_compatible(model, request_data, token, timeout, provider_config or {})
    raise ProviderRequestError(kind="validation", message=f"Unsupported provider: {provider}")


def _generate_huggingface(model: str, req: GenerationRequest, token: Optional[str], timeout: int) -> GenerationResult:
    dims = dimensions_for("huggingface", model, req.aspect_ratio, req.enable_hd)
    seed = req.seed if req.seed is not None else random.randint(1, 2_147_483_647)
    steps = req.steps if req.steps is not None else default_steps("huggingface", model)
    guidance = req.guidance_scale if req.guidance_scale is not None else default_guidance("huggingface", model)

    if model == "z-image-turbo":
        output = _run_gradio_task(
            base_url=HF_Z_IMAGE_TURBO,
            data=[req.prompt, dims["height"], dims["width"], steps, seed, False],
            fn_index=1,
            trigger_id=16,
            token=token,
            timeout=timeout,
        )
    elif model == "z-image":
        output = _run_gradio_task(
            base_url=HF_Z_IMAGE,
            data=[req.prompt, HF_Z_NEGATIVE_PROMPT, dims["height"], dims["width"], steps, guidance, seed, False],
            fn_index=2,
            trigger_id=18,
            token=token,
            timeout=timeout,
        )
    elif model == "qwen-image":
        randomize = req.seed is None
        qwen_seed = req.seed if req.seed is not None else 42
        output = _run_gradio_task(
            base_url=HF_QWEN_IMAGE,
            data=[req.prompt, qwen_seed, randomize, req.aspect_ratio, 3, steps],
            fn_index=1,
            trigger_id=6,
            token=token,
            timeout=timeout,
        )
        seed = _extract_qwen_seed(output) or qwen_seed
    elif model == "ovis-image":
        output = _run_gradio_task(
            base_url=HF_OVIS_IMAGE,
            data=[req.prompt, dims["height"], dims["width"], seed, steps, 4],
            fn_index=2,
            trigger_id=5,
            token=token,
            timeout=timeout,
        )
    elif model == "flux-1-schnell":
        output = _run_gradio_task(
            base_url=HF_FLUX_SCHNELL,
            data=[req.prompt, seed, False, dims["width"], dims["height"], steps],
            fn_index=2,
            trigger_id=5,
            token=token,
            timeout=timeout,
        )
    else:
        raise ProviderRequestError(kind="validation", message=f"Model not supported on huggingface: {model}")

    try:
        image_url = output["data"][0]["url"]
    except (KeyError, IndexError, TypeError):
        raise ProviderRequestError(kind="provider", message="Invalid Hugging Face response format", payload=output)

    return GenerationResult(
        url=image_url,
        provider="huggingface",
        model=model,
        seed=seed,
        steps=steps,
        guidance_scale=guidance,
        raw_response=output,
    )


def _generate_gitee(model: str, req: GenerationRequest, token: Optional[str], timeout: int) -> GenerationResult:
    if not token:
        raise ProviderRequestError(kind="auth", message="Gitee token is required")

    api_model = API_MODEL_MAP["gitee"].get(model)
    if not api_model:
        raise ProviderRequestError(kind="validation", message=f"Model not supported on gitee: {model}")

    dims = dimensions_for("gitee", model, req.aspect_ratio, req.enable_hd)
    seed = req.seed if req.seed is not None else random.randint(1, 2_147_483_647)
    steps = req.steps if req.steps is not None else default_steps("gitee", model)
    guidance = req.guidance_scale if req.guidance_scale is not None else default_guidance("gitee", model)

    payload: Dict[str, Any] = {
        "prompt": req.prompt,
        "model": api_model,
        "width": dims["width"],
        "height": dims["height"],
        "seed": seed,
        "num_inference_steps": steps,
        "response_format": "url",
    }
    if guidance is not None:
        payload["guidance_scale"] = guidance

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    try:
        response = requests.post(GITEE_GENERATE_API_URL, headers=headers, json=payload, timeout=timeout)
    except requests.RequestException as exc:
        raise ProviderRequestError(kind="network", message=f"Gitee request failed: {exc}")

    if not response.ok:
        _raise_response_error(response, "Gitee generation failed")

    body = _safe_json(response)
    image_url = _nested_value(body, ["data", 0, "url"])
    if not image_url:
        raise ProviderRequestError(kind="provider", message="Invalid Gitee response format", payload=body)

    return GenerationResult(
        url=image_url,
        provider="gitee",
        model=model,
        seed=seed,
        steps=steps,
        guidance_scale=guidance,
        raw_response=body,
    )


def _generate_modelscope(model: str, req: GenerationRequest, token: Optional[str], timeout: int) -> GenerationResult:
    if not token:
        raise ProviderRequestError(kind="auth", message="ModelScope token is required")

    api_model = API_MODEL_MAP["modelscope"].get(model)
    if not api_model:
        raise ProviderRequestError(kind="validation", message=f"Model not supported on modelscope: {model}")

    dims = dimensions_for("modelscope", model, req.aspect_ratio, req.enable_hd)
    seed = req.seed if req.seed is not None else random.randint(1, 2_147_483_647)
    steps = req.steps if req.steps is not None else default_steps("modelscope", model)
    guidance = req.guidance_scale if req.guidance_scale is not None else default_guidance("modelscope", model)

    payload: Dict[str, Any] = {
        "prompt": req.prompt,
        "model": api_model,
        "size": f"{dims['width']}x{dims['height']}",
        "seed": seed,
        "steps": steps,
    }
    if guidance is not None:
        payload["guidance"] = guidance

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "X-ModelScope-Async-Mode": "true",
    }

    try:
        response = requests.post(MODELSCOPE_GENERATE_ENDPOINT, headers=headers, json=payload, timeout=timeout)
    except requests.RequestException as exc:
        raise ProviderRequestError(kind="network", message=f"ModelScope request failed: {exc}")

    if not response.ok:
        _raise_response_error(response, "ModelScope generation failed")

    init_body = _safe_json(response)
    task_id = init_body.get("task_id")
    if not task_id:
        raise ProviderRequestError(kind="provider", message="ModelScope did not return task_id", payload=init_body)

    poll_headers = {
        "Authorization": f"Bearer {token}",
        "X-ModelScope-Task-Type": "image_generation",
    }
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            poll_response = requests.get(
                MODELSCOPE_TASK_ENDPOINT.format(task_id=task_id),
                headers=poll_headers,
                timeout=min(30, timeout),
            )
        except requests.RequestException as exc:
            raise ProviderRequestError(kind="network", message=f"ModelScope polling failed: {exc}")

        if not poll_response.ok:
            _raise_response_error(poll_response, "ModelScope task polling failed")

        poll_body = _safe_json(poll_response)
        status = str(poll_body.get("task_status", "")).upper()
        if status == "SUCCEED":
            output_images = poll_body.get("output_images")
            if isinstance(output_images, list) and output_images:
                return GenerationResult(
                    url=output_images[0],
                    provider="modelscope",
                    model=model,
                    seed=seed,
                    steps=steps,
                    guidance_scale=guidance,
                    raw_response=poll_body,
                )
            raise ProviderRequestError(kind="provider", message="ModelScope task succeeded but no image returned", payload=poll_body)
        if status == "FAILED":
            message = poll_body.get("message") or "ModelScope task failed"
            raise ProviderRequestError(kind=classify_error(str(message)), message=str(message), payload=poll_body)

        time.sleep(2.5)

    raise ProviderRequestError(kind="network", message="ModelScope task polling timed out")


def _generate_a4f(model: str, req: GenerationRequest, token: Optional[str], timeout: int) -> GenerationResult:
    if not token:
        raise ProviderRequestError(kind="auth", message="A4F token is required")

    api_model = API_MODEL_MAP["a4f"].get(model)
    if not api_model:
        raise ProviderRequestError(kind="validation", message=f"Model not supported on a4f: {model}")

    dims = dimensions_for("a4f", model, req.aspect_ratio, req.enable_hd)
    seed = req.seed if req.seed is not None else random.randint(1, 2_147_483_647)
    steps = req.steps if req.steps is not None else default_steps("a4f", model)
    guidance = req.guidance_scale if req.guidance_scale is not None else default_guidance("a4f", model)

    payload = {
        "model": api_model,
        "prompt": req.prompt,
        "n": 1,
        "size": f"{dims['width']}x{dims['height']}",
        "response_format": "url",
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    try:
        response = requests.post(A4F_GENERATE_API_URL, headers=headers, json=payload, timeout=timeout)
    except requests.RequestException as exc:
        raise ProviderRequestError(kind="network", message=f"A4F request failed: {exc}")

    if not response.ok:
        _raise_response_error(response, "A4F generation failed")

    body = _safe_json(response)
    image_url = _nested_value(body, ["data", 0, "url"])
    if not image_url:
        raise ProviderRequestError(kind="provider", message="Invalid A4F response format", payload=body)

    return GenerationResult(
        url=image_url,
        provider="a4f",
        model=model,
        seed=seed,
        steps=steps,
        guidance_scale=guidance,
        raw_response=body,
    )


def _generate_openai_compatible(
    model: str,
    req: GenerationRequest,
    token: Optional[str],
    timeout: int,
    provider_config: Dict[str, Any],
) -> GenerationResult:
    if not token:
        raise ProviderRequestError(kind="auth", message="OpenAI-compatible token is required")

    api_url = str(provider_config.get("api_url", "")).strip().rstrip("/")
    if not api_url:
        raise ProviderRequestError(kind="validation", message="providers.openai_compatible.api_url is required")

    endpoint = str(provider_config.get("images_endpoint", "/images/generations")).strip()
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"
    generate_url = f"{api_url}{endpoint}"

    api_model = API_MODEL_MAP["openai_compatible"].get(model, model)
    dims = dimensions_for("openai_compatible", model, req.aspect_ratio, req.enable_hd)
    seed = req.seed if req.seed is not None else random.randint(1, 2_147_483_647)
    size = f"{dims['width']}x{dims['height']}"

    payload: Dict[str, Any] = {
        "model": api_model,
        "prompt": req.prompt,
        "size": size,
        "n": 1,
        "response_format": "url",
    }
    if bool(provider_config.get("send_seed", False)):
        payload["seed"] = seed

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    try:
        response = requests.post(generate_url, headers=headers, json=payload, timeout=timeout)
    except requests.RequestException as exc:
        raise ProviderRequestError(kind="network", message=f"OpenAI-compatible request failed: {exc}")

    if not response.ok:
        _raise_response_error(response, "OpenAI-compatible generation failed")

    body = _safe_json(response)
    image_url = _nested_value(body, ["data", 0, "url"])
    if not image_url:
        b64_data = _nested_value(body, ["data", 0, "b64_json"])
        if b64_data:
            image_url = f"data:image/png;base64,{b64_data}"
    if not image_url:
        raise ProviderRequestError(kind="provider", message="Invalid OpenAI-compatible response format", payload=body)

    return GenerationResult(
        url=image_url,
        provider="openai_compatible",
        model=model,
        seed=seed,
        raw_response=body,
    )


def _run_gradio_task(
    base_url: str,
    data: list,
    fn_index: int,
    trigger_id: int,
    token: Optional[str],
    timeout: int,
) -> Dict[str, Any]:
    session_hash = uuid.uuid4().hex[:16]
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    join_payload = {
        "data": data,
        "fn_index": fn_index,
        "trigger_id": trigger_id,
        "session_hash": session_hash,
        "event_data": None,
    }

    try:
        join_response = requests.post(
            f"{base_url}/gradio_api/queue/join",
            headers=headers,
            json=join_payload,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise ProviderRequestError(kind="network", message=f"Hugging Face queue join failed: {exc}")

    if not join_response.ok:
        _raise_response_error(join_response, "Hugging Face queue join failed")

    stream_headers = {"Accept": "text/event-stream"}
    if token:
        stream_headers["Authorization"] = f"Bearer {token}"

    try:
        stream_response = requests.get(
            f"{base_url}/gradio_api/queue/data",
            params={"session_hash": session_hash},
            headers=stream_headers,
            stream=True,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise ProviderRequestError(kind="network", message=f"Hugging Face queue stream failed: {exc}")

    if not stream_response.ok:
        _raise_response_error(stream_response, "Hugging Face queue stream failed")

    for raw_line in stream_response.iter_lines(decode_unicode=True):
        if not raw_line or not raw_line.startswith("data: "):
            continue
        payload = raw_line[6:].strip()
        if not payload:
            continue
        try:
            event = json.loads(payload)
        except json.JSONDecodeError:
            continue

        if event.get("msg") == "process_completed":
            if event.get("success"):
                output = event.get("output")
                if isinstance(output, dict):
                    return output
                raise ProviderRequestError(kind="provider", message="Invalid Hugging Face output payload", payload=event)

            output = event.get("output") or {}
            details = ""
            if isinstance(output, dict):
                details = str(output.get(" ") or output.get("error") or "")
            title = str(event.get("title") or "Hugging Face task failed")
            message = f"{title}: {details}" if details else title
            raise ProviderRequestError(kind=classify_error(message), message=message, payload=event)

    raise ProviderRequestError(kind="provider", message="Hugging Face stream ended without a result")


def _safe_json(response: requests.Response) -> Dict[str, Any]:
    try:
        payload = response.json()
        if isinstance(payload, dict):
            return payload
    except ValueError:
        pass
    return {}


def _extract_qwen_seed(output: Dict[str, Any]) -> Optional[int]:
    data = output.get("data")
    if not isinstance(data, list) or len(data) < 2:
        return None
    seed_text = data[1]
    if not isinstance(seed_text, str):
        return None
    match = re.search(r"(\d+)", seed_text)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def _nested_value(obj: Dict[str, Any], path: list) -> Optional[str]:
    current: Any = obj
    for key in path:
        if isinstance(key, int):
            if not isinstance(current, list) or key >= len(current):
                return None
            current = current[key]
        else:
            if not isinstance(current, dict):
                return None
            current = current.get(key)
    if isinstance(current, str):
        return current
    return None


def _raise_response_error(response: requests.Response, fallback_message: str) -> None:
    body = _safe_json(response)
    message = (
        body.get("message")
        or _nested_value(body, ["error", "message"])
        or body.get("error")
        or fallback_message
    )
    message_str = str(message)
    kind = classify_error(message_str, response.status_code)
    raise ProviderRequestError(
        kind=kind,
        message=f"{message_str} (status={response.status_code})",
        status_code=response.status_code,
        payload=body,
    )
