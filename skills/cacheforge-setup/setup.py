#!/usr/bin/env python3
"""CacheForge setup CLI — register, configure upstream, get your API key in 30 seconds."""

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path

# ── ANSI colors ──────────────────────────────────────────────────────────────

CYAN = "\033[36m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

# ── Helpers ──────────────────────────────────────────────────────────────────

DEFAULT_BASE_URL = "https://app.anvil-ai.io"
DEFAULT_OPENCLAW_CONFIG_PATH = "~/.openclaw/openclaw.json"
OPENROUTER_POPULAR_MODEL_CANDIDATES: list[tuple[str, str]] = [
    ("anthropic/claude-opus-4.6", "OpenRouter: Claude Opus 4.6"),
    ("openai/gpt-5.2", "OpenRouter: GPT-5.2"),
    ("anthropic/claude-sonnet-4.5", "OpenRouter: Claude Sonnet 4.5"),
    ("moonshotai/kimi-k2.5", "OpenRouter: Kimi K2.5"),
]
UPSTREAM_DEFAULT_BASE_URLS: dict[str, str] = {
    "openrouter": "https://openrouter.ai/api/v1",
    "anthropic": "https://api.anthropic.com",
    "custom": "https://api.fireworks.ai/inference/v1",
}
LEGACY_OPENAI_BASE_URL = "https://api.openai.com"

def normalize_base_url(url: str) -> str:
    """Normalize a CacheForge base URL (accepts both with and without /v1)."""
    url = (url or "").strip().rstrip("/")
    if url.endswith("/v1"):
        url = url[:-3]
    return url.rstrip("/")


def get_base_url(args_base_url: str | None) -> str:
    """Resolve base URL from arg, env, or default."""
    url = args_base_url or os.environ.get("CACHEFORGE_BASE_URL") or DEFAULT_BASE_URL
    return normalize_base_url(url)


def box(title: str, lines: list[tuple[str, str]], color: str = CYAN) -> str:
    """Render a Unicode box with key-value lines."""
    # Calculate width from content
    content_lines = []
    for label, value in lines:
        content_lines.append(f"  {label}: {value}")

    max_width = max(len(title) + 4, *(len(l) for l in content_lines)) + 4
    width = max(max_width, 50)

    parts = []
    parts.append(f"{color}{BOLD}  {title}{RESET}")
    parts.append(f"{color}  {'─' * width}{RESET}")
    for label, value in lines:
        parts.append(f"{DIM}  {label}:{RESET} {GREEN}{value}{RESET}")
    parts.append(f"{color}  {'─' * width}{RESET}")
    return "\n".join(parts)


def draw_box(title: str, lines: list[tuple[str, str]], color: str = CYAN) -> str:
    """Render a framed Unicode box with box-drawing characters."""
    content_lines = []
    for label, value in lines:
        content_lines.append((f" {label}: ", f"{value} "))

    inner_widths = []
    for label_part, value_part in content_lines:
        inner_widths.append(len(label_part) + len(value_part))
    title_display = f" {title} "
    inner_widths.append(len(title_display))
    inner_width = max(max(inner_widths), 48)

    parts = []
    # Top border
    parts.append(f"{color}{BOLD}")
    parts.append(f"  ┌{'─' * inner_width}┐")
    parts.append(f"  │{title_display}{' ' * (inner_width - len(title_display))}│")
    parts.append(f"  ├{'─' * inner_width}┤")

    # Content lines
    for label_part, value_part in content_lines:
        raw = label_part + value_part
        padding = inner_width - len(raw)
        parts.append(
            f"  │{DIM}{label_part}{RESET}{color}{GREEN}{value_part}{RESET}"
            f"{color}{BOLD}{' ' * padding}│"
        )

    # Bottom border
    parts.append(f"  └{'─' * inner_width}┘")
    parts.append(f"{RESET}")
    return "\n".join(parts)


