#!/usr/bin/env python3
"""Model Switchboard v2 backend for OpenClaw (stdlib-only)."""

import copy
import http.server
import json
import os
import re
import shutil
import time
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PORT = int(os.environ.get("SWITCHBOARD_PORT", "8770"))
ENV_FILE = Path(os.environ.get("SWITCHBOARD_ENV", os.path.expanduser("~/.openclaw/workspace/.env")))
CONFIG_FILE = Path(os.path.expanduser("~/.openclaw/openclaw.json"))
BACKUP_DIR = Path(os.path.expanduser("~/.openclaw/backups/switchboard"))
UI_DIR = Path(__file__).resolve().parent


def _resolve_registry_file() -> Path:
    candidates = [
        Path(os.environ.get("SWITCHBOARD_REGISTRY", "")).expanduser() if os.environ.get("SWITCHBOARD_REGISTRY") else None,
        UI_DIR / "model-registry.json",
        UI_DIR.parent / "model-registry.json",
    ]
    for c in candidates:
        if c and c.exists():
            return c
    return UI_DIR / "model-registry.json"


REGISTRY_FILE = _resolve_registry_file()

MODEL_RE = re.compile(r"^[a-z][a-z0-9_-]*/[a-z0-9._:/-]+$")
ENV_KEY_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
DM_POLICY = {"pairing", "allowlist", "open", "disabled"}

COST_ORDER = {
    "free": 0,
    "very-low": 1,
    "low": 2,
    "medium": 3,
    "high": 4,
    "subscription": 5,
    "proxy": 3,
    "variable": 3,
}

ROLE_SPECS: Dict[str, Dict[str, Any]] = {
    "primary": {
        "path": ["agents", "defaults", "model", "primary"],
        "capabilities": ["llm", "tools"],
        "safe_role": "primary",
        "label": "Primary LLM",
    },
    "llm_fallbacks": {
        "path": ["agents", "defaults", "model", "fallbacks"],
        "is_list": True,
        "capabilities": ["llm", "tools"],
        "safe_role": "fallback",
        "label": "LLM Fallbacks",
    },
    "image_model": {
        "path": ["agents", "defaults", "imageModel", "primary"],
        "capabilities": ["vision"],
        "safe_role": "image",
        "label": "Image Model",
    },
    "image_fallbacks": {
        "path": ["agents", "defaults", "imageModel", "fallbacks"],
        "is_list": True,
        "capabilities": ["vision"],
        "safe_role": "image",
        "label": "Image Fallbacks",
    },
    "research": {
        "path": ["switchboard", "roles", "research"],
        "capabilities": ["llm", "reasoning"],
        "label": "Research",
    },
    "coding_pass1": {
        "path": ["switchboard", "roles", "coding_pass1"],
        "capabilities": ["llm", "code"],
        "safe_role": "coding",
        "label": "Coding Pass 1",
    },
    "coding_pass2": {
        "path": ["switchboard", "roles", "coding_pass2"],
        "capabilities": ["llm", "code"],
        "safe_role": "coding",
        "label": "Coding Pass 2",
    },
    "coding_pass3": {
        "path": ["switchboard", "roles", "coding_pass3"],
        "capabilities": ["llm", "code"],
        "safe_role": "coding",
        "label": "Coding Pass 3",
    },
    "social_media": {
        "path": ["switchboard", "roles", "social_media"],
        "capabilities": ["llm"],
        "label": "Social Media",
    },
    "web_ops": {
        "path": ["switchboard", "roles", "web_ops"],
        "capabilities_any": [["tools"], ["search"]],
        "capabilities": ["llm"],
        "label": "Web Ops",
    },
    "heartbeat": {
        "path": ["switchboard", "roles", "heartbeat"],
        "capabilities": ["llm"],
        "safe_role": "heartbeat",
        "label": "Heartbeat",
    },
}

SWITCHBOARD_ROLES = [
    "research",
    "coding_pass1",
    "coding_pass2",
    "coding_pass3",
    "social_media",
    "web_ops",
    "heartbeat",
]


def read_env() -> Dict[str, str]:
    values: Dict[str, str] = {}
    if not ENV_FILE.exists():
        return values
    for raw in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key:
            values[key] = value.strip().strip('"').strip("'")
    return values


def write_env_key(key: str, value: str) -> None:
    ENV_FILE.parent.mkdir(parents=True, exist_ok=True)
    lines = ENV_FILE.read_text(encoding="utf-8").splitlines() if ENV_FILE.exists() else []
    pat = re.compile(rf"^{re.escape(key)}\s*=")
    out: List[str] = []
    replaced = False
    for line in lines:
        if pat.match(line.strip()):
            out.append(f'{key}="{value}"')
            replaced = True
        else:
            out.append(line)
    if not replaced:
        out.append(f'{key}="{value}"')
    ENV_FILE.write_text("\n".join(out) + "\n", encoding="utf-8")
    os.chmod(str(ENV_FILE), 0o600)


def delete_env_key(key: str) -> bool:
    if not ENV_FILE.exists():
        return False
    lines = ENV_FILE.read_text(encoding="utf-8").splitlines()
    pat = re.compile(rf"^{re.escape(key)}\s*=")
    out = [line for line in lines if not pat.match(line.strip())]
    if len(out) == len(lines):
        return False
    ENV_FILE.write_text("\n".join(out) + "\n", encoding="utf-8")
    os.chmod(str(ENV_FILE), 0o600)
    return True


def read_registry() -> Dict[str, Any]:
    try:
        return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"version": "?", "models": {}, "providers": {}}


def read_config() -> Dict[str, Any]:
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def validate_model_ref(ref: Any) -> bool:
    return isinstance(ref, str) and bool(MODEL_RE.match(ref)) and len(ref) < 220


def provider_of(ref: str) -> str:
    return ref.split("/", 1)[0] if "/" in ref else ""


def _provider_authenticated(pid: str, pinfo: Dict[str, Any], env: Dict[str, str]) -> bool:
    auth_method = pinfo.get("authMethod", "api-key")
    auth_env = pinfo.get("authEnv", [])
    if auth_method in {"oauth", "oauth-plugin", "local", "gcloud-adc"} and not auth_env:
        return True
    return any(bool(env.get(k)) for k in auth_env)


