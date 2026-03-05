"""
QST Long-term Memory - Persistence Layer

長期記憶持久化實現。

支持：
- JSON 文件存儲
- SQLite 數據庫
- 混合模式（JSON + SQLite）
"""

import json
import sqlite3
import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path
import threading
import hashlib

from memory_core import QSTMemoryCore, MemorySpinor, E8Projector


# ===== JSON 存儲 =====
class JSONStorage:
    """JSON 文件存儲"""
    
    def __init__(self, filepath: str = "qst_memory.json"):
        """
        初始化
        
        Args:
            filepath: 文件路徑
        """
        self.filepath = Path(filepath)
        self._lock = threading.Lock()
        
    def save(self, memories: Dict[str, MemorySpinor]):
        """
        保存所有記憶
        
        Args:
            memories: 記憶字典
        """
        with self._lock:
            data = {
                "version": "1.0",
                "saved_at": datetime.now().isoformat(),
                "memories": {
                    mid: memory.to_dict()
                    for mid, memory in memories.items()
                }
            }
            
            # 原子寫入
            temp_path = self.filepath.with_suffix(".tmp")
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            temp_path.replace(self.filepath)
            
    def load(self, e8_projector: E8Projector = None) -> Dict[str, MemorySpinor]:
        """
        載入所有記憶
        
        Args:
            e8_projector: E8 投影器
            
        Returns:
            記憶字典
        """
        if not self.filepath.exists():
            return {}
            
        with self._lock:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
        memories = {}
        for mid, mdata in data.get("memories", {}).items():
            memory = MemorySpinor.from_dict(mdata, e8_projector)
            memories[mid] = memory
            
        return memories
    
    def append(self, memory: MemorySpinor):
        """
        追加單一記憶
        
        Args:
            memory: 記憶
        """
        # 先載入
        memories = self.load()
        
        # 添加
        memories[memory.id] = memory
        
        # 保存
        self.save(memories)
    
    def delete(self, memory_id: str):
        """
        刪除記憶
        
        Args:
            memory_id: 記憶 ID
        """
        memories = self.load()
        
        if memory_id in memories:
            del memories[memory_id]
            self.save(memories)
    
    def clear(self):
        """清空所有記憶"""
        if self.filepath.exists():
            self.filepath.unlink()


