"""
QST Memory Embedding - Embedding Integration

Embedding 整合層。

支持：
- OpenAI Embeddings
- Sentence Transformers
- 自定義 Embedding
- QST + Embedding 混合檢索
"""

import numpy as np
from typing import List, Dict, Optional, Union, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod

from memory_core import QSTMemoryCore, MemorySpinor


# ===== Embedding 配置 =====
@dataclass
class EmbeddingConfig:
    """Embedding 配置"""
    model: str = "text-embedding-3-small"
    api_key: str = None
    base_url: str = None
    dimensions: int = 1536
    normalize: bool = True


# ===== Embedding 介面 =====
class EmbeddingProvider(ABC):
    """Embedding 提供者介面"""
    
    @abstractmethod
    def encode(self, texts: List[str]) -> np.ndarray:
        """
        編碼文本為向量
        
        Args:
            texts: 文本列表
            
        Returns:
            向量矩陣 (n x d)
        """
        pass
    
    @abstractmethod
    def encode_single(self, text: str) -> np.ndarray:
        """編碼單一文本"""
        pass


# ===== OpenAI Embedding =====
class OpenAIEmbedding(EmbeddingProvider):
    """OpenAI Embedding 提供者"""
    
    def __init__(self, config: EmbeddingConfig = None):
        """
        初始化
        
        Args:
            config: 配置
        """
        self.config = config or EmbeddingConfig()
        
        # 初始化客戶端
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url
            )
        except ImportError:
            print("Warning: openai package not installed")
            self.client = None
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """編碼文本"""
        if not self.client:
            # 返回零向量
            return np.zeros((len(texts), self.config.dimensions))
        
        response = self.client.embeddings.create(
            model=self.config.model,
            input=texts,
            dimensions=self.config.dimensions
        )
        
        vectors = np.array([e.embedding for e in response.data])
        
        if self.config.normalize:
            vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
            
        return vectors
    
    def encode_single(self, text: str) -> np.ndarray:
        """編碼單一文本"""
        return self.encode([text])[0]


# ===== Sentence Transformers =====
class SentenceTransformerEmbedding(EmbeddingProvider):
    """Sentence Transformers 提供者"""
    
    def __init__(self, 
                 model_name: str = "all-MiniLM-L6-v2",
                 device: str = None):
        """
        初始化
        
        Args:
            model_name: 模型名稱
            device: "cpu" | "cuda" | None (自動)
        """
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name, device=device)
            self.config = EmbeddingConfig(model=model_name)
        except ImportError:
            print("Warning: sentence-transformers package not installed")
            self.model = None
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """編碼文本"""
        if not self.model:
            return np.zeros((len(texts), 384))
        
        vectors = self.model.encode(texts, normalize_embeddings=True)
        return vectors
    
    def encode_single(self, text: str) -> np.ndarray:
        """編碼單一文本"""
        return self.encode([text])[0]


# ===== 簡化 Embedding (TF-IDF 風格) =====
class SimpleEmbedding(EmbeddingProvider):
    """簡化 Embedding (基於詞頻)"""
    
    def __init__(self, vocab_size: int = 10000, dimensions: int = 768):
        """
        初始化
        
        Args:
            vocab_size: 詞彙表大小
            dimensions: 向量維度
        """
        self.vocab_size = vocab_size
        self.dimensions = dimensions
        self.vocab: Dict[str, int] = {}
        self._build_vocab()
    
    def _build_vocab(self):
        """構建詞彙表"""
        import re
        import collections
        
        # 常見詞
        common_words = [
            "我", "你", "他", "她", "它", "我們", "你們", "他們",
            "是", "有", "在", "不是", "沒有", "在", "和", "或",
            "皇帝", "丞相", "將軍", "大臣", "王", "陛下",
            "記憶", "知識", "理論", "系統", "數據", "計算",
            "時間", "空間", "能量", "物質", "量子", "信息"
        ]
        
        for i, word in enumerate(common_words):
            if i < self.vocab_size:
                self.vocab[word] = i
    
    def _tokenize(self, text: str) -> List[str]:
        """簡單分詞"""
        import re
        # 中英文混合分詞
        tokens = re.findall(r'[\w\u4e00-\u9fff]+', text.lower())
        return tokens
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """編碼文本"""
        vectors = np.zeros((len(texts), self.dimensions))
        
        for i, text in enumerate(texts):
            tokens = self._tokenize(text)
            
            # 詞頻統計
            freq = collections.Counter(tokens)
            
            # 填充向量
            for token, count in freq.items():
                if token in self.vocab:
                    idx = self.vocab[token]
                    if idx < self.dimensions:
                        vectors[i, idx] = count
        
        # 正規化
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1
        vectors = vectors / norms
        
        return vectors
    
    def encode_single(self, text: str) -> np.ndarray:
        """編碼單一文本"""
        return self.encode([text])[0]


