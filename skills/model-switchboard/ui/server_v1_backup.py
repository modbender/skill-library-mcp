#!/usr/bin/env python3
"""Model Switchboard — Local API server for the interactive dashboard."""

import http.server
import json
import os
import re
import shutil
import sys
import time
import urllib.parse
from pathlib import Path

PORT = int(os.environ.get("SWITCHBOARD_PORT", "8770"))
ENV_FILE = os.environ.get("SWITCHBOARD_ENV", os.path.expanduser("~/.openclaw/workspace/.env"))
REGISTRY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "model-registry.json")
CONFIG_FILE = os.path.expanduser("~/.openclaw/openclaw.json")
BACKUP_DIR = os.path.expanduser("~/.openclaw/backups/switchboard")
UI_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Helpers ──────────────────────────────────────────────────────────────

def read_env() -> dict:
    env = {}
    p = Path(ENV_FILE)
    if not p.exists():
        return env
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def write_env_key(key: str, value: str) -> None:
    p = Path(ENV_FILE)
    p.parent.mkdir(parents=True, exist_ok=True)
    lines = p.read_text().splitlines() if p.exists() else []
    found = False
    new_lines = []
    pattern = re.compile(rf"^{re.escape(key)}\s*=")
    for line in lines:
        if pattern.match(line.strip()):
            new_lines.append(f'{key}="{value}"')
            found = True
        else:
            new_lines.append(line)
    if not found:
        new_lines.append(f'{key}="{value}"')
    p.write_text("\n".join(new_lines) + "\n")
    os.chmod(str(p), 0o600)


def delete_env_key(key: str) -> bool:
    p = Path(ENV_FILE)
    if not p.exists():
        return False
    lines = p.read_text().splitlines()
    pattern = re.compile(rf"^{re.escape(key)}\s*=")
    new_lines = [l for l in lines if not pattern.match(l.strip())]
    if len(new_lines) == len(lines):
        return False
    p.write_text("\n".join(new_lines) + "\n")
    os.chmod(str(p), 0o600)
    return True


def read_registry() -> dict:
    try:
        return json.loads(Path(REGISTRY_FILE).read_text())
    except Exception:
        return {"models": {}, "providers": {}}


def read_config() -> dict:
    try:
        return json.loads(Path(CONFIG_FILE).read_text())
    except Exception:
        return {}


def write_config(config: dict) -> None:
    """Write openclaw.json with backup."""
    backup_config()
    Path(CONFIG_FILE).write_text(json.dumps(config, indent=2) + "\n")


def backup_config() -> str:
    """Create timestamped backup of openclaw.json. Returns backup path."""
    src = Path(CONFIG_FILE)
    if not src.exists():
        return ""
    bdir = Path(BACKUP_DIR)
    bdir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    dest = bdir / f"openclaw-{ts}.json"
    shutil.copy2(str(src), str(dest))
    # Keep max 20 backups
    backups = sorted(bdir.glob("openclaw-*.json"))
    while len(backups) > 20:
        backups.pop(0).unlink()
    return str(dest)


def count_backups() -> int:
    bdir = Path(BACKUP_DIR)
    if not bdir.exists():
        return 0
    return len(list(bdir.glob("openclaw-*.json")))


def build_status() -> dict:
    registry = read_registry()
    config = read_config()
    env = read_env()

    agents = config.get("agents", {}).get("defaults", {})
    model_cfg = agents.get("model", {})
    img_cfg = agents.get("imageModel", {})

    providers_status = {}
    for pid, pinfo in registry.get("providers", {}).items():
        auth_envs = pinfo.get("authEnv", [])
        has_auth = any(env.get(k) for k in auth_envs)
        auth_method = pinfo.get("authMethod", "api-key")
        providers_status[pid] = {
            "displayName": pinfo.get("displayName", pid),
            "type": pinfo.get("type", "built-in"),
            "hasAuth": has_auth,
            "authMethod": auth_method,
            "authEnvVars": auth_envs,
            "website": pinfo.get("website", ""),
            "note": pinfo.get("note", ""),
        }

    models_cfg = agents.get("models", {})
    allowlist = list(models_cfg.keys()) if models_cfg else []

    return {
        "primary": model_cfg.get("primary", ""),
        "imageModel": img_cfg.get("primary", ""),
        "fallbacks": model_cfg.get("fallbacks", []),
        "imageFallbacks": img_cfg.get("fallbacks", []),
        "providers": providers_status,
        "allowlist": allowlist,
        "models": registry.get("models", {}),
        "registryVersion": registry.get("version", "?"),
        "timestamp": registry.get("lastUpdated", ""),
        "backupCount": count_backups(),
    }


