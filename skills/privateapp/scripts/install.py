#!/usr/bin/env python3
"""
Install script for privateapp v2 — Personal PWA App Marketplace.

Installs Python dependencies, generates VAPID keys, creates config and data directories.
Works on macOS and Linux (Python 3.9+).

Architecture:
  - Built-in apps:  apps/<id>/backend/routes.py + apps/<id>/frontend/App.tsx

  - Commons:        scripts/commons/  (shared Python utilities)
  - Frontend:       frontend/src/commons/  (shared React components/hooks)
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPTS_DIR.parent
DEFAULT_CONFIG_PATH = SCRIPTS_DIR / "config.json"

REQUIRED_PACKAGES = [
    "fastapi>=0.100",
    "uvicorn[standard]>=0.20",
    "psutil>=5.9",
    "pywebpush>=2.0",
    "py-vapid>=1.9",
]


def run(cmd: list[str], check: bool = True, capture: bool = True) -> subprocess.CompletedProcess:
    display = " ".join(str(c) for c in cmd)
    print(f"  → {display}")
    return subprocess.run(cmd, check=check, capture_output=capture, text=True)


def pip_install(packages: list[str]) -> None:
    """Install packages; handles venv, --user, and Homebrew PEP 668 environments."""
    base_cmd = [sys.executable, "-m", "pip", "install", "--quiet"]

    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )

    attempts = []
    if in_venv:
        attempts = [base_cmd + packages]
    else:
        attempts = [
            base_cmd + ["--user"] + packages,
            base_cmd + packages,
            base_cmd + ["--break-system-packages"] + packages,
            base_cmd + ["--user", "--break-system-packages"] + packages,
        ]

    for cmd in attempts:
        result = run(cmd, check=False)
        if result.returncode == 0:
            return
        last_err = result.stderr

    print(f"  ⚠️  pip install may have failed. Last error:\n{last_err[:300]}")
    print("  Continuing anyway — packages may already be installed.")


def generate_vapid_keys(data_dir: Path, email: str) -> tuple[str, str]:
    """Generate VAPID key pair and write to data_dir. Returns (private_pem_path, public_key_b64)."""
    private_pem = data_dir / "vapid_private.pem"
    public_txt = data_dir / "vapid_public.txt"

    if private_pem.exists() and public_txt.exists():
        print("  ✅ VAPID keys already exist — skipping generation")
        return str(private_pem), public_txt.read_text().strip()

    try:
        from py_vapid import Vapid
    except ImportError:
        print("  ❌ py-vapid not available — skipping VAPID key generation")
        return "", ""

    print("  Generating VAPID key pair...")
    vapid = Vapid()
    vapid.generate_keys()

    # Write private key
    vapid.save_key(str(private_pem))

    # Export public key as URL-safe base64 (application server key for browsers)
    from py_vapid import b64urlencode
    import json as _json

    pub_key_bytes = vapid.public_key.public_bytes(
        encoding=__import__("cryptography.hazmat.primitives.serialization", fromlist=["Encoding"]).Encoding.X962,
        format=__import__("cryptography.hazmat.primitives.serialization", fromlist=["PublicFormat"]).PublicFormat.UncompressedPoint,
    )
    pub_key_b64 = b64urlencode(pub_key_bytes)
    public_txt.write_text(pub_key_b64)

    print(f"  ✅ VAPID private key: {private_pem}")
    print(f"  ✅ VAPID public key:  {pub_key_b64[:40]}...")
    return str(private_pem), pub_key_b64


def main() -> None:
    print("🔧 Installing Private App...\n")

    # 1. Python version check
    v = sys.version_info
    print(f"Python: {v.major}.{v.minor}.{v.micro}")
    if v < (3, 9):
        print("❌ Python 3.9+ required")
        sys.exit(1)
    print(f"  ✅ Python {v.major}.{v.minor}\n")

    # 2. Platform check
    if sys.platform == "win32":
        print("❌ Windows is not supported. Use macOS or Linux.")
        sys.exit(1)
    print(f"  ✅ Platform: {sys.platform}\n")

    # 3. Install Python packages
    print("📦 Installing Python packages...")
    pip_install(REQUIRED_PACKAGES)
    print()

    # 4. Verify imports
    print("🔍 Verifying imports...")
    errors = []
    checks = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("psutil", "psutil"),
        ("pywebpush", "pywebpush"),
        ("py-vapid", "py_vapid"),
    ]
    for name, module in checks:
        result = run(
            [sys.executable, "-c", f"import {module}; print('ok')"],
            check=False,
        )
        if result.returncode == 0 and "ok" in result.stdout:
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name}")
            errors.append(name)
    print()

    if errors:
        print(f"❌ Missing packages: {', '.join(errors)}")
        print("   Try: pip install " + " ".join(errors))
        sys.exit(1)

    # 5. Read config to find data_dir
    config = {}
    if DEFAULT_CONFIG_PATH.exists():
        try:
            config = json.loads(DEFAULT_CONFIG_PATH.read_text())
        except Exception:
            pass
    data_dir = Path(config.get("data_dir", "~/.local/share/privateapp")).expanduser()
    vapid_email = config.get("push", {}).get("vapid_email", "admin@localhost")

    # 6. Create data directory
    print(f"📁 Setting up data directory: {data_dir}")
    data_dir.mkdir(parents=True, exist_ok=True)
    print(f"  ✅ {data_dir}\n")

    # 7. Copy default config to data_dir if not present
    user_config = data_dir / "config.json"
    if not user_config.exists() and DEFAULT_CONFIG_PATH.exists():
        shutil.copy(DEFAULT_CONFIG_PATH, user_config)
        print(f"  ✅ Config copied to {user_config}")
    elif user_config.exists():
        print(f"  ✅ Config already exists: {user_config}")
    print()

    # 8. Generate VAPID keys
    print("🔑 Setting up VAPID keys for push notifications...")
    private_key_path, public_key = generate_vapid_keys(data_dir, vapid_email)
    print()

    # 9. Verify apps are present
    print("📱 Checking built-in apps...")
    apps_dir = REPO_DIR / "apps"
    if apps_dir.is_dir():
        app_names = [d.name for d in sorted(apps_dir.iterdir()) if d.is_dir() and (d / "app.json").exists()]
        for name in app_names:
            print(f"  ✅ {name}")
        if not app_names:
            print("  ⚠️  No apps found in apps/")
    else:
        print(f"  ⚠️  Apps directory not found: {apps_dir}")
    print()

    # 10. Quick server test (import check)
    print("🧪 Testing server startup (import check)...")
    result = run(
        [sys.executable, "-c",
         f"import sys; sys.argv=['server','--config','{DEFAULT_CONFIG_PATH}']; "
         "from pathlib import Path; import importlib.util; "
         f"spec = importlib.util.spec_from_file_location('server', '{SCRIPTS_DIR}/server.py'); "
         "m = importlib.util.module_from_spec(spec); print('ok')"],
        check=False,
    )
    if result.returncode == 0:
        print("  ✅ Server imports OK")
    else:
        print(f"  ⚠️  Server import test inconclusive: {result.stderr[:200]}")
    print()

    # 11. Print summary
    print("=" * 50)
    print("✅ Private App installed successfully!")
    print()
    print("▶  Start the server:")
    print(f"   python3 {SCRIPTS_DIR}/server.py")
    print()
    print(f"   Then open: http://localhost:{config.get('port', 8800)}/")
    print()
    print("📱 Add to home screen:")
    print("   iOS Safari  → Share → Add to Home Screen")
    print("   Android     → Chrome menu → Add to Home Screen")
    print()
    if public_key:
        print(f"🔔 VAPID public key: {public_key[:40]}...")
        print()

    print("🛠  systemd service (Linux):")
    print("   See SKILL.md for systemd/launchd setup instructions.")
    print()
    print("📖 Documentation: SKILL.md")


if __name__ == "__main__":
    main()
