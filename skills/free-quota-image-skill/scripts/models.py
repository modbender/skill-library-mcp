#!/usr/bin/env python3
"""Shared model and request types for free-quota-image-skill."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

PROVIDERS = ("huggingface", "gitee", "modelscope", "a4f", "openai_compatible")
DEFAULT_PROVIDER_ORDER = ["huggingface", "gitee", "modelscope", "a4f", "openai_compatible"]

PROVIDER_MODEL_ORDER: Dict[str, List[str]] = {
    "huggingface": ["z-image-turbo", "z-image", "qwen-image", "ovis-image", "flux-1-schnell"],
    "gitee": ["z-image-turbo", "qwen-image", "flux-2", "flux-1-schnell", "flux-1-krea", "flux-1"],
    "modelscope": ["z-image-turbo", "z-image", "flux-2", "flux-1-krea", "flux-1"],
    "a4f": ["z-image-turbo", "imagen-4", "imagen-3.5"],
    "openai_compatible": ["Qwen/Qwen-Image", "Kwai-Kolors/Kolors"],
}

PROVIDER_DEFAULT_MODEL: Dict[str, str] = {
    provider: models[0] for provider, models in PROVIDER_MODEL_ORDER.items()
}

API_MODEL_MAP: Dict[str, Dict[str, str]] = {
    "huggingface": {
        "z-image-turbo": "z-image-turbo",
        "z-image": "z-image",
        "qwen-image": "qwen-image-fast",
        "ovis-image": "ovis-image",
        "flux-1-schnell": "flux-1-schnell",
        "openai-fast": "openai-fast",
    },
    "gitee": {
        "z-image-turbo": "z-image-turbo",
        "qwen-image": "Qwen-Image",
        "flux-2": "FLUX.2-dev",
        "flux-1-schnell": "flux-1-schnell",
        "flux-1-krea": "FLUX_1-Krea-dev",
        "flux-1": "FLUX.1-dev",
        "deepseek-3_2": "DeepSeek-V3.2",
    },
    "modelscope": {
        "z-image-turbo": "Tongyi-MAI/Z-Image-Turbo",
        "z-image": "Tongyi-MAI/Z-Image",
        "flux-2": "black-forest-labs/FLUX.2-dev",
        "flux-1-krea": "black-forest-labs/FLUX.1-Krea-dev",
        "flux-1": "MusePublic/489_ckpt_FLUX_1",
        "deepseek-3_2": "deepseek-ai/DeepSeek-V3.2",
    },
    "a4f": {
        "z-image-turbo": "provider-8/z-image",
        "imagen-4": "provider-8/imagen-4",
        "imagen-3.5": "provider-4/imagen-3.5",
        "gemini-2.5-flash-lite": "provider-5/gemini-2.5-flash-lite",
    },
    "openai_compatible": {
        "Qwen/Qwen-Image": "Qwen/Qwen-Image",
        "Kwai-Kolors/Kolors": "Kwai-Kolors/Kolors",
    },
}

PROMPT_OPTIMIZER_DEFAULT_MODEL: Dict[str, str] = {
    "huggingface": "openai-fast",
    "gitee": "deepseek-3_2",
    "modelscope": "deepseek-3_2",
    "a4f": "gemini-2.5-flash-lite",
    "openai_compatible": "openai-fast",
}

ASPECT_RATIO_DIMENSIONS: Dict[str, Dict[str, int]] = {
    "1:1": {"width": 1024, "height": 1024},
    "16:9": {"width": 1024, "height": 576},
    "9:16": {"width": 576, "height": 1024},
    "4:3": {"width": 1024, "height": 768},
    "3:4": {"width": 768, "height": 1024},
    "3:2": {"width": 960, "height": 640},
    "2:3": {"width": 640, "height": 960},
    "4:5": {"width": 819, "height": 1024},
    "5:4": {"width": 1024, "height": 819},
}

STEP_DEFAULTS: Dict[str, Dict[str, int]] = {
    "huggingface": {
        "z-image-turbo": 9,
        "z-image": 30,
        "qwen-image": 8,
        "ovis-image": 20,
        "flux-1-schnell": 8,
    },
    "gitee": {
        "z-image-turbo": 9,
        "qwen-image": 20,
        "flux-2": 20,
        "flux-1-schnell": 8,
        "flux-1-krea": 20,
        "flux-1": 20,
    },
    "modelscope": {
        "z-image-turbo": 9,
        "z-image": 30,
        "flux-2": 20,
        "flux-1-krea": 20,
        "flux-1": 20,
    },
    "a4f": {
        "z-image-turbo": 9,
        "imagen-4": 9,
        "imagen-3.5": 9,
    },
    "openai_compatible": {
        "Qwen/Qwen-Image": 1,
        "Kwai-Kolors/Kolors": 1,
    },
}

GUIDANCE_DEFAULTS: Dict[str, Dict[str, float]] = {
    "huggingface": {"z-image": 4.0},
    "gitee": {
        "flux-1-schnell": 7.5,
        "flux-1-krea": 4.5,
        "flux-1": 4.5,
        "flux-2": 3.5,
    },
    "modelscope": {
        "z-image": 4.0,
        "flux-1-krea": 3.5,
        "flux-1": 3.5,
        "flux-2": 3.5,
    },
    "a4f": {},
    "openai_compatible": {},
}

FLUX_MODEL_PREFIX = "flux"


@dataclass
class GenerationRequest:
    prompt: str
    aspect_ratio: str
    seed: Optional[int] = None
    steps: Optional[int] = None
    guidance_scale: Optional[float] = None
    enable_hd: bool = False


@dataclass
class GenerationResult:
    url: str
    provider: str
    model: str
    seed: Optional[int] = None
    steps: Optional[int] = None
    guidance_scale: Optional[float] = None
    raw_response: Optional[Dict[str, Any]] = None


def ensure_aspect_ratio(value: str) -> str:
    if value in ASPECT_RATIO_DIMENSIONS:
        return value
    return "1:1"


def supports_model(provider: str, model: str) -> bool:
    return model in PROVIDER_MODEL_ORDER.get(provider, [])


def model_candidates(provider: str, requested_model: str) -> List[str]:
    provider_default = PROVIDER_DEFAULT_MODEL[provider]
    chain = [requested_model, "z-image-turbo", provider_default]
    seen = set()
    candidates: List[str] = []
    for model in chain:
        if model in seen:
            continue
        seen.add(model)
        if supports_model(provider, model):
            candidates.append(model)
    return candidates


def default_steps(provider: str, model: str) -> Optional[int]:
    return STEP_DEFAULTS.get(provider, {}).get(model)


def default_guidance(provider: str, model: str) -> Optional[float]:
    return GUIDANCE_DEFAULTS.get(provider, {}).get(model)


def is_flux_model(model: str) -> bool:
    return model.startswith(FLUX_MODEL_PREFIX)


def _hd_multiplier(provider: str, model: str) -> float:
    if provider == "gitee" and is_flux_model(model):
        return 1.5
    return 2.0


def dimensions_for(provider: str, model: str, aspect_ratio: str, enable_hd: bool) -> Dict[str, int]:
    ratio = ensure_aspect_ratio(aspect_ratio)
    base = ASPECT_RATIO_DIMENSIONS[ratio]
    if not enable_hd:
        return {"width": base["width"], "height": base["height"]}

    multiplier = _hd_multiplier(provider, model)
    return {
        "width": int(round(base["width"] * multiplier)),
        "height": int(round(base["height"] * multiplier)),
    }
