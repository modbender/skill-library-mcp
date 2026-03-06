"""
QST Memory Optimization - Advanced Retrieval Algorithms

高級檢索算法優化。

包含：
- 多路徑檢索
- 負載均衡
- 並行處理
- 近似最近鄰 (ANN)
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import threading
import heapq
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

from memory_core import QSTMemoryCore, MemorySpinor, E8Projector
from retrieval import RetrievalResult, RetrievalConfig


# ===== 配置 =====
@dataclass
class OptimizationConfig:
    """優化配置"""
    use_ann: bool = True              # 使用近似最近鄰
    ann_threshold: float = 0.8        # ANN 閾值
    parallel_threads: int = 4         # 並行線程數
    cache_enabled: bool = True        # 啟用緩冲
    cache_size: int = 1000           # 緩冲大小
    batch_size: int = 100             # 批量大小


# ===== 緩冲條目 =====
@dataclass
class CacheEntry:
    """緩冲條目"""
    result: List[RetrievalResult]
    timestamp: datetime
    hits: int = 0
    
    def __lt__(self, other):
        return self.hits > other.hits  # 按 hits 排序


# ===== 高級檢索器 =====
class OptimizedRetriever:
    """
    高級檢索器
    
    優化策略：
    - 近似最近鄰 (ANN) 快速過濾
    - 並行檢索
    - 多路徑融合
    """
    
    def __init__(self,
                 core: QSTMemoryCore,
                 config: OptimizationConfig = None):
        """
        初始化
        
        Args:
            core: QST 記憶核心
            config: 配置
        """
        self.core = core
        self.config = config or OptimizationConfig()
        
        # ANN 索引
        self.ann_index: Optional['AnnIndex'] = None
        if self.config.use_ann:
            self._build_ann_index()
        
        # 緩冲
        self.cache: Dict[str, CacheEntry] = {}
        self.cache_lock = threading.Lock()
        
        # 統計
        self.stats = {
            "total_queries": 0,
            "cache_hits": 0,
            "ann_uses": 0,
            "parallel_uses": 0
        }
    
    def _build_ann_index(self):
        """構建 ANN 索引"""
        # 簡化實現：使用 KD-Tree
        # 實際應用可替換為 FAISS/Annoy
        
        if len(self.core.memories) < 10:
            return  # 樣本太少，不構建
        
        # 收集所有向量
        vectors = []
        ids = []
        for mid, memory in self.core.memories.items():
            vectors.append(memory.e8_vector)
            ids.append(mid)
        
        self.ann_index = KDTreeIndex(np.array(vectors), ids)
        self.ann_ids = set(ids)
    
    def retrieve(self,
                 query: str,
                 top_k: int = 5,
                 method: str = "hybrid") -> List[RetrievalResult]:
        """
        檢索（優化版）
        
        Args:
            query: 查詢
            top_k: 返回數量
            method: "ann" | "exact" | "hybrid"
            
        Returns:
            檢索結果
        """
        # 檢查緩冲
        cache_key = self._get_cache_key(query, top_k)
        if self.config.cache_enabled:
            cached = self._get_cache(cache_key)
            if cached:
                self.stats["cache_hits"] += 1
                return cached[:top_k]
        
        # 選擇檢索方法
        if method == "ann" and self.ann_index:
            results = self._retrieve_ann(query, top_k)
        elif method == "parallel":
            results = self._retrieve_parallel(query, top_k)
        elif method == "hybrid":
            results = self._retrieve_hybrid(query, top_k)
        else:
            results = self._retrieve_exact(query, top_k)
        
        # 更新統計
        self.stats["total_queries"] += 1
        
        # 緩冲
        if self.config.cache_enabled:
            self._set_cache(cache_key, results)
        
        return results[:top_k]
    
    def _retrieve_exact(self,
                       query: str,
                       top_k: int) -> List[RetrievalResult]:
        """精確檢索"""
        return self.core.retrieve(query, top_k)
    
    def _retrieve_ann(self,
                     query: str,
                     top_k: int) -> List[RetrievalResult]:
        """ANN 檢索"""
        if not self.ann_index:
            return self._retrieve_exact(query, top_k)
        
        self.stats["ann_uses"] += 1
        
        # 編碼查詢
        query_vec = self.core.e8_projector.project(0.9, 0)
        
        # ANN 搜索
        ann_results = self.ann_index.search(query_vec, k=top_k * 3)
        
        # 獲取完整結果
        results = []
        for mid, score in ann_results:
            if mid in self.core.memories:
                memory = self.core.memories[mid]
                results.append(RetrievalResult(
                    memory=memory,
                    overlap_score=score,
                    ethical_score=1.0 - memory.ethical_tension,
                    recency_score=1.0,
                    total_score=score,
                    collapse_probability=score
                ))
        
        return results[:top_k]
    
    def _retrieve_parallel(self,
                        query: str,
                        top_k: int) -> List[RetrievalResult]:
        """並行檢索"""
        self.stats["parallel_uses"] += 1
        
        # 分組
        memories = list(self.core.memories.values())
        batch_size = len(memories) // self.config.parallel_threads
        
        def search_batch(batch: List[MemorySpinor]) -> List[Tuple[RetrievalResult, float]]:
            results = []
            for memory in batch:
                overlap = self._compute_overlap(query, memory)
                results.append((RetrievalResult(
                    memory=memory,
                    overlap_score=overlap,
                    ethical_score=1.0 - memory.ethical_tension,
                    recency_score=1.0,
                    total_score=overlap,
                    collapse_probability=overlap
                ), overlap))
            return results
        
        # 並行執行
        with ThreadPoolExecutor(max_workers=self.config.parallel_threads) as executor:
            futures = []
            for i in range(0, len(memories), batch_size):
                batch = memories[i:i + batch_size]
                futures.append(executor.submit(search_batch, batch))
            
            all_results = []
            for future in as_completed(futures):
                all_results.extend(future.result())
        
        # 排序
        all_results.sort(key=lambda x: x[1], reverse=True)
        
        return [r[0] for r in all_results[:top_k]]
    
    def _retrieve_hybrid(self,
                       query: str,
                       top_k: int) -> List[RetrievalResult]:
        """混合檢索：ANN + Exact"""
        # 第一階段：ANN 快速過濾
        if self.ann_index and len(self.core.memories) > 100:
            # ANN 獲取候選集
            ann_results = self._retrieve_ann(query, top_k * 5)
            candidate_ids = {r.memory.id for r in ann_results}
            
            # 精確計算候選集
            results = []
            for r in ann_results:
                overlap = self._compute_overlap(query, r.memory)
                r.overlap_score = overlap
                r.total_score = overlap
                r.collapse_probability = overlap
                results.append(r)
            
            # 精確搜索補全
            if len(results) < top_k:
                exact = self._retrieve_exact(query, top_k)
                for r in exact:
                    if r.memory.id not in candidate_ids:
                        results.append(r)
        else:
            results = self._retrieve_exact(query, top_k)
        
        return results[:top_k]
    
    def _compute_overlap(self, query: str, memory: MemorySpinor) -> float:
        """計算 overlap"""
        query_vec = self.core.e8_projector.project(0.9, 0)
        return self.core.e8_projector.similarity(query_vec, memory.e8_vector)
    
    def _get_cache_key(self, query: str, top_k: int) -> str:
        """生成緩冲 key"""
        data = f"{query}_{top_k}_{datetime.now().strftime('%Y%m%d%H')}"
        return hashlib.md5(data.encode()).hexdigest()
    
    def _get_cache(self, key: str) -> Optional[List[RetrievalResult]]:
        """獲取緩冲"""
        with self.cache_lock:
            if key in self.cache:
                entry = self.cache[key]
                entry.hits += 1
                return entry.result
        return None
    
    def _set_cache(self, key: str, results: List[RetrievalResult]):
        """設置緩冲"""
        with self.cache_lock:
            # LRU 清理
            if len(self.cache) >= self.config.cache_size:
                smallest = heapq.nsmallest(
                    int(self.config.cache_size * 0.2),
                    self.cache.items(),
                    key=lambda x: x[1].hits
                )
                for k, _ in smallest:
                    del self.cache[k]
            
            self.cache[key] = CacheEntry(
                result=results,
                timestamp=datetime.now()
            )
    
    def get_stats(self) -> Dict:
        """獲取統計"""
        return {
            **self.stats,
            "cache_size": len(self.cache),
            "memory_count": len(self.core.memories),
            "ann_built": self.ann_index is not None
        }
    
    def clear_cache(self):
        """清空緩冲"""
        with self.cache_lock:
            self.cache.clear()


# ===== KD-Tree 實現（簡化版）=====
class KDTreeIndex:
    """
    簡化 KD-Tree ANN 索引
    
    注意：生產環境建議使用 FAISS/Annoy
    """
    
    def __init__(self, points: np.ndarray, ids: List[str]):
        """
        初始化
        
        Args:
            points: 數據點 (n x d)
            ids: 對應 ID
        """
        self.points = points
        self.ids = ids
        self.kd_tree = self._build_kdtree(points)
    
    def _build_kdtree(self, points: np.ndarray):
        """構建 KD-Tree"""
        try:
            from scipy.spatial import cKDTree
            return cKDTree(points)
        except ImportError:
            # 簡化實現
            return None
    
    def search(self, query: np.ndarray, k: int = 5) -> List[Tuple[str, float]]:
        """
        搜索
        
        Args:
            query: 查詢向量
            k: 返回數量
            
        Returns:
            [(id, distance)] 列表
        """
        if self.kd_tree is None:
            # 暴力搜索
            distances = np.linalg.norm(self.points - query, axis=1)
            sorted_indices = np.argsort(distances)[:k]
            return [
                (self.ids[i], 1.0 / (1.0 + distances[i]))
                for i in sorted_indices
            ]
        
        # KD-Tree 搜索
        distances, indices = self.kd_tree.query(query, k=min(k, len(self.points)))
        
        results = []
        for i, dist in zip(indices, distances):
            if i < len(self.ids):
                score = 1.0 / (1.0 + dist)
                results.append((self.ids[i], score))
        
        return results


# ===== 多路徑融合 =====
class MultiPathFusion:
    """
    多路徑結果融合
    
    策略：
    - Reciprocal Rank Fusion (RRF)
    - Score Fusion
    - Voting
    """
    
    def __init__(self, methods: List[str] = None):
        """
        初始化
        
        Args:
            methods: 檢索方法列表
        """
        self.methods = methods or ["qst", "embedding", "keyword"]
    
    def fuse_rrf(self,
                results_dict: Dict[str, List[RetrievalResult]],
                k: int = 60) -> List[Tuple[str, float]]:
        """
        Reciprocal Rank Fusion
        
        RRF(d) = Σ 1 / (k + rank(d))
        """
        scores: Dict[str, float] = {}
        
        for method, results in results_dict.items():
            for rank, r in enumerate(results):
                mid = r.memory.id
                rrf_score = 1.0 / (k + rank + 1)
                scores[mid] = scores.get(mid, 0) + rrf_score
        
        # 排序
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_scores
    
    def fuse_weighted(self,
                     results_dict: Dict[str, List[RetrievalResult]],
                     weights: Dict[str, float] = None) -> List[Tuple[str, float]]:
        """
        加權分數融合
        
        Score = Σ w_i * score_i
        """
        weights = weights or {m: 1.0 / len(results_dict) for m in results_dict}
        
        scores: Dict[str, float] = {}
        max_scores: Dict[str, float] = {}
        
        for method, results in results_dict.items():
            w = weights.get(method, 1.0)
            
            # 找到最大分數用於正規化
            if results:
                max_score = max(r.total_score for r in results)
                if max_score > 0:
                    for r in results:
                        mid = r.memory.id
                        normalized = r.total_score / max_score
                        scores[mid] = scores.get(mid, 0) + w * normalized
        
        # 排序
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_scores


# ===== 負載均衡 =====
class LoadBalancer:
    """
    負載均衡器
    
    策略：
    - Round Robin
    - Least Connections
    - Weighted
    """
    
    def __init__(self, retrievers: List[OptimizedRetriever]):
        """
        初始化
        
        Args:
            retrievers: 檢索器列表
        """
        self.retrievers = retrievers
        self.rr_index = 0
        self.connections = [0] * len(retrievers)
        self.lock = threading.Lock()
    
    def select(self, method: str = "least_connections") -> OptimizedRetriever:
        """
        選擇檢索器
        
        Args:
            method: "round_robin" | "least_connections"
        """
        with self.lock:
            if method == "round_robin":
                self.rr_index = (self.rr_index + 1) % len(self.retrievers)
                return self.retrievers[self.rr_index]
            
            elif method == "least_connections":
                min_idx = min(range(len(self.retrievers)), 
                             key=lambda i: self.connections[i])
                self.connections[min_idx] += 1
                return self.retrievers[min_idx]
            
            return self.retrievers[0]
    
    def release(self, retriever: OptimizedRetriever):
        """釋放連接"""
        with self.lock:
            idx = self.retrievers.index(retriever)
            self.connections[idx] = max(0, self.connections[idx] - 1)


# ===== 便捷函數 =====
def create_optimized_retriever(core: QSTMemoryCore,
                             use_ann: bool = True,
                             parallel: bool = True) -> OptimizedRetriever:
    """創建優化檢索器"""
    config = OptimizationConfig(
        use_ann=use_ann,
        parallel_threads=4 if parallel else 1
    )
    return OptimizedRetriever(core, config)


# ===== 測試 =====
if __name__ == "__main__":
    print("=== Optimization Test ===\n")
    
    from memory_core import QSTMemoryCore
    from short_term import ShortTermMemory
    
    # 初始化
    short_mem = ShortTermMemory()
    
    # 添加測試數據
    print("Creating test memories...")
    for i in range(50):
        short_mem.add_conversation(
            "user", 
            f"Test memory {i} - {"皇帝丞相將軍"[:i%10]}",
            "user"
        )
    
    # 轉換為記憶
    short_mem.consolidate_to_short()
    
    # 創建優化檢索器
    print("\nCreating optimized retriever...")
    optimizer = create_optimized_retriever(short_mem.core)
    
    # 測試檢索
    print("\nTesting retrieval...")
    results = optimizer.retrieve("皇帝", top_k=5)
    print(f"Results: {len(results)}")
    
    for i, r in enumerate(results):
        print(f"  {i+1}. [{r.total_score:.3f}] {r.memory.content[:40]}")
    
    # 統計
    print("\nStats:")
    print(optimizer.get_stats())
    
    # 測試混合檢索
    print("\n=== Hybrid Retrieval ===")
    hybrid_results = optimizer.retrieve("將軍", top_k=5, method="hybrid")
    for i, r in enumerate(hybrid_results):
        print(f"  {i+1}. [{r.total_score:.3f}] {r.memory.content[:40]}")
    
    # 多路徑融合
    print("\n=== Multi-Path Fusion ===")
    results_dict = {
        "qst": optimizer.retrieve("丞相", top_k=5),
        "embedding": optimizer.retrieve("丞相", top_k=5)
    }
    
    fusion = MultiPathFusion()
    fused = fusion.fuse_weighted(results_dict)
    
    for mid, score in fused[:5]:
        print(f"  [{score:.3f}] {short_mem.core.memories[mid].content[:40]}")
    
    print("\n=== Complete ===")
