#!/usr/bin/env python3
"""Her Voice — Configuration management and shared utilities."""

import copy
import json
import os
import sys
from typing import Any, Optional

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.expanduser("~/.her-voice")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

KNOWN_MLX_VENVS = [
    os.path.expanduser("~/.her-voice/mlx-audio-venv"),
    os.path.expanduser("~/.openclaw/tools/mlx-audio/.venv"),
]

KNOWN_PYTORCH_VENVS = [
    os.path.expanduser("~/.her-voice/kokoro-venv"),
    os.path.expanduser("~/.openclaw/tools/kokoro/.venv"),
]

# Canonical language -> Kokoro lang code mapping (also mirrored in HerVoice.swift)
LANG_MAP: dict[str, str] = {
    "en": "a", "en-us": "a", "en-gb": "b",
    "ja": "j", "zh": "z", "ko": "k",
}

DEFAULT_CONFIG: dict[str, Any] = {
    "agent_name": "",
    "user_name": "",
    "user_name_tts": "",
    "voice": "af_heart",
    "voice_blend": {"af_heart": 0.6, "af_sky": 0.4},
    "speed": 1.05,
    "language": "en",
    "tts_engine": "auto",  # "auto", "mlx", or "pytorch"
    "model": "mlx-community/Kokoro-82M-bf16",
    "visualizer": {
        "enabled": True,
        "mode": "v2",
        "fps": 60,
        "remember_position": True
    },
    "notification_sound": {
        "enabled": True,
        "sound": "Blow"
    },
    "daemon": {
        "auto_start": True,
        "socket_path": os.path.join(CONFIG_DIR, "tts.sock"),
        "pid_file": os.path.join(CONFIG_DIR, "tts.pid")
    },
    "paths": {
        "mlx_audio_venv": "",
        "visualizer_binary": "",
        "voices_dir": ""
    }
}


def find_venv(config: dict[str, Any], engine: str) -> Optional[str]:
    """Find the Python interpreter for the given engine."""
    if engine == "mlx":
        configured = config["paths"].get("mlx_audio_venv", "")
        if configured:
            python = os.path.join(configured, "bin", "python3")
            if os.path.exists(python):
                return python
        for venv in KNOWN_MLX_VENVS:
            python = os.path.join(venv, "bin", "python3")
            if os.path.exists(python):
                return python
    else:
        configured = config["paths"].get("kokoro_venv", "")
        if configured:
            python = os.path.join(configured, "bin", "python3")
            if os.path.exists(python):
                return python
        for venv in KNOWN_PYTORCH_VENVS:
            python = os.path.join(venv, "bin", "python3")
            if os.path.exists(python):
                return python
    return None


def _validate_venv_python(python: str) -> bool:
    """Validate that a venv Python path is safe to execute."""
    # Use abspath (not realpath) — venv pythons are symlinks to system Python
    abspath = os.path.abspath(python)
    if not os.path.basename(abspath).startswith("python"):
        return False
    bin_dir = os.path.dirname(abspath)
    if os.path.basename(bin_dir) not in ("bin", "Scripts"):
        return False
    venv_dir = os.path.dirname(bin_dir)
    if not os.path.exists(os.path.join(venv_dir, "pyvenv.cfg")):
        return False
    return True


def ensure_correct_python(config: dict[str, Any], engine: str) -> bool:
    """Re-exec with the correct venv Python if we're not already in it."""
    if engine == "mlx":
        try:
            import mlx_audio  # noqa: F401
            return True
        except ImportError:
            pass
    else:
        try:
            import kokoro  # noqa: F401
            return True
        except ImportError:
            pass

    python = find_venv(config, engine)
    if not python:
        print(f"Error: {'mlx-audio' if engine == 'mlx' else 'kokoro'} not found. Run setup first:", file=sys.stderr)
        print(f"  python3 {os.path.join(SKILL_DIR, 'scripts', 'setup.py')}", file=sys.stderr)
        sys.exit(1)

    if not _validate_venv_python(python):
        print(f"Error: resolved Python path failed validation: {python}", file=sys.stderr)
        print("Ensure the path points to a Python interpreter inside a valid venv.", file=sys.stderr)
        sys.exit(1)

    os.execv(python, [python] + sys.argv)


def detect_engine(config: dict[str, Any]) -> str:
    """Detect which TTS engine to use: 'mlx' or 'pytorch'."""
    engine = config.get("tts_engine", "auto")
    if engine in ("mlx", "pytorch"):
        return engine
    # Auto-detect
    try:
        import mlx_audio  # noqa: F401
        return "mlx"
    except ImportError:
        pass
    try:
        import kokoro  # noqa: F401
        return "pytorch"
    except ImportError:
        pass
    # Fallback: check platform
    import platform as _platform
    if _platform.system() == "Darwin" and _platform.machine() == "arm64":
        return "mlx"
    return "pytorch"


