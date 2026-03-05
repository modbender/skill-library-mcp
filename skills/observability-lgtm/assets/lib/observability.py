"""
openclaw observability — drop-in for FastAPI apps.

Usage:
    from observability import setup_observability
    setup_observability(app, service_name="my-service")

What you get:
    • /metrics          — Prometheus endpoint (auto-scraped)
    • Structured JSON logs → Loki (via Alloy log scraping)
    • OpenTelemetry traces → Tempo (OTLP gRPC on localhost:4317)
    • Langfuse integration preserved (existing Langfuse usage unaffected)

Deps (add to requirements.txt):
    prometheus-fastapi-instrumentator>=7.0.0
    opentelemetry-sdk>=1.25.0
    opentelemetry-exporter-otlp-proto-grpc>=1.25.0
    opentelemetry-instrumentation-fastapi>=0.46b0
    python-json-logger>=2.0.7
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Callable

# ── Optional imports (graceful degradation) ───────────────────────────────────
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    _HAS_PROM = True
except ImportError:
    _HAS_PROM = False

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.resources import Resource, SERVICE_NAME
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    _HAS_OTEL = True
except ImportError:
    _HAS_OTEL = False

try:
    from pythonjsonlogger import jsonlogger
    _HAS_JSONLOG = True
except ImportError:
    _HAS_JSONLOG = False


# ── Log directory ─────────────────────────────────────────────────────────────
_LOG_BASE = Path(os.environ.get(
    "OPENCLAW_LOG_DIR",
    Path(__file__).parent.parent / "logs",   # relative to observability/
))


def _setup_logging(service_name: str, log_level: int = logging.INFO) -> logging.Logger:
    """
    Configure root logger with:
      - JSON formatter → file  (Alloy scrapes this → Loki)
      - Plain formatter → stderr (local dev readability)

    Log file: <OPENCLAW_LOG_DIR>/<service_name>/app.log
    """
    log_dir = _LOG_BASE / service_name
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"

    root = logging.getLogger()
    root.setLevel(log_level)

    # Avoid adding duplicate handlers on re-import
    if any(isinstance(h, logging.FileHandler) and str(log_file) in str(getattr(h, 'baseFilename', ''))
           for h in root.handlers):
        return logging.getLogger(service_name)

    # JSON handler → file → Alloy → Loki
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    if _HAS_JSONLOG:
        fmt = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
            rename_fields={"asctime": "ts", "levelname": "level", "name": "logger"},
        )
    else:
        # Fallback: manual JSON-ish format (still parseable by Loki)
        fmt = logging.Formatter(
            '{"ts":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","service":"' + service_name + '","msg":"%(message)s"}',
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    file_handler.setFormatter(fmt)
    file_handler.setLevel(log_level)
    root.addHandler(file_handler)

    # Plain stderr handler for local dev
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(logging.Formatter(
        "%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%H:%M:%S",
    ))
    stderr_handler.setLevel(log_level)
    root.addHandler(stderr_handler)

    logger = logging.getLogger(service_name)
    logger.info("Logging initialised", extra={"service": service_name, "log_file": str(log_file)})
    return logger


def _setup_tracing(service_name: str, otlp_endpoint: str) -> None:
    """Configure OpenTelemetry traces → Tempo via OTLP gRPC."""
    if not _HAS_OTEL:
        return

    resource = Resource.create({SERVICE_NAME: service_name})
    provider = TracerProvider(resource=resource)

    exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))

    trace.set_tracer_provider(provider)


def _setup_metrics(app, service_name: str) -> None:
    """Mount Prometheus /metrics endpoint and auto-instrument all FastAPI routes."""
    if not _HAS_PROM:
        return

    Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        excluded_handlers=[r"/metrics", r"/health", r"/static/.*"],
        env_var_name=None,
    ).instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)


def setup_observability(
    app,
    service_name: str,
    *,
    log_level: int = logging.INFO,
    otlp_endpoint: str | None = None,
    enable_traces: bool = True,
    enable_metrics: bool = True,
    enable_logs: bool = True,
) -> logging.Logger:
    """
    One-call setup for all observability pillars.

    Args:
        app:            FastAPI application instance.
        service_name:   Identifier for this service (used in all telemetry labels).
        log_level:      Python logging level. Default INFO.
        otlp_endpoint:  Override OTLP gRPC endpoint. Default: localhost:4317.
        enable_traces:  Send traces to Tempo. Default True.
        enable_metrics: Expose /metrics for Prometheus. Default True.
        enable_logs:    Write JSON logs to file for Alloy→Loki. Default True.

    Returns:
        A configured logger for the service.
    """
    if otlp_endpoint is None:
        otlp_endpoint = os.environ.get("OTLP_ENDPOINT", "localhost:4317")

    logger = logging.getLogger(service_name)

    if enable_logs:
        logger = _setup_logging(service_name, log_level)

    if enable_metrics:
        _setup_metrics(app, service_name)

    if enable_traces:
        _setup_tracing(service_name, otlp_endpoint)
        if _HAS_OTEL:
            FastAPIInstrumentor.instrument_app(
                app,
                tracer_provider=trace.get_tracer_provider(),
                excluded_urls="/metrics,/health,/static/.*",
            )

    logger.info(
        "Observability initialised",
        extra={
            "service": service_name,
            "metrics": enable_metrics and _HAS_PROM,
            "traces": enable_traces and _HAS_OTEL,
            "logs": enable_logs,
            "otlp": otlp_endpoint,
        },
    )
    return logger


# ── Convenience: get a tracer for manual instrumentation ─────────────────────

def get_tracer(name: str = __name__):
    """Get an OpenTelemetry tracer. Call setup_observability() first."""
    if not _HAS_OTEL:
        return _NoopTracer()
    return trace.get_tracer(name)


class _NoopTracer:
    """Fallback when OpenTelemetry is not installed."""
    def start_as_current_span(self, *a, **kw):
        from contextlib import contextmanager
        @contextmanager
        def _noop(*_, **__):
            yield self
        return _noop()
    def set_attribute(self, *a, **kw): pass
    def record_exception(self, *a, **kw): pass
