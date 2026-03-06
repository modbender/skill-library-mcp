#!/usr/bin/env python3
"""
Tests for qwen3-tts-local-inference skill.

Run from the skill directory:
    python -m pytest test_tts.py -v
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import numpy as np

SCRIPTS_DIR = Path(__file__).resolve().parent / "scripts"
sys.path.insert(0, SCRIPTS_DIR.as_posix())


# ── Config tests ──────────────────────────────────────────────────────────────


class TestConfig:
    def test_default_model_size_is_small(self):
        import importlib
        import config

        importlib.reload(config)
        assert config.USE_SMALL_MODEL is True
        assert config.MODEL_SIZE_LABEL == "small"

    def test_model_size_large_via_env(self, monkeypatch):
        monkeypatch.setenv("QWEN_TTS_MODEL_SIZE", "large")
        import importlib
        import config

        importlib.reload(config)
        assert config.USE_SMALL_MODEL is False
        assert config.MODEL_SIZE_LABEL == "large"
        assert "1.7B" in config.MODEL_VARIANTS["custom-voice"]

    def test_model_size_small_via_env(self, monkeypatch):
        monkeypatch.setenv("QWEN_TTS_MODEL_SIZE", "small")
        import importlib
        import config

        importlib.reload(config)
        assert config.USE_SMALL_MODEL is True
        assert "0.6B" in config.MODEL_VARIANTS["custom-voice"]

    def test_custom_model_dir_via_env(self, monkeypatch, tmp_path):
        monkeypatch.setenv("QWEN_TTS_MODEL_DIR", str(tmp_path))
        import importlib
        import config

        importlib.reload(config)
        assert config.MODEL_DIR == str(tmp_path)

    def test_speaker_names_populated(self):
        import config

        assert len(config.SPEAKER_NAMES) == 9
        assert "Ryan" in config.SPEAKER_NAMES

    def test_supported_languages(self):
        import config

        assert "English" in config.SUPPORTED_LANGUAGES
        assert "Auto" in config.SUPPORTED_LANGUAGES

    def test_all_three_variants_present(self):
        import config

        for variants in (config.LARGE_MODELS, config.SMALL_MODELS):
            assert "custom-voice" in variants
            assert "voice-design" in variants
            assert "voice-clone" in variants


# ── Fake model for inference tests ────────────────────────────────────────────


def _make_fake_wav(duration_s: float = 1.0, sr: int = 24000):
    """Return (list-of-arrays, sample_rate) mimicking qwen_tts output."""
    samples = np.zeros(int(sr * duration_s), dtype=np.float32)
    return [samples], sr


class FakeQwen3TTSModel:
    """Stands in for qwen_tts.Qwen3TTSModel during tests."""

    @classmethod
    def from_pretrained(cls, model_id, **kwargs):
        return cls()

    def generate_custom_voice(self, **kwargs):
        return _make_fake_wav()

    def generate_voice_design(self, **kwargs):
        return _make_fake_wav()

    def generate_voice_clone(self, **kwargs):
        return _make_fake_wav()


# ── Inference engine tests ────────────────────────────────────────────────────


class TestInferenceEngine:
    @pytest.fixture(autouse=True)
    def _setup(self, tmp_path):
        self.output_dir = tmp_path / "output"
        self.model_dir = tmp_path / "models"
        self.model_dir.mkdir()

        fake_module = MagicMock()
        fake_module.Qwen3TTSModel = FakeQwen3TTSModel
        self._patcher = patch.dict(sys.modules, {"qwen_tts": fake_module})
        self._patcher.start()

        from inference import TTSInferenceEngine

        self.engine = TTSInferenceEngine(
            model_dir=str(self.model_dir),
            output_dir=str(self.output_dir),
        )

    def teardown_method(self):
        self._patcher.stop()

    def test_custom_voice_produces_wav(self):
        result = self.engine.generate_custom_voice(text="Hello", speaker="Ryan")
        assert result["file"].endswith(".wav")
        assert Path(result["file"]).exists()
        assert result["duration_s"] > 0
        assert "inference_s" in result

    def test_voice_design_produces_wav(self):
        result = self.engine.generate_voice_design(
            text="Welcome", instruct="Warm female voice"
        )
        assert Path(result["file"]).exists()

    def test_voice_clone_produces_wav(self):
        result = self.engine.generate_voice_clone(
            text="Cloned speech", ref_audio="ref.wav", ref_text="ref text"
        )
        assert Path(result["file"]).exists()

    def test_status_returns_expected_keys(self):
        status = self.engine.status()
        assert "loaded_variant" in status
        assert "device" in status
        assert "model_dir" in status
        assert "output_dir" in status
        assert "model_variants" in status

    def test_model_swap_on_mode_change(self):
        self.engine.generate_custom_voice(text="a")
        assert self.engine._current_variant == "custom-voice"

        self.engine.generate_voice_clone(text="b", ref_audio="r.wav", ref_text="r")
        assert self.engine._current_variant == "voice-clone"

    def test_no_reload_same_variant(self):
        self.engine.generate_custom_voice(text="first")
        model_after_first = self.engine._model

        self.engine.generate_custom_voice(text="second")
        assert self.engine._model is model_after_first

    def test_output_dir_created(self):
        assert self.output_dir.is_dir()


# ── CLI tests ─────────────────────────────────────────────────────────────────


class TestCLI:
    @pytest.fixture(autouse=True)
    def _setup(self):
        fake_module = MagicMock()
        fake_module.Qwen3TTSModel = FakeQwen3TTSModel
        self._patcher = patch.dict(sys.modules, {"qwen_tts": fake_module})
        self._patcher.start()

    def teardown_method(self):
        self._patcher.stop()

    def test_cli_custom_voice(self, tmp_path):
        from tts import build_parser, main

        out_dir = str(tmp_path / "cli_out")
        sys.argv = [
            "tts.py",
            "Hello from CLI",
            "--output-dir", out_dir,
            "--json",
        ]
        from io import StringIO

        captured = StringIO()
        with patch("sys.stdout", captured):
            main()

        output = json.loads(captured.getvalue())
        assert "file" in output
        assert output["duration_s"] > 0

    def test_cli_voice_design_requires_instruct(self, tmp_path):
        sys.argv = [
            "tts.py",
            "Hello",
            "--mode", "voice-design",
            "--output-dir", str(tmp_path),
        ]
        with pytest.raises(SystemExit) as exc_info:
            from tts import main
            main()
        assert exc_info.value.code == 1

    def test_cli_voice_clone_requires_ref_audio(self, tmp_path):
        sys.argv = [
            "tts.py",
            "Hello",
            "--mode", "voice-clone",
            "--output-dir", str(tmp_path),
        ]
        with pytest.raises(SystemExit) as exc_info:
            from tts import main
            main()
        assert exc_info.value.code == 1

    def test_cli_output_flag(self, tmp_path):
        out_file = str(tmp_path / "custom_out.wav")
        sys.argv = [
            "tts.py",
            "Test output flag",
            "-o", out_file,
            "--output-dir", str(tmp_path / "wav"),
            "--json",
        ]
        from io import StringIO

        captured = StringIO()
        with patch("sys.stdout", captured):
            from tts import main
            main()

        output = json.loads(captured.getvalue())
        assert output["file"] == out_file
        assert Path(out_file).exists()

    def test_build_parser_defaults(self):
        from tts import build_parser

        parser = build_parser()
        args = parser.parse_args(["hello world"])
        assert args.text == "hello world"
        assert args.mode == "custom-voice"
        assert args.speaker == "Ryan"
        assert args.language == "Auto"


# ── Download script tests ────────────────────────────────────────────────────


class TestDownloadModels:
    def test_skip_if_already_present(self, tmp_path):
        model_id = "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice"
        local_name = model_id.replace("/", "--")
        model_path = tmp_path / local_name
        model_path.mkdir(parents=True)
        (model_path / "model.safetensors").write_text("fake")

        from download_models import download_model

        with patch("huggingface_hub.snapshot_download") as mock_dl:
            result = download_model(model_id, tmp_path)

        assert result is True
        mock_dl.assert_not_called()

    def test_downloads_when_not_present(self, tmp_path):
        model_id = "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice"

        from download_models import download_model

        with patch("huggingface_hub.snapshot_download") as mock_dl:
            result = download_model(model_id, tmp_path)

        assert result is True
        mock_dl.assert_called_once()