def registry_model_ok(
    ref: str,
    registry: Dict[str, Any],
    capabilities: Optional[List[str]] = None,
    capabilities_any: Optional[List[List[str]]] = None,
    safe_role: Optional[str] = None,
) -> Tuple[bool, Optional[str]]:
    if not validate_model_ref(ref):
        return False, "Model must use provider/model format"
    model = registry.get("models", {}).get(ref)
    if not model:
        return True, "Model not in registry; capability checks skipped"
    if model.get("blocked"):
        return False, model.get("blockReason", "Model is blocked")

    caps = set(model.get("capabilities", []))
    if capabilities:
        missing = [c for c in capabilities if c not in caps]
        if missing:
            return False, f"Model missing required capabilities: {', '.join(missing)}"
    if capabilities_any:
        if not any(all(c in caps for c in group) for group in capabilities_any):
            choices = ["+".join(g) for g in capabilities_any]
            return False, f"Model must support one of: {', '.join(choices)}"

    if safe_role:
        unsafe = model.get("unsafeRoles", [])
        if safe_role in unsafe:
            return False, f"Model is marked unsafe for role '{safe_role}'"

    return True, None


def _get_path(config: Dict[str, Any], path: List[str], default: Any = None) -> Any:
    cur: Any = config
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def _ensure_path(config: Dict[str, Any], path: List[str]) -> Dict[str, Any]:
    cur = config
    for key in path:
        nxt = cur.get(key)
        if not isinstance(nxt, dict):
            nxt = {}
            cur[key] = nxt
        cur = nxt
    return cur


def _set_path(config: Dict[str, Any], path: List[str], value: Any) -> None:
    parent = _ensure_path(config, path[:-1]) if len(path) > 1 else config
    parent[path[-1]] = value


def _normalize_channels(config: Dict[str, Any]) -> None:
    channels = config.setdefault("channels", {})
    if not isinstance(channels, dict):
        channels = {}
        config["channels"] = channels
    telegram = channels.setdefault("telegram", {})
    if not isinstance(telegram, dict):
        telegram = {}
        channels["telegram"] = telegram
    telegram.setdefault("enabled", False)
    telegram.setdefault("dmPolicy", "disabled")
    telegram.setdefault("allowFrom", [])
    telegram.setdefault("groups", {})
    if not isinstance(telegram.get("groups"), dict):
        telegram["groups"] = {}
    telegram["groups"].setdefault("requireMention", True)


