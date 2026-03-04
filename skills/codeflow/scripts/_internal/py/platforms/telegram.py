"""Telegram adapter for posting relay messages.

Required env:
- TELEGRAM_CHAT_ID (target chat id)
Optional env:
- TELEGRAM_BOT_TOKEN (if missing, try OpenClaw config)
- TELEGRAM_THREAD_ID (forum topic thread id)
- TELEGRAM_SILENT=true|false
"""

from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.error
import urllib.request
from collections import OrderedDict
from pathlib import Path
from typing import Optional

from redaction import redact_text
from delivery_errors import DeliveryError, DeliveryRateLimited


MAX_TEXT = 3900
_SINGLE_TRUNC_SUFFIX = "\n…(truncated)"
_SINGLE_TRUNC_MID = "…"


def _load_openclaw_config() -> dict:
    cfg_path = os.environ.get("OPENCLAW_CONFIG_PATH") or os.path.expanduser("~/.openclaw/openclaw.json")
    try:
        raw = Path(cfg_path).read_text(encoding="utf-8")
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _bot_token() -> str:
    tok = (os.environ.get("TELEGRAM_BOT_TOKEN") or "").strip()
    if tok:
        return tok
    cfg = _load_openclaw_config()
    t = (((cfg.get("channels") or {}).get("telegram") or {}).get("botToken") or "").strip()
    return t


BOT_TOKEN = _bot_token()
CHAT_ID = (os.environ.get("TELEGRAM_CHAT_ID") or "").strip()
THREAD_ID = (os.environ.get("TELEGRAM_THREAD_ID") or "").strip()
SILENT = (os.environ.get("TELEGRAM_SILENT") or "false").lower() == "true"


SUPPORTS_EDIT = True


DELIVERY_STATS = {
    "http_requests": 0,
    "http_ok": 0,
    "http_fail": 0,
    "http_retries": 0,
    "last_error": "",
    "rate_limit_count": 0,
    "fail_by_code": {},
    "drops": 0,
    "anchor_recreates": 0,
    "last_retry_after": None,
}

# Track multi-message edit groups for oversized messages.
#
# Memory guard: long sessions can emit many oversized posts (file previews, long outputs).
# Keep a bounded LRU so we don't retain unbounded chunks/tail_ids in memory.
def _env_flag(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return int(default)
    try:
        return int(str(raw).strip(), 10)
    except Exception:
        return int(default)


# If disabled, telegram.edit() still works, but cannot manage prior tail messages.
TRACK_EDIT_GROUPS = _env_flag("CODEFLOW_TELEGRAM_TRACK_EDIT_GROUPS", True)
# Max number of tracked edit groups (LRU). Set <=0 to disable tracking.
EDIT_GROUPS_MAX = _env_int("CODEFLOW_TELEGRAM_EDIT_GROUPS_MAX", 64)

# Track multi-message edit groups for oversized edits.
# Key: anchor message_id (the one parse-stream.py holds).
# Value: {"tail_ids": [int, ...], "chunks": [str, ...]} where len(chunks)=1+len(tail_ids).
_EDIT_GROUPS: "OrderedDict[int, dict[str, object]]" = OrderedDict()


def _safe_err_text(text: str, limit: int = 200) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    text = redact_text(text, strict=True)
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)] + "…"

def _parse_retry_after(data: object) -> Optional[float]:
    try:
        if not isinstance(data, dict):
            return None
        params = data.get("parameters") or {}
        if not isinstance(params, dict):
            return None
        ra = params.get("retry_after")
        if isinstance(ra, (int, float)):
            return float(ra)
    except Exception:
        return None
    return None


