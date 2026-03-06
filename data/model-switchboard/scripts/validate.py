#!/usr/bin/env python3
"""
Model Switchboard — Validation Engine
Validates model assignments, config integrity, and generates dry-run diffs.
Zero external dependencies. Python 3.8+.
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ── Paths ──────────────────────────────────────────────────────
SKILL_DIR = Path(__file__).resolve().parent.parent
REGISTRY_PATH = SKILL_DIR / "model-registry.json"
CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"
BACKUP_DIR = Path.home() / ".openclaw" / "model-backups"

# ── Registry ───────────────────────────────────────────────────

class RegistryLoadError(Exception):
    """Raised when the model registry cannot be loaded."""
    pass


class ConfigLoadError(Exception):
    """Raised when openclaw.json cannot be loaded."""
    pass


def load_registry(strict: bool = True) -> Dict[str, Any]:
    """
    Load the model registry.
    In strict mode (default for safety operations): raises on failure.
    In non-strict mode (status/display): returns empty structure.
    """
    try:
        with open(REGISTRY_PATH, "r") as f:
            data = json.load(f)
            if "models" not in data or "roles" not in data:
                if strict:
                    raise RegistryLoadError(f"Registry missing required keys (models/roles): {REGISTRY_PATH}")
                return {"models": {}, "providers": {}, "roles": {}}
            return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        if strict:
            raise RegistryLoadError(f"Cannot load model registry: {e}")
        return {"models": {}, "providers": {}, "roles": {}}


def load_config(strict: bool = False) -> Dict[str, Any]:
    """
    Load openclaw.json.
    In strict mode: raises on failure.
    In non-strict mode (default): returns empty dict with _load_error flag.
    """
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        if strict:
            raise ConfigLoadError(f"Config not found: {CONFIG_PATH}")
        return {"_load_error": "Config file not found"}
    except json.JSONDecodeError as e:
        if strict:
            raise ConfigLoadError(f"Config is not valid JSON: {e}")
        return {"_load_error": f"Invalid JSON: {e}"}


# ── Validation Functions ───────────────────────────────────────

def validate_model_ref(model: str) -> Tuple[bool, str]:
    """
    Validate model reference format.
    Must be provider/model-name (e.g., anthropic/claude-opus-4-6).
    OpenRouter uses provider/subprovider/model format.
    """
    if not model or not isinstance(model, str):
        return False, "Model reference cannot be empty"

    parts = model.split("/", 1)
    if len(parts) < 2 or not parts[0] or not parts[1]:
        return False, f"Invalid format: '{model}'. Must be provider/model-name (e.g., anthropic/claude-opus-4-6)"

    provider = parts[0]
    model_id = parts[1]

    # Provider must be alphanumeric + hyphens
    if not re.match(r'^[a-z0-9][a-z0-9-]*$', provider):
        return False, f"Invalid provider: '{provider}'. Use lowercase alphanumeric + hyphens"

    # Model ID: alphanumeric + hyphens + dots + slashes (for OpenRouter)
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9._/-]*$', model_id):
        return False, f"Invalid model ID: '{model_id}'"

    return True, "Valid"


def validate_role_compatibility(model: str, role: str) -> Tuple[bool, str, Optional[str]]:
    """
    Check if a model is compatible with a given role.
    Returns (is_valid, message, suggestion).
    FAIL-CLOSED: if registry can't load, rejects the assignment.
    """
    try:
        registry = load_registry(strict=True)
    except RegistryLoadError as e:
        return False, f"SAFETY BLOCK: Cannot load model registry — {e}. Fix registry before changing models.", None
    roles = registry.get("roles", {})
    models = registry.get("models", {})

    if role not in roles:
        return True, f"Unknown role '{role}' — skipping capability check", None

    role_info = roles[role]
    required_caps = set(role_info.get("requiredCapabilities", []))

    # Check registry for known models
    if model in models:
        model_info = models[model]

        # Hard block check
        if model_info.get("blocked", False):
            reason = model_info.get("blockReason", "This model is blocked for all roles")
            return False, f"BLOCKED: {reason}", None

        # Unsafe role check
        unsafe = model_info.get("unsafeRoles", [])
        if role in unsafe:
            return False, f"'{model}' is not safe for the '{role}' role", None

        # Safe role check
        safe = set(model_info.get("safeRoles", []))
        if role not in safe:
            return False, f"'{model}' is not verified for the '{role}' role. Safe roles: {', '.join(safe)}", None

        # Capability check
        model_caps = set(model_info.get("capabilities", []))
        missing = required_caps - model_caps
        if missing:
            return False, f"'{model}' lacks required capabilities for '{role}': {', '.join(missing)}", None

        return True, f"'{model}' is compatible with '{role}' role", None

    # Unknown model — warn but allow (might be OpenRouter or new model)
    provider = model.split("/")[0]
    if provider == "openrouter":
        return True, f"OpenRouter model — cannot verify capabilities offline. Proceed with caution.", None

    return True, f"Model '{model}' not in registry — cannot verify capabilities. Proceed with caution.", \
        "Add this model to model-registry.json for future validation"


def validate_config_schema(config: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Validate the config structure for model-related keys.
    Returns list of issues found.
    """
    issues: List[Dict[str, str]] = []

    # Check for load errors
    if "_load_error" in config:
        issues.append({
            "level": "error",
            "field": "openclaw.json",
            "message": f"Config load failed: {config['_load_error']}"
        })
        return issues

    agents = config.get("agents", {})
    defaults = agents.get("defaults", {}) if isinstance(agents, dict) else {}

    model = defaults.get("model", {}) if isinstance(defaults, dict) else {}
    image_model = defaults.get("imageModel", {}) if isinstance(defaults, dict) else {}

    # Check model structure
    if isinstance(model, str):
        # Old format — should be { primary: "..." }
        issues.append({
            "level": "warning",
            "field": "agents.defaults.model",
            "message": f"Model is a plain string ('{model}'). Recommended: {{ primary: \"{model}\" }}"
        })
    elif isinstance(model, dict):
        primary = model.get("primary")
        if primary:
            valid, msg = validate_model_ref(primary)
            if not valid:
                issues.append({"level": "error", "field": "agents.defaults.model.primary", "message": msg})

        fallbacks = model.get("fallbacks", [])
        if not isinstance(fallbacks, list):
            issues.append({
                "level": "error",
                "field": "agents.defaults.model.fallbacks",
                "message": "Fallbacks must be an array"
            })
        else:
            for i, fb in enumerate(fallbacks):
                valid, msg = validate_model_ref(fb)
                if not valid:
                    issues.append({
                        "level": "error",
                        "field": f"agents.defaults.model.fallbacks[{i}]",
                        "message": msg
                    })

    # Check imageModel structure
    if isinstance(image_model, str):
        issues.append({
            "level": "warning",
            "field": "agents.defaults.imageModel",
            "message": f"Image model is a plain string ('{image_model}'). Recommended: {{ primary: \"{image_model}\" }}"
        })
    elif isinstance(image_model, dict):
        img_primary = image_model.get("primary")
        if img_primary:
            valid, msg = validate_model_ref(img_primary)
            if not valid:
                issues.append({"level": "error", "field": "agents.defaults.imageModel.primary", "message": msg})

        img_fallbacks = image_model.get("fallbacks", [])
        if not isinstance(img_fallbacks, list):
            issues.append({
                "level": "error",
                "field": "agents.defaults.imageModel.fallbacks",
                "message": "Image fallbacks must be an array"
            })
        else:
            for i, ifb in enumerate(img_fallbacks):
                valid, msg = validate_model_ref(ifb)
                if not valid:
                    issues.append({
                        "level": "error",
                        "field": f"agents.defaults.imageModel.fallbacks[{i}]",
                        "message": msg
                    })

    # Check allowlist
    models_list = defaults.get("models", {})
    if models_list and isinstance(models_list, dict):
        for model_key in models_list:
            valid, msg = validate_model_ref(model_key)
            if not valid:
                issues.append({
                    "level": "warning",
                    "field": f"agents.defaults.models.{model_key}",
                    "message": f"Invalid model ref in allowlist: {msg}"
                })

    return issues


