#!/usr/bin/env python3
"""
Hebbian Co-occurrence Tracker
记录记忆之间的共现关联
"""

import sqlite3
import json
import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple

class CoOccurrenceTracker:
    """Hebbian 共现图追踪器"""
    
    def __init__(self, db_path: str = "~/.config/cortexgraph/co_occurrence.db"):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS co_occurrence (
                memory_a TEXT,
                memory_b TEXT,
                weight REAL,
                last_updated TEXT,
                created_at TEXT,
                PRIMARY KEY (memory_a, memory_b)
            )
        ''')
        
        c.execute('CREATE INDEX IF NOT EXISTS idx_memory_a ON co_occurrence(memory_a)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_memory_b ON co_occurrence(memory_b)')
        
        conn.commit()
        conn.close()
    
    def record_co_occurrence(self, memory_ids: List[str], context: str = ""):
        """
        记录记忆共现
        
        Args:
            memory_ids: 同时被检索的记忆 ID 列表
            context: 上下文描述（可选）
        """
        if len(memory_ids) < 2:
            return
        
        now = datetime.now().isoformat()
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 记录所有两两组合
        for i, mem_a in enumerate(memory_ids):
            for mem_b in memory_ids[i+1:]:
                # 确保 mem_a < mem_b 以避免重复
                if mem_a > mem_b:
                    mem_a, mem_b = mem_b, mem_a
                
                # 检查是否已存在
                c.execute('''
                    SELECT weight FROM co_occurrence 
                    WHERE memory_a = ? AND memory_b = ?
                ''', (mem_a, mem_b))
                
                row = c.fetchone()
                if row:
                    # 更新权重
                    new_weight = row[0] + 1.0
                    c.execute('''
                        UPDATE co_occurrence 
                        SET weight = ?, last_updated = ?
                        WHERE memory_a = ? AND memory_b = ?
                    ''', (new_weight, now, mem_a, mem_b))
                else:
                    # 创建新边
                    c.execute('''
                        INSERT INTO co_occurrence 
                        (memory_a, memory_b, weight, last_updated, created_at)
                        VALUES (?, ?, 1.0, ?, ?)
                    ''', (mem_a, mem_b, now, now))
        
        conn.commit()
        conn.close()
    
    def get_co_occurrence_score(self, memory_id: str, related_ids: List[str] = None) -> float:
        """
        获取记忆的共现得分
        
        Args:
            memory_id: 目标记忆 ID
            related_ids: 相关记忆 ID 列表（如果提供，只计算与这些记忆的共现）
        
        Returns:
            共现得分（0.0 - 1.0）
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 获取所有相关边
        c.execute('''
            SELECT memory_a, memory_b, weight, last_updated
            FROM co_occurrence
            WHERE memory_a = ? OR memory_b = ?
        ''', (memory_id, memory_id))
        
        rows = c.fetchall()
        conn.close()
        
        if not rows:
            return 0.0
        
        # 计算有效权重（考虑衰减）
        total_weight = 0.0
        half_life_days = 30.0
        
        for mem_a, mem_b, weight, last_updated in rows:
            # 计算衰减
            updated = datetime.fromisoformat(last_updated)
            age_days = (datetime.now() - updated).days
            decay = math.pow(2, -age_days / half_life_days)
            effective_weight = weight * decay
            
            # 如果指定了相关记忆，只计算与它们的共现
            if related_ids:
                other_id = mem_b if mem_a == memory_id else mem_a
                if other_id in related_ids:
                    total_weight += effective_weight
            else:
                total_weight += effective_weight
        
        # 归一化到 0-1
        return min(1.0, total_weight / 10.0)
    
    def get_related_memories(self, memory_id: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        获取与指定记忆最相关的其他记忆
        
        Args:
            memory_id: 目标记忆 ID
            top_k: 返回数量
        
        Returns:
            [(memory_id, effective_weight), ...]
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT memory_a, memory_b, weight, last_updated
            FROM co_occurrence
            WHERE memory_a = ? OR memory_b = ?
            ORDER BY weight DESC
            LIMIT ?
        ''', (memory_id, memory_id, top_k * 2))
        
        rows = c.fetchall()
        conn.close()
        
        results = []
        half_life_days = 30.0
        
        for mem_a, mem_b, weight, last_updated in rows:
            other_id = mem_b if mem_a == memory_id else mem_a
            
            # 计算衰减
            updated = datetime.fromisoformat(last_updated)
            age_days = (datetime.now() - updated).days
            decay = math.pow(2, -age_days / half_life_days)
            effective_weight = weight * decay
            
            results.append((other_id, effective_weight))
        
        # 按有效权重排序
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 总边数
        c.execute('SELECT COUNT(*) FROM co_occurrence')
        total_edges = c.fetchone()[0]
        
        # 唯一记忆数
        c.execute('SELECT COUNT(DISTINCT memory_a) FROM co_occurrence')
        unique_memories = c.fetchone()[0]
        
        # 平均权重
        c.execute('SELECT AVG(weight) FROM co_occurrence')
        avg_weight = c.fetchone()[0] or 0
        
        # 最大权重
        c.execute('SELECT MAX(weight) FROM co_occurrence')
        max_weight = c.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_edges': total_edges,
            'unique_memories': unique_memories,
            'avg_weight': round(avg_weight, 2),
            'max_weight': max_weight,
            'avg_edges_per_memory': round(total_edges / unique_memories * 2, 2) if unique_memories > 0 else 0
        }
    
    def decay_old_edges(self, days: int = 90):
        """
        删除过旧的边（可选维护）
        
        Args:
            days: 超过多少天未更新的边删除
        """
        threshold = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('DELETE FROM co_occurrence WHERE last_updated < ?', (threshold,))
        deleted = c.rowcount
        
        conn.commit()
        conn.close()
        
        return deleted


if __name__ == "__main__":
    tracker = CoOccurrenceTracker()
    
    # 测试
    test_memories = [
        "mem_001",
        "mem_002", 
        "mem_003"
    ]
    
    print("记录共现...")
    tracker.record_co_occurrence(test_memories)
    
    print("\n统计:")
    stats = tracker.get_stats()
    for k, v in stats.items():
        print(f"  {k}: {v}")
    
    print("\n与 mem_001 相关的记忆:")
    related = tracker.get_related_memories("mem_001")
    for mem_id, weight in related:
        print(f"  {mem_id}: {weight:.2f}")
