"""
Exporters — pluggable backends for shipping transaction data.

The exporter interface is simple: implement `export_tx(tx)` and
optionally `export_snapshot(snapshot)`. The tracker calls exporters
on every new transaction; the dashboard calls them on snapshot requests.

Built-in exporters:
  - JsonlExporter    — append to local JSONL file (default)
  - WebhookExporter  — POST JSON to any HTTP endpoint
  - ConsoleExporter   — pretty-print to stdout (debugging)
  - MultiExporter    — fan-out to multiple exporters

Roll your own:
  class MyExporter(BaseExporter):
      def export_tx(self, tx): ...
"""

from __future__ import annotations

import json
import logging
import sys
import threading
import time
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .metrics import Snapshot
    from .types import AgentTx

logger = logging.getLogger("agentfinobs.exporters")


class BaseExporter:
    """
    Abstract base for all exporters.
    Subclass and implement `export_tx` at minimum.
    """

    def export_tx(self, tx: "AgentTx") -> None:
        """Called on every new or settled transaction."""
        raise NotImplementedError

    def export_snapshot(self, snapshot: "Snapshot") -> None:
        """Called periodically with a metrics snapshot. Optional."""
        pass

    def flush(self) -> None:
        """Flush any buffered data. Called on shutdown."""
        pass

    def close(self) -> None:
        """Clean up resources."""
        pass


class JsonlExporter(BaseExporter):
    """
    Append transactions as JSON lines to a local file.
    This is the default exporter — zero dependencies, human-readable.
    """

    def __init__(self, path: str | Path):
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def export_tx(self, tx: "AgentTx") -> None:
        with self._lock:
            try:
                with open(self._path, "a") as f:
                    f.write(json.dumps(tx.to_dict()) + "\n")
            except Exception as e:
                logger.warning(f"JsonlExporter write failed: {e}")

    def export_snapshot(self, snapshot: "Snapshot") -> None:
        # Optionally write snapshots to a separate file
        snap_path = self._path.with_suffix(".snapshots.jsonl")
        with self._lock:
            try:
                with open(snap_path, "a") as f:
                    f.write(json.dumps(snapshot.to_dict()) + "\n")
            except Exception as e:
                logger.warning(f"JsonlExporter snapshot write failed: {e}")


class WebhookExporter(BaseExporter):
    """
    POST transactions to an HTTP endpoint as JSON.
    Batches and retries for reliability. Requires `httpx`.

    Usage::

        exporter = WebhookExporter(
            url="https://your-saas.com/api/v1/ingest",
            headers={"Authorization": "Bearer xxx"},
        )
    """

    def __init__(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        batch_size: int = 10,
        flush_interval: float = 5.0,
        timeout: float = 10.0,
    ):
        self._url = url
        self._headers = headers or {}
        self._batch_size = batch_size
        self._flush_interval = flush_interval
        self._timeout = timeout
        self._buffer: list[dict] = []
        self._lock = threading.Lock()
        self._client = None

        # Start background flusher
        self._stop_event = threading.Event()
        self._flusher = threading.Thread(
            target=self._flush_loop, daemon=True, name="webhook-exporter"
        )
        self._flusher.start()

    def _get_client(self):
        if self._client is None:
            try:
                import httpx
                self._client = httpx.Client(timeout=self._timeout)
            except ImportError:
                raise ImportError(
                    "WebhookExporter requires httpx. "
                    "Install with: pip install agentfinobs[webhook]"
                )
        return self._client

    def export_tx(self, tx: "AgentTx") -> None:
        with self._lock:
            self._buffer.append(tx.to_dict())
            if len(self._buffer) >= self._batch_size:
                self._send_batch()

    def flush(self) -> None:
        with self._lock:
            self._send_batch()

    def close(self) -> None:
        self._stop_event.set()
        self.flush()
        if self._client:
            self._client.close()

    def _send_batch(self):
        """Send buffered transactions. Must be called with lock held."""
        if not self._buffer:
            return
        batch = self._buffer[:]
        self._buffer.clear()

        try:
            client = self._get_client()
            resp = client.post(
                self._url,
                json={"transactions": batch},
                headers=self._headers,
            )
            if resp.status_code >= 400:
                logger.warning(
                    f"Webhook POST failed: {resp.status_code} {resp.text[:200]}"
                )
        except Exception as e:
            logger.warning(f"Webhook POST error: {e}")
            # Put unsent items back (best effort, may lose ordering)
            self._buffer = batch + self._buffer

    def _flush_loop(self):
        while not self._stop_event.is_set():
            self._stop_event.wait(self._flush_interval)
            self.flush()


class ConsoleExporter(BaseExporter):
    """
    Pretty-print transactions to stdout. Useful for development.
    """

    def __init__(self, color: bool = True):
        self._color = color and hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

    def export_tx(self, tx: "AgentTx") -> None:
        pnl = tx.pnl
        pnl_str = f"${pnl:+.4f}" if tx.revenue > 0 else "pending"

        if self._color:
            color = "\033[32m" if pnl > 0 else "\033[31m" if pnl < 0 else "\033[33m"
            reset = "\033[0m"
        else:
            color = reset = ""

        line = (
            f"[agentfinobs] {color}"
            f"${tx.amount:.4f} → {tx.counterparty or 'unknown'} "
            f"| {tx.description or tx.task_id or '-'} "
            f"| pnl={pnl_str}"
            f"{reset}"
        )
        print(line)

    def export_snapshot(self, snapshot: "Snapshot") -> None:
        print(
            f"[agentfinobs] SNAPSHOT: "
            f"txs={snapshot.tx_count} "
            f"spent=${snapshot.total_spent:.2f} "
            f"pnl=${snapshot.total_pnl:+.2f} "
            f"burn=${snapshot.burn_rate_per_hour:.2f}/hr"
        )


class MultiExporter(BaseExporter):
    """
    Fan-out to multiple exporters. Errors in one don't block others.

    Usage::

        multi = MultiExporter([
            JsonlExporter("data/txs.jsonl"),
            WebhookExporter("https://..."),
            ConsoleExporter(),
        ])
    """

    def __init__(self, exporters: list[BaseExporter]):
        self._exporters = exporters

    def add(self, exporter: BaseExporter):
        self._exporters.append(exporter)

    def export_tx(self, tx: "AgentTx") -> None:
        for exp in self._exporters:
            try:
                exp.export_tx(tx)
            except Exception as e:
                logger.warning(f"{exp.__class__.__name__}.export_tx error: {e}")

    def export_snapshot(self, snapshot: "Snapshot") -> None:
        for exp in self._exporters:
            try:
                exp.export_snapshot(snapshot)
            except Exception as e:
                logger.warning(f"{exp.__class__.__name__}.export_snapshot error: {e}")

    def flush(self) -> None:
        for exp in self._exporters:
            try:
                exp.flush()
            except Exception:
                pass

    def close(self) -> None:
        for exp in self._exporters:
            try:
                exp.close()
            except Exception:
                pass