def check_provider_auth(provider: str) -> Tuple[bool, str]:
    """Check if a provider has auth configured (via environment variables)."""
    registry = load_registry(strict=False)
    providers = registry.get("providers", {})

    if provider not in providers:
        return False, f"Unknown provider: '{provider}'"

    provider_info = providers[provider]
    auth_envs = provider_info.get("authEnv", [])

    if not auth_envs:
        auth_method = provider_info.get("authMethod", "unknown")
        return True, f"Provider uses {auth_method} auth (not env-based)"

    for env_var in auth_envs:
        if os.environ.get(env_var):
            return True, f"Auth configured via {env_var}"

    return False, f"No auth found. Set one of: {', '.join(auth_envs)}"


def generate_dry_run_diff(action: str, model: str, role: str) -> Dict[str, Any]:
    """Generate a diff showing what would change without applying."""
    config = load_config()
    agents = config.get("agents", {}).get("defaults", {})

    current = {}
    proposed = {}

    if action == "set-primary":
        model_cfg = agents.get("model", {})
        current_primary = model_cfg.get("primary") if isinstance(model_cfg, dict) else model_cfg
        current = {"agents.defaults.model.primary": current_primary or "(not set)"}
        proposed = {"agents.defaults.model.primary": model}

    elif action == "set-image":
        img_cfg = agents.get("imageModel", {})
        current_img = img_cfg.get("primary") if isinstance(img_cfg, dict) else img_cfg
        current = {"agents.defaults.imageModel.primary": current_img or "(not set)"}
        proposed = {"agents.defaults.imageModel.primary": model}

    elif action == "add-fallback":
        model_cfg = agents.get("model", {})
        fb = model_cfg.get("fallbacks", []) if isinstance(model_cfg, dict) else []
        current = {"agents.defaults.model.fallbacks": fb}
        proposed = {"agents.defaults.model.fallbacks": fb + [model]}

    elif action == "add-image-fallback":
        img_cfg = agents.get("imageModel", {})
        ifb = img_cfg.get("fallbacks", []) if isinstance(img_cfg, dict) else []
        current = {"agents.defaults.imageModel.fallbacks": ifb}
        proposed = {"agents.defaults.imageModel.fallbacks": ifb + [model]}

    return {
        "action": action,
        "model": model,
        "role": role,
        "current": current,
        "proposed": proposed,
        "wouldChange": current != proposed
    }


