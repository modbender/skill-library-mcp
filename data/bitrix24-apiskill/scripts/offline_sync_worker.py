#!/usr/bin/env python3
"""Offline event worker baseline for Bitrix24.

This worker:
- pulls offline events via event.offline.get(clear=0),
- retries failed records with bounded budget,
- sends exhausted records to DLQ jsonl with file locking,
- clears only successfully processed (or DLQ'ed) records,
- supports graceful shutdown via SIGTERM/SIGINT.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import pathlib
import signal
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

THIS_DIR = pathlib.Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from bitrix24_client import (
    Bitrix24Client,
    BitrixAPIError,
    load_tenant_config_from_env,
    secure_compare,
)


class GracefulShutdown:
    """Handle graceful shutdown on SIGTERM/SIGINT."""

    def __init__(self) -> None:
        self._shutdown_requested = False
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)

    def _handle_signal(self, signum: int, frame: Any) -> None:
        print(f"\nReceived signal {signum}, shutting down gracefully...")
        self._shutdown_requested = True

    @property
    def should_stop(self) -> bool:
        return self._shutdown_requested


def parse_offline_get(response: Dict[str, Any]) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    result = response.get("result", {})
    process_id = result.get("process_id")

    candidates = (
        result.get("events"),
        result.get("items"),
        result.get("result"),
    )
    events: List[Dict[str, Any]] = []
    for candidate in candidates:
        if isinstance(candidate, list):
            events = [item for item in candidate if isinstance(item, dict)]
            break
        if isinstance(candidate, dict):
            events = [value for value in candidate.values() if isinstance(value, dict)]
            break

    return process_id, events


def validate_offline_get_response_schema(response: Dict[str, Any]) -> Optional[str]:
    if not isinstance(response, dict):
        return "response is not an object"
    result = response.get("result")
    if result is None:
        return "missing result field"
    if not isinstance(result, dict):
        return "result is not an object"
    process_id = result.get("process_id")
    if process_id is not None and not isinstance(process_id, str):
        return "result.process_id must be string when present"
    return None


def event_message_id(event_item: Dict[str, Any]) -> Optional[str]:
    for key in ("message_id", "MESSAGE_ID", "id", "ID"):
        value = event_item.get(key)
        if value is not None:
            return str(value)
    return None


def event_dedup_key(event_item: Dict[str, Any]) -> str:
    event_name = str(event_item.get("event") or event_item.get("EVENT") or "unknown")
    payload = event_item.get("data") or event_item.get("DATA") or {}
    stable = json.dumps(payload, sort_keys=True, ensure_ascii=True)
    digest = hashlib.sha256(stable.encode("utf-8")).hexdigest()[:16]
    return f"{event_name}:{digest}"


def validate_event_item_schema(event_item: Dict[str, Any]) -> Optional[str]:
    if not isinstance(event_item, dict):
        return "event item is not an object"
    event_name = event_item.get("event") or event_item.get("EVENT")
    if event_name is not None and not isinstance(event_name, str):
        return "event field must be a string"
    data = event_item.get("data") or event_item.get("DATA")
    if data is not None and not isinstance(data, dict):
        return "data field must be an object"
    auth = event_item.get("auth") or event_item.get("AUTH")
    if auth is not None and not isinstance(auth, dict):
        return "auth field must be an object"
    return None


def validate_application_token(
    event_auth: Dict[str, Any],
    expected_token: Optional[str],
) -> bool:
    """Validate application_token from event using constant-time comparison."""
    if expected_token is None:
        return True  # No validation configured
    received_token = event_auth.get("application_token")
    return secure_compare(received_token, expected_token)


class RetryBudget:
    def __init__(self, state_file: pathlib.Path, max_retries: int) -> None:
        self.state_file = state_file
        self.max_retries = max_retries
        self._state: Dict[str, int] = {}
        self._load()

    def _load(self) -> None:
        if not self.state_file.exists():
            self._state = {}
            return
        try:
            self._state = json.loads(self.state_file.read_text(encoding="utf-8"))
        except Exception:
            self._state = {}

    def save(self) -> None:
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        # Use atomic write with temp file
        temp_file = self.state_file.with_suffix(".tmp")
        temp_file.write_text(json.dumps(self._state, ensure_ascii=True, indent=2), encoding="utf-8")
        temp_file.rename(self.state_file)

    def fail(self, key: str) -> int:
        count = self._state.get(key, 0) + 1
        self._state[key] = count
        return count

    def clear(self, key: str) -> None:
        if key in self._state:
            del self._state[key]

    def exhausted(self, key: str) -> bool:
        return self._state.get(key, 0) >= self.max_retries


def write_dlq(
    dlq_path: pathlib.Path,
    *,
    tenant: str,
    event_item: Dict[str, Any],
    error: str,
    retries: int,
) -> None:
    """Write to DLQ with file locking to prevent corruption from concurrent writes."""
    dlq_path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "tenant": tenant,
        "event": event_item.get("event") or event_item.get("EVENT"),
        "message_id": event_message_id(event_item),
        "retry_count": retries,
        "error": error,
        "payload": event_item,
        "ts": int(time.time()),
    }
    row_json = json.dumps(row, ensure_ascii=True) + "\n"

    # Open with append mode and use exclusive lock for the write
    with dlq_path.open("a", encoding="utf-8") as fh:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        try:
            fh.write(row_json)
            fh.flush()
        finally:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


def process_event_default(event_item: Dict[str, Any]) -> None:
    """Replace this with domain-specific processing."""
    _ = event_item
    return


def clear_processed(
    client: Bitrix24Client,
    *,
    process_id: str,
    message_ids: List[str],
) -> None:
    params: Dict[str, Any] = {"process_id": process_id}
    if message_ids:
        params["message_id"] = message_ids
    client.call("event.offline.clear", params=params)


def report_offline_error(
    client: Bitrix24Client,
    *,
    process_id: str,
    message_ids: List[str],
) -> None:
    if not message_ids:
        return
    try:
        client.call(
            "event.offline.error",
            params={
                "process_id": process_id,
                "message_id": message_ids,
            },
        )
    except BitrixAPIError as exc:
        print(f"Warning: failed to report event.offline.error ({exc.code}): {exc}")


def run_once(
    client: Bitrix24Client,
    *,
    tenant_key: str,
    retry_budget: RetryBudget,
    dlq_path: pathlib.Path,
    application_token: Optional[str] = None,
) -> int:
    response = client.call("event.offline.get", params={"clear": "0"})
    response_error = validate_offline_get_response_schema(response)
    if response_error:
        raise BitrixAPIError(
            f"Invalid offline response schema: {response_error}",
            code="INVALID_OFFLINE_RESPONSE_SCHEMA",
            payload={"raw": response},
        )
    process_id, events = parse_offline_get(response)
    if not process_id or not events:
        return 0

    clear_ids: List[str] = []
    error_ids: List[str] = []
    has_pending_failures = False
    for event_item in events:
        event_schema_error = validate_event_item_schema(event_item)
        if event_schema_error:
            msg_id = event_message_id(event_item)
            write_dlq(
                dlq_path,
                tenant=tenant_key,
                event_item=event_item,
                error=f"INVALID_EVENT_SCHEMA: {event_schema_error}",
                retries=0,
            )
            if msg_id:
                clear_ids.append(msg_id)
                error_ids.append(msg_id)
            else:
                has_pending_failures = True
            continue

        # Validate application_token if configured
        event_auth = event_item.get("auth") or {}
        if not validate_application_token(event_auth, application_token):
            # Log security event and skip (don't clear - might be injection attempt)
            print(f"SECURITY: Invalid application_token for event {event_message_id(event_item)}")
            has_pending_failures = True
            continue

        dedup = event_dedup_key(event_item)
        msg_id = event_message_id(event_item)
        try:
            process_event_default(event_item)
            retry_budget.clear(dedup)
            if msg_id:
                clear_ids.append(msg_id)
        except Exception as exc:  # noqa: BLE001
            retries = retry_budget.fail(dedup)
            if retry_budget.exhausted(dedup):
                write_dlq(
                    dlq_path,
                    tenant=tenant_key,
                    event_item=event_item,
                    error=str(exc),
                    retries=retries,
                )
                retry_budget.clear(dedup)
                if msg_id:
                    clear_ids.append(msg_id)
                    error_ids.append(msg_id)
            else:
                has_pending_failures = True

    if error_ids:
        report_offline_error(client, process_id=process_id, message_ids=error_ids)

    # If there are no pending failures, clear whole process_id even when message IDs are absent.
    # If there are pending failures, clear only explicitly successful/DLQ'ed message IDs.
    if (not has_pending_failures) or clear_ids:
        clear_processed(client, process_id=process_id, message_ids=clear_ids)
    retry_budget.save()
    return len(events)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bitrix24 offline events worker")
    parser.add_argument("--sleep", type=float, default=3.0, help="Sleep seconds between polling cycles")
    parser.add_argument("--once", action="store_true", help="Run one polling iteration and exit")
    parser.add_argument("--max-retries", type=int, default=5, help="Retry budget per dedup event key")
    parser.add_argument(
        "--state-file",
        default=".runtime/offline_retry_state.json",
        help="Path to retry state JSON",
    )
    parser.add_argument(
        "--dlq-file",
        default=".runtime/offline_dlq.jsonl",
        help="Path to DLQ jsonl output",
    )
    parser.add_argument(
        "--application-token",
        default=None,
        help="Expected application_token for event validation (optional)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Setup graceful shutdown handler
    shutdown = GracefulShutdown()

    tenant, token_store = load_tenant_config_from_env()
    tenant_key = tenant.domain
    client = Bitrix24Client(tenant, token_store=token_store)
    retry_budget = RetryBudget(pathlib.Path(args.state_file), max_retries=args.max_retries)
    dlq_path = pathlib.Path(args.dlq_file)

    consecutive_errors = 0
    max_consecutive_errors = 10

    while not shutdown.should_stop:
        try:
            count = run_once(
                client,
                tenant_key=tenant_key,
                retry_budget=retry_budget,
                dlq_path=dlq_path,
                application_token=args.application_token,
            )
            consecutive_errors = 0  # Reset on success

            if args.once:
                print(f"Processed batch size: {count}")
                return
            if count == 0:
                time.sleep(args.sleep)
        except BitrixAPIError as exc:
            consecutive_errors += 1
            print(f"Bitrix API error: code={exc.code} status={exc.status} msg={exc}")

            # Circuit breaker for fatal errors
            if exc.fatal:
                print(f"FATAL: Error code {exc.code} is not recoverable. Exiting.")
                sys.exit(1)

            if args.once:
                return

            # Circuit breaker for too many consecutive errors
            if consecutive_errors >= max_consecutive_errors:
                print(f"FATAL: {consecutive_errors} consecutive errors. Exiting to prevent infinite loop.")
                sys.exit(1)

            time.sleep(args.sleep)
        except KeyboardInterrupt:
            print("\nInterrupted by user")
            break

    print("Worker stopped gracefully")


if __name__ == "__main__":
    main()
