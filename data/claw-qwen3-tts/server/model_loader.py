"""
model_loader.py — Download and fix Qwen3-TTS models before loading.

Handles the known issue where speech_tokenizer/preprocessor_config.json
is missing from the cached model directory. Pre-downloads all files via
huggingface_hub.snapshot_download, then symlinks the missing configs.
"""

import os
from pathlib import Path
from typing import Optional

import torch


def get_device(override: Optional[str] = None) -> str:
    if override and override != "auto":
        return override
    if torch.cuda.is_available():
        return "cuda:0"
    if hasattr(torch, "xpu") and torch.xpu.is_available():
        return "xpu:0"
    return "cpu"


def get_attn_impl() -> str:
    try:
        import flash_attn
        return "flash_attention_2"
    except ImportError:
        return "sdpa"


def download_and_fix_model(model_id: str, cache_dir: Optional[str] = None) -> str:
    """
    Download a Qwen3-TTS model and fix the speech_tokenizer directory structure.

    Returns the local path to the fixed model directory.
    """
    from huggingface_hub import snapshot_download

    print(f"[INFO] Downloading model {model_id}...")

    kwargs = {}
    if cache_dir:
        kwargs["cache_dir"] = cache_dir

    local_dir = snapshot_download(model_id, **kwargs)
    print(f"[OK]   Model downloaded to {local_dir}")

    # Fix: ensure speech_tokenizer has preprocessor_config.json
    speech_tokenizer_dir = Path(local_dir) / "speech_tokenizer"
    if speech_tokenizer_dir.is_dir():
        _fix_speech_tokenizer(local_dir, speech_tokenizer_dir)

    return local_dir


def _fix_speech_tokenizer(model_dir: str, speech_tokenizer_dir: Path):
    """
    Fix the known issue where preprocessor_config.json and config.json
    are missing from the speech_tokenizer subfolder.
    """
    model_path = Path(model_dir)

    for filename in ["preprocessor_config.json", "config.json"]:
        target = speech_tokenizer_dir / filename
        source = model_path / filename

        if target.exists():
            continue  # Already present, nothing to do

        if source.exists():
            try:
                os.symlink(source, target)
                print(f"[FIX]  Symlinked {filename} → speech_tokenizer/{filename}")
            except OSError:
                # Symlinks may fail on some filesystems, copy instead
                import shutil
                shutil.copy2(source, target)
                print(f"[FIX]  Copied {filename} → speech_tokenizer/{filename}")
        else:
            print(f"[WARN] {filename} not found in model root either — skipping")


def load_model(model_id: str, cache_dir: Optional[str] = None, device: str = "auto"):
    """
    Download (if needed), fix, and load a Qwen3-TTS model.

    Returns a ready-to-use Qwen3TTSModel instance.
    """
    from qwen_tts import Qwen3TTSModel

    # Step 1: Download and fix directory structure
    local_path = download_and_fix_model(model_id, cache_dir)

    # Step 2: Load from local fixed path
    resolved_device = get_device(device)
    attn_impl = get_attn_impl()

    print(f"[INFO] Loading model from {local_path} on {resolved_device} with {attn_impl}")

    model = Qwen3TTSModel.from_pretrained(
        local_path,
        device_map=resolved_device,
        dtype=torch.bfloat16,
        attn_implementation=attn_impl,
    )

    print(f"[OK]   Model loaded successfully")
    return model
