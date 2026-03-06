"""One-time script to generate the tray icon and fallback activation chime."""

import struct
import wave
import math
from pathlib import Path

ASSETS_DIR = Path(__file__).parent / "assets"
ASSETS_DIR.mkdir(exist_ok=True)


def generate_chime():
    """Generate a pleasant two-tone activation chime (WAV)."""
    sample_rate = 44100
    duration = 0.25  # seconds per tone
    volume = 0.4

    samples = []

    # Tone 1: C5 (523 Hz)
    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        env = min(t * 20, 1.0) * max(0, 1.0 - (t / duration) * 0.5)
        val = volume * env * math.sin(2 * math.pi * 523 * t)
        samples.append(int(val * 32767))

    # Tone 2: E5 (659 Hz)
    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        env = min(t * 20, 1.0) * max(0, 1.0 - (t / duration))
        val = volume * env * math.sin(2 * math.pi * 659 * t)
        samples.append(int(val * 32767))

    chime_path = ASSETS_DIR / "chime.wav"
    with wave.open(str(chime_path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack(f"<{len(samples)}h", *samples))

    print(f"Created {chime_path}")


def generate_icon():
    """Generate a simple 64x64 PNG tray icon."""
    try:
        from PIL import Image, ImageDraw

        size = 64
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Dark circle background
        draw.ellipse([4, 4, 60, 60], fill=(30, 30, 40, 255))

        # Microphone shape (simplified)
        draw.rounded_rectangle([24, 14, 40, 34], radius=6, fill=(0, 200, 130, 255))
        draw.line([32, 34, 32, 44], fill=(0, 200, 130, 255), width=3)
        draw.arc([22, 30, 42, 48], start=0, end=180, fill=(0, 200, 130, 255), width=2)
        draw.line([26, 48, 38, 48], fill=(0, 200, 130, 255), width=2)

        icon_path = ASSETS_DIR / "icon.png"
        img.save(str(icon_path))
        print(f"Created {icon_path}")

    except ImportError:
        import zlib

        def create_minimal_png(color=(0, 180, 120)):
            width, height = 16, 16
            raw_data = b""
            for _ in range(height):
                raw_data += b"\x00"
                for _ in range(width):
                    raw_data += bytes(color) + b"\xff"

            compressed = zlib.compress(raw_data)

            png = b"\x89PNG\r\n\x1a\n"
            ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
            ihdr_crc = zlib.crc32(b"IHDR" + ihdr_data) & 0xFFFFFFFF
            png += struct.pack(">I", 13) + b"IHDR" + ihdr_data + struct.pack(">I", ihdr_crc)
            idat_crc = zlib.crc32(b"IDAT" + compressed) & 0xFFFFFFFF
            png += struct.pack(">I", len(compressed)) + b"IDAT" + compressed + struct.pack(">I", idat_crc)
            iend_crc = zlib.crc32(b"IEND") & 0xFFFFFFFF
            png += struct.pack(">I", 0) + b"IEND" + struct.pack(">I", iend_crc)
            return png

        icon_path = ASSETS_DIR / "icon.png"
        icon_path.write_bytes(create_minimal_png())
        print(f"Created {icon_path} (minimal placeholder — install Pillow for a better icon)")


if __name__ == "__main__":
    generate_chime()
    generate_icon()
    print("Done! Assets generated in assets/")
