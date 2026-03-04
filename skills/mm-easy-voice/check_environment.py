#!/usr/bin/env python3
"""
Simple environment check for mmEasyVoice.

Usage:
    python check_environment.py
"""

import sys
import os
import subprocess


def check_python():
    """Check Python version (3.8+)"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
        return True
    print(f"[FAIL] Python {version.major}.{version.minor} (need 3.8+)")
    return False


def check_package(name):
    """Check if Python package is installed"""
    try:
        __import__(name)
        print(f"[OK] {name}")
        return True
    except ImportError:
        print(f"[FAIL] {name} not installed (pip install {name})")
        return False


def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"[OK] FFmpeg installed")
            return True
    except:
        pass
    print("[FAIL] FFmpeg not installed")
    return False


def check_api_key():
    """Check if MINIMAX_VOICE_API_KEY is set and valid"""
    api_key = os.getenv("MINIMAX_VOICE_API_KEY")
    if not api_key:
        print("[FAIL] MINIMAX_VOICE_API_KEY not set")
        print("  export MINIMAX_VOICE_API_KEY='your-key'")
        return False

    if not api_key.startswith("sk-api"):
        print(f"[FAIL] Invalid API key format (must start with 'sk-api'). The key start with 'sk-cp'(coding plan key) has no access to the voice model.")
        return False

    print(f"[OK] MINIMAX_VOICE_API_KEY set ({len(api_key)} chars)")
    return True


def main():
    """Run all checks"""
    print("mmEasyVoice Environment Check\n" + "=" * 40)

    checks = [
        ("Python", check_python()),
        ("requests", check_package("requests")),
        ("FFmpeg", check_ffmpeg()),
        ("API Key", check_api_key()),
    ]

    print("\n" + "=" * 40)
    passed = sum(1 for _, result in checks if result)
    total = len(checks)

    if passed == total:
        print(f"✓ All {total} checks passed!")
        return 0
    else:
        print(f"✗ {total - passed} check(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
