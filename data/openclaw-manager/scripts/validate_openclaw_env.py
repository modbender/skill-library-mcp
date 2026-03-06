#!/usr/bin/env python3
"""Validate OpenClaw env files for profile-aware deployment readiness."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PLACEHOLDER_PATTERNS = (
    "changeme",
    "todo",
    "your-key",
    "your_token",
    "example",
    "replace-me",
    "placeholder",
)

KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
HEX_RE = re.compile(r"^[0-9a-fA-F]+$")

PROFILE_CONFIG = {
    "local": {
        "required": ["OPENCLAW_GATEWAY_TOKEN"],
        "require_any": [["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]],
        "recommended": [],
    },
    "hosted-fly": {
        "required": ["OPENCLAW_GATEWAY_TOKEN"],
        "require_any": [["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]],
        "recommended": ["FLY_API_TOKEN"],
    },
    "hosted-render": {
        "required": ["OPENCLAW_GATEWAY_TOKEN"],
        "require_any": [["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]],
        "recommended": ["RENDER_API_KEY"],
    },
    "hosted-railway": {
        "required": ["OPENCLAW_GATEWAY_TOKEN"],
        "require_any": [["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]],
        "recommended": ["RAILWAY_TOKEN"],
    },
    "hosted-hetzner": {
        "required": ["OPENCLAW_GATEWAY_TOKEN"],
        "require_any": [["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]],
        "recommended": ["HCLOUD_TOKEN"],
    },
    "hosted-gcp": {
        "required": ["OPENCLAW_GATEWAY_TOKEN"],
        "require_any": [["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]],
        "recommended": ["GCP_SERVICE_ACCOUNT_JSON", "GOOGLE_APPLICATION_CREDENTIALS"],
    },
}


def parse_env(env_path: Path):
    values: dict[str, str] = {}
    duplicates: list[str] = []
    malformed: list[tuple[int, str]] = []

    for idx, raw_line in enumerate(env_path.read_text().splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            malformed.append((idx, raw_line))
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if not KEY_RE.match(key):
            malformed.append((idx, raw_line))
            continue

        if key in values:
            duplicates.append(key)

        values[key] = value

    return values, duplicates, malformed


def is_placeholder(value: str) -> bool:
    lowered = value.lower()
    return any(pattern in lowered for pattern in PLACEHOLDER_PATTERNS)


def parse_require_any(values: list[str]) -> list[list[str]]:
    groups: list[list[str]] = []
    for raw in values:
        parts = [part.strip() for part in raw.split(",") if part.strip()]
        if len(parts) < 2:
            raise ValueError("--require-any must include at least two comma-separated keys")
        groups.append(parts)
    return groups


def check_secret_strength(values: dict[str, str]):
    weak: list[str] = []

    gateway = values.get("OPENCLAW_GATEWAY_TOKEN", "")
    if gateway:
        if len(gateway) < 32:
            weak.append("OPENCLAW_GATEWAY_TOKEN (too short; expected >=32 chars)")
        elif HEX_RE.match(gateway) and len(gateway) < 64:
            weak.append("OPENCLAW_GATEWAY_TOKEN (hex token shorter than 64 chars)")

    for key, value in values.items():
        if not value:
            continue

        lowered = key.lower()
        sensitive = any(token in lowered for token in ["token", "secret", "password", "api_key"])
        if sensitive and len(value) < 16:
            weak.append(f"{key} (too short for sensitive credential)")

    return sorted(set(weak))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate .env file for OpenClaw deployments")
    parser.add_argument("--env-file", required=True, help="Path to .env file")
    parser.add_argument(
        "--profile",
        required=True,
        choices=sorted(PROFILE_CONFIG),
        help="Validation profile (local or hosted provider profile)",
    )
    parser.add_argument(
        "--require",
        action="append",
        default=[],
        help="Additional required key (can be passed multiple times)",
    )
    parser.add_argument(
        "--require-any",
        action="append",
        default=[],
        help="Additional key group requirement; pass as comma-separated list (e.g. A,B)",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")
    args = parser.parse_args()

    env_path = Path(args.env_file)
    if not env_path.exists():
        payload = {"ok": False, "errors": [f"Env file not found: {env_path}"]}
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(f"[ERROR] Env file not found: {env_path}")
        return 1

    values, duplicates, malformed = parse_env(env_path)
    normalized = values

    profile = PROFILE_CONFIG[args.profile]
    required_keys = sorted(set(profile["required"] + args.require))

    try:
        dynamic_require_any = parse_require_any(args.require_any)
    except ValueError as err:
        if args.json:
            print(json.dumps({"ok": False, "errors": [str(err)]}, indent=2))
        else:
            print(f"[ERROR] {err}")
        return 1

    require_any_groups = profile["require_any"] + dynamic_require_any

    missing_required = [key for key in required_keys if key not in normalized or not normalized[key]]
    missing_any_groups: list[list[str]] = []
    for group in require_any_groups:
        if not any(normalized.get(key) for key in group):
            missing_any_groups.append(group)

    placeholders = [key for key, value in normalized.items() if value and is_placeholder(value)]
    weak_secrets = check_secret_strength(normalized)

    recommended_missing = [
        key for key in profile.get("recommended", []) if key not in normalized or not normalized[key]
    ]

    errors = []
    warnings = []

    if malformed:
        errors.append("malformed env lines detected")
    if duplicates:
        errors.append("duplicate env keys detected")
    if missing_required:
        errors.append("required keys missing")
    if missing_any_groups:
        errors.append("required alternative key groups unsatisfied")
    if placeholders:
        errors.append("placeholder values detected")
    if weak_secrets:
        errors.append("weak secrets detected")

    if recommended_missing:
        warnings.append(
            "recommended keys missing for profile: " + ", ".join(recommended_missing)
        )

    payload = {
        "ok": len(errors) == 0,
        "profile": args.profile,
        "parsed_keys": len(normalized),
        "required_keys": required_keys,
        "missing_required": missing_required,
        "require_any_groups": require_any_groups,
        "missing_require_any_groups": missing_any_groups,
        "malformed_lines": [{"line": line_no, "content": line} for line_no, line in malformed],
        "duplicate_keys": sorted(set(duplicates)),
        "placeholder_keys": sorted(placeholders),
        "weak_secrets": weak_secrets,
        "warnings": warnings,
        "errors": errors,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Parsed keys (normalized): {payload['parsed_keys']}")

        if malformed:
            print("\nMalformed lines:")
            for line_no, line in malformed:
                print(f"  - line {line_no}: {line}")

        if duplicates:
            print("\nDuplicate keys:")
            for key in sorted(set(duplicates)):
                print(f"  - {key}")

        if missing_required:
            print("\nMissing required keys:")
            for key in missing_required:
                print(f"  - {key}")

        if missing_any_groups:
            print("\nUnsatisfied required key groups (need at least one key from each):")
            for group in missing_any_groups:
                print(f"  - {', '.join(group)}")

        if placeholders:
            print("\nPotential placeholder values:")
            for key in sorted(placeholders):
                print(f"  - {key}")

        if weak_secrets:
            print("\nWeak secret checks:")
            for issue in weak_secrets:
                print(f"  - {issue}")

        if warnings:
            print("\nWarnings:")
            for warning in warnings:
                print(f"  - {warning}")

        if payload["ok"]:
            print("\n[OK] Env validation passed.")
        else:
            print("\n[FAIL] Env validation failed.")

    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
