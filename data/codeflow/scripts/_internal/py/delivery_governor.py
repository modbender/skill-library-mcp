"""Delivery governor: single-thread scheduling, retries, and rate limiting.

Design goals (per project requirements):
- Parser/Delivery decoupling: parser submits logical updates; governor delivers.
- Channels:
  - state (thinking/cmd): per-slot anchor; strict snapshot overwrite (latest-wins)
  - event (warning/error/milestone): FIFO
  - final (turn completed/summary): highest priority
  Priority: final > event > state
- Telegram 429 policy:
  - next_allowed_at = now + retry_after + 1s (strict; +1s guard avoids boundary re-429)
  - do not send any request before next_allowed_at
  - when window opens, dequeue by priority; state updates coalesce in memory (latest snapshot only)
- No extra log files: delivery anomalies are appended to stream.jsonl only.
"""

from __future__ import annotations

import json
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Deque, Dict, Optional, TextIO

from redaction import redact_text

from delivery_errors import DeliveryError, DeliveryRateLimited


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_reason(reason: str, *, limit: int = 200) -> str:
    text = (reason or "").strip()
    if not text:
        return ""
    text = redact_text(text, strict=True)
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)] + "…"


@dataclass(slots=True)
class _QueuedMsg:
    op: str  # "post"
    text: str
    name: Optional[str]
    attempt: int = 0


@dataclass(slots=True)
class _StateSlot:
    key: str  # "think" | "cmd"
    anchor_id: Optional[int] = None
    last_sent_text: str = ""
    pending_text: str = ""
    pending_attempt: int = 0
    anchor_recreates_this_turn: int = 0


