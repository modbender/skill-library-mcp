#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
import faiss
import os
import logging
from typing import List

# --- 日誌設定 ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("memory-pro")

# --- 環境變數設定 ---
base_dir = os.path.dirname(os.path.abspath(__file__))
index_dir = os.getenv("MEMORY_PRO_INDEX_DIR", base_dir)

MEMORY_PRO_PORT = int(os.getenv("MEMORY_PRO_PORT", "8001"))
MEMORY_PRO_INDEX_PATH = os.getenv("MEMORY_PRO_INDEX_PATH", os.path.join(index_dir, "memory.index"))

# --- 初始化 ---
app = FastAPI(title="Memory Pro API", description="Semantic Search Service for OpenClaw Memory")

# 全局變數 (延遲初始化)
model = None
index = None
sentences = []

# --- Pydantic 模型 ---
class SearchRequest(BaseModel):
    query: str = Field(..., description="搜尋查詢字串", min_length=1)
    top_k: int = Field(3, ge=1, le=20, description="返回結果數量")

class SearchResult(BaseModel):
    score: float
    sentence: str

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]

# --- 啟動事件 ---
@app.on_event("startup")
async def startup_event():
    global model, index, sentences
    try:
        logger.info("Starting Memory Pro service...")
        
        # 載入模型
        logger.info("Loading SentenceTransformer model...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # 載入索引
        index_path = MEMORY_PRO_INDEX_PATH
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"FAISS index not found at {index_path}")
        logger.info(f"Loading FAISS index from {index_path}...")
        index = faiss.read_index(index_path)
        
        # 載入句子
        logger.info("Loading sentences via preprocess_directory()...")
        from preprocess import preprocess_directory
        sentences = preprocess_directory()
        
        # 驗證同步
        if index.ntotal != len(sentences):
            error_msg = f"Index size mismatch: FAISS has {index.ntotal}, sentences list has {len(sentences)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        logger.info(f"Service ready. Indexed {len(sentences)} items.")
        
    except Exception as e:
        logger.critical(f"Startup failed: {e}")
        raise e

# --- 健康檢查 ---
@app.get("/health")
async def health_check():
    if model is None or index is None or not sentences:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return {"status": "ok", "indexed_items": len(sentences)}

# --- 搜尋端點 ---
@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    try:
        query = request.query.strip()
        top_k = request.top_k

        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        # 向量化
        query_embedding = model.encode([query])

        # FAISS 搜尋
        distances, indices = index.search(query_embedding, top_k)

        # 組裝結果
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx != -1:
                if 0 <= idx < len(sentences):
                    results.append({
                        "score": float(1 - distance),
                        "sentence": sentences[idx]
                    })
                else:
                    logger.warning(f"Index {idx} out of bounds for sentences list (len={len(sentences)})")

        return {
            "query": query,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
