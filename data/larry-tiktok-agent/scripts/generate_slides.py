#!/usr/bin/env python3
"""
Larry — Image Generation
Generiert 6 konsistente Bilder via NVIDIA FLUX.1-schnell (€0, kostenlos).
Basis-Szene bleibt über alle Slides gleich → konsistenter Look.
"""
import base64 as _b64, json, os, requests, time
from io import BytesIO
from pathlib import Path
from datetime import datetime

# FLUX.1-dev: bessere Qualität, ~0.5s, realistischer
NVIDIA_ENDPOINT = "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.1-dev"
NVIDIA_STEPS = 28

def generate_images(concept: dict, portal: dict, config: dict) -> list:
    """Generiert 6 Slide-Bilder via NVIDIA FLUX.1-schnell. Gibt Liste von Pfaden zurück."""
    api_key = config.get("nvidia_api_key") or os.environ.get("NVIDIA_API_KEY", "")
    if not api_key:
        raise ValueError("Kein NVIDIA_API_KEY in config.json oder Umgebungsvariable")

    output_dir = Path("/tmp") / f"larry_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_dir.mkdir(parents=True, exist_ok=True)

    base_scene = _build_base_scene(concept, portal)
    slides = concept.get("slides", [])
    image_paths = []

    print(f"  Generiere {len(slides)} Bilder via NVIDIA FLUX.1-schnell...", flush=True)

    for i, slide in enumerate(slides):
        prompt = _build_image_prompt(base_scene, slide, portal, i)
        print(f"  Slide {i+1}/6: {slide['text'][:40]}...", flush=True)

        img_path = output_dir / f"slide_{i+1:02d}.png"
        success = _generate_single(prompt, img_path, api_key)

        if not success:
            print(f"  ⚠️  Slide {i+1} NVIDIA fehlgeschlagen — Fallback-Bild", flush=True)
            _create_fallback_image(img_path, slide["text"])

        image_paths.append(str(img_path))
        time.sleep(0.5)  # kurze Pause zwischen Requests

    print(f"  ✅ Alle {len(image_paths)} Bilder in {output_dir}", flush=True)
    return image_paths


def _generate_single(prompt: str, out_path: Path, api_key: str) -> bool:
    """
    FLUX.1-dev via NVIDIA. Response: JSON → base64 JPEG → BytesIO → Zoom+Crop Portrait.
    Speichert als JPEG (PNG-Konvertierung via Datei-Pfad erzeugt schwarze Bilder).
    """
    from PIL import Image, ImageStat

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"prompt": prompt, "width": 1024, "height": 1024, "steps": NVIDIA_STEPS}

    try:
        resp = requests.post(NVIDIA_ENDPOINT, headers=headers, json=payload, timeout=120)
        if resp.status_code == 200:
            raw_bytes = _b64.b64decode(resp.json()["artifacts"][0]["base64"])
            img = Image.open(BytesIO(raw_bytes)).convert("RGB")

            # Qualitätscheck — schwarz = Prompt zu lang oder Fehler
            from PIL import ImageStat
            mean = sum(ImageStat.Stat(img).mean) / 3
            if mean < 5:
                print(f"    → ⚠️ Bild fast schwarz (Mean {mean:.1f}) — Prompt zu komplex?", flush=True)
                return False

            # Zoom+Crop: 1024×1024 → 1024×1820 Portrait (kein schwarze Balken)
            portrait = _zoom_crop_portrait(img, target_w=1024, target_h=1820)

            # Als JPEG speichern (nicht PNG — führt zu schwarzen Bildern)
            jpg_path = out_path.with_suffix(".jpg")
            portrait.save(str(jpg_path), "JPEG", quality=95)
            out_path.unlink(missing_ok=True)
            jpg_path.rename(out_path)  # Umbenennen auf .png für Kompatibilität

            print(f"    → {img.size} → 1024×1820 Portrait ✅ (Mean {mean:.1f})", flush=True)
            return True
        else:
            print(f"    → HTTP {resp.status_code}: {resp.text[:120]}", flush=True)
    except Exception as e:
        print(f"    → Fehler: {e}", flush=True)

    return False


def _zoom_crop_portrait(img, target_w: int = 1024, target_h: int = 1820):
    """Skaliert 1:1 Bild auf Portrait-Format via Zoom+Center-Crop (kein schwarze Balken)."""
    from PIL import Image
    w, h = img.size
    # Hochskalieren auf Zielhöhe
    scaled = img.resize((target_h, target_h), Image.LANCZOS)
    # Mittig croppen auf Zielbreite
    left = (target_h - target_w) // 2
    return scaled.crop((left, 0, left + target_w, target_h))


def _letterbox_to_portrait(img_path: Path):
    """
    Konvertiert 1:1 Bild zu 9:16 Portrait via Zoom+Center-Crop.
    Kein schwarze Balken — Bild füllt den gesamten Frame.
    """
    try:
        from PIL import Image
        img = Image.open(img_path).convert("RGB")
        w, h = img.size  # 1024×1024

        target_w, target_h = w, int(w * 16 / 9)  # 1024×1820

        # Auf Zielhöhe hochskalieren (Zoom)
        scaled = img.resize((target_h, target_h), Image.LANCZOS)  # 1820×1820

        # Mittig auf Zielbreite croppen
        left = (target_h - target_w) // 2  # (1820-1024)//2 = 398
        portrait = scaled.crop((left, 0, left + target_w, target_h))  # 1024×1820

        portrait.save(str(img_path))
    except ImportError:
        pass


def _build_base_scene(concept: dict, portal: dict) -> str:
    """
    Kurze Basis-Szene (max ~15 Wörter) — FLUX.1-schnell bricht bei langen Prompts ab.
    """
    style = portal.get("style", "lifestyle photography")
    topic = concept.get("topic", "")

    # Max ~12 Wörter — FLUX.1-dev bricht bei >20 Wörtern ab → schwarz
    scene_templates = {
        "sauna": "Finnish sauna, wooden benches, hot stones, steam, warm amber light",
        "golf": "golf course fairway, green grass, blue sky, morning sunshine",
        "reit": "horse stable interior, wooden stall, warm window light, straw",
        "boot": "german lake, wooden dock, calm water, morning mist",
        "wolle": "wool yarn, soft pastel colors, warm side light, cozy",
    }

    for key, template in scene_templates.items():
        if key in style.lower() or key in topic.lower():
            return template

    return " ".join(style.split()[:8])


def _build_image_prompt(base_scene: str, slide: dict, portal: dict, index: int) -> str:
    """
    Gesamtprompt STRIKT unter 20 Wörter — FLUX.1-dev gibt sonst schwarzes Bild.
    base_scene (~10 Wörter) + detail (~4 Wörter) + style (2 Wörter) = ~16 Wörter.
    """
    detail = slide.get("detail", "")
    detail_short = " ".join(detail.split()[:4])  # max 4 Wörter
    suffix = "dramatic light" if index == 0 else ("warm light" if index == 5 else "sharp focus")
    return f"{base_scene}, {detail_short}, {suffix}"


def _create_fallback_image(path: Path, text: str):
    """Erstellt dunkles Fallback-Bild wenn API komplett fehlschlägt"""
    try:
        from PIL import Image, ImageDraw
        img = Image.new("RGB", (1024, 1792), color=(30, 30, 30))
        draw = ImageDraw.Draw(img)
        draw.text((512, 896), text[:50], fill=(180, 180, 180), anchor="mm")
        img.save(str(path))
    except ImportError:
        path.write_bytes(b"")
