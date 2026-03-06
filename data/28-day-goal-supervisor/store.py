"""
Habit Tracker - 数据持久化层
JSON 文件读写，带文件锁保护
"""

import json
import os
import fcntl
import shutil
from datetime import datetime
from typing import Optional

from models import UserData


class HabitStore:
    """JSON 文件持久化存储，带文件锁"""

    def __init__(self, data_dir: Optional[str] = None):
        if data_dir:
            self.data_dir = data_dir
        else:
            # 默认存储在 OpenClaw 工作区
            workspace = os.environ.get(
                "OPENCLAW_WORKSPACE",
                os.path.expanduser("~/.openclaw/workspace"),
            )
            self.data_dir = os.path.join(workspace, "data", "habit-tracker")

        os.makedirs(self.data_dir, exist_ok=True)
        self._data_file = os.path.join(self.data_dir, "habits.json")
        self._backup_dir = os.path.join(self.data_dir, "backups")

    def load(self) -> UserData:
        """加载用户数据，文件不存在则返回空数据"""
        if not os.path.exists(self._data_file):
            return UserData()

        try:
            with open(self._data_file, "r", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                try:
                    data = json.load(f)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            return UserData.from_dict(data)
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            # 数据损坏时备份并返回空数据
            self._backup_corrupted(str(e))
            return UserData()

    def save(self, user_data: UserData) -> None:
        """保存用户数据，原子写入 + 文件锁"""
        tmp_file = self._data_file + ".tmp"

        try:
            data = user_data.to_dict()
            with open(tmp_file, "w", encoding="utf-8") as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

            # 原子替换
            os.replace(tmp_file, self._data_file)
        except Exception:
            if os.path.exists(tmp_file):
                os.remove(tmp_file)
            raise

    def _backup_corrupted(self, reason: str) -> None:
        """备份损坏的数据文件"""
        if not os.path.exists(self._data_file):
            return

        os.makedirs(self._backup_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"habits_corrupted_{ts}.json"
        backup_path = os.path.join(self._backup_dir, backup_name)
        shutil.copy2(self._data_file, backup_path)

        # 写入错误日志
        log_path = os.path.join(self._backup_dir, f"error_{ts}.txt")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"Corruption detected: {reason}\n")
            f.write(f"Original file backed up to: {backup_name}\n")

    def create_backup(self) -> str:
        """手动创建备份，返回备份路径"""
        os.makedirs(self._backup_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"habits_backup_{ts}.json"
        backup_path = os.path.join(self._backup_dir, backup_name)

        if os.path.exists(self._data_file):
            shutil.copy2(self._data_file, backup_path)

        # 清理超过 30 天的备份
        self._cleanup_old_backups(max_age_days=30)

        return backup_path

    def _cleanup_old_backups(self, max_age_days: int = 30) -> None:
        """清理超期备份"""
        if not os.path.exists(self._backup_dir):
            return

        now = datetime.now().timestamp()
        for fname in os.listdir(self._backup_dir):
            fpath = os.path.join(self._backup_dir, fname)
            if os.path.isfile(fpath):
                age_days = (now - os.path.getmtime(fpath)) / 86400
                if age_days > max_age_days:
                    os.remove(fpath)

    def exists(self) -> bool:
        """数据文件是否存在"""
        return os.path.exists(self._data_file)

    @property
    def data_path(self) -> str:
        return self._data_file
