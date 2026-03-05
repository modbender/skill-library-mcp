"""OKX Exchange Skill — Structured logging

Environment variables:
  OKX_LOG_LEVEL  : DEBUG | INFO | WARNING | ERROR  (default: INFO)
  OKX_LOG_FORMAT : text | json                     (default: text)
  OKX_CRON_MODE  : 1 to suppress INFO output       (default: 0)
"""
import json
import logging
import os
import sys
from datetime import datetime, timezone

_LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}

_level = _LOG_LEVELS.get(os.getenv("OKX_LOG_LEVEL", "INFO").upper(), logging.INFO)
_json_mode = os.getenv("OKX_LOG_FORMAT", "text").lower() == "json"
_cron_mode = os.getenv("OKX_CRON_MODE", "0") == "1"


class _OKXFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        msg = record.getMessage()
        if _json_mode:
            return json.dumps({
                "ts": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "msg": msg,
            })
        if record.levelno == logging.DEBUG:
            return f"[DBG] {msg}"
        if record.levelno == logging.WARNING:
            return f"⚠️  {msg}"
        if record.levelno >= logging.ERROR:
            return f"❌ {msg}"
        return msg  # INFO: pass through unchanged (preserves table formatting)


def get_logger(name: str = "okx") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # In cron mode: only WARNING+ to stderr; otherwise respect OKX_LOG_LEVEL to stdout
    if _cron_mode:
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.WARNING)
    else:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(_level)

    handler.setFormatter(_OKXFormatter())
    logger.addHandler(handler)
    logger.propagate = False
    return logger
