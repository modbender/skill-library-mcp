#!/usr/bin/env python3
"""
Interactive onboarding for holocube-emotes.
Guides through device discovery, character creation, and setup.
"""

import sys
import os
import json
import time
import urllib.request
import concurrent.futures
import socket
from pathlib import Path


def print_banner():
    print("""
╔══════════════════════════════════════╗
║     🤖 Holocube Emotes Setup 🤖     ║
║  Give your AI a face on the cube!   ║
╚══════════════════════════════════════╝
""")


def discover_devices():
    """Scan local subnet for GeekMagic devices."""
    def check(ip):
        try:
            with urllib.request.urlopen(f"http://{ip}/v.json", timeout=1) as r:
                data = json.loads(r.read())
                if "m" in data:
                    return ip, data
        except:
            pass
        return None, None

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
    subnet = ".".join(local_ip.split(".")[:3])

    print(f"Scanning {subnet}.0/24 for holocube devices...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as ex:
        futures = {ex.submit(check, f"{subnet}.{i}"): i for i in range(1, 255)}
        found = []
        for f in concurrent.futures.as_completed(futures):
            ip, data = f.result()
            if ip:
                found.append((ip, data))
    return found


CHARACTER_PRESETS = {
    "robot": {
        "name": "Holographic Robot",
        "desc": "A glowing holographic robot head floating in pure black void. Cyan and blue neon wireframe style. Luminous eyes. Ethereal digital particles dissolving around it. No background elements, just black. Hologram aesthetic, high contrast.",
    },
    "cat": {
        "name": "Neon Cat",
        "desc": "A glowing holographic cat face floating in pure black void. Purple and magenta neon wireframe style. Glowing eyes with slit pupils. Whiskers made of light. No background elements, just black. Hologram aesthetic, high contrast.",
    },
    "skull": {
        "name": "Cyber Skull",
        "desc": "A glowing holographic skull floating in pure black void. Green and teal neon wireframe style. Glowing eye sockets with flickering flames. No background elements, just black. Hologram aesthetic, high contrast.",
    },
    "alien": {
        "name": "Alien Visitor",
        "desc": "A glowing holographic alien head floating in pure black void. Green and cyan bioluminescent style. Large oval eyes that glow. Smooth elongated head. No background elements, just black. Hologram aesthetic, high contrast.",
    },
    "ghost": {
        "name": "Friendly Ghost",
        "desc": "A glowing holographic friendly ghost floating in pure black void. White and pale blue ethereal glow. Round cute eyes. Wispy trailing bottom. No background elements, just black. Hologram aesthetic, high contrast.",
    },
}


def pick_character():
    """Let user choose or describe a character."""
    print("\n🎨 Choose your character:\n")
    presets = list(CHARACTER_PRESETS.items())
    for i, (key, preset) in enumerate(presets, 1):
        print(f"  {i}. {preset['name']}")
    print(f"  {len(presets) + 1}. Custom (describe your own)")

    while True:
        choice = input(f"\nPick [1-{len(presets) + 1}]: ").strip()
        try:
            idx = int(choice)
            if 1 <= idx <= len(presets):
                key, preset = presets[idx - 1]
                print(f"\n✓ {preset['name']} selected!")
                return preset["desc"], preset["name"]
            elif idx == len(presets) + 1:
                print("\nDescribe your character (holographic style on black background):")
                print("Example: 'A glowing dragon head with fire eyes'")
                desc = input("> ").strip()
                if desc:
                    # Append holocube style guidance
                    full_desc = (
                        f"A glowing holographic {desc} floating in pure black void. "
                        f"Neon wireframe style. No background elements, just black. "
                        f"Hologram aesthetic, high contrast."
                    )
                    name = input("Give it a name: ").strip() or "Custom"
                    return full_desc, name
        except ValueError:
            pass
        print("Invalid choice, try again.")


def generate_sprites(character_desc, output_dir, api_key):
    """Generate all emote sprites."""
    from generate_sprites import EMOTES, find_nano_banana, generate_base, generate_emote
    import shutil

    script = find_nano_banana()
    if not script:
        print("ERROR: nano-banana-pro skill not found.")
        return False

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n⏳ Generating base character (this takes ~15 seconds)...")
    base = generate_base(output_dir, character_desc, api_key, script)
    if not base:
        return False

    shutil.copy(base, output_dir / "neutral.png")

    # Only generate the 5 non-neutral emotes
    emotes_to_gen = {k: v for k, v in EMOTES.items() if k != "neutral"}
    total = len(emotes_to_gen)

    print(f"\n⏳ Generating {total} emote variations (~15 sec each)...")
    for i, (emote, desc) in enumerate(emotes_to_gen.items(), 1):
        print(f"  [{i}/{total}] {emote}...")
        generate_emote(base, emote, desc, output_dir, character_desc, api_key, script)

    return True


def convert_and_upload(sprites_dir, ip):
    """Convert sprites to animated GIFs and upload to device."""
    from generate_sprites import convert_to_holocube

    sprites_dir = Path(sprites_dir)
    print("\n🎬 Creating animations...")
    convert_to_holocube(sprites_dir)

    gif_dir = sprites_dir / "gif"

    print(f"\n📡 Uploading to holocube at {ip}...")

    # Clear device
    urllib.request.urlopen(f"http://{ip}/set?clear=image", timeout=5)
    print("  Cleared old images")
    time.sleep(1)

    # Upload GIFs
    import http.client
    for f in sorted(gif_dir.iterdir()):
        if not f.suffix == ".gif":
            continue
        with open(f, "rb") as fh:
            data = fh.read()
        boundary = "----HolocubeUpload"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{f.name}"\r\n'
            f"Content-Type: image/gif\r\n\r\n"
        ).encode() + data + f"\r\n--{boundary}--\r\n".encode()
        conn = http.client.HTTPConnection(ip, timeout=10)
        conn.request("POST", "/doUpload?dir=/image", body,
                      {"Content-Type": f"multipart/form-data; boundary={boundary}"})
        resp = conn.getresponse()
        conn.close()
        size = len(data) // 1024
        print(f"  {'✓' if resp.status == 200 else '✗'} {f.name} ({size}KB)")

    # Set theme and default
    urllib.request.urlopen(f"http://{ip}/set?theme=2", timeout=3)
    time.sleep(1)
    urllib.request.urlopen(f"http://{ip}/set?img=%2Fimage%2Fadam-neutral.gif", timeout=3)
    print("\n  Set to Photo Album, default: neutral")

    with urllib.request.urlopen(f"http://{ip}/space.json", timeout=3) as r:
        space = json.loads(r.read())
    print(f"  Storage: {space.get('free', 0) // 1024}KB free")


