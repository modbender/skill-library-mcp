"""Tests for create-thread command."""
import pytest
import subprocess
import os

SCRIPT_PATH = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'bsky.py')
VENV_PYTHON = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'venv', 'bin', 'python3')


class TestCreateThreadDryRun:
    """Test create-thread --dry-run (no auth needed)."""

    def test_dry_run_basic(self):
        result = subprocess.run(
            [VENV_PYTHON, SCRIPT_PATH, 'create-thread', 'Post 1', 'Post 2', '--dry-run'],
            capture_output=True, text=True
        )
        assert result.returncode == 0
        assert 'DRY RUN' in result.stdout
        assert 'Post 1' in result.stdout
        assert 'Post 2' in result.stdout
        assert '2 posts' in result.stdout

    def test_dry_run_three_posts(self):
        result = subprocess.run(
            [VENV_PYTHON, SCRIPT_PATH, 'create-thread', 'A', 'B', 'C', '--dry-run'],
            capture_output=True, text=True
        )
        assert result.returncode == 0
        assert '3 posts' in result.stdout
        assert '1/3' in result.stdout
        assert '2/3' in result.stdout
        assert '3/3' in result.stdout

    def test_dry_run_shows_char_count(self):
        result = subprocess.run(
            [VENV_PYTHON, SCRIPT_PATH, 'create-thread', 'Hello', 'World', '--dry-run'],
            capture_output=True, text=True
        )
        assert result.returncode == 0
        assert '5 chars' in result.stdout

    def test_dry_run_with_urls(self):
        result = subprocess.run(
            [VENV_PYTHON, SCRIPT_PATH, 'create-thread', 'Check https://example.com', 'Post 2', '--dry-run'],
            capture_output=True, text=True
        )
        assert result.returncode == 0
        assert 'https://example.com' in result.stdout


class TestCreateThreadValidation:
    """Test input validation for create-thread."""

    def test_single_post_rejected(self):
        result = subprocess.run(
            [VENV_PYTHON, SCRIPT_PATH, 'create-thread', 'Only one', '--dry-run'],
            capture_output=True, text=True
        )
        assert result.returncode != 0
        assert 'at least 2' in result.stderr.lower()

    def test_too_long_post_rejected(self):
        long = 'x' * 301
        result = subprocess.run(
            [VENV_PYTHON, SCRIPT_PATH, 'create-thread', long, 'Short', '--dry-run'],
            capture_output=True, text=True
        )
        assert result.returncode != 0
        assert '301' in result.stderr or 'max 300' in result.stderr.lower()

    def test_empty_post_rejected(self):
        result = subprocess.run(
            [VENV_PYTHON, SCRIPT_PATH, 'create-thread', '', 'Post 2', '--dry-run'],
            capture_output=True, text=True
        )
        assert result.returncode != 0
        assert 'empty' in result.stderr.lower()

    def test_image_without_alt_rejected(self):
        result = subprocess.run(
            [VENV_PYTHON, SCRIPT_PATH, 'create-thread', 'A', 'B', '--image', 'fake.jpg', '--dry-run'],
            capture_output=True, text=True
        )
        assert result.returncode != 0
        assert 'alt' in result.stderr.lower()

    def test_300_chars_accepted(self):
        text = 'x' * 300
        result = subprocess.run(
            [VENV_PYTHON, SCRIPT_PATH, 'create-thread', text, 'Post 2', '--dry-run'],
            capture_output=True, text=True
        )
        assert result.returncode == 0


class TestCreateThreadHelp:
    """Test help output."""

    def test_help(self):
        result = subprocess.run(
            [VENV_PYTHON, SCRIPT_PATH, 'create-thread', '--help'],
            capture_output=True, text=True
        )
        assert result.returncode == 0
        assert 'thread' in result.stdout.lower()

    def test_alias_ct(self):
        result = subprocess.run(
            [VENV_PYTHON, SCRIPT_PATH, 'ct', 'A', 'B', '--dry-run'],
            capture_output=True, text=True
        )
        assert result.returncode == 0
        assert 'DRY RUN' in result.stdout


class TestVersionUpdate:
    """Verify version was updated."""

    def test_version_1_6_0(self):
        result = subprocess.run(
            [VENV_PYTHON, SCRIPT_PATH, '--version'],
            capture_output=True, text=True
        )
        assert '1.6.0' in result.stdout
