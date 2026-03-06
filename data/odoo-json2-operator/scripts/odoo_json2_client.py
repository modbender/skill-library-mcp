#!/usr/bin/env python3
"""Odoo JSON-2 API client with discovery and local connection profiles.

Examples:
  # Save a connection profile
  python scripts/odoo_json2_client.py --save-profile odoo19c \
    --base-url https://odoo19c.example.com --database odoo19c --api-key YOUR_KEY

  # List saved profiles
  python scripts/odoo_json2_client.py --list-profiles

  # Discover models with a saved profile
  python scripts/odoo_json2_client.py --profile odoo19c --discover-index

  # Execute model method with a saved profile
  python scripts/odoo_json2_client.py --profile odoo19c --model res.partner --method search_read \
    --payload '{"domain": [], "fields": ["name"], "limit": 5}'
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_TMP_DIR = SKILL_DIR / ".tmp"
PROFILE_FILE = SCRIPT_DIR / "connections.json"


def _configure_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")


def _load_profiles() -> dict[str, dict[str, str]]:
    if not PROFILE_FILE.exists():
        return {}
    with PROFILE_FILE.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    if not isinstance(raw, dict):
        return {}
    return {k: v for k, v in raw.items() if isinstance(v, dict)}


def _save_profiles(profiles: dict[str, dict[str, str]]) -> None:
    PROFILE_FILE.write_text(
        json.dumps(profiles, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def list_profiles() -> int:
    profiles = _load_profiles()
    print(f"Stored profiles: {len(profiles)}")
    for name in sorted(profiles):
        profile = profiles[name]
        base_url = profile.get("base_url", "")
        database = profile.get("database", "")
        print(f"- {name}: base_url={base_url}, database={database}")
    return 0


def save_profile(name: str, base_url: str, database: str, api_key: str) -> int:
    profiles = _load_profiles()
    profiles[name] = {
        "base_url": base_url.rstrip("/"),
        "database": database,
        "api_key": api_key,
    }
    _save_profiles(profiles)
    print(f"Profile saved: {name}")
    return 0


def delete_profile(name: str) -> int:
    profiles = _load_profiles()
    if name not in profiles:
        print(f"Profile not found: {name}")
        return 1
    profiles.pop(name)
    _save_profiles(profiles)
    print(f"Profile deleted: {name}")
    return 0


def resolve_connection(args: argparse.Namespace) -> tuple[str, str, str]:
    if args.profile:
        profiles = _load_profiles()
        if args.profile not in profiles:
            raise ValueError(f"Unknown profile: {args.profile}")
        profile = profiles[args.profile]
        base_url = profile.get("base_url")
        database = profile.get("database")
        api_key = profile.get("api_key")
    else:
        base_url = args.base_url
        database = args.database
        api_key = args.api_key

    if not base_url or not database or not api_key:
        raise ValueError("Connection requires base_url, database, and api_key.")

    return base_url.rstrip("/"), database, api_key


def build_exec_url(base_url: str, model: str, method: str) -> str:
    return f"{base_url}/json/2/{model}/{method}"


def build_doc_index_url(base_url: str) -> str:
    return f"{base_url}/doc-bearer/index.json"


def build_doc_model_url(base_url: str, model: str) -> str:
    return f"{base_url}/doc-bearer/{model}.json"


def resolve_payload_path(payload_file: str, tmp_dir: Path) -> Path:
    payload_path = Path(payload_file)
    if payload_path.is_absolute():
        return payload_path

    direct_path = payload_path.resolve()
    if direct_path.exists():
        return direct_path

    tmp_path = (tmp_dir / payload_path).resolve()
    if tmp_path.exists():
        return tmp_path

    return direct_path


def is_cleanup_candidate(path: Path, tmp_dir: Path) -> bool:
    if path.suffix.lower() != ".json":
        return False
    if path.name.startswith("tmp_"):
        return True
    try:
        path.relative_to(tmp_dir.resolve())
        return True
    except ValueError:
        return False


def load_payload(
    payload: str | None,
    payload_file: str | None,
    cleanup_tmp_payload_file: bool,
    tmp_dir: Path,
) -> tuple[dict[str, Any], Path | None]:
    if payload and payload_file:
        raise ValueError("Use either --payload or --payload-file, not both.")

    cleanup_file: Path | None = None
    if payload_file:
        payload_path = resolve_payload_path(payload_file, tmp_dir)
        with payload_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if cleanup_tmp_payload_file and is_cleanup_candidate(payload_path, tmp_dir):
            cleanup_file = payload_path
    elif payload:
        data = json.loads(payload)
    else:
        data = {}

    if not isinstance(data, dict):
        raise ValueError("Payload must be a JSON object.")
    return data, cleanup_file


def build_headers(api_key: str, database: str, include_content_type: bool = True) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {api_key}", "X-Odoo-Database": database}
    if include_content_type:
        headers["Content-Type"] = "application/json"
    return headers


def http_get_json(url: str, headers: dict[str, str]) -> tuple[int, str]:
    request = Request(url=url, headers=headers, method="GET")
    return http_request(request)


def http_post_json(url: str, headers: dict[str, str], payload: dict[str, Any]) -> tuple[int, str]:
    body = json.dumps(payload).encode("utf-8")
    request = Request(url=url, headers=headers, data=body, method="POST")
    return http_request(request)


def http_request(request: Request) -> tuple[int, str]:
    try:
        with urlopen(request, timeout=60) as response:
            raw = response.read().decode("utf-8", errors="replace")
            return response.status, raw
    except HTTPError as err:
        raw = err.read().decode("utf-8", errors="replace")
        return err.code, raw
    except URLError as err:
        raise RuntimeError(f"Network error: {err}") from err


def print_response(status: int, raw: str) -> None:
    print(f"HTTP {status}")
    try:
        parsed = json.loads(raw)
        print(json.dumps(parsed, indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        print(raw)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Call Odoo JSON-2 API and api_doc discovery endpoints.")

    parser.add_argument("--profile", help="Saved profile name from connections.json")
    parser.add_argument("--base-url", help="Odoo base URL, e.g. https://odoo.example.com")
    parser.add_argument("--database", help="Odoo database name")
    parser.add_argument("--api-key", help="Odoo API key (Bearer token)")

    parser.add_argument("--save-profile", help="Save or update profile name using base-url/database/api-key")
    parser.add_argument("--list-profiles", action="store_true", help="List local profiles")
    parser.add_argument("--delete-profile", help="Delete profile by name")

    parser.add_argument("--discover-index", action="store_true", help="GET /doc-bearer/index.json")
    parser.add_argument("--discover-model", help="GET /doc-bearer/<model>.json")

    parser.add_argument("--model", help="Model name, e.g. res.partner")
    parser.add_argument("--method", help="Method name, e.g. search_read")
    parser.add_argument("--payload", help="Inline JSON payload object")
    parser.add_argument("--payload-file", help="Path to JSON payload file")
    parser.add_argument(
        "--cleanup-tmp-payload-file",
        action="store_true",
        default=True,
        help="Auto-delete payload-file when file name matches tmp_*.json (default: enabled)",
    )
    parser.add_argument(
        "--keep-tmp-payload-file",
        action="store_true",
        help="Disable auto-delete for payload-file even when name matches tmp_*.json",
    )
    parser.add_argument(
        "--tmp-dir",
        default=str(DEFAULT_TMP_DIR),
        help="Temp directory for payload files (default: skills/odoo-json2-operator/.tmp)",
    )

    return parser.parse_args()


def run_discover_index(base_url: str, database: str, api_key: str) -> int:
    url = build_doc_index_url(base_url)
    headers = build_headers(api_key, database, include_content_type=False)
    status, raw = http_get_json(url, headers)
    print_response(status, raw)
    return 0 if 200 <= status < 300 else 1


def run_discover_model(base_url: str, database: str, api_key: str, model: str) -> int:
    url = build_doc_model_url(base_url, model)
    headers = build_headers(api_key, database, include_content_type=False)
    status, raw = http_get_json(url, headers)
    print_response(status, raw)
    return 0 if 200 <= status < 300 else 1


def run_execute(args: argparse.Namespace, base_url: str, database: str, api_key: str) -> int:
    if not args.model or not args.method:
        raise ValueError("Execution requires --model and --method.")

    tmp_dir = Path(args.tmp_dir).resolve()
    tmp_dir.mkdir(parents=True, exist_ok=True)
    cleanup_tmp_payload_file = args.cleanup_tmp_payload_file and not args.keep_tmp_payload_file
    payload, cleanup_file = load_payload(
        args.payload,
        args.payload_file,
        cleanup_tmp_payload_file,
        tmp_dir,
    )
    try:
        url = build_exec_url(base_url, args.model, args.method)
        headers = build_headers(api_key, database, include_content_type=True)
        status, raw = http_post_json(url, headers, payload)
        print_response(status, raw)
        return 0 if 200 <= status < 300 else 1
    finally:
        if cleanup_file and cleanup_file.exists():
            try:
                cleanup_file.unlink()
            except OSError as err:
                print(f"WARN: failed to remove temp payload file {cleanup_file}: {err}", file=sys.stderr)


def main() -> int:
    _configure_stdout()
    args = parse_args()

    try:
        if args.list_profiles:
            return list_profiles()

        if args.delete_profile:
            return delete_profile(args.delete_profile)

        if args.save_profile:
            if not args.base_url or not args.database or not args.api_key:
                raise ValueError("Saving profile requires --base-url, --database, and --api-key.")
            return save_profile(args.save_profile, args.base_url, args.database, args.api_key)

        base_url, database, api_key = resolve_connection(args)

        if args.discover_index:
            return run_discover_index(base_url, database, api_key)

        if args.discover_model:
            return run_discover_model(base_url, database, api_key, args.discover_model)

        return run_execute(args, base_url, database, api_key)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
