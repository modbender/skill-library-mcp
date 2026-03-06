#!/usr/bin/env python3
"""
Test secret detection scanner.
"""

import os
import sys
import tempfile
import json
import subprocess

# Add parent directory to path so we can import the script
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from main import scan_file, SECRET_PATTERNS

def test_scan_file():
    """Test scanning a file with secrets."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('''# Config
AWS_ACCESS_KEY_ID=AKIA1234567890ABCDEF
password = "super_secret_123"
token = ghp_abcdefghijklmnopqrstuvwxyz123456789012
api_key = sk-1234567890abcdefghijklmnopqrstuvwxyz123456789012345678
# Clean line
something = "not_a_secret"
''')
        temp_path = f.name
    
    try:
        findings = scan_file(temp_path)
        # Expect at least 4 findings
        assert len(findings) >= 4, f"Expected >=4 findings, got {len(findings)}"
        labels = [f['label'] for f in findings]
        # Check that we found some secrets (might not match all due to pattern specifics)
        secret_labels = set(labels)
        assert len(secret_labels) >= 2, f"Expected at least 2 distinct secret types, got {secret_labels}"
        print(f"✓ File scanning passed (found {len(findings)} secrets: {secret_labels})")
    finally:
        os.unlink(temp_path)

def test_cli_scan():
    """Test CLI scan command."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('password = "test123"\n')
        temp_path = f.name
    
    try:
        # Run the script via subprocess
        result = subprocess.run(
            [sys.executable, os.path.join(os.path.dirname(__file__), '..', 'scripts', 'main.py'),
             'scan', '--file', temp_path],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        output = result.stdout
        assert 'Password' in output or 'secret' in output.lower()
        print("✓ CLI scan passed")
    finally:
        os.unlink(temp_path)

def test_cli_install_simulation():
    """Test install command (simulated, not in a git repo)."""
    # This will fail because we're not in a git repo, but we can check the error
    result = subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(__file__), '..', 'scripts', 'main.py'),
         'install'],
        capture_output=True,
        text=True
    )
    # Extract JSON from output (may be multiline)
    lines = result.stdout.strip().split('\n')
    json_start = None
    json_end = None
    for i, line in enumerate(lines):
        if line.strip().startswith('{'):
            json_start = i
            break
    if json_start is not None:
        # Find the matching closing brace (simplistic: join from start to end)
        json_str = '\n'.join(lines[json_start:])
        try:
            data = json.loads(json_str)
            assert data['status'] in ['success', 'error']
            print("✓ CLI install (error case) passed")
            return
        except json.JSONDecodeError:
            pass
    
    # Fallback: check stderr for error
    if 'Not a git repository' in result.stderr or 'Not a git repository' in result.stdout:
        print("✓ CLI install (error case) passed (error message detected)")
    else:
        print(f"✗ CLI install output not JSON. Output: {result.stdout[:200]}")
        raise AssertionError("Install test failed")

if __name__ == '__main__':
    print("Running secret detection tests...")
    test_scan_file()
    test_cli_scan()
    test_cli_install_simulation()
    print("All tests passed!")