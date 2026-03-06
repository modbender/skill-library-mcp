"""
voice_designer.py — Create new voices from natural language descriptions.

Uses Qwen3-TTS-12Hz-1.7B-VoiceDesign model to generate speech with
a voice matching the given description.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional

import torch
import soundfile as sf


class VoiceDesigner:
    """
    Generates speech using a natural language voice description.

    The voice-design model takes a text description (instruct) of the desired voice
    and produces speech in that style.
    """

    def __init__(self, model_id: str = "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
                 cache_dir: Optional[str] = None, device: str = "auto"):
        self.model_id = model_id
        self.cache_dir = cache_dir
        self.device = self._resolve_device(device)
        self._model = None
        self._loaded = False

    def _resolve_device(self, device: str) -> str:
        if device != "auto":
            return device
        if torch.cuda.is_available():
            return "cuda:0"
        if hasattr(torch, "xpu") and torch.xpu.is_available():
            return "xpu:0"
        return "cpu"

    def _get_attn_impl(self) -> str:
        """Choose attention implementation based on flash-attn availability."""
        try:
            import flash_attn
            return "flash_attention_2"
        except ImportError:
            return "sdpa"

    def _ensure_loaded(self):
        """Lazy-load the model on first use."""
        if self._loaded:
            return

        try:
            from model_loader import load_model

            print(f"[INFO] Loading VoiceDesign model on {self.device}")
            self._model = load_model(
                self.model_id, cache_dir=self.cache_dir, device=self.device
            )
            self._loaded = True
            print("[OK] VoiceDesign model loaded")

        except ImportError:
            raise RuntimeError(
                "qwen-tts package not installed. Run: pip install qwen-tts"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load voice design model: {e}")

    def generate(
        self,
        text: str,
        voice_description: str,
        language: str = "English",
        output_path: Optional[str] = None,
    ) -> dict:
        """
        Generate speech with a designed voice.

        Args:
            text: The text to synthesize
            voice_description: Natural language description of the desired voice (instruct)
            language: Target language (e.g. "English", "Chinese", "German")
            output_path: Where to save the audio. If None, uses a temp file.

        Returns:
            dict with keys:
                - audio_path: Path to the generated audio file
                - voice_id: Temporary voice ID for saving
                - sample_rate: Audio sample rate
                - ref_text: The text that was synthesized (for clone prompt reuse)
        """
        self._ensure_loaded()

        if output_path is None:
            fd, output_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)

        try:
            wavs, sr = self._model.generate_voice_design(
                text=text,
                language=language,
                instruct=voice_description,
            )

            audio = wavs[0]
            sf.write(output_path, audio, sr)

            voice_id = f"vd_{hash(voice_description) & 0xFFFFFFFF:08x}"

            return {
                "audio_path": output_path,
                "audio_data": audio,
                "voice_id": voice_id,
                "sample_rate": sr,
                "ref_text": text,
            }

        except Exception as e:
            raise RuntimeError(f"Voice design generation failed: {e}")

    def unload(self):
        """Unload the model to free memory."""
        if self._model is not None:
            del self._model
            self._model = None
            self._loaded = False
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