# ── Config modification helpers ──────────────────────────────────────────

def validate_model_ref(ref: str) -> bool:
    """Validate a model reference format."""
    return bool(ref and "/" in ref and len(ref) < 200 and
                re.match(r'^[a-z][a-z0-9_-]*/[a-z0-9._:/-]+$', ref))


def validate_model_for_role(ref: str, role: str, registry: dict) -> tuple:
    """Check if model is safe for given role. Returns (ok, reason)."""
    models = registry.get("models", {})
    model_info = models.get(ref)
    if not model_info:
        # Unknown model — allow but warn
        return True, "Model not in registry — cannot verify compatibility"
    if model_info.get("blocked"):
        return False, model_info.get("blockReason", "Model is blocked")
    unsafe = model_info.get("unsafeRoles", [])
    if role in unsafe:
        return False, f"Model is unsafe for {role} role"
    safe = model_info.get("safeRoles", [])
    if role not in safe:
        return True, f"Model not explicitly listed as safe for {role} — proceed with caution"
    return True, ""


def config_add_fallback(ref: str) -> dict:
    """Add LLM fallback. Returns result dict."""
    if not validate_model_ref(ref):
        return {"error": f"Invalid model ref: {ref}"}
    registry = read_registry()
    ok, reason = validate_model_for_role(ref, "fallback", registry)
    if not ok:
        return {"error": reason}

    config = read_config()
    agents = config.setdefault("agents", {}).setdefault("defaults", {})
    model_cfg = agents.setdefault("model", {})
    fallbacks = model_cfg.setdefault("fallbacks", [])
    if ref in fallbacks:
        return {"error": f"{ref} is already a fallback"}
    fallbacks.append(ref)
    # Also add to allowlist if it exists
    models = agents.get("models")
    if models is not None and ref not in models:
        models[ref] = {}
    write_config(config)
    return {"ok": True, "action": "add_fallback", "model": ref, "warning": reason}


def config_add_image_fallback(ref: str) -> dict:
    """Add image model fallback."""
    if not validate_model_ref(ref):
        return {"error": f"Invalid model ref: {ref}"}
    registry = read_registry()
    ok, reason = validate_model_for_role(ref, "image", registry)
    if not ok:
        return {"error": reason}

    config = read_config()
    agents = config.setdefault("agents", {}).setdefault("defaults", {})
    img_cfg = agents.setdefault("imageModel", {})
    fallbacks = img_cfg.setdefault("fallbacks", [])
    if ref in fallbacks:
        return {"error": f"{ref} is already an image fallback"}
    fallbacks.append(ref)
    models = agents.get("models")
    if models is not None and ref not in models:
        models[ref] = {}
    write_config(config)
    return {"ok": True, "action": "add_image_fallback", "model": ref, "warning": reason}


def config_remove_fallback(ref: str, is_image: bool = False) -> dict:
    """Remove a fallback."""
    config = read_config()
    agents = config.get("agents", {}).get("defaults", {})
    key = "imageModel" if is_image else "model"
    cfg = agents.get(key, {})
    fallbacks = cfg.get("fallbacks", [])
    if ref not in fallbacks:
        return {"error": f"{ref} not in {'image ' if is_image else ''}fallbacks"}
    fallbacks.remove(ref)
    write_config(config)
    return {"ok": True, "action": "remove_fallback", "model": ref}


def config_add_to_allowlist(ref: str) -> dict:
    """Add model to allowlist."""
    if not validate_model_ref(ref):
        return {"error": f"Invalid model ref: {ref}"}
    config = read_config()
    agents = config.setdefault("agents", {}).setdefault("defaults", {})
    models = agents.setdefault("models", {})
    if ref in models:
        return {"error": f"{ref} already in allowlist"}
    models[ref] = {}
    write_config(config)
    return {"ok": True, "action": "add_allowlist", "model": ref}


def config_remove_from_allowlist(ref: str) -> dict:
    """Remove model from allowlist."""
    config = read_config()
    agents = config.get("agents", {}).get("defaults", {})
    models = agents.get("models", {})
    if ref not in models:
        return {"error": f"{ref} not in allowlist"}
    # Don't remove if it's the primary or in fallbacks
    model_cfg = agents.get("model", {})
    if ref == model_cfg.get("primary"):
        return {"error": "Cannot remove primary model from allowlist"}
    del models[ref]
    write_config(config)
    return {"ok": True, "action": "remove_allowlist", "model": ref}


