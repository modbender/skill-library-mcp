#!/usr/bin/env python3
"""Her Voice — Setup wizard.

Detects platform, installs dependencies, compiles visualizer."""

import copy
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from typing import Optional

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HER_VOICE_DIR = os.path.expanduser("~/.her-voice")
BIN_DIR = os.path.join(HER_VOICE_DIR, "bin")
CONFIG_FILE = os.path.join(HER_VOICE_DIR, "config.json")
MLX_VENV_DIR = os.path.join(HER_VOICE_DIR, "mlx-audio-venv")
PYTORCH_VENV_DIR = os.path.join(HER_VOICE_DIR, "kokoro-venv")

# Known locations where mlx-audio venv might already exist
KNOWN_MLX_VENVS = [
    os.path.expanduser("~/.openclaw/tools/mlx-audio/.venv"),
    MLX_VENV_DIR,
]


def print_step(msg: str) -> None:
    print(f"\n\U0001f527 {msg}")


def print_ok(msg: str) -> None:
    print(f"   \u2705 {msg}")


def print_warn(msg: str) -> None:
    print(f"   \u26a0\ufe0f  {msg}")


def print_err(msg: str) -> None:
    print(f"   \u274c {msg}")


def detect_platform() -> str:
    """Detect platform and return preferred TTS engine: 'mlx' or 'pytorch'."""
    if platform.system() == "Darwin" and platform.machine() == "arm64":
        return "mlx"
    return "pytorch"


def check_platform() -> str:
    """Check platform and report."""
    print_step("Checking platform...")
    engine = detect_platform()
    if engine == "mlx":
        print_ok(f"macOS {platform.mac_ver()[0]} on Apple Silicon ({platform.machine()}) — using MLX engine")
    else:
        print_ok(f"{platform.system()} {platform.machine()} — using PyTorch Kokoro engine")
    return engine