def validate_cron_models() -> Dict[str, Any]:
    """
    Validate model references in cron jobs against the registry and allowlist.
    Reads from ~/.openclaw/cron/jobs.json.
    """
    cron_path = Path.home() / ".openclaw" / "cron" / "jobs.json"
    issues: List[Dict[str, str]] = []

    if not cron_path.exists():
        return {"totalJobs": 0, "issues": [], "note": "No cron jobs file found"}

    try:
        with open(cron_path) as f:
            jobs = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        return {"totalJobs": 0, "issues": [{"level": "error", "job": "(file)", "message": f"Cannot read cron jobs: {e}"}]}

    if not isinstance(jobs, list):
        jobs = list(jobs.values()) if isinstance(jobs, dict) else []

    registry = load_registry(strict=False)
    config = load_config(strict=False)
    agents = config.get("agents", {}).get("defaults", {})
    raw_models = agents.get("models")
    allowlist = set(raw_models.keys()) if isinstance(raw_models, dict) else set()

    for job in jobs:
        if not isinstance(job, dict):
            continue
        job_name = job.get("name") or job.get("id") or "unnamed"
        # Extract model from various possible locations
        model = (job.get("model") or
                 (job.get("payload") or {}).get("model") or
                 (job.get("config") or {}).get("model"))
        if not model:
            continue

        # Validate format
        valid, msg = validate_model_ref(model)
        if not valid:
            issues.append({"level": "error", "job": job_name, "message": f"Invalid model ref '{model}': {msg}"})
            continue

        # Check registry
        if model not in registry.get("models", {}):
            issues.append({"level": "warning", "job": job_name, "message": f"Model '{model}' not in registry"})

        # Check allowlist (if allowlist is configured)
        if allowlist and model not in allowlist:
            issues.append({"level": "warning", "job": job_name, "message": f"Model '{model}' not in allowlist"})

        # Check if blocked
        model_info = registry.get("models", {}).get(model, {})
        if model_info.get("blocked"):
            issues.append({"level": "error", "job": job_name, "message": f"Model '{model}' is blocked: {model_info.get('blockReason', 'no reason')}"})

    return {"totalJobs": len(jobs), "issues": issues}


def get_full_status() -> Dict[str, Any]:
    """Get complete model configuration status for UI rendering."""
    config = load_config(strict=False)
    registry = load_registry(strict=False)
    agents = config.get("agents", {}).get("defaults", {})

    model_cfg = agents.get("model", {})
    image_cfg = agents.get("imageModel", {})

    # Extract primary + fallbacks
    if isinstance(model_cfg, str):
        primary = model_cfg
        fallbacks = []
    elif isinstance(model_cfg, dict):
        primary = model_cfg.get("primary")
        fallbacks = model_cfg.get("fallbacks", [])
    else:
        primary = None
        fallbacks = []

    if isinstance(image_cfg, str):
        image_primary = image_cfg
        image_fallbacks = []
    elif isinstance(image_cfg, dict):
        image_primary = image_cfg.get("primary")
        image_fallbacks = image_cfg.get("fallbacks", [])
    else:
        image_primary = None
        image_fallbacks = []

    # Allowlist (safe: handle non-dict types)
    raw_models = agents.get("models")
    allowlist = list(raw_models.keys()) if isinstance(raw_models, dict) else []

    # Provider auth status
    provider_status = {}
    for pid, pinfo in registry.get("providers", {}).items():
        has_auth, auth_msg = check_provider_auth(pid)
        provider_status[pid] = {
            "displayName": pinfo.get("displayName", pid),
            "hasAuth": has_auth,
            "authMessage": auth_msg
        }

    # Backup count
    backup_count = 0
    if BACKUP_DIR.exists():
        backup_count = len(list(BACKUP_DIR.glob("openclaw-*.json")))

    # Config validation
    issues = validate_config_schema(config)

    return {
        "primary": primary,
        "fallbacks": fallbacks,
        "imageModel": image_primary,
        "imageFallbacks": image_fallbacks,
        "allowlist": allowlist,
        "providers": provider_status,
        "backupCount": backup_count,
        "issues": issues,
        "registryModels": list(registry.get("models", {}).keys()),
        "timestamp": __import__("datetime").datetime.now().isoformat()
    }


