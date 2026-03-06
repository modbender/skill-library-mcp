"""FastAPI GPU service - BERTScore + Embeddings (v0.2)."""

import asyncio
import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import torch
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from device import get_device, get_device_info
from models import (
    BertScoreRequest,
    BertScoreResponse,
    EmbedRequest,
    EmbedResponse,
    HealthResponse,
    InfoResponse,
    JobStatus,
    QueueStatus,
    StatusResponse,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("gpu-service")


DEFAULT_BERTSCORE_MODEL = os.environ.get("MODEL_BERTSCORE", "microsoft/deberta-xlarge-mnli")
DEFAULT_EMBED_MODEL = os.environ.get("MODEL_EMBED", "all-MiniLM-L6-v2")


def _vram_mb() -> str:
    """Return current VRAM usage string, e.g. '412 MB / 11264 MB'."""
    if not torch.cuda.is_available():
        return "CPU"
    used = round(torch.cuda.memory_allocated(0) / 1024 / 1024)
    total = round(torch.cuda.get_device_properties(0).total_memory / 1024 / 1024)
    return f"{used} MB / {total} MB VRAM"


# --- Concurrency guard ---
MAX_CONCURRENT = int(os.environ.get("GPU_MAX_CONCURRENT", "2"))
semaphore = asyncio.Semaphore(MAX_CONCURRENT)

# --- Auth ---
API_KEY = os.environ.get("API_KEY")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize service state and warm default models."""
    device = get_device()
    app.state.device = device

    from bert_score import BERTScorer
    from sentence_transformers import SentenceTransformer

    app.state.BERTScorer = BERTScorer
    app.state.SentenceTransformer = SentenceTransformer
    app.state.bertscore_cache = {}
    app.state.embed_cache = {}
    app.state.active_jobs = {}

    logger.info(f"Warming default BERTScore model: {DEFAULT_BERTSCORE_MODEL} ...")
    t0 = time.time()
    app.state.bertscore_cache[DEFAULT_BERTSCORE_MODEL] = BERTScorer(
        model_type=DEFAULT_BERTSCORE_MODEL,
        device=str(device),
        lang="en",
    )
    logger.info(f"BERTScore warm ready ({time.time()-t0:.1f}s) - {_vram_mb()}")

    logger.info(f"Warming default embed model: {DEFAULT_EMBED_MODEL} ...")
    t0 = time.time()
    app.state.embed_cache[DEFAULT_EMBED_MODEL] = SentenceTransformer(DEFAULT_EMBED_MODEL, device=str(device))
    logger.info(f"Embed warm ready ({time.time()-t0:.1f}s) - {_vram_mb()}")

    logger.info("=" * 55)
    logger.info("  OpenClaw GPU Bridge ready!")
    logger.info(f"  Device : {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")
    logger.info(f"  Models : bertscore:{DEFAULT_BERTSCORE_MODEL}, embed:{DEFAULT_EMBED_MODEL}")
    logger.info(f"  VRAM   : {_vram_mb()}")
    logger.info("=" * 55)
    yield


app = FastAPI(title="OpenClaw GPU Bridge Service", version="0.2.0", lifespan=lifespan)


def _loaded_models(request: Request) -> list[str]:
    return [
        *[f"bertscore:{name}" for name in request.app.state.bertscore_cache.keys()],
        *[f"embed:{name}" for name in request.app.state.embed_cache.keys()],
    ]


def _to_iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


async def _get_bertscorer(request: Request, model_type: str):
    cache = request.app.state.bertscore_cache
    if model_type in cache:
        return cache[model_type]

    logger.info(f"[model-load] Loading BERTScore model on-demand: {model_type} - {_vram_mb()}")
    t0 = time.time()
    scorer = await asyncio.to_thread(
        request.app.state.BERTScorer,
        model_type=model_type,
        device=str(request.app.state.device),
        lang="en",
    )
    cache[model_type] = scorer
    logger.info(f"[model-load] BERTScore model ready in {time.time()-t0:.2f}s: {model_type} - {_vram_mb()}")
    return scorer


async def _get_embedder(request: Request, model_name: str):
    cache = request.app.state.embed_cache
    if model_name in cache:
        return cache[model_name]

    logger.info(f"[model-load] Loading embed model on-demand: {model_name} - {_vram_mb()}")
    t0 = time.time()
    embedder = await asyncio.to_thread(
        request.app.state.SentenceTransformer,
        model_name,
        device=str(request.app.state.device),
    )
    cache[model_name] = embedder
    logger.info(f"[model-load] Embed model ready in {time.time()-t0:.2f}s: {model_name} - {_vram_mb()}")
    return embedder


# --- Middleware: API key auth ---
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if API_KEY and request.url.path != "/health":
        key = request.headers.get("X-API-Key")
        if key != API_KEY:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    return await call_next(request)


# --- Endpoints ---

@app.get("/health", response_model=HealthResponse)
async def health(request: Request):
    return HealthResponse(status="ok", device=str(request.app.state.device))


@app.get("/info", response_model=InfoResponse)
async def info(request: Request):
    di = get_device_info(request.app.state.device)
    di["loaded_models"] = _loaded_models(request)
    return InfoResponse(**di)


@app.get("/status", response_model=StatusResponse)
async def status(request: Request):
    in_flight = len(request.app.state.active_jobs)
    queue = QueueStatus(
        max_concurrent=MAX_CONCURRENT,
        in_flight=in_flight,
        available_slots=max(0, MAX_CONCURRENT - in_flight),
        waiting_estimate=max(0, in_flight - MAX_CONCURRENT),
    )
    jobs = [JobStatus(**job) for job in request.app.state.active_jobs.values()]
    return StatusResponse(queue=queue, active_jobs=jobs)


@app.post("/bertscore", response_model=BertScoreResponse)
async def bertscore(req: BertScoreRequest, request: Request):
    if len(req.candidates) != len(req.references):
        raise HTTPException(400, "candidates and references must have equal length")

    try:
        await asyncio.wait_for(semaphore.acquire(), timeout=1.0)
    except asyncio.TimeoutError as exc:
        raise HTTPException(503, "GPU busy - retry later", headers={"Retry-After": "5"}) from exc

    job_id = str(uuid.uuid4())
    request.app.state.active_jobs[job_id] = {
        "id": job_id,
        "type": "bertscore",
        "started_at": _to_iso(time.time()),
        "items": len(req.candidates),
        "model": req.model_type or DEFAULT_BERTSCORE_MODEL,
        "progress": 0.0,
    }

    try:
        scorer = await _get_bertscorer(request, req.model_type or DEFAULT_BERTSCORE_MODEL)
        n = len(req.candidates)
        logger.info(f"[bertscore] job={job_id} start {n} pair(s), model={req.model_type} - {_vram_mb()}")
        t0 = time.time()

        P, R, F1 = await asyncio.to_thread(scorer.score, req.candidates, req.references)
        request.app.state.active_jobs[job_id]["progress"] = 1.0

        elapsed = time.time() - t0
        avg_f1 = sum(F1.tolist()) / len(F1)
        logger.info(f"[bertscore] job={job_id} done in {elapsed:.2f}s - avg F1={avg_f1:.4f} - {_vram_mb()}")

        return BertScoreResponse(
            precision=P.tolist(),
            recall=R.tolist(),
            f1=F1.tolist(),
            model=req.model_type or DEFAULT_BERTSCORE_MODEL,
        )
    finally:
        request.app.state.active_jobs.pop(job_id, None)
        semaphore.release()


@app.post("/embed", response_model=EmbedResponse)
async def embed(req: EmbedRequest, request: Request):
    try:
        await asyncio.wait_for(semaphore.acquire(), timeout=1.0)
    except asyncio.TimeoutError as exc:
        raise HTTPException(503, "GPU busy - retry later", headers={"Retry-After": "5"}) from exc

    job_id = str(uuid.uuid4())
    request.app.state.active_jobs[job_id] = {
        "id": job_id,
        "type": "embed",
        "started_at": _to_iso(time.time()),
        "items": len(req.texts),
        "model": req.model or DEFAULT_EMBED_MODEL,
        "progress": 0.0,
    }

    try:
        embedder = await _get_embedder(request, req.model or DEFAULT_EMBED_MODEL)
        n = len(req.texts)
        logger.info(f"[embed] job={job_id} start {n} text(s), model={req.model} - {_vram_mb()}")
        t0 = time.time()

        batch_size = max(1, int(os.environ.get("GPU_EMBED_BATCH", "32")))
        chunks = [req.texts[i:i + batch_size] for i in range(0, n, batch_size)]
        vectors = []

        for idx, chunk in enumerate(chunks, start=1):
            vecs = await asyncio.to_thread(embedder.encode, chunk, convert_to_numpy=True)
            vectors.append(vecs)
            progress = idx / len(chunks)
            request.app.state.active_jobs[job_id]["progress"] = progress
            logger.info(f"[embed] job={job_id} batch {idx}/{len(chunks)} ({progress*100:.0f}%) - {_vram_mb()}")

        import numpy as np

        merged = np.concatenate(vectors, axis=0) if vectors else np.empty((0, 0))
        elapsed = time.time() - t0
        dims = int(merged.shape[1]) if merged.size else 0

        logger.info(f"[embed] job={job_id} done in {elapsed:.2f}s - {dims}d vectors - {_vram_mb()}")
        return EmbedResponse(
            embeddings=merged.tolist(),
            model=req.model or DEFAULT_EMBED_MODEL,
            dimensions=dims,
        )
    finally:
        request.app.state.active_jobs.pop(job_id, None)
        semaphore.release()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8765)
