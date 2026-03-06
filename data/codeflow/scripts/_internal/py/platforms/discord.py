"""Discord webhook adapter for posting relay messages.

Important: do not spawn curl with secrets on argv. This adapter uses stdlib
urllib to keep tokens/webhook URLs out of process args (ps).
"""

from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

webhook_url = os.environ.get("WEBHOOK_URL", "").strip()
agent_name = os.environ.get("AGENT_NAME", "Claude Code").strip() or "Claude Code"
thread_mode = os.environ.get("THREAD_MODE", "false").lower() == "true"
allow_mentions = (os.environ.get("CODEFLOW_DISCORD_ALLOW_MENTIONS") or "").strip().lower() in {
    "1",
    "true",
    "yes",
    "y",
    "on",
}

# Discord hard limit is 2000 chars; keep a small safety margin.
MAX_TEXT = 1900

# Thread state: first post creates the thread, subsequent posts go into it.
_thread_id: Optional[str] = None
_thread_create_disabled: bool = False
_thread_create_warned: bool = False

DELIVERY_STATS = {
    "http_requests": 0,
    "http_ok": 0,
    "http_fail": 0,
    "http_retries": 0,
    "last_error": "",
}


def _with_query(url: str, **params: str) -> str:
    parts = urllib.parse.urlsplit(url)
    q = urllib.parse.parse_qs(parts.query, keep_blank_values=True)
    for k, v in params.items():
        q[k] = [v]
    query = urllib.parse.urlencode(q, doseq=True)
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))


def _http_post_json(url: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    DELIVERY_STATS["http_requests"] += 1
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)

    last_err = ""
    # Be conservative: only retry explicit rate-limit responses to avoid duplicate posts.
    retryable = {429}
    max_attempts = 2

    for attempt in range(max_attempts):
        if attempt:
            DELIVERY_STATS["http_retries"] += 1
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                status = getattr(resp, "status", None) or resp.getcode()
                raw = resp.read().decode("utf-8", errors="replace")

            if 200 <= int(status) < 300:
                DELIVERY_STATS["http_ok"] += 1
                if not raw:
                    return {}
                try:
                    data = json.loads(raw)
                    return data if isinstance(data, dict) else {}
                except json.JSONDecodeError:
                    return {}

            last_err = f"HTTP {status}"
            if int(status) in retryable and attempt < (max_attempts - 1):
                time.sleep(1.0)
                continue
            break

        except urllib.error.HTTPError as e:
            status = getattr(e, "code", None) or 0
            last_err = f"HTTP {status}"

            retry_after = None
            try:
                body_raw = e.read().decode("utf-8", errors="replace")
                if int(status) == 429 and body_raw:
                    data = json.loads(body_raw)
                    ra = data.get("retry_after")
                    if isinstance(ra, (int, float)):
                        retry_after = float(ra)
            except Exception:
                pass

            if int(status) in retryable and attempt < (max_attempts - 1):
                if retry_after is not None:
                    time.sleep(min(10.0, max(0.0, retry_after)))
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

    DELIVERY_STATS["http_fail"] += 1
    DELIVERY_STATS["last_error"] = last_err
    return {}


def _split_text(text: str, limit: int) -> list[str]:
    """Split long text into ordered chunks with no data loss.

    Guarantees: each chunk length <= limit and "".join(chunks) == text.
    Prefers splitting on a newline near the end of the chunk for readability.
    """
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    start = 0
    threshold = max(1, limit // 2)
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


def _post_thread_failure_warning_once(reason: str, name: Optional[str]) -> None:
    """Emit a one-time warning when thread creation fails and we fall back to channel posts."""
    global _thread_create_warned
    if _thread_create_warned:
        return
    _thread_create_warned = True

    reason = (reason or "").strip()
    if reason:
        msg = f"⚠️ Codeflow: Discord thread creation failed; falling back to channel posts. ({reason})"
    else:
        msg = "⚠️ Codeflow: Discord thread creation failed; falling back to channel posts."

    payload = {"content": msg, "username": name or agent_name}
    if not allow_mentions:
        payload["allowed_mentions"] = {"parse": []}
    _http_post_json(webhook_url, payload)


def _create_thread_via_webhook(first_msg: str, name: Optional[str]) -> bool:
    """Create a thread by posting the first message, then starting a thread on it."""
    global _thread_id

    payload = {"content": first_msg, "username": name or agent_name}
    if not allow_mentions:
        payload["allowed_mentions"] = {"parse": []}
    resp = _http_post_json(_with_query(webhook_url, wait="true"), payload)
    msg_id = resp.get("id")
    channel_id = resp.get("channel_id")

    if not msg_id or not channel_id:
        return False  # Fall back to no-thread mode (and let caller retry post)

    bot_token = (os.environ.get("BOT_TOKEN") or "").strip()
    if not bot_token:
        # No bot token — can't create threads. Thread mode silently degrades.
        return True

    thread_name = f"{agent_name} — {time.strftime('%H:%M')}"
    thread_resp = _http_post_json(
        f"https://discord.com/api/v10/channels/{channel_id}/messages/{msg_id}/threads",
        {"name": thread_name, "auto_archive_duration": 1440},
        headers={"Authorization": f"Bot {bot_token}"},
    )
    tid = thread_resp.get("id")
    if isinstance(tid, str) and tid:
        _thread_id = tid
    return True


def post(msg: str, name: Optional[str] = None) -> None:
    """Post a message to Discord via webhook.

    In thread mode, the first message creates a thread (via bot API),
    and all subsequent messages are posted into that thread.
    """
    global _thread_id, _thread_create_disabled

    if not webhook_url:
        return

    msg = msg or ""
    if not msg:
        return
    chunks = _split_text(msg, MAX_TEXT)

    start = 0
    thread_failed = False
    thread_fail_reason = ""
    if thread_mode and _thread_id is None and chunks and not _thread_create_disabled:
        # The first message is posted as part of the thread creation flow; don't double-post it.
        first_posted = _create_thread_via_webhook(chunks[0], name)
        if first_posted:
            start = 1
        if _thread_id is None:
            # Fail once, warn once, then stop retrying thread creation to avoid noise.
            thread_failed = True
            _thread_create_disabled = True
            bot_token = (os.environ.get("BOT_TOKEN") or "").strip()
            if not bot_token:
                thread_fail_reason = "missing BOT_TOKEN"
            else:
                thread_fail_reason = (DELIVERY_STATS.get("last_error") or "").strip()

    for chunk in chunks[start:]:
        if not chunk:
            continue
        url = _with_query(webhook_url, thread_id=_thread_id) if _thread_id else webhook_url
        payload = {"content": chunk, "username": name or agent_name}
        if not allow_mentions:
            payload["allowed_mentions"] = {"parse": []}
        _http_post_json(url, payload)

    if thread_failed:
        _post_thread_failure_warning_once(thread_fail_reason, name)
