"""
memory_decay.py — 记忆衰减与归档引擎（含白名单锁 + 命中反馈学习）
每日执行：扫描 → 计算权重 → 命中反馈升权 → 归档低权重条目 → 重建索引
"""
import json
from datetime import date, datetime
from pathlib import Path

from memory_meta import read_all_meta, parse_meta, format_meta, bump_access, META_PATTERN

MEMORY_DIR = Path(__file__).resolve().parent.parent / "memory"
ARCHIVE_DIR = MEMORY_DIR / ".archive"
INDEX_FILE = MEMORY_DIR / "memory_index.json"
PINNED_FILE = MEMORY_DIR / "pinned.json"

# 衰减参数
ACCESS_BONUS = 0.5       # 每次访问加分（上限 10 次）
ACCESS_CAP = 10          # 访问次数加分上限
DECAY_RATE = 0.3         # 每天未访问扣分
ARCHIVE_THRESHOLD = 2.0  # 低于此值归档
PROTECT_IMPORTANCE = 8   # >= 此值永不归档

# 命中反馈学习参数
HIGH_HIT_THRESHOLD = 5   # 访问次数 >= 此值，自动升权
HIGH_HIT_BOOST = 1       # 升权幅度
MAX_IMPORTANCE = 10      # importance 上限
LOW_HIT_DAYS = 30        # 超过此天数未访问且 importance < 5，候选降权
LOW_HIT_PENALTY = 1      # 降权幅度
MIN_IMPORTANCE = 1       # importance 下限


def load_pinned() -> set[str]:
    """加载白名单（pinned 记忆的摘要集合）"""
    if not PINNED_FILE.exists():
        return set()
    try:
        data = json.loads(PINNED_FILE.read_text(encoding="utf-8"))
        return set(data.get("pinned", []))
    except Exception:
        return set()


