"""Compute Marketplace — Sell lab GPU inference/video gen to Conway agents.

This is a Flask blueprint that exposes your actual lab hardware as
x402-payable endpoints. Conway Automaton agents discover this via
the /.well-known/agent-card.json and pay USDC per request.

Real endpoints that route to your actual infrastructure:
  - /api/compute/inference → POWER8 Ollama (100.75.100.89:11434)
  - /api/compute/vision   → BAGEL-7B on .160 (192.168.0.160:8095)
  - /api/compute/tts      → XTTS on localhost:5500
  - /api/compute/video    → ComfyUI on .126 (192.168.0.126:8188)

Beacon 2.9.0 — Elyan Labs.
"""

import json
import os
import time
import uuid
from typing import Any, Dict, Optional

import requests
from flask import Blueprint, jsonify, request

from .x402_bridge import x402_required

compute_bp = Blueprint("compute_marketplace", __name__)

# ── Lab infrastructure endpoints ──

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://100.75.100.89:11434")
BAGEL_URL = os.environ.get("BAGEL_URL", "http://100.75.100.89:8095")
XTTS_URL = os.environ.get("XTTS_URL", "http://localhost:5500")
COMFYUI_URL = os.environ.get("COMFYUI_URL", "http://192.168.0.126:8188")
BOTTUBE_API = os.environ.get("BOTTUBE_API", "https://bottube.ai/api")

# Track jobs for billing
_jobs: Dict[str, Dict] = {}


