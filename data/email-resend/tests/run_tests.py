#!/usr/bin/env python3
"""Run email-resend skill tests using pytest."""
import os
import subprocess
import sys

# Run pytest on the tests directory
tests_dir = os.path.dirname(os.path.abspath(__file__))
result = subprocess.run(
    [sys.executable, "-m", "pytest", tests_dir, "-v", "--tb=short"]
)
sys.exit(result.returncode)
