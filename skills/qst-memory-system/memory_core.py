"""
QST Memory Core - Matrix Operations

利用 E8 幾何結構實現高效記憶存取。

核心數學：
- 記憶態向量：|Ψ_M⟩ = Σ_n c_n |σ_n⟩ ⊗ |D_n⟩ ⊗ |E8_n⟩
- QST Matrix：M_QST = ⟨Ψ_M| E8 |Θ_M⟩
- DSI 尺度：D_n = D_0 - n·φ²
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
import hashlib
import json
from datetime import datetime

# ===== 常數定義 =====
PHI = (1 + np.sqrt(5)) / 2  # 黃金比例 ≈ 1.618
SIGMA_CRYSTAL = 1.0          # 晶體化閾值
DELTA_SIGMA = 0.15           # Coherence 展寬
ETA = 0.1                    # Ethical Tension 系數
D_MAX = 36                  # DSI 最大層次

# ===== E8 基底投影 (簡化版) =====
class E8Projector:
    """E8 基底投影器"""
    
    def __init__(self, dim: int = 16):
        """
        初始化 E8 投影器
        
        Args:
            dim: 投影維度 (預設 16)
        """
        self.dim = dim
        # 生成隨機 E8 基底投影
        np.random.seed(42)
        self.e8_basis = np.random.randn(dim, 248) / np.sqrt(248)
        
    def project(self, coherence: float, dsi_level: int) -> np.ndarray:
        """
        將 coherence 和 DSI 層次投影到 E8 基底
        
        Args:
            coherence: σ 值 (0-2)
            dsi_level: DSI 層次 (0-36)
            
        Returns:
            E8 投影向量
        """
        # 編碼 coherence
        sigma_enc = np.array([
            coherence,
            coherence ** 2,
            np.sin(np.pi * coherence),
            np.cos(np.pi * coherence)
        ])
        
        # 編碼 DSI 層次
        d_actual = dsi_level if dsi_level <= D_MAX else D_MAX
        d_enc = np.array([
            d_actual / D_MAX,
            (d_actual / D_MAX) ** 2,
            np.sin(2 * np.pi * d_actual / D_MAX),
            np.cos(2 * np.pi * d_actual / D_MAX)
        ])
        
        # 組合特徵
        features = np.concatenate([sigma_enc, d_enc])
        
        # 投影到 E8 基底
        projected = features @ self.e8_basis
        
        # L2 正規化
        norm = np.linalg.norm(projected)
        if norm > 0:
            projected = projected / norm
            
        return projected
    
    def similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """
        計算兩個 E8 向量的相似度
        
        Args:
            v1, v2: E8 投影向量
            
        Returns:
            相似度 (0-1)
        """
        # Cosine similarity
        dot = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return max(0.0, min(1.0, dot / (norm1 * norm2)))


# ===== 記憶態向量 =====
class MemorySpinor:
    """記憶態向量包裝器"""
    
    def __init__(self, 
                 content: str,
                 coherence: float = 0.8,
                 dsi_level: int = 0,
                 e8_projector: E8Projector = None):
        """
        初始化記憶態向量
        
        Args:
            content: 記憶內容
            coherence: σ 值
            dsi_level: DSI 層次
            e8_projector: E8 投影器
        """
        self.content = content
        self.coherence = coherence
        self.dsi_level = dsi_level
        self.id = self._generate_id()
        self.timestamp = datetime.now()
        self.ethical_tension = 0.0
        
        # E8 投影
        self.e8_projector = e8_projector or E8Projector()
        self.e8_vector = self.e8_projector.project(coherence, dsi_level)
        
    def _generate_id(self) -> str:
        """生成唯一 ID"""
        data = f"{self.content}_{self.coherence}_{self.dsi_level}_{datetime.now()}"
        return hashlib.md5(data.encode()).hexdigest()[:16]
    
    def update_coherence(self, new_coherence: float):
        """更新 coherence 並重新計算 E8 投影"""
        self.coherence = new_coherence
        self.e8_vector = self.e8_projector.project(new_coherence, self.dsi_level)
        self.timestamp = datetime.now()
        
    def to_dict(self) -> Dict:
        """轉換為字典"""
        return {
            "id": self.id,
            "content": self.content,
            "coherence": self.coherence,
            "dsi_level": self.dsi_level,
            "e8_vector": self.e8_vector.tolist(),
            "timestamp": self.timestamp.isoformat(),
            "ethical_tension": self.ethical_tension
        }
    
    @classmethod
    def from_dict(cls, data: Dict, e8_projector: E8Projector = None) -> 'MemorySpinor':
        """從字典恢復"""
        m = cls(
            content=data["content"],
            coherence=data["coherence"],
            dsi_level=data["dsi_level"],
            e8_projector=e8_projector
        )
        m.id = data["id"]
        m.timestamp = datetime.fromisoformat(data["timestamp"])
        m.e8_vector = np.array(data["e8_vector"])
        m.ethical_tension = data.get("ethical_tension", 0.0)
        return m


# ===== QST Matrix 核心 =====
class QSTMemoryCore:
    """QST 記憶核心引擎"""
    
    def __init__(self, e8_dim: int = 16):
        """
        初始化 QST 記憶核心
        
        Args:
            e8_dim: E8 投影維度
        """
        self.e8_projector = E8Projector(dim=e8_dim)
        self.memories: Dict[str, MemorySpinor] = {}
        
    def encode(self, content: str, 
               base_coherence: float = 0.8,
               dsi_level: int = 0) -> MemorySpinor:
        """
        編碼新記憶
        
        Args:
            content: 內容
            base_coherence: 基礎 coherence
            dsi_level: DSI 層次
            
        Returns:
            MemorySpinor 實例
        """
        memory = MemorySpinor(
            content=content,
            coherence=base_coherence,
            dsi_level=dsi_level,
            e8_projector=self.e8_projector
        )
        
        self.memories[memory.id] = memory
        return memory
    
    def retrieve(self, 
                 query: str,
                 top_k: int = 3,
                 coherence_weight: float = 0.5) -> List[Tuple[MemorySpinor, float]]:
        """
        檢索相關記憶 (ICT Collapse 簡化版)
        
        Args:
            query: 查詢文本
            top_k: 返回數量
            coherence_weight: Coherence 權重
            
        Returns:
            [(記憶, 分數)] 列表
        """
        # 簡化：將查詢編碼為虛擬 spinor
        # 實際應用中應使用 embedding model
        query_coherence = 0.9  # 查詢 coherence
        query_e8 = self.e8_projector.project(query_coherence, 0)
        
        scores = []
        for memory in self.memories.values():
            # E8 相似度
            e8_sim = self.e8_projector.similarity(query_e8, memory.e8_vector)
            
            # Coherence 權重
            coh_sim = 1.0 - abs(query_coherence - memory.coherence)
            
            # 綜合分數
            total_score = (1 - coherence_weight) * e8_sim + coherence_weight * coh_sim
            
            # Ethical Tension 修正
            score = total_score * np.exp(-ETA * memory.ethical_tension)
            
            scores.append((memory, score))
        
        # 排序並返回 top_k
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
    
    def consolidate(self, 
                    memory_id: str,
                    new_content: str = None) -> Optional[MemorySpinor]:
        """
        長期整合 (Coherence 增長)
        
        Args:
            memory_id: 記憶 ID
            new_content: 新內容 (可選)
            
        Returns:
            更新後的 MemorySpinor 或 None
        """
        if memory_id not in self.memories:
            return None
            
        memory = self.memories[memory_id]
        
        # 增加 coherence
        new_coherence = min(2.0, memory.coherence + 0.05)
        
        # 如果達到晶體化閾值，升級 DSI 層次
        if new_coherence >= SIGMA_CRYSTAL:
            new_dsi = min(D_MAX, memory.dsi_level + 1)
        else:
            new_dsi = memory.dsi_level
            
        # 更新記憶
        if new_content:
            memory.content = new_content
            
        memory.update_coherence(new_coherence)
        memory.dsi_level = new_dsi
        memory.timestamp = datetime.now()
        
        return memory
    
    def decay_check(self) -> List[str]:
        """
        檢查並衰減低 coherence 記憶
        
        Returns:
            應該刪除的記憶 ID 列表
        """
        to_delete = []
        
        for memory in self.memories.values():
            # 短記憶閾值
            if memory.dsi_level == 0 and memory.coherence < 0.5:
                to_delete.append(memory.id)
            # Medium 記憶
            elif 1 <= memory.dsi_level <= 5 and memory.coherence < 0.7:
                to_delete.append(memory.id)
                
        return to_delete
    
    def prune(self, memory_ids: List[str]):
        """刪除記憶"""
        for mid in memory_ids:
            if mid in self.memories:
                del self.memories[mid]
                
    def save_state(self, filepath: str):
        """保存狀態"""
        with open(filepath, 'w') as f:
            json.dump(
                {mid: m.to_dict() for mid, m in self.memories.items()},
                f,
                indent=2
            )
            
    def load_state(self, filepath: str):
        """載入狀態"""
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.memories = {
                mid: MemorySpinor.from_dict(mdata, self.e8_projector)
                for mid, mdata in data.items()
            }


# ===== 便捷函數 =====
def create_memory(content: str, 
                  coherence: float = 0.8,
                  dsi_level: int = 0) -> MemorySpinor:
    """創建單一記憶"""
    core = QSTMemoryCore()
    return core.encode(content, coherence, dsi_level)


def retrieve_memories(core: QSTMemoryCore, 
                      query: str, 
                      top_k: int = 3) -> List[Tuple[MemorySpinor, float]]:
    """檢索記憶"""
    return core.retrieve(query, top_k)


# ===== 測試 =====
if __name__ == "__main__":
    # 初始化
    core = QSTMemoryCore()
    
    # 創建測試記憶
    print("=== QST Memory Core Test ===\n")
    
    memories = [
        ("秦王是皇帝", 0.9, 2),
        ("李斯是丞相", 0.85, 1),
        ("蒙恬是將軍", 0.88, 1),
        ("QST是量子時空理論", 0.95, 3),
    ]
    
    for content, coh, dsi in memories:
        core.encode(content, coh, dsi)
        print(f"✓ Encoded: {content}")
    
    print(f"\nTotal memories: {len(core.memories)}")
    
    # 檢索測試
    print("\n=== Retrieval Test ===")
    results = core.retrieve("誰是大臣？", top_k=2)
    
    for memory, score in results:
        print(f"- [{score:.3f}] {memory.content}")
    
    print("\n=== Consolidation Test ===")
    # 整合測試
    test_id = list(core.memories.keys())[0]
    updated = core.consolidate(test_id)
    if updated:
        print(f"Updated {updated.id}: coherence={updated.coherence}, dsi={updated.dsi_level}")
    
    print("\n=== DSI Scale Test ===")
    for i in range(5):
        v = core.e8_projector.project(0.8, i)
        print(f"DSI Level {i}: vector norm = {np.linalg.norm(v):.4f}")