def _validate_telegram(config: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    channels = config.get("channels", {})
    telegram = channels.get("telegram", {}) if isinstance(channels, dict) else {}
    if not isinstance(telegram, dict):
        return ["channels.telegram must be an object"]

    enabled = bool(telegram.get("enabled", False))
    dm_policy = telegram.get("dmPolicy", "disabled")
    allow_from = telegram.get("allowFrom", [])

    if dm_policy not in DM_POLICY:
        errors.append("channels.telegram.dmPolicy must be one of pairing/allowlist/open/disabled")

    if not isinstance(allow_from, list) or not all(isinstance(v, str) for v in allow_from):
        errors.append("channels.telegram.allowFrom must be an array of strings")

    if enabled:
        token = str(telegram.get("botToken", "")).strip()
        if not token:
            errors.append("channels.telegram.botToken must not be empty when telegram is enabled")

    groups = telegram.get("groups", {})
    if groups is not None and not isinstance(groups, dict):
        errors.append("channels.telegram.groups must be an object")
    elif isinstance(groups, dict) and "requireMention" in groups and not isinstance(groups.get("requireMention"), bool):
        errors.append("channels.telegram.groups.requireMention must be boolean")

    return errors


def _collect_referenced_models(config: Dict[str, Any]) -> List[str]:
    refs: List[str] = []
    primary = _get_path(config, ["agents", "defaults", "model", "primary"], "")
    if isinstance(primary, str) and primary:
        refs.append(primary)

    for key_path in [
        ["agents", "defaults", "model", "fallbacks"],
        ["agents", "defaults", "imageModel", "fallbacks"],
    ]:
        arr = _get_path(config, key_path, [])
        if isinstance(arr, list):
            refs.extend([v for v in arr if isinstance(v, str) and v])

    image_primary = _get_path(config, ["agents", "defaults", "imageModel", "primary"], "")
    if isinstance(image_primary, str) and image_primary:
        refs.append(image_primary)

    for role in SWITCHBOARD_ROLES:
        rv = _get_path(config, ["switchboard", "roles", role], "")
        if isinstance(rv, str) and rv:
            refs.append(rv)

    return refs


def validate_config(config: Dict[str, Any], registry: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    primary = _get_path(config, ["agents", "defaults", "model", "primary"], "")
    if not validate_model_ref(primary):
        errors.append("agents.defaults.model.primary must be provider/model format")

    for pth, label in [
        (["agents", "defaults", "model", "fallbacks"], "LLM fallbacks"),
        (["agents", "defaults", "imageModel", "fallbacks"], "Image fallbacks"),
    ]:
        arr = _get_path(config, pth, [])
        if arr is None:
            arr = []
        if not isinstance(arr, list):
            errors.append(f"{label} must be an array")
            continue
        invalid = [v for v in arr if not validate_model_ref(v)]
        if invalid:
            errors.append(f"{label} contains invalid model refs: {', '.join(invalid[:5])}")
        if len(arr) != len(set(arr)):
            errors.append(f"{label} contains duplicate entries")

    image_primary = _get_path(config, ["agents", "defaults", "imageModel", "primary"], "")
    if image_primary and not validate_model_ref(image_primary):
        errors.append("agents.defaults.imageModel.primary must be provider/model format")

    errors.extend(_validate_telegram(config))

    allow_models = _get_path(config, ["agents", "defaults", "models"], None)
    if allow_models is None:
        allow_models = {}
    if not isinstance(allow_models, dict):
        errors.append("agents.defaults.models must be an object")
        allow_models = {}

    refs = _collect_referenced_models(config)
    missing_allow = sorted({r for r in refs if r and r not in allow_models})
    if missing_allow:
        errors.append(
            "Allowlist missing referenced models: " + ", ".join(missing_allow[:10])
        )

    # Validate role model requirements when model is known.
    for role, spec in ROLE_SPECS.items():
        if spec.get("is_list"):
            continue
        ref = _get_path(config, spec["path"], "")
        if not ref:
            continue
        ok, msg = registry_model_ok(
            ref,
            registry,
            capabilities=spec.get("capabilities"),
            capabilities_any=spec.get("capabilities_any"),
            safe_role=spec.get("safe_role"),
        )
        if not ok:
            errors.append(f"{role}: {msg}")
        elif msg:
            warnings.append(f"{role}: {msg}")

    # Coding provider diversity.
    cp1 = _get_path(config, ["switchboard", "roles", "coding_pass1"], "")
    cp2 = _get_path(config, ["switchboard", "roles", "coding_pass2"], "")
    cp3 = _get_path(config, ["switchboard", "roles", "coding_pass3"], "")
    assigned = [m for m in [cp1, cp2, cp3] if isinstance(m, str) and m]
    if len(assigned) >= 2:
        providers = [provider_of(x) for x in assigned]
        if len(set(providers)) != len(providers):
            errors.append("coding_pass1/2/3 must use different providers")

    return len(errors) == 0, errors, warnings


def backup_config() -> str:
    if not CONFIG_FILE.exists():
        return ""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S") + f"-{int((time.time() % 1) * 1000):03d}"
    target = BACKUP_DIR / f"openclaw-{ts}.json"
    shutil.copy2(str(CONFIG_FILE), str(target))
    backups = sorted(BACKUP_DIR.glob("openclaw-*.json"))
    while len(backups) > 100:
        old = backups.pop(0)
        try:
            old.unlink()
        except Exception:
            pass
    return target.name


def list_backups(limit: int = 200) -> List[Dict[str, Any]]:
    if not BACKUP_DIR.exists():
        return []
    result = []
    files = sorted(BACKUP_DIR.glob("openclaw-*.json"), reverse=True)
    for f in files[:limit]:
        st = f.stat()
        result.append(
            {
                "filename": f.name,
                "path": str(f),
                "size": st.st_size,
                "modified": st.st_mtime,
                "modifiedIso": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(st.st_mtime)),
            }
        )
    return result


def _write_config_transaction(new_config: Dict[str, Any], registry: Dict[str, Any]) -> Tuple[bool, str, Optional[str], List[str]]:
    ok, errs, warnings = validate_config(new_config, registry)
    if not ok:
        return False, "; ".join(errs), None, warnings

    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    backup_name = backup_config()

    try:
        payload = json.dumps(new_config, indent=2, sort_keys=False) + "\n"
        CONFIG_FILE.write_text(payload, encoding="utf-8")

        # Health check after write: parse + validate again.
        parsed = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        ok2, errs2, _warnings2 = validate_config(parsed, registry)
        if not ok2:
            raise ValueError("Post-write validation failed: " + "; ".join(errs2))

        return True, "ok", backup_name, warnings
    except Exception as exc:
        # Automatic rollback.
        try:
            if backup_name:
                src = BACKUP_DIR / backup_name
                if src.exists():
                    shutil.copy2(str(src), str(CONFIG_FILE))
        except Exception:
            pass
        return False, f"Write failed and rollback attempted: {exc}", backup_name, warnings


def _mutate_config(mutator) -> Dict[str, Any]:
    registry = read_registry()
    current = read_config()
    if not isinstance(current, dict):
        return {"ok": False, "error": "Current config is not a JSON object"}

    candidate = copy.deepcopy(current)
    try:
        mutator(candidate)
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}

    ok, message, backup_name, warnings = _write_config_transaction(candidate, registry)
    if not ok:
        return {"ok": False, "error": message, "backup": backup_name, "warnings": warnings}
    return {"ok": True, "backup": backup_name, "warnings": warnings}


def _model_candidates(
    registry: Dict[str, Any],
    env: Dict[str, str],
    capabilities: Optional[List[str]] = None,
    capabilities_any: Optional[List[List[str]]] = None,
    safe_role: Optional[str] = None,
    exclude: Optional[set] = None,
    exclude_provider: Optional[str] = None,
) -> List[str]:
    exclude = exclude or set()
    providers = registry.get("providers", {})
    scored: List[Tuple[int, int, str]] = []

    for ref, model in registry.get("models", {}).items():
        if ref in exclude:
            continue
        if exclude_provider and provider_of(ref) == exclude_provider:
            continue
        ok, _msg = registry_model_ok(
            ref,
            registry,
            capabilities=capabilities,
            capabilities_any=capabilities_any,
            safe_role=safe_role,
        )
        if not ok:
            continue
        pid = provider_of(ref)
        pinfo = providers.get(pid, {})
        authed = _provider_authenticated(pid, pinfo, env)
        if not authed:
            continue
        tier = COST_ORDER.get(model.get("costTier", "medium"), 3)
        bonus = 0 if model.get("reasoning") else 1
        scored.append((tier, bonus, ref))

    scored.sort()
    return [ref for _, _, ref in scored]


def _ensure_allowlist_has(config: Dict[str, Any], refs: List[str]) -> None:
    models = _ensure_path(config, ["agents", "defaults", "models"])
    for ref in refs:
        if ref:
            models.setdefault(ref, {})


def _validate_input_model(data: Dict[str, Any], key: str = "model") -> str:
    ref = data.get(key)
    if not isinstance(ref, str) or not validate_model_ref(ref):
        raise ValueError(f"{key} must be provider/model")
    return ref


