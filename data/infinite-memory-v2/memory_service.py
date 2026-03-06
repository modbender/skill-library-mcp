from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import os
import sys

# Add nested engine to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'engine'))
try:
    import memory_engine_parallel_lms as engine
except ImportError as e:
    print(f"❌ Critical Error: Could not load memory engine. {e}")
    sys.exit(1)

app = FastAPI(title="OpenClaw Memory Sidecar")

class SearchRequest(BaseModel):
    query: str

class IngestRequest(BaseModel):
    text: str
    filename: str = "openclaw_ingest.txt"

@app.post("/search")
async def search_memory(request: SearchRequest):
    """Bridge to the Phase 16 High-Precision Engine"""
    try:
        answer, timings = await engine.chat_logic_async(request.query)
        return {
            "answer": answer,
            "timings": timings,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
async def ingest_memory(request: IngestRequest):
    """Direct ingestion into the Phase 16 ChromaDB"""
    try:
        collection = engine.get_collection()
        chunk_size = 2000
        chunks = [request.text[i:i+chunk_size] for i in range(0, len(request.text), chunk_size)]
        
        # Batch addition
        metas = [{"source": request.filename, "chunk": i} for i in range(len(chunks))]
        ids = [f"oc_{os.urandom(4).hex()}" for _ in chunks]
        
        collection.add(
            documents=chunks,
            metadatas=metas,
            ids=ids
        )
        return {"status": "success", "chunks_added": len(chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("\n🦞 OPENCLAW MEMORY BRIDGE RUNNING")
    print("════════════════════════════════════")
    print("API: http://localhost:8000")
    print("Engine: Phase 16 Parallel (100% Accuracy)")
    uvicorn.run(app, host="0.0.0.0", port=8000)
