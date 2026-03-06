"""
QST Memory Retrieval - ICT Collapse & Fast Retrieval

實現 ICT (Induced Collapse Theory) 快速檢索。

核心原理：
- Overlap 計算：⟨Q|Ψ_M⟩
- Collapse 概率：P(M) ∝ |Overlap|²
- Ethical Tension 修正：P(M) ∝ P(M) · exp(-η · V_eth)
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import hashlib

from memory_core import (
    QSTMemoryCore,
    MemorySpinor,
    E8Projector,
    ETA
)


# ===== 檢索配置 =====
@dataclass
class RetrievalConfig:
    """檢索配置"""
    top_k: int = 5
    coherence_weight: float = 0.5
    ethical_weight: float = 0.3
    recency_weight: float = 0.2
    min_score: float = 0.1
    use_collapse: bool = True
    collapse_temperature: float = 1.0


# ===== 查詢編碼器 =====
class QueryEncoder:
    """查詢編碼器"""
    
    def __init__(self, e8_projector: E8Projector = None):
        """
        初始化查詢編碼器
        
        Args:
            e8_projector: E8 投影器
        """
        self.e8_projector = e8_projector or E8Projector()
        
    def encode(self, query: str) -> np.ndarray:
        """
        編碼查詢文本
        
        簡化實現：
        - 基於關鍵詞特徵
        - 未來可替換為 embedding model
        
        Args:
            query: 查詢文本
            
        Returns:
            E8 投影向量
        """
        # 簡化：基於查詢長度和結構估計 coherence
        length_factor = min(1.0, len(query) / 100)
        
        # 問句通常更聚焦
        if '?' in query or '什麼' in query or '誰' in query or '如何' in query:
            query_coherence = 0.95
        elif len(query) < 20:
            query_coherence = 0.75
        else:
            query_coherence = 0.85
            
        return self.e8_projector.project(query_coherence, 0)
    
    def encode_with_keywords(self, 
                             query: str, 
                             keywords: List[str]) -> np.ndarray:
        """
        編碼查詢（帶關鍵詞權重）
        
        Args:
            query: 查詢文本
            keywords: 關鍵詞列表及其權重
            
        Returns:
            E8 投影向量
        """
        # 混合 coherence
        base = self.encode(query)
        
        # 關鍵詞權重調整
        if keywords:
            keyword_boost = len(keywords) * 0.05
            boosted = base * (1 + keyword_boost)
            return boosted / np.linalg.norm(boosted)
            
        return base


# ===== 檢索結果 =====
@dataclass
class RetrievalResult:
    """檢索結果"""
    memory: MemorySpinor
    overlap_score: float
    ethical_score: float
    recency_score: float
    total_score: float
    collapse_probability: float


# ===== ICT Collapse 檢索器 =====
class ICTRetriever:
    """
    ICT Collapse 檢索器
    
    實現：
    - Overlap 計算
    - Collapse 概率
    - Ethical Tension 修正
    """
    
    def __init__(self, 
                 core: QSTMemoryCore,
                 config: RetrievalConfig = None):
        """
        初始化 ICT 檢索器
        
        Args:
            core: QST 記憶核心
            config: 檢索配置
        """
        self.core = core
        self.config = config or RetrievalConfig()
        self.encoder = QueryEncoder(core.e8_projector)
        
        # 統計
        self.stats = {
            "total_queries": 0,
            "avg_retrieval_time": 0.0,
            "collapse_used": 0
        }
    
    def retrieve(self, 
                 query: str,
                 keywords: List[str] = None,
                 filter_ids: List[str] = None) -> List[RetrievalResult]:
        """
        檢索記憶 (ICT Collapse)
        
        Args:
            query: 查詢文本
            keywords: 關鍵詞列表
            filter_ids: 只檢索這些 ID
            
        Returns:
            RetrievalResult 列表（按分數排序）
        """
        import time
        start_time = time.time()
        
        # 編碼查詢
        query_vec = self.encoder.encode_with_keywords(query, keywords or [])
        
        # 計算所有記憶的分數
        candidates = []
        
        for memory in self.core.memories.values():
            # ID 過濾
            if filter_ids and memory.id not in filter_ids:
                continue
                
            # 1. Overlap 分數
            overlap = self._compute_overlap(query_vec, memory)
            
            # 2. Ethical Tension 分數
            ethical = self._compute_ethical_score(memory)
            
            # 3. Recency 分數
            recency = self._compute_recency_score(memory)
            
            # 4. 總分數
            total = (
                (1 - self.config.coherence_weight - self.config.ethical_weight - self.config.recency_weight) * overlap +
                self.config.coherence_weight * overlap +
                self.config.ethical_weight * ethical +
                self.config.recency_score * recency
            )
            
            # ICT Collapse 概率
            collapse_prob = self._compute_collapse_prob(overlap, memory)
            
            result = RetrievalResult(
                memory=memory,
                overlap_score=overlap,
                ethical_score=ethical,
                recency_score=recency,
                total_score=total,
                collapse_probability=collapse_prob
            )
            
            candidates.append(result)
        
        # 排序
        candidates.sort(key=lambda x: x.total_score, reverse=True)
        
        # 過濾低分
        candidates = [c for c in candidates if c.total_score >= self.config.min_score]
        
        # Top-K
        results = candidates[:self.config.top_k]
        
        # 更新統計
        elapsed = time.time() - start_time
        self.stats["total_queries"] += 1
        self.stats["avg_retrieval_time"] = (
            (self.stats["avg_retrieval_time"] * (self.stats["total_queries"] - 1) + elapsed)
            / self.stats["total_queries"]
        )
        
        return results
    
    def _compute_overlap(self, query_vec: np.ndarray, memory: MemorySpinor) -> float:
        """
        計算 Overlap 分數
        
        ⟨Q|Ψ_M⟩ = Σ_i w_i · c_i · ⟨E8_i| E8_query⟩
        """
        # E8 重疊
        e8_overlap = self.core.e8_projector.similarity(query_vec, memory.e8_vector)
        
        # Coherence 加權
        coherence_factor = memory.coherence / 1.5  # 正規化
        
        return e8_overlap * coherence_factor
    
    def _compute_ethical_score(self, memory: MemorySpinor) -> float:
        """
        計算 Ethical Tension 分數
        
        原則：
        - 重要記憶（高 coherence）分數高
        - 低 ethical tension 分數高
        """
        # 1 - normalized ethical tension
        ethical = 1.0 - min(1.0, memory.ethical_tension)
        
        # Coherence 相關
        coherence_bonus = memory.coherence / 2.0
        
        return ethical * (1 + coherence_bonus)
    
    def _compute_recency_score(self, memory: MemorySpinor) -> float:
        """
        計算 Recency 分數
        
        新記憶分數高
        """
        age = (datetime.now() - memory.timestamp).total_seconds()
        
        # 24小時內衰減
        max_age = 24 * 3600
        
        if age < 3600:  # 1小時內
            return 1.0
        elif age < max_age:
            return np.exp(-(age - 3600) / max_age)
        else:
            return 0.1  # 長期記憶保留基本分
    
    def _compute_collapse_prob(self, overlap: float, memory: MemorySpinor) -> float:
        """
        計算 Collapse 概率
        
        P(M) = |Overlap|² / Σ|Overlap|²
        P(M) ∝ P(M) · exp(-η · V_eth)
        """
        if not self.config.use_collapse:
            return 1.0
            
        # Boltzmann 風格的概率
        energy = -overlap + ETA * memory.ethical_tension
        
        # Softmax 風格
        prob = np.exp(-energy / self.config.collapse_temperature)
        
        return min(1.0, prob)
    
    def batch_retrieve(self, 
                       queries: List[str],
                       top_k: int = 3) -> Dict[str, List[RetrievalResult]]:
        """
        批量檢索
        
        Args:
            queries: 查詢列表
            top_k: 每個查詢返回數量
            
        Returns:
            {查詢: [結果列表]}
        """
        original_top_k = self.config.top_k
        self.config.top_k = top_k
        
        results = {}
        for query in queries:
            results[query] = self.retrieve(query)
            
        self.config.top_k = original_top_k
        return results


# ===== 快速檢索緩冲 =====
class RetrievalCache:
    """
    檢索結果緩冲
    
    避免重複計算相同查詢
    """
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 300):
        """
        初始化緩冲
        
        Args:
            max_size: 最大緩冲大小
            ttl_seconds: 存活時間
        """
        self.cache: Dict[str, Tuple[List[RetrievalResult], datetime]] = {}
        self.max_size = max_size
        self.ttl = ttl_seconds
        
    def get(self, query: str) -> Optional[List[RetrievalResult]]:
        """
        獲取緩冲結果
        """
        if query not in self.cache:
            return None
            
        results, timestamp = self.cache[query]
        
        # 檢查 TTL
        if (datetime.now() - timestamp).total_seconds() > self.ttl:
            del self.cache[query]
            return None
            
        return results
    
    def set(self, query: str, results: List[RetrievalResult]):
        """
        設置緩冲
        """
        # 清理過期
        if len(self.cache) >= self.max_size:
            self._cleanup()
            
        self.cache[query] = (results, datetime.now())
    
    def _cleanup(self):
        """清理過期條目"""
        now = datetime.now()
        expired = [
            q for q, (_, ts) in self.cache.items()
            if (now - ts).total_seconds() > self.ttl
        ]
        for q in expired:
            del self.cache[q]
    
    def clear(self):
        """清空緩冲"""
        self.cache.clear()


# ===== 整合檢索器 =====
class FastRetriever:
    """
    快速檢索器
    
    整合：
    - ICT Retriever
    - Retrieval Cache
    """
    
    def __init__(self, 
                 core: QSTMemoryCore,
                 config: RetrievalConfig = None):
        """
        初始化
        """
        self.retriever = ICTRetriever(core, config)
        self.cache = RetrievalCache()
        
    def retrieve(self, 
                 query: str,
                 keywords: List[str] = None,
                 use_cache: bool = True) -> List[RetrievalResult]:
        """
        檢索（帶緩冲）
        """
        # 檢查緩冲
        if use_cache:
            cached = self.cache.get(query)
            if cached:
                return cached
        
        # 執行檢索
        results = self.retriever.retrieve(query, keywords)
        
        # 緩冲
        if use_cache:
            self.cache.set(query, results)
            
        return results
    
    def retrieve_with_context(self,
                              query: str,
                              context: str,
                              context_weight: float = 0.3) -> List[RetrievalResult]:
        """
        帶上下文檢索
        
        混合查詢和上下文向量
        """
        # 獲取上下文相關結果
        context_results = self.retriever.retrieve(context, top_k=10)
        
        # 獲取查詢相關結果
        query_results = self.retriever.retrieve(query, top_k=10)
        
        # 合併（去重）
        seen_ids = set()
        merged = []
        
        for r in context_results + query_results:
            if r.memory.id not in seen_ids:
                seen_ids.add(r.memory.id)
                # 重新計算混合分數
                r.total_score = (
                    (1 - context_weight) * r.overlap_score +
                    context_weight * r.overlap_score
                )
                merged.append(r)
        
        # 排序
        merged.sort(key=lambda x: x.total_score, reverse=True)
        
        return merged[:self.retriever.config.top_k]
    
    def get_stats(self) -> dict:
        """
        獲取統計
        """
        return {
            **self.retriever.stats,
            "cache_size": len(self.cache.cache)
        }


# ===== 便捷函數 =====
def create_retriever(core: QSTMemoryCore,
                     top_k: int = 5) -> FastRetriever:
    """創建快速檢索器"""
    config = RetrievalConfig(top_k=top_k)
    return FastRetriever(core, config)


# ===== 測試 =====
if __name__ == "__main__":
    print("=== ICT Retrieval Test ===\n")
    
    # 初始化
    from short_term import ShortTermMemory
    
    short_mem = ShortTermMemory()
    
    # 添加一些測試記憶
    short_mem.add_conversation("user", "秦王是皇帝", "user")
    short_mem.add_conversation("assistant", "臣李斯參見陛下！", "assistant")
    short_mem.add_conversation("user", "我是Eddy", "user")
    short_mem.add_conversation("assistant", "Edda陛下萬歲！", "assistant")
    short_mem.add_conversation("user", "QST理論是什麼？", "user")
    
    # 轉換為記憶
    short_mem.consolidate_to_short()
    
    # 創建檢索器
    retriever = create_retriever(short_mem.core, top_k=3)
    
    # 測試檢索
    print("=== Query: '皇帝' ===")
    results = retriever.retrieve("皇帝")
    for i, r in enumerate(results):
        print(f"{i+1}. [{r.collapse_prob:.3f}] {r.memory.content[:40]}...")
    
    print("\n=== Query: 'QST' ===")
    results = retriever.retrieve("QST理論")
    for i, r in enumerate(results):
        print(f"{i+1}. [{r.collapse_prob:.3f}] {r.memory.content[:40]}...")
    
    print("\n=== With Cache ===")
    results2 = retriever.retrieve("皇帝")  # 應該命中緩冲
    print(f"Cache used: {len(retriever.cache.cache)} items")
    
    print("\n=== Stats ===")
    print(retriever.get_stats())
    
    print("\n=== Complete ===")