def _api_post_once(method: str, form: dict, *, op: str) -> dict:
    """Single-attempt Telegram API call.

    Governed (delivery governor) paths rely on this being:
    - no internal retries
    - no sleeps
    - raising DeliveryRateLimited with retry_after on 429
    """
    if not BOT_TOKEN:
        raise DeliveryError(platform="telegram", op=op, reason="missing_bot_token")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    body = urllib.parse.urlencode(form).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        data = json.loads(raw) if raw else {}
        if not isinstance(data, dict):
            data = {}
    except urllib.error.HTTPError as e:
        body_raw = ""
        try:
            body_raw = e.read().decode("utf-8", errors="replace")
        except Exception:
            body_raw = ""
        try:
            data = json.loads(body_raw) if body_raw else {}
            if not isinstance(data, dict):
                data = {}
        except Exception:
            data = {}
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise DeliveryError(platform="telegram", op=op, reason=type(e).__name__) from e
    except Exception as e:
        raise DeliveryError(platform="telegram", op=op, reason=type(e).__name__) from e

    if data.get("ok") is True:
        return data

    code = data.get("error_code")
    code_int = int(code) if isinstance(code, int) else None
    desc = _safe_err_text(str(data.get("description") or ""))
    retry_after = _parse_retry_after(data)

    if code_int == 429:
        raise DeliveryRateLimited(
            platform="telegram",
            op=op,
            code=429,
            retry_after=retry_after,
            reason=desc or "rate_limited",
        )

    raise DeliveryError(
        platform="telegram",
        op=op,
        code=code_int,
        retry_after=retry_after,
        reason=desc or "telegram_error",
    )


def _api_post(method: str, form: dict) -> dict:
    if not BOT_TOKEN:
        return {}
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    body = urllib.parse.urlencode(form).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")

    last_err = ""
    # Be conservative: only retry explicit rate-limit responses to avoid duplicate posts.
    retryable = {429}
    max_attempts = 2

    for attempt in range(max_attempts):
        if attempt:
            DELIVERY_STATS["http_retries"] += 1
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
            data = json.loads(raw) if raw else {}
            if not isinstance(data, dict):
                data = {}

            if data.get("ok") is True:
                return data

            code = data.get("error_code")
            desc = data.get("description")
            safe_desc = _safe_err_text(desc)
            if isinstance(code, int):
                last_err = f"{method} TELEGRAM {code}: {safe_desc}" if safe_desc else f"{method} TELEGRAM {code}"
            else:
                last_err = f"{method} TELEGRAM error"

            retry_after = None
            try:
                params = data.get("parameters") or {}
                ra = params.get("retry_after") if isinstance(params, dict) else None
                if isinstance(ra, (int, float)):
                    retry_after = float(ra)
            except Exception:
                pass

            if isinstance(code, int) and code in retryable and attempt < (max_attempts - 1):
                if retry_after is not None:
                    time.sleep(max(0.0, float(retry_after)))
                else:
                    time.sleep(1.0)
                continue
            break

        except urllib.error.HTTPError as e:
            status = getattr(e, "code", None) or 0
            body_raw = ""
            try:
                body_raw = e.read().decode("utf-8", errors="replace")
            except Exception:
                body_raw = ""

            code = None
            desc = ""
            retry_after = None
            try:
                data = json.loads(body_raw) if body_raw else {}
                if isinstance(data, dict):
                    code = data.get("error_code")
                    desc = str(data.get("description") or "")
                    params = data.get("parameters") or {}
                    ra = params.get("retry_after") if isinstance(params, dict) else None
                    if isinstance(ra, (int, float)):
                        retry_after = float(ra)
            except Exception:
                pass

            safe_desc = _safe_err_text(desc)
            if isinstance(code, int):
                last_err = f"{method} TELEGRAM {code}: {safe_desc}" if safe_desc else f"{method} TELEGRAM {code}"
            else:
                last_err = f"{method} HTTP {status}"

            if int(status) in retryable and attempt < (max_attempts - 1):
                if retry_after is not None:
                    time.sleep(max(0.0, float(retry_after)))
                else:
                    time.sleep(1.0)
                continue
            break

        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_err = type(e).__name__
            break

        except Exception as e:
            last_err = type(e).__name__
            break

    DELIVERY_STATS["last_error"] = last_err
    return {}


