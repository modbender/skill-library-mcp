#!/usr/bin/env python3
"""
Qwen3-TTS Local Inference — Model Downloader

Downloads model weights to a local directory for offline / faster inference.

Usage:
    python download_models.py                     # download active model set (small by default)
    python download_models.py --size small         # download 0.6B models
    python download_models.py --size large         # download 1.7B models
    python download_models.py --size all           # download both small and large models
    python download_models.py --model-dir ./models # custom download location
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, Path(__file__).resolve().parent.as_posix())

from config import LARGE_MODELS, MODEL_DIR, SMALL_MODELS, TOKENIZER_ID

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)-24s  %(levelname)-5s  %(message)s",
)
logger = logging.getLogger("qwen3-tts.download")


def download_model(model_id: str, dest_dir: Path) -> bool:
    """Download a single model from HuggingFace Hub to *dest_dir*."""
    from huggingface_hub import snapshot_download

    local_name = model_id.replace("/", "--")
    local_path = dest_dir / local_name

    if local_path.is_dir() and any(local_path.iterdir()):
        logger.info("Already present: %s  ->  %s", model_id, local_path)
        return True

    logger.info("Downloading %s  ->  %s ...", model_id, local_path)
    try:
        snapshot_download(
            model_id,
            local_dir=str(local_path),
        )
        logger.info("  OK: %s", model_id)
        return True
    except Exception as exc:
        logger.error("  FAILED %s: %s", model_id, exc)
        return False


def download_set(label: str, variants: dict[str, str], dest_dir: Path) -> int:
    """Download all variants in a set. Returns count of failures."""
    logger.info("=== Downloading %s models ===", label)
    failures = 0
    seen_ids: set[str] = set()
    for variant, model_id in variants.items():
        if model_id in seen_ids:
            continue
        seen_ids.add(model_id)
        if not download_model(model_id, dest_dir):
            failures += 1
    return failures


def main() -> None:
    parser = argparse.ArgumentParser(description="Download Qwen3-TTS model weights")
    parser.add_argument(
        "--size",
        choices=["small", "large", "all"],
        default=None,
        help="Which model set to download (default: active set from QWEN_TTS_MODEL_SIZE)",
    )
    parser.add_argument(
        "--model-dir",
        default=None,
        help=f"Download destination (default: {MODEL_DIR})",
    )
    args = parser.parse_args()

    dest = Path(args.model_dir or MODEL_DIR)
    dest.mkdir(parents=True, exist_ok=True)
    logger.info("Model directory: %s", dest)

    failures = 0

    if args.size == "all":
        failures += download_set("small (0.6B)", SMALL_MODELS, dest)
        failures += download_set("large (1.7B)", LARGE_MODELS, dest)
    elif args.size == "large":
        failures += download_set("large (1.7B)", LARGE_MODELS, dest)
    elif args.size == "small":
        failures += download_set("small (0.6B)", SMALL_MODELS, dest)
    else:
        from config import MODEL_SIZE_LABEL, MODEL_VARIANTS
        failures += download_set(MODEL_SIZE_LABEL, MODEL_VARIANTS, dest)

    logger.info("--- Downloading tokenizer ---")
    if not download_model(TOKENIZER_ID, dest):
        failures += 1

    if failures:
        logger.error("%d download(s) failed.", failures)
        sys.exit(1)
    else:
        logger.info("All downloads complete.")


if __name__ == "__main__":
    main()