# ── CLI Interface ──────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: validate.py <command> [args]"}, indent=2))
        sys.exit(1)

    command = sys.argv[1]

    if command == "ref":
        # Validate a model reference format
        model = sys.argv[2] if len(sys.argv) > 2 else ""
        valid, msg = validate_model_ref(model)
        result = {"valid": valid, "message": msg, "model": model}
        print(json.dumps(result, indent=2))
        sys.exit(0 if valid else 1)

    elif command == "role":
        # Validate model + role compatibility
        model = sys.argv[2] if len(sys.argv) > 2 else ""
        role = sys.argv[3] if len(sys.argv) > 3 else "primary"
        valid, msg, suggestion = validate_role_compatibility(model, role)
        result = {"valid": valid, "message": msg, "model": model, "role": role}
        if suggestion:
            result["suggestion"] = suggestion
        print(json.dumps(result, indent=2))
        sys.exit(0 if valid else 1)

    elif command == "config":
        # Validate current config
        config = load_config()
        issues = validate_config_schema(config)
        result = {"valid": len([i for i in issues if i["level"] == "error"]) == 0, "issues": issues}
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["valid"] else 1)

    elif command == "auth":
        # Check provider auth
        provider = sys.argv[2] if len(sys.argv) > 2 else ""
        has_auth, msg = check_provider_auth(provider)
        result = {"provider": provider, "hasAuth": has_auth, "message": msg}
        print(json.dumps(result, indent=2))
        sys.exit(0 if has_auth else 1)

    elif command == "dry-run":
        # Generate dry-run diff
        action = sys.argv[2] if len(sys.argv) > 2 else ""
        model = sys.argv[3] if len(sys.argv) > 3 else ""
        role = sys.argv[4] if len(sys.argv) > 4 else "primary"
        diff = generate_dry_run_diff(action, model, role)
        print(json.dumps(diff, indent=2))

    elif command == "status":
        # Full status for UI
        status = get_full_status()
        print(json.dumps(status, indent=2))

    elif command == "validate-cron-models":
        result = validate_cron_models()
        print(json.dumps(result, indent=2))
        sys.exit(0 if not any(i["level"] == "error" for i in result.get("issues", [])) else 1)

    elif command == "recommend":
        # Recommend models for each role based on available providers
        registry = load_registry(strict=False)
        recommendations = {}
        for role_id, role_info in registry.get("roles", {}).items():
            required = set(role_info.get("requiredCapabilities", []))
            preferred_cost = role_info.get("preferCostTier", [])
            candidates = []
            for mid, minfo in registry.get("models", {}).items():
                if minfo.get("blocked"):
                    continue
                if role_id not in minfo.get("safeRoles", []):
                    continue
                caps = set(minfo.get("capabilities", []))
                if required.issubset(caps):
                    # Check if provider has auth
                    provider = mid.split("/")[0]
                    has_auth, _ = check_provider_auth(provider)
                    score = 0
                    if has_auth:
                        score += 100
                    cost = minfo.get("costTier", "medium")
                    if preferred_cost and cost in preferred_cost:
                        score += 50
                    recommended_caps = set(role_info.get("recommendedCapabilities", []))
                    score += len(caps & recommended_caps) * 10
                    candidates.append({
                        "model": mid,
                        "displayName": minfo.get("displayName", mid),
                        "costTier": cost,
                        "hasAuth": has_auth,
                        "score": score
                    })
            candidates.sort(key=lambda x: x["score"], reverse=True)
            recommendations[role_id] = {
                "role": role_info.get("displayName", role_id),
                "candidates": candidates[:5]
            }
        print(json.dumps(recommendations, indent=2))

    else:
        print(json.dumps({"error": f"Unknown command: {command}. Use: ref, role, config, auth, dry-run, status, recommend"}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
