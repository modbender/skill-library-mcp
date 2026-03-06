"""Pydantic request/response models."""

from pydantic import BaseModel, Field, field_validator
import os

MAX_BATCH_SIZE = int(os.environ.get("GPU_MAX_BATCH_SIZE", "100"))
MAX_TEXT_LENGTH = int(os.environ.get("GPU_MAX_TEXT_LENGTH", "10000"))


class BertScoreRequest(BaseModel):
    candidates: list[str]
    references: list[str]
    lang: str = "en"
    model_type: str = "microsoft/deberta-xlarge-mnli"

    @field_validator("candidates", "references")
    @classmethod
    def validate_batch_size(cls, v: list[str], info) -> list[str]:
        if len(v) > MAX_BATCH_SIZE:
            raise ValueError(
                f"{info.field_name} array length {len(v)} exceeds max batch size of {MAX_BATCH_SIZE}"
            )
        for i, text in enumerate(v):
            if len(text) > MAX_TEXT_LENGTH:
                raise ValueError(
                    f"{info.field_name}[{i}] length {len(text)} exceeds max text length of {MAX_TEXT_LENGTH}"
                )
        return v


class BertScoreResponse(BaseModel):
    precision: list[float]
    recall: list[float]
    f1: list[float]
    model: str


class EmbedRequest(BaseModel):
    texts: list[str]
    model: str = "all-MiniLM-L6-v2"

    @field_validator("texts")
    @classmethod
    def validate_texts(cls, v: list[str]) -> list[str]:
        if len(v) > MAX_BATCH_SIZE:
            raise ValueError(
                f"texts array length {len(v)} exceeds max batch size of {MAX_BATCH_SIZE}"
            )
        for i, text in enumerate(v):
            if len(text) > MAX_TEXT_LENGTH:
                raise ValueError(
                    f"texts[{i}] length {len(text)} exceeds max text length of {MAX_TEXT_LENGTH}"
                )
        return v


class EmbedResponse(BaseModel):
    embeddings: list[list[float]]
    model: str
    dimensions: int


class HealthResponse(BaseModel):
    status: str = "ok"
    device: str


class InfoResponse(BaseModel):
    device: str
    device_name: str
    vram_total_mb: int | None = None
    vram_used_mb: int | None = None
    pytorch_version: str
    cuda_version: str | None = None
    loaded_models: list[str] = Field(default_factory=list)


class QueueStatus(BaseModel):
    max_concurrent: int
    in_flight: int
    available_slots: int
    waiting_estimate: int


class JobStatus(BaseModel):
    id: str
    type: str
    started_at: str
    items: int
    model: str
    progress: float


class StatusResponse(BaseModel):
    queue: QueueStatus
    active_jobs: list[JobStatus] = Field(default_factory=list)