def http_post(url: str, payload: dict) -> dict:
    """POST JSON to a URL, return parsed response."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(body)
        except Exception:
            detail = {"raw": body}
        raise SystemExit(
            f"\n{RED}  Error {e.code} from {url}{RESET}\n"
            f"{DIM}  {json.dumps(detail, indent=2)}{RESET}\n"
        )
    except urllib.error.URLError as e:
        raise SystemExit(
            f"\n{RED}  Connection failed: {e.reason}{RESET}\n"
            f"{DIM}  URL: {url}{RESET}\n"
        )


def http_get(url: str, headers: dict | None = None) -> dict:
    """GET a URL with optional headers, return parsed response."""
    req = urllib.request.Request(url, headers=headers or {}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {"_http_error": e.code, "_body": body}
    except urllib.error.URLError as e:
        raise SystemExit(
            f"\n{RED}  Connection failed: {e.reason}{RESET}\n"
            f"{DIM}  URL: {url}{RESET}\n"
        )


def detect_upstream_key() -> tuple[str, str] | None:
    """Auto-detect upstream provider from environment variables."""
    for env_var, kind, prefix_label in [
        ("OPENROUTER_API_KEY", "openrouter", "sk-or-"),
        ("ANTHROPIC_API_KEY", "anthropic", "sk-ant-"),
        ("FIREWORKS_API_KEY", "custom", ""),
        ("OPENAI_API_KEY", "openai", "sk-"),
    ]:
        key = os.environ.get(env_var)
        if key:
            return (kind, key)
    return None


def infer_kind_from_key(key: str) -> str:
    """Infer upstream kind from API key prefix."""
    if key.startswith("sk-or-"):
        return "openrouter"
    if key.startswith("sk-ant-"):
        return "anthropic"
    if key.startswith("sk-"):
        return "openai"  # legacy alias for direct OpenAI
    return "custom"  # default fallback for OpenAI-compatible providers


def canonical_upstream_kind(kind: str) -> str:
    """Normalize kind for API payloads while preserving legacy aliases."""
    kind = (kind or "").strip().lower()
    if kind == "openai":
        return "custom"
    return kind


def resolve_upstream_base_url(kind: str, explicit_base_url: str | None) -> str:
    """Resolve upstream base URL from explicit override or preset defaults."""
    base = (explicit_base_url or "").strip()
    if base:
        return base
    kind = (kind or "").strip().lower()
    if kind == "openai":
        return LEGACY_OPENAI_BASE_URL
    return UPSTREAM_DEFAULT_BASE_URLS.get(kind, UPSTREAM_DEFAULT_BASE_URLS["custom"])


# ── Subcommands ──────────────────────────────────────────────────────────────


def resolve_openclaw_config_path(arg_path: str | None) -> str:
    raw = (arg_path or os.environ.get("OPENCLAW_CONFIG_PATH") or DEFAULT_OPENCLAW_CONFIG_PATH).strip()
    return str(Path(raw).expanduser().resolve())


def have_openclaw_cli() -> bool:
    return shutil.which("openclaw") is not None


def run_openclaw(args: list[str], config_path: str, timeout_s: int = 20) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["OPENCLAW_CONFIG_PATH"] = config_path
    return subprocess.run(
        ["openclaw"] + args,
        text=True,
        capture_output=True,
        env=env,
        timeout=timeout_s,
        check=False,
    )


def maybe_backup_file(path: str) -> None:
    p = Path(path)
    if not p.exists():
        return
    backup = p.with_suffix(p.suffix + ".cacheforge.bak")
    try:
        # Only create once; preserve first-known-good.
        if not backup.exists():
            backup.write_bytes(p.read_bytes())
    except Exception:
        # Non-fatal; continue.
        return


def looks_like_cacheforge_key(key: str) -> bool:
    k = (key or "").strip()
    return k.startswith("cf_") or k.startswith("cfk_")


def fetch_openrouter_available_model_ids(base_url: str, api_key: str) -> set[str]:
    """Best-effort fetch of available model ids via OpenAI-compatible /v1/models."""
    if not api_key:
        return set()
    resp = http_get(f"{base_url}/v1/models", headers={"Authorization": f"Bearer {api_key}"})
    if resp.get("_http_error"):
        return set()
    data = resp.get("data")
    if not isinstance(data, list):
        return set()
    ids: set[str] = set()
    for item in data:
        if not isinstance(item, dict):
            continue
        model_id = str(item.get("id") or "").strip()
        if model_id:
            ids.add(model_id)
    return ids


def default_openclaw_models_for_upstream(kind: str, base_url: str, available_model_ids: set[str] | None = None) -> list[dict[str, str]]:
    kind = (kind or "").strip().lower()
    base_url = (base_url or "").strip().lower()

    if kind == "custom" and "fireworks.ai" in base_url:
        return [{"id": "accounts/fireworks/models/kimi-k2p5", "name": "Fireworks: Kimi K2.5"}]

    if kind == "openrouter":
        models = OPENROUTER_POPULAR_MODEL_CANDIDATES
        if available_model_ids:
            filtered = [(mid, mname) for mid, mname in models if mid in available_model_ids]
            if filtered:
                models = filtered
            else:
                # Fallback when discovery succeeded but no curated ids matched.
                models = OPENROUTER_POPULAR_MODEL_CANDIDATES[:2]
        if not models:
            models = OPENROUTER_POPULAR_MODEL_CANDIDATES[:2]
        return [{"id": mid, "name": mname} for mid, mname in models]

    if kind == "anthropic":
        return [{"id": "claude-opus-4-6-latest", "name": "Claude Opus 4.6"}]

    return [{"id": "gpt-5.2", "name": "GPT-5.2"}]


def default_openclaw_model_for_upstream(kind: str, base_url: str, available_model_ids: set[str] | None = None) -> tuple[str, str]:
    models = default_openclaw_models_for_upstream(kind, base_url, available_model_ids)
    first = models[0]
    return (first["id"], first["name"])


def build_openclaw_snippet(base_url: str, models: list[dict[str, str]], primary_model_id: str) -> dict:
    # Matches the console OpenClaw snippet shape for consistent copy/paste.
    return {
        "models": {
            "mode": "merge",
            "providers": {
                "cacheforge": {
                    "baseUrl": f"{base_url}/v1",
                    "apiKey": "${CACHEFORGE_API_KEY}",
                    "api": "openai-completions",
                    "models": models,
                }
            },
        },
        "agents": {"defaults": {"model": {"primary": f"cacheforge/{primary_model_id}"}}},
    }


def cmd_openclaw_snippet(args: argparse.Namespace) -> None:
    """Print the OpenClaw config snippet (same structure as the CacheForge console)."""
    base_url = get_base_url(args.base_url)
    api_key = args.api_key or os.environ.get("CACHEFORGE_API_KEY") or ""
    if not api_key:
        oai_key = os.environ.get("OPENAI_API_KEY", "")
        if looks_like_cacheforge_key(oai_key):
            api_key = oai_key

    upstream_kind = ""
    upstream_base = ""
    available_openrouter_models: set[str] = set()
    if api_key:
        up = http_get(f"{base_url}/v1/account/upstream", headers={"Authorization": f"Bearer {api_key}"})
        if not up.get("_http_error") and up.get("configured") and isinstance(up.get("upstream"), dict):
            upstream_kind = str(up["upstream"].get("kind") or "")
            upstream_base = str(up["upstream"].get("baseUrl") or "")
            if upstream_kind.strip().lower() == "openrouter":
                available_openrouter_models = fetch_openrouter_available_model_ids(base_url, api_key)

    models = default_openclaw_models_for_upstream(upstream_kind, upstream_base, available_openrouter_models)
    if args.model_id:
        model_id = args.model_id.strip()
        model_name = args.model_name.strip() if args.model_name else args.model_id.strip()
        models = [{"id": model_id, "name": model_name}]
    elif args.model_name and models:
        models[0]["name"] = args.model_name.strip()

    snippet = build_openclaw_snippet(base_url, models, models[0]["id"])
    print(f"\n{CYAN}{BOLD}  OpenClaw snippet (paste into ~/.openclaw/openclaw.json){RESET}\n")
    print(json.dumps(snippet, indent=2))
    print(f"\n{CYAN}{BOLD}  Required env:{RESET}")
    print(f"  {GREEN}export CACHEFORGE_API_KEY=cf_...{RESET}")
    print(f"{DIM}  (We keep secrets out of openclaw.json by default.){RESET}\n")


def cmd_openclaw_apply(args: argparse.Namespace) -> None:
    """Apply CacheForge provider config into OpenClaw via `openclaw config set` (JSON5-safe)."""
    base_url = get_base_url(args.base_url)
    config_path = resolve_openclaw_config_path(args.openclaw_config_path)
    api_key = args.api_key or os.environ.get("CACHEFORGE_API_KEY") or ""
    if not api_key:
        oai_key = os.environ.get("OPENAI_API_KEY", "")
        if looks_like_cacheforge_key(oai_key):
            api_key = oai_key
    if not api_key:
        raise SystemExit(
            f"\n{RED}  Missing CacheForge API key.{RESET}\n"
            f"{DIM}  Set CACHEFORGE_API_KEY (cf_...) or pass --api-key.{RESET}\n"
        )

    if not have_openclaw_cli():
        raise SystemExit(
            f"\n{RED}  OpenClaw CLI not found in PATH.{RESET}\n"
            f"{DIM}  Install OpenClaw and re-run, or use openclaw-snippet for manual paste.{RESET}\n"
        )

    # Resolve upstream kind to pick a sane default model like the console.
    upstream_kind = ""
    upstream_base = ""
    available_openrouter_models: set[str] = set()
    up = http_get(f"{base_url}/v1/account/upstream", headers={"Authorization": f"Bearer {api_key}"})
    if not up.get("_http_error") and up.get("configured") and isinstance(up.get("upstream"), dict):
        upstream_kind = str(up["upstream"].get("kind") or "")
        upstream_base = str(up["upstream"].get("baseUrl") or "")
        if upstream_kind.strip().lower() == "openrouter":
            available_openrouter_models = fetch_openrouter_available_model_ids(base_url, api_key)

    models = default_openclaw_models_for_upstream(upstream_kind, upstream_base, available_openrouter_models)
    if args.model_id:
        model_id = args.model_id.strip()
        model_name = args.model_name.strip() if args.model_name else args.model_id.strip()
        models = [{"id": model_id, "name": model_name}]
    elif args.model_name and models:
        models[0]["name"] = args.model_name.strip()
    model_id = models[0]["id"]

    provider_obj = {
        "baseUrl": f"{base_url}/v1",
        "apiKey": "${CACHEFORGE_API_KEY}",
        "api": "openai-completions",
        "models": models,
    }

    print(f"\n{CYAN}{BOLD}  About to update OpenClaw config:{RESET}")
    print(f"{DIM}  Config:{RESET} {config_path}")
    print(f"{DIM}  Add provider:{RESET} models.providers.cacheforge")
    if args.set_default:
        print(f"{DIM}  Set default model:{RESET} agents.defaults.model.primary = cacheforge/{model_id}")
    else:
        print(f"{DIM}  Default model:{RESET} (unchanged)")
    print()

    if not args.yes:
        resp = input(f"{YELLOW}{BOLD}  Apply changes? (y/n): {RESET}").strip().lower()
        if resp not in ("y", "yes"):
            print(f"\n{YELLOW}  Skipped. Use openclaw-snippet for manual paste.{RESET}\n")
            return

    maybe_backup_file(config_path)

    steps: list[tuple[str, list[str]]] = [
        ("set models.mode", ["config", "set", "models.mode", "merge"]),
        ("set models.providers.cacheforge", ["config", "set", "models.providers.cacheforge", json.dumps(provider_obj), "--json"]),
    ]
    if args.set_default:
        steps.append(("set agents.defaults.model.primary", ["config", "set", "agents.defaults.model.primary", f"cacheforge/{model_id}"]))

    for label, cmd in steps:
        cp = run_openclaw(cmd, config_path=config_path, timeout_s=30)
        if cp.returncode != 0:
            raise SystemExit(
                f"\n{RED}  Failed to {label}.{RESET}\n"
                f"{DIM}  stdout:{RESET}\n{cp.stdout}\n"
                f"{DIM}  stderr:{RESET}\n{cp.stderr}\n"
            )

    print(f"\n{GREEN}{BOLD}  OpenClaw config updated.{RESET}")
    print(f"{CYAN}  Next:{RESET} set your key and try an agent run:\n")
    print(f"  {GREEN}export CACHEFORGE_API_KEY={api_key}{RESET}")
    print(f"  {GREEN}openclaw agent --message \"hi\" --model cacheforge/{model_id}{RESET}\n")


def cmd_openclaw_validate(args: argparse.Namespace) -> None:
    """Validate OpenClaw config contains the CacheForge provider (optionally run a test agent message)."""
    config_path = resolve_openclaw_config_path(args.openclaw_config_path)
    if not have_openclaw_cli():
        raise SystemExit(f"\n{RED}  OpenClaw CLI not found in PATH.{RESET}\n")

    cp = run_openclaw(["config", "get", "models.providers.cacheforge"], config_path=config_path, timeout_s=15)
    if cp.returncode != 0 or not cp.stdout.strip():
        raise SystemExit(
            f"\n{RED}  CacheForge provider not found in OpenClaw config.{RESET}\n"
            f"{DIM}  Run: setup.py openclaw-apply{RESET}\n"
        )

    print(f"\n{GREEN}{BOLD}  OpenClaw is configured with CacheForge.{RESET}\n")
    if args.run_agent_test:
        model_id = args.model_id.strip() if args.model_id else ""
        if not model_id:
            model_id = "gpt-5.2"
        msg = args.message or "CacheForge OpenClaw validation: reply with OK."
        cp2 = run_openclaw(["agent", "--message", msg, "--model", f"cacheforge/{model_id}", "--thinking", "low"], config_path=config_path, timeout_s=120)
        if cp2.returncode != 0:
            raise SystemExit(
                f"\n{RED}  OpenClaw agent test failed.{RESET}\n"
                f"{DIM}  stdout:{RESET}\n{cp2.stdout}\n"
                f"{DIM}  stderr:{RESET}\n{cp2.stderr}\n"
            )
        print(cp2.stdout.strip() + "\n")


def cmd_provision(args: argparse.Namespace) -> None:
    """Register or authenticate and provision a CacheForge API key."""
    base_url = get_base_url(args.base_url)

    # Check if already provisioned
    existing_key = os.environ.get("CACHEFORGE_API_KEY")
    if existing_key and not args.email:
        print(f"\n{YELLOW}  CACHEFORGE_API_KEY is already set in your environment.{RESET}")
        print(f"{DIM}  Use 'validate' to check it, or pass --email to re-provision.{RESET}\n")
        return

    # Resolve email and password
    email = args.email
    password = args.password

    if not email:
        print(f"\n{RED}  --email is required for provisioning.{RESET}")
        print(f"{DIM}  Usage: setup.py provision --email you@example.com --password '...'{RESET}\n")
        raise SystemExit(1)

    if not password:
        print(f"\n{RED}  --password is required for provisioning.{RESET}")
        raise SystemExit(1)

    invite_code = (args.invite_code or os.environ.get("CACHEFORGE_INVITE_CODE") or "").strip()

    # Resolve upstream
    upstream_kind = (args.upstream_kind or "").strip().lower()
    upstream_key = args.upstream_key
    upstream_base_url = args.upstream_base_url or os.environ.get("UPSTREAM_BASE_URL")

    if not upstream_key:
        detected = detect_upstream_key()
        if detected:
            auto_kind, auto_key = detected
            upstream_kind = upstream_kind or auto_kind
            upstream_key = auto_key
            masked = auto_key[:8] + "..." + auto_key[-4:]
            print(f"\n{CYAN}  Auto-detected upstream:{RESET} {GREEN}{auto_kind}{RESET} ({DIM}{masked}{RESET})")
        else:
            print(f"\n{RED}  No upstream API key found.{RESET}")
            print(f"{DIM}  Pass --upstream-key or set OPENAI_API_KEY / OPENROUTER_API_KEY / ANTHROPIC_API_KEY / FIREWORKS_API_KEY{RESET}\n")
            raise SystemExit(1)

    if not upstream_kind:
        upstream_kind = infer_kind_from_key(upstream_key)
        print(f"{CYAN}  Inferred upstream kind:{RESET} {GREEN}{upstream_kind}{RESET}")

    if upstream_kind not in {"openrouter", "anthropic", "custom", "openai"}:
        raise SystemExit(
            f"\n{RED}  Invalid --upstream-kind: {upstream_kind}{RESET}\n"
            f"{DIM}  Use: openrouter | anthropic | custom (legacy alias: openai){RESET}\n"
        )

    if upstream_kind == "openai":
        print(f"{YELLOW}  Using legacy upstream kind 'openai' alias; sending as 'custom' with OpenAI base URL.{RESET}")
    canonical_kind = canonical_upstream_kind(upstream_kind)
    upstream_base_url = resolve_upstream_base_url(upstream_kind, upstream_base_url)

    # Call provision endpoint
    provision_url = f"{base_url}/api/provision"
    payload = {
        "email": email,
        "password": password,
        "upstream": {
            "kind": canonical_kind,
            "baseUrl": upstream_base_url,
            "apiKey": upstream_key,
        },
    }
    if invite_code:
        payload["inviteCode"] = invite_code

    print(f"\n{CYAN}{BOLD}  Provisioning CacheForge account...{RESET}")
    print(f"{DIM}  POST {provision_url}{RESET}\n")

    result = http_post(provision_url, payload)

    # Verification-required flow: provisioning succeeded but key is not returned.
    if result.get("requiresVerification"):
        print(f"\n{YELLOW}{BOLD}  Email verification required.{RESET}")
        print(f"{DIM}  {result.get('message', 'Check your email to verify your account.')}{RESET}")
        if result.get("verificationUrl"):
            print(f"\n{CYAN}{BOLD}  Verification URL:{RESET}")
            print(f"  {result.get('verificationUrl')}\n")
        print(f"{DIM}  After verifying, rerun provision to mint an API key.{RESET}\n")
        return

    api_key = result.get("apiKey") or result.get("api_key") or result.get("key")
    tenant_id = result.get("tenantId") or result.get("tenant_id") or result.get("id", "")

    if not api_key:
        print(f"{RED}  Unexpected response — no API key returned.{RESET}")
        print(f"{DIM}  {json.dumps(result, indent=2)}{RESET}")
        raise SystemExit(1)

    # Success output
    print(draw_box(
        "CacheForge Ready",
        [
            ("API Key", api_key),
            ("Base URL", f"{base_url}/v1"),
            ("Tenant", str(tenant_id)),
            ("Upstream", canonical_kind),
            ("Upstream Base", upstream_base_url),
        ],
        color=CYAN,
    ))

    print(f"\n{CYAN}{BOLD}  Next steps:{RESET}")
    print(f"{DIM}  Add these to your environment:{RESET}\n")
    print(f"  {GREEN}export OPENAI_BASE_URL={base_url}/v1{RESET}")
    print(f"  {GREEN}export OPENAI_API_KEY={api_key}{RESET}")
    print()
    print(f"{CYAN}{BOLD}  Billing:{RESET}")
    print(f"{DIM}  Before first proxy traffic, add credits (minimum top-up is typically $10).{RESET}")
    print(f"  {GREEN}python skills/cacheforge-ops/ops.py topup --amount 10 --method stripe{RESET}")
    print(f"  {GREEN}python skills/cacheforge-ops/ops.py topup --amount 10 --method crypto{RESET}")
    print()


def cmd_validate(args: argparse.Namespace) -> None:
    """Validate an existing CacheForge setup by hitting the account info endpoint."""
    base_url = get_base_url(args.base_url)

    api_key = args.api_key or os.environ.get("CACHEFORGE_API_KEY")
    if not api_key:
        # Also check OPENAI_API_KEY if it looks like a CacheForge key
        oai_key = os.environ.get("OPENAI_API_KEY", "")
        if looks_like_cacheforge_key(oai_key):
            api_key = oai_key

    if not api_key:
        print(f"\n{RED}  No API key found.{RESET}")
        print(f"{DIM}  Pass --api-key or set CACHEFORGE_API_KEY / OPENAI_API_KEY (cf_...){RESET}\n")
        raise SystemExit(1)

    info_url = f"{base_url}/v1/account/info"
    masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else api_key

    print(f"\n{CYAN}{BOLD}  Validating CacheForge connection...{RESET}")
    print(f"{DIM}  GET {info_url}{RESET}")
    print(f"{DIM}  Key: {masked_key}{RESET}\n")

    result = http_get(info_url, headers={"Authorization": f"Bearer {api_key}"})

    # Handle HTTP errors
    http_error = result.get("_http_error")
    if http_error:
        body = result.get("_body", "")
        if http_error == 401:
            print(f"{RED}  Authentication failed (401).{RESET}")
            print(f"{YELLOW}  Your API key is invalid or expired.{RESET}")
            print(f"{DIM}  Run 'provision' to get a new key, or check CACHEFORGE_API_KEY.{RESET}\n")
            raise SystemExit(1)
        elif http_error == 402:
            print(f"{YELLOW}  Payment required (402).{RESET}")
            print(f"{YELLOW}  Your account is active but has no credits remaining.{RESET}")
            print(f"{DIM}  Visit {base_url} to add credits or upgrade your plan.{RESET}\n")
            raise SystemExit(1)
        else:
            print(f"{RED}  Unexpected error ({http_error}).{RESET}")
            print(f"{DIM}  {body[:500]}{RESET}\n")
            raise SystemExit(1)

    # Success — display account info
    # API returns {"tenant": {"id": "...", "name": "...", "status": "...", ...}}
    tenant_data = result.get("tenant", {})
    if isinstance(tenant_data, dict):
        tenant_name = tenant_data.get("name", "unknown")
        status = tenant_data.get("status", "active")
        upstream_ok = tenant_data.get("upstreamConfigured", False)
    else:
        tenant_name = str(tenant_data) if tenant_data else "unknown"
        status = "active"
        upstream_ok = False

    info_lines = [("Status", f"{status}")]
    if tenant_name:
        info_lines.insert(0, ("Tenant", tenant_name))
    if upstream_ok:
        info_lines.append(("Upstream", "configured"))
    info_lines.append(("Endpoint", f"{base_url}/v1"))

    print(draw_box("Connection OK", info_lines, color=CYAN))
    print(f"\n{GREEN}  CacheForge is working. All requests will be proxied and optimized.{RESET}\n")


# ── CLI entrypoint ───────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CacheForge setup CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python setup.py provision --email me@co.com --password s3cret --upstream-key sk-or-...\n"
            "  python setup.py validate --api-key cf_abc123\n"
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ── provision ──
    prov = sub.add_parser("provision", help="Register/authenticate and get a CacheForge API key")
    prov.add_argument("--email", help="Account email address")
    prov.add_argument("--password", help="Account password")
    prov.add_argument("--invite-code", help="Invite code (required on invite-only deployments)")
    prov.add_argument(
        "--upstream-kind",
        help="Upstream preset: openrouter | anthropic | custom (OpenAI-compatible). Legacy alias: openai",
    )
    prov.add_argument("--upstream-key", help="Upstream provider API key")
    prov.add_argument(
        "--upstream-base-url",
        help="Optional upstream base URL override (for custom OpenAI-compatible providers)",
    )
    prov.add_argument("--base-url", help=f"CacheForge base URL (default: {DEFAULT_BASE_URL})")

    # ── validate ──
    val = sub.add_parser("validate", help="Validate an existing CacheForge setup")
    val.add_argument("--api-key", help="CacheForge API key (cf_...)")
    val.add_argument("--base-url", help=f"CacheForge base URL (default: {DEFAULT_BASE_URL})")

    # ── openclaw-snippet ──
    sn = sub.add_parser("openclaw-snippet", help="Print the OpenClaw config snippet for CacheForge")
    sn.add_argument("--api-key", help="CacheForge API key (cf_...)")
    sn.add_argument("--base-url", help=f"CacheForge base URL (default: {DEFAULT_BASE_URL})")
    sn.add_argument("--model-id", help="Override the default example model id")
    sn.add_argument("--model-name", help="Override the default example model name")

    # ── openclaw-apply ──
    ap = sub.add_parser("openclaw-apply", help="Apply CacheForge provider config into OpenClaw via `openclaw config set`")
    ap.add_argument("--api-key", help="CacheForge API key (cf_...)")
    ap.add_argument("--base-url", help=f"CacheForge base URL (default: {DEFAULT_BASE_URL})")
    ap.add_argument("--openclaw-config-path", help=f"OpenClaw config path (default: {DEFAULT_OPENCLAW_CONFIG_PATH})")
    ap.add_argument("--model-id", help="Override the default example model id")
    ap.add_argument("--model-name", help="Override the default example model name")
    ap.add_argument("--set-default", action="store_true", help="Set agents.defaults.model.primary to CacheForge (recommended)")
    ap.add_argument("--yes", action="store_true", help="Do not prompt for confirmation")

    # ── openclaw-validate ──
    ov = sub.add_parser("openclaw-validate", help="Validate OpenClaw is configured with CacheForge (optional agent run)")
    ov.add_argument("--openclaw-config-path", help=f"OpenClaw config path (default: {DEFAULT_OPENCLAW_CONFIG_PATH})")
    ov.add_argument("--run-agent-test", action="store_true", help="Run a short `openclaw agent` test message")
    ov.add_argument("--model-id", help="Model id to test (default: gpt-5.2)")
    ov.add_argument("--message", help="Message to send when running agent test")

    args = parser.parse_args()

    if args.command == "provision":
        cmd_provision(args)
    elif args.command == "validate":
        cmd_validate(args)
    elif args.command == "openclaw-snippet":
        cmd_openclaw_snippet(args)
    elif args.command == "openclaw-apply":
        cmd_openclaw_apply(args)
    elif args.command == "openclaw-validate":
        cmd_openclaw_validate(args)


if __name__ == "__main__":
    main()