def resolve_voice(config: dict[str, Any], engine: Optional[str] = None) -> str:
    """Resolve voice path — check for blended voice file, fall back to base voice.
    For pytorch engine, returns voice name string (not a path)."""
    if engine is None:
        engine = config.get("tts_engine", "auto")
        if engine == "auto":
            engine = detect_engine(config)

    if engine == "pytorch":
        # PyTorch kokoro uses voice name strings, not .safetensors paths
        return config["voice"]

    voices_dir = config["paths"].get("voices_dir", "")
    blend = config.get("voice_blend", {})

    if blend and voices_dir:
        parts = []
        for name, weight in sorted(blend.items(), key=lambda x: -x[1]):
            parts.append(f"{name}_{int(weight * 100)}")
        blend_name = "_".join(parts) + ".safetensors"
        blend_path = os.path.join(voices_dir, blend_name)
        if os.path.exists(blend_path):
            return blend_path

    if voices_dir:
        base = os.path.join(voices_dir, f"{config['voice']}.safetensors")
        if os.path.exists(base):
            return base

    return config["voice"]


def load_config() -> dict[str, Any]:
    """Load config, returning defaults merged with saved values."""
    config = copy.deepcopy(DEFAULT_CONFIG)
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            saved = json.load(f)
        _deep_merge(config, saved)
    return config


def save_config(config: dict[str, Any]) -> None:
    """Save config to disk."""
    os.makedirs(CONFIG_DIR, mode=0o700, exist_ok=True)
    fd = os.open(CONFIG_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(config, f, indent=2)


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> None:
    """Merge override into base (in-place)."""
    for k, v in override.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v


def get_value(config: dict[str, Any], key: str) -> Any:
    """Get a value using dot notation (e.g. 'visualizer.enabled')."""
    parts = key.split(".")
    obj = config
    for p in parts:
        if isinstance(obj, dict) and p in obj:
            obj = obj[p]
        else:
            return None
    return obj


def set_value(config: dict[str, Any], key: str, value: Any) -> None:
    """Set a value using dot notation."""
    parts = key.split(".")
    obj = config
    for p in parts[:-1]:
        if p not in obj or not isinstance(obj[p], dict):
            obj[p] = {}
        obj = obj[p]
    # Prevent overwriting nested dicts — use dot notation instead
    old = obj.get(parts[-1])
    if isinstance(old, dict):
        print(f"Error: '{key}' is a section, not a value. Use dot notation (e.g. '{key}.enabled').", file=sys.stderr)
        sys.exit(1)
    if isinstance(old, bool):
        value = value.lower() in ("true", "1", "yes")
    elif isinstance(old, int):
        try:
            value = int(value)
        except ValueError:
            pass
    elif isinstance(old, float):
        try:
            value = float(value)
        except ValueError:
            pass
    elif old is None:
        # No existing value — try to infer type from the string
        if value.lower() in ("true", "false"):
            value = value.lower() == "true"
        else:
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass  # Keep as string
    obj[parts[-1]] = value


def cmd_init() -> None:
    """Create default config."""
    if os.path.exists(CONFIG_FILE):
        print(f"Config already exists: {CONFIG_FILE}")
        print("Use 'set' to modify values.")
        return
    save_config(DEFAULT_CONFIG)
    print(f"Created default config: {CONFIG_FILE}")


def cmd_get(key: str) -> None:
    """Get a config value."""
    config = load_config()
    val = get_value(config, key)
    if val is None:
        print(f"Key not found: {key}", file=sys.stderr)
        sys.exit(1)
    if isinstance(val, dict):
        print(json.dumps(val, indent=2))
    else:
        print(val)


def cmd_set(key: str, value: str) -> None:
    """Set a config value."""
    config = load_config()
    set_value(config, key, value)
    save_config(config)
    print(f"{key} = {get_value(config, key)}")


def cmd_status() -> None:
    """Show current config summary."""
    config = load_config()
    exists = os.path.exists(CONFIG_FILE)
    print(f"Config file: {CONFIG_FILE} ({'exists' if exists else 'NOT FOUND'})")
    print()
    print(f"  Voice:        {config['voice']}")
    print(f"  Voice blend:  {config['voice_blend']}")
    print(f"  Speed:        {config['speed']}")
    print(f"  Language:     {config['language']}")
    print(f"  Model:        {config['model']}")
    print()
    viz = config["visualizer"]
    print(f"  Visualizer:   {'ON' if viz['enabled'] else 'OFF'} (mode: {viz['mode']}, {viz['fps']}fps)")
    ns = config["notification_sound"]
    print(f"  Notify sound: {'ON' if ns['enabled'] else 'OFF'} ({ns['sound']})")
    d = config["daemon"]
    print(f"  Daemon:       auto_start={'ON' if d['auto_start'] else 'OFF'}")
    print(f"                socket: {d['socket_path']}")
    print()
    paths = config["paths"]
    for k, v in paths.items():
        status = v if v else "(auto-detect)"
        print(f"  paths.{k}: {status}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: config.py <init|get|set|status> [args...]", file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "init":
        cmd_init()
    elif cmd == "get":
        if len(sys.argv) < 3:
            print("Usage: config.py get <key>", file=sys.stderr)
            sys.exit(1)
        cmd_get(sys.argv[2])
    elif cmd == "set":
        if len(sys.argv) < 4:
            print("Usage: config.py set <key> <value>", file=sys.stderr)
            sys.exit(1)
        cmd_set(sys.argv[2], sys.argv[3])
    elif cmd == "status":
        cmd_status()
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
