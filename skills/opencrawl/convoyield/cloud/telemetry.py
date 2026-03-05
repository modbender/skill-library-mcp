"""
ConvoYield Telemetry — Phone-home module for cloud analytics.

This module sends anonymized yield data to ConvoYield Cloud for
dashboard analytics. It's completely optional and can be disabled.

Data sent:
- Sentiment scores (no raw text)
- Momentum scores
- Yield estimates
- Phase transitions
- Play recommendations
- Arbitrage types detected
- Micro-conversion types

Data NOT sent:
- User messages
- Bot responses
- Personal information
- Raw conversation content

Privacy first. Analytics second.
"""

from __future__ import annotations

import json
import threading
import queue
import time
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import URLError

from convoyield.models.yield_result import YieldResult


class Telemetry:
    """
    Async telemetry sender for ConvoYield Cloud.

    Events are queued and sent in a background thread to avoid
    blocking the bot's response pipeline.
    """

    def __init__(
        self,
        api_key: str,
        server_url: str = "http://localhost:8000",
        enabled: bool = True,
        flush_interval: float = 5.0,
        max_queue_size: int = 1000,
    ):
        self._api_key = api_key
        self._server = server_url.rstrip("/")
        self._enabled = enabled
        self._flush_interval = flush_interval
        self._queue: queue.Queue = queue.Queue(maxsize=max_queue_size)
        self._thread: Optional[threading.Thread] = None
        self._running = False

        if enabled:
            self._start()

    def _start(self):
        """Start the background sender thread."""
        self._running = True
        self._thread = threading.Thread(target=self._sender_loop, daemon=True)
        self._thread.start()

    def _sender_loop(self):
        """Background loop that batches and sends events."""
        while self._running:
            events = []
            try:
                # Drain the queue
                while not self._queue.empty() and len(events) < 50:
                    events.append(self._queue.get_nowait())
            except queue.Empty:
                pass

            if events:
                self._send_batch(events)

            time.sleep(self._flush_interval)

    def _send_batch(self, events: list[dict]):
        """Send a batch of events to the cloud."""
        for event in events:
            try:
                endpoint = event.pop("_endpoint", "/api/v1/events/yield")
                url = f"{self._server}{endpoint}"
                data = json.dumps(event).encode("utf-8")

                req = Request(
                    url,
                    data=data,
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": self._api_key,
                    },
                    method="POST",
                )

                with urlopen(req, timeout=5) as resp:
                    resp.read()  # Consume response

            except (URLError, OSError, ValueError):
                pass  # Silently drop failed events — never block the bot

    def send_yield_event(
        self,
        session_id: str,
        turn_number: int,
        result: YieldResult,
    ):
        """Queue a yield event for sending."""
        if not self._enabled:
            return

        event = {
            "_endpoint": "/api/v1/events/yield",
            "session_id": session_id,
            "turn_number": turn_number,
            "sentiment": result.current_sentiment,
            "sentiment_delta": result.sentiment_delta,
            "momentum": result.momentum_score,
            "estimated_yield": result.estimated_yield,
            "captured_yield": result.yield_captured_so_far,
            "phase": result.phase or "unknown",
            "risk_level": result.risk_level,
            "recommended_play": result.recommended_play,
            "arbitrage_types": [a.type for a in result.arbitrage_opportunities],
            "micro_conversion_types": [m.type for m in result.micro_conversions],
        }

        try:
            self._queue.put_nowait(event)
        except queue.Full:
            pass  # Drop event rather than block

    def send_conversion(
        self,
        session_id: str,
        conversion_type: str,
        value: float,
    ):
        """Queue a conversion event."""
        if not self._enabled:
            return

        event = {
            "_endpoint": "/api/v1/events/conversion",
            "session_id": session_id,
            "conversion_type": conversion_type,
            "value": value,
        }

        try:
            self._queue.put_nowait(event)
        except queue.Full:
            pass

    def send_session_summary(
        self,
        session_id: str,
        total_turns: int,
        estimated_yield: float,
        captured_yield: float,
        final_phase: str,
        final_sentiment: float,
        duration_seconds: float,
        plays_recommended: list[str],
        arbitrage_detected: list[str],
        conversions_captured: list[str],
    ):
        """Queue a session summary event."""
        if not self._enabled:
            return

        event = {
            "_endpoint": "/api/v1/events/session",
            "session_id": session_id,
            "total_turns": total_turns,
            "estimated_yield": estimated_yield,
            "captured_yield": captured_yield,
            "final_phase": final_phase,
            "final_sentiment": final_sentiment,
            "duration_seconds": duration_seconds,
            "plays_recommended": plays_recommended,
            "arbitrage_detected": arbitrage_detected,
            "conversions_captured": conversions_captured,
        }

        try:
            self._queue.put_nowait(event)
        except queue.Full:
            pass

    def flush(self):
        """Force-flush all queued events."""
        events = []
        try:
            while not self._queue.empty():
                events.append(self._queue.get_nowait())
        except queue.Empty:
            pass

        if events:
            self._send_batch(events)

    def stop(self):
        """Stop the background sender and flush remaining events."""
        self._running = False
        self.flush()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value
        if value and not self._running:
            self._start()
        elif not value:
            self._running = False
