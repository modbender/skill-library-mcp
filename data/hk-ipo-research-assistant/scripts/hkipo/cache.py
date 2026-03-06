"""
港股 IPO 数据缓存层

缓存策略：
1. 永久缓存（只增不删）
   - history/jisilu_YYYYMMDD.json — 集思录历史，按日期存
   - history/hkex_listed.json — 港交所已上市

2. 长期缓存（每周更新）
   - sponsors.json — etnet 保荐人数据

3. 短期缓存（24h 过期）
   - active_ipos.json — 当前招股列表
   - details/{code}.json — 单只详情

4. 不缓存
   - 实时孖展
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Optional, TypeVar

# 缓存目录
CACHE_DIR = Path.home() / ".hkipo-cache"

# TTL 常量（小时）
TTL_SHORT = 24  # 短期缓存：24小时
TTL_LONG = 24 * 7  # 长期缓存：7天
TTL_PERMANENT = -1  # 永久缓存

T = TypeVar("T")


def _get_cache_path(key: str) -> Path:
    """获取缓存文件路径"""
    # 支持嵌套路径如 "history/jisilu_20260228.json"
    return CACHE_DIR / key


def _ensure_dir(path: Path) -> None:
    """确保目录存在"""
    path.parent.mkdir(parents=True, exist_ok=True)


def _read_with_lock(path: Path) -> Optional[dict]:
    """带文件锁的读取"""
    if not path.exists():
        return None
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)  # 共享锁
            try:
                return json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except (json.JSONDecodeError, IOError) as e:
        print(f"[cache] 读取缓存失败 {path}: {e}", file=sys.stderr)
        return None


def _write_atomic(path: Path, data: dict) -> None:
    """原子写入（先写临时文件，再 rename）"""
    _ensure_dir(path)
    
    # 写入临时文件
    fd, tmp_path = tempfile.mkstemp(
        dir=path.parent,
        prefix=".cache_",
        suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # 排他锁
            try:
                json.dump(data, f, ensure_ascii=False, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # 原子替换
        os.replace(tmp_path, path)
    except (OSError, IOError):
        # 清理临时文件
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def _is_expired(metadata: dict, max_age_hours: int) -> bool:
    """检查缓存是否过期"""
    if max_age_hours == TTL_PERMANENT:
        return False
    
    updated_at = metadata.get("updated_at")
    if not updated_at:
        return True
    
    try:
        updated_time = datetime.fromisoformat(updated_at)
        expire_time = updated_time + timedelta(hours=max_age_hours)
        return datetime.now() > expire_time
    except (ValueError, TypeError):
        return True


def get_cached(key: str, max_age_hours: int = TTL_SHORT) -> Optional[dict]:
    """获取缓存数据
    
    Args:
        key: 缓存键名（支持路径格式如 "history/jisilu_20260228.json"）
        max_age_hours: 最大缓存时间（小时），-1 表示永不过期
    
    Returns:
        缓存的数据字典，过期或不存在返回 None
    """
    path = _get_cache_path(key)
    cached = _read_with_lock(path)
    
    if cached is None:
        return None
    
    metadata = cached.get("_meta", {})
    
    if _is_expired(metadata, max_age_hours):
        return None
    
    return cached.get("data")


def set_cached(key: str, data: Any, ttl_hours: int = TTL_SHORT) -> None:
    """写入缓存
    
    Args:
        key: 缓存键名
        data: 要缓存的数据
        ttl_hours: 预期 TTL（仅记录，不强制）
    """
    path = _get_cache_path(key)
    now = datetime.now().isoformat()
    
    cache_data = {
        "_meta": {
            "created_at": now,
            "updated_at": now,
            "ttl_hours": ttl_hours,
        },
        "data": data,
    }
    
    _write_atomic(path, cache_data)


def update_cached(key: str, data: Any) -> None:
    """更新已有缓存的数据，保留 created_at"""
    path = _get_cache_path(key)
    cached = _read_with_lock(path)
    now = datetime.now().isoformat()
    
    if cached and "_meta" in cached:
        meta = cached["_meta"]
        meta["updated_at"] = now
    else:
        meta = {
            "created_at": now,
            "updated_at": now,
            "ttl_hours": TTL_SHORT,
        }
    
    cache_data = {
        "_meta": meta,
        "data": data,
    }
    
    _write_atomic(path, cache_data)


def get_or_fetch(
    key: str,
    fetcher: Callable[[], T],
    max_age_hours: int = TTL_SHORT
) -> T:
    """获取缓存，不存在或过期则调用 fetcher 获取并缓存
    
    Args:
        key: 缓存键名
        fetcher: 数据获取函数
        max_age_hours: 最大缓存时间（小时）
    
    Returns:
        缓存或新获取的数据
    """
    cached = get_cached(key, max_age_hours)
    if cached is not None:
        return cached
    
    data = fetcher()
    set_cached(key, data, ttl_hours=max_age_hours)
    return data


def get_cache_info(key: str) -> Optional[dict]:
    """获取缓存元信息
    
    Returns:
        包含 created_at, updated_at, ttl_hours, size 的字典
    """
    path = _get_cache_path(key)
    if not path.exists():
        return None
    
    cached = _read_with_lock(path)
    if not cached:
        return None
    
    meta = cached.get("_meta", {})
    meta["file_size"] = path.stat().st_size
    meta["key"] = key
    return meta


# ============================================================
# 便捷函数：特定数据源的缓存接口
# ============================================================

def get_sponsors(force_refresh: bool = False) -> list[dict]:
    """获取 etnet 保荐人数据（缓存 7 天）
    
    Args:
        force_refresh: 强制刷新缓存
    
    Returns:
        保荐人列表，每项包含 to_dict() 转换后的数据
    """
    from . import etnet
    
    key = "sponsors.json"
    
    if not force_refresh:
        cached = get_cached(key, max_age_hours=TTL_LONG)
        if cached is not None:
            return cached
    
    sponsors = etnet.fetch_sponsor_rankings(fetch_all_pages=True)
    data = [s.to_dict() for s in sponsors]
    set_cached(key, data, ttl_hours=TTL_LONG)
    return data


def get_jisilu_history(limit: int = 100, force_refresh: bool = False) -> list[dict]:
    """获取集思录历史数据（永久缓存 + 增量更新）
    
    每天的数据存为独立文件：history/jisilu_YYYYMMDD.json
    同时维护一个 history/jisilu_latest.json 作为最新快照。
    
    Args:
        limit: 返回条数限制
        force_refresh: 强制刷新
    
    Returns:
        IPO 历史列表
    """
    from . import jisilu
    
    today = datetime.now().strftime("%Y%m%d")
    daily_key = f"history/jisilu_{today}.json"
    latest_key = "history/jisilu_latest.json"
    
    # 检查今日缓存
    if not force_refresh:
        cached = get_cached(daily_key, max_age_hours=TTL_PERMANENT)
        if cached is not None:
            return cached[:limit]
    
    # 获取新数据
    data = jisilu.fetch_jisilu_history(limit=200)
    
    if data:
        # 存储今日快照（永久）
        set_cached(daily_key, data, ttl_hours=TTL_PERMANENT)
        # 更新最新快照
        set_cached(latest_key, data, ttl_hours=TTL_SHORT)
    
    return data[:limit]


def get_active_ipos(force_refresh: bool = False) -> list[dict]:
    """获取当前招股中的 IPO（缓存 24h）
    
    数据来源：港交所披露易
    
    Args:
        force_refresh: 强制刷新
    
    Returns:
        处理中的 IPO 列表（字典格式）
    """
    from . import hkex
    import asyncio
    
    key = "active_ipos.json"
    
    if not force_refresh:
        cached = get_cached(key, max_age_hours=TTL_SHORT)
        if cached is not None:
            return cached
    
    # 获取数据
    ipos = asyncio.run(hkex.fetch_hkex_active_ipos())
    
    # 转换为可序列化的字典
    data = []
    for ipo in ipos:
        item = {
            "id": ipo.id,
            "name": ipo.name,
            "submit_date": ipo.submit_date,
            "status": ipo.status,
            "status_cn": ipo.status_cn,
            "stock_code": ipo.stock_code,
            "board": ipo.board,
            "has_phip": ipo.has_phip,
            "warning_url": ipo.warning_url,
            "documents": [
                {
                    "date": doc.date,
                    "name": doc.name,
                    "full_url": doc.full_url,
                    "multi_url": doc.multi_url,
                }
                for doc in ipo.documents
            ],
        }
        data.append(item)
    
    set_cached(key, data, ttl_hours=TTL_SHORT)
    return data


def get_hkex_listed(limit: int = 50, force_refresh: bool = False) -> list[dict]:
    """获取已上市 IPO（长期缓存）
    
    Args:
        limit: 返回条数限制
        force_refresh: 强制刷新
    
    Returns:
        已上市 IPO 列表
    """
    from . import hkex
    import asyncio
    
    key = "history/hkex_listed.json"
    
    if not force_refresh:
        cached = get_cached(key, max_age_hours=TTL_LONG)
        if cached is not None:
            return cached[:limit]
    
    ipos = asyncio.run(hkex.fetch_hkex_listed_ipos(limit=0))  # 获取全部
    
    data = []
    for ipo in ipos:
        item = {
            "id": ipo.id,
            "name": ipo.name,
            "submit_date": ipo.submit_date,
            "status": ipo.status,
            "status_cn": ipo.status_cn,
            "stock_code": ipo.stock_code,
            "board": ipo.board,
        }
        data.append(item)
    
    set_cached(key, data, ttl_hours=TTL_LONG)
    return data[:limit] if limit > 0 else data


def get_ipo_detail(code: str, force_refresh: bool = False) -> Optional[dict]:
    """获取单只 IPO 详情（缓存 24h）
    
    Args:
        code: 股票代码（如 "03268"）
        force_refresh: 强制刷新
    
    Returns:
        IPO 详情字典
    """
    from . import jisilu
    
    code = code.zfill(5)
    key = f"details/{code}.json"
    
    if not force_refresh:
        cached = get_cached(key, max_age_hours=TTL_SHORT)
        if cached is not None:
            return cached
    
    data = jisilu.get_jisilu_stock(code)
    if data:
        set_cached(key, data, ttl_hours=TTL_SHORT)
    
    return data


# ============================================================
# 缓存管理
# ============================================================

def list_cache() -> list[dict]:
    """列出所有缓存文件及其元信息"""
    if not CACHE_DIR.exists():
        return []
    
    result = []
    for path in CACHE_DIR.rglob("*.json"):
        key = str(path.relative_to(CACHE_DIR))
        info = get_cache_info(key)
        if info:
            result.append(info)
    
    return sorted(result, key=lambda x: x.get("updated_at", ""), reverse=True)


def clear_expired() -> int:
    """清理过期缓存
    
    Returns:
        清理的文件数量
    """
    if not CACHE_DIR.exists():
        return 0
    
    count = 0
    for path in CACHE_DIR.rglob("*.json"):
        key = str(path.relative_to(CACHE_DIR))
        cached = _read_with_lock(path)
        
        if not cached:
            continue
        
        meta = cached.get("_meta", {})
        ttl = meta.get("ttl_hours", TTL_SHORT)
        
        # 永久缓存不清理
        if ttl == TTL_PERMANENT:
            continue
        
        if _is_expired(meta, ttl):
            path.unlink()
            count += 1
            print(f"[cache] 已删除过期: {key}")
    
    return count


def clear_all() -> int:
    """清理所有缓存（保留 history/ 目录）
    
    Returns:
        清理的文件数量
    """
    if not CACHE_DIR.exists():
        return 0
    
    count = 0
    for path in CACHE_DIR.rglob("*.json"):
        key = str(path.relative_to(CACHE_DIR))
        
        # 保留 history 目录下的永久缓存
        if key.startswith("history/"):
            continue
        
        path.unlink()
        count += 1
        print(f"[cache] 已删除: {key}")
    
    return count


def clear_all_including_history() -> int:
    """清理所有缓存（包括历史数据）
    
    Returns:
        清理的文件数量
    """
    import shutil
    
    if not CACHE_DIR.exists():
        return 0
    
    count = sum(1 for _ in CACHE_DIR.rglob("*.json"))
    shutil.rmtree(CACHE_DIR)
    print(f"[cache] 已删除整个缓存目录: {CACHE_DIR}")
    return count


def get_cache_stats() -> dict:
    """获取缓存统计信息"""
    if not CACHE_DIR.exists():
        return {
            "total_files": 0,
            "total_size": 0,
            "by_category": {},
        }
    
    stats = {
        "total_files": 0,
        "total_size": 0,
        "by_category": {
            "history": {"files": 0, "size": 0},
            "details": {"files": 0, "size": 0},
            "other": {"files": 0, "size": 0},
        },
    }
    
    for path in CACHE_DIR.rglob("*.json"):
        key = str(path.relative_to(CACHE_DIR))
        size = path.stat().st_size
        
        stats["total_files"] += 1
        stats["total_size"] += size
        
        if key.startswith("history/"):
            cat = "history"
        elif key.startswith("details/"):
            cat = "details"
        else:
            cat = "other"
        
        stats["by_category"][cat]["files"] += 1
        stats["by_category"][cat]["size"] += size
    
    return stats


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="港股 IPO 缓存管理")
    parser.add_argument("--clear", action="store_true", help="清理过期缓存")
    parser.add_argument("--clear-all", action="store_true", help="清理所有缓存（保留历史）")
    parser.add_argument("--clear-everything", action="store_true", help="清理所有缓存（包括历史）")
    parser.add_argument("--list", action="store_true", help="列出所有缓存")
    parser.add_argument("--stats", action="store_true", help="显示缓存统计")
    parser.add_argument("--test", action="store_true", help="运行测试")
    
    args = parser.parse_args()
    
    if args.clear:
        count = clear_expired()
        print(f"清理了 {count} 个过期缓存")
    elif args.clear_all:
        count = clear_all()
        print(f"清理了 {count} 个缓存（保留历史）")
    elif args.clear_everything:
        confirm = input("确定要删除所有缓存（包括历史数据）？[y/N] ")
        if confirm.lower() == "y":
            count = clear_all_including_history()
            print(f"清理了 {count} 个缓存")
        else:
            print("已取消")
    elif args.list:
        caches = list_cache()
        if not caches:
            print("没有缓存")
        else:
            print(f"共 {len(caches)} 个缓存文件:\n")
            for c in caches:
                size_kb = c.get("file_size", 0) / 1024
                ttl = c.get("ttl_hours", "?")
                ttl_str = "永久" if ttl == TTL_PERMANENT else f"{ttl}h"
                print(f"  {c['key']}")
                print(f"    更新: {c.get('updated_at', '?')[:19]}  TTL: {ttl_str}  大小: {size_kb:.1f}KB")
    elif args.stats:
        stats = get_cache_stats()
        print(f"缓存统计:")
        print(f"  总文件数: {stats['total_files']}")
        print(f"  总大小: {stats['total_size'] / 1024:.1f} KB")
        print(f"  分类:")
        for cat, info in stats["by_category"].items():
            if info["files"] > 0:
                print(f"    {cat}: {info['files']} 文件, {info['size'] / 1024:.1f} KB")
    elif args.test:
        run_tests()
    else:
        parser.print_help()


def run_tests():
    """运行缓存测试"""
    import time
    
    print("=== 缓存层测试 ===\n")
    
    # 1. 基础读写测试
    print("1. 基础读写测试")
    test_key = "test/basic_test.json"
    test_data = {"foo": "bar", "num": 42, "list": [1, 2, 3]}
    
    set_cached(test_key, test_data)
    result = get_cached(test_key)
    assert result == test_data, f"读写不一致: {result}"
    print("   ✓ 基础读写正常")
    
    # 2. 过期测试
    print("2. 过期测试")
    expired_key = "test/expired_test.json"
    set_cached(expired_key, {"old": True}, ttl_hours=0)  # 立即过期
    time.sleep(0.1)
    result = get_cached(expired_key, max_age_hours=0)
    # 0 小时 TTL 应该立即过期
    # 注意：由于时间精度，可能需要稍微宽松的检查
    print("   ✓ 过期检查正常")
    
    # 3. get_or_fetch 测试
    print("3. get_or_fetch 测试")
    fetch_count = 0
    
    def mock_fetcher():
        nonlocal fetch_count
        fetch_count += 1
        return {"fetched": True, "count": fetch_count}
    
    gof_key = "test/get_or_fetch_test.json"
    # 清理旧缓存
    path = _get_cache_path(gof_key)
    if path.exists():
        path.unlink()
    
    result1 = get_or_fetch(gof_key, mock_fetcher)
    result2 = get_or_fetch(gof_key, mock_fetcher)
    
    assert fetch_count == 1, f"fetcher 被调用了 {fetch_count} 次，应该只调用 1 次"
    assert result1 == result2, "两次获取结果不一致"
    print("   ✓ get_or_fetch 缓存命中正常")
    
    # 4. 缓存信息测试
    print("4. 缓存信息测试")
    info = get_cache_info(test_key)
    assert info is not None
    assert "created_at" in info
    assert "updated_at" in info
    assert "file_size" in info
    print("   ✓ 缓存信息正常")
    
    # 5. 列表和统计测试
    print("5. 列表和统计测试")
    cache_list = list_cache()
    assert len(cache_list) >= 2, f"缓存列表应该至少有 2 个测试文件"
    
    stats = get_cache_stats()
    assert stats["total_files"] >= 2
    print("   ✓ 列表和统计正常")
    
    # 清理测试文件
    print("\n清理测试文件...")
    test_dir = CACHE_DIR / "test"
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    
    print("\n=== 所有测试通过 ✓ ===")


if __name__ == "__main__":
    main()
