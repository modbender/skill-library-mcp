#!/usr/bin/env python3
"""Apify actor runner for Twitter/X followers + optional email enrichment."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from dataclasses import dataclass
from typing import Any

try:
    import requests
except ModuleNotFoundError:
    requests = None

FOLLOWER_ACTOR_DEFAULT = "bIYXeMcKISYGnHhBG"
EMAIL_ACTOR_DEFAULT = "mSaHt2tt3Z7Fcwf0o"
APIFY_BASE = "https://api.apify.com/v2/acts"


class SkillError(Exception):
    pass


@dataclass
class Config:
    token: str
    follower_actor_id: str = FOLLOWER_ACTOR_DEFAULT
    email_actor_id: str = EMAIL_ACTOR_DEFAULT


def utc_now_iso() -> str:
    return dt.datetime.now(dt.UTC).isoformat()


def parse_username(target: str) -> str:
    s = (target or "").strip()
    if not s:
        raise SkillError("Target is empty")

    if "twitter.com" not in s and "x.com" not in s:
        return s.replace("@", "").strip()

    m = re.search(r"(?:x|twitter)\.com/([A-Za-z0-9_]+)", s, flags=re.IGNORECASE)
    if not m:
        raise SkillError(f"Could not parse username from target: {target}")
    return m.group(1)


def require_token(explicit: str | None) -> str:
    token = explicit or os.getenv("APIFY_TOKEN", "")
    if not token:
        raise SkillError("Apify token missing. Pass --apify-token or set APIFY_TOKEN.")
    return token


def run_actor_sync(actor_id: str, token: str, payload: dict[str, Any], timeout_sec: int = 600) -> list[dict[str, Any]]:
    if requests is None:
        raise SkillError("Missing dependency: requests. Install with `pip install requests`.")

    url = f"{APIFY_BASE}/{actor_id}/run-sync-get-dataset-items"
    params = {"token": token, "format": "json", "clean": "true"}
    resp = requests.post(url, params=params, json=payload, timeout=timeout_sec)

    if resp.status_code >= 400:
        raise SkillError(f"Actor {actor_id} failed: HTTP {resp.status_code} - {resp.text[:500]}")

    data = resp.json()
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if isinstance(data.get("data"), list):
            return data["data"]
        return [data]
    return []


def build_follower_input(username: str, collect_type: str, limit: int) -> dict[str, Any]:
    collect_type = collect_type.lower().strip()
    if collect_type not in {"followers", "following", "both"}:
        raise SkillError("collectType must be one of: followers, following, both")
    if limit < 1:
        raise SkillError("limit must be >= 1")

    get_followers = collect_type in {"followers", "both"}
    get_following = collect_type in {"following", "both"}

    return {
        "userNameList": [username],
        "userIdList": [],
        "maxFollowers": limit if get_followers else 1,
        "maxFollowing": limit if get_following else 1,
        "getFollowers": get_followers,
        "getFollowing": get_following,
        "outputMode": "usernames",
    }


def normalize_usernames(raw_rows: list[dict[str, Any]], target_username: str, collect_type: str, limit: int) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []

    for row in raw_rows:
        username = str(
            row.get("username")
            or row.get("screenname")
            or row.get("userName")
            or row.get("handle")
            or row.get("value")
            or ""
        ).replace("@", "").strip()

        if not username:
            continue

        key = username.lower()
        if key in seen:
            continue
        seen.add(key)

        out.append(
            {
                "targetUsername": target_username,
                "username": username,
                "sourceType": collect_type,
                "collectedAt": utc_now_iso(),
            }
        )

        if len(out) >= limit:
            break

    return out


def build_email_input(rows: list[dict[str, Any]], limit: int) -> dict[str, Any]:
    usernames = [r["username"] for r in rows if r.get("username")]
    return {
        "usernames": "\n".join(usernames),
        "max_results": limit,
    }


def merge_email_rows(base_rows: list[dict[str, Any]], email_rows_raw: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    by_username: dict[str, dict[str, str]] = {}
    for row in email_rows_raw:
        key = str(row.get("screenname") or row.get("username") or "").replace("@", "").strip().lower()
        if not key:
            continue
        by_username[key] = {
            "name": str(row.get("name") or ""),
            "email": str(row.get("email") or ""),
        }

    merged: list[dict[str, Any]] = []
    found = 0
    for row in base_rows:
        hit = by_username.get(row["username"].lower(), {"name": "", "email": ""})
        item = {**row, "name": hit["name"], "email": hit["email"]}
        if item["email"]:
            found += 1
        merged.append(item)

    return merged, found


def run_followers(cfg: Config, target: str, collect_type: str, limit: int) -> dict[str, Any]:
    target_username = parse_username(target)
    follower_input = build_follower_input(target_username, collect_type, limit)
    raw = run_actor_sync(cfg.follower_actor_id, cfg.token, follower_input)
    rows = normalize_usernames(raw, target_username, collect_type, limit)

    return {
        "ok": True,
        "targetUsername": target_username,
        "collectType": collect_type,
        "limit": limit,
        "rows": rows,
        "recordsCount": len(rows),
    }


def run_pipeline(cfg: Config, target: str, collect_type: str, limit: int, include_emails: bool) -> dict[str, Any]:
    base = run_followers(cfg, target, collect_type, limit)
    rows = base["rows"]

    if not include_emails:
        final_rows = [{**r, "name": "", "email": ""} for r in rows]
        return {
            "ok": True,
            "targetUsername": base["targetUsername"],
            "collectType": collect_type,
            "includeEmails": False,
            "totalCollected": len(final_rows),
            "emailsFound": 0,
            "rows": final_rows,
        }

    email_input = build_email_input(rows, limit)
    email_raw = run_actor_sync(cfg.email_actor_id, cfg.token, email_input)
    final_rows, emails_found = merge_email_rows(rows, email_raw)

    return {
        "ok": True,
        "targetUsername": base["targetUsername"],
        "collectType": collect_type,
        "includeEmails": True,
        "totalCollected": len(final_rows),
        "emailsFound": emails_found,
        "rows": final_rows,
    }


def cmd_parse_username(args: argparse.Namespace) -> int:
    print(parse_username(args.target))
    return 0


def cmd_run_followers(args: argparse.Namespace) -> int:
    token = require_token(args.apify_token)
    cfg = Config(token=token, follower_actor_id=args.follower_actor_id, email_actor_id=args.email_actor_id)
    result = run_followers(cfg, args.target, args.collect_type, args.limit)
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


def cmd_run_pipeline(args: argparse.Namespace) -> int:
    token = require_token(args.apify_token)
    cfg = Config(token=token, follower_actor_id=args.follower_actor_id, email_actor_id=args.email_actor_id)
    result = run_pipeline(cfg, args.target, args.collect_type, args.limit, args.include_emails)
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Twitter/X Apify actors for followers + optional emails.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_user = sub.add_parser("parse-username", help="Extract username from x.com/twitter.com link or @username")
    p_user.add_argument("--target", required=True)
    p_user.set_defaults(func=cmd_parse_username)

    common = {
        "apify-token": {"help": "Apify API token (fallback: APIFY_TOKEN env)"},
        "target": {"required": True, "help": "Twitter/X profile URL or @username"},
        "collect-type": {"default": "followers", "choices": ["followers", "following", "both"]},
        "limit": {"type": int, "default": 1000},
        "follower-actor-id": {"default": FOLLOWER_ACTOR_DEFAULT},
        "email-actor-id": {"default": EMAIL_ACTOR_DEFAULT},
    }

    p_follow = sub.add_parser("run-followers", help="Run follower/following actor and return normalized usernames")
    p_follow.add_argument("--apify-token", **common["apify-token"])
    p_follow.add_argument("--target", **common["target"])
    p_follow.add_argument("--collect-type", **common["collect-type"])
    p_follow.add_argument("--limit", **common["limit"])
    p_follow.add_argument("--follower-actor-id", **common["follower-actor-id"])
    p_follow.add_argument("--email-actor-id", **common["email-actor-id"])
    p_follow.set_defaults(func=cmd_run_followers)

    p_pipe = sub.add_parser("run-pipeline", help="Run followers actor + optional email enrichment")
    p_pipe.add_argument("--apify-token", **common["apify-token"])
    p_pipe.add_argument("--target", **common["target"])
    p_pipe.add_argument("--collect-type", **common["collect-type"])
    p_pipe.add_argument("--limit", **common["limit"])
    p_pipe.add_argument("--include-emails", action="store_true")
    p_pipe.add_argument("--follower-actor-id", **common["follower-actor-id"])
    p_pipe.add_argument("--email-actor-id", **common["email-actor-id"])
    p_pipe.set_defaults(func=cmd_run_pipeline)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except SkillError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    except Exception as exc:
        if requests is not None and isinstance(exc, requests.RequestException):
            print(json.dumps({"ok": False, "error": f"Network error: {exc}"}), file=sys.stderr)
            return 3
        raise


if __name__ == "__main__":
    raise SystemExit(main())
