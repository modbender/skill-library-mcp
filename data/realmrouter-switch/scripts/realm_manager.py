#!/usr/bin/env python3
"""
RealmRouter model switcher for OpenClaw.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from urllib import error, request

API_BASE = "https://realmrouter.cn/v1"
DEFAULT_CONFIG = Path.home() / ".openclaw" / "openclaw.json"
BACKUP_DIR = Path.home() / ".openclaw" / "backups"
KEY_ENV = "REALMROUTER_API_KEY"

MODELS = {
    "anthropic": [
        "claude-haiku-4.5",
        "claude-opus-4-5-thinking",
        "claude-opus-4-6-thinking",
        "claude-sonnet-4-5",
        "claude-opus-4.6",
        "claude-sonnet-4.6",
    ],
    "openai": ["gpt-5.2", "gpt-5.2-codex", "gpt-5.3-codex", "openai/gpt-oss-120b"],
    "qwen": [
        "qwen3-max",
        "qwen3-coder-plus",
        "qwen3-max-preview",
        "qwen3-vl-plus",
        "qwen3-vl-max",
        "Qwen/Qwen3.5",
        "Qwen/Qwen3-Coder-Next",
        "Qwen/Qwen3-Coder-480B-A35B-Instruct",
    ],
    "deepseek": [
        "deepseek-ai/DeepSeek-R1",
        "deepseek-ai/DeepSeek-R1-0528",
        "deepseek-ai/DeepSeek-V3.1",
        "deepseek-ai/DeepSeek-V3.1-Terminus",
        "deepseek-ai/DeepSeek-V3.2-Exp",
    ],
    "google": ["gemini-3.1-pro-high", "gemini-3.1-pro-low"],
    "minimax": ["MiniMaxAI/MiniMax-M2.1", "MiniMaxAI/MiniMax-M2.5"],
    "moonshot": ["moonshotai/Kimi-K2.5", "moonshotai/Kimi-K2-Thinking"],
    "bytedance": ["doubao-seed-code-preview-251028"],
    "zai": ["zai-org/GLM-4.7", "zai-org/GLM-4.6V", "zai-org/GLM-5"],
}

PREFERRED = [
    "claude-opus-4-6-thinking",
    "claude-sonnet-4.6",
    "gpt-5.3-codex",
    "gpt-5.2-codex",
    "qwen3-max",
    "qwen3-coder-plus",
    "deepseek-ai/DeepSeek-R1",
    "deepseek-ai/DeepSeek-V3.1",
    "gemini-3.1-pro-high",
]

ALIASES = {
    "opus": "claude-opus-4-6-thinking",
    "sonnet": "claude-sonnet-4.6",
    "gpt53": "gpt-5.3-codex",
    "gpt52": "gpt-5.2-codex",
    "qwen": "qwen3-max",
    "r1": "deepseek-ai/DeepSeek-R1",
    "gemini": "gemini-3.1-pro-high",
}

KNOWN_MODELS = {m for group in MODELS.values() for m in group}


def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def load_config(path: Path) -> dict:
    if not path.exists():
        die(f"OpenClaw config not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        die(f"Invalid JSON in {path}: {e}")


def save_config(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def backup_config(path: Path) -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"openclaw.json.bak.{ts}"
    shutil.copy2(path, backup)
    return backup


def latest_backup() -> Path | None:
    if not BACKUP_DIR.exists():
        return None
    backups = sorted(BACKUP_DIR.glob("openclaw.json.bak.*"), reverse=True)
    return backups[0] if backups else None


def ensure_schema(cfg: dict) -> None:
    cfg.setdefault("models", {})
    cfg["models"].setdefault("providers", {})
    cfg.setdefault("agents", {})
    cfg["agents"].setdefault("defaults", {})
    cfg["agents"]["defaults"].setdefault("model", {})


def normalize_model_id(model: str) -> str:
    model = model.strip()
    model = model.split("realmrouter/", 1)[1] if model.startswith("realmrouter/") else model
    return ALIASES.get(model.lower(), model)


def provider_models() -> list[dict]:
    return [{"id": m, "name": m} for m in sorted(KNOWN_MODELS)]


def configured_key(cfg: dict) -> str:
    return (
        cfg.get("models", {})
        .get("providers", {})
        .get("realmrouter", {})
        .get("apiKey", "")
        .strip()
    )


def configured_model(cfg: dict) -> str:
    return (
        cfg.get("agents", {})
        .get("defaults", {})
        .get("model", {})
        .get("primary", "realmrouter/qwen3-max")
    )


def resolve_api_key(explicit: str, cfg: dict | None = None) -> str:
    if explicit and explicit.strip():
        return explicit.strip()
    env = os.environ.get(KEY_ENV, "").strip()
    if env:
        return env
    if cfg is not None:
        return configured_key(cfg)
    return ""


def maybe_restart_gateway(should_restart: bool) -> None:
    if not should_restart:
        print("Hint: run 'openclaw gateway restart' to apply changes.")
        return
    try:
        subprocess.run(["openclaw", "gateway", "restart"], check=True)
        print("OK: gateway restarted")
    except Exception as e:
        print(f"WARN: gateway restart failed: {e}")


def test_connectivity(api_key: str, model: str) -> tuple[bool, int, str]:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 1,
    }
    req = request.Request(
        f"{API_BASE}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
            return True, resp.status, body
    except error.HTTPError as e:
        return False, e.code, e.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return False, 0, str(e)


def verify_key_usable(api_key: str, model: str) -> tuple[bool, int, str]:
    return test_connectivity(api_key, model)


def resolve_model_input(raw: str) -> str:
    raw = raw.strip()
    if raw.isdigit():
        idx = int(raw)
        ordered = model_picker_order()
        if 1 <= idx <= len(ordered):
            return ordered[idx - 1]
        die(f"Model number out of range: {idx}")
    return normalize_model_id(raw)


def model_picker_order() -> list[str]:
    seen = set()
    ordered = []
    for m in PREFERRED + sorted(KNOWN_MODELS):
        if m not in seen:
            seen.add(m)
            ordered.append(m)
    return ordered


def cmd_models_picker(_: argparse.Namespace) -> None:
    ordered = model_picker_order()
    for i, model in enumerate(ordered, 1):
        print(f"[{i}] {model}")


def cmd_install(args: argparse.Namespace) -> None:
    cfg = load_config(args.config)
    api_key = resolve_api_key(args.api_key)
    if not api_key:
        die(f"API key required. Use --api-key or env {KEY_ENV}")

    model = resolve_model_input(args.default_model)

    ok, status, body = verify_key_usable(api_key, model)
    if not ok and not args.force:
        print(f"KEY_VERIFY_FAIL: model={model} http={status}")
        if body:
            print(body[:300])
        die("API key verification failed. Re-run with --force to continue anyway.")

    ensure_schema(cfg)
    backup = backup_config(args.config)

    cfg["models"]["providers"]["realmrouter"] = {
        "baseUrl": API_BASE,
        "apiKey": api_key,
        "api": "openai-completions",
        "models": provider_models(),
    }
    cfg["agents"]["defaults"]["model"]["primary"] = f"realmrouter/{model}"
    save_config(args.config, cfg)

    print(f"OK: installed/updated realmrouter provider, default=realmrouter/{model}")
    print(f"Backup: {backup}")
    if model not in KNOWN_MODELS:
        print(f"WARN: custom model id used: {model}")
    maybe_restart_gateway(args.restart_gateway)


def cmd_update_key(args: argparse.Namespace) -> None:
    cfg = load_config(args.config)
    api_key = resolve_api_key(args.api_key)
    if not api_key:
        die(f"API key required. Use --api-key or env {KEY_ENV}")

    ensure_schema(cfg)
    if "realmrouter" not in cfg["models"]["providers"]:
        die("realmrouter provider not found. Run install first.")

    verify_model = resolve_model_input(args.verify_model) if args.verify_model else normalize_model_id(configured_model(cfg))
    ok, status, body = verify_key_usable(api_key, verify_model)
    if not ok and not args.force:
        print(f"KEY_VERIFY_FAIL: model={verify_model} http={status}")
        if body:
            print(body[:300])
        die("API key verification failed. Re-run with --force to continue anyway.")

    backup = backup_config(args.config)
    cfg["models"]["providers"]["realmrouter"]["apiKey"] = api_key
    save_config(args.config, cfg)
    print("OK: API key updated")
    print(f"Backup: {backup}")
    maybe_restart_gateway(args.restart_gateway)


def cmd_switch_model(args: argparse.Namespace) -> None:
    cfg = load_config(args.config)
    ensure_schema(cfg)

    model = resolve_model_input(args.model)

    key = resolve_api_key(args.api_key, cfg)
    if not key:
        die("No API key found. Set key first before switching model.")

    # Always precheck by default (user request). Use --skip-precheck to bypass.
    if not args.skip_precheck:
        ok, status, body = test_connectivity(key, model)
        if not ok:
            print(f"MODEL_VERIFY_FAIL: model={model} http={status}")
            if body:
                print(body[:300])
            if not args.force:
                die("Model verification failed. Re-run with --force or --skip-precheck to switch anyway.")

    backup = backup_config(args.config)
    cfg["agents"]["defaults"]["model"]["primary"] = f"realmrouter/{model}"
    save_config(args.config, cfg)

    print(f"OK: switched to realmrouter/{model}")
    print(f"Backup: {backup}")
    if model not in KNOWN_MODELS:
        print(f"WARN: custom model id used: {model}")
    maybe_restart_gateway(args.restart_gateway)


def cmd_test(args: argparse.Namespace) -> None:
    cfg = load_config(args.config)
    key = resolve_api_key(args.api_key, cfg)
    if not key:
        die(f"No API key found. Set --api-key or env {KEY_ENV}")

    model = resolve_model_input(args.model) if args.model else normalize_model_id(configured_model(cfg))
    ok, status, body = test_connectivity(key, model)
    print(f"Model: {model}")
    print(f"HTTP: {status}")
    if ok:
        print("OK: connectivity test passed")
        raise SystemExit(0)

    print("FAIL: connectivity test failed")
    if body:
        print(body[:800])
    raise SystemExit(2)


def cmd_show(args: argparse.Namespace) -> None:
    cfg = load_config(args.config)
    provider = "present" if cfg.get("models", {}).get("providers", {}).get("realmrouter") else "missing"
    model = configured_model(cfg)
    key = configured_key(cfg)
    masked = ("*" * max(0, len(key) - 4) + key[-4:]) if key else "(not set)"
    print("realmrouter provider:", provider)
    print("primary model:", model)
    print("api key:", masked)


def cmd_list_models(_: argparse.Namespace) -> None:
    for provider, models in MODELS.items():
        print(f"[{provider}]")
        for m in models:
            print(f"  - {m}")


def cmd_rollback(args: argparse.Namespace) -> None:
    if args.backup:
        backup = Path(args.backup).expanduser().resolve()
    else:
        maybe = latest_backup()
        if not maybe:
            die("No backup found in ~/.openclaw/backups")
        backup = maybe

    if not backup.exists():
        die(f"Backup not found: {backup}")

    current_backup = backup_config(args.config)
    shutil.copy2(backup, args.config)
    print(f"OK: restored from {backup}")
    print(f"Current config backup: {current_backup}")
    maybe_restart_gateway(args.restart_gateway)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="RealmRouter/OpenClaw config manager")
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="path to openclaw.json")
    sub = p.add_subparsers(dest="cmd", required=True)

    s1 = sub.add_parser("install", help="inject/refresh provider and set default model")
    s1.add_argument("--api-key", default="", help=f"RealmRouter key (or env {KEY_ENV})")
    s1.add_argument("--default-model", default="qwen3-max", help="model id / alias / picker index")
    s1.add_argument("--force", action="store_true", help="continue even if key verification fails")
    s1.add_argument("--restart-gateway", action="store_true")
    s1.set_defaults(func=cmd_install)

    s2 = sub.add_parser("update-key", help="update API key")
    s2.add_argument("--api-key", default="", help=f"RealmRouter key (or env {KEY_ENV})")
    s2.add_argument("--verify-model", default="", help="verify key using this model (default: current model)")
    s2.add_argument("--force", action="store_true", help="continue even if key verification fails")
    s2.add_argument("--restart-gateway", action="store_true")
    s2.set_defaults(func=cmd_update_key)

    s2b = sub.add_parser("set-key", help="alias of update-key")
    s2b.add_argument("--api-key", default="", help=f"RealmRouter key (or env {KEY_ENV})")
    s2b.add_argument("--verify-model", default="", help="verify key using this model (default: current model)")
    s2b.add_argument("--force", action="store_true", help="continue even if key verification fails")
    s2b.add_argument("--restart-gateway", action="store_true")
    s2b.set_defaults(func=cmd_update_key)

    s3 = sub.add_parser("switch-model", help="switch default model")
    s3.add_argument("--model", required=True, help="model id / alias / picker index")
    s3.add_argument("--api-key", default="", help="optional key override for verification")
    s3.add_argument("--skip-precheck", action="store_true", help="skip model verification before switching")
    s3.add_argument("--force", action="store_true", help="switch even when verification fails")
    s3.add_argument("--restart-gateway", action="store_true")
    s3.set_defaults(func=cmd_switch_model)

    s4 = sub.add_parser("set-model", help="alias of switch-model")
    s4.add_argument("--model", required=True)
    s4.add_argument("--api-key", default="")
    s4.add_argument("--skip-precheck", action="store_true")
    s4.add_argument("--force", action="store_true")
    s4.add_argument("--restart-gateway", action="store_true")
    s4.set_defaults(func=cmd_switch_model)

    s5 = sub.add_parser("test", help="test connectivity")
    s5.add_argument("--api-key", default="", help=f"override key (or env {KEY_ENV})")
    s5.add_argument("--model", default="", help="override model")
    s5.set_defaults(func=cmd_test)

    s6 = sub.add_parser("show", help="show provider/model/key status")
    s6.set_defaults(func=cmd_show)

    s7 = sub.add_parser("list-models", help="print built-in model ids by provider")
    s7.set_defaults(func=cmd_list_models)

    s8 = sub.add_parser("models", help="print numbered model picker list")
    s8.set_defaults(func=cmd_models_picker)

    s9 = sub.add_parser("rollback", help="restore latest backup (or target backup)")
    s9.add_argument("--backup", default="", help="backup file path")
    s9.add_argument("--restart-gateway", action="store_true")
    s9.set_defaults(func=cmd_rollback)

    return p


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