def find_mlx_audio_venv() -> Optional[str]:
    """Find an existing mlx-audio venv with the package installed."""
    for venv_path in KNOWN_MLX_VENVS:
        python = os.path.join(venv_path, "bin", "python3")
        if os.path.exists(python):
            try:
                result = subprocess.run(
                    [python, "-c", "import mlx_audio; print(mlx_audio.__file__)"],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    return venv_path
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
    return None


def setup_mlx_audio() -> str:
    """Find or install mlx-audio."""
    print_step("Checking mlx-audio...")
    existing = find_mlx_audio_venv()
    if existing:
        print_ok(f"Found mlx-audio at: {existing}")
        return existing

    print_warn("mlx-audio not found. Installing...")
    os.makedirs(MLX_VENV_DIR, exist_ok=True)
    subprocess.run([sys.executable, "-m", "venv", MLX_VENV_DIR], check=True)
    pip = os.path.join(MLX_VENV_DIR, "bin", "pip")
    subprocess.run([pip, "install", "--upgrade", "pip"], check=True, capture_output=True)
    print("   Installing mlx-audio + numpy (this may take a few minutes)...")
    subprocess.run([pip, "install", "mlx-audio", "numpy"], check=True)
    print_ok(f"Installed mlx-audio at: {MLX_VENV_DIR}")
    return MLX_VENV_DIR


def setup_pytorch_kokoro() -> str:
    """Install PyTorch Kokoro in a venv."""
    print_step("Checking PyTorch Kokoro...")
    python = os.path.join(PYTORCH_VENV_DIR, "bin", "python3")
    if os.path.exists(python):
        result = subprocess.run(
            [python, "-c", "import kokoro; print('ok')"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print_ok(f"Found kokoro at: {PYTORCH_VENV_DIR}")
            return PYTORCH_VENV_DIR

    print_warn("PyTorch Kokoro not found. Installing...")
    os.makedirs(PYTORCH_VENV_DIR, exist_ok=True)
    subprocess.run([sys.executable, "-m", "venv", PYTORCH_VENV_DIR], check=True)
    pip = os.path.join(PYTORCH_VENV_DIR, "bin", "pip")
    subprocess.run([pip, "install", "--upgrade", "pip"], check=True, capture_output=True)
    print("   Installing kokoro + soundfile + numpy (this may take a few minutes)...")
    subprocess.run([pip, "install", "kokoro>=0.8", "soundfile", "numpy"], check=True)
    print_ok(f"Installed kokoro at: {PYTORCH_VENV_DIR}")
    return PYTORCH_VENV_DIR


def check_espeak() -> None:
    """Check and install espeak-ng if needed."""
    print_step("Checking espeak-ng...")
    if shutil.which("espeak-ng"):
        print_ok("espeak-ng found")
        return

    # Check homebrew paths (macOS)
    brew_espeak = "/opt/homebrew/bin/espeak-ng"
    if os.path.exists(brew_espeak):
        print_ok(f"espeak-ng found at {brew_espeak}")
        return

    if platform.system() == "Darwin":
        print_warn("espeak-ng not found. Installing via Homebrew...")
        if not shutil.which("brew"):
            print_err("Homebrew not installed. Please install espeak-ng manually:")
            print_err("  1. Install Homebrew: https://brew.sh")
            print_err("  2. brew install espeak-ng")
            sys.exit(1)
        subprocess.run(["brew", "install", "espeak-ng"], check=True)
        print_ok("espeak-ng installed")
    elif platform.system() == "Linux":
        if shutil.which("apt-get"):
            print_err("espeak-ng not found. Install it with:")
            print_err("  sudo apt-get install espeak-ng")
        else:
            print_err("espeak-ng not found. Please install it for your distribution.")
        sys.exit(1)
    else:
        print_err("Please install espeak-ng manually.")
        sys.exit(1)


def patch_misaki_espeak(venv_path: str) -> None:
    """Patch misaki's espeak.py if it has broken espeakng_loader paths on macOS."""
    if platform.system() != "Darwin":
        return  # Only needed on macOS

    print_step("Checking misaki espeak patch...")
    python = os.path.join(venv_path, "bin", "python3")

    # First check if espeak loading works without patching
    test_code = """
try:
    from misaki.espeak import EspeakG2P
    g2p = EspeakG2P(language='en-us')
    print("OK")
except Exception as e:
    print(f"FAIL:{e}")
"""
    result = subprocess.run([python, "-c", test_code], capture_output=True, text=True, timeout=30)
    if result.stdout.strip() == "OK":
        print_ok("espeak integration works — no patch needed")
        return

    # Find the espeak.py file in misaki
    find_code = """
import misaki.espeak as me
print(me.__file__)
"""
    result = subprocess.run([python, "-c", find_code], capture_output=True, text=True, timeout=10)
    if result.returncode != 0:
        print_warn("Could not locate misaki espeak module — skipping patch")
        return

    espeak_py = result.stdout.strip()
    if not os.path.exists(espeak_py):
        print_warn(f"File not found: {espeak_py}")
        return

    with open(espeak_py) as f:
        content = f.read()

    if "espeakng_loader" not in content and "ctypes" in content:
        print_warn("Unexpected espeak.py structure — skipping patch")
        return

    brew_lib_paths = [
        "/opt/homebrew/lib/libespeak-ng.dylib",
        "/opt/homebrew/lib/libespeak-ng.1.dylib",
        "/usr/local/lib/libespeak-ng.dylib",
    ]
    lib_path = None
    for p in brew_lib_paths:
        if os.path.exists(p):
            lib_path = p
            break

    if not lib_path:
        print_warn("Could not find libespeak-ng.dylib — espeak-ng may not work correctly")
        return

    if lib_path in content:
        print_ok("Already patched")
        return

    backup = espeak_py + ".bak"
    if not os.path.exists(backup):
        shutil.copy2(espeak_py, backup)

    patched = content.replace(
        "from espeakng_loader import get_library_path",
        f"def get_library_path(): return '{lib_path}'  # Patched by Her Voice setup"
    )

    if patched == content:
        patched = re.sub(
            r'get_library_path\(\)',
            f"'{lib_path}'",
            content,
            count=1
        )

    if patched != content:
        with open(espeak_py, "w") as f:
            f.write(patched)
        print_ok(f"Patched {espeak_py} \u2192 {lib_path}")
    else:
        print_warn("Could not auto-patch. You may need to patch manually.")


def compile_visualizer() -> str:
    """Compile the HerVoice.swift visualizer (macOS only)."""
    if platform.system() != "Darwin":
        print_step("Skipping visualizer compilation (not macOS)")
        print_ok("Visualizer requires macOS — audio will play without visualization")
        return ""

    if not shutil.which("swiftc"):
        print_step("Skipping visualizer compilation (swiftc not found)")
        print_warn("Install Xcode Command Line Tools for visualizer: xcode-select --install")
        return ""

    print_step("Compiling visualizer...")
    os.makedirs(BIN_DIR, exist_ok=True)
    swift_src = os.path.join(SKILL_DIR, "assets", "HerVoice.swift")
    binary = os.path.join(BIN_DIR, "her-voice-viz")

    if not os.path.exists(swift_src):
        print_err(f"Source not found: {swift_src}")
        sys.exit(1)

    result = subprocess.run([
        "swiftc", "-o", binary, swift_src,
        "-framework", "Cocoa", "-framework", "AVFoundation"
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print_err(f"Compilation failed:\n{result.stderr}")
        sys.exit(1)

    print_ok(f"Compiled: {binary}")
    return binary


def create_config(engine: str, venv_path: str, viz_binary: str) -> dict:
    """Create or update config with discovered paths."""
    print_step("Setting up config...")

    sys.path.insert(0, os.path.join(SKILL_DIR, "scripts"))
    from config import load_config, save_config, DEFAULT_CONFIG

    if os.path.exists(CONFIG_FILE):
        config = load_config()
        print_ok("Config exists, updating paths")
    else:
        config = copy.deepcopy(DEFAULT_CONFIG)
        print_ok("Creating new config")

    config["tts_engine"] = engine

    if engine == "mlx":
        config["paths"]["mlx_audio_venv"] = venv_path
    else:
        config["paths"]["kokoro_venv"] = venv_path

    if viz_binary:
        config["paths"]["visualizer_binary"] = viz_binary

    # Find voices dir from model cache (MLX only)
    if engine == "mlx":
        python = os.path.join(venv_path, "bin", "python3")
        find_voices = """
import os, glob
pattern = os.path.expanduser("~/.cache/huggingface/hub/models--mlx-community--Kokoro-82M-bf16/snapshots/*/voices")
matches = glob.glob(pattern)
if matches:
    print(matches[0])
"""
        result = subprocess.run([python, "-c", find_voices], capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip():
            config["paths"]["voices_dir"] = result.stdout.strip()
            print_ok(f"Voices dir: {result.stdout.strip()}")

    save_config(config)
    print_ok(f"Config saved: {CONFIG_FILE}")
    return config


def download_model_mlx(venv_path: str, model_name: str = "mlx-community/Kokoro-82M-bf16") -> None:
    """Download the Kokoro model by doing a test load (MLX)."""
    print_step(f"Downloading model: {model_name}...")
    python = os.path.join(venv_path, "bin", "python3")
    result = subprocess.run([
        python, "-c",
        f"from mlx_audio.tts.utils import load_model; m = load_model(model_path='{model_name}'); print('Model loaded, sample_rate:', getattr(m, 'sample_rate', 24000))"
    ], capture_output=True, text=True, timeout=300)

    if result.returncode == 0:
        print_ok(result.stdout.strip())
    else:
        print_warn(f"Model download issue: {result.stderr[:200]}")
        print_warn("Model will download on first use.")


def download_model_pytorch(venv_path: str) -> None:
    """Trigger PyTorch Kokoro model download by importing the pipeline."""
    print_step("Downloading PyTorch Kokoro model...")
    python = os.path.join(venv_path, "bin", "python3")
    result = subprocess.run([
        python, "-c",
        "from kokoro import KPipeline; p = KPipeline(lang_code='a'); print('Model ready')"
    ], capture_output=True, text=True, timeout=300)

    if result.returncode == 0:
        print_ok(result.stdout.strip())
    else:
        print_warn(f"Model download issue: {result.stderr[:200]}")
        print_warn("Model will download on first use.")


def print_summary(config: dict, engine: str) -> None:
    """Print setup summary."""
    print("\n" + "=" * 50)
    print("\U0001f399\ufe0f  Her Voice — Setup Complete!")
    print("=" * 50)
    print(f"  Engine:     {engine}")
    print(f"  Config:     {CONFIG_FILE}")
    if engine == "mlx":
        print(f"  Venv:       {config['paths'].get('mlx_audio_venv', '')}")
    else:
        print(f"  Venv:       {config['paths'].get('kokoro_venv', '')}")
    viz = config['paths'].get('visualizer_binary', '')
    print(f"  Visualizer: {viz if viz else '(not available on this platform)'}")
    print(f"  Voices:     {config['paths'].get('voices_dir', '(will detect on first use)')}")
    print(f"  Model:      {config.get('model', 'kokoro (auto-download)')}")
    print()
    print("  Quick test:")
    print(f"    python3 {os.path.join(SKILL_DIR, 'scripts', 'speak.py')} \"Hello, world!\"")
    print()


def cmd_status() -> None:
    """Check status of all components."""
    print("\U0001f399\ufe0f  Her Voice — Status Check\n")

    engine = detect_platform()
    print(f"  Platform:     {platform.system()} {platform.machine()}")
    print(f"  Engine:       {engine}")

    # Config
    print(f"  Config:       {'\u2705' if os.path.exists(CONFIG_FILE) else '\u274c'} {CONFIG_FILE}")

    # Venv
    if engine == "mlx":
        venv = find_mlx_audio_venv()
        print(f"  mlx-audio:    {'\u2705 ' + venv if venv else '\u274c not found'}")
    else:
        pytorch_python = os.path.join(PYTORCH_VENV_DIR, "bin", "python3")
        if os.path.exists(pytorch_python):
            result = subprocess.run(
                [pytorch_python, "-c", "import kokoro; print('ok')"],
                capture_output=True, text=True, timeout=10
            )
            has_kokoro = result.returncode == 0
        else:
            has_kokoro = False
        print(f"  kokoro:       {'\u2705 ' + PYTORCH_VENV_DIR if has_kokoro else '\u274c not found'}")

    # espeak-ng
    has_espeak = shutil.which("espeak-ng") or os.path.exists("/opt/homebrew/bin/espeak-ng")
    print(f"  espeak-ng:    {'\u2705' if has_espeak else '\u274c'}")

    # Visualizer
    viz = os.path.join(BIN_DIR, "her-voice-viz")
    if platform.system() == "Darwin":
        print(f"  Visualizer:   {'\u2705' if os.path.exists(viz) else '\u274c'} {viz}")
    else:
        print(f"  Visualizer:   \u26aa not available (macOS only)")

    # Model
    if engine == "mlx":
        venv = find_mlx_audio_venv()
        if venv:
            python = os.path.join(venv, "bin", "python3")
            result = subprocess.run(
                [python, "-c", "from mlx_audio.tts.utils import load_model; load_model(model_path='mlx-community/Kokoro-82M-bf16'); print('OK')"],
                capture_output=True, text=True, timeout=60
            )
            model_ok = result.stdout.strip() == "OK"
        else:
            model_ok = False
        print(f"  Model:        {'\u2705' if model_ok else '\u274c'} mlx-community/Kokoro-82M-bf16")
    else:
        pytorch_python = os.path.join(PYTORCH_VENV_DIR, "bin", "python3")
        if os.path.exists(pytorch_python):
            result = subprocess.run(
                [pytorch_python, "-c", "from kokoro import KPipeline; print('OK')"],
                capture_output=True, text=True, timeout=60
            )
            model_ok = result.stdout.strip() == "OK"
        else:
            model_ok = False
        print(f"  Model:        {'\u2705' if model_ok else '\u274c'} kokoro (PyTorch)")

    # Daemon
    pid_file = os.path.join(HER_VOICE_DIR, "tts.pid")
    daemon_running = False
    if os.path.exists(pid_file):
        try:
            with open(pid_file) as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)
            daemon_running = True
        except (ProcessLookupError, ValueError, OSError):
            pass
    print(f"  Daemon:       {'\U0001f7e2 running' if daemon_running else '\u26aa stopped'}")
    print()


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        cmd_status()
        return

    print("\U0001f399\ufe0f  Her Voice — Setup Wizard\n")

    engine = check_platform()

    if engine == "mlx":
        venv_path = setup_mlx_audio()
    else:
        venv_path = setup_pytorch_kokoro()

    check_espeak()

    if engine == "mlx":
        patch_misaki_espeak(venv_path)

    viz_binary = compile_visualizer()
    config = create_config(engine, venv_path, viz_binary)

    if engine == "mlx":
        download_model_mlx(venv_path, config.get("model", "mlx-community/Kokoro-82M-bf16"))
    else:
        download_model_pytorch(venv_path)

    print_summary(config, engine)


if __name__ == "__main__":
    main()
