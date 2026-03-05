#!/usr/bin/env python3
"""Prompt optimization and translation helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import requests

from models import API_MODEL_MAP, PROMPT_OPTIMIZER_DEFAULT_MODEL

POLLINATIONS_API_URL = "https://text.pollinations.ai/openai"
GITEE_CHAT_API_URL = "https://ai.gitee.com/v1/chat/completions"
MODELSCOPE_CHAT_API_URL = "https://api-inference.modelscope.cn/v1/chat/completions"
A4F_CHAT_API_URL = "https://api.a4f.co/v1/chat/completions"

FIXED_SYSTEM_PROMPT_SUFFIX = (
    "\nEnsure the output language matches the language of user's prompt that needs to be optimized."
)

DEFAULT_SYSTEM_PROMPT = (
    "I am a master AI image prompt engineering advisor, specializing in crafting prompts that yield cinematic, "
    "hyper-realistic, and deeply evocative visual narratives, optimized for advanced generative models.\n"
    "My core purpose is to meticulously rewrite, expand, and enhance user's image prompts.\n"
    "I transform prompts to create visually stunning images by rigorously optimizing dramatic lighting, textures, "
    "composition, and artistic style.\n"
    "My generated prompt output will be strictly under 300 words.\n"
    "My output will consist exclusively of the refined image prompt text with no markdown or explanations.\n"
    "The character's face is clearly visible and unobstructed."
)

DEFAULT_TRANSLATION_SYSTEM_PROMPT = (
    "You are a professional language translation engine.\n"
    "Translate user text into English. If already English, return it unchanged.\n"
    "Output only the final English text with no extra commentary."
)


@dataclass
class PromptToolError(Exception):
    message: str

    def __str__(self) -> str:
        return self.message


def prepare_prompt(
    prompt_original: str,
    provider: str,
    model: str,
    token: Optional[str],
    prompt_optimization_cfg: Dict[str, object],
    translation_cfg: Dict[str, object],
    optimize_enabled: bool,
    auto_translate_enabled: bool,
    timeout: int = 60,
) -> str:
    current_prompt = prompt_original
    optimize_supported = provider in {"huggingface", "gitee", "modelscope", "a4f"}

    if auto_translate_enabled and bool(translation_cfg.get("enabled", False)):
        target_models = translation_cfg.get("target_models", [])
        if isinstance(target_models, list) and model in target_models:
            try:
                current_prompt = translate_prompt(current_prompt, timeout=timeout)
            except PromptToolError:
                pass

    if optimize_supported and optimize_enabled and bool(prompt_optimization_cfg.get("enabled", True)):
        try:
            current_prompt = optimize_prompt(
                prompt=current_prompt,
                provider=provider,
                token=token,
                prompt_optimization_cfg=prompt_optimization_cfg,
                timeout=timeout,
            )
        except PromptToolError:
            pass

    return current_prompt


def translate_prompt(text: str, timeout: int = 60) -> str:
    payload = {
        "model": "openai-fast",
        "messages": [
            {"role": "system", "content": DEFAULT_TRANSLATION_SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        "stream": False,
    }

    try:
        response = requests.post(POLLINATIONS_API_URL, json=payload, timeout=timeout)
    except requests.RequestException as exc:
        raise PromptToolError(f"Translation request failed: {exc}")

    if not response.ok:
        raise PromptToolError(f"Translation failed: status={response.status_code}")

    content = _extract_message_content(response)
    return content or text


def optimize_prompt(
    prompt: str,
    provider: str,
    token: Optional[str],
    prompt_optimization_cfg: Dict[str, object],
    timeout: int = 60,
) -> str:
    default_models = prompt_optimization_cfg.get("default_model_by_provider", {})
    model_key = PROMPT_OPTIMIZER_DEFAULT_MODEL.get(provider, "openai-fast")
    if isinstance(default_models, dict):
        model_key = str(default_models.get(provider, model_key))

    system_prompt = str(prompt_optimization_cfg.get("system_prompt", DEFAULT_SYSTEM_PROMPT)) + FIXED_SYSTEM_PROMPT_SUFFIX

    if provider == "huggingface":
        api_model = API_MODEL_MAP["huggingface"].get(model_key, model_key)
        payload = {
            "model": api_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
        }
        return _chat_request(POLLINATIONS_API_URL, payload, headers={}, timeout=timeout, fallback=prompt)

    if provider == "gitee":
        if not token:
            raise PromptToolError("Gitee token is required for prompt optimization")
        api_model = API_MODEL_MAP["gitee"].get(model_key, model_key)
        payload = {
            "model": api_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
        }
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        return _chat_request(GITEE_CHAT_API_URL, payload, headers=headers, timeout=timeout, fallback=prompt)

    if provider == "modelscope":
        if not token:
            raise PromptToolError("ModelScope token is required for prompt optimization")
        api_model = API_MODEL_MAP["modelscope"].get(model_key, model_key)
        payload = {
            "model": api_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
        }
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        return _chat_request(MODELSCOPE_CHAT_API_URL, payload, headers=headers, timeout=timeout, fallback=prompt)

    if provider == "a4f":
        if not token:
            raise PromptToolError("A4F token is required for prompt optimization")
        api_model = API_MODEL_MAP["a4f"].get(model_key, model_key)
        payload = {
            "model": api_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
        }
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        return _chat_request(A4F_CHAT_API_URL, payload, headers=headers, timeout=timeout, fallback=prompt)

    raise PromptToolError(f"Unsupported provider for prompt optimization: {provider}")


def _chat_request(url: str, payload: Dict[str, object], headers: Dict[str, str], timeout: int, fallback: str) -> str:
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=timeout)
    except requests.RequestException as exc:
        raise PromptToolError(f"Prompt optimization request failed: {exc}")

    if not response.ok:
        raise PromptToolError(f"Prompt optimization failed: status={response.status_code}")

    content = _extract_message_content(response)
    return content or fallback


def _extract_message_content(response: requests.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return ""

    if not isinstance(payload, dict):
        return ""

    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""

    first = choices[0]
    if not isinstance(first, dict):
        return ""

    message = first.get("message")
    if not isinstance(message, dict):
        return ""

    content = message.get("content")
    if isinstance(content, str):
        return content.strip()
    return ""
