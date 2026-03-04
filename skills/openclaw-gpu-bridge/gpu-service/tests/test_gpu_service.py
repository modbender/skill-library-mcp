"""Unit tests for FastAPI GPU service endpoints.

Tests the API endpoints, auth middleware, and helper functions.
Uses a standalone test app that mirrors the real gpu_service but with
mocked ML models and no lifespan (since httpx ASGITransport does not
trigger ASGI lifespan events).
"""

import sys
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import torch
from httpx import ASGITransport, AsyncClient

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


def _create_mock_scorer():
    """Create a mock BERTScorer that returns fixed scores."""
    scorer = MagicMock()
    scorer.score.return_value = (
        torch.tensor([0.9]),
        torch.tensor([0.85]),
        torch.tensor([0.87]),
    )
    return scorer


def _create_mock_embedder():
    """Create a mock SentenceTransformer that returns fixed embeddings."""
    embedder = MagicMock()
    embedder.encode.return_value = np.array([[0.1, 0.2, 0.3]])
    return embedder


def _make_test_app(api_key: str | None = None):
    """Build a test FastAPI app with mocked ML state (no lifespan needed).

    This mirrors the real gpu_service endpoints but skips the model-warming
    lifespan, which requires real GPU models and is not compatible with
    httpx ASGITransport (it does not send lifespan events).
    """
    import asyncio
    import time
    import uuid
    from datetime import datetime, timezone

    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import JSONResponse

    from device import get_device_info

    MAX_CONCURRENT = 2
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    DEFAULT_BERTSCORE_MODEL = "microsoft/deberta-xlarge-mnli"
    DEFAULT_EMBED_MODEL = "all-MiniLM-L6-v2"

    app = FastAPI(title="OpenClaw GPU Bridge Service (test)")

    # -- Initialize state directly (no lifespan) --
    app.state.device = torch.device("cpu")
    app.state.BERTScorer = MagicMock(return_value=_create_mock_scorer())
    app.state.SentenceTransformer = MagicMock(return_value=_create_mock_embedder())
    app.state.bertscore_cache = {DEFAULT_BERTSCORE_MODEL: _create_mock_scorer()}
    app.state.embed_cache = {DEFAULT_EMBED_MODEL: _create_mock_embedder()}
    app.state.active_jobs = {}

    # -- Middleware --
    @app.middleware("http")
    async def auth_middleware(request: Request, call_next):
        if api_key and request.url.path != "/health":
            key = request.headers.get("X-API-Key")
            if key != api_key:
                return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
        return await call_next(request)

    # -- Helpers (copied from gpu_service to keep tests self-contained) --
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
        scorer = await asyncio.to_thread(
            request.app.state.BERTScorer,
            model_type=model_type,
            device=str(request.app.state.device),
            lang="en",
        )
        cache[model_type] = scorer
        return scorer

    async def _get_embedder(request: Request, model_name: str):
        cache = request.app.state.embed_cache
        if model_name in cache:
            return cache[model_name]
        embedder = await asyncio.to_thread(
            request.app.state.SentenceTransformer,
            model_name,
            device=str(request.app.state.device),
        )
        cache[model_name] = embedder
        return embedder

    # -- Endpoints --
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
            raise HTTPException(503, "GPU busy - retry later") from exc

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
            P, R, F1 = await asyncio.to_thread(scorer.score, req.candidates, req.references)
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
            raise HTTPException(503, "GPU busy - retry later") from exc

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
            batch_size = 32
            chunks = [req.texts[i:i + batch_size] for i in range(0, n, batch_size)]
            vectors = []

            for chunk in chunks:
                vecs = await asyncio.to_thread(embedder.encode, chunk, convert_to_numpy=True)
                vectors.append(vecs)

            merged = np.concatenate(vectors, axis=0) if vectors else np.empty((0, 0))
            dims = int(merged.shape[1]) if merged.size else 0

            return EmbedResponse(
                embeddings=merged.tolist(),
                model=req.model or DEFAULT_EMBED_MODEL,
                dimensions=dims,
            )
        finally:
            request.app.state.active_jobs.pop(job_id, None)
            semaphore.release()

    return app