def send_action(action: str = "typing") -> bool:
    """Send a chat action (typing, upload_photo, etc).

    Best-effort: try thread-scoped action first (if THREAD_ID is set), then
    fallback to chat-level action, since support has historically varied.
    """
    if not BOT_TOKEN or not CHAT_ID:
        return False

    action = (action or "typing").strip() or "typing"
    form = {"chat_id": CHAT_ID, "action": action}

    if THREAD_ID:
        data = _api_post("sendChatAction", {**form, "message_thread_id": THREAD_ID})
        if bool(data.get("ok")):
            return True

    data = _api_post("sendChatAction", form)
    return bool(data.get("ok"))


def _split_text(text: str, limit: int) -> list[str]:
    """Split long text into ordered chunks with no data loss.

    Guarantees: each chunk length <= limit and "".join(chunks) == text.
    Prefers splitting on a newline near the end of the chunk for readability.
    """
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    start = 0
    threshold = limit // 2
    text_len = len(text)

    while start < text_len:
        end = min(start + limit, text_len)
        if end < text_len:
            split_at = text.rfind("\n", start, end)
            if split_at != -1 and (split_at - start) >= threshold:
                end = split_at + 1
        if end <= start:
            end = min(start + limit, text_len)
        chunks.append(text[start:end])
        start = end

    return chunks


