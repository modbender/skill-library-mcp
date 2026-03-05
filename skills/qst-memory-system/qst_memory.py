"""
QST Memory System - Main Integration

整合所有模組，提供統一介面。

使用示例：
```python
from qst_memory import QSTMemory

# 初始化
memory = QSTMemory()

# 存儲對話
memory.store("用戶說的話")

# 檢索
results = memory.retrieve("查詢關鍵詞")

# 獲取對話上下文
context = memory.get_context()
```

作者：李斯 (丞相)
基於：QSTv7.1 框架
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime

from memory_core import QSTMemoryCore, MemorySpinor
from short_term import ShortTermMemory, ConversationBuffer
from retrieval import FastRetriever, RetrievalConfig, RetrievalResult


# ===== QST Memory 主類 =====
class QSTMemory:
    """
    QST 記憶系統主類
    
    整合：
    - Short-term Memory (對話緩冲)
    - Long-term Memory (知識庫)
    - Fast Retrieval (ICT Collapse)
    """
    
    def __init__(self, 
                 e8_dim: int = 16,
                 top_k: int = 5):
        """
        初始化 QST 記憶系統
        
        Args:
            e8_dim: E8 投影維度
            top_k: 檢索返回數量
        """
        # 初始化核心
        self.core = QSTMemoryCore(e8_dim=e8_dim)
        
        # 初始化短記憶
        self.short_term = ShortTermMemory(e8_dim=e8_dim)
        
        # 初始化檢索器
        config = RetrievalConfig(top_k=top_k)
        self.retriever = FastRetriever(self.core, config)
        
        # 配置
        self.e8_dim = e8_dim
        self.top_k = top_k
        
        # 統計
        self.stats = {
            "total_stores": 0,
            "total_retrievals": 0,
            "avg_response_time": 0.0
        }
    
    # ===== 存儲操作 =====
    
    def store(self, 
              content: str,
              context: str = None,
              coherence: float = None,
              memory_type: str = "short") -> str:
        """
        存儲新記憶
        
        Args:
            content: 記憶內容
            context: 上下文標籤
            coherence: Coherence 值 (None 為自動)
            memory_type: "short" | "long"
            
        Returns:
            記憶 ID
        """
        # 自動 coherence
        if coherence is None:
            coherence = self._estimate_coherence(content)
        
        # 存儲
        if memory_type == "short":
            # 添加到短記憶緩冲
            self.short_term.add_conversation(
                speaker="system",
                content=content,
                turn_type="user" if context == "user" else "assistant"
            )
            
            # 獲取 ID
            turn_id = list(self.short_term.buffer.turns)[-1].turn_id
            self.stats["total_stores"] += 1
            
            return turn_id
        else:
            # 直接存儲到長期記憶
            memory = self.core.encode(
                content=content,
                base_coherence=coherence,
                dsi_level=2  # Medium level
            )
            self.stats["total_stores"] += 1
            return memory.id
    
    def store_conversation(self,
                           speaker: str,
                           content: str,
                           turn_type: str = "user") -> str:
        """
        存儲對話輪次
        
        Args:
            speaker: 說話者
            content: 內容
            turn_type: "user" | "assistant" | "system"
            
        Returns:
            輪次 ID
        """
        turn = self.short_term.add_conversation(speaker, content, turn_type)
        self.stats["total_stores"] += 1
        return turn.turn_id
    
    # ===== 檢索操作 =====
    
    def retrieve(self, 
                 query: str,
                 top_k: int = None,
                 keywords: List[str] = None) -> List[RetrievalResult]:
        """
        檢索相關記憶
        
        Args:
            query: 查詢文本
            top_k: 返回數量
            keywords: 關鍵詞
            
        Returns:
            RetrievalResult 列表
        """
        import time
        start = time.time()
        
        # 檢索
        results = self.retriever.retrieve(query, keywords)
        
        # 更新統計
        elapsed = time.time() - start
        self.stats["total_retrievals"] += 1
        n = self.stats["total_retrievals"]
        self.stats["avg_response_time"] = (
            (self.stats["avg_response_time"] * (n - 1) + elapsed) / n
        )
        
        return results[:top_k or self.top_k]
    
    def retrieve_with_context(self,
                              query: str,
                              context: str,
                              context_weight: float = 0.3) -> List[RetrievalResult]:
        """
        帶上下文檢索
        
        混合查詢和上下文
        """
        return self.retriever.retrieve_with_context(
            query, context, context_weight
        )
    
    # ===== 上下文操作 =====
    
    def get_context(self, 
                    max_turns: int = 10) -> str:
        """
        獲取當前對話上下文
        
        Returns:
            格式化上下文字符串
        """
        return self.short_term.get_context(max_turns)
    
    def get_coherence_info(self) -> dict:
        """
        獲取 coherence 統計
        
        Returns:
            Coherence 配置信息
        """
        return self.short_term.get_coherence_info()
    
    # ===== 管理操作 =====
    
    def consolidate(self, 
                    memory_id: str = None,
                    new_content: str = None) -> int:
        """
        整合記憶到長期
        
        Args:
            memory_id: 目標記憶 ID (None 為全部)
            new_content: 新內容
            
        Returns:
            整合數量
        """
        if memory_id:
            # 單一記憶
            updated = self.core.consolidate(memory_id, new_content)
            return 1 if updated else 0
        else:
            # 全部短記憶
            count = self.short_term.consolidate_to_short()
            return count
    
    def decay_all(self) -> int:
        """
        全局衰減
        
        Returns:
            刪除數量
        """
        return self.short_term.decay_all()
    
    def clear(self):
        """清空所有記憶"""
        self.short_term.buffer.clear()
        self.core.memories.clear()
        self.retriever.cache.clear()
    
    # ===== 輔助方法 =====
    
    def _estimate_coherence(self, content: str) -> float:
        """
        估計 coherence
        
        原則：
        - 短內容: σ ↓
        - 含關鍵詞: σ ↑
        - 系統消息: σ ↑↑
        """
        base = 0.7
        
        # 長度因素
        length_factor = min(1.0, len(content) / 500)
        
        # 關鍵詞因素
        keywords = ["記住", "重要", "千萬", "必須", "記得"]
        keyword_bonus = sum(1 for k in keywords if k in content) * 0.05
        
        return min(1.5, base + 0.2 * length_factor + keyword_bonus)
    
    # ===== 持久化 =====
    
    def save_state(self, filepath: str = "qst_memory_state.json"):
        """
        保存狀態
        
        Args:
            filepath: 文件路徑
        """
        # 保存核心
        self.core.save_state(filepath + ".core")
        
        # 保存短記憶
        self.short_term.buffer.save(filepath + ".buffer")
        
        print(f"State saved to {filepath}.core and {filepath}.buffer")
    
    def load_state(self, filepath: str = "qst_memory_state.json"):
        """
        載入狀態
        
        Args:
            filepath: 文件路徑
        """
        # 載入核心
        self.core.load_state(filepath + ".core")
        
        # 載入短記憶
        self.short_term.buffer.load(filepath + ".buffer")
        
        print(f"State loaded from {filepath}.core and {filepath}.buffer")
    
    # ===== 統計 =====
    
    def get_stats(self) -> dict:
        """
        獲取統計
        
        Returns:
            統計字典
        """
        return {
            **self.stats,
            "short_term_turns": len(self.short_term.buffer.turns),
            "long_term_memories": len(self.core.memories),
            "cache_size": len(self.retriever.cache.cache),
            "e8_dim": self.e8_dim
        }


# ===== 便捷工廠函數 =====
def create_memory(e8_dim: int = 16, top_k: int = 5) -> QSTMemory:
    """創建 QST 記憶實例"""
    return QSTMemory(e8_dim=e8_dim, top_k=top_k)


# ===== OpenClaw Skill 適配 =====
class QSTMemorySkill:
    """
    OpenClaw Skill 適配器
    
    用於直接整合到 OpenClaw
    """
    
    def __init__(self, e8_dim: int = 16):
        self.memory = create_memory(e8_dim)
        
    def store(self, content: str, context: str = None) -> str:
        return self.memory.store(content, context)
        
    def retrieve(self, query: str, top_k: int = 3) -> List[dict]:
        results = self.memory.retrieve(query, top_k=top_k)
        return [
            {
                "content": r.memory.content,
                "score": r.total_score,
                "coherence": r.memory.coherence,
                "id": r.memory.id
            }
            for r in results
        ]
        
    def get_context(self) -> str:
        return self.memory.get_context()


# ===== 測試 =====
if __name__ == "__main__":
    print("=== QST Memory System Test ===\n")
    
    # 創建記憶
    memory = create_memory(e8_dim=16)
    
    # 存儲對話
    print("Storing conversations...")
    memory.store_conversation("user", "你好！", "user")
    memory.store_conversation("assistant", "秦王陛下萬歲！", "assistant")
    memory.store_conversation("user", "我是皇帝", "user")
    memory.store_conversation("assistant", "臣李斯參見！", "assistant")
    memory.store_conversation("user", "QST是什麼？", "user")
    
    print(f"Total stores: {memory.stats['total_stores']}")
    
    # 獲取上下文
    print("\n=== Context ===")
    print(memory.get_context())
    
    # 檢索
    print("\n=== Retrieval: '皇帝' ===")
    results = memory.retrieve("皇帝")
    for i, r in enumerate(results):
        print(f"{i+1}. [{r.total_score:.3f}] {r.memory.content}")
    
    print("\n=== Retrieval: 'QST' ===")
    results = memory.retrieve("QST")
    for i, r in enumerate(results):
        print(f"{i+1}. [{r.total_score:.3f}] {r.memory.content}")
    
    # 統計
    print("\n=== Stats ===")
    print(memory.get_stats())
    
    # 整合
    print("\n=== Consolidation ===")
    count = memory.consolidate()
    print(f"Consolidated: {count} memories")
    
    print("\n=== Complete ===")
