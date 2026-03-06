"""
Whisper Transcription - Audio to text using faster-whisper
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
from faster_whisper import WhisperModel
from modelscope import snapshot_download


class Transcriber:
    """Handle audio transcription with Whisper."""

    # ModelScope mirrors for fast CN download on core models
    MODEL_MAP = {
        "tiny": "pengzhendong/faster-whisper-tiny",
        "base": "pengzhendong/faster-whisper-base",
        "small": "pengzhendong/faster-whisper-small",
        "medium": "pengzhendong/faster-whisper-medium",
        "large-v2": "pengzhendong/faster-whisper-large-v2",
        "large-v3": "pengzhendong/faster-whisper-large-v3",
    }

    # Multilingual-only models (single-language *.en models intentionally excluded)
    MULTILINGUAL_MODELS = {
        "tiny",
        "base",
        "small",
        "medium",
        "large",
        "large-v1",
        "large-v2",
        "large-v3",
        "turbo",
        "large-v3-turbo",
        "distil-large-v2",
        "distil-large-v3",
        "distil-large-v3.5",
    }

    def __init__(
        self,
        model_size: str = "large-v2",
        model_dir: str = "./models/whisper",
        language: Optional[str] = None,
    ):
        self.model_size = model_size
        self.model_dir = Path(model_dir)
        self.language = (language or "").strip() or None
        self.model_dir.mkdir(exist_ok=True, parents=True)
        self._model: Optional[WhisperModel] = None

    def _load_model(self):
        """Load Whisper model (lazy loading)."""
        if self._model is not None:
            return

        if self.model_size not in self.MULTILINGUAL_MODELS:
            allowed = ", ".join(sorted(self.MULTILINGUAL_MODELS))
            raise ValueError(
                f"Unsupported model: {self.model_size}. Allowed models: {allowed}"
            )

        model_path = self.model_dir / f"whisper-{self.model_size}"
        repo_id = self.MODEL_MAP.get(self.model_size)

        # Prefer ModelScope mirror when configured in MODEL_MAP
        if repo_id:
            if not model_path.exists():
                print(f"[INFO] Downloading Whisper {self.model_size} model...")
                snapshot_download(repo_id, local_dir=str(model_path))
            model_ref = str(model_path)
        else:
            # Fallback to faster-whisper built-in HuggingFace model resolver
            model_ref = self.model_size

        print(f"[INFO] Loading Whisper {self.model_size}...")
        loaded_model = WhisperModel(
            model_ref, device="cpu", compute_type="int8", cpu_threads=4
        )
        self._model = loaded_model

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe audio file to text.

        Returns:
            Full transcription text
        """
        self._load_model()
        model = self._model
        if model is None:
            raise RuntimeError("Whisper model failed to initialize")

        transcribe_kwargs = {}
        if self.language is not None:
            transcribe_kwargs["language"] = self.language
        segments_generator, info = model.transcribe(audio_path, **transcribe_kwargs)

        full_text = ""
        for segment in segments_generator:
            full_text += segment.text.strip() + " "

        full_text = full_text.strip()

        # Traditional to Simplified
        full_text = self._convert_traditional_to_simplified(full_text)

        return full_text

    def transcribe_with_timestamps(self, audio_path: str) -> List[Dict[str, Any]]:
        """
        Transcribe audio file to text with timestamp information.

        Args:
            audio_path: Path to audio file

        Returns:
            List of segments, each containing:
            - start: Start time in seconds (float)
            - end: End time in seconds (float)
            - text: Transcribed text for this segment (str)
        """
        self._load_model()
        model = self._model
        if model is None:
            raise RuntimeError("Whisper model failed to initialize")

        transcribe_kwargs = {}
        if self.language is not None:
            transcribe_kwargs["language"] = self.language
        segments_generator, info = model.transcribe(audio_path, **transcribe_kwargs)

        timestamped_segments = []
        for segment in segments_generator:
            text = segment.text.strip()
            # Traditional to Simplified
            text = self._convert_traditional_to_simplified(text)

            timestamped_segments.append(
                {"start": segment.start, "end": segment.end, "text": text}
            )

        return timestamped_segments

    def _convert_traditional_to_simplified(self, text: str) -> str:
        """Convert Traditional Chinese to Simplified."""
        try:
            from opencc import OpenCC

            cc = OpenCC("t2s")
            return cc.convert(text)
        except ImportError:
            return text
