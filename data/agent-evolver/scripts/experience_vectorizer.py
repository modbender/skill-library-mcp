#!/usr/bin/env python3
"""
Experience Vectorizer - 经验向量化模块
将经验转化为向量表示，支持语义搜索
"""

import json
import os
import hashlib
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class VectorSearchResult:
    """向量搜索结果"""
    experience_id: str
    similarity: float
    metadata: Dict[str, Any]


class ExperienceVectorizer:
    """将经验转化为向量表示，支持语义搜索"""
    
    def __init__(self, api_key: str = None, model: str = "text-embedding-3-small"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        self.vector_store = None
        self._init_vector_store()
    
    def _init_vector_store(self):
        """初始化向量存储"""
        try:
            import chromadb
            from chromadb.config import Settings
            
            persist_dir = os.path.expanduser("~/.evolver/chroma")
            os.makedirs(persist_dir, exist_ok=True)
            
            self.vector_store = chromadb.PersistentClient(
                path=persist_dir,
                settings=Settings(anonymized_telemetry=False)
            )
            
            self.collection = self.vector_store.get_or_create_collection(
                name="experiences",
                metadata={"description": "Agent evolution experiences"}
            )
        except ImportError:
            print("Warning: chromadb not installed, vector search disabled")
            self.vector_store = None
            self.collection = None
    
    def vectorize_experience(self, capsule) -> Optional[str]:
        """将经验胶囊转化为向量"""
        if not self.vector_store or not self.api_key:
            return None
        
        try:
            text = self._build_experience_text(capsule)
            
            embedding = self._get_embedding(text)
            
            if not embedding:
                return None
            
            vector_id = f"vec_{hashlib.md5(capsule.id.encode()).hexdigest()[:12]}"
            
            self.collection.add(
                ids=[vector_id],
                embeddings=[embedding],
                metadatas=[{
                    "experience_id": capsule.id,
                    "error_type": capsule.error_type,
                    "task_type": capsule.task_type,
                    "status": capsule.status
                }],
                documents=[text]
            )
            
            return vector_id
            
        except Exception as e:
            print(f"Vectorization failed: {e}")
            return None
    
    def search_similar_experiences(self, query: str, 
                                    top_k: int = 5) -> List[VectorSearchResult]:
        """搜索相似经验"""
        if not self.vector_store or not self.api_key:
            return []
        
        try:
            query_embedding = self._get_embedding(query)
            
            if not query_embedding:
                return []
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            search_results = []
            
            if results and results['ids']:
                for i, exp_id in enumerate(results['ids'][0]):
                    distance = results['distances'][0][i] if results.get('distances') else 0
                    similarity = 1 - distance
                    
                    metadata = results['metadatas'][0][i] if results.get('metadatas') else {}
                    
                    search_results.append(VectorSearchResult(
                        experience_id=metadata.get('experience_id', exp_id),
                        similarity=round(similarity, 3),
                        metadata=metadata
                    ))
            
            return search_results
            
        except Exception as e:
            print(f"Vector search failed: {e}")
            return []
    
    def _build_experience_text(self, capsule) -> str:
        """构建用于向量化的文本"""
        return f"""
任务类型: {capsule.task_type}
错误类型: {capsule.error_type}
错误信息: {capsule.error_message}
解决方案: {capsule.solution}
策略变更: {capsule.strategy_delta}
LLM分析: {capsule.llm_analysis}
关键词: {', '.join(capsule.keywords)}
上下文: {json.dumps(capsule.context, ensure_ascii=False)}
"""
    
    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """获取文本的向量表示"""
        if not self.api_key:
            return None
        
        try:
            import requests
            
            response = requests.post(
                f"{self.api_base}/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "input": text
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["data"][0]["embedding"]
            else:
                print(f"Embedding API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Failed to get embedding: {e}")
            return None
    
    def delete_vector(self, vector_id: str):
        """删除向量"""
        if self.vector_store and self.collection:
            try:
                self.collection.delete(ids=[vector_id])
            except Exception as e:
                print(f"Failed to delete vector: {e}")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """获取向量集合统计"""
        if not self.vector_store or not self.collection:
            return {"enabled": False, "count": 0}
        
        try:
            count = self.collection.count()
            return {
                "enabled": True,
                "count": count,
                "model": self.model
            }
        except Exception as e:
            return {"enabled": False, "error": str(e)}


class SimpleVectorIndex:
    """简单向量索引（无需外部依赖的备选方案）"""
    
    def __init__(self, index_path: str = None):
        self.index_path = index_path or os.path.expanduser("~/.evolver/vector_index.json")
        self.index = self._load_index()
    
    def _load_index(self) -> Dict:
        """加载索引"""
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"experiences": [], "keywords": {}}
    
    def _save_index(self):
        """保存索引"""
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        with open(self.index_path, 'w') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
    
    def index_experience(self, capsule):
        """索引经验（基于关键词）"""
        exp_entry = {
            "id": capsule.id,
            "task_type": capsule.task_type,
            "error_type": capsule.error_type,
            "keywords": capsule.keywords,
            "solution": capsule.solution
        }
        
        self.index["experiences"].append(exp_entry)
        
        for keyword in capsule.keywords:
            keyword_lower = keyword.lower()
            if keyword_lower not in self.index["keywords"]:
                self.index["keywords"][keyword_lower] = []
            self.index["keywords"][keyword_lower].append(capsule.id)
        
        self._save_index()
    
    def search_by_keywords(self, query: str, top_k: int = 5) -> List[Dict]:
        """基于关键词搜索"""
        query_words = set(query.lower().split())
        
        matched_ids = {}
        for word in query_words:
            if word in self.index["keywords"]:
                for exp_id in self.index["keywords"][word]:
                    matched_ids[exp_id] = matched_ids.get(exp_id, 0) + 1
        
        results = []
        for exp_id, score in sorted(matched_ids.items(), 
                                     key=lambda x: x[1], 
                                     reverse=True)[:top_k]:
            for exp in self.index["experiences"]:
                if exp["id"] == exp_id:
                    results.append({
                        "experience_id": exp_id,
                        "similarity": score / len(query_words),
                        "experience": exp
                    })
                    break
        
        return results


if __name__ == "__main__":
    from evolver_core import ExperienceCapsule, ExperienceStore
    
    vectorizer = ExperienceVectorizer()
    
    capsule = ExperienceCapsule(
        id="exp_test_001",
        task_id="task_test_001",
        task_type="code_generation",
        status="failed",
        error_type="ValueError",
        error_message="不支持负数输入",
        context={"input": -5},
        solution="使用绝对值处理负数",
        strategy_delta="添加负数检查",
        metrics={},
        llm_analysis="",
        vector_id=None,
        embedding_model="",
        keywords=["负数", "平方计算", "ValueError"],
        created_at="2026-02-24T10:00:00"
    )
    
    vector_id = vectorizer.vectorize_experience(capsule)
    print(f"Vector ID: {vector_id}")
    
    results = vectorizer.search_similar_experiences("负数平方计算错误")
    print(f"Search results: {len(results)}")
    for r in results:
        print(f"  - {r.experience_id}: {r.similarity}")