def _validate_role_assignment(role: str, model: str, config: Dict[str, Any], registry: Dict[str, Any]) -> Optional[str]:
    spec = ROLE_SPECS.get(role)
    if not spec:
        return "Unknown role"

    ok, msg = registry_model_ok(
        model,
        registry,
        capabilities=spec.get("capabilities"),
        capabilities_any=spec.get("capabilities_any"),
        safe_role=spec.get("safe_role"),
    )
    if not ok:
        return msg

    if role.startswith("coding_pass"):
        roles = {
            "coding_pass1": _get_path(config, ["switchboard", "roles", "coding_pass1"], ""),
            "coding_pass2": _get_path(config, ["switchboard", "roles", "coding_pass2"], ""),
            "coding_pass3": _get_path(config, ["switchboard", "roles", "coding_pass3"], ""),
        }
        roles[role] = model
        providers = [provider_of(v) for v in roles.values() if isinstance(v, str) and v]
        if len(providers) != len(set(providers)):
            return "Coding pass 1/2/3 must use different providers"

    return None


def detect_issues(status: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    roles = status.get("roles", {})
    providers = status.get("providers", {})

    if not status.get("fallbacks"):
        issues.append(
            {
                "id": "no_llm_fallbacks",
                "severity": "error",
                "title": "No LLM fallbacks configured",
                "description": "Primary LLM outages will cause hard failures.",
                "actions": [
                    {"type": "auto_fix", "label": "⚡ Auto-Fix", "issue": "no_llm_fallbacks"},
                    {"type": "choose", "label": "🎯 Choose", "target": "llm_fallbacks"},
                ],
            }
        )

    if not status.get("imageFallbacks"):
        issues.append(
            {
                "id": "no_image_fallbacks",
                "severity": "warning",
                "title": "No image fallbacks configured",
                "description": "Vision workflows can fail when the image model is unavailable.",
                "actions": [
                    {"type": "auto_fix", "label": "⚡ Auto-Fix", "issue": "no_image_fallbacks"},
                    {"type": "choose", "label": "🎯 Choose", "target": "image_fallbacks"},
                ],
            }
        )

    for role in SWITCHBOARD_ROLES:
        if not roles.get(role):
            issues.append(
                {
                    "id": f"missing_role:{role}",
                    "severity": "warning",
                    "title": f"Missing role assignment: {ROLE_SPECS[role]['label']}",
                    "description": "Role has no model set and may fail when invoked.",
                    "actions": [{"type": "choose", "label": "Pick Model", "target": role}],
                }
            )

    cp = [roles.get("coding_pass1"), roles.get("coding_pass2"), roles.get("coding_pass3")]
    cp_filled = [x for x in cp if x]
    if len(cp_filled) >= 2:
        p = [provider_of(x) for x in cp_filled]
        if len(set(p)) != len(p):
            issues.append(
                {
                    "id": "coding_provider_collision",
                    "severity": "error",
                    "title": "Coding pipeline uses same provider in multiple passes",
                    "description": "Pass1/Pass2/Pass3 must use different providers.",
                    "actions": [{"type": "auto_fix", "label": "🔀 Swap", "issue": "coding_provider_collision"}],
                }
            )

    unauth = sorted([pid for pid, p in providers.items() if not p.get("hasAuth") and p.get("requiresAuth")])
    if unauth:
        needed = []
        referenced = [
            status.get("primary"),
            status.get("imageModel"),
            *status.get("fallbacks", []),
            *status.get("imageFallbacks", []),
            *[roles.get(r) for r in SWITCHBOARD_ROLES],
        ]
        for ref in referenced:
            if ref and provider_of(ref) in unauth:
                needed.append(provider_of(ref))
        for pid in sorted(set(needed)):
            issues.append(
                {
                    "id": f"unconfigured_provider:{pid}",
                    "severity": "error",
                    "title": f"Provider not authenticated: {pid}",
                    "description": "A referenced model depends on provider auth that is not configured.",
                    "actions": [{"type": "provider_key", "label": "🔑 Add API Key", "provider": pid}],
                }
            )

    auth_count = len([1 for _pid, p in providers.items() if p.get("hasAuth")])
    if auth_count < 3:
        issues.append(
            {
                "id": "few_authenticated_providers",
                "severity": "info" if auth_count >= 2 else "warning",
                "title": f"Only {auth_count} providers authenticated",
                "description": "More authenticated providers improves resilience and fallback coverage.",
                "actions": [{"type": "scroll", "label": "🔑 Configure Providers", "target": "providers"}],
            }
        )

    allowlist = status.get("allowlist", [])
    if isinstance(allowlist, list) and 0 < len(allowlist) < 8:
        issues.append(
            {
                "id": "small_allowlist",
                "severity": "warning",
                "title": "Model allowlist is small",
                "description": "A narrow allowlist can block fallback and role assignments.",
                "actions": [{"type": "auto_fix", "label": "⚡ Add All Auth'd", "issue": "small_allowlist"}],
            }
        )

    tg = status.get("channels", {}).get("telegram", {})
    if not tg.get("enabled"):
        issues.append(
            {
                "id": "channel_not_configured:telegram",
                "severity": "info",
                "title": "Telegram channel not configured",
                "description": "Enable and configure Telegram channel settings.",
                "actions": [{"type": "channel", "label": "⚙️ Setup", "channel": "telegram"}],
            }
        )
    else:
        if not tg.get("botTokenConfigured"):
            issues.append(
                {
                    "id": "missing_bot_token",
                    "severity": "error",
                    "title": "Telegram bot token missing",
                    "description": "Telegram is enabled but no bot token is configured.",
                    "actions": [{"type": "channel", "label": "🔑 Add Token", "channel": "telegram"}],
                }
            )
        if tg.get("dmPolicy") == "allowlist" and not tg.get("allowFrom"):
            issues.append(
                {
                    "id": "telegram_empty_allowfrom",
                    "severity": "warning",
                    "title": "Telegram allowFrom is empty",
                    "description": "Allowlist policy requires at least one permitted user ID.",
                    "actions": [{"type": "channel", "label": "👤 Add User ID", "channel": "telegram"}],
                }
            )

    return issues


def build_status() -> Dict[str, Any]:
    registry = read_registry()
    config = read_config()
    env = read_env()

    _normalize_channels(config)

    providers_status: Dict[str, Any] = {}
    providers = registry.get("providers", {})
    for pid, pinfo in providers.items():
        auth_method = pinfo.get("authMethod", "api-key")
        auth_env = pinfo.get("authEnv", [])
        has_auth = _provider_authenticated(pid, pinfo, env)
        providers_status[pid] = {
            "id": pid,
            "displayName": pinfo.get("displayName", pid),
            "type": pinfo.get("type", "external"),
            "authMethod": auth_method,
            "authEnvVars": auth_env,
            "hasAuth": has_auth,
            "requiresAuth": auth_method not in {"local"},
            "website": pinfo.get("website", ""),
            "note": pinfo.get("note", ""),
        }

    primary = _get_path(config, ["agents", "defaults", "model", "primary"], "")
    fallbacks = _get_path(config, ["agents", "defaults", "model", "fallbacks"], [])
    if not isinstance(fallbacks, list):
        fallbacks = []
    image_primary = _get_path(config, ["agents", "defaults", "imageModel", "primary"], "")
    image_fallbacks = _get_path(config, ["agents", "defaults", "imageModel", "fallbacks"], [])
    if not isinstance(image_fallbacks, list):
        image_fallbacks = []

    roles = {r: _get_path(config, ["switchboard", "roles", r], "") for r in SWITCHBOARD_ROLES}

    allow_obj = _get_path(config, ["agents", "defaults", "models"], {})
    allowlist = list(allow_obj.keys()) if isinstance(allow_obj, dict) else []

    tg = _get_path(config, ["channels", "telegram"], {})
    if not isinstance(tg, dict):
        tg = {}
    tg_token = str(tg.get("botToken", "")).strip()
    token_configured = bool(tg_token and tg_token != "${TELEGRAM_BOT_TOKEN}") or bool(env.get("TELEGRAM_BOT_TOKEN"))

    status = {
        "primary": primary,
        "fallbacks": fallbacks,
        "imageModel": image_primary,
        "imageFallbacks": image_fallbacks,
        "roles": roles,
        "providers": providers_status,
        "models": registry.get("models", {}),
        "allowlist": allowlist,
        "channels": {
            "telegram": {
                "enabled": bool(tg.get("enabled", False)),
                "dmPolicy": tg.get("dmPolicy", "disabled"),
                "allowFrom": tg.get("allowFrom", []) if isinstance(tg.get("allowFrom"), list) else [],
                "groups": tg.get("groups", {}) if isinstance(tg.get("groups"), dict) else {"requireMention": True},
                "botTokenRef": tg.get("botToken", ""),
                "botTokenConfigured": token_configured,
            }
        },
        "registryVersion": registry.get("version", "?"),
        "registryUpdated": registry.get("lastUpdated", ""),
        "providerCount": len(providers_status),
        "modelCount": len(registry.get("models", {})),
        "backupCount": len(list_backups()),
        "backups": list_backups(20),
    }
    status["issues"] = detect_issues(status)
    return status


def health_check() -> Dict[str, Any]:
    registry = read_registry()
    try:
        raw = CONFIG_FILE.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {
            "ok": False,
            "error": f"Config file not found: {CONFIG_FILE}",
            "configPath": str(CONFIG_FILE),
            "registryPath": str(REGISTRY_FILE),
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": f"Unable to read config: {exc}",
            "configPath": str(CONFIG_FILE),
            "registryPath": str(REGISTRY_FILE),
        }

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        return {
            "ok": False,
            "error": f"Invalid JSON: {exc}",
            "configPath": str(CONFIG_FILE),
            "registryPath": str(REGISTRY_FILE),
        }

    ok, errors, warnings = validate_config(parsed, registry)
    return {
        "ok": ok,
        "errors": errors,
        "warnings": warnings,
        "configPath": str(CONFIG_FILE),
        "registryPath": str(REGISTRY_FILE),
    }


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI_DIR), **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/status":
            self._json(build_status())
            return
        if path == "/api/registry":
            self._json(read_registry())
            return
        if path == "/api/backups":
            self._json({"backups": list_backups(200), "count": len(list_backups())})
            return
        if path == "/api/health":
            health = health_check()
            self._json(health, 200 if health.get("ok") else 500)
            return

        if path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        payload = self._read_json_body()
        if payload is None:
            return

        routes = {
            "/api/key": self._route_save_key,
            "/api/key/delete": self._route_delete_key,
            "/api/config/set-role": self._route_set_role,
            "/api/config/add-fallback": self._route_add_fallback,
            "/api/config/add-image-fallback": self._route_add_image_fallback,
            "/api/config/remove-fallback": self._route_remove_fallback,
            "/api/config/add-allowlist": self._route_add_allowlist,
            "/api/config/remove-allowlist": self._route_remove_allowlist,
            "/api/config/set-primary": self._route_set_primary,
            "/api/config/set-image-model": self._route_set_image,
            "/api/config/auto-fix": self._route_auto_fix,
            "/api/config/backup": self._route_backup,
            "/api/config/rollback": self._route_rollback,
            "/api/config/validate": self._route_validate,
            "/api/channels/telegram": self._route_set_telegram,
            "/api/channels/telegram/add-user": self._route_tg_add_user,
            "/api/channels/telegram/remove-user": self._route_tg_remove_user,
        }

        handler = routes.get(parsed.path)
        if not handler:
            self._json({"ok": False, "error": "Route not found"}, 404)
            return

        try:
            res = handler(payload)
        except ValueError as exc:
            self._json({"ok": False, "error": str(exc)}, 400)
            return
        except Exception as exc:
            self._json({"ok": False, "error": f"Internal error: {exc}"}, 500)
            return

        status = 200 if res.get("ok") else 400
        self._json(res, status)

    def _route_save_key(self, data: Dict[str, Any]) -> Dict[str, Any]:
        key = data.get("key")
        value = data.get("value")
        if not isinstance(key, str) or not ENV_KEY_RE.match(key):
            raise ValueError("key must be a valid env variable name")
        if not isinstance(value, str) or not value.strip():
            raise ValueError("value is required")
        if any(ch in value for ch in ["\n", "\r", "`", ";"]):
            raise ValueError("value contains unsupported characters")
        write_env_key(key, value.strip())
        return {"ok": True, "saved": key}

    def _route_delete_key(self, data: Dict[str, Any]) -> Dict[str, Any]:
        key = data.get("key")
        if not isinstance(key, str) or not ENV_KEY_RE.match(key):
            raise ValueError("key must be a valid env variable name")
        return {"ok": True, "removed": delete_env_key(key), "key": key}

    def _route_set_role(self, data: Dict[str, Any]) -> Dict[str, Any]:
        role = data.get("role")
        model = data.get("model")
        if role not in SWITCHBOARD_ROLES:
            raise ValueError("role must be one of switchboard roles")
        if not isinstance(model, str):
            raise ValueError("model must be a string")

        registry = read_registry()

        def mutate(config: Dict[str, Any]):
            err = _validate_role_assignment(role, model, config, registry)
            if err:
                raise ValueError(err)
            _set_path(config, ["switchboard", "roles", role], model)
            _ensure_allowlist_has(config, [model])

        res = _mutate_config(mutate)
        if res.get("ok"):
            res.update({"role": role, "model": model})
        return res

    def _route_set_primary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        model = _validate_input_model(data)
        registry = read_registry()

        def mutate(config: Dict[str, Any]):
            err = _validate_role_assignment("primary", model, config, registry)
            if err:
                raise ValueError(err)
            _set_path(config, ["agents", "defaults", "model", "primary"], model)
            _ensure_allowlist_has(config, [model])

        res = _mutate_config(mutate)
        if res.get("ok"):
            res["model"] = model
        return res

    def _route_set_image(self, data: Dict[str, Any]) -> Dict[str, Any]:
        model = _validate_input_model(data)
        registry = read_registry()

        def mutate(config: Dict[str, Any]):
            err = _validate_role_assignment("image_model", model, config, registry)
            if err:
                raise ValueError(err)
            _set_path(config, ["agents", "defaults", "imageModel", "primary"], model)
            _ensure_allowlist_has(config, [model])

        res = _mutate_config(mutate)
        if res.get("ok"):
            res["model"] = model
        return res

    def _route_add_fallback(self, data: Dict[str, Any]) -> Dict[str, Any]:
        model = _validate_input_model(data)
        registry = read_registry()

        def mutate(config: Dict[str, Any]):
            ok, msg = registry_model_ok(
                model,
                registry,
                capabilities=ROLE_SPECS["llm_fallbacks"].get("capabilities"),
                safe_role=ROLE_SPECS["llm_fallbacks"].get("safe_role"),
            )
            if not ok:
                raise ValueError(msg or "Invalid model for fallback")
            arr = _get_path(config, ["agents", "defaults", "model", "fallbacks"], None)
            if arr is None:
                arr = []
            if not isinstance(arr, list):
                raise ValueError("agents.defaults.model.fallbacks must be an array")
            if model in arr:
                raise ValueError("Model already exists in fallbacks")
            arr.append(model)
            _set_path(config, ["agents", "defaults", "model", "fallbacks"], arr)
            _ensure_allowlist_has(config, [model])

        res = _mutate_config(mutate)
        if res.get("ok"):
            res["model"] = model
        return res

    def _route_add_image_fallback(self, data: Dict[str, Any]) -> Dict[str, Any]:
        model = _validate_input_model(data)
        registry = read_registry()

        def mutate(config: Dict[str, Any]):
            ok, msg = registry_model_ok(
                model,
                registry,
                capabilities=ROLE_SPECS["image_fallbacks"].get("capabilities"),
                safe_role=ROLE_SPECS["image_fallbacks"].get("safe_role"),
            )
            if not ok:
                raise ValueError(msg or "Invalid model for image fallback")
            arr = _get_path(config, ["agents", "defaults", "imageModel", "fallbacks"], None)
            if arr is None:
                arr = []
            if not isinstance(arr, list):
                raise ValueError("agents.defaults.imageModel.fallbacks must be an array")
            if model in arr:
                raise ValueError("Model already exists in image fallbacks")
            arr.append(model)
            _set_path(config, ["agents", "defaults", "imageModel", "fallbacks"], arr)
            _ensure_allowlist_has(config, [model])

        res = _mutate_config(mutate)
        if res.get("ok"):
            res["model"] = model
        return res

    def _route_remove_fallback(self, data: Dict[str, Any]) -> Dict[str, Any]:
        model = _validate_input_model(data)
        is_image = bool(data.get("image", False))

        def mutate(config: Dict[str, Any]):
            path = ["agents", "defaults", "imageModel" if is_image else "model", "fallbacks"]
            arr = _get_path(config, path, [])
            if not isinstance(arr, list):
                raise ValueError("Fallbacks value must be array")
            if model not in arr:
                raise ValueError("Model not found in fallback list")
            arr = [x for x in arr if x != model]
            _set_path(config, path, arr)

        res = _mutate_config(mutate)
        if res.get("ok"):
            res["model"] = model
            res["image"] = is_image
        return res

    def _route_add_allowlist(self, data: Dict[str, Any]) -> Dict[str, Any]:
        model = _validate_input_model(data)

        def mutate(config: Dict[str, Any]):
            models = _ensure_path(config, ["agents", "defaults", "models"])
            if model in models:
                raise ValueError("Model already exists in allowlist")
            models[model] = {}

        res = _mutate_config(mutate)
        if res.get("ok"):
            res["model"] = model
        return res

    def _route_remove_allowlist(self, data: Dict[str, Any]) -> Dict[str, Any]:
        model = _validate_input_model(data)

        def mutate(config: Dict[str, Any]):
            models = _get_path(config, ["agents", "defaults", "models"], None)
            if not isinstance(models, dict):
                raise ValueError("Allowlist is not configured")
            refs = set(_collect_referenced_models(config))
            if model in refs:
                raise ValueError("Cannot remove model that is currently assigned")
            if model not in models:
                raise ValueError("Model not in allowlist")
            del models[model]

        res = _mutate_config(mutate)
        if res.get("ok"):
            res["model"] = model
        return res

    def _route_backup(self, _data: Dict[str, Any]) -> Dict[str, Any]:
        name = backup_config()
        return {"ok": bool(name), "backup": name, "error": "Config file missing" if not name else None}

    def _route_rollback(self, data: Dict[str, Any]) -> Dict[str, Any]:
        filename = data.get("filename")
        if not isinstance(filename, str) or not filename.strip() or "/" in filename or ".." in filename:
            raise ValueError("filename is required")
        src = BACKUP_DIR / filename
        if not src.exists() or not src.is_file():
            raise ValueError("Backup file not found")

        registry = read_registry()
        try:
            rollback_cfg = json.loads(src.read_text(encoding="utf-8"))
        except Exception as exc:
            raise ValueError(f"Backup is not valid JSON: {exc}")

        ok, errs, _warn = validate_config(rollback_cfg, registry)
        if not ok:
            raise ValueError("Backup config does not validate: " + "; ".join(errs))

        backup_name = backup_config()
        try:
            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            CONFIG_FILE.write_text(json.dumps(rollback_cfg, indent=2) + "\n", encoding="utf-8")
            return {"ok": True, "rolledBackTo": filename, "backup": backup_name}
        except Exception as exc:
            if backup_name:
                src2 = BACKUP_DIR / backup_name
                if src2.exists():
                    shutil.copy2(str(src2), str(CONFIG_FILE))
            return {"ok": False, "error": f"Rollback failed: {exc}", "backup": backup_name}

    def _route_validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        registry = read_registry()
        target = data.get("config")
        if target is None:
            target = read_config()
        if not isinstance(target, dict):
            raise ValueError("config must be a JSON object")
        ok, errors, warnings = validate_config(target, registry)
        return {"ok": ok, "errors": errors, "warnings": warnings}

    def _route_set_telegram(self, data: Dict[str, Any]) -> Dict[str, Any]:
        allowed = {"botToken", "dmPolicy", "allowFrom", "groups", "enabled"}
        unknown = [k for k in data.keys() if k not in allowed]
        if unknown:
            raise ValueError(f"Unknown keys: {', '.join(unknown)}")

        if "dmPolicy" in data and data.get("dmPolicy") not in DM_POLICY:
            raise ValueError("dmPolicy must be pairing/allowlist/open/disabled")
        if "allowFrom" in data and (not isinstance(data.get("allowFrom"), list) or not all(isinstance(v, str) for v in data.get("allowFrom", []))):
            raise ValueError("allowFrom must be array of strings")
        if "groups" in data and (not isinstance(data.get("groups"), dict)):
            raise ValueError("groups must be object")
        if "enabled" in data and not isinstance(data.get("enabled"), bool):
            raise ValueError("enabled must be boolean")

        token_provided = "botToken" in data
        if token_provided:
            bt = data.get("botToken")
            if bt is None:
                bt = ""
            if not isinstance(bt, str):
                raise ValueError("botToken must be string")
            bt = bt.strip()
            if bt:
                write_env_key("TELEGRAM_BOT_TOKEN", bt)

        def mutate(config: Dict[str, Any]):
            _normalize_channels(config)
            tg = _get_path(config, ["channels", "telegram"], {})
            if not isinstance(tg, dict):
                tg = {}
                _set_path(config, ["channels", "telegram"], tg)

            if token_provided:
                bt = str(data.get("botToken") or "").strip()
                if bt:
                    tg["botToken"] = "${TELEGRAM_BOT_TOKEN}"
                else:
                    tg["botToken"] = ""
                    delete_env_key("TELEGRAM_BOT_TOKEN")

            if "dmPolicy" in data:
                tg["dmPolicy"] = data["dmPolicy"]
            if "allowFrom" in data:
                tg["allowFrom"] = list(dict.fromkeys(data["allowFrom"]))
            if "groups" in data:
                groups = tg.get("groups", {}) if isinstance(tg.get("groups"), dict) else {}
                if "requireMention" in data["groups"]:
                    if not isinstance(data["groups"]["requireMention"], bool):
                        raise ValueError("groups.requireMention must be boolean")
                    groups["requireMention"] = data["groups"]["requireMention"]
                tg["groups"] = groups
            if "enabled" in data:
                tg["enabled"] = bool(data["enabled"])

        return _mutate_config(mutate)

    def _route_tg_add_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = data.get("userId")
        if not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("userId is required")
        user_id = user_id.strip()

        def mutate(config: Dict[str, Any]):
            _normalize_channels(config)
            arr = _get_path(config, ["channels", "telegram", "allowFrom"], [])
            if not isinstance(arr, list):
                raise ValueError("channels.telegram.allowFrom must be array")
            if user_id not in arr:
                arr.append(user_id)
            _set_path(config, ["channels", "telegram", "allowFrom"], arr)

        res = _mutate_config(mutate)
        if res.get("ok"):
            res["userId"] = user_id
        return res

    def _route_tg_remove_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = data.get("userId")
        if not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("userId is required")
        user_id = user_id.strip()

        def mutate(config: Dict[str, Any]):
            _normalize_channels(config)
            arr = _get_path(config, ["channels", "telegram", "allowFrom"], [])
            if not isinstance(arr, list):
                raise ValueError("channels.telegram.allowFrom must be array")
            arr = [v for v in arr if v != user_id]
            _set_path(config, ["channels", "telegram", "allowFrom"], arr)

        res = _mutate_config(mutate)
        if res.get("ok"):
            res["userId"] = user_id
        return res

    def _route_auto_fix(self, data: Dict[str, Any]) -> Dict[str, Any]:
        issue = data.get("issue")
        if not isinstance(issue, str) or not issue:
            raise ValueError("issue is required")

        registry = read_registry()
        env = read_env()

        def mutate(config: Dict[str, Any]):
            _normalize_channels(config)
            if issue == "no_llm_fallbacks":
                primary = _get_path(config, ["agents", "defaults", "model", "primary"], "")
                arr = _get_path(config, ["agents", "defaults", "model", "fallbacks"], [])
                if not isinstance(arr, list):
                    arr = []
                exclude = set(arr)
                if isinstance(primary, str) and primary:
                    exclude.add(primary)
                picks = _model_candidates(
                    registry,
                    env,
                    capabilities=ROLE_SPECS["llm_fallbacks"]["capabilities"],
                    safe_role=ROLE_SPECS["llm_fallbacks"].get("safe_role"),
                    exclude=exclude,
                    exclude_provider=provider_of(primary) if primary else None,
                )
                if not picks:
                    raise ValueError("No authenticated candidates for LLM fallback")
                arr.append(picks[0])
                _set_path(config, ["agents", "defaults", "model", "fallbacks"], arr)
                _ensure_allowlist_has(config, [picks[0]])

            elif issue == "no_image_fallbacks":
                primary = _get_path(config, ["agents", "defaults", "imageModel", "primary"], "")
                arr = _get_path(config, ["agents", "defaults", "imageModel", "fallbacks"], [])
                if not isinstance(arr, list):
                    arr = []
                exclude = set(arr)
                if isinstance(primary, str) and primary:
                    exclude.add(primary)
                picks = _model_candidates(
                    registry,
                    env,
                    capabilities=ROLE_SPECS["image_fallbacks"]["capabilities"],
                    safe_role=ROLE_SPECS["image_fallbacks"].get("safe_role"),
                    exclude=exclude,
                    exclude_provider=provider_of(primary) if primary else None,
                )
                if not picks:
                    raise ValueError("No authenticated candidates for image fallback")
                arr.append(picks[0])
                _set_path(config, ["agents", "defaults", "imageModel", "fallbacks"], arr)
                _ensure_allowlist_has(config, [picks[0]])

            elif issue == "small_allowlist":
                models = _ensure_path(config, ["agents", "defaults", "models"])
                added = 0
                for ref, model in registry.get("models", {}).items():
                    if model.get("blocked"):
                        continue
                    pid = provider_of(ref)
                    pinfo = registry.get("providers", {}).get(pid, {})
                    if _provider_authenticated(pid, pinfo, env) and ref not in models:
                        models[ref] = {}
                        added += 1
                if added == 0:
                    raise ValueError("No additional authenticated models available")

            elif issue == "coding_provider_collision":
                cp1 = _get_path(config, ["switchboard", "roles", "coding_pass1"], "")
                cp2 = _get_path(config, ["switchboard", "roles", "coding_pass2"], "")
                cp3 = _get_path(config, ["switchboard", "roles", "coding_pass3"], "")
                if not cp1:
                    raise ValueError("coding_pass1 must be set first")
                p1 = provider_of(cp1)
                picks2 = _model_candidates(
                    registry,
                    env,
                    capabilities=ROLE_SPECS["coding_pass2"]["capabilities"],
                    safe_role="coding",
                    exclude={cp1},
                    exclude_provider=p1,
                )
                if not picks2:
                    raise ValueError("No alternative provider available for coding_pass2")
                if not cp2 or provider_of(cp2) == p1:
                    cp2 = picks2[0]
                    _set_path(config, ["switchboard", "roles", "coding_pass2"], cp2)

                used = {provider_of(cp1), provider_of(cp2)}
                picks3 = [
                    m
                    for m in _model_candidates(
                        registry,
                        env,
                        capabilities=ROLE_SPECS["coding_pass3"]["capabilities"],
                        safe_role="coding",
                        exclude={cp1, cp2},
                    )
                    if provider_of(m) not in used
                ]
                if not picks3:
                    raise ValueError("No third provider available for coding_pass3")
                if not cp3 or provider_of(cp3) in used:
                    cp3 = picks3[0]
                    _set_path(config, ["switchboard", "roles", "coding_pass3"], cp3)
                _ensure_allowlist_has(config, [cp2, cp3])

            elif issue.startswith("missing_role:"):
                role = issue.split(":", 1)[1]
                if role not in SWITCHBOARD_ROLES:
                    raise ValueError("Unknown role for auto-fix")
                spec = ROLE_SPECS[role]
                cur = _get_path(config, spec["path"], "")
                if cur:
                    return
                exclude_providers = set()
                if role in {"coding_pass2", "coding_pass3"}:
                    cp1 = _get_path(config, ["switchboard", "roles", "coding_pass1"], "")
                    cp2 = _get_path(config, ["switchboard", "roles", "coding_pass2"], "")
                    if role == "coding_pass2" and cp1:
                        exclude_providers.add(provider_of(cp1))
                    if role == "coding_pass3":
                        for ref in [cp1, cp2]:
                            if ref:
                                exclude_providers.add(provider_of(ref))

                picks = _model_candidates(
                    registry,
                    env,
                    capabilities=spec.get("capabilities"),
                    capabilities_any=spec.get("capabilities_any"),
                    safe_role=spec.get("safe_role"),
                )
                picks = [m for m in picks if provider_of(m) not in exclude_providers]
                if not picks:
                    raise ValueError(f"No authenticated candidate found for role {role}")
                _set_path(config, spec["path"], picks[0])
                _ensure_allowlist_has(config, [picks[0]])

            else:
                raise ValueError(f"Unknown issue id: {issue}")

        res = _mutate_config(mutate)
        if res.get("ok"):
            res["issue"] = issue
        return res

    def _read_json_body(self) -> Optional[Dict[str, Any]]:
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._json({"ok": False, "error": "Invalid Content-Length"}, 400)
            return None
        raw = self.rfile.read(size) if size > 0 else b"{}"
        try:
            data = json.loads(raw)
        except Exception:
            self._json({"ok": False, "error": "Request body must be valid JSON"}, 400)
            return None
        if not isinstance(data, dict):
            self._json({"ok": False, "error": "JSON body must be an object"}, 400)
            return None
        return data

    def _json(self, obj: Dict[str, Any], status: int = 200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, _fmt, *_args):
        return


if __name__ == "__main__":
    print(f"Model Switchboard v2 server listening on http://127.0.0.1:{PORT}")
    print(f"Config:   {CONFIG_FILE}")
    print(f"Registry: {REGISTRY_FILE}")
    print(f"Env:      {ENV_FILE}")
    print(f"Backups:  {BACKUP_DIR}")
    server = http.server.HTTPServer(("127.0.0.1", PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()