def config_set_primary(ref: str) -> dict:
    """Set primary model."""
    if not validate_model_ref(ref):
        return {"error": f"Invalid model ref: {ref}"}
    registry = read_registry()
    ok, reason = validate_model_for_role(ref, "primary", registry)
    if not ok:
        return {"error": reason}

    config = read_config()
    agents = config.setdefault("agents", {}).setdefault("defaults", {})
    model_cfg = agents.setdefault("model", {})
    model_cfg["primary"] = ref
    models = agents.get("models")
    if models is not None and ref not in models:
        models[ref] = {}
    write_config(config)
    return {"ok": True, "action": "set_primary", "model": ref, "warning": reason}


def config_set_image_model(ref: str) -> dict:
    """Set image model."""
    if not validate_model_ref(ref):
        return {"error": f"Invalid model ref: {ref}"}
    registry = read_registry()
    ok, reason = validate_model_for_role(ref, "image", registry)
    if not ok:
        return {"error": reason}

    config = read_config()
    agents = config.setdefault("agents", {}).setdefault("defaults", {})
    img_cfg = agents.setdefault("imageModel", {})
    img_cfg["primary"] = ref
    models = agents.get("models")
    if models is not None and ref not in models:
        models[ref] = {}
    write_config(config)
    return {"ok": True, "action": "set_image_model", "model": ref, "warning": reason}


def config_auto_fix(issue_id: str) -> dict:
    """Auto-fix a known issue by ID."""
    registry = read_registry()
    config = read_config()
    env = read_env()
    agents = config.setdefault("agents", {}).setdefault("defaults", {})

    if issue_id == "no_llm_fallbacks":
        # Add diverse fallbacks from authenticated providers
        model_cfg = agents.setdefault("model", {})
        primary = model_cfg.get("primary", "")
        primary_provider = primary.split("/")[0] if primary else ""
        fallbacks = model_cfg.setdefault("fallbacks", [])

        candidates = _get_auth_candidates(registry, env, "fallback", primary_provider, fallbacks)
        added = []
        for ref in candidates[:3]:
            if ref not in fallbacks and ref != primary:
                fallbacks.append(ref)
                models = agents.get("models")
                if models is not None and ref not in models:
                    models[ref] = {}
                added.append(ref)
        if added:
            write_config(config)
            return {"ok": True, "action": "auto_fix", "issue": issue_id,
                    "added": added, "message": f"Added {len(added)} fallback(s): {', '.join(added)}"}
        return {"error": "No authenticated models available to add as fallbacks"}

    elif issue_id == "no_image_fallbacks":
        img_cfg = agents.setdefault("imageModel", {})
        img_primary = img_cfg.get("primary", "")
        img_provider = img_primary.split("/")[0] if img_primary else ""
        img_fallbacks = img_cfg.setdefault("fallbacks", [])

        candidates = _get_auth_candidates(registry, env, "image", img_provider, img_fallbacks)
        added = []
        for ref in candidates[:2]:
            if ref not in img_fallbacks and ref != img_primary:
                img_fallbacks.append(ref)
                models = agents.get("models")
                if models is not None and ref not in models:
                    models[ref] = {}
                added.append(ref)
        if added:
            write_config(config)
            return {"ok": True, "action": "auto_fix", "issue": issue_id,
                    "added": added, "message": f"Added {len(added)} image fallback(s): {', '.join(added)}"}
        return {"error": "No authenticated vision-capable models available"}

    elif issue_id == "small_allowlist":
        # Add all models from authenticated providers
        models_cfg = agents.setdefault("models", {})
        all_models = registry.get("models", {})
        added = []
        for ref, minfo in all_models.items():
            if ref in models_cfg or minfo.get("blocked"):
                continue
            provider = ref.split("/")[0]
            pinfo = registry.get("providers", {}).get(provider, {})
            auth_envs = pinfo.get("authEnv", [])
            if any(env.get(k) for k in auth_envs):
                models_cfg[ref] = {}
                added.append(ref)
        if added:
            write_config(config)
            return {"ok": True, "action": "auto_fix", "issue": issue_id,
                    "added": added, "message": f"Added {len(added)} models from authenticated providers to allowlist"}
        return {"error": "No additional models from authenticated providers to add"}

    elif issue_id == "few_providers":
        return {"ok": False, "action": "redirect",
                "message": "Click on unconfigured providers above to add API keys",
                "redirect": "providers"}

    return {"error": f"Unknown issue: {issue_id}"}


