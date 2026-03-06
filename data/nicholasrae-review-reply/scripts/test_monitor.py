#!/usr/bin/env python3
"""Stub regression test for monitor.py — expand as implementation grows."""
import subprocess, sys, os

SCRIPT = os.path.join(os.path.dirname(__file__), "monitor.py")

def test_syntax():
    """Script must have valid Python syntax."""
    result = subprocess.run([sys.executable, "-m", "py_compile", SCRIPT], capture_output=True)
    assert result.returncode == 0, f"Syntax error: {result.stderr.decode()}"

def test_help():
    """Script must respond to --help without crashing."""
    result = subprocess.run([sys.executable, SCRIPT, "--help"], capture_output=True, timeout=10)
    assert result.returncode in (0, 1), f"--help crashed: {result.stderr.decode()[:200]}"

if __name__ == "__main__":
    test_syntax()
    test_help()
    print("✅ All stub tests passed.")
