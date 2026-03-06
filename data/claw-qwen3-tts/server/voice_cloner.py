"""
voice_cloner.py — Clone voices from reference audio.

Uses Qwen3-TTS-12Hz-1.7B-Base model to clone a voice from a reference
audio clip and generate new speech in that voice.

Supports reusable voice_clone_prompt for efficient multi-generation.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Any

import torch
import soundfile as sf


class VoiceCloner:
    """
    Clones a voice from reference audio and generates new speech in that voice.

    Requirements:
        - Minimum 3 seconds of reference audio
        - Recommended 10-30 seconds for best quality
        - Accurate transcription of reference audio improves results
        - Supports cross-language cloning
    """

    def __init__(
        self,
        model_id: str = "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
        cache_dir: Optional[str] = None,
        device: str = "auto",
    ):
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
        try:
            import flash_attn
            return "flash_attention_2"
        except ImportError:
            return "sdpa"

    def _ensure_loaded(self):
        """Lazy-load model on first use."""
        if self._loaded:
            return

        try:
            from model_loader import load_model

            print(f"[INFO] Loading Base/Clone model on {self.device}")
            self._model = load_model(
                self.model_id, cache_dir=self.cache_dir, device=self.device
            )
            self._loaded = True
            print("[OK] Base/Clone model loaded")

        except ImportError:
            raise RuntimeError(
                "qwen-tts package not installed. Run: pip install qwen-tts"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load voice cloning model: {e}")

    def clone(
        self,
        text: str,
        reference_audio_path: str,
        reference_text: str = "",
        language: str = "English",
        output_path: Optional[str] = None,
    ) -> dict:
        """
        Clone a voice from reference audio and generate new speech.

        Args:
            text: The new text to synthesize in the cloned voice
            reference_audio_path: Path to the reference audio file
            reference_text: Transcription of the reference audio (recommended)
            language: Target language (e.g. "English", "Chinese", "German")
            output_path: Where to save the output. If None, uses a temp file.

        Returns:
            dict with keys:
                - audio_path: Path to the generated audio
                - voice_id: Temporary voice ID for saving
                - voice_clone_prompt: Reusable prompt object for future generations
                - sample_rate: Audio sample rate
        """
        self._ensure_loaded()

        if not os.path.exists(reference_audio_path):
            raise FileNotFoundError(
                f"Reference audio not found: {reference_audio_path}"
            )

        if output_path is None:
            fd, output_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)

        try:
            # Build a reusable clone prompt
            voice_clone_prompt = self._model.create_voice_clone_prompt(
                ref_audio=reference_audio_path,
                ref_text=reference_text if reference_text else None,
                x_vector_only_mode=not bool(reference_text),
            )

            # Generate cloned speech
            wavs, sr = self._model.generate_voice_clone(
                text=text,
                language=language,
                voice_clone_prompt=voice_clone_prompt,
            )

            audio = wavs[0]
            sf.write(output_path, audio, sr)

            voice_id = f"vc_{hash(reference_audio_path) & 0xFFFFFFFF:08x}"

            return {
                "audio_path": output_path,
                "voice_id": voice_id,
                "voice_clone_prompt": voice_clone_prompt,
                "sample_rate": sr,
            }

        except Exception as e:
            raise RuntimeError(f"Voice cloning failed: {e}")

    def clone_from_prompt(
        self,
        text: str,
        voice_clone_prompt: Any,
        language: str = "English",
        output_path: Optional[str] = None,
    ) -> dict:
        """
        Generate speech using a pre-built voice_clone_prompt.

        This is more efficient for repeated use of the same voice,
        as it skips re-extracting features from reference audio.
        """
        self._ensure_loaded()

        if output_path is None:
            fd, output_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)

        wavs, sr = self._model.generate_voice_clone(
            text=text,
            language=language,
            voice_clone_prompt=voice_clone_prompt,
        )

        audio = wavs[0]
        sf.write(output_path, audio, sr)

        return {
            "audio_path": output_path,
            "sample_rate": sr,
        }

    def create_prompt_from_audio(
        self,
        ref_audio_path: str,
        ref_text: str = "",
    ) -> Any:
        """
        Create a reusable voice_clone_prompt from reference audio.
        """
        self._ensure_loaded()
        return self._model.create_voice_clone_prompt(
            ref_audio=ref_audio_path,
            ref_text=ref_text if ref_text else None,
            x_vector_only_mode=not bool(ref_text),
        )

    def create_prompt_from_audio_data(
        self,
        audio_data,
        sample_rate: int,
        ref_text: str = "",
    ) -> Any:
        """
        Create a reusable voice_clone_prompt from audio data (numpy array + sample rate).
        Used for the Voice Design → Clone pipeline.
        """
        self._ensure_loaded()
        return self._model.create_voice_clone_prompt(
            ref_audio=(audio_data, sample_rate),
            ref_text=ref_text if ref_text else None,
            x_vector_only_mode=not bool(ref_text),
        )

    def unload(self):
        """Unload models to free memory."""
        if self._model is not None:
            del self._model
        self._model = None
        self._loaded = False
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