# ===== QST + Embedding 混合記憶 =====
class HybridMemoryCore:
    """
    QST + Embedding 混合記憶核心
    
    結合：
    - QST Matrix 結構化檢索
    - Embedding 語義相似度
    """
    
    def __init__(self,
                 qst_core: QSTMemoryCore,
                 embedding_provider: EmbeddingProvider = None):
        """
        初始化
        
        Args:
            qst_core: QST 記憶核心
            embedding_provider: Embedding 提供者
        """
        self.qst_core = qst_core
        self.embedding_provider = embedding_provider or SimpleEmbedding()
        
        # Embedding 緩冲
        self.embedding_cache: Dict[str, np.ndarray] = {}
        
    def encode(self, 
               content: str,
               coherence: float = 0.8,
               dsi_level: int = 0) -> MemorySpinor:
        """
        編碼並創建記憶
        
        Args:
            content: 內容
            coherence: Coherence
            dsi_level: DSI 層次
            
        Returns:
            MemorySpinor
        """
        # QST 編碼
        memory = self.qst_core.encode(content, coherence, dsi_level)
        
        # Embedding 編碼
        if content not in self.embedding_cache:
            self.embedding_cache[content] = self.embedding_provider.encode_single(content)
        
        memory.embedding = self.embedding_cache[content]
        
        return memory
    
    def retrieve(self, 
                 query: str,
                 top_k: int = 5,
                 qst_weight: float = 0.5,
                 embedding_weight: float = 0.5) -> List[Dict]:
        """
        混合檢索
        
        Args:
            query: 查詢
            top_k: 返回數量
            qst_weight: QST 權重
            embedding_weight: Embedding 權重
            
        Returns:
            結果列表
        """
        # QST 檢索
        qst_results = self.qst_core.retrieve(query, top_k * 2)
        
        # Embedding 檢索
        if query not in self.embedding_cache:
            self.embedding_cache[query] = self.embedding_provider.encode_single(query)
        
        query_embedding = self.embedding_cache[query]
        
        embedding_results = []
        for memory in self.qst_core.memories.values():
            if hasattr(memory, 'embedding') and memory.embedding is not None:
                # Cosine similarity
                similarity = np.dot(query_embedding, memory.embedding)
                embedding_results.append((memory, similarity))
        
        # 按相似度排序
        embedding_results.sort(key=lambda x: x[1], reverse=True)
        embedding_results = embedding_results[:top_k * 2]
        
        # 合併分數
        merged_scores: Dict[str, float] = {}
        
        for i, (memory, score) in enumerate(qst_results):
            qst_score = 1.0 - i / (len(qst_results) + 1)
            if memory.id in merged_scores:
                merged_scores[memory.id] += qst_weight * qst_score
            else:
                merged_scores[memory.id] = qst_weight * qst_score
        
        for i, (memory, score) in enumerate(embedding_results):
            emb_score = 1.0 - i / (len(embedding_results) + 1)
            if memory.id in merged_scores:
                merged_scores[memory.id] += embedding_weight * emb_score
            else:
                merged_scores[memory.id] = embedding_weight * emb_score
        
        # 排序並返回
        sorted_ids = sorted(merged_scores.keys(), 
                          key=lambda x: merged_scores[x], 
                          reverse=True)
        
        results = []
        for mid in sorted_ids[:top_k]:
            memory = self.qst_core.memories[mid]
            results.append({
                "memory": memory,
                "total_score": merged_scores[mid],
                "qst_score": merged_scores.get(mid, 0) * qst_weight,
                "embedding_score": merged_scores.get(mid, 0) * embedding_weight
            })
        
        return results
    
    def clear_cache(self):
        """清空 Embedding 緩冲"""
        self.embedding_cache.clear()


# ===== Embedding 工廠 =====
def create_embedding_provider(
    provider_type: str = "simple",
    **kwargs
) -> EmbeddingProvider:
    """
    創建 Embedding 提供者
    
    Args:
        provider_type: "openai" | "sentence_transformers" | "simple"
        **kwargs: 其他參數
        
    Returns:
        EmbeddingProvider 實例
    """
    if provider_type == "openai":
        config = EmbeddingConfig(
            model=kwargs.get("model", "text-embedding-3-small"),
            api_key=kwargs.get("api_key"),
            base_url=kwargs.get("base_url"),
            dimensions=kwargs.get("dimensions", 1536)
        )
        return OpenAIEmbedding(config)
    
    elif provider_type == "sentence_transformers":
        return SentenceTransformerEmbedding(
            model_name=kwargs.get("model_name", "all-MiniLM-L6-v2"),
            device=kwargs.get("device")
        )
    
    else:
        return SimpleEmbedding(
            vocab_size=kwargs.get("vocab_size", 10000),
            dimensions=kwargs.get("dimensions", 768)
        )


# ===== 測試 =====
if __name__ == "__main__":
    print("=== Embedding Integration Test ===\n")
    
    # 初始化
    from memory_core import QSTMemoryCore
    
    qst_core = QSTMemoryCore()
    
    # 測試 Simple Embedding
    print("1. Testing Simple Embedding...")
    simple = create_embedding_provider("simple")
    vec = simple.encode_single("秦王是皇帝")
    print(f"   Vector shape: {vec.shape}")
    
    # 測試混合記憶
    print("\n2. Testing Hybrid Memory...")
    hybrid = HybridMemoryCore(qst_core, simple)
    
    # 創建記憶
    memories = [
        "秦王是皇帝",
        "李斯是丞相",
        "蒙恬是將軍",
        "QST是量子時空理論",
        "AI需要記憶系統"
    ]
    
    for content in memories:
        hybrid.encode(content, 0.9, 1)
    
    print(f"   Created {len(hybrid.qst_core.memories)} memories")
    
    # 混合檢索
    print("\n3. Hybrid Retrieval Test...")
    results = hybrid.retrieve("誰是大臣？", top_k=3)
    
    for i, r in enumerate(results):
        print(f"   {i+1}. [{r['total_score']:.3f}] {r['memory'].content}")
    
    # 測試 Embedding 相似度
    print("\n4. Embedding Similarity Test...")
    vec1 = simple.encode_single("皇帝")
    vec2 = simple.encode_single("國王")
    vec3 = simple.encode_single("記憶")
    
    sim_12 = np.dot(vec1, vec2)
    sim_13 = np.dot(vec1, vec3)
    
    print(f"   皇帝 vs 國王: {sim_12:.4f}")
    print(f"   皇帝 vs 記憶: {sim_13:.4f}")
    
    print("\n=== Complete ===")
