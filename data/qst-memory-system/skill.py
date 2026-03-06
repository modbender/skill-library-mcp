"""
QST Memory Skill - OpenClaw Integration

OpenClaw Skill 包裝器。

用法：
1. 複製此目錄到 OpenClaw skills 目錄
2. 在 AGENTS.md 中添加 skill
"""

from typing import List, Dict, Optional, Any
import json
import os

# ===== 配置 =====
CONFIG = {
    "e8_dim": 16,
    "top_k": 5,
    "storage_type": "hybrid",
    "embedding_type": "simple",
    "auto_consolidate": True,
    "decay_interval": 100
}


def load_config(config_path: str = None) -> Dict:
    """載入配置"""
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return {**CONFIG, **json.load(f)}
    return CONFIG


# ===== 主要類 =====
class Skill:
    """QST Memory Skill"""
    
    def __init__(self, config: Dict = None):
        """
        初始化 Skill
        
        Args:
            config: 配置字典
        """
        self.config = config or load_config()
        
        # 延遲初始化（避免載入時錯誤）
        self._memory = None
        self._initialized = False
    
    def _ensure_init(self):
        """確保已初始化"""
        if not self._initialized:
            from qst_memory import QSTMemory
            self._memory = QSTMemory(
                e8_dim=self.config.get("e8_dim", 16),
                top_k=self.config.get("top_k", 5)
            )
            self._initialized = True
    
    # ===== 存儲操作 =====
    
    def store(self, 
              content: str,
              context: str = None,
              coherence: float = None) -> str:
        """
        存儲記憶
        
        Args:
            content: 記憶內容
            context: 上下文標籤
            coherence: Coherence 值
            
        Returns:
            記憶 ID
        """
        self._ensure_init()
        return self._memory.store(content, context, coherence)
    
    def store_conversation(self,
                          speaker: str,
                          content: str,
                          turn_type: str = "user") -> str:
        """
        存儲對話
        
        Args:
            speaker: 說話者
            content: 內容
            turn_type: "user" | "assistant" | "system"
            
        Returns:
            輪次 ID
        """
        self._ensure_init()
        return self._memory.store_conversation(speaker, content, turn_type)
    
    # ===== 檢索操作 =====
    
    def retrieve(self, 
                 query: str,
                 top_k: int = None,
                 keywords: List[str] = None) -> List[Dict]:
        """
        檢索記憶
        
        Args:
            query: 查詢
            top_k: 返回數量
            keywords: 關鍵詞
            
        Returns:
            結果列表
        """
        self._ensure_init()
        results = self._memory.retrieve(query, top_k, keywords)
        
        return [
            {
                "id": r.memory.id,
                "content": r.memory.content,
                "score": r.total_score,
                "coherence": r.memory.coherence,
                "dsi_level": r.memory.dsi_level
            }
            for r in results
        ]
    
    def retrieve_with_context(self,
                              query: str,
                              context: str) -> List[Dict]:
        """
        帶上下文檢索
        
        Args:
            query: 查詢
            context: 上下文
            
        Returns:
            結果列表
        """
        self._ensure_init()
        results = self._memory.retrieve_with_context(query, context)
        
        return [
            {
                "id": r.memory.id,
                "content": r.memory.content,
                "score": r.total_score
            }
            for r in results
        ]
    
    # ===== 上下文操作 =====
    
    def get_context(self, max_turns: int = 10) -> str:
        """
        獲取對話上下文
        
        Args:
            max_turns: 最大輪次
            
        Returns:
            格式化上下文字符串
        """
        self._ensure_init()
        return self._memory.get_context(max_turns)
    
    def get_coherence_info(self) -> Dict:
        """
        獲取 Coherence 狀態
        
        Returns:
            Coherence 信息
        """
        self._ensure_init()
        return self._memory.get_coherence_info()
    
    # ===== 管理操作 =====
    
    def consolidate(self, memory_id: str = None) -> int:
        """
        整合記憶
        
        Args:
            memory_id: 目標 ID (None 為全部)
            
        Returns:
            整合數量
        """
        self._ensure_init()
        return self._memory.consolidate(memory_id)
    
    def decay(self) -> int:
        """
        衰減記憶
        
        Returns:
            刪除數量
        """
        self._ensure_init()
        return self._memory.decay_all()
    
    def clear(self):
        """清空所有記憶"""
        self._ensure_init()
        self._memory.clear()
    
    # ===== 持久化 =====
    
    def save_state(self, filepath: str = "qst_memory_state.json"):
        """
        保存狀態
        
        Args:
            filepath: 文件路徑
        """
        self._ensure_init()
        self._memory.save_state(filepath)
    
    def load_state(self, filepath: str = "qst_memory_state.json"):
        """
        載入狀態
        
        Args:
            filepath: 文件路徑
        """
        self._ensure_init()
        self._memory.load_state(filepath)
    
    # ===== 統計 =====
    
    def get_stats(self) -> Dict:
        """
        獲取統計
        
        Returns:
            統計字典
        """
        self._ensure_init()
        return self._memory.get_stats()


# ===== 便捷函數 =====
def create_skill(config: Dict = None) -> Skill:
    """創建 Skill 實例"""
    return Skill(config)


# ===== OpenClaw 工具函數 =====
def register_tools() -> Dict:
    """
    註冊工具描述（供 OpenClaw 使用）
    
    Returns:
        工具 Schema
    """
    return {
        "name": "qst_memory",
        "description": "QST Matrix-based Memory System - Fast retrieval using E8 geometry and ICT Collapse",
        "functions": {
            "store": {
                "description": "Store a memory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Memory content"},
                        "context": {"type": "string", "description": "Context label"},
                        "coherence": {"type": "number", "description": "Coherence value (0-2)"}
                    },
                    "required": ["content"]
                }
            },
            "retrieve": {
                "description": "Retrieve relevant memories",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "top_k": {"type": "integer", "description": "Number of results"}
                    },
                    "required": ["query"]
                }
            },
            "get_context": {
                "description": "Get conversation context",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "max_turns": {"type": "integer", "description": "Max turns"}
                    }
                }
            },
            "get_coherence_info": {
                "description": "Get memory coherence status"
            }
        }
    }


# ===== 測試 =====
if __name__ == "__main__":
    print("=== QST Memory Skill Test ===\n")
    
    # 初始化
    skill = Skill()
    
    # 存儲對話
    print("Storing conversations...")
    skill.store_conversation("user", "你好！", "user")
    skill.store_conversation("assistant", "秦王陛下萬歲！", "assistant")
    skill.store_conversation("user", "我是皇帝", "user")
    skill.store_conversation("assistant", "臣李斯參見！", "assistant")
    
    # 獲取上下文
    print("\nContext:")
    print(skill.get_context(5))
    
    # 檢索
    print("\nRetrieval: '皇帝'")
    results = skill.retrieve("皇帝", top_k=3)
    for r in results:
        print(f"  - [{r['score']:.3f}] {r['content']}")
    
    # 統計
    print("\nStats:")
    print(skill.get_stats())
    
    print("\n=== Complete ===")