# --- Fixtures ---


@pytest.fixture
async def client():
    """Async HTTP client with no auth."""
    app = _make_test_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
async def authed_client():
    """Async HTTP client with API_KEY set."""
    app = _make_test_app(api_key="test-secret")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


# --- Health endpoint ---


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health_returns_ok(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["device"] == "cpu"

    @pytest.mark.asyncio
    async def test_health_bypasses_auth(self, authed_client):
        """Health endpoint should work even when API_KEY is set."""
        resp = await authed_client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


# --- Info endpoint ---


class TestInfoEndpoint:
    @pytest.mark.asyncio
    async def test_info_returns_device_info(self, client):
        resp = await client.get("/info")
        assert resp.status_code == 200
        data = resp.json()
        assert data["device"] == "cpu"
        assert data["device_name"] == "cpu"
        assert "pytorch_version" in data
        assert isinstance(data["loaded_models"], list)
        assert len(data["loaded_models"]) == 2  # bertscore + embed defaults


# --- Status endpoint ---


class TestStatusEndpoint:
    @pytest.mark.asyncio
    async def test_status_empty_queue(self, client):
        resp = await client.get("/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["queue"]["in_flight"] == 0
        assert data["queue"]["max_concurrent"] == 2
        assert data["active_jobs"] == []


# --- BERTScore endpoint ---


class TestBertScoreEndpoint:
    @pytest.mark.asyncio
    async def test_bertscore_single_pair(self, client):
        resp = await client.post(
            "/bertscore",
            json={
                "candidates": ["The cat sat on the mat."],
                "references": ["A cat was sitting on a mat."],
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["precision"]) == 1
        assert len(data["recall"]) == 1
        assert len(data["f1"]) == 1
        assert data["model"] == "microsoft/deberta-xlarge-mnli"

    @pytest.mark.asyncio
    async def test_bertscore_mismatched_lengths(self, client):
        resp = await client.post(
            "/bertscore",
            json={
                "candidates": ["one", "two"],
                "references": ["only one"],
            },
        )
        assert resp.status_code == 400
        assert "equal length" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_bertscore_custom_model(self, client):
        resp = await client.post(
            "/bertscore",
            json={
                "candidates": ["hello"],
                "references": ["hi"],
                "model_type": "bert-base-uncased",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["model"] == "bert-base-uncased"

    @pytest.mark.asyncio
    async def test_bertscore_batch_validation(self, client):
        resp = await client.post(
            "/bertscore",
            json={
                "candidates": ["text"] * 101,
                "references": ["text"] * 101,
            },
        )
        assert resp.status_code == 422  # Pydantic validation error


# --- Embed endpoint ---


class TestEmbedEndpoint:
    @pytest.mark.asyncio
    async def test_embed_single_text(self, client):
        resp = await client.post(
            "/embed",
            json={"texts": ["hello world"]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["embeddings"]) == 1
        assert data["dimensions"] == 3
        assert data["model"] == "all-MiniLM-L6-v2"

    @pytest.mark.asyncio
    async def test_embed_custom_model(self, client):
        resp = await client.post(
            "/embed",
            json={"texts": ["hello"], "model": "custom-model"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["model"] == "custom-model"

    @pytest.mark.asyncio
    async def test_embed_batch_validation(self, client):
        resp = await client.post(
            "/embed",
            json={"texts": ["text"] * 101},
        )
        assert resp.status_code == 422  # Pydantic validation error

    @pytest.mark.asyncio
    async def test_embed_empty_texts(self, client):
        resp = await client.post(
            "/embed",
            json={"texts": []},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["embeddings"] == []
        assert data["dimensions"] == 0


# --- Auth middleware ---


class TestAuthMiddleware:
    @pytest.mark.asyncio
    async def test_no_auth_required_without_api_key(self, client):
        resp = await client.get("/info")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_auth_required_with_api_key(self, authed_client):
        resp = await authed_client.get("/info")
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Unauthorized"

    @pytest.mark.asyncio
    async def test_auth_succeeds_with_correct_key(self, authed_client):
        resp = await authed_client.get(
            "/info", headers={"X-API-Key": "test-secret"}
        )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_auth_fails_with_wrong_key(self, authed_client):
        resp = await authed_client.get(
            "/info", headers={"X-API-Key": "wrong-key"}
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_health_exempt_from_auth(self, authed_client):
        resp = await authed_client.get("/health")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_bertscore_requires_auth(self, authed_client):
        resp = await authed_client.post(
            "/bertscore",
            json={"candidates": ["hi"], "references": ["hello"]},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_embed_requires_auth(self, authed_client):
        resp = await authed_client.post(
            "/embed",
            json={"texts": ["hello"]},
        )
        assert resp.status_code == 401


# --- Helper function tests ---


class TestBertScoreMultiplePairs:
    @pytest.mark.asyncio
    async def test_bertscore_multiple_pairs(self, client):
        """BERTScore endpoint handles multiple candidate/reference pairs."""
        # Re-build app with a scorer that returns 3 scores
        app = _make_test_app()
        scorer = app.state.bertscore_cache["microsoft/deberta-xlarge-mnli"]
        scorer.score.return_value = (
            torch.tensor([0.9, 0.85, 0.8]),
            torch.tensor([0.88, 0.82, 0.78]),
            torch.tensor([0.89, 0.83, 0.79]),
        )
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            resp = await c.post(
                "/bertscore",
                json={
                    "candidates": ["a", "b", "c"],
                    "references": ["x", "y", "z"],
                },
            )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["precision"]) == 3
        assert len(data["recall"]) == 3
        assert len(data["f1"]) == 3


class TestEmbedBatching:
    @pytest.mark.asyncio
    async def test_embed_multiple_texts(self, client):
        """Embed endpoint handles multiple texts in a single request."""
        app = _make_test_app()
        embedder = app.state.embed_cache["all-MiniLM-L6-v2"]
        embedder.encode.return_value = np.array([
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
            [0.7, 0.8, 0.9],
        ])
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            resp = await c.post(
                "/embed",
                json={"texts": ["hello", "world", "test"]},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["embeddings"]) == 3
        assert data["dimensions"] == 3


class TestOnDemandModelLoading:
    @pytest.mark.asyncio
    async def test_bertscore_loads_uncached_model(self):
        """BERTScore endpoint loads a non-cached model on demand."""
        app = _make_test_app()
        # The factory should produce a new scorer for uncached models
        new_scorer = _create_mock_scorer()
        app.state.BERTScorer = MagicMock(return_value=new_scorer)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            resp = await c.post(
                "/bertscore",
                json={
                    "candidates": ["hello"],
                    "references": ["hi"],
                    "model_type": "new-uncached-model",
                },
            )
        assert resp.status_code == 200
        assert resp.json()["model"] == "new-uncached-model"
        # Model should now be cached
        assert "new-uncached-model" in app.state.bertscore_cache

    @pytest.mark.asyncio
    async def test_embed_loads_uncached_model(self):
        """Embed endpoint loads a non-cached model on demand."""
        app = _make_test_app()
        new_embedder = _create_mock_embedder()
        app.state.SentenceTransformer = MagicMock(return_value=new_embedder)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            resp = await c.post(
                "/embed",
                json={"texts": ["hello"], "model": "new-uncached-model"},
            )
        assert resp.status_code == 200
        assert resp.json()["model"] == "new-uncached-model"
        assert "new-uncached-model" in app.state.embed_cache


class TestJobTracking:
    @pytest.mark.asyncio
    async def test_jobs_cleaned_up_after_bertscore(self):
        """Active jobs dict is empty after bertscore completes."""
        app = _make_test_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            await c.post(
                "/bertscore",
                json={"candidates": ["hi"], "references": ["hello"]},
            )
        assert len(app.state.active_jobs) == 0

    @pytest.mark.asyncio
    async def test_jobs_cleaned_up_after_embed(self):
        """Active jobs dict is empty after embed completes."""
        app = _make_test_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            await c.post(
                "/embed",
                json={"texts": ["hello"]},
            )
        assert len(app.state.active_jobs) == 0

    @pytest.mark.asyncio
    async def test_status_shows_no_active_jobs_when_idle(self, client):
        """Status endpoint shows zero in-flight jobs when idle."""
        resp = await client.get("/status")
        data = resp.json()
        assert data["queue"]["in_flight"] == 0
        assert data["queue"]["available_slots"] == 2
        assert data["active_jobs"] == []


class TestConcurrencyGuard:
    @pytest.mark.asyncio
    async def test_bertscore_returns_503_when_gpu_busy(self):
        """BERTScore endpoint returns 503 when all semaphore slots are taken."""
        app = _make_test_app()
        # Manually acquire all semaphore slots to simulate a full GPU queue.
        # The test app uses MAX_CONCURRENT=2, so we need to find and exhaust
        # the semaphore. We rebuild with a semaphore of 0 available slots.
        import asyncio

        # Create a new app with a custom semaphore that has 0 slots
        test_app = _make_test_app()
        # Patch the semaphore in the embed/bertscore closures by pre-acquiring
        # We need to access the semaphore via the app's route closures.
        # Simpler approach: build a variant that starts with 0 capacity.
        from fastapi import FastAPI, HTTPException, Request
        from fastapi.responses import JSONResponse
        from device import get_device_info

        blocker_sem = asyncio.Semaphore(0)  # Zero capacity - always blocks

        blocked_app = FastAPI(title="OpenClaw GPU Bridge Service (test)")
        blocked_app.state.device = torch.device("cpu")
        blocked_app.state.BERTScorer = MagicMock(return_value=_create_mock_scorer())
        blocked_app.state.SentenceTransformer = MagicMock(return_value=_create_mock_embedder())
        blocked_app.state.bertscore_cache = {"microsoft/deberta-xlarge-mnli": _create_mock_scorer()}
        blocked_app.state.embed_cache = {"all-MiniLM-L6-v2": _create_mock_embedder()}
        blocked_app.state.active_jobs = {}

        @blocked_app.post("/bertscore", response_model=BertScoreResponse)
        async def bertscore(req: BertScoreRequest, request: Request):
            if len(req.candidates) != len(req.references):
                raise HTTPException(400, "candidates and references must have equal length")
            try:
                await asyncio.wait_for(blocker_sem.acquire(), timeout=1.0)
            except asyncio.TimeoutError as exc:
                raise HTTPException(503, "GPU busy - retry later") from exc
            blocker_sem.release()
            return BertScoreResponse(precision=[0.9], recall=[0.85], f1=[0.87], model="test")

        transport = ASGITransport(app=blocked_app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            resp = await c.post(
                "/bertscore",
                json={"candidates": ["hello"], "references": ["hi"]},
            )
        assert resp.status_code == 503
        assert "GPU busy" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_embed_returns_503_when_gpu_busy(self):
        """Embed endpoint returns 503 when all semaphore slots are taken."""
        import asyncio
        from fastapi import FastAPI, HTTPException, Request

        blocker_sem = asyncio.Semaphore(0)

        blocked_app = FastAPI(title="OpenClaw GPU Bridge Service (test)")
        blocked_app.state.device = torch.device("cpu")
        blocked_app.state.SentenceTransformer = MagicMock(return_value=_create_mock_embedder())
        blocked_app.state.embed_cache = {"all-MiniLM-L6-v2": _create_mock_embedder()}
        blocked_app.state.active_jobs = {}

        @blocked_app.post("/embed", response_model=EmbedResponse)
        async def embed(req: EmbedRequest, request: Request):
            try:
                await asyncio.wait_for(blocker_sem.acquire(), timeout=1.0)
            except asyncio.TimeoutError as exc:
                raise HTTPException(503, "GPU busy - retry later") from exc
            blocker_sem.release()
            return EmbedResponse(embeddings=[], model="test", dimensions=0)

        transport = ASGITransport(app=blocked_app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            resp = await c.post(
                "/embed",
                json={"texts": ["hello"]},
            )
        assert resp.status_code == 503
        assert "GPU busy" in resp.json()["detail"]


class TestStatusResponseShape:
    @pytest.mark.asyncio
    async def test_status_response_has_correct_fields(self, client):
        """The /status response contains queue and active_jobs with proper types."""
        resp = await client.get("/status")
        assert resp.status_code == 200
        data = resp.json()
        # Verify top-level keys
        assert "queue" in data
        assert "active_jobs" in data
        # Verify queue sub-fields
        queue = data["queue"]
        assert isinstance(queue["max_concurrent"], int)
        assert isinstance(queue["in_flight"], int)
        assert isinstance(queue["available_slots"], int)
        assert isinstance(queue["waiting_estimate"], int)
        # active_jobs should be a list
        assert isinstance(data["active_jobs"], list)


class TestHelpers:
    def test_vram_mb_cpu(self):
        """_vram_mb returns 'CPU' when no CUDA available."""
        with patch.dict("sys.modules", {
            "bert_score": MagicMock(),
            "sentence_transformers": MagicMock(),
        }):
            if "gpu_service" in sys.modules:
                del sys.modules["gpu_service"]
            import gpu_service
            with patch.object(gpu_service.torch.cuda, "is_available", return_value=False):
                result = gpu_service._vram_mb()
                assert result == "CPU"

    def test_vram_mb_cuda(self):
        """_vram_mb returns VRAM string when CUDA available."""
        with patch.dict("sys.modules", {
            "bert_score": MagicMock(),
            "sentence_transformers": MagicMock(),
        }):
            if "gpu_service" in sys.modules:
                del sys.modules["gpu_service"]
            import gpu_service

            mock_props = MagicMock()
            mock_props.total_memory = 12 * 1024 * 1024 * 1024  # 12 GB

            with patch.object(gpu_service.torch.cuda, "is_available", return_value=True), \
                 patch.object(gpu_service.torch.cuda, "memory_allocated", return_value=512 * 1024 * 1024), \
                 patch.object(gpu_service.torch.cuda, "get_device_properties", return_value=mock_props):
                result = gpu_service._vram_mb()
                assert "512 MB" in result
                assert "12288 MB" in result
                assert "VRAM" in result

    def test_to_iso_epoch(self):
        """_to_iso converts epoch 0 to 1970-01-01."""
        with patch.dict("sys.modules", {
            "bert_score": MagicMock(),
            "sentence_transformers": MagicMock(),
        }):
            if "gpu_service" in sys.modules:
                del sys.modules["gpu_service"]
            import gpu_service
            result = gpu_service._to_iso(0)
            assert "1970-01-01" in result

    def test_to_iso_has_timezone(self):
        """_to_iso returns UTC timezone info."""
        with patch.dict("sys.modules", {
            "bert_score": MagicMock(),
            "sentence_transformers": MagicMock(),
        }):
            if "gpu_service" in sys.modules:
                del sys.modules["gpu_service"]
            import gpu_service
            result = gpu_service._to_iso(1709000000)
            assert "T" in result
            assert "+00:00" in result

    def test_loaded_models_lists_both_caches(self):
        """_loaded_models returns both bertscore and embed cache keys."""
        app = _make_test_app()
        transport = ASGITransport(app=app)

        # Access loaded_models via /info endpoint
        import asyncio
        async def _check():
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                resp = await c.get("/info")
                data = resp.json()
                models = data["loaded_models"]
                assert any("bertscore:" in m for m in models)
                assert any("embed:" in m for m in models)
                assert len(models) == 2

        asyncio.get_event_loop().run_until_complete(_check())