def _compact_middle(text: str, limit: int) -> str:
    """Compact text to <= limit chars using head+tail with a mid marker.

    Guarantees: len(out) <= limit (best-effort) and out is non-empty when limit > 0.
    """
    text = text or ""
    if limit <= 0:
        return ""
    if len(text) <= limit:
        return text

    mid = _SINGLE_TRUNC_MID
    if limit <= len(mid):
        return mid[:limit]

    head_len = max(0, (limit - len(mid)) // 2)
    tail_len = max(0, limit - len(mid) - head_len)
    if head_len <= 0 or tail_len <= 0:
        return text[:limit]
    return text[:head_len] + mid + text[-tail_len:]


def _truncate_single_message(text: str, limit: int) -> str:
    """Fit text into a single Telegram message (no splitting).

    Preserves the first line as a header when present, then compacts the body.
    Appends a small truncation suffix when compaction occurs.
    """
    text = text or ""
    if len(text) <= limit:
        return text
    if limit <= 0:
        return ""

    suffix = _SINGLE_TRUNC_SUFFIX
    if len(suffix) >= limit:
        suffix = _SINGLE_TRUNC_MID

    keep = max(0, limit - len(suffix))
    if keep <= 0:
        return suffix[:limit]

    if "\n" in text:
        header, body = text.split("\n", 1)
        header_prefix = header + "\n"
        remaining = keep - len(header_prefix)
        if remaining > 0:
            body_compact = _compact_middle(body, remaining)
            return header_prefix + body_compact + suffix

    compact = _compact_middle(text, keep)
    return compact + suffix


def _coerce_message_id(message_id) -> Optional[int]:
    try:
        mid = int(message_id)
        return mid if mid > 0 else None
    except Exception:
        return None


def _send_message(text: str) -> Optional[int]:
    if not BOT_TOKEN or not CHAT_ID:
        return None

    form = {
        "chat_id": CHAT_ID,
        "text": text,
        "disable_web_page_preview": "true",
        "disable_notification": "true" if SILENT else "false",
    }
    if THREAD_ID:
        form["message_thread_id"] = THREAD_ID

    data = _api_post("sendMessage", form)
    try:
        return int(((data.get("result") or {}).get("message_id")))
    except Exception:
        return None

def _send_message_governed(text: str) -> int:
    if not CHAT_ID:
        raise DeliveryError(platform="telegram", op="post_single", reason="missing_chat_id")

    form = {
        "chat_id": CHAT_ID,
        "text": text,
        "disable_web_page_preview": "true",
        "disable_notification": "true" if SILENT else "false",
    }
    if THREAD_ID:
        form["message_thread_id"] = THREAD_ID

    data = _api_post_once("sendMessage", form, op="post_single")
    try:
        mid = int(((data.get("result") or {}).get("message_id")))
        if mid > 0:
            return mid
    except Exception:
        pass
    raise DeliveryError(platform="telegram", op="post_single", reason="no_message_id")


def _edit_message(message_id: int, text: str) -> bool:
    if not BOT_TOKEN or not CHAT_ID or not message_id:
        return False

    form = {
        "chat_id": CHAT_ID,
        "message_id": str(message_id),
        "text": text,
        "disable_web_page_preview": "true",
    }
    if THREAD_ID:
        form["message_thread_id"] = THREAD_ID

    data = _api_post("editMessageText", form)
    return bool(data.get("ok"))

def _edit_message_governed(message_id: int, text: str) -> None:
    if not CHAT_ID or not message_id:
        raise DeliveryError(platform="telegram", op="edit_single", reason="missing_chat_or_message_id", anchor=message_id)

    form = {
        "chat_id": CHAT_ID,
        "message_id": str(message_id),
        "text": text,
        "disable_web_page_preview": "true",
    }
    if THREAD_ID:
        form["message_thread_id"] = THREAD_ID

    _api_post_once("editMessageText", form, op="edit_single")


def _delete_message(message_id: int) -> bool:
    if not BOT_TOKEN or not CHAT_ID or not message_id:
        return False
    data = _api_post("deleteMessage", {"chat_id": CHAT_ID, "message_id": str(message_id)})
    return bool(data.get("ok"))


def _clear_tail_messages(anchor_id: int):
    state = _EDIT_GROUPS.get(anchor_id)
    if not state:
        return
    try:
        _EDIT_GROUPS.move_to_end(anchor_id)
    except Exception:
        pass
    tail_ids = state.get("tail_ids")
    if isinstance(tail_ids, list):
        for mid in tail_ids:
            try:
                _delete_message(int(mid))
            except Exception:
                pass
    _EDIT_GROUPS.pop(anchor_id, None)

def _remember_edit_group(anchor_id: int, *, tail_ids: list[int], chunks: list[str]) -> None:
    if not TRACK_EDIT_GROUPS:
        return
    if int(EDIT_GROUPS_MAX) <= 0:
        return

    _EDIT_GROUPS.pop(anchor_id, None)
    _EDIT_GROUPS[anchor_id] = {"tail_ids": tail_ids, "chunks": chunks}
    try:
        _EDIT_GROUPS.move_to_end(anchor_id)
    except Exception:
        pass

    # Evict LRU entries beyond the cap (best-effort, non-destructive).
    try:
        while len(_EDIT_GROUPS) > int(EDIT_GROUPS_MAX):
            _EDIT_GROUPS.popitem(last=False)
    except Exception:
        pass


def post(msg, name=None):
    if not BOT_TOKEN or not CHAT_ID:
        return None

    text = msg or ""
    if len(text) <= MAX_TEXT:
        return _send_message(text)

    # Telegram has a hard per-message limit; split to avoid truncation.
    chunks = _split_text(text, MAX_TEXT)
    message_ids: list[int] = []
    for chunk in chunks:
        mid = _send_message(chunk)
        if isinstance(mid, int) and mid > 0:
            message_ids.append(mid)

    if not message_ids:
        return None

    anchor_id = message_ids[0]
    if len(message_ids) > 1:
        _remember_edit_group(anchor_id, tail_ids=message_ids[1:], chunks=chunks)
    return anchor_id


def edit(message_id, msg):
    if not BOT_TOKEN or not CHAT_ID or not message_id:
        return False

    anchor_id = _coerce_message_id(message_id)
    if not anchor_id:
        return False

    text = msg or ""
    chunks = _split_text(text, MAX_TEXT)

    state = _EDIT_GROUPS.get(anchor_id)
    if state:
        try:
            _EDIT_GROUPS.move_to_end(anchor_id)
        except Exception:
            pass
    prev_chunks = state.get("chunks") if isinstance(state, dict) else None
    prev_tail_ids = state.get("tail_ids") if isinstance(state, dict) else None
    tail_ids: list[int] = [int(x) for x in prev_tail_ids] if isinstance(prev_tail_ids, list) else []

    # Head
    if not (isinstance(prev_chunks, list) and len(prev_chunks) >= 1 and prev_chunks[0] == chunks[0]):
        ok = _edit_message(anchor_id, chunks[0])
        if not ok:
            return False

    # Tail management
    desired_tail = chunks[1:]
    new_tail_ids: list[int] = []

    for i, chunk in enumerate(desired_tail):
        # Reuse existing tail message if possible.
        existing_id = tail_ids[i] if i < len(tail_ids) else None

        if existing_id is None:
            mid = _send_message(chunk)
            if isinstance(mid, int) and mid > 0:
                new_tail_ids.append(mid)
            continue

        # Skip per-chunk edits when content is unchanged to avoid Telegram's
        # "message is not modified" hard failure.
        prev_chunk = None
        if isinstance(prev_chunks, list):
            prev_idx = i + 1
            if 0 <= prev_idx < len(prev_chunks):
                prev_chunk = prev_chunks[prev_idx]
        if prev_chunk == chunk:
            new_tail_ids.append(existing_id)
            continue

        ok_tail = _edit_message(existing_id, chunk)
        if ok_tail:
            new_tail_ids.append(existing_id)
            continue

        # Tail edit failed: replace this chunk with a new message.
        mid = _send_message(chunk)
        if isinstance(mid, int) and mid > 0:
            new_tail_ids.append(mid)
            _delete_message(existing_id)
        else:
            new_tail_ids.append(existing_id)

    if not desired_tail:
        _clear_tail_messages(anchor_id)
        return True

    # Delete any extra previous tail messages.
    for extra_id in tail_ids[len(desired_tail):]:
        _delete_message(extra_id)

    _remember_edit_group(anchor_id, tail_ids=new_tail_ids, chunks=chunks)
    return True


def post_single(msg, name=None):
    """Post a single Telegram message (truncate if oversized)."""
    if not BOT_TOKEN or not CHAT_ID:
        return None
    text = _truncate_single_message(msg or "", MAX_TEXT)
    return _send_message(text)

def post_single_governed(msg, name=None):
    """Governor-controlled single-message post (no truncation, no internal splitting)."""
    if not BOT_TOKEN or not CHAT_ID:
        raise DeliveryError(platform="telegram", op="post_single", reason="missing_credentials")
    text = msg or ""
    if len(text) > MAX_TEXT:
        raise DeliveryError(platform="telegram", op="post_single", reason="message_too_long")
    return _send_message_governed(text)


def post_governed(msg, name=None):
    # Governor uses post_single for Telegram (and splits upstream when needed).
    return post_single_governed(msg, name)


def edit_single(message_id, msg):
    """Edit a single Telegram message (truncate if oversized).

    This does not create or maintain multi-message edit groups.
    """
    if not BOT_TOKEN or not CHAT_ID or not message_id:
        return False

    anchor_id = _coerce_message_id(message_id)
    if not anchor_id:
        return False

    # Enforce single-message invariant: clear any previously tracked tail messages.
    _clear_tail_messages(anchor_id)

    text = _truncate_single_message(msg or "", MAX_TEXT)
    return bool(_edit_message(anchor_id, text))


def edit_single_governed(message_id, msg):
    """Governor-controlled single-message edit (no truncation, no internal splitting)."""
    if not BOT_TOKEN or not CHAT_ID or not message_id:
        raise DeliveryError(platform="telegram", op="edit_single", reason="missing_credentials", anchor=_coerce_message_id(message_id))
    anchor_id = _coerce_message_id(message_id)
    if not anchor_id:
        raise DeliveryError(platform="telegram", op="edit_single", reason="invalid_message_id", anchor=None)
    text = msg or ""
    if len(text) > MAX_TEXT:
        raise DeliveryError(platform="telegram", op="edit_single", reason="message_too_long", anchor=anchor_id)
    _clear_tail_messages(anchor_id)
    _edit_message_governed(anchor_id, text)
    return True
