"""
Qwen3-TTS Local Inference — Core Engine

Standalone TTS inference without a server. Manages lazy model loading so only
one model variant is resident in memory at a time.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import soundfile as sf
import torch

from config import DEVICE, DTYPE, MODEL_DIR, MODEL_VARIANTS, OUTPUT_DIR

logger = logging.getLogger("qwen3-tts.inference")

_DTYPE_MAP = {
    "float32": torch.float32,
    "float16": torch.float16,
    "bfloat16": torch.bfloat16,
}


def _resolve_dtype() -> torch.dtype:
    return _DTYPE_MAP.get(DTYPE, torch.float32)


class TTSInferenceEngine:
    """Direct Qwen3-TTS inference — no server required."""

    def __init__(self, model_dir: str | None = None, output_dir: str | None = None) -> None:
        self._model_dir = Path(model_dir or MODEL_DIR)
        self._output_dir = Path(output_dir or OUTPUT_DIR)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._model = None
        self._current_variant: Optional[str] = None

    # ── model lifecycle ───────────────────────────────────────────────────

    def _local_model_path(self, variant: str) -> Path | None:
        """Return the local model path if weights exist on disk."""
        model_id = MODEL_VARIANTS[variant]
        local_dir = self._model_dir / model_id.replace("/", "--")
        if local_dir.is_dir() and any(local_dir.iterdir()):
            return local_dir
        return None

    def _load_model(self, variant: str) -> None:
        from qwen_tts import Qwen3TTSModel

        if self._current_variant == variant and self._model is not None:
            return

        self._unload_model()

        model_id = MODEL_VARIANTS[variant]
        local_path = self._local_model_path(variant)

        load_source = str(local_path) if local_path else model_id
        logger.info(
            "Loading '%s' from %s on %s [%s] ...",
            variant,
            "local cache" if local_path else "HuggingFace Hub",
            DEVICE,
            DTYPE,
        )

        load_kwargs: dict = {
            "device_map": DEVICE,
            "dtype": _resolve_dtype(),
        }
        if DEVICE.startswith("cuda") and DTYPE in ("float16", "bfloat16"):
            load_kwargs["attn_implementation"] = "flash_attention_2"

        start = time.time()
        self._model = Qwen3TTSModel.from_pretrained(load_source, **load_kwargs)
        elapsed = time.time() - start
        logger.info("Model loaded in %.1fs", elapsed)
        self._current_variant = variant

    def _unload_model(self) -> None:
        if self._model is not None:
            logger.info("Unloading '%s'", self._current_variant)
            del self._model
            self._model = None
            self._current_variant = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            import gc
            gc.collect()

    # ── output helpers ────────────────────────────────────────────────────

    def _wav_path(self, prefix: str) -> str:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return str(self._output_dir / f"{prefix}_{ts}.wav")

    @staticmethod
    def _save_wav(wav_data, sample_rate: int, path: str) -> None:
        sf.write(path, wav_data, sample_rate)
        logger.info("Saved %s", path)

    # ── public generation methods ─────────────────────────────────────────

    def generate_custom_voice(
        self,
        text: str,
        language: str = "Auto",
        speaker: str = "Ryan",
        instruct: str = "",
    ) -> dict:
        """Generate speech with a built-in speaker voice."""
        self._load_model("custom-voice")

        kwargs: dict = {"text": text, "language": language, "speaker": speaker}
        if instruct:
            kwargs["instruct"] = instruct

        start = time.time()
        wavs, sr = self._model.generate_custom_voice(**kwargs)
        elapsed = time.time() - start

        out_path = self._wav_path("custom_voice")
        self._save_wav(wavs[0], sr, out_path)
        duration_s = round(len(wavs[0]) / sr, 2)
        return {"file": out_path, "duration_s": duration_s, "inference_s": round(elapsed, 2)}

    def generate_voice_design(
        self,
        text: str,
        language: str = "Auto",
        instruct: str = "",
    ) -> dict:
        """Generate speech with a voice described in natural language."""
        self._load_model("voice-design")

        start = time.time()
        wavs, sr = self._model.generate_voice_design(
            text=text, language=language, instruct=instruct,
        )
        elapsed = time.time() - start

        out_path = self._wav_path("voice_design")
        self._save_wav(wavs[0], sr, out_path)
        duration_s = round(len(wavs[0]) / sr, 2)
        return {"file": out_path, "duration_s": duration_s, "inference_s": round(elapsed, 2)}

    def generate_voice_clone(
        self,
        text: str,
        language: str = "Auto",
        ref_audio: str = "",
        ref_text: str = "",
    ) -> dict:
        """Clone a voice from reference audio and synthesise new text."""
        self._load_model("voice-clone")

        start = time.time()
        wavs, sr = self._model.generate_voice_clone(
            text=text, language=language, ref_audio=ref_audio, ref_text=ref_text,
        )
        elapsed = time.time() - start

        out_path = self._wav_path("voice_clone")
        self._save_wav(wavs[0], sr, out_path)
        duration_s = round(len(wavs[0]) / sr, 2)
        return {"file": out_path, "duration_s": duration_s, "inference_s": round(elapsed, 2)}

    def status(self) -> dict:
        return {
            "loaded_variant": self._current_variant,
            "device": DEVICE,
            "dtype": DTYPE,
            "model_dir": str(self._model_dir),
            "output_dir": str(self._output_dir),
            "model_variants": MODEL_VARIANTS,
        }
