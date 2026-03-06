"""Detection accuracy tests with real fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest
from magika import Magika

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def magika_instance():
    return Magika()


def test_detect_text(magika_instance):
    result = magika_instance.identify_path(FIXTURES_DIR / "tiny.txt")
    assert result.output.group == "text"


def test_detect_png(magika_instance):
    result = magika_instance.identify_path(FIXTURES_DIR / "sample.png")
    assert result.output.label == "png"
    assert result.output.mime_type == "image/png"


def test_detect_zip(magika_instance):
    result = magika_instance.identify_path(FIXTURES_DIR / "sample.zip")
    assert result.output.label == "zip"


def test_detect_empty(magika_instance):
    result = magika_instance.identify_path(FIXTURES_DIR / "empty.bin")
    assert result.output.label == "empty"


def test_detect_misleading_extension(magika_instance):
    """A file with .png extension but text content should detect as text, not PNG."""
    result = magika_instance.identify_path(FIXTURES_DIR / "misleading.txt.png")
    assert result.output.group == "text"
    assert result.output.label != "png"


def test_identify_bytes(magika_instance):
    data = b"Hello, world! This is a plain text test string.\n" * 20
    result = magika_instance.identify_bytes(data)
    assert result.output.group == "text"


def test_batch_detection(magika_instance):
    paths = [
        FIXTURES_DIR / "tiny.txt",
        FIXTURES_DIR / "sample.png",
        FIXTURES_DIR / "sample.zip",
    ]
    results = magika_instance.identify_paths(paths)
    assert len(results) == 3
    assert results[1].output.label == "png"