class DeliveryGovernor:
    """Single-thread delivery scheduler with strict rate-limit compliance."""

    def __init__(
        self,
        platform: object,
        *,
        platform_name: str,
        stream_log: Optional[TextIO],
        delivery_stats: Dict[str, object],
        flush_delivery_summary: Optional[Callable[[], None]] = None,
        replay_delay_sec: float = 0.0,
        clock: Optional[Callable[[], float]] = None,
        sleeper: Optional[Callable[[float], None]] = None,
    ) -> None:
        self._platform = platform
        self._platform_name = (platform_name or "unknown").strip().lower() or "unknown"
        self._stream_log = stream_log
        self._stats = delivery_stats
        self._flush_summary = flush_delivery_summary
        self._replay_delay = max(0.0, float(replay_delay_sec or 0.0))
        self._clock = clock or time.time
        self._sleep = sleeper or time.sleep

        self._next_allowed_at: float = 0.0

        self._final_q: Deque[_QueuedMsg] = deque()
        self._event_q: Deque[_QueuedMsg] = deque()
        self._state: Dict[str, _StateSlot] = {
            "think": _StateSlot("think"),
            "cmd": _StateSlot("cmd"),
        }

        self._ensure_stats_shape()

    # ------------------------------------------------------------------ stats
    def _ensure_stats_shape(self) -> None:
        d = self._stats
        d.setdefault("http_requests", 0)
        d.setdefault("http_ok", 0)
        d.setdefault("http_fail", 0)
        d.setdefault("http_retries", 0)
        d.setdefault("last_error", "")
        d.setdefault("rate_limit_count", 0)
        d.setdefault("fail_by_code", {})
        d.setdefault("drops", 0)
        d.setdefault("anchor_recreates", 0)
        d.setdefault("last_retry_after", None)

    def _inc(self, key: str, delta: int = 1) -> None:
        try:
            self._stats[key] = int(self._stats.get(key, 0) or 0) + int(delta)
        except Exception:
            self._stats[key] = int(delta)

    def _set_last_error(self, text: str) -> None:
        self._stats["last_error"] = _safe_reason(text, limit=240)

    def _inc_fail_code(self, code: Optional[int]) -> None:
        if code is None:
            return
        try:
            m = self._stats.get("fail_by_code")
            if not isinstance(m, dict):
                m = {}
            k = str(int(code))
            m[k] = int(m.get(k, 0) or 0) + 1
            self._stats["fail_by_code"] = m
        except Exception:
            pass

    def _flush_summary_best_effort(self) -> None:
        if not callable(self._flush_summary):
            return
        try:
            self._flush_summary()
        except Exception:
            pass

    # ------------------------------------------------------------- stream.jsonl
    def _append_stream_event(
        self,
        event_type: str,
        *,
        op: str,
        code: Optional[int],
        retry_after: Optional[float],
        attempt: int,
        anchor: Optional[int],
        reason: str,
    ) -> None:
        if not self._stream_log:
            return
        rec = {
            "ts": _now_iso(),
            "type": event_type,
            "platform": self._platform_name,
            "op": op,
            "code": int(code) if isinstance(code, int) else (int(code) if str(code).isdigit() else code),
            "retry_after": retry_after,
            "attempt": int(attempt),
            "anchor": int(anchor) if isinstance(anchor, int) else None,
            "reason": _safe_reason(reason),
        }
        # Drop Nones to keep the log light.
        rec = {k: v for k, v in rec.items() if v is not None and v != ""}
        try:
            self._stream_log.write(json.dumps(rec, ensure_ascii=False) + "\n")
            self._stream_log.flush()
        except Exception:
            pass

    # ----------------------------------------------------------------- API
    def start_turn(self) -> None:
        """Reset state anchors for a new Codex turn (compact mode semantics)."""
        for slot in self._state.values():
            slot.anchor_id = None
            slot.last_sent_text = ""
            slot.pending_text = ""
            slot.pending_attempt = 0
            slot.anchor_recreates_this_turn = 0

    def submit_state(self, key: str, text: str) -> None:
        slot = self._state.get(key)
        if not slot:
            return
        slot.pending_text = text or ""
        # Latest-wins merge: attempt counter is tied to the pending payload.
        slot.pending_attempt = 0

    def submit_state_delta(self, key: str, text: str) -> None:
        """Deprecated: state deltas removed; treat as snapshot overwrite (latest-wins)."""
        self.submit_state(key, text)

    def submit_event(self, text: str, *, name: Optional[str] = None) -> None:
        self._event_q.append(_QueuedMsg(op="post", text=text or "", name=name))

    def submit_final(self, text: str, *, name: Optional[str] = None) -> None:
        self._final_q.append(_QueuedMsg(op="post", text=text or "", name=name))

    def has_pending(self) -> bool:
        if self._final_q or self._event_q:
            return True
        return any(bool(slot.pending_text) for slot in self._state.values())

    # --------------------------------------------------------------- internals
    def _rate_limit_until(self, retry_after: Optional[float]) -> None:
        # Telegram 429 backoff policy: strictly honor retry_after, plus a +1s guard.
        # next_allowed_at = now + retry_after + 1s
        ra = float(retry_after or 0.0)
        wait = max(0.0, ra) + 1.0
        # Keep the effective wait we actually apply (+1s guard included).
        self._stats["last_retry_after"] = float(wait)
        until = self._clock() + float(wait)
        if until > self._next_allowed_at:
            self._next_allowed_at = until

    def _can_send_now(self) -> bool:
        return self._clock() >= float(self._next_allowed_at or 0.0)

    def _sleep_until_allowed(self) -> None:
        now = self._clock()
        wait = float(self._next_allowed_at or 0.0) - float(now)
        if wait > 0:
            self._sleep(wait)

    def _platform_call(self, fn_name: str, *args):
        # Prefer a governed variant when available so adapters can keep
        # best-effort helpers for other call sites (e.g., bash snippets).
        governed = getattr(self._platform, f"{fn_name}_governed", None)
        fn = governed if callable(governed) else getattr(self._platform, fn_name, None)
        if not callable(fn):
            raise DeliveryError(platform=self._platform_name, op=fn_name, reason="unsupported operation")
        return fn(*args)

    def _do_post(self, msg: _QueuedMsg, *, channel: str) -> None:
        # Telegram: avoid adapter-side pagination to prevent partial-send duplication
        # under retries/rate limits. Split here, then send as single-message posts.
        if self._platform_name == "telegram":
            limit = getattr(self._platform, "MAX_TEXT", None)
            if isinstance(limit, int) and limit > 0 and len(msg.text) > limit:
                chunks = self._split_plain_text(msg.text, limit)
                if chunks:
                    # Enqueue the remaining chunks right after this one (front),
                    # preserving order and channel priority.
                    rest = chunks[1:]
                    target = self._final_q if channel == "final" else self._event_q
                    for chunk in reversed(rest):
                        target.appendleft(_QueuedMsg(op="post", text=chunk, name=msg.name, attempt=0))
                    msg.text = chunks[0]

        # Count this as an HTTP request attempt.
        self._inc("http_requests", 1)
        try:
            if self._platform_name == "telegram":
                self._platform_call("post_single", msg.text, msg.name)
            else:
                self._platform_call("post", msg.text, msg.name)
            self._inc("http_ok", 1)
            if self._replay_delay:
                self._sleep(self._replay_delay)
        except DeliveryRateLimited as e:
            self._inc("rate_limit_count", 1)
            self._set_last_error(str(e.reason or "rate_limited"))
            self._append_stream_event(
                "codeflow.delivery.rate_limited",
                op=e.op or "post",
                code=e.code or 429,
                retry_after=e.retry_after,
                attempt=msg.attempt,
                anchor=e.anchor,
                reason=e.reason or "rate_limited",
            )
            self._rate_limit_until(e.retry_after)
            self._inc("http_retries", 1)
            msg.attempt += 1
            # Requeue at front to preserve FIFO and channel priority.
            if channel == "final":
                self._final_q.appendleft(msg)
            else:
                self._event_q.appendleft(msg)
            self._append_stream_event(
                "codeflow.delivery.retry_scheduled",
                op=e.op or "post",
                code=e.code or 429,
                retry_after=e.retry_after,
                attempt=msg.attempt,
                anchor=e.anchor,
                reason="rate_limited",
            )
            self._flush_summary_best_effort()
        except DeliveryError as e:
            self._inc("http_fail", 1)
            self._inc_fail_code(e.code)
            self._set_last_error(str(e.reason or e))
            self._append_stream_event(
                "codeflow.delivery.drop",
                op=e.op or "post",
                code=e.code,
                retry_after=e.retry_after,
                attempt=msg.attempt,
                anchor=e.anchor,
                reason=e.reason or "delivery_failed",
            )
            self._inc("drops", 1)
            self._flush_summary_best_effort()
        except Exception as e:
            self._inc("http_fail", 1)
            self._set_last_error(type(e).__name__)
            self._append_stream_event(
                "codeflow.delivery.drop",
                op="post",
                code=None,
                retry_after=None,
                attempt=msg.attempt,
                anchor=None,
                reason=type(e).__name__,
            )
            self._inc("drops", 1)
            self._flush_summary_best_effort()

    def _split_plain_text(self, text: str, limit: int) -> list[str]:
        if limit <= 0:
            return [text or ""]
        text = text or ""
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

    def _do_state_send(self, slot: _StateSlot) -> None:
        text = slot.pending_text or ""
        if not text:
            return

        # No-op guard: snapshot already applied.
        if slot.anchor_id is not None and text == slot.last_sent_text:
            slot.pending_text = ""
            slot.pending_attempt = 0
            return

        # Enforce single-message invariant for governed adapters (e.g., Telegram edit_single_governed).
        limit = getattr(self._platform, "MAX_TEXT", None)
        if isinstance(limit, int) and limit > 0 and len(text) > limit:
            text = self._fit_single_message_tail(text, limit)

        op = "post_single" if slot.anchor_id is None else "edit_single"
        self._inc("http_requests", 1)
        try:
            if slot.anchor_id is None:
                mid = self._platform_call("post_single", text, None)
                if isinstance(mid, int) and mid > 0:
                    slot.anchor_id = mid
                    slot.last_sent_text = text
                    slot.pending_text = ""
                    slot.pending_attempt = 0
                    self._inc("http_ok", 1)
                else:
                    raise DeliveryError(
                        platform=self._platform_name,
                        op="post_single",
                        code=None,
                        reason="no_message_id",
                    )
            else:
                ok = bool(self._platform_call("edit_single", int(slot.anchor_id), text))
                if ok:
                    slot.last_sent_text = text
                    slot.pending_text = ""
                    slot.pending_attempt = 0
                    self._inc("http_ok", 1)
                else:
                    raise DeliveryError(
                        platform=self._platform_name,
                        op="edit_single",
                        code=None,
                        anchor=int(slot.anchor_id),
                        reason="edit_failed",
                    )
            if self._replay_delay:
                self._sleep(self._replay_delay)
        except DeliveryRateLimited as e:
            self._inc("rate_limit_count", 1)
            self._set_last_error(str(e.reason or "rate_limited"))
            self._append_stream_event(
                "codeflow.delivery.rate_limited",
                op=e.op or op,
                code=e.code or 429,
                retry_after=e.retry_after,
                attempt=slot.pending_attempt,
                anchor=slot.anchor_id,
                reason=e.reason or "rate_limited",
            )
            self._rate_limit_until(e.retry_after)
            self._inc("http_retries", 1)
            slot.pending_attempt += 1
            self._append_stream_event(
                "codeflow.delivery.retry_scheduled",
                op=e.op or op,
                code=e.code or 429,
                retry_after=e.retry_after,
                attempt=slot.pending_attempt,
                anchor=slot.anchor_id,
                reason="rate_limited",
            )
            self._flush_summary_best_effort()
        except DeliveryError as e:
            # Anchor stability policy: never "edit failed -> post new anchor" blindly.
            self._inc("http_fail", 1)
            self._inc_fail_code(e.code)
            self._set_last_error(str(e.reason or e))

            if op == "edit_single" and self._should_recreate_anchor(e) and slot.anchor_recreates_this_turn < 1:
                old_anchor = slot.anchor_id
                slot.anchor_id = None
                slot.anchor_recreates_this_turn += 1
                self._inc("anchor_recreates", 1)
                self._append_stream_event(
                    "codeflow.delivery.anchor_recreate",
                    op="edit_single",
                    code=e.code,
                    retry_after=e.retry_after,
                    attempt=slot.pending_attempt,
                    anchor=old_anchor,
                    reason=e.reason or "anchor_lost",
                )
                self._flush_summary_best_effort()
                # Keep pending_text; next tick will post_single a fresh anchor.
                return

            self._append_stream_event(
                "codeflow.delivery.drop",
                op=op,
                code=e.code,
                retry_after=e.retry_after,
                attempt=slot.pending_attempt,
                anchor=slot.anchor_id,
                reason=e.reason or "delivery_failed",
            )
            self._inc("drops", 1)
            # Drop the pending update (state is lossy by design).
            slot.pending_text = ""
            slot.pending_attempt = 0
            self._flush_summary_best_effort()
        except Exception as e:
            self._inc("http_fail", 1)
            self._set_last_error(type(e).__name__)
            self._append_stream_event(
                "codeflow.delivery.drop",
                op=op,
                code=None,
                retry_after=None,
                attempt=slot.pending_attempt,
                anchor=slot.anchor_id,
                reason=type(e).__name__,
            )
            self._inc("drops", 1)
            slot.pending_text = ""
            slot.pending_attempt = 0
            self._flush_summary_best_effort()

    def _should_recreate_anchor(self, err: DeliveryError) -> bool:
        # Telegram: editMessageText common unrecoverable errors for missing anchors.
        if self._platform_name != "telegram":
            return False
        code = err.code
        reason = (err.reason or "").lower()
        if code in {400, 404} and ("message to edit not found" in reason or "message_id_invalid" in reason):
            return True
        return False

    def _pick_pending_state_slot(self) -> Optional[_StateSlot]:
        pending = [s for s in self._state.values() if bool(s.pending_text)]
        if not pending:
            return None
        # Keep both cards updated: send the one that's currently stale (no anchor),
        # else deterministic ordering (think then cmd).
        order = {"think": 0, "cmd": 1}
        pending.sort(key=lambda s: (0 if s.anchor_id is None else 1, order.get(s.key, 99)))
        return pending[0]

    def _fit_single_message_tail(self, text: str, limit: int) -> str:
        """Fit text into a single message, truncating only when it exceeds limit.

        Policy (compact state cards): preserve the header line (if any) and the most recent tail content.
        """
        if limit <= 0:
            return text or ""
        text = text or ""
        if len(text) <= limit:
            return text

        suffix = "\n…(truncated)"
        if len(suffix) >= limit:
            return "…"[:limit]

        keep = max(0, limit - len(suffix))
        if keep <= 0:
            return suffix[:limit]

        if "\n" in text:
            header, body = text.split("\n", 1)
            header_prefix = header + "\n"
            remaining = keep - len(header_prefix)
            if remaining > 0:
                body_tail = body[-remaining:]
                return header_prefix + body_tail + suffix

        return text[-keep:] + suffix

    # ----------------------------------------------------------------- pump
    def tick(self, *, max_ops: int = 8) -> int:
        """Attempt to deliver up to max_ops operations (non-blocking)."""
        if max_ops <= 0:
            return 0
        if not self._can_send_now():
            return 0

        did = 0
        for _ in range(int(max_ops)):
            if not self._can_send_now():
                break
            if self._final_q:
                msg = self._final_q.popleft()
                self._do_post(msg, channel="final")
                did += 1
                continue
            if self._event_q:
                msg = self._event_q.popleft()
                self._do_post(msg, channel="event")
                did += 1
                continue
            slot = self._pick_pending_state_slot()
            if slot:
                self._do_state_send(slot)
                did += 1
                continue
            break
        return did

    def flush(self) -> None:
        """Drain all pending deliveries (may block while respecting rate limits)."""
        while self.has_pending():
            if not self._can_send_now():
                self._sleep_until_allowed()
            n = self.tick(max_ops=32)
            if n <= 0 and self.has_pending() and self._can_send_now():
                # Avoid a tight loop if nothing progressed due to persistent errors.
                self._sleep(0.2)
