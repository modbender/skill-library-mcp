#!/usr/bin/env python3
"""Run LinkedIn email + phone enrichment pipeline via two Apify actors."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List

PHONE_ACTOR_ID = "X95BXRaFOqZ7rzjxM"
EMAIL_ACTOR_ID = "q3wko0Sbx6ZAAB2xf"
DEFAULT_TIMEOUT_SEC = 1800


class SkillError(Exception):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_bool(value: Any, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return default


def normalize_linkedin_url(value: str) -> str:
    text = value.strip()
    if not text:
        return ""
    if not re.match(r"^https?://", text, flags=re.IGNORECASE):
        text = f"https://{text}"
    text = re.sub(r"^https?://(www\.)?", "https://", text, flags=re.IGNORECASE)
    text = text.split("?", 1)[0].split("#", 1)[0].rstrip("/")
    m = re.search(r"linkedin\.com/in/([^/]+)", text, flags=re.IGNORECASE)
    if m:
        return f"https://linkedin.com/in/{m.group(1)}"
    return text


def resolve_token(explicit: str | None) -> str:
    token = explicit or os.getenv("APIFY_TOKEN", "")
    if not token:
        raise SkillError("Apify token missing. Pass --apify-token or set APIFY_TOKEN.")
    return token


def read_input(args: argparse.Namespace) -> Dict[str, Any]:
    if args.input_json:
        try:
            payload = json.loads(args.input_json)
        except json.JSONDecodeError as exc:
            raise SkillError(f"Invalid --input-json: {exc}") from exc
    elif args.input_file:
        try:
            with open(args.input_file, "r", encoding="utf-8") as fh:
                payload = json.load(fh)
        except OSError as exc:
            raise SkillError(f"Cannot read --input-file: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise SkillError(f"Invalid JSON in --input-file: {exc}") from exc
    else:
        raise SkillError("Provide --input-json or --input-file.")

    if not isinstance(payload, dict):
        raise SkillError("Input payload must be a JSON object.")
    return payload


def build_config(payload: Dict[str, Any]) -> Dict[str, Any]:
    urls = payload.get("linkedinUrls")
    if not isinstance(urls, list) or not urls:
        raise SkillError("linkedinUrls must be a non-empty array.")

    normalized_urls: List[str] = []
    seen = set()
    for item in urls:
        if not isinstance(item, str):
            continue
        normalized = normalize_linkedin_url(item)
        if normalized and normalized not in seen:
            seen.add(normalized)
            normalized_urls.append(normalized)

    if not normalized_urls:
        raise SkillError("No valid LinkedIn URLs after normalization.")

    include_emails = parse_bool(payload.get("includeEmails"), True)
    include_phones = parse_bool(payload.get("includePhones"), True)
    if not include_emails and not include_phones:
        raise SkillError("At least one branch must be enabled: includeEmails or includePhones.")

    return {
        "linkedinUrls": normalized_urls,
        "includeEmails": include_emails,
        "includePhones": include_phones,
        "includeWorkEmails": parse_bool(payload.get("includeWorkEmails"), True),
        "includePersonalEmails": parse_bool(payload.get("includePersonalEmails"), True),
        "onlyWithEmails": parse_bool(payload.get("onlyWithEmails"), True),
        "onlyWithPhones": parse_bool(payload.get("onlyWithPhones"), True),
    }


def run_actor(token: str, actor_id: str, actor_input: Dict[str, Any], timeout_sec: int) -> List[Dict[str, Any]]:
    base_url = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items"
    params = {"token": token, "timeout": timeout_sec, "clean": "true"}
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url=url,
        data=json.dumps(actor_input).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=min(timeout_sec + 30, 3600)) as response:
            status_code = getattr(response, "status", 200)
            raw = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        raise SkillError(f"Apify API error for actor {actor_id} ({exc.code}): {text[:1000]}") from exc
    except urllib.error.URLError as exc:
        raise SkillError(f"Network error for actor {actor_id}: {exc}") from exc

    if status_code >= 400:
        raise SkillError(f"Apify API error for actor {actor_id} ({status_code}): {raw[:1000]}")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SkillError(f"Invalid JSON response from actor {actor_id}.") from exc
    if not isinstance(data, list):
        raise SkillError(f"Expected array output from actor {actor_id}.")
    return [row for row in data if isinstance(row, dict)]


def build_key(row: Dict[str, Any]) -> str:
    value = row.get("linkedin_url") or row.get("linkedinUrl") or ""
    if not isinstance(value, str):
        value = ""
    normalized = normalize_linkedin_url(value)
    if normalized:
        return normalized
    # Fallback by LinkedIn handle if present
    username = row.get("linkedin_username") or row.get("linkedinUsername")
    if isinstance(username, str) and username.strip():
        return f"https://linkedin.com/in/{username.strip()}"
    return ""


def merge_rows(email_rows: List[Dict[str, Any]], phone_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    merged: Dict[str, Dict[str, Any]] = {}

    for row in email_rows:
        key = build_key(row)
        if not key:
            continue
        merged[key] = {
            "linkedin_url": key,
            "full_name": row.get("full_name"),
            "first_name": row.get("first_name"),
            "last_name": row.get("last_name"),
            "job_title": row.get("job_title"),
            "company": row.get("company"),
            "work_email": row.get("work_email"),
            "personal_emails": row.get("personal_emails"),
            "personal_emails_count": row.get("personal_emails_count"),
            "has_email": row.get("has_email"),
            "mobile_phone": None,
            "has_phone": False,
        }

    for row in phone_rows:
        key = build_key(row)
        if not key:
            continue
        current = merged.get(key, {
            "linkedin_url": key,
            "full_name": row.get("full_name"),
            "first_name": row.get("first_name"),
            "last_name": row.get("last_name"),
            "job_title": row.get("job_title"),
            "company": row.get("company"),
            "work_email": None,
            "personal_emails": None,
            "personal_emails_count": None,
            "has_email": False,
            "mobile_phone": None,
            "has_phone": False,
        })
        if not current.get("full_name"):
            current["full_name"] = row.get("full_name")
        if not current.get("first_name"):
            current["first_name"] = row.get("first_name")
        if not current.get("last_name"):
            current["last_name"] = row.get("last_name")
        if not current.get("job_title"):
            current["job_title"] = row.get("job_title")
        if not current.get("company"):
            current["company"] = row.get("company")
        current["mobile_phone"] = row.get("mobile_phone")
        current["has_phone"] = row.get("has_phone")
        merged[key] = current

    return list(merged.values())


def run_pipeline(token: str, cfg: Dict[str, Any], timeout_sec: int) -> Dict[str, Any]:
    phone_rows: List[Dict[str, Any]] = []
    email_rows: List[Dict[str, Any]] = []

    if cfg["includePhones"]:
        phone_input = {
            "linkedinUrls": cfg["linkedinUrls"],
            "onlyWithPhones": cfg["onlyWithPhones"],
        }
        phone_rows = run_actor(token, PHONE_ACTOR_ID, phone_input, timeout_sec)

    if cfg["includeEmails"]:
        email_input = {
            "linkedinUrls": cfg["linkedinUrls"],
            "includeWorkEmails": cfg["includeWorkEmails"],
            "includePersonalEmails": cfg["includePersonalEmails"],
            "onlyWithEmails": cfg["onlyWithEmails"],
        }
        email_rows = run_actor(token, EMAIL_ACTOR_ID, email_input, timeout_sec)

    merged = merge_rows(email_rows, phone_rows)
    return {
        "ok": True,
        "fetchedAt": utc_now(),
        "actors": {
            "phoneActorId": PHONE_ACTOR_ID,
            "emailActorId": EMAIL_ACTOR_ID,
        },
        "inputSummary": {
            "urlsRequested": len(cfg["linkedinUrls"]),
            "includeEmails": cfg["includeEmails"],
            "includePhones": cfg["includePhones"],
            "onlyWithEmails": cfg["onlyWithEmails"],
            "onlyWithPhones": cfg["onlyWithPhones"],
        },
        "counts": {
            "emailRows": len(email_rows),
            "phoneRows": len(phone_rows),
            "mergedRows": len(merged),
        },
        "rows": merged,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="LinkedIn email + phone enrichment via Apify")
    sub = parser.add_subparsers(dest="command", required=True)

    run_cmd = sub.add_parser("run", help="Run combined pipeline")
    run_cmd.add_argument("--apify-token", help="Apify API token (fallback: APIFY_TOKEN env)")
    run_cmd.add_argument("--timeout-sec", type=int, default=DEFAULT_TIMEOUT_SEC)
    run_cmd.add_argument("--input-json", help="Inline JSON payload")
    run_cmd.add_argument("--input-file", help="Path to JSON payload file")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        token = resolve_token(getattr(args, "apify_token", None))
        timeout_sec = int(getattr(args, "timeout_sec", DEFAULT_TIMEOUT_SEC))
        if timeout_sec <= 0:
            raise SkillError("--timeout-sec must be > 0.")

        payload = read_input(args)
        cfg = build_config(payload)
        result = run_pipeline(token, cfg, timeout_sec)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except SkillError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
