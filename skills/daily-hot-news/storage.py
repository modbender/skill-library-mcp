# -*- coding: utf-8 -*-
"""
每日热榜 Skill - 数据存储模块

功能：
- 自动保存每日热榜数据
- 查询历史热榜记录
- 管理数据文件
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from config import config


class DataStorage:
    """数据存储类"""

    def __init__(self):
        self.data_dir = config.data_dir
        self.auto_save = config.auto_save
        os.makedirs(self.data_dir, exist_ok=True)

    def save_hot_list(self, source_id: str, data: Dict[str, Any]) -> bool:
        """
        保存热榜数据到文件

        Args:
            source_id: 热榜源 ID（如 weibo, zhihu）
            data: 热榜数据字典

        Returns:
            是否保存成功
        """
        if not self.auto_save:
            return False

        try:
            # 获取今日日期的文件路径
            file_path = config.get_data_path(source_id)

            # 构建存储结构
            storage_data = {
                "source_id": source_id,
                "save_time": datetime.now().isoformat(),
                "update_time": data.get("update_time", ""),
                "total": data.get("total", 0),
                "data": data.get("data", [])
            }

            # 读取现有数据（如果有）
            existing_data = []
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        existing_data = json.load(f)
                        if not isinstance(existing_data, list):
                            existing_data = []
                    except:
                        existing_data = []

            # 添加新数据到列表
            existing_data.append(storage_data)

            # 保存到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            print(f"[DataStorage] 保存失败: {e}")
            return False

    def load_history(self, source_id: str = "", days: int = 7) -> Dict[str, List[Dict]]:
        """
        加载历史热榜数据

        Args:
            source_id: 热榜源 ID（空则加载所有源）
            days: 加载最近几天的数据

        Returns:
            按日期组织的热榜数据
        """
        result = {}

        if source_id:
            # 加载指定源的历史数据
            source_dir = os.path.join(self.data_dir, source_id)
            if not os.path.exists(source_dir):
                return {}

            for i in range(days):
                date_str = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                file_path = os.path.join(source_dir, f"{date_str}.json")

                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        try:
                            data = json.load(f)
                            result[date_str] = data
                        except:
                            continue

        else:
            # 加载所有源的历史数据
            if not os.path.exists(self.data_dir):
                return {}

            for source in os.listdir(self.data_dir):
                source_dir = os.path.join(self.data_dir, source)
                if not os.path.isdir(source_dir):
                    continue

                result[source] = {}
                for i in range(days):
                    date_str = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                    file_path = os.path.join(source_dir, f"{date_str}.json")

                    if os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            try:
                                data = json.load(f)
                                result[source][date_str] = data
                            except:
                                continue

        return result

    def get_saved_dates(self, source_id: str) -> List[str]:
        """
        获取指定热榜源已保存的日期列表

        Args:
            source_id: 热榜源 ID

        Returns:
            已保存的日期列表（降序）
        """
        dates = []
        source_dir = os.path.join(self.data_dir, source_id)

        if not os.path.exists(source_dir):
            return []

        for filename in os.listdir(source_dir):
            if filename.endswith('.json'):
                date_str = filename.replace('.json', '')
                dates.append(date_str)

        return sorted(dates, reverse=True)

    def load_hot_list(self, source_id: str, date_str: str = "") -> Optional[List[Dict]]:
        """
        加载指定日期的热榜数据

        Args:
            source_id: 热榜源 ID
            date_str: 日期（默认今天）

        Returns:
            热榜数据列表
        """
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")

        file_path = config.get_data_path(source_id, date_str)

        if not os.path.exists(file_path):
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                # 返回当天的最后一条记录
                if isinstance(data, list) and len(data) > 0:
                    return data[-1].get("data", [])
            except:
                pass

        return None

    def list_all_data(self) -> Dict[str, int]:
        """
        列出所有已保存的热榜数据统计

        Returns:
            源ID -> 保存记录数
        """
        stats = {}

        if not os.path.exists(self.data_dir):
            return {}

        for source in os.listdir(self.data_dir):
            source_dir = os.path.join(self.data_dir, source)
            if not os.path.isdir(source_dir):
                continue

            count = 0
            for filename in os.listdir(source_dir):
                if filename.endswith('.json'):
                    count += 1

            if count > 0:
                stats[source] = count

        return stats

    def clear_old_data(self, keep_days: int = 30) -> int:
        """
        清理旧数据

        Args:
            keep_days: 保留最近几天的数据

        Returns:
            删除的文件数量
        """
        deleted_count = 0
        cutoff_date = datetime.now() - timedelta(days=keep_days)

        if not os.path.exists(self.data_dir):
            return 0

        for source in os.listdir(self.data_dir):
            source_dir = os.path.join(self.data_dir, source)
            if not os.path.isdir(source_dir):
                continue

            for filename in os.listdir(source_dir):
                if not filename.endswith('.json'):
                    continue

                try:
                    file_date = datetime.strptime(filename.replace('.json', ''), "%Y-%m-%d")
                    if file_date < cutoff_date:
                        file_path = os.path.join(source_dir, filename)
                        os.remove(file_path)
                        deleted_count += 1
                except:
                    continue

        return deleted_count


# 全局存储实例
storage = DataStorage()


def auto_save_hot_list(source_id: str, data: Dict[str, Any]) -> bool:
    """
    自动保存热榜数据的便捷函数

    在获取热榜数据后调用此函数保存数据
    """
    return storage.save_hot_list(source_id, data)


if __name__ == "__main__":
    # 测试存储功能
    print("📊 每日热榜数据存储管理")
    print("=" * 50)

    # 列出所有数据
    stats = storage.list_all_data()
    if stats:
        print("\n已保存的热榜数据：")
        for source, count in stats.items():
            print(f"  • {source}: {count} 条记录")
    else:
        print("\n暂无保存的数据")

    # 列出已保存的日期
    print("\n已保存的日期（微博）：")
    dates = storage.get_saved_dates("weibo")
    if dates:
        for date in dates[:7]:
            print(f"  • {date}")
    else:
        print("  暂无数据")
