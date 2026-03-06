#!/usr/bin/env python3
"""
Larry — Autonomous TikTok Slideshow Agent
Erstellt und postet täglich TikTok-Karussells für Affiliate-Sites.

Usage:
  python3 larry.py --portal saunamagie --dry-run
  python3 larry.py --portal golfmagie --topic "Die 5 besten Golfschläger 2026"
  python3 larry.py --portal reitherz --auto
  python3 larry.py --all --auto
"""
import argparse, json, os, sys
from pathlib import Path
from datetime import datetime

LARRY_DIR = Path(__file__).parent.parent
CONFIG_PATH = LARRY_DIR / "config.json"
LOG_DIR = LARRY_DIR / "logs"
QUEUE_DIR = LARRY_DIR / "queue"

LOG_DIR.mkdir(exist_ok=True)
QUEUE_DIR.mkdir(exist_ok=True)

def load_config():
    if not CONFIG_PATH.exists():
        example = LARRY_DIR / "config.example.json"
        print(f"⚠️  Config fehlt! Kopiere: cp {example} {CONFIG_PATH}")
        print("   Dann trage OpenAI + Postiz API-Keys ein.")
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        return json.load(f)

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    icons = {"INFO": "ℹ️ ", "OK": "✅", "WARN": "⚠️ ", "ERR": "❌"}
    print(f"[{ts}] {icons.get(level, '')} {msg}", flush=True)

def run_portal(portal_id: str, config: dict, args):
    portal = config["portals"].get(portal_id)
    if not portal:
        log(f"Portal '{portal_id}' nicht in config.json", "ERR")
        return False

    log(f"Larry startet für {portal_id} ({portal['niche']})")

    # Step 1: Research — Trends + Hook-Formel
    from research import get_hook_and_topic
    hook_data = get_hook_and_topic(portal_id, portal, config, dry_run=args.dry_run)
    if not hook_data:
        log("Research fehlgeschlagen", "ERR")
        return False
    log(f"Hook: {hook_data['hook']}", "OK")

    # Step 2: Slide-Konzept generieren
    from research import generate_slide_concept
    concept = generate_slide_concept(hook_data, portal, config, dry_run=args.dry_run)
    log(f"Konzept: {concept['title']}", "OK")

    # Step 3: Bilder generieren
    if args.dry_run:
        log("DRY RUN: Bild-Generierung übersprungen", "WARN")
        image_paths = [f"/tmp/larry_slide_{i+1}.jpg" for i in range(6)]
    else:
        from generate_slides import generate_images
        image_paths = generate_images(concept, portal, config)
        log(f"{len(image_paths)} Bilder generiert", "OK")

    # Step 4: Text Overlays
    if not args.dry_run:
        from overlay import add_overlays
        image_paths = add_overlays(image_paths, concept)
        log("Text-Overlays hinzugefügt", "OK")

    # Step 5: Post erstellen
    post_data = {
        "portal": portal_id,
        "concept": concept,
        "images": image_paths,
        "caption": build_caption(concept, portal),
        "hashtags": portal["hashtags"],
        "created_at": datetime.now().isoformat()
    }

    # Step 6: Posten oder als Draft speichern
    if args.dry_run:
        draft_path = QUEUE_DIR / f"{portal_id}_{datetime.now().strftime('%Y%m%d_%H%M')}_draft.json"
        with open(draft_path, "w") as f:
            json.dump(post_data, f, ensure_ascii=False, indent=2)
        log(f"DRY RUN: Draft gespeichert → {draft_path}", "OK")
    else:
        from postiz import upload_to_tiktok
        result = upload_to_tiktok(post_data, portal, config)
        if result:
            log(f"TikTok Draft erstellt: {result.get('id', '?')}", "OK")
            save_to_log(portal_id, post_data, result)

    return True

def build_caption(concept: dict, portal: dict) -> str:
    """Erstellt TikTok-Caption im Story-Style"""
    lines = []
    lines.append(concept.get("caption_hook", concept["title"]))
    lines.append("")
    lines.append(concept.get("caption_body", ""))
    lines.append("")
    lines.append(f"👉 Mehr auf {portal['site_url']}")
    lines.append("")
    lines.append(" ".join(portal["hashtags"][:5]))
    return "\n".join(lines)

def save_to_log(portal_id: str, post: dict, result: dict):
    log_file = LOG_DIR / "performance.json"
    data = []
    if log_file.exists():
        with open(log_file) as f:
            data = json.load(f)
    data.append({
        "portal": portal_id,
        "post_id": result.get("id"),
        "title": post["concept"]["title"],
        "hook": post["concept"]["hook"],
        "posted_at": datetime.now().isoformat(),
        "views": 0,
        "likes": 0,
        "comments": 0,
        "shares": 0
    })
    with open(log_file, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Larry — Autonomous TikTok Agent")
    parser.add_argument("--portal", help="Portal ID: saunamagie, golfmagie, reitherz")
    parser.add_argument("--all", action="store_true", help="Alle Portale")
    parser.add_argument("--topic", help="Optionales Thema vorgeben")
    parser.add_argument("--dry-run", action="store_true", help="Ohne echte API-Calls")
    parser.add_argument("--auto", action="store_true", help="Autonomer Modus (2x täglich)")
    args = parser.parse_args()

    config = load_config()

    # Prüfe ob Config befüllt ist
    if not args.dry_run:
        if config.get("openai_api_key", "").startswith("sk-YOUR"):
            log("OpenAI API-Key fehlt in config.json!", "ERR")
            sys.exit(1)
        if config.get("postiz_api_key", "") == "YOUR_POSTIZ_KEY":
            log("Postiz API-Key fehlt in config.json!", "ERR")
            sys.exit(1)

    portals = list(config["portals"].keys()) if args.all else [args.portal]

    if not portals[0]:
        parser.print_help()
        sys.exit(1)

    log(f"Larry ist wach 🤖 | Portale: {', '.join(portals)} | Dry-Run: {args.dry_run}")

    for portal_id in portals:
        success = run_portal(portal_id, config, args)
        if success:
            log(f"[{portal_id}] Post erstellt ✅", "OK")
        else:
            log(f"[{portal_id}] Fehler beim Post", "ERR")

if __name__ == "__main__":
    main()
