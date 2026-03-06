"""
channel_memory.py — 频道级记忆读写封装（文件层）
规则：
- boss: 可读所有频道记忆
- 其他频道: 仅可读本频道记忆
- 写入时强制记录 channel
- 检索优先走 memory_index.json，未命中再降级全量扫描
- 写入前执行轻量去重（同频道）
"""
from pathlib import Path
from typing import Optional
import json
import re
from difflib import SequenceMatcher

from memory_meta import write_meta_to_entry, read_all_meta, bump_access

WORKSPACE = Path(__file__).resolve().parent.parent
MEMORY_DIR = WORKSPACE / "memory"
INDEX_FILE = MEMORY_DIR / "memory_index.json"


def _normalize_channel(channel: str) -> str:
    ch = (channel or "").strip().lower().replace("#", "")
    if ch:
        return ch
    name = Path.cwd().name.lower()
    if name.endswith("openclaw-workspace"):
        return "boss"
    mapping = {
        "openclaw-workspace-knowledge": "knowledge",
        "openclaw-workspace-twitter": "twitter-trends",
        "openclaw-workspace-trading": "trading",
        "openclaw-workspace-twitter2xhs": "twitter2xhs",
        "openclaw-workspace-alpha": "alpha",
        "openclaw-workspace-github-push": "github-push",
    }
    return mapping.get(name, "boss")


def _norm_text(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def _is_duplicate(text: str, channel: str, threshold: float = 0.88) -> Optional[dict]:
    """轻量去重：同频道下与已有摘要相似度过高则判重"""
    needle = _norm_text(text)
    if not needle:
        return None

    # 优先用索引
    candidates = []
    if INDEX_FILE.exists():
        try:
            idx = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
            for item in idx:
                ch = item.get("channel", "boss")
                if channel != "boss" and ch != channel:
                    continue
                summary = _norm_text(item.get("summary", ""))
                if not summary:
                    continue
                candidates.append({"summary": summary, **item})
        except Exception:
            candidates = []

    # 索引不可用则退化扫描
    if not candidates:
        for md in sorted(MEMORY_DIR.glob("*.md")):
            entries = read_all_meta(md, channel=channel, boss_full_access=True)
            for e in entries:
                summary = _norm_text(e.get("summary", ""))
                if summary:
                    candidates.append({"summary": summary, **e})

    for c in candidates:
        sim = SequenceMatcher(None, needle, c["summary"]).ratio()
        if sim >= threshold or needle in c["summary"] or c["summary"] in needle:
            c["similarity"] = round(sim, 3)
            return c
    return None


def store_memory(text: str, importance: int = 5, channel: str = "boss", file_name: str = None) -> dict:
    ch = _normalize_channel(channel)

    dup = _is_duplicate(text, ch)
    if dup:
        return {
            "stored": False,
            "reason": "duplicate",
            "channel": ch,
            "duplicate_of": {
                "file": dup.get("file"),
                "line": dup.get("line"),
                "summary": dup.get("summary"),
                "similarity": dup.get("similarity", 1.0),
            },
        }

    file_path = MEMORY_DIR / (file_name or f"{Path.cwd().name}.md")
    if file_name is None:
        from datetime import datetime
        file_path = MEMORY_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.md"
    write_meta_to_entry(file_path, text, importance=importance, channel=ch)
    return {"stored": True, "path": str(file_path), "channel": ch}


def search_memory(channel: str = "boss", keyword: Optional[str] = None, limit: int = 20) -> list[dict]:
    """检索路由：优先索引，索引不可用或未命中时回退扫描。"""
    ch = _normalize_channel(channel)
    key = _norm_text(keyword or "")

    # 1) 索引优先
    if INDEX_FILE.exists():
        try:
            idx = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
            results = []
            for item in idx:
                ich = item.get("channel", "boss")
                if ch != "boss" and ich != ch:
                    continue
                summary = _norm_text(item.get("summary", ""))
                if key and key not in summary:
                    continue
                results.append(item)
            if results:
                return results[:limit]
        except Exception:
            pass

    # 2) 回退全量扫描
    results = []
    for md in sorted(MEMORY_DIR.glob("*.md")):
        entries = read_all_meta(md, channel=ch, boss_full_access=True)
        for e in entries:
            if key and key not in _norm_text(e.get("summary", "")):
                continue
            results.append(e)
    return results[:limit]


def search_and_bump(channel: str = "boss", keyword: Optional[str] = None, limit: int = 20) -> list[dict]:
    hits = search_memory(channel=channel, keyword=keyword, limit=limit)
    for h in hits:
        if h.get("file") and h.get("line"):
            bump_access(Path(h["file"]), h["line"])
    return hits