# ===== SQLite 存儲 =====
class SQLiteStorage:
    """SQLite 數據庫存儲"""
    
    def __init__(self, filepath: str = "qst_memory.db"):
        """
        初始化
        
        Args:
            filepath: 數據庫路徑
        """
        self.filepath = Path(filepath)
        self._lock = threading.Lock()
        self._init_db()
        
    def _init_db(self):
        """初始化數據庫"""
        with self._lock:
            conn = sqlite3.connect(self.filepath)
            cursor = conn.cursor()
            
            # 創建表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    coherence REAL NOT NULL,
                    dsi_level INTEGER NOT NULL,
                    e8_vector TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    ethical_tension REAL DEFAULT 0.0,
                    metadata TEXT DEFAULT '{}'
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            
            conn.commit()
            conn.close()
    
    def save(self, memories: Dict[str, MemorySpinor]):
        """
        保存所有記憶
        
        Args:
            memories: 記憶字典
        """
        with self._lock:
            conn = sqlite3.connect(self.filepath)
            cursor = conn.cursor()
            
            # 更新元數據
            cursor.execute(
                "INSERT OR REPLACE INTO metadata VALUES (?, ?)",
                ("last_saved", datetime.now().isoformat())
            )
            
            # 保存每個記憶
            for memory in memories.values():
                cursor.execute("""
                    INSERT OR REPLACE INTO memories 
                    (id, content, coherence, dsi_level, e8_vector, timestamp, ethical_tension, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    memory.id,
                    memory.content,
                    memory.coherence,
                    memory.dsi_level,
                    json.dumps(memory.e8_vector.tolist()),
                    memory.timestamp.isoformat(),
                    memory.ethical_tension,
                    "{}"
                ))
            
            conn.commit()
            conn.close()
    
    def load(self, e8_projector: E8Projector = None) -> Dict[str, MemorySpinor]:
        """
        載入所有記憶
        
        Args:
            e8_projector: E8 投影器
            
        Returns:
            記憶字典
        """
        memories = {}
        
        with self._lock:
            conn = sqlite3.connect(self.filepath)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM memories")
            rows = cursor.fetchall()
            
            conn.close()
            
        for row in rows:
            mdata = {
                "id": row[0],
                "content": row[1],
                "coherence": row[2],
                "dsi_level": row[3],
                "e8_vector": json.loads(row[4]),
                "timestamp": row[5],
                "ethical_tension": row[6]
            }
            
            memory = MemorySpinor.from_dict(mdata, e8_projector)
            memories[memory.id] = memory
            
        return memories
    
    def append(self, memory: MemorySpinor):
        """
        追加單一記憶
        
        Args:
            memory: 記憶
        """
        with self._lock:
            conn = sqlite3.connect(self.filepath)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO memories 
                (id, content, coherence, dsi_level, e8_vector, timestamp, ethical_tension, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                memory.id,
                memory.content,
                memory.coherence,
                memory.dsi_level,
                json.dumps(memory.e8_vector.tolist()),
                memory.timestamp.isoformat(),
                memory.ethical_tension,
                "{}"
            ))
            
            conn.commit()
            conn.close()
    
    def delete(self, memory_id: str):
        """刪除記憶"""
        with self._lock:
            conn = sqlite3.connect(self.filepath)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            
            conn.commit()
            conn.close()
    
    def search_by_content(self, keyword: str) -> List[str]:
        """
        按內容關鍵詞搜索
        
        Args:
            keyword: 關鍵詞
            
        Returns:
            記憶 ID 列表
        """
        with self._lock:
            conn = sqlite3.connect(self.filepath)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id FROM memories WHERE content LIKE ?",
                (f"%{keyword}%",)
            )
            
            results = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
        return results
    
    def get_stats(self) -> dict:
        """獲取統計"""
        with self._lock:
            conn = sqlite3.connect(self.filepath)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM memories")
            count = cursor.fetchone()[0]
            
            cursor.execute("SELECT MAX(timestamp) FROM memories")
            last_saved = cursor.fetchone()[0]
            
            conn.close()
            
        return {
            "memory_count": count,
            "last_saved": last_saved
        }
    
    def clear(self):
        """清空所有記憶"""
        with self._lock:
            conn = sqlite3.connect(self.filepath)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM memories")
            cursor.execute("DELETE FROM metadata")
            
            conn.commit()
            conn.close()


# ===== 混合存儲 =====
class HybridStorage:
    """
    混合存儲（JSON + SQLite）
    
    策略：
    - SQLite: 主要存儲，快速查詢
    - JSON: 備份/導出
    """
    
    def __init__(self, 
                 sqlite_path: str = "qst_memory.db",
                 json_path: str = "qst_memory_backup.json"):
        """
        初始化
        
        Args:
            sqlite_path: SQLite 路徑
            json_path: JSON 備份路徑
        """
        self.sqlite = SQLiteStorage(sqlite_path)
        self.json = JSONStorage(json_path)
        
    def save(self, memories: Dict[str, MemorySpinor]):
        """
        保存所有記憶
        
        Args:
            memories: 記憶字典
        """
        self.sqlite.save(memories)
        self.json.save(memories)
    
    def load(self, e8_projector: E8Projector = None) -> Dict[str, MemorySpinor]:
        """
        載入所有記憶
        
        Args:
            e8_projector: E8 投影器
            
        Returns:
            記憶字典
        """
        # 優先從 SQLite 載入
        memories = self.sqlite.load(e8_projector)
        
        if not memories:
            # 嘗試 JSON
            memories = self.json.load(e8_projector)
            
        return memories
    
    def append(self, memory: MemorySpinor):
        """追加單一記憶"""
        self.sqlite.append(memory)
        self.json.append(memory)
    
    def delete(self, memory_id: str):
        """刪除記憶"""
        self.sqlite.delete(memory_id)
        self.json.delete(memory_id)
    
    def backup(self):
        """創建 JSON 備份"""
        memories = self.sqlite.load()
        self.json.save(memories)
        
    def restore(self, e8_projector: E8Projector = None) -> Dict[str, MemorySpinor]:
        """從 JSON 恢復"""
        memories = self.json.load(e8_projector)
        self.sqlite.save(memories)
        return memories
    
    def get_stats(self) -> dict:
        """獲取統計"""
        return self.sqlite.get_stats()
    
    def clear(self):
        """清空所有"""
        self.sqlite.clear()
        self.json.clear()


# ===== 長期記憶管理器 =====
class LongTermMemory:
    """
    長期記憶管理器
    
    管理：
    - 記憶持久化
    - 自動備份
    - 版本控制
    """
    
    def __init__(self,
                 storage: HybridStorage = None,
                 auto_backup_interval: int = 100,
                 max_versions: int = 5):
        """
        初始化
        
        Args:
            storage: 存儲引擎
            auto_backup_interval: 自動備份間隔（操作次數）
            max_versions: 最大版本數
        """
        self.storage = storage or HybridStorage()
        self.auto_backup_interval = auto_backup_interval
        self.max_versions = max_versions
        
        # 狀態
        self.operation_count = 0
        self.last_backup = datetime.now()
        
        # 版本控制
        self.versions: List[datetime] = []
        
    def save(self, memories: Dict[str, MemorySpinor]):
        """
        保存記憶
        
        Args:
            memories: 記憶字典
        """
        self.storage.save(memories)
        self.operation_count += 1
        
        # 自動備份
        if self.operation_count >= self.auto_backup_interval:
            self.backup()
    
    def load(self, e8_projector: E8Projector = None) -> Dict[str, MemorySpinor]:
        """
        載入記憶
        
        Args:
            e8_projector: E8 投影器
            
        Returns:
            記憶字典
        """
        return self.storage.load(e8_projector)
    
    def backup(self):
        """創建版本備份"""
        now = datetime.now()
        
        # 檢查版本數量
        if len(self.versions) >= self.max_versions:
            oldest = self.versions.pop(0)
            old_path = self.storage.json.filepath.with_suffix(f".{oldest.strftime('%Y%m%d_%H%M%S')}.json")
            if old_path.exists():
                old_path.unlink()
        
        # 保存當前狀態
        self.storage.backup()
        self.versions.append(now)
        self.last_backup = now
        self.operation_count = 0
        
    def restore_from_version(self, 
                            timestamp: datetime,
                            e8_projector: E8Projector = None) -> Dict[str, MemorySpinor]:
        """
        從版本恢復
        
        Args:
            timestamp: 版本時間戳
            e8_projector: E8 投影器
            
        Returns:
            記憶字典
        """
        # 構造備份路徑
        backup_path = self.storage.json.filepath.with_suffix(
            f".{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Version not found: {backup_path}")
        
        # 載入
        memories = self.storage.restore(e8_projector)
        return memories
    
    def export_to_json(self, filepath: str):
        """
        導出為 JSON
        
        Args:
            filepath: 目標路徑
        """
        memories = self.storage.load()
        
        data = {
            "exported_at": datetime.now().isoformat(),
            "version": "1.0",
            "memories": {
                mid: memory.to_dict()
                for mid, memory in memories.items()
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_stats(self) -> dict:
        """獲取統計"""
        stats = self.storage.get_stats()
        stats.update({
            "operation_count": self.operation_count,
            "last_backup": self.last_backup.isoformat(),
            "version_count": len(self.versions)
        })
        return stats


# ===== 便捷函數 =====
def create_long_term_memory(
    storage_type: str = "hybrid",
    **kwargs
) -> LongTermMemory:
    """
    創建長期記憶實例
    
    Args:
        storage_type: "json" | "sqlite" | "hybrid"
        **kwargs: 其他參數
        
    Returns:
        LongTermMemory 實例
    """
    if storage_type == "json":
        storage = JSONStorage(kwargs.get("filepath", "qst_memory.json"))
    elif storage_type == "sqlite":
        storage = SQLiteStorage(kwargs.get("filepath", "qst_memory.db"))
    else:
        storage = HybridStorage(
            kwargs.get("sqlite_path", "qst_memory.db"),
            kwargs.get("json_path", "qst_memory_backup.json")
        )
    
    return LongTermMemory(
        storage=storage,
        auto_backup_interval=kwargs.get("auto_backup_interval", 100),
        max_versions=kwargs.get("max_versions", 5)
    )


# ===== 測試 =====
if __name__ == "__main__":
    print("=== Long-term Memory Test ===\n")
    
    from memory_core import QSTMemoryCore
    
    # 初始化
    core = QSTMemoryCore()
    long_term = create_long_term_memory("hybrid")
    
    # 創建測試記憶
    print("Creating test memories...")
    memories = []
    for i in range(5):
        m = core.encode(f"Test memory {i}", 0.8 + i * 0.05, i)
        memories.append(m)
    
    print(f"Created {len(memories)} memories")
    
    # 保存
    print("\nSaving...")
    long_term.save(core.memories)
    print("Saved!")
    
    # 獲取統計
    print("\nStats:")
    print(long_term.get_stats())
    
    # 清除內存
    core.memories.clear()
    
    # 載入
    print("\nLoading...")
    core.memories = long_term.load(core.e8_projector)
    print(f"Loaded {len(core.memories)} memories")
    
    # 測試 SQLite 查詢
    print("\nSQLite search test...")
    ids = long_term.storage.sqlite.search_by_content("Test")
    print(f"Found: {ids}")
    
    # 導出
    print("\nExporting...")
    long_term.export_to_json("exported_memories.json")
    print("Exported to exported_memories.json")
    
    print("\n=== Complete ===")
