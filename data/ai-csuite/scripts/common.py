from __future__ import annotations

from pathlib import Path
from typing import Any

REQUIRED_KEYS = [
    "company_name",
    "product",
    "stage",
    "arr_or_mrr",
    "runway_months",
    "team_size",
    "constraints",
]

STAGE_ALIASES = {
    "solo founder": "solo",
    "solo": "solo",
    "pre-seed": "pre-seed",
    "preseed": "pre-seed",
    "seed": "seed",
    "series-a": "series-a",
    "series a": "series-a",
}

PROFILES: dict[str, dict[str, Any]] = {
    "solo": {"rounds": 2, "agents": ["CEO", "CTO", "CPO", "CFO", "CoS"]},
    "pre-seed": {"rounds": 2, "agents": ["CEO", "CTO", "CPO", "CoS", "CV"]},
    "seed": {"rounds": 3, "agents": ["CEO", "CTO", "CPO", "CMO", "CRO", "CoS", "CV"]},
    "series-a": {
        "rounds": 3,
        "agents": ["CEO", "CTO", "CPO", "CFO", "CMO", "CRO", "COO", "CSA", "CISO", "CoS", "CV"],
    },
}


def parse_simple_yaml(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    list_key = ""
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- ") and list_key:
            data.setdefault(list_key, []).append(line[2:].strip().strip("\"'"))
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value:
            data[key] = value.strip("\"'")
            list_key = ""
        else:
            data[key] = []
            list_key = key
    return data


def load_company(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Missing company context file: {file_path}")
    data = parse_simple_yaml(file_path.read_text(encoding="utf-8"))
    missing = [k for k in REQUIRED_KEYS if k not in data or data[k] in ("", [], None)]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")
    data["stage"] = normalize_stage(str(data["stage"]))
    if data["stage"] not in PROFILES:
        raise ValueError(f"Unsupported stage: {data['stage']}")
    if not isinstance(data.get("constraints"), list):
        data["constraints"] = [str(data["constraints"])]
    return data


def normalize_stage(raw: str) -> str:
    return STAGE_ALIASES.get(raw.strip().lower(), raw.strip().lower())


def to_float(value: Any) -> float:
    text = str(value)
    digits = "".join(ch for ch in text if ch.isdigit() or ch == ".")
    return float(digits) if digits else 0.0


def profile_for_stage(stage: str) -> dict[str, Any]:
    return PROFILES[stage]


def ensure_logs(root_dir: Path) -> Path:
    logs_dir = root_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir
