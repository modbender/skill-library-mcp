#!/usr/bin/env python3
"""CLI entrypoint for free-quota-first text-to-image generation."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import requests
import yaml

from models import (
    DEFAULT_PROVIDER_ORDER,
    PROVIDER_MODEL_ORDER,
    GenerationRequest,
    model_candidates,
)
from prompt_tools import DEFAULT_SYSTEM_PROMPT, prepare_prompt
from provider_clients import ProviderRequestError, generate
from token_pool import TokenPool

DEFAULT_STATE_FILE = "~/.codex/skills/.state/free-quota-image-skill/token_status.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "providers": {
        "huggingface": {"enabled": True, "tokens": [], "allow_public_quota": True},
        "gitee": {"enabled": True, "tokens": []},
        "modelscope": {"enabled": True, "tokens": []},
        "a4f": {"enabled": True, "tokens": []},
        "openai_compatible": {
            "enabled": False,
            "tokens": [],
            "api_url": "",
            "images_endpoint": "/images/generations",
        },
    },
    "routing": {"provider_order": DEFAULT_PROVIDER_ORDER},
    "prompt_optimization": {
        "enabled": True,
        "default_model_by_provider": {
            "huggingface": "openai-fast",
            "gitee": "deepseek-3_2",
            "modelscope": "deepseek-3_2",
            "a4f": "gemini-2.5-flash-lite",
        },
        "system_prompt": DEFAULT_SYSTEM_PROMPT,
    },
    "translation": {
        "enabled": False,
        "target_models": ["flux-1-schnell", "flux-1-krea", "flux-1", "flux-2"],
    },
    "state": {
        "token_status_file": DEFAULT_STATE_FILE,
    },
}


class ValidationError(Exception):
    pass


def load_dotenv() -> None:
    script_dir = Path(__file__).resolve().parent
    candidates = [
        Path.cwd() / ".env",
        script_dir.parent / ".env",
        script_dir.parent.parent / ".env",
    ]
    seen = set()
    for path in candidates:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        _load_dotenv_file(path)


def _load_dotenv_file(path: Path) -> None:
    if not path.exists() or not path.is_file():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        value = _strip_env_quotes(value.strip())
        os.environ.setdefault(key, value)


def _strip_env_quotes(value: str) -> str:
    if len(value) >= 2 and ((value[0] == '"' and value[-1] == '"') or (value[0] == "'" and value[-1] == "'")):
        return value[1:-1]
    return value


def parse_args() -> argparse.Namespace:
    script_dir = Path(__file__).resolve().parent
    default_config = script_dir.parent / "assets" / "config.example.yaml"

    parser = argparse.ArgumentParser(description="Free-quota-first text-to-image generator")
    parser.add_argument("--prompt", required=True, help="Prompt text")
    parser.add_argument(
        "--provider",
        default="auto",
        choices=["auto", "huggingface", "gitee", "modelscope", "a4f", "openai_compatible"],
        help="Provider routing mode",
    )
    parser.add_argument("--model", default="z-image-turbo", help="Requested model name")
    parser.add_argument("--aspect-ratio", default="1:1", help="Aspect ratio, e.g. 1:1, 16:9")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--steps", type=int, default=None)
    parser.add_argument("--guidance-scale", type=float, default=None)
    parser.add_argument("--enable-hd", action="store_true", help="Enable HD upscale for supported providers")
    parser.add_argument("--optimize-prompt", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--auto-translate", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--config", default=str(default_config), help="Path to YAML config")
    parser.add_argument("--output", default=None, help="Download output image to file path")
    parser.add_argument("--count", type=int, default=1, help="Number of images to generate in one run")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON output")
    parser.add_argument("--timeout", type=int, default=180, help="Request timeout in seconds")
    return parser.parse_args()


def load_config(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise ValidationError(f"Config file not found: {path}")

    try:
        user_cfg = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ValidationError(f"Config YAML is invalid: {exc}")

    if not isinstance(user_cfg, dict):
        raise ValidationError("Config root must be a mapping")

    merged = _deep_merge(DEFAULT_CONFIG, user_cfg)
    merged = _resolve_env_placeholders(merged)
    validate_config(merged)
    return merged


def validate_config(config: Dict[str, Any]) -> None:
    providers = config.get("providers")
    if not isinstance(providers, dict):
        raise ValidationError("config.providers must be a mapping")

    for provider in DEFAULT_PROVIDER_ORDER:
        if provider not in providers:
            raise ValidationError(f"Missing provider config: providers.{provider}")

    routing = config.get("routing", {})
    order = routing.get("provider_order") if isinstance(routing, dict) else None
    if not isinstance(order, list) or not order:
        raise ValidationError("routing.provider_order must be a non-empty list")

    invalid = [p for p in order if p not in DEFAULT_PROVIDER_ORDER]
    if invalid:
        raise ValidationError(f"routing.provider_order contains unsupported providers: {', '.join(invalid)}")

    openai_cfg = providers.get("openai_compatible", {})
    if isinstance(openai_cfg, dict) and bool(openai_cfg.get("enabled", False)):
        api_url = str(openai_cfg.get("api_url", "")).strip()
        if not api_url:
            raise ValidationError("providers.openai_compatible.api_url is required when enabled")


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    output: Dict[str, Any] = {}
    for key, value in base.items():
        if key in override:
            override_value = override[key]
            if isinstance(value, dict) and isinstance(override_value, dict):
                output[key] = _deep_merge(value, override_value)
            else:
                output[key] = override_value
        else:
            output[key] = value

    for key, value in override.items():
        if key not in output:
            output[key] = value
    return output


_ENV_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def _resolve_env_placeholders(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _resolve_env_placeholders(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_env_placeholders(v) for v in value]
    if isinstance(value, str):
        return _ENV_PATTERN.sub(lambda m: os.environ.get(m.group(1), ""), value)
    return value


def resolve_provider_order(cli_provider: str, config: Dict[str, Any]) -> List[str]:
    providers_cfg = config.get("providers", {})
    if cli_provider != "auto":
        provider_cfg = providers_cfg.get(cli_provider, {})
        if not isinstance(provider_cfg, dict) or not bool(provider_cfg.get("enabled", True)):
            return []
        return [cli_provider]

    configured_order = config.get("routing", {}).get("provider_order", DEFAULT_PROVIDER_ORDER)
    order: List[str] = []
    for provider in configured_order:
        provider_cfg = providers_cfg.get(provider, {})
        if isinstance(provider_cfg, dict) and bool(provider_cfg.get("enabled", True)):
            order.append(provider)
    return order


def main() -> int:
    load_dotenv()
    args = parse_args()
    started = time.time()

    try:
        config = load_config(Path(args.config).expanduser())
    except ValidationError as exc:
        return _emit_error(args.json, "validation", str(exc), fallback_chain=[])

    state_file = Path(str(config.get("state", {}).get("token_status_file", DEFAULT_STATE_FILE))).expanduser()
    token_pool = TokenPool(state_file=state_file, providers_config=config.get("providers", {}))

    fallback_chain: List[str] = []
    provider_order = resolve_provider_order(args.provider, config)
    if not provider_order:
        return _emit_error(args.json, "validation", "No enabled providers available", fallback_chain=fallback_chain)

    if args.count < 1:
        return _emit_error(args.json, "validation", "--count must be >= 1", fallback_chain=fallback_chain)

    images: List[Dict[str, Any]] = []
    for index in range(args.count):
        if args.seed is None:
            current_seed = None
        else:
            current_seed = args.seed + index

        if args.count > 1 and args.provider == "auto":
            run_provider_order = _rotate_list(provider_order, index)
        else:
            run_provider_order = provider_order

        one = _generate_single_image(
            provider_order=run_provider_order,
            config=config,
            prompt=args.prompt,
            requested_model=args.model,
            aspect_ratio=args.aspect_ratio,
            seed=current_seed,
            steps=args.steps,
            guidance_scale=args.guidance_scale,
            enable_hd=args.enable_hd,
            optimize_prompt=args.optimize_prompt,
            auto_translate=args.auto_translate,
            timeout=args.timeout,
            fallback_chain=fallback_chain,
            token_pool=token_pool,
            attempt_offset=index,
        )

        if not one:
            return _emit_error(args.json, "provider", "All providers failed", fallback_chain=fallback_chain)

        result, prepared_prompt = one
        payload = {
            "id": str(uuid.uuid4()),
            "url": result.url,
            "provider": result.provider,
            "model": result.model,
            "prompt_original": args.prompt,
            "prompt_final": prepared_prompt,
            "seed": result.seed,
            "steps": result.steps,
            "guidance_scale": result.guidance_scale,
            "aspect_ratio": args.aspect_ratio,
            "fallback_chain": list(fallback_chain),
            "elapsed_ms": int((time.time() - started) * 1000),
        }
        images.append(payload)

    if args.output:
        output_path = Path(args.output).expanduser()
        if args.count == 1:
            try:
                download_to_file(images[0]["url"], output_path, timeout=args.timeout)
            except Exception as exc:  # pylint: disable=broad-except
                return _emit_error(
                    args.json,
                    "network",
                    f"Image generated but download failed: {exc}",
                    fallback_chain=fallback_chain,
                )
        else:
            output_path.mkdir(parents=True, exist_ok=True)
            for idx, item in enumerate(images, start=1):
                try:
                    download_to_file(item["url"], output_path / f"image-{idx:02d}.png", timeout=args.timeout)
                except Exception as exc:  # pylint: disable=broad-except
                    return _emit_error(
                        args.json,
                        "network",
                        f"Image {idx} generated but download failed: {exc}",
                        fallback_chain=fallback_chain,
                    )

    if args.count == 1:
        return _emit_success(args.json, images[0])
    return _emit_success(
        args.json,
        {
            "count": len(images),
            "images": images,
            "elapsed_ms": int((time.time() - started) * 1000),
        },
    )


def _generate_single_image(
    provider_order: List[str],
    config: Dict[str, Any],
    prompt: str,
    requested_model: str,
    aspect_ratio: str,
    seed: Optional[int],
    steps: Optional[int],
    guidance_scale: Optional[float],
    enable_hd: bool,
    optimize_prompt: bool,
    auto_translate: bool,
    timeout: int,
    fallback_chain: List[str],
    token_pool: TokenPool,
    attempt_offset: int = 0,
) -> Optional[Tuple[Any, str]]:
    for provider in provider_order:
        model_chain = model_candidates(provider, requested_model)
        if not model_chain:
            model_chain = [PROVIDER_MODEL_ORDER[provider][0]]

        for model in model_chain:
            provider_cfg = config.get("providers", {}).get(provider, {})
            allow_public = provider == "huggingface" and bool(provider_cfg.get("allow_public_quota", True))
            attempts = token_pool.available_attempts(provider, allow_public=allow_public)
            attempts = _rotate_list(attempts, attempt_offset)

            if not attempts:
                fallback_chain.append(f"{provider}(no-token)")
                continue

            prompt_token = attempts[0].token
            prepared_prompt = prepare_prompt(
                prompt_original=prompt,
                provider=provider,
                model=model,
                token=prompt_token,
                prompt_optimization_cfg=config.get("prompt_optimization", {}),
                translation_cfg=config.get("translation", {}),
                optimize_enabled=optimize_prompt,
                auto_translate_enabled=auto_translate,
                timeout=max(30, timeout // 2),
            )

            for attempt in attempts:
                fallback_chain.append(f"{provider}({attempt.label})")
                request_data = GenerationRequest(
                    prompt=prepared_prompt,
                    aspect_ratio=aspect_ratio,
                    seed=seed,
                    steps=steps,
                    guidance_scale=guidance_scale,
                    enable_hd=enable_hd,
                )

                try:
                    result = generate(
                        provider=provider,
                        model=model,
                        request_data=request_data,
                        token=attempt.token,
                        timeout=timeout,
                        provider_config=provider_cfg if isinstance(provider_cfg, dict) else {},
                    )
                    return result, prepared_prompt
                except ProviderRequestError as exc:
                    if exc.kind == "quota" and attempt.token is not None:
                        token_pool.mark_exhausted(provider, attempt.token)
                        continue
                    if exc.kind == "auth" and attempt.token is not None:
                        continue
                    break
    return None


def _rotate_list(items: Sequence[Any], offset: int) -> List[Any]:
    values = list(items)
    if not values:
        return values
    shift = offset % len(values)
    if shift == 0:
        return values
    return values[shift:] + values[:shift]


def download_to_file(url: str, output_path: Path, timeout: int) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, stream=True, timeout=timeout)
    response.raise_for_status()
    with output_path.open("wb") as handle:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                handle.write(chunk)


def _emit_success(as_json: bool, payload: Dict[str, Any]) -> int:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        if "url" in payload:
            print(payload["url"])
        else:
            images = payload.get("images", [])
            for item in images:
                url = item.get("url")
                if isinstance(url, str):
                    print(url)
    return 0


def _emit_error(as_json: bool, kind: str, message: str, fallback_chain: List[str]) -> int:
    if as_json:
        payload = {
            "error_type": kind,
            "error": message,
            "fallback_chain": fallback_chain,
        }
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print(f"[{kind}] {message}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
