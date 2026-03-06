"""
memory_consistency.py
跨层一致性校验（阶段3）
- 校验 MEMORY.md 中记录的 Discord 频道ID 是否与 ~/.openclaw/openclaw.json bindings 一致
- 生成报告: memory/consistency-report.json
"""
import json
import re
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).resolve().parent.parent
MEMORY_MD = WORKSPACE / "MEMORY.md"
REPORT = WORKSPACE / "memory" / "consistency-report.json"
CONFIG = Path.home() / ".openclaw" / "openclaw.json"


def extract_channel_ids_from_memory() -> set[str]:
    text = MEMORY_MD.read_text(encoding="utf-8") if MEMORY_MD.exists() else ""
    # 抓 16~20 位纯数字（Discord snowflake）
    ids = set(re.findall(r"\b\d{16,20}\b", text))
    return ids


def extract_channel_ids_from_config() -> set[str]:
    if not CONFIG.exists():
        return set()
    obj = json.loads(CONFIG.read_text(encoding="utf-8"))
    out = set()
    for b in obj.get("bindings", []):
        pid = (((b.get("match") or {}).get("peer") or {}).get("id"))
        if isinstance(pid, str) and pid.isdigit():
            out.add(pid)
    return out


def run() -> dict:
    mem_ids = extract_channel_ids_from_memory()
    cfg_ids = extract_channel_ids_from_config()

    only_in_memory = sorted(mem_ids - cfg_ids)
    only_in_config = sorted(cfg_ids - mem_ids)
    overlap = sorted(mem_ids & cfg_ids)

    report = {
        "generatedAt": datetime.now().isoformat(),
        "memoryCount": len(mem_ids),
        "configCount": len(cfg_ids),
        "overlapCount": len(overlap),
        "onlyInMemory": only_in_memory,
        "onlyInConfig": only_in_config,
        "status": "ok" if not only_in_memory else "warn",
    }

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    r = run()
    print(json.dumps(r, ensure_ascii=False, indent=2))