def _get_auth_candidates(registry, env, role, exclude_provider, exclude_refs):
    """Get model candidates from authenticated providers for a role, excluding given provider."""
    candidates = []
    all_models = registry.get("models", {})
    providers = registry.get("providers", {})

    # Score: prefer different providers, lower cost, more capabilities
    scored = []
    for ref, minfo in all_models.items():
        if minfo.get("blocked"):
            continue
        safe_roles = minfo.get("safeRoles", [])
        if role not in safe_roles:
            continue
        provider = ref.split("/")[0]
        if provider == exclude_provider:
            continue
        if ref in exclude_refs:
            continue
        pinfo = providers.get(provider, {})
        auth_envs = pinfo.get("authEnv", [])
        if not any(env.get(k) for k in auth_envs):
            continue
        # Score: lower cost = better
        cost_scores = {"free": 0, "very-low": 1, "low": 2, "medium": 3, "high": 4, "subscription": 5, "proxy": 3}
        score = cost_scores.get(minfo.get("costTier", "medium"), 3)
        scored.append((score, ref))

    scored.sort()
    return [ref for _, ref in scored]


# ── HTTP Handler ─────────────────────────────────────────────────────────

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=UI_DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/status":
            self._json_response(build_status())
        elif parsed.path == "/api/registry":
            self._json_response(read_registry())
        elif parsed.path == "/api/env":
            env = read_env()
            self._json_response({"keys": list(env.keys())})
        elif parsed.path == "/api/backups":
            bdir = Path(BACKUP_DIR)
            backups = []
            if bdir.exists():
                for f in sorted(bdir.glob("openclaw-*.json"), reverse=True)[:10]:
                    backups.append({"name": f.name, "size": f.stat().st_size,
                                    "modified": f.stat().st_mtime})
            self._json_response({"backups": backups})
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len) if content_len else b"{}"
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self._json_response({"error": "Invalid JSON"}, 400)
            return

        routes = {
            "/api/key": self._handle_save_key,
            "/api/key/delete": self._handle_delete_key,
            "/api/config/add-fallback": lambda d: self._json_response(config_add_fallback(d.get("model", ""))),
            "/api/config/add-image-fallback": lambda d: self._json_response(config_add_image_fallback(d.get("model", ""))),
            "/api/config/remove-fallback": lambda d: self._json_response(config_remove_fallback(d.get("model", ""), d.get("image", False))),
            "/api/config/add-allowlist": lambda d: self._json_response(config_add_to_allowlist(d.get("model", ""))),
            "/api/config/remove-allowlist": lambda d: self._json_response(config_remove_from_allowlist(d.get("model", ""))),
            "/api/config/set-primary": lambda d: self._json_response(config_set_primary(d.get("model", ""))),
            "/api/config/set-image-model": lambda d: self._json_response(config_set_image_model(d.get("model", ""))),
            "/api/config/auto-fix": lambda d: self._json_response(config_auto_fix(d.get("issue", ""))),
            "/api/config/backup": lambda d: self._json_response({"ok": True, "path": backup_config()}),
        }

        handler = routes.get(parsed.path)
        if handler:
            handler(data)
        else:
            self._json_response({"error": "Not found"}, 404)

    def _handle_save_key(self, data):
        key = data.get("key", "").strip()
        value = data.get("value", "").strip()
        if not key or not value:
            self._json_response({"error": "Missing key or value"}, 400)
            return
        if not re.match(r"^[A-Z][A-Z0-9_]*$", key):
            self._json_response({"error": "Invalid env var name"}, 400)
            return
        if any(c in value for c in ["\n", "\r", "`", "$", ";"]):
            self._json_response({"error": "Invalid characters in value"}, 400)
            return
        write_env_key(key, value)
        self._json_response({"ok": True, "key": key, "saved": True})

    def _handle_delete_key(self, data):
        key = data.get("key", "").strip()
        if not key:
            self._json_response({"error": "Missing key"}, 400)
            return
        removed = delete_env_key(key)
        self._json_response({"ok": True, "key": key, "removed": removed})

    def _json_response(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    print(f"🔀 Model Switchboard server on http://127.0.0.1:{PORT}")
    print(f"   .env file: {ENV_FILE}")
    print(f"   Registry:  {REGISTRY_FILE}")
    print(f"   Config:    {CONFIG_FILE}")
    server = http.server.HTTPServer(("127.0.0.1", PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()
