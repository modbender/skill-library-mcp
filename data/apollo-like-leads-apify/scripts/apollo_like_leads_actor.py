#!/usr/bin/env python3
"""Run Apify actor LurATYM4hkEo78GVj for Apollo-like B2B leads collection."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict

DEFAULT_ACTOR_ID = "LurATYM4hkEo78GVj"
DEFAULT_TIMEOUT_SEC = 1800
VALID_SENIORITY = {
    "owner",
    "cxo",
    "partner",
    "vp",
    "director",
    "manager",
    "senior",
    "entry",
    "training",
    "unpaid",
}


class SkillError(Exception):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_token(explicit: str | None) -> str:
    token = explicit or os.getenv("APIFY_TOKEN", "")
    if not token:
        raise SkillError("Apify token missing. Pass --apify-token or set APIFY_TOKEN.")
    return token


def parse_input(args: argparse.Namespace) -> Dict[str, Any]:
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

    max_results = payload.get("max_results")
    if max_results is not None:
        try:
            max_results = int(max_results)
        except (TypeError, ValueError) as exc:
            raise SkillError("max_results must be an integer.") from exc
        if max_results <= 0:
            raise SkillError("max_results must be > 0.")
        payload["max_results"] = max_results

    return normalize_payload(payload)


def quick_founders_us_50_payload() -> Dict[str, Any]:
    return {
        "max_results": 50,
        "job_titles": ["Founder", "Co-Founder", "CEO"],
        "job_title_seniority": ["owner", "cxo"],
        "person_location_country": ["United States"],
        "employee_size": ["1-10", "11-50", "51-200"],
        "email_status": "verified",
        "include_emails": True,
        "include_phones": False,
    }


def normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    # Accept Apollo-style aliases and map them to actor-native fields.
    aliases = {
        "personTitleIncludes": "job_titles",
        "seniorityIncludes": "job_title_seniority",
        "personLocationCityIncludes": "person_location_locality",
        "personLocationStateIncludes": "person_location_region",
        "personLocationCountryIncludes": "person_location_country",
        "companyLocationCityIncludes": "company_location_locality",
        "companyLocationStateIncludes": "company_location_region",
        "companyLocationCountryIncludes": "company_location_country",
        "hasEmail": "include_emails",
        "hasPhone": "include_phones",
        "emailStatus": "email_status",
    }
    for src, dst in aliases.items():
        if src in payload and dst not in payload:
            payload[dst] = payload.pop(src)

    # Normalize seniority values to actor-supported enum.
    raw_seniority = payload.get("job_title_seniority")
    if isinstance(raw_seniority, list):
        normalized: list[str] = []
        for value in raw_seniority:
            if not isinstance(value, str):
                continue
            v = value.strip().lower()
            if v in {"founder", "co-founder", "cofounder"}:
                v = "owner"
            if v in VALID_SENIORITY:
                normalized.append(v)
        if normalized:
            payload["job_title_seniority"] = sorted(set(normalized))
        else:
            payload.pop("job_title_seniority", None)

    return payload


def run_actor(token: str, actor_id: str, payload: Dict[str, Any], timeout_sec: int) -> Dict[str, Any]:
    base_url = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items"
    params = {
        "token": token,
        "timeout": timeout_sec,
        "clean": "true",
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url=url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=min(timeout_sec + 30, 3600)) as response:
            raw = response.read().decode("utf-8", errors="replace")
            status_code = getattr(response, "status", 200)
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        raise SkillError(f"Apify API error {exc.code}: {text[:1000]}") from exc
    except urllib.error.URLError as exc:
        raise SkillError(f"Network error calling Apify: {exc}") from exc

    if status_code >= 400:
        raise SkillError(f"Apify API error {status_code}: {raw[:1000]}")

    try:
        rows = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SkillError("Apify response is not valid JSON.") from exc

    if not isinstance(rows, list):
        raise SkillError("Expected actor output as JSON array.")

    return {
        "ok": True,
        "actorId": actor_id,
        "fetchedAt": utc_now(),
        "leadsCount": len(rows),
        "inputUsed": payload,
        "rows": rows,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Apollo-like B2B leads actor on Apify")
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--apify-token", help="Apify API token (fallback: APIFY_TOKEN env)")
    common.add_argument("--actor-id", default=DEFAULT_ACTOR_ID, help="Apify actor ID")
    common.add_argument("--timeout-sec", type=int, default=DEFAULT_TIMEOUT_SEC, help="Run timeout in seconds")

    run_cmd = sub.add_parser("run", parents=[common], help="Run with custom payload")
    run_cmd.add_argument("--input-json", help="Inline JSON payload")
    run_cmd.add_argument("--input-file", help="Path to JSON payload file")

    sub.add_parser("quick-founders-us-50", parents=[common], help="Run preset payload")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        token = resolve_token(getattr(args, "apify_token", None))
        actor_id = getattr(args, "actor_id", DEFAULT_ACTOR_ID)
        timeout_sec = int(getattr(args, "timeout_sec", DEFAULT_TIMEOUT_SEC))
        if timeout_sec <= 0:
            raise SkillError("--timeout-sec must be > 0.")

        if args.command == "quick-founders-us-50":
            payload = quick_founders_us_50_payload()
        else:
            payload = parse_input(args)

        result = run_actor(token, actor_id, payload, timeout_sec)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except SkillError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