def save_pinned(pinned: set[str]):
    """保存白名单"""
    PINNED_FILE.write_text(
        json.dumps({"pinned": sorted(pinned), "updatedAt": datetime.now().isoformat()},
                   ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def pin_memory(summary: str):
    """将一条记忆加入白名单（永不归档/删除）"""
    pinned = load_pinned()
    pinned.add(summary.strip())
    save_pinned(pinned)


def unpin_memory(summary: str):
    """从白名单移除"""
    pinned = load_pinned()
    pinned.discard(summary.strip())
    save_pinned(pinned)


def is_pinned(summary: str) -> bool:
    """检查是否在白名单"""
    pinned = load_pinned()
    return summary.strip() in pinned


def calc_weight(importance: int, access_count: int, days_since: int) -> float:
    """计算记忆权重"""
    return importance + min(access_count, ACCESS_CAP) * ACCESS_BONUS - days_since * DECAY_RATE


def scan_all() -> list[dict]:
    """扫描 memory/ 下所有 .md 文件，提取元数据"""
    all_entries = []
    for md_file in sorted(MEMORY_DIR.glob("*.md")):
        entries = read_all_meta(md_file)
        all_entries.extend(entries)
    return all_entries


def apply_hit_feedback(entries: list[dict]) -> dict:
    """命中反馈学习：高频命中升权，长期未命中降权"""
    today = date.today()
    feedback_stats = {"boosted": 0, "penalized": 0}

    for entry in entries:
        filepath = Path(entry["file"])
        if not filepath.exists():
            continue

        lines = filepath.read_text(encoding="utf-8").splitlines()
        idx = entry["line"] - 1
        if idx < 0 or idx >= len(lines):
            continue

        meta = parse_meta(lines[idx])
        if not meta:
            continue

        changed = False
        imp = meta["importance"]
        acc = meta["access_count"]
        last = date.fromisoformat(meta["last_accessed"])
        days_since = (today - last).days

        # 高频命中升权
        if acc >= HIGH_HIT_THRESHOLD and imp < MAX_IMPORTANCE:
            imp = min(imp + HIGH_HIT_BOOST, MAX_IMPORTANCE)
            changed = True
            feedback_stats["boosted"] += 1

        # 长期未命中降权（仅对低重要性）
        if days_since >= LOW_HIT_DAYS and imp < 5 and imp > MIN_IMPORTANCE:
            imp = max(imp - LOW_HIT_PENALTY, MIN_IMPORTANCE)
            changed = True
            feedback_stats["penalized"] += 1

        if changed:
            new_meta = format_meta(
                imp, acc, meta["created"], meta["last_accessed"],
                channel=meta.get("channel", "boss"),
            )
            lines[idx] = META_PATTERN.sub(new_meta, lines[idx])
            filepath.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return feedback_stats


def decay_and_archive() -> dict:
    """执行衰减计算，归档低权重条目（含白名单保护）"""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today()
    pinned = load_pinned()
    stats = {"scanned": 0, "archived": 0, "protected": 0, "pinned_protected": 0, "active": 0}
    entries = scan_all()
    stats["scanned"] = len(entries)

    files_to_archive = {}

    for entry in entries:
        last_accessed = date.fromisoformat(entry["last_accessed"])
        days_since = (today - last_accessed).days
        weight = calc_weight(entry["importance"], entry["access_count"], days_since)
        entry["weight"] = round(weight, 2)
        entry["days_since"] = days_since

        summary = entry.get("summary", "").strip()

        # 白名单锁：pinned 记忆绝对不归档
        if summary in pinned:
            stats["pinned_protected"] += 1
            stats["active"] += 1
            continue

        # importance >= 8 绝对保护
        if entry["importance"] >= PROTECT_IMPORTANCE:
            stats["protected"] += 1
            stats["active"] += 1
            continue

        if weight < ARCHIVE_THRESHOLD:
            fp = entry["file"]
            if fp not in files_to_archive:
                files_to_archive[fp] = []
            files_to_archive[fp].append(entry)
            stats["archived"] += 1
        else:
            stats["active"] += 1

    # 执行归档
    for filepath_str, entries_to_remove in files_to_archive.items():
        filepath = Path(filepath_str)
        archive_path = ARCHIVE_DIR / filepath.name

        archive_content = ""
        if archive_path.exists():
            archive_content = archive_path.read_text(encoding="utf-8")
        with open(archive_path, "a", encoding="utf-8") as f:
            if not archive_content:
                f.write(f"# Archived from {filepath.name}\n\n")
            for e in entries_to_remove:
                f.write(f"[archived {today.isoformat()}] {e['summary']}\n")
                f.write(f"<!-- meta: importance={e['importance']} access={e['access_count']} "
                        f"created={e['created']} last_accessed={e['last_accessed']} "
                        f"channel={e.get('channel','boss')} weight={e['weight']} -->\n\n")

        lines = filepath.read_text(encoding="utf-8").splitlines()
        remove_lines = set()
        for e in entries_to_remove:
            meta_line = e["line"] - 1
            remove_lines.add(meta_line)
            for j in range(meta_line - 1, -1, -1):
                stripped = lines[j].strip()
                if stripped and not stripped.startswith("<!--"):
                    remove_lines.add(j)
                    break

        new_lines = [l for i, l in enumerate(lines) if i not in remove_lines]
        filepath.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    return stats


def build_index() -> int:
    """全量扫描并生成 memory_index.json"""
    today = date.today()
    pinned = load_pinned()
    entries = scan_all()
    index = []

    for entry in entries:
        last_accessed = date.fromisoformat(entry["last_accessed"])
        days_since = (today - last_accessed).days
        weight = calc_weight(entry["importance"], entry["access_count"], days_since)
        summary = entry.get("summary", "").strip()
        index.append({
            "file": entry["file"],
            "line": entry["line"],
            "summary": summary,
            "channel": entry.get("channel", "boss"),
            "importance": entry["importance"],
            "access_count": entry["access_count"],
            "created": entry["created"],
            "last_accessed": entry["last_accessed"],
            "weight": round(weight, 2),
            "pinned": summary in pinned,
        })

    index.sort(key=lambda x: x["weight"], reverse=True)

    INDEX_FILE.write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return len(index)


def run():
    """完整执行：命中反馈 → 衰减归档 → 索引重建"""
    print(f"[{datetime.now().isoformat()}] 开始记忆维护...")

    # 阶段5：命中反馈学习
    entries = scan_all()
    fb = apply_hit_feedback(entries)
    print(f"  命中反馈: 升权 {fb['boosted']} | 降权 {fb['penalized']}")

    # 衰减归档（含阶段4白名单保护）
    stats = decay_and_archive()
    print(f"  扫描: {stats['scanned']} | 活跃: {stats['active']} | "
          f"保护(imp>=8): {stats['protected']} | 白名单保护: {stats['pinned_protected']} | "
          f"归档: {stats['archived']}")

    count = build_index()
    print(f"  索引重建完成，共 {count} 条活跃记忆")
    return {**stats, **fb}


if __name__ == "__main__":
    run()
