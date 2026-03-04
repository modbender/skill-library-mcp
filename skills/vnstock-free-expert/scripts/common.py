#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class RateLimiter:
    min_interval_sec: float = 3.2
    last_call_ts: float = 0.0

    def wait(self) -> None:
        now = time.time()
        elapsed = now - self.last_call_ts
        if elapsed < self.min_interval_sec:
            time.sleep(self.min_interval_sec - elapsed)
        self.last_call_ts = time.time()


def safe_float(v) -> Optional[float]:
    try:
        if v is None:
            return None
        if isinstance(v, str):
            v = v.replace(",", "").replace("%", "").strip()
        f = float(v)
        if math.isfinite(f):
            return f
    except Exception:
        return None
    return None


def find_metric(df, candidates: List[str]) -> Optional[float]:
    if df is None or df.empty:
        return None

    local = df.copy()
    local.columns = [str(c).strip().lower() for c in local.columns]

    for c in local.columns:
        for k in candidates:
            if k in c:
                v = local.iloc[0][c]
                fv = safe_float(v)
                if fv is not None:
                    return fv

    item_cols = [c for c in local.columns if c in {"item", "item_id", "item_en"}]
    period_cols = [
        c
        for c in local.columns
        if c not in {"item", "item_id", "item_en", "unit", "levels", "row_number"}
    ]
    if item_cols and period_cols:
        id_col = item_cols[0]
        latest_col = sorted(period_cols, reverse=True)[0]
        for _, row in local.iterrows():
            name = str(row.get(id_col, "")).lower()
            if any(k in name for k in candidates):
                fv = safe_float(row.get(latest_col))
                if fv is not None:
                    return fv
    return None


def pct_return(history, days: int) -> Optional[float]:
    if history is None or history.empty or "close" not in history.columns:
        return None
    h = history.sort_values("time").copy()
    if len(h) < days + 1:
        return None
    start_price = safe_float(h.iloc[-days - 1]["close"])
    end_price = safe_float(h.iloc[-1]["close"])
    if start_price is None or end_price is None or start_price == 0:
        return None
    return (end_price / start_price - 1.0) * 100.0


def zscore(series, reverse: bool = False):
    clean = series.astype(float)
    std = clean.std(ddof=0)
    if std == 0 or str(std) == "nan":
        z = clean * 0
    else:
        z = (clean - clean.mean()) / std
    return -z if reverse else z


def ensure_outdir(outdir: str) -> Path:
    p = Path(outdir)
    p.mkdir(parents=True, exist_ok=True)
    return p


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def write_latest_alias(path: Path, alias_name: str) -> None:
    alias = path.parent / alias_name
    alias.write_text(str(path), encoding="utf-8")


def write_json(path: Path, payload: Dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _read_env_file(path: Path) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        out[k.strip()] = v.strip().strip("'").strip('"')
    return out


def resolve_vnstock_api_key(explicit_key: Optional[str] = None) -> Optional[str]:
    if explicit_key:
        return explicit_key.strip()

    env_key = os.getenv("VNSTOCK_API_KEY")
    if env_key:
        return env_key.strip()

    # Skill-local fallback: <skill_root>/.env
    # scripts/common.py -> skill root is parents[1]
    env_path = Path(__file__).resolve().parents[1] / ".env"
    values = _read_env_file(env_path)
    file_key = values.get("VNSTOCK_API_KEY", "").strip()
    return file_key or None


def configure_vnstock_api_key(explicit_key: Optional[str] = None) -> bool:
    key = resolve_vnstock_api_key(explicit_key)
    if not key:
        return False

    try:
        from vnstock.core.utils.auth import change_api_key

        change_api_key(key)
        return True
    except Exception:
        # Best-effort: continue even if auth helper is unavailable in this runtime.
        return False
