#!/usr/bin/env python3
"""Run SignalRadar Polymarket monitoring jobs.

Behavior:
- prints NO_REPLY when nothing should be pushed
- prints concise HIT summary when threshold events exist
- supports job modes: ai/crypto/geopolitics/watchlist-refresh
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config_utils import DEFAULT_CONFIG, deep_merge, load_json_config
from error_utils import emit_error

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore[assignment]


POLYMARKET_BASE_URL = "https://gamma-api.polymarket.com/markets"
POLYMARKET_PAGE_SIZE = 500
POLYMARKET_MAX_PAGES = 10  # 5000 markets max

CRYPTO_KEYWORDS = [
    "btc",
    "bitcoin",
    "eth",
    "ethereum",
    "crypto",
    "sol",
    "solana",
    "doge",
    "xrp",
    "altcoin",
]

GEOPOLITICS_KEYWORDS = [
    "ukraine",
    "russia",
    "israel",
    "gaza",
    "iran",
    "china",
    "taiwan",
    "war",
    "ceasefire",
    "election",
    "president",
    "nato",
    "tariff",
    "sanction",
]

AI_FALLBACK_KEYWORDS = [
    "openai",
    "anthropic",
    "claude",
    "gpt",
    "gemini",
    "deepseek",
    "xai",
    "grok",
    "llm",
    "ai model",
]
PAGE_NOTICE_RE = re.compile(r"\A```signalradar-page\n.*?\n```\n*", re.DOTALL)
WATCH_LEVELS = {"normal", "important"}
DIGEST_FREQUENCIES = {"off", "daily", "weekly", "biweekly"}


def default_workspace_root() -> str:
    env_root = os.environ.get("SIGNALRADAR_WORKSPACE_ROOT", "").strip()
    if env_root:
        return env_root
    try:
        script_root = Path(__file__).resolve().parent.parent.parent.parent
        if (script_root / "skills" / "signalradar" / "scripts").exists():
            return str(script_root)
    except Exception:
        pass
    return str(Path.cwd())


def fetch_json(url: str, timeout: int) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": "signalradar/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _parse_rows(payload: Any) -> list[dict[str, Any]] | None:
    rows: Any = payload
    if isinstance(rows, dict):
        for key in ["markets", "data", "items"]:
            if isinstance(rows.get(key), list):
                rows = rows[key]
                break
    if isinstance(rows, list):
        return [x for x in rows if isinstance(x, dict)]
    return None


def fetch_markets(timeout: int, retries: int = 2, backoff_seconds: float = 1.0) -> list[dict[str, Any]]:
    all_rows: list[dict[str, Any]] = []
    last_error = None
    for page in range(POLYMARKET_MAX_PAGES):
        offset = page * POLYMARKET_PAGE_SIZE
        url = f"{POLYMARKET_BASE_URL}?active=true&closed=false&limit={POLYMARKET_PAGE_SIZE}&offset={offset}"
        fetched = False
        for attempt in range(retries + 1):
            try:
                payload = fetch_json(url, timeout)
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                if attempt < retries:
                    time.sleep(backoff_seconds * (2**attempt))
                continue
            rows = _parse_rows(payload)
            if rows is not None:
                all_rows.extend(rows)
                fetched = True
                break
            last_error = ValueError(f"unexpected payload format at offset={offset}")
            break
        if not fetched:
            if page == 0:
                raise RuntimeError(f"failed to fetch markets: {last_error}")
            break  # partial fetch OK if we already have some pages
        if len(_parse_rows(payload) or []) < POLYMARKET_PAGE_SIZE:
            break  # last page
    return all_rows


def as_percent(value: Any) -> float | None:
    if value is None:
        return None
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    if v <= 1.0:
        return round(v * 100.0, 6)
    return round(v, 6)


def first_non_null(item: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        if key in item and item[key] is not None:
            return item[key]
    return None


def slugify(text: str) -> str:
    lowered = text.strip().lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    return lowered.strip("-") or "unknown"


def extract_probability(item: dict[str, Any]) -> float | None:
    val = first_non_null(
        item,
        [
            "probability",
            "current",
            "price",
            "lastPrice",
            "yesPrice",
            "lastTradePrice",
        ],
    )
    p = as_percent(val)
    if p is not None:
        return p
    outcome_prices = item.get("outcomePrices")
    if isinstance(outcome_prices, str) and outcome_prices.startswith("["):
        try:
            outcome_prices = json.loads(outcome_prices)
        except (json.JSONDecodeError, ValueError):
            outcome_prices = None
    if isinstance(outcome_prices, list) and outcome_prices:
        return as_percent(outcome_prices[0])
    return None


def extract_volume(item: dict[str, Any]) -> float:
    val = first_non_null(
        item,
        ["volume_24h", "volume24h", "volume", "liquidity", "oneDayVolume", "volumeNum"],
    )
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def normalize_item(item: dict[str, Any]) -> dict[str, Any] | None:
    market_id = first_non_null(item, ["id", "market_id", "marketId", "conditionId"])
    question = first_non_null(item, ["question", "title", "name"])
    if market_id is None or not question:
        return None
    probability = extract_probability(item)
    if probability is None:
        return None

    event_id = str(
        first_non_null(item, ["event_id", "eventId", "event", "parentEvent", "eventSlug", "id"]) or market_id
    )
    status = str(first_non_null(item, ["status", "state"]) or "active")
    if "active" in item and item.get("active") is False:
        status = "inactive"
    end_date = first_non_null(item, ["endDate", "end_date", "closeTime", "endDateIso"])

    return {
        "source": "polymarket",
        "market_id": str(market_id),
        "event_id": str(event_id),
        "slug": str(item.get("slug") or slugify(str(question))),
        "question": str(question),
        "probability": probability,
        "volume_24h": extract_volume(item),
        "status": status.lower(),
        "end_date": end_date,
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def norm_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_ai_watchlist_questions(path: Path) -> set[str]:
    if not path.exists():
        return set()
    keep_categories = {"ai releases", "ai leaders", "openai ipo"}
    out: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 2:
            continue
        category = parts[0].lower()
        question = parts[1]
        if category in keep_categories and question and question.lower() != "问题":
            out.add(norm_text(question))
    return out


def normalize_watch_level(raw: str) -> str:
    v = raw.strip().lower()
    return v if v in WATCH_LEVELS else "normal"


def parse_threshold_pp(raw: str) -> float | None:
    text = raw.strip().replace("%", "")
    if not text:
        return None
    try:
        value = float(text)
    except ValueError:
        return None
    return value if value > 0 else None


def parse_watchlist_settings(path: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 2:
            continue
        if parts[0] in {"分类", "Category"} or parts[1] in {"问题", "Question"}:
            continue
        if parts[0].startswith("---"):
            continue
        category = parts[0]
        question = parts[1]
        if not question:
            continue
        watch_level = normalize_watch_level(parts[6] if len(parts) >= 7 else "")
        threshold_pp = parse_threshold_pp(parts[7] if len(parts) >= 8 else "")
        out[norm_text(question)] = {
            "category": category or "AI Releases",
            "question": question,
            "watch_level": watch_level,
            "threshold_abs_pp": threshold_pp,
        }
    return out


def infer_category_from_text(text: str, mode: str) -> str:
    lowered = text.lower()
    if mode == "crypto" or contains_keyword(lowered, CRYPTO_KEYWORDS):
        return "Crypto"
    if mode == "geopolitics" or contains_keyword(lowered, GEOPOLITICS_KEYWORDS):
        return "Geopolitics"
    if "ipo" in lowered and "spacex" in lowered:
        return "SpaceX IPO"
    if "spacex" in lowered and any(k in lowered for k in ["launch", "starship", "mission"]):
        return "SpaceX Missions"
    if "openai" in lowered and "ipo" in lowered:
        return "OpenAI IPO"
    if any(k in lowered for k in ["best ai", "top ai"]):
        return "AI Leaders"
    return "AI Releases"


def entry_id_for_row(row: dict[str, Any]) -> str:
    return f"{row.get('source')}:{row.get('market_id')}:{row.get('slug')}:{row.get('event_id')}"


def digest_interval_days(frequency: str) -> int:
    if frequency == "daily":
        return 1
    if frequency == "weekly":
        return 7
    if frequency == "biweekly":
        return 14
    return 0


def load_json_obj(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def should_emit_digest(state_path: Path, frequency: str) -> bool:
    interval = digest_interval_days(frequency)
    if interval <= 0:
        return False
    now = datetime.now(timezone.utc)
    state = load_json_obj(state_path)
    last_sent_raw = str(state.get("last_sent_ts", "")).strip()
    if not last_sent_raw:
        return True
    try:
        last = datetime.fromisoformat(last_sent_raw.replace("Z", "+00:00"))
    except Exception:
        return True
    return (now - last).days >= interval


def write_digest_state(state_path: Path, frequency: str) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "last_sent_ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "frequency": frequency,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def build_digest_text(
    *,
    frequency: str,
    important_entries: list[dict[str, Any]],
    row_by_question: dict[str, dict[str, Any]],
    hit_questions: set[str],
    user_tz: str,
) -> str:
    now_local = format_local_ts(datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), user_tz)
    changed = 0
    lines = []
    for item in important_entries:
        key = norm_text(str(item.get("question", "")))
        row = row_by_question.get(key)
        current = "N/A"
        if row is not None:
            current = f"{row.get('probability')}%"
        status = "changed" if key in hit_questions else "stable"
        if status == "changed":
            changed += 1
        lines.append(f"- [{status}] {item.get('question')} | current={current} | category={item.get('category')}")
    stable = len(important_entries) - changed
    header = (
        f"SignalRadar DIGEST {frequency} important={len(important_entries)} "
        f"changed={changed} stable={stable} at {now_local}"
    )
    return header + "\n" + "\n".join(lines)


def contains_keyword(text: str, keywords: list[str]) -> bool:
    lowered = text.lower()
    return any(k in lowered for k in keywords)


def select_mode_rows(
    rows: list[dict[str, Any]],
    mode: str,
    ai_questions: set[str],
    limit: int,
) -> list[dict[str, Any]]:
    if mode == "crypto":
        selected = [r for r in rows if contains_keyword(str(r.get("question", "")), CRYPTO_KEYWORDS)]
        selected.sort(key=extract_volume, reverse=True)
        return selected[:limit]

    if mode == "geopolitics":
        selected = [r for r in rows if contains_keyword(str(r.get("question", "")), GEOPOLITICS_KEYWORDS)]
        selected.sort(key=extract_volume, reverse=True)
        return selected[:limit]

    if mode == "ai":
        if ai_questions:
            selected = []
            for r in rows:
                q = norm_text(str(r.get("question", "")))
                if q in ai_questions:
                    selected.append(r)
            selected.sort(key=extract_volume, reverse=True)
            return selected[:limit]
        selected = [r for r in rows if contains_keyword(str(r.get("question", "")), AI_FALLBACK_KEYWORDS)]
        selected.sort(key=extract_volume, reverse=True)
        return selected[:limit]

    raise ValueError(f"unsupported mode: {mode}")


def run_cmd(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"command failed ({proc.returncode}): {' '.join(cmd)}\nstdout={proc.stdout}\nstderr={proc.stderr}"
        )
    return proc


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def format_local_ts(ts: str, user_tz: str) -> str:
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if ZoneInfo is None:
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    try:
        return dt.astimezone(ZoneInfo(user_tz)).strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:  # noqa: BLE001
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def load_env_file(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        key = k.strip()
        val = v.strip().strip("'").strip('"')
        if key:
            out[key] = val
    return out


def token_value(text: str, key: str) -> str:
    m = re.search(rf"{re.escape(key)}=([A-Za-z0-9-]+)", text)
    if not m:
        return ""
    return m.group(1).strip()


def build_page_notice(page_name: str, purpose: str, editable: str, notes: str) -> str:
    return "\n".join(
        [
            "```signalradar-page",
            f"page = {page_name}",
            f"purpose = {purpose}",
            f"editable = {editable}",
            f"notes = {notes}",
            "```",
            "",
        ]
    )


def ensure_page_notice(path: Path, notice_block: str) -> None:
    if not path.exists():
        return
    raw = path.read_text(encoding="utf-8")
    if raw.startswith("```signalradar-page\n"):
        updated = PAGE_NOTICE_RE.sub(notice_block, raw, count=1)
    else:
        updated = notice_block + raw
    if updated != raw:
        path.write_text(updated, encoding="utf-8")


def resolve_runtime_script(workspace_root: Path, skill_root: Path, filename: str) -> Path | None:
    candidates = [
        skill_root / "scripts" / filename,
        workspace_root / "scripts" / filename,
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def run_watchlist_refresh(
    workspace_root: Path,
    notion_page_id: str | None,
    notion_manual_page_title: str,
    notion_root_page_title: str,
    *,
    dry_run: bool,
    cfg: dict[str, Any] | None = None,
) -> int:
    skill_root = workspace_root / "skills" / "signalradar"
    refresh_script = resolve_runtime_script(workspace_root, skill_root, "polymarket_watchlist_refresh.py")
    if refresh_script is None:
        return emit_error(
            "SR_SOURCE_UNAVAILABLE",
            "watchlist refresh dependency missing",
            retryable=False,
            details={
                "missing": "polymarket_watchlist_refresh.py",
                "checked": [
                    str(skill_root / "scripts" / "polymarket_watchlist_refresh.py"),
                    str(workspace_root / "scripts" / "polymarket_watchlist_refresh.py"),
                ],
            },
        )

    watchlist_path = workspace_root / "memory" / "polymarket_watchlist_2026.md"
    notion_pull_note = ""
    notion_root_note = ""
    runtime_env = os.environ.copy()
    runtime_env.update(load_env_file(workspace_root / ".env"))
    sync_target_page_id = notion_page_id or ""

    keywords_config = skill_root / "config" / "watchlist_keywords.json"
    try:
        refresh_cmd = [
            sys.executable,
            str(refresh_script),
            "--workspace-root",
            str(workspace_root),
            "--output-watchlist",
            str(workspace_root / "memory" / "polymarket_watchlist_2026.md"),
            "--output-rollover",
            str(workspace_root / "memory" / "polymarket_rollover_2026.md"),
            "--state",
            str(workspace_root / "cache" / "polymarket" / "watchlist_state.json"),
        ]
        if keywords_config.exists():
            refresh_cmd.extend(["--keywords-config", str(keywords_config)])
        if dry_run:
            refresh_cmd.append("--dry-run")
        proc = subprocess.run(
            refresh_cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return emit_error(
            "SR_TIMEOUT",
            "watchlist refresh timeout",
            retryable=True,
            details={"script": str(refresh_script)},
        )
    out = (proc.stdout or "").strip()
    if proc.returncode != 0:
        return emit_error(
            "SR_SOURCE_UNAVAILABLE",
            "watchlist refresh failed",
            retryable=True,
            details={
                "script": str(refresh_script),
                "stdout": out,
                "stderr": (proc.stderr or "").strip(),
            },
        )

    sync_note = ""
    db_note = ""
    sync_readonly = bool((cfg or {}).get("notion", {}).get("sync_readonly_pages", False))
    if notion_page_id:
        # Find SignalRadar root page for sync target
        try:
            from pull_notion_watchlist_entries import (
                find_child_page_id as _find_child,
                notion_headers as _pull_headers,
            )
            _ph = _pull_headers()
            _root_candidates = [notion_root_page_title, "SignalRadar", "signalradar"]
            directory_page_id = _find_child(notion_page_id, _ph, list(set(_root_candidates)))
            if directory_page_id:
                sync_target_page_id = directory_page_id
                notion_root_note = f"notion_root_page={directory_page_id}"
                notion_pull_note = "notion_pull=skipped(check_new_urls handles manual entries)"
            else:
                notion_pull_note = "notion_pull=no_root_page"
        except Exception as _pull_exc:
            notion_pull_note = f"notion_pull=warn error={_pull_exc}"

        ensure_page_notice(
            watchlist_path,
            build_page_notice(
                "polymarket_watchlist_2026",
                "Polymarket 监测条目主清单（AI任务读取源）",
                "partial",
                "可编辑表格行；建议通过 SignalRadar_Manual_Entries 增加条目，避免破坏表头格式",
            ),
        )
        if sync_readonly:
            ensure_page_notice(
                workspace_root / "memory" / "polymarket_rollover_2026.md",
                build_page_notice(
                    "polymarket_rollover_2026",
                    "watchlist 自动维护与迁移日志",
                    "no",
                    "运行时自动生成，建议只读",
                ),
            )

        # 构建同步排除列表
        sync_env = {**runtime_env, "NOTION_PARENT_PAGE_ID": sync_target_page_id or notion_page_id}
        if not sync_readonly:
            sync_env["SYNC_EXCLUDE_PATTERNS"] = "polymarket_rollover_2026|polymarket_watchlist_2026"

        sync_script = resolve_runtime_script(workspace_root, skill_root, "sync_md_to_notion_v4.sh")
        if sync_script is None:
            return emit_error(
                "SR_SOURCE_UNAVAILABLE",
                "notion sync dependency missing",
                retryable=False,
                details={
                    "missing": "sync_md_to_notion_v4.sh",
                    "checked": [
                        str(skill_root / "scripts" / "sync_md_to_notion_v4.sh"),
                        str(workspace_root / "scripts" / "sync_md_to_notion_v4.sh"),
                    ],
                },
            )
        try:
            sync = subprocess.run(
                [
                    "bash",
                    str(sync_script),
                    sync_target_page_id or notion_page_id,
                ],
                capture_output=True,
                text=True,
                timeout=180,
                env=sync_env,
            )
        except subprocess.TimeoutExpired:
            return emit_error(
                "SR_TIMEOUT",
                "notion sync timeout",
                retryable=True,
                details={"script": str(sync_script)},
            )
        if sync.returncode != 0:
            return emit_error(
                "SR_ROUTE_FAILURE",
                "notion sync failed",
                retryable=True,
                details={
                    "script": str(sync_script),
                    "stdout": (sync.stdout or "").strip(),
                    "stderr": (sync.stderr or "").strip(),
                },
            )
        sync_note = "notion_sync=ok"

        # --- Notion Database sync ---
        db_note = ""
        try:
            from notion_watchlist_db import (
                find_or_create_watchlist_db as _find_or_create_db,
                sync_watchlist_to_db as _sync_to_db,
                notion_headers as _notion_hdrs,
            )
            _headers = _notion_hdrs()
            _db_root = sync_target_page_id or notion_page_id
            _db_id = _find_or_create_db(_db_root, _headers)
            if _db_id:
                # Read watchlist items from state file
                _state_path = workspace_root / "cache" / "polymarket" / "watchlist_state.json"
                _wl_items: list[dict[str, Any]] = []
                if _state_path.exists():
                    try:
                        _st = json.loads(_state_path.read_text(encoding="utf-8"))
                        _wl_items = _st.get("items", []) if isinstance(_st.get("items"), list) else []
                    except Exception:
                        pass
                if _wl_items:
                    _result = _sync_to_db(_db_id, _headers, _wl_items)
                    db_note = f"notion_db=ok created={_result['created']} updated={_result['updated']} skipped={_result['skipped']} db_id={_db_id}"
                    # Cache database ID
                    _db_cache = workspace_root / "cache" / "signalradar" / ".notion_db_id"
                    _db_cache.parent.mkdir(parents=True, exist_ok=True)
                    _db_cache.write_text(_db_id, encoding="utf-8")
        except Exception as _db_exc:
            db_note = f"notion_db=warn error={_db_exc}"

    # Manual entries are handled by check_new_urls.py (user-scheduled), not here.
    if "NO_CHANGE" in out:
        print("NO_REPLY")
        return 0
    print("SignalRadar watchlist updated.")
    if notion_pull_note:
        print(notion_pull_note)
    if notion_root_note:
        print(notion_root_note)
    if sync_note:
        print(sync_note)
    if db_note:
        print(db_note)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run SignalRadar Polymarket production job")
    parser.add_argument(
        "--mode",
        required=True,
        choices=["ai", "crypto", "geopolitics", "watchlist-refresh"],
    )
    parser.add_argument("--workspace-root", default=default_workspace_root())
    parser.add_argument("--config", default="", help="Optional config.json path")
    parser.add_argument("--user-timezone", default=None)
    parser.add_argument("--threshold-abs-pp", type=float, default=None)
    parser.add_argument("--threshold-rel-pct", type=float, default=None)
    parser.add_argument("--dedup-window-minutes", type=int, default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--timeout", type=int, default=None)
    parser.add_argument("--source-retries", type=int, default=None)
    parser.add_argument("--route-primary", default=None)
    parser.add_argument("--notion-page-id", default="")
    parser.add_argument("--notion-root-page-title", default="SignalRadar")
    parser.add_argument("--notion-manual-page-title", default="SignalRadar_Manual_Entries")
    parser.add_argument("--digest-frequency", default=None, choices=sorted(DIGEST_FREQUENCIES))
    parser.add_argument("--cleanup-expired", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--cleanup-ttl-days", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root)
    skill_root = workspace_root / "skills" / "signalradar"
    cache_root = workspace_root / "cache" / "signalradar"
    config_path = (
        Path(args.config)
        if args.config
        else Path(os.environ.get("SIGNALRADAR_CONFIG", "")) if os.environ.get("SIGNALRADAR_CONFIG", "").strip() else None
    )
    if config_path is None:
        config_path = workspace_root / "config" / "signalradar_config.json"
    cfg = deep_merge(DEFAULT_CONFIG, load_json_config(config_path))

    user_timezone = args.user_timezone or str(cfg.get("profile", {}).get("timezone", "Asia/Shanghai"))
    threshold_abs_pp = float(args.threshold_abs_pp if args.threshold_abs_pp is not None else cfg["threshold"]["abs_pp"])
    threshold_rel_pct = float(args.threshold_rel_pct if args.threshold_rel_pct is not None else cfg["threshold"]["rel_pct"])
    dedup_enabled = bool(cfg.get("dedup", {}).get("enabled", False))
    dedup_window_default = int(cfg.get("dedup", {}).get("window_minutes", 0))
    dedup_window_minutes = args.dedup_window_minutes if args.dedup_window_minutes is not None else dedup_window_default
    if not dedup_enabled and args.dedup_window_minutes is None:
        dedup_window_minutes = 0
    limit = int(args.limit if args.limit is not None else 200)
    timeout = int(args.timeout if args.timeout is not None else 20)
    source_retries = int(args.source_retries if args.source_retries is not None else cfg.get("source", {}).get("retries", 2))
    route_primary = args.route_primary or f"{cfg.get('delivery', {}).get('primary', {}).get('channel', 'openclaw')}:{cfg.get('delivery', {}).get('primary', {}).get('target', 'direct')}"
    digest_frequency = (args.digest_frequency or str(cfg.get("digest", {}).get("frequency", "off"))).lower().strip()
    if digest_frequency not in DIGEST_FREQUENCIES:
        digest_frequency = "off"
    cleanup_expired = (
        args.cleanup_expired
        if args.cleanup_expired is not None
        else bool(cfg.get("baseline", {}).get("cleanup_expired", False))
    )
    cleanup_ttl_days = int(
        args.cleanup_ttl_days
        if args.cleanup_ttl_days is not None
        else cfg.get("baseline", {}).get("cleanup_ttl_days", 45)
    )
    per_category_thresholds = cfg.get("threshold", {}).get("per_category_abs_pp", {})
    if not isinstance(per_category_thresholds, dict):
        per_category_thresholds = {}
    per_entry_thresholds = cfg.get("threshold", {}).get("per_entry_abs_pp", {})
    if not isinstance(per_entry_thresholds, dict):
        per_entry_thresholds = {}

    if args.mode == "watchlist-refresh":
        return run_watchlist_refresh(
            workspace_root,
            args.notion_page_id or None,
            args.notion_manual_page_title,
            args.notion_root_page_title,
            dry_run=args.dry_run,
            cfg=cfg,
        )

    try:
        rows = fetch_markets(timeout=timeout, retries=source_retries)
        watchlist_path = workspace_root / "memory" / "polymarket_watchlist_2026.md"
        watchlist_settings = parse_watchlist_settings(watchlist_path)
        ai_watch_questions = parse_ai_watchlist_questions(watchlist_path)
        selected = select_mode_rows(rows, args.mode, ai_watch_questions, limit=limit)

        normalized: list[dict[str, Any]] = []
        for item in selected:
            row = normalize_item(item)
            if row is None:
                continue
            q_key = norm_text(str(row.get("question", "")))
            settings = watchlist_settings.get(q_key, {})
            category = str(settings.get("category") or infer_category_from_text(str(row.get("question", "")), args.mode))
            watch_level = normalize_watch_level(str(settings.get("watch_level", "normal")))
            entry_key = entry_id_for_row(row)
            threshold_override: float | None = None

            raw_entry_override = per_entry_thresholds.get(entry_key)
            if raw_entry_override is None:
                raw_entry_override = per_entry_thresholds.get(q_key)
            if raw_entry_override is not None:
                try:
                    threshold_override = float(raw_entry_override)
                except (TypeError, ValueError):
                    threshold_override = None

            if threshold_override is None and settings.get("threshold_abs_pp") is not None:
                try:
                    threshold_override = float(settings.get("threshold_abs_pp"))
                except (TypeError, ValueError):
                    threshold_override = None

            if threshold_override is None and category in per_category_thresholds:
                try:
                    threshold_override = float(per_category_thresholds.get(category))
                except (TypeError, ValueError):
                    threshold_override = None

            row["category"] = category
            row["watch_level"] = watch_level
            if threshold_override is not None and threshold_override > 0:
                row["threshold_abs_pp"] = threshold_override
            normalized.append(row)

        snapshots = cache_root / "snapshots" / f"{args.mode}.json"
        events = cache_root / "events" / f"{args.mode}_hits.json"
        envelopes = cache_root / "events" / f"{args.mode}_envelopes.json"
        baselines = cache_root / "baselines" / args.mode
        dedup = cache_root / "dedup" / args.mode
        audit = cache_root / "events" / f"signal_events_{args.mode}.jsonl"

        write_json(cache_root / "raw" / f"polymarket_{args.mode}.json", selected)
        write_json(snapshots, normalized)

        decide_cmd = [
            sys.executable,
            str(skill_root / "scripts" / "decide_threshold.py"),
            "--snapshots",
            str(snapshots),
            "--out-events",
            str(events),
            "--baseline-dir",
            str(baselines),
            "--audit-log",
            str(audit),
            "--threshold-abs-pp",
            str(threshold_abs_pp),
            "--threshold-rel-pct",
            str(threshold_rel_pct),
        ]
        if cleanup_expired:
            decide_cmd.extend(["--cleanup-expired", "--cleanup-ttl-days", str(cleanup_ttl_days)])
        if args.dry_run:
            decide_cmd.append("--dry-run")
        run_cmd(decide_cmd)

        route_cmd = [
            sys.executable,
            str(skill_root / "scripts" / "route_delivery.py"),
            "--events",
            str(events),
            "--out-envelopes",
            str(envelopes),
            "--route-primary",
            route_primary,
            "--dedup-window-minutes",
            str(dedup_window_minutes),
            "--dedup-dir",
            str(dedup),
        ]
        if args.dry_run:
            route_cmd.append("--dry-run")
        run_cmd(route_cmd)

        event_rows = read_json(events)
        if not isinstance(event_rows, list):
            event_rows = []

        digest_output = ""
        important_entries = [v for v in watchlist_settings.values() if v.get("watch_level") == "important"]
        digest_state = cache_root / "digest" / "state.json"
        if digest_frequency != "off" and important_entries and should_emit_digest(digest_state, digest_frequency):
            row_by_question: dict[str, dict[str, Any]] = {}
            for item in rows:
                norm_row = normalize_item(item)
                if norm_row is None:
                    continue
                row_by_question[norm_text(str(norm_row.get("question", "")))] = norm_row
            hit_questions = {norm_text(str(e.get("question", ""))) for e in event_rows if isinstance(e, dict)}
            digest_output = build_digest_text(
                frequency=digest_frequency,
                important_entries=important_entries,
                row_by_question=row_by_question,
                hit_questions=hit_questions,
                user_tz=user_timezone,
            )
            if not args.dry_run:
                write_digest_state(digest_state, digest_frequency)

        if not event_rows and not digest_output:
            print("NO_REPLY")
            return 0

        label = "DRY_RUN HIT" if args.dry_run else "HIT"
        print(f"SignalRadar {args.mode} {label} {len(event_rows)}")
        for idx, event in enumerate(event_rows[:10], start=1):
            q = event.get("question") or event.get("entry_id")
            current = event.get("current")
            baseline = event.get("baseline")
            abs_pp = event.get("abs_pp")
            ts_local = format_local_ts(str(event.get("ts", "")), user_timezone)
            print(f"{idx}. {q}")
            print(f"   {baseline}% -> {current}% (delta {abs_pp}pp) at {ts_local}")
        if digest_output:
            if event_rows:
                print("")
            print(digest_output)
        print("\n— Powered by SignalRadar")
        return 0
    except Exception as exc:  # noqa: BLE001
        return emit_error(
            "SR_TIMEOUT" if "timed out" in str(exc).lower() else "SR_SOURCE_UNAVAILABLE",
            f"signalradar run failed: {exc}",
            retryable=True,
            details={"script": "run_signalradar_job.py", "mode": args.mode},
        )


if __name__ == "__main__":
    raise SystemExit(main())
