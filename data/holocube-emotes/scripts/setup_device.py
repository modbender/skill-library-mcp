#!/usr/bin/env python3
"""
Upload sprite kit to a GeekMagic holocube and configure it.

Usage:
    python3 setup_device.py --sprites-dir ./sprites [--ip IP] [--clear] [--backup-dir DIR]
"""

import sys
import os
import argparse
import urllib.request
import urllib.error
import json
from pathlib import Path


def check_device(ip):
    """Verify holocube is reachable."""
    try:
        with urllib.request.urlopen(f"http://{ip}/v.json", timeout=3) as r:
            info = json.loads(r.read())
        with urllib.request.urlopen(f"http://{ip}/space.json", timeout=3) as r:
            space = json.loads(r.read())
        print(f"Device: {info.get('m', 'unknown')} {info.get('v', '')}")
        print(f"Storage: {space.get('free', 0) // 1024}KB free / {space.get('total', 0) // 1024}KB total")
        return True
    except Exception as e:
        print(f"ERROR: Can't reach device at {ip}: {e}")
        return False


def backup_device(ip, backup_dir):
    """Download all existing images from the device."""
    backup_dir = Path(backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)

    try:
        with urllib.request.urlopen(f"http://{ip}/filelist?dir=/image", timeout=5) as r:
            html = r.read().decode()
    except Exception as e:
        print(f"ERROR: Can't list files: {e}")
        return False

    # Parse filenames from HTML
    import re
    files = re.findall(r"href='/image/([^']+)'", html)

    if not files:
        print("No files to back up.")
        return True

    print(f"Backing up {len(files)} files...")
    for f in files:
        try:
            urllib.request.urlretrieve(f"http://{ip}/image/{f}", str(backup_dir / f))
            print(f"  ✓ {f}")
        except Exception as e:
            print(f"  ✗ {f}: {e}")
    return True


def clear_device(ip):
    """Clear all images from the device."""
    try:
        with urllib.request.urlopen(f"http://{ip}/set?clear=image", timeout=5) as r:
            body = r.read().decode()
        if "OK" in body:
            print("Cleared all images from device.")
            return True
        print(f"Unexpected response: {body}")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def upload_file(ip, filepath, filename):
    """Upload a single file to the holocube."""
    import http.client
    import mimetypes

    with open(filepath, "rb") as f:
        file_data = f.read()

    boundary = "----HolocubeUpload"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: {mimetypes.guess_type(filename)[0] or 'application/octet-stream'}\r\n"
        f"\r\n"
    ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()

    try:
        conn = http.client.HTTPConnection(ip, timeout=10)
        conn.request(
            "POST", "/doUpload?dir=/image", body,
            {"Content-Type": f"multipart/form-data; boundary={boundary}"},
        )
        resp = conn.getresponse()
        conn.close()
        return resp.status == 200
    except Exception as e:
        print(f"  ✗ Upload error: {e}")
        return False


def upload_sprites(ip, sprites_dir):
    """Upload all sprites (JPG and GIF) to the device."""
    sprites_dir = Path(sprites_dir)
    jpg_dir = sprites_dir / "jpg"
    gif_dir = sprites_dir / "gif"

    files_to_upload = []
    for d in [jpg_dir, gif_dir]:
        if d.exists():
            for f in sorted(d.iterdir()):
                if f.suffix in (".jpg", ".gif"):
                    files_to_upload.append(f)

    if not files_to_upload:
        print("ERROR: No sprite files found.")
        return False

    print(f"Uploading {len(files_to_upload)} sprites...")
    for f in files_to_upload:
        ok = upload_file(ip, str(f), f.name)
        size = os.path.getsize(f) // 1024
        print(f"  {'✓' if ok else '✗'} {f.name} ({size}KB)")

    return True


def configure_device(ip):
    """Set theme to Photo Album and set neutral as default."""
    try:
        urllib.request.urlopen(f"http://{ip}/set?theme=2", timeout=3)
        import time; time.sleep(1)
        urllib.request.urlopen(f"http://{ip}/set?img=%2Fimage%2Fadam-neutral.gif", timeout=3)
        print("Set theme to Photo Album, default emote: neutral (animated)")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Upload sprites to holocube")
    parser.add_argument("--sprites-dir", default="./sprites", help="Sprites directory")
    parser.add_argument("--ip", default=None, help="Holocube IP (auto-discovers if not provided)")
    parser.add_argument("--clear", action="store_true", help="Clear existing images first")
    parser.add_argument("--backup-dir", help="Back up existing images before clearing")
    args = parser.parse_args()

    ip = args.ip
    if not ip:
        # Auto-discover
        print("No IP provided, scanning network...")
        from holocube import discover_holocube
        found = discover_holocube()
        if found:
            ip = found[0][0]
            print(f"Using discovered device: {ip}")
        else:
            print("ERROR: No device found. Provide --ip manually.")
            sys.exit(1)

    print(f"Connecting to holocube at {ip}...")
    if not check_device(ip):
        sys.exit(1)

    if args.backup_dir:
        backup_device(ip, args.backup_dir)

    if args.clear:
        clear_device(ip)

    upload_sprites(ip, args.sprites_dir)
    configure_device(ip)

    print("\n✓ Setup complete!")
    with urllib.request.urlopen(f"http://{ip}/space.json", timeout=3) as r:
        space = json.loads(r.read())
    print(f"Storage remaining: {space.get('free', 0) // 1024}KB free")


if __name__ == "__main__":
    main()
