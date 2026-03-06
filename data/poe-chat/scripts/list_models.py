from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import requests


MODEL_LIST_URL = "https://api.poe.com/v1/models"
MODEL_CACHE_TTL_SECONDS = 60 * 60


@dataclass
class ModelInfo:
    model_id: str
    description: str


_cached_models: List[ModelInfo] = []
_cached_at: float = 0.0


def _build_headers(api_key: Optional[str]) -> dict:
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _parse_models_payload(payload: dict) -> List[ModelInfo]:
    data = payload.get("data", [])
    models: List[ModelInfo] = []
    for item in data:
        model_id = item.get("id")
        if not model_id:
            continue
        description = item.get("description") or ""
        models.append(ModelInfo(model_id=model_id, description=description))
    return models


def _fetch_models_from_api(api_key: Optional[str]) -> List[ModelInfo]:
    response = requests.get(
        MODEL_LIST_URL,
        headers=_build_headers(api_key),
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    return _parse_models_payload(payload)


def _is_fresh(path: Path) -> bool:
    if not path.exists():
        return False
    age = time.time() - path.stat().st_mtime
    return age < MODEL_CACHE_TTL_SECONDS


def _load_cached(path: Path) -> Optional[List[ModelInfo]]:
    if not _is_fresh(path):
        return None
    return load_models_from_file(path)


def get_models(api_key: Optional[str] = None, cache_file: Optional[Path] = None) -> List[ModelInfo]:
    global _cached_models, _cached_at
    now = time.time()
    if _cached_models and (now - _cached_at) < MODEL_CACHE_TTL_SECONDS:
        return _cached_models

    if cache_file:
        cached = _load_cached(cache_file)
        if cached:
            _cached_models = cached
            _cached_at = now
            return _cached_models

    _cached_models = _fetch_models_from_api(api_key)
    _cached_at = now
    return _cached_models


def load_models_from_file(path: str | Path) -> List[ModelInfo]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return _parse_models_payload(payload)


def _build_output(models: List[ModelInfo], full: bool) -> dict:
    if full:
        return {"data": [model.__dict__ for model in models]}
    return {"data": [{"id": model.model_id} for model in models]}


def main() -> int:
    parser = argparse.ArgumentParser(description="List Poe models")
    parser.add_argument(
        "--out",
        default="models.json",
        help="Output file path to save models JSON (default: models.json)",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Output full model details (id + description)",
    )
    args = parser.parse_args()

    api_key = os.getenv("POE_API_KEY")
    out_path = Path(args.out)
    models = get_models(api_key, cache_file=out_path)
    output = _build_output(models, args.full)
    payload = json.dumps(output, ensure_ascii=False, indent=2)

    out_path.write_text(payload, encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
