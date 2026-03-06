#!/usr/bin/env python3
"""Minimal fal Queue API client (stdlib-only).

This is intentionally dependency-free so contributors can run it anywhere with Python 3.

Docs (for reference): https://docs.fal.ai/model-apis/model-endpoints/queue/
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


FAL_QUEUE_BASE_URL = "https://queue.fal.run"


class FalQueueError(RuntimeError):
    pass


@dataclass(frozen=True)
class FalQueuedRequest:
    request_id: str
    status_url: str
    response_url: str


def _json_request(
    *,
    url: str,
    method: str,
    fal_key: str,
    payload: dict[str, Any] | None = None,
    timeout_s: float = 30,
    extra_headers: dict[str, str] | None = None,
) -> tuple[int, dict[str, Any]]:
    headers = {
        "Authorization": f"Key {fal_key}",
        "Accept": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)

    body: bytes | None = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8", errors="replace").strip()
            return resp.getcode(), json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace").strip()
        try:
            parsed = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            parsed = {"error": raw or f"HTTP {exc.code}"}
        raise FalQueueError(f"fal queue HTTP {exc.code}: {parsed}") from exc
    except urllib.error.URLError as exc:
        raise FalQueueError(f"fal queue network error: {exc}") from exc


def submit(
    *,
    model_id: str,
    input_payload: dict[str, Any],
    fal_key: str,
    request_timeout_s: int | None = 60,
) -> FalQueuedRequest:
    """Submit an inference request to fal's queue and return tracking URLs."""

    url = f"{FAL_QUEUE_BASE_URL}/{model_id}"
    extra_headers: dict[str, str] = {}
    if request_timeout_s is not None:
        extra_headers["X-Fal-Request-Timeout"] = str(int(request_timeout_s))

    _, body = _json_request(
        url=url,
        method="POST",
        fal_key=fal_key,
        payload=input_payload,
        timeout_s=30,
        extra_headers=extra_headers,
    )

    request_id = str(body.get("request_id", "")).strip()
    status_url = str(body.get("status_url", "")).strip()
    response_url = str(body.get("response_url", "")).strip()

    if not request_id or not status_url or not response_url:
        raise FalQueueError(f"unexpected fal submit response: {body}")

    return FalQueuedRequest(request_id=request_id, status_url=status_url, response_url=response_url)


def wait_for_result(
    *,
    queued: FalQueuedRequest,
    fal_key: str,
    timeout_s: float = 300,
    poll_s: float = 1.0,
    include_logs: bool = False,
) -> dict[str, Any]:
    """Poll the queue status until completed, then return the model output.

    Returns the *model output* (the JSON under the `response` key), not the queue wrapper.
    """

    start = time.monotonic()
    status_url = queued.status_url
    if include_logs:
        # fal supports enabling logs via `?logs=1` on the status endpoint.
        status_url = f"{status_url}?logs=1"

    last_status: str | None = None
    while True:
        _, status_body = _json_request(
            url=status_url,
            method="GET",
            fal_key=fal_key,
            payload=None,
            timeout_s=30,
        )

        last_status = str(status_body.get("status", "")).strip().upper() or None
        if last_status == "COMPLETED":
            break

        elapsed = time.monotonic() - start
        if elapsed > timeout_s:
            raise FalQueueError(f"fal queue timeout after {timeout_s:.0f}s (last_status={last_status})")

        time.sleep(max(0.2, poll_s))

    _, result_body = _json_request(
        url=queued.response_url,
        method="GET",
        fal_key=fal_key,
        payload=None,
        timeout_s=60,
    )

    # Some fal endpoints return a queue wrapper:
    #   {"status":"COMPLETED","response":{...}}
    # Others return the model payload directly:
    #   {"images":[...], ...}
    wrapper_status = str(result_body.get("status", "")).strip().upper()
    if wrapper_status:
        if wrapper_status != "COMPLETED":
            raise FalQueueError(f"unexpected fal result wrapper: {result_body}")
        response = result_body.get("response")
        if not isinstance(response, dict):
            raise FalQueueError(f"unexpected fal response payload: {result_body}")
        return response

    if isinstance(result_body, dict) and any(k in result_body for k in ("images", "video")):
        return result_body

    raise FalQueueError(f"unexpected fal result payload: {result_body}")