def get_api_key():
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
        key = config.get("skills", {}).get("entries", {}).get("nano-banana-pro", {}).get("apiKey", "")
        if key:
            return key
    return None


def main():
    print_banner()

    # Step 1: Find device
    print("Step 1: Find your holocube\n")
    found = discover_devices()

    if found:
        if len(found) == 1:
            ip = found[0][0]
            info = found[0][1]
            print(f"  Found: {info.get('m', '?')} at {ip}")
            confirm = input("  Use this device? [Y/n]: ").strip().lower()
            if confirm == "n":
                ip = input("  Enter IP manually: ").strip()
        else:
            print("  Multiple devices found:")
            for i, (dev_ip, info) in enumerate(found, 1):
                print(f"    {i}. {info.get('m', '?')} at {dev_ip}")
            choice = input(f"  Pick [1-{len(found)}]: ").strip()
            ip = found[int(choice) - 1][0]
    else:
        print("  No devices found automatically.")
        ip = input("  Enter holocube IP address: ").strip()

    print(f"\n✓ Using device at {ip}")

    # Step 2: Pick character
    print("\nStep 2: Design your character")
    character_desc, char_name = pick_character()

    # Step 3: Check API key
    api_key = get_api_key()
    if not api_key:
        print("\n⚠️  No Gemini API key found.")
        api_key = input("Enter your GEMINI_API_KEY: ").strip()
        if not api_key:
            print("Cannot generate sprites without an API key.")
            sys.exit(1)

    # Step 4: Generate
    print(f"\nStep 3: Generating '{char_name}' sprite kit")
    print("This will take 1-2 minutes...\n")

    sprites_dir = Path.home() / ".openclaw" / "workspace" / "assets" / "holocube-sprites"
    if not generate_sprites(character_desc, sprites_dir, api_key):
        print("Sprite generation failed.")
        sys.exit(1)

    # Step 5: Convert and upload
    print("\nStep 4: Animating and uploading")
    convert_and_upload(sprites_dir, ip)

    # Done
    print(f"""
╔══════════════════════════════════════╗
║          ✅ Setup Complete!          ║
╠══════════════════════════════════════╣
║  Your holocube now has a face!      ║
║                                     ║
║  Control it:                        ║
║    python3 holocube.py happy        ║
║    python3 holocube.py thinking     ║
║    python3 holocube.py --auto       ║
║    python3 holocube.py --discover   ║
║                                     ║
║  Device: {ip:>25s}  ║
║  Character: {char_name:>22s}  ║
╚══════════════════════════════════════╝
""")


if __name__ == "__main__":
    main()