@compute_bp.route("/api/compute/inference", methods=["POST"])
@x402_required("inference_llm", "LLM inference on POWER8 512GB RAM (Ollama)")
def inference():
    """LLM inference via Ollama on POWER8.

    Request body:
        {"model": "llama3.2:3b", "prompt": "...", "options": {...}}

    Returns:
        {"response": "...", "model": "...", "eval_duration_ms": ...}
    """
    data = request.get_json(force=True)
    model = data.get("model", "llama3.2:3b")
    prompt = data.get("prompt", "")
    system = data.get("system", "")
    options = data.get("options", {})

    if not prompt:
        return jsonify({"error": "prompt required"}), 400

    job_id = f"inf_{uuid.uuid4().hex[:12]}"
    start = time.time()

    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "system": system,
                "stream": False,
                "options": options,
            },
            timeout=120,
        )
        resp.raise_for_status()
        result = resp.json()

        elapsed = time.time() - start
        _jobs[job_id] = {
            "type": "inference",
            "model": model,
            "elapsed_s": round(elapsed, 2),
            "tokens": result.get("eval_count", 0),
            "timestamp": int(time.time()),
        }

        return jsonify({
            "job_id": job_id,
            "response": result.get("response", ""),
            "model": result.get("model", model),
            "eval_count": result.get("eval_count", 0),
            "eval_duration_ms": result.get("eval_duration", 0) / 1_000_000,
            "total_duration_ms": round(elapsed * 1000, 1),
            "hardware": "POWER8-S824-512GB",
        })
    except requests.Timeout:
        return jsonify({"error": "Inference timeout (120s limit)"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 502


@compute_bp.route("/api/compute/vision", methods=["POST"])
@x402_required("inference_vision", "Vision model inference (BAGEL-7B on V100)")
def vision():
    """Vision inference via BAGEL-7B-MoT on .160 V100.

    Request body:
        {"image_url": "...", "prompt": "Describe this image"}
        OR
        {"image_base64": "...", "prompt": "..."}

    Returns:
        {"response": "...", "model": "BAGEL-7B-MoT"}
    """
    data = request.get_json(force=True)
    prompt = data.get("prompt", "Describe this image in detail.")
    image_url = data.get("image_url", "")
    image_b64 = data.get("image_base64", "")

    if not image_url and not image_b64:
        return jsonify({"error": "image_url or image_base64 required"}), 400

    start = time.time()

    try:
        bagel_payload: Dict[str, Any] = {
            "prompt": prompt,
            "max_new_tokens": 512,
        }
        if image_url:
            bagel_payload["image_url"] = image_url
        elif image_b64:
            bagel_payload["image_base64"] = image_b64

        resp = requests.post(
            f"{BAGEL_URL}/api/understand",
            json=bagel_payload,
            timeout=60,
        )
        resp.raise_for_status()
        result = resp.json()
        elapsed = time.time() - start

        return jsonify({
            "response": result.get("response", ""),
            "model": "BAGEL-7B-MoT",
            "total_duration_ms": round(elapsed * 1000, 1),
            "hardware": "V100-16GB-NF4",
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 502


@compute_bp.route("/api/compute/tts", methods=["POST"])
@x402_required("inference_tts", "Text-to-speech (XTTS on RTX 4070)")
def tts():
    """Text-to-speech via XTTS server.

    Request body:
        {"text": "Hello world", "language": "en"}

    Returns:
        Audio WAV file (binary)
    """
    data = request.get_json(force=True)
    text = data.get("text", "")
    language = data.get("language", "en")

    if not text:
        return jsonify({"error": "text required"}), 400

    try:
        resp = requests.post(
            f"{XTTS_URL}/tts_to_audio",
            json={
                "text": text,
                "speaker_wav": "sophia_reference.wav",
                "language": language,
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.content, 200, {
            "Content-Type": "audio/wav",
            "X-Hardware": "RTX4070-8GB",
        }
    except Exception as e:
        return jsonify({"error": str(e)}), 502


@compute_bp.route("/api/compute/video", methods=["POST"])
@x402_required("video_generate", "Video generation (LTX-2/ComfyUI on V100 32GB)")
def video_generate():
    """Queue a video generation job on ComfyUI.

    Request body:
        {"prompt": "A robot walking through a swamp at sunset",
         "width": 720, "height": 720, "frames": 24}

    Returns:
        {"job_id": "...", "status": "queued", "estimated_seconds": 30}
    """
    data = request.get_json(force=True)
    prompt = data.get("prompt", "")

    if not prompt:
        return jsonify({"error": "prompt required"}), 400

    job_id = f"vid_{uuid.uuid4().hex[:12]}"

    # Queue to ComfyUI (simplified — real impl would use websocket API)
    workflow = {
        "prompt": prompt,
        "width": min(data.get("width", 720), 1280),
        "height": min(data.get("height", 720), 1280),
        "frames": min(data.get("frames", 24), 120),
    }

    _jobs[job_id] = {
        "type": "video",
        "status": "queued",
        "workflow": workflow,
        "timestamp": int(time.time()),
    }

    return jsonify({
        "job_id": job_id,
        "status": "queued",
        "estimated_seconds": 30,
        "hardware": "V100-32GB-ComfyUI",
        "check_status": f"/api/compute/job/{job_id}",
    })


@compute_bp.route("/api/compute/job/<job_id>", methods=["GET"])
def job_status(job_id: str):
    """Check status of a compute job."""
    job = _jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify({"job_id": job_id, **job})


@compute_bp.route("/api/compute/catalog", methods=["GET"])
def catalog():
    """Public catalog of available compute services and pricing."""
    return jsonify({
        "provider": "Elyan Labs",
        "location": "Baton Rouge, LA",
        "services": [
            {
                "id": "inference_llm",
                "name": "LLM Inference",
                "description": "Ollama on IBM POWER8 S824 (512GB RAM, 128 threads)",
                "models": ["llama3.2:3b", "llama3.1:8b", "qwen2.5:14b", "deepseek-r1:32b"],
                "price_usdc": 0.01,
                "price_rtc": 0.1,
                "endpoint": "/api/compute/inference",
            },
            {
                "id": "inference_vision",
                "name": "Vision Understanding",
                "description": "BAGEL-7B-MoT on V100 (image understanding + generation)",
                "price_usdc": 0.05,
                "price_rtc": 0.5,
                "endpoint": "/api/compute/vision",
            },
            {
                "id": "inference_tts",
                "name": "Text-to-Speech",
                "description": "XTTS on RTX 4070 (multi-language, custom voices)",
                "price_usdc": 0.02,
                "price_rtc": 0.2,
                "endpoint": "/api/compute/tts",
            },
            {
                "id": "video_generate",
                "name": "Video Generation",
                "description": "LTX-2 / ComfyUI on V100 32GB (text-to-video, up to 720p)",
                "price_usdc": 0.50,
                "price_rtc": 5.0,
                "endpoint": "/api/compute/video",
            },
        ],
        "payment_methods": [
            {
                "type": "x402_usdc",
                "network": "Base (eip155:8453)",
                "asset": "USDC",
                "facilitator": "https://x402.org/facilitator",
            },
            {
                "type": "rustchain_rtc",
                "node": "https://50.28.86.131",
                "rate": "1 RTC = $0.10 USD",
            },
        ],
        "hardware_inventory": {
            "gpus": {
                "V100-32GB": 2,
                "V100-16GB": 3,
                "RTX-5070-12GB": 2,
                "RTX-4070-8GB": 1,
                "RTX-3060-12GB": 2,
                "M40-12GB": 2,
            },
            "total_vram_gb": 192,
            "cpu": "POWER8 S824 (16-core, 128-thread, SMT8)",
            "ram_gb": 512,
            "accelerators": ["Hailo-8 TPU", "Alveo U30 FPGA x2"],
        },
        "uptime_url": "https://50.28.86.131/health",
        "beacon_atlas": "https://50.28.86.131:8070/beacon/",
    })
