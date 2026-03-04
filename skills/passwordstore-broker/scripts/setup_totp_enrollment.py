#!/usr/bin/env python3
import base64
from datetime import datetime, timezone
import json
import os
import secrets
import shutil
import subprocess
import sys
from pathlib import Path


def _install_hint() -> str:
    if sys.platform == "darwin":
        return "brew install qrencode"
    if shutil.which("apt-get"):
        return "sudo apt-get install -y qrencode"
    if shutil.which("dnf"):
        return "sudo dnf install -y qrencode"
    if shutil.which("pacman"):
        return "sudo pacman -S --needed qrencode"
    return "install qrencode using your system package manager"


def _base32_secret(num_bytes: int = 20) -> str:
    return base64.b32encode(secrets.token_bytes(num_bytes)).decode("ascii").rstrip("=")


def _decode_base32(value: str) -> bytes:
    cleaned = value.strip().replace(" ", "")
    padding = "=" * ((8 - len(cleaned) % 8) % 8)
    return base64.b32decode(cleaned.upper() + padding, casefold=True)


def main() -> int:
    base_dir = Path.home() / ".passwordstore-broker"
    secret_file = base_dir / "totp.secret"
    qr_png_path = base_dir / "totp-enroll.png"
    setup_timestamp_file = base_dir / "setup_completed_at.txt"

    base_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        os.chmod(base_dir, 0o700)
    except OSError:
        pass

    provisioned = False
    if secret_file.exists():
        secret = secret_file.read_text(encoding="utf-8").strip().replace(" ", "")
        if not secret:
            print(f"TOTP secret file is empty: {secret_file}", file=sys.stderr)
            return 2
    else:
        secret = _base32_secret()
        secret_file.write_text(secret + "\n", encoding="utf-8")
        provisioned = True

    try:
        _decode_base32(secret)
    except Exception:  # noqa: BLE001
        print(f"Invalid base32 value in TOTP secret file: {secret_file}", file=sys.stderr)
        return 2

    try:
        os.chmod(secret_file, 0o600)
    except OSError:
        pass

    if setup_timestamp_file.exists():
        setup_completed_at = setup_timestamp_file.read_text(encoding="utf-8").strip()
    else:
        setup_completed_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        setup_timestamp_file.write_text(setup_completed_at + "\n", encoding="utf-8")
    try:
        os.chmod(setup_timestamp_file, 0o600)
    except OSError:
        pass

    otpauth_url = (
        "otpauth://totp/Passwordstore%20Broker"
        f"?secret={secret}&issuer=PasswordstoreBroker&algorithm=SHA1&digits=6&period=30"
    )

    payload = {
        "secret_file": str(secret_file),
        "otpauth_url": otpauth_url,
        "qr_png_path": str(qr_png_path),
        "setup_timestamp_file": str(setup_timestamp_file),
        "setup_completed_at": setup_completed_at,
        "provisioned": provisioned,
    }

    qrencode = shutil.which("qrencode")
    if qrencode is None:
        print(json.dumps(payload), flush=True)
        print(f"Missing required command: qrencode. Install with: {_install_hint()}", file=sys.stderr)
        print(f"Manual enrollment URL: {otpauth_url}", file=sys.stderr)
        return 2

    try:
        subprocess.run(
            [qrencode, "-o", str(qr_png_path), "-t", "PNG", otpauth_url],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        print(json.dumps(payload), flush=True)
        message = exc.stderr.strip() or "qrencode failed"
        print(f"Failed to generate QR PNG: {message}", file=sys.stderr)
        print(f"Manual enrollment URL: {otpauth_url}", file=sys.stderr)
        return 2

    try:
        os.chmod(qr_png_path, 0o600)
    except OSError:
        pass

    print(json.dumps(payload), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
