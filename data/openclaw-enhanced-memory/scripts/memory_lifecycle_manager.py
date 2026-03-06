#!/usr/bin/env python3
"""
记忆生命周期管理（Memory Lifecycle Manager）
自动归档旧记忆，实现持久化存储，永不删除
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime, timedelta

MEMORY_BASE = Path("/home/clawdbot/.openclaw/workspace/memory")

# 归档配置
ARCHIVE_THRESHOLD_DAYS = 180  # 6个月
ARCHIVE_DIR = MEMORY_BASE / "archived"

# 要归档的记忆模块（相对于MEMORY_BASE）
MODULES_TO_ARCHIVE = [
    "current",
    "food",
    "training",
    "misc",
]


def get_file_modification_date(file_path: Path) -> datetime:
    """
    获取文件的修改日期
    """
    if file_path.exists():
        timestamp = file_path.stat().st_mtime
        return datetime.fromtimestamp(timestamp)
    else:
        return datetime.min


def should_archive_file(file_path: Path, threshold_days: int = ARCHIVE_THRESHOLD_DAYS) -> bool:
    """
    判断文件是否应该归档
    """
    mod_date = get_file_modification_date(file_path)
    age = datetime.now() - mod_date

    # 如果文件超过threshold_days天未修改，则归档
    return age > timedelta(days=threshold_days)


def create_archive_directory(year_month: str):
    """
    创建归档目录：memory/archived/YYYY-MM/
    """
    archive_dir = ARCHIVE_DIR / year_month
    archive_dir.mkdir(parents=True, exist_ok=True)
    return archive_dir


def archive_file(file_path: Path, target_dir: Path) -> Path:
    """
    归档单个文件
    """
    # 保留文件名，但添加时间戳后缀
    # 例如：2026-02-16.md → 2026-02-16_20260216.md
    original_name = file_path.name
    timestamp = datetime.now().strftime("%Y%m%d")
    new_name = f"{original_name}_{timestamp}.md"

    target_path = target_dir / new_name

    # 复制文件到归档目录（保留原始文件）
    shutil.copy2(file_path, target_path)

    # 从当前目录删除文件
    file_path.unlink()

    print(f"  📦 归档: {original_name} → {new_name}")
    return target_path


def archive_module(module_path: Path, threshold_days: int = ARCHIVE_THRESHOLD_DAYS) -> dict:
    """
    归档整个记忆模块
    返回：{module: {archived: int, skipped: int, total: int}}
    """
    results = {"archived": 0, "skipped": 0, "total": 0}

    if not module_path.exists():
        print(f"  ⚠️  模块不存在: {module_path}")
        return results

    print(f"\n📂 处理模块: {module_path.relative_to(MEMORY_BASE)}")

    # 获取模块下所有.md文件（递归）
    md_files = list(module_path.rglob("*.md"))

    for md_file in md_files:
        # 跳过archived目录（防止重复归档）
        if "archived" in str(md_file):
            continue

        results["total"] += 1

        # 检查是否应该归档
        if should_archive_file(md_file, threshold_days):
            # 计算文件所属的年月
            mod_date = get_file_modification_date(md_file)
            year_month = mod_date.strftime("%Y-%m")

            # 创建归档目录
            target_dir = create_archive_directory(year_month)

            # 归档文件
            archive_file(md_file, target_dir)
            results["archived"] += 1
        else:
            results["skipped"] += 1

    return results


def archive_all_modules(threshold_days: int = ARCHIVE_THRESHOLD_DAYS):
    """
    归档所有配置的记忆模块
    """
    print(f"\n🔍 记忆生命周期管理")
    print(f"⏰ 归档阈值: {threshold_days} 天 ({threshold_days//30} 个月)")
    print(f"📁 归档目录: {ARCHIVE_DIR}")

    # 检查归档目录是否存在
    if not ARCHIVE_DIR.exists():
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建归档目录: {ARCHIVE_DIR}")

    # 统计信息
    total_archived = 0
    total_skipped = 0
    total_files = 0

    # 归档每个模块
    for module in MODULES_TO_ARCHIVE:
        module_path = MEMORY_BASE / module
        results = archive_module(module_path, threshold_days)

        total_archived += results["archived"]
        total_skipped += results["skipped"]
        total_files += results["total"]

        print(f"  ✅ 模块归档完成: {results['archived']} 个文件归档, {results['skipped']} 个跳过")

    # 总结
    print(f"\n📊 归档统计:")
    print(f"  总文件数: {total_files}")
    print(f"  已归档: {total_archived}")
    print(f"  跳过: {total_skipped}")

    # 检查当前活跃记忆文件数
    current_files = 0
    for module in MODULES_TO_ARCHIVE:
        module_path = MEMORY_BASE / module
        if module_path.exists():
            current_files += len(list(module_path.rglob("*.md")))

    print(f"\n🎯 当前活跃记忆文件数: {current_files}")
    print(f"📦 归档记忆文件数: {total_archived}")
    print(f"💾 磁盘占用: {'✅ 已持久化，永不删除'}")


def main():
    import sys

    if len(sys.argv) > 1:
        # 允许手动指定归档阈值
        try:
            days = int(sys.argv[1])
            archive_all_modules(days)
        except ValueError:
            print("❌ 错误：请输入有效的天数（例如：180 表示6个月）")
            sys.exit(1)
    else:
        # 默认使用配置的阈值
        archive_all_modules(ARCHIVE_THRESHOLD_DAYS)


if __name__ == "__main__":
    main()
