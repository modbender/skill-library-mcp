#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import uuid

_CTX_LOCK = threading.Lock()
_AUDIT_LOCK = threading.Lock()
_RUN_CTX: Dict[str, str] = {
    "log_dir": "",
    "run_id": f"run_{uuid.uuid4().hex[:8]}",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sanitize_event_value(v: Any) -> Any:
    if isinstance(v, dict):
        out: Dict[str, Any] = {}
        for k, val in v.items():
            key = str(k).lower()
            if "token" in key or "secret" in key or "password" in key or "authorization" in key:
                out[k] = "***"
            else:
                out[k] = _sanitize_event_value(val)
        return out
    if isinstance(v, list):
        return [_sanitize_event_value(x) for x in v]
    return v


def set_run_context(log_dir: Path, run_id: str) -> None:
    with _CTX_LOCK:
        _RUN_CTX["log_dir"] = str(log_dir.resolve())
        _RUN_CTX["run_id"] = str(run_id or "").strip()


def get_run_context() -> Dict[str, str]:
    with _CTX_LOCK:
        return dict(_RUN_CTX)


def _resolve_log_dir(explicit: Optional[Path] = None) -> Path:
    if explicit is not None:
        return explicit.resolve()
    ctx = get_run_context()
    if ctx.get("log_dir"):
        return Path(ctx["log_dir"]).resolve()
    return Path("logs").resolve()


def setup_logger(name: str, log_dir: Optional[Path] = None) -> logging.Logger:
    target_dir = _resolve_log_dir(log_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    app_log = target_dir / "app.log"
    err_log = target_dir / "error.log"

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    current = getattr(logger, "_nonuse_log_dir", "")
    if current == str(target_dir):
        return logger

    for h in list(logger.handlers):
        logger.removeHandler(h)

    fmt = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    fh_app = logging.FileHandler(app_log, encoding="utf-8")
    fh_app.setLevel(logging.INFO)
    fh_app.setFormatter(fmt)
    logger.addHandler(fh_app)

    fh_err = logging.FileHandler(err_log, encoding="utf-8")
    fh_err.setLevel(logging.ERROR)
    fh_err.setFormatter(fmt)
    logger.addHandler(fh_err)

    logger._nonuse_log_dir = str(target_dir)
    return logger


def audit(event: Dict[str, Any]) -> None:
    ctx = get_run_context()
    log_dir = _resolve_log_dir(None)
    log_dir.mkdir(parents=True, exist_ok=True)
    line = dict(event or {})
    if not line.get("ts"):
        line["ts"] = _now_iso()
    if not line.get("run_id"):
        line["run_id"] = ctx.get("run_id", "")
    if not line.get("type"):
        line["type"] = "unspecified"
    if not line.get("step"):
        line["step"] = "unspecified"
    if line.get("file"):
        try:
            fv = str(line.get("file", "")).strip()
            if fv and not (fv.startswith("http://") or fv.startswith("https://")):
                line["file"] = str(Path(fv).expanduser().resolve())
        except Exception:
            # 审计本身不可中断业务流程，保留原始 file 值。
            line["file"] = str(line.get("file", ""))
    line = _sanitize_event_value(line)
    path = log_dir / "audit.jsonl"
    with _AUDIT_LOCK:
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(line, ensure_ascii=False) + "\n")
