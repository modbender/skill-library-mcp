"""Unit tests for Pydantic request/response models."""

import pytest
from pydantic import ValidationError

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


# --- BertScoreRequest ---


class TestBertScoreRequest:
    def test_valid_request(self):
        req = BertScoreRequest(
            candidates=["The cat sat on the mat."],
            references=["A cat was sitting on the mat."],
        )
        assert len(req.candidates) == 1
        assert len(req.references) == 1
        assert req.lang == "en"
        assert req.model_type == "microsoft/deberta-xlarge-mnli"

    def test_custom_model_and_lang(self):
        req = BertScoreRequest(
            candidates=["hello"],
            references=["hi"],
            lang="de",
            model_type="bert-base-uncased",
        )
        assert req.lang == "de"
        assert req.model_type == "bert-base-uncased"

    def test_multiple_pairs(self):
        req = BertScoreRequest(
            candidates=["a", "b", "c"],
            references=["x", "y", "z"],
        )
        assert len(req.candidates) == 3
        assert len(req.references) == 3

    def test_batch_size_exceeds_max(self):
        over_limit = ["text"] * 101
        with pytest.raises(ValidationError, match="exceeds max batch size"):
            BertScoreRequest(candidates=over_limit, references=over_limit)

    def test_text_length_exceeds_max(self):
        long_text = "x" * 10001
        with pytest.raises(ValidationError, match="exceeds max text length"):
            BertScoreRequest(candidates=[long_text], references=["short"])

    def test_reference_text_length_exceeds_max(self):
        long_text = "x" * 10001
        with pytest.raises(ValidationError, match="exceeds max text length"):
            BertScoreRequest(candidates=["short"], references=[long_text])

    def test_empty_lists_allowed(self):
        req = BertScoreRequest(candidates=[], references=[])
        assert req.candidates == []
        assert req.references == []


# --- BertScoreResponse ---


class TestBertScoreResponse:
    def test_valid_response(self):
        resp = BertScoreResponse(
            precision=[0.9, 0.8],
            recall=[0.85, 0.75],
            f1=[0.87, 0.77],
            model="microsoft/deberta-xlarge-mnli",
        )
        assert len(resp.precision) == 2
        assert resp.model == "microsoft/deberta-xlarge-mnli"


# --- EmbedRequest ---


class TestEmbedRequest:
    def test_valid_request(self):
        req = EmbedRequest(texts=["hello world", "test text"])
        assert len(req.texts) == 2
        assert req.model == "all-MiniLM-L6-v2"

    def test_custom_model(self):
        req = EmbedRequest(texts=["hello"], model="custom-model")
        assert req.model == "custom-model"

    def test_batch_size_exceeds_max(self):
        over_limit = ["text"] * 101
        with pytest.raises(ValidationError, match="exceeds max batch size"):
            EmbedRequest(texts=over_limit)

    def test_text_length_exceeds_max(self):
        long_text = "x" * 10001
        with pytest.raises(ValidationError, match="exceeds max text length"):
            EmbedRequest(texts=[long_text])

    def test_empty_texts_allowed(self):
        req = EmbedRequest(texts=[])
        assert req.texts == []

    def test_at_max_batch_size(self):
        req = EmbedRequest(texts=["text"] * 100)
        assert len(req.texts) == 100

    def test_at_max_text_length(self):
        req = EmbedRequest(texts=["x" * 10000])
        assert len(req.texts[0]) == 10000


# --- EmbedResponse ---


class TestEmbedResponse:
    def test_valid_response(self):
        resp = EmbedResponse(
            embeddings=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
            model="all-MiniLM-L6-v2",
            dimensions=3,
        )
        assert len(resp.embeddings) == 2
        assert resp.dimensions == 3


# --- HealthResponse ---


class TestHealthResponse:
    def test_valid_response(self):
        resp = HealthResponse(status="ok", device="cuda")
        assert resp.status == "ok"
        assert resp.device == "cuda"

    def test_default_status(self):
        resp = HealthResponse(device="cpu")
        assert resp.status == "ok"


# --- InfoResponse ---


class TestInfoResponse:
    def test_gpu_info(self):
        resp = InfoResponse(
            device="cuda",
            device_name="NVIDIA RTX 3060",
            vram_total_mb=12288,
            vram_used_mb=1024,
            pytorch_version="2.6.0",
            cuda_version="12.4",
            loaded_models=["bertscore:microsoft/deberta-xlarge-mnli"],
        )
        assert resp.vram_total_mb == 12288
        assert len(resp.loaded_models) == 1

    def test_cpu_info(self):
        resp = InfoResponse(
            device="cpu",
            device_name="cpu",
            pytorch_version="2.6.0",
        )
        assert resp.vram_total_mb is None
        assert resp.cuda_version is None
        assert resp.loaded_models == []


# --- QueueStatus ---


class TestQueueStatus:
    def test_valid_queue(self):
        q = QueueStatus(
            max_concurrent=2,
            in_flight=1,
            available_slots=1,
            waiting_estimate=0,
        )
        assert q.max_concurrent == 2
        assert q.available_slots == 1


# --- JobStatus ---


class TestJobStatus:
    def test_valid_job(self):
        j = JobStatus(
            id="abc-123",
            type="bertscore",
            started_at="2026-02-27T00:00:00+00:00",
            items=5,
            model="microsoft/deberta-xlarge-mnli",
            progress=0.5,
        )
        assert j.type == "bertscore"
        assert j.progress == 0.5


# --- StatusResponse ---


class TestStatusResponse:
    def test_valid_status(self):
        resp = StatusResponse(
            queue=QueueStatus(
                max_concurrent=2,
                in_flight=0,
                available_slots=2,
                waiting_estimate=0,
            ),
            active_jobs=[],
        )
        assert resp.queue.in_flight == 0
        assert resp.active_jobs == []
