"""GPU detection and device selection."""

import logging
import os
import torch

logger = logging.getLogger("gpu-service")


def get_device() -> torch.device:
    """Auto-detect GPU or fall back to CPU. Supports CUDA (NVIDIA) and ROCm (AMD)."""
    override = os.environ.get("TORCH_DEVICE")
    if override:
        logger.info(f"Device override via TORCH_DEVICE={override}")
        return torch.device(override)

    if torch.cuda.is_available():
        name = torch.cuda.get_device_name(0)
        logger.info(f"GPU detected: {name}")
        return torch.device("cuda")

    logger.warning("No GPU detected - falling back to CPU (inference will be slow)")
    return torch.device("cpu")


def get_device_info(device: torch.device) -> dict:
    """Return device diagnostics."""
    info = {
        "device": str(device),
        "pytorch_version": torch.__version__,
        "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
    }
    if device.type == "cuda":
        info["device_name"] = torch.cuda.get_device_name(0)
        mem = torch.cuda.get_device_properties(0).total_memory
        info["vram_total_mb"] = round(mem / 1024 / 1024)
        info["vram_used_mb"] = round(torch.cuda.memory_allocated(0) / 1024 / 1024)
    else:
        info["device_name"] = "cpu"
    return info
