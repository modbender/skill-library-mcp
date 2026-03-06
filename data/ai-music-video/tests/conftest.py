"""Shared fixtures for AI Music Video E2E tests."""
import json
import os
import shutil
import subprocess
import tempfile

import pytest

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(SKILL_DIR, "scripts")


@pytest.fixture(scope="session")
def skill_env():
    """Environment with API keys from environment variables."""
    return os.environ.copy()


@pytest.fixture
def work_dir(tmp_path):
    """Fresh temp directory per test."""
    return str(tmp_path)


@pytest.fixture
def sample_prompts_file(work_dir):
    """Create a minimal prompts.json (3 scenes) for testing."""
    prompts = [
        "A neon-lit city street at night with rain reflections on the pavement",
        "A lone figure standing on a hilltop watching a dramatic sunset",
        "Cherry blossom petals falling in slow motion through golden light",
    ]
    path = os.path.join(work_dir, "prompts.json")
    with open(path, "w") as f:
        json.dump(prompts, f)
    return path


@pytest.fixture
def single_prompt_file(work_dir):
    """Create a 1-scene prompts.json for minimal cost testing."""
    prompts = ["A warm sunrise over a calm ocean, peaceful and serene"]
    path = os.path.join(work_dir, "prompts.json")
    with open(path, "w") as f:
        json.dump(prompts, f)
    return path


def run_script(script_name, args, env, timeout=600):
    """Run a bash script and return CompletedProcess."""
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    cmd = ["bash", script_path] + args
    result = subprocess.run(
        cmd, capture_output=True, text=True, env=env, timeout=timeout
    )
    return result


# Markers
def pytest_configure(config):
    config.addinivalue_line("markers", "free: no API calls, no cost")
    config.addinivalue_line("markers", "cheap: minimal API calls (~$0.01-0.05)")
    config.addinivalue_line("markers", "expensive: full pipeline (~$0.30+)")
