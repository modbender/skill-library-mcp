#!/usr/bin/env python3
"""
Larry — Research Module
Generiert Hooks + Slide-Konzepte via Claude CLI (kein API-Key nötig).
Analysiert vergangene Performance für Hook-Optimierung.
"""
import json, subprocess, sys
from pathlib import Path
from datetime import datetime

LARRY_DIR = Path(__file__).parent.parent

# Hook-Formeln die TikTok-Algorithmus lieben (von Larry gelernt)
HOOK_TEMPLATES = [
    "Die {N} Fehler die {ZIELGRUPPE} bei {THEMA} machen",
    "{N} Dinge über {THEMA} die niemand dir sagt",
    "Warum {FALSCHANNAHME} falsch ist 🚫",
    "Ich hätte das früher wissen sollen: {TIPP}",
    "Das passiert wenn du {AKTION} — Test nach {ZEITRAUM}",
    "POV: Du kaufst deinen ersten {PRODUKT}",
    "{N} Zeichen dass du einen besseren {PRODUKT} brauchst",
    "So wählen Profis ihren {PRODUKT} aus",
]

NICHE_TOPICS = {
    "saunamagie": [
        "Saunaaufguss richtig machen",
        "Infrarotsauna vs. finnische Sauna",
        "Eisbad nach der Sauna — Vorteile",
        "Sauna für Anfänger: diese Fehler vermeiden",
        "Die besten Saunaöle für Zuhause",
        "Fasssauna im Garten — lohnt es sich?",
        "Wie oft in die Sauna ist optimal?",
        "Saunatuch Größe — was ist richtig?",
    ],
    "golfmagie": [
        "Golfschläger für Anfänger — was kaufen?",
        "Diese Fehler machen Golf-Anfänger immer",
        "Golfschuhe — worauf wirklich achten?",
        "Driver richtig wählen — Loft und Flex erklärt",
        "Golfball Unterschiede — macht das wirklich was?",
        "Golf Trolley vs. Caddy Bag — was lohnt sich?",
        "Handicap verbessern — 5 Tipps die wirklich helfen",
        "Golfreise: Diese Länder sind ein Muss",
    ],
    "reitherz": [
        "Sattel kaufen — die 3 wichtigsten Punkte",
        "Reithelm richtig anpassen — Sicherheit first",
        "Reithose für Anfänger — was man wissen muss",
        "Pferd putzen — vollständige Routine",
        "Reitstiefel vs. Kurzstiefel — was ist besser?",
        "Pferdedecke Größe bestimmen — so geht's",
        "Erste Reitstunde — das erwartet dich",
        "Sattel anpassen lassen — wie oft nötig?",
    ]
}

def get_best_hooks(portal_id: str) -> list:
    """Liest Performance-Log und gibt erfolgreiche Hook-Formeln zurück"""
    log_file = LARRY_DIR / "logs" / "performance.json"
    if not log_file.exists():
        return HOOK_TEMPLATES[:3]

    with open(log_file) as f:
        data = json.load(f)

    portal_posts = [p for p in data if p.get("portal") == portal_id and p.get("views", 0) > 0]
    if not portal_posts:
        return HOOK_TEMPLATES[:3]

    # Top-Hooks nach Views sortieren
    portal_posts.sort(key=lambda x: x.get("views", 0), reverse=True)
    return [p["hook"] for p in portal_posts[:5]]

def get_hook_and_topic(portal_id: str, portal: dict, config: dict, dry_run: bool = False) -> dict:
    """Generiert Hook + Thema via Claude"""
    topics = NICHE_TOPICS.get(portal_id, [])
    best_hooks = get_best_hooks(portal_id)

    # Rotation: nächstes unbenutztes Topic
    log_file = LARRY_DIR / "logs" / "used_topics.json"
    used = []
    if log_file.exists():
        with open(log_file) as f:
            used = json.load(f).get(portal_id, [])

    available = [t for t in topics if t not in used]
    if not available:
        available = topics  # Reset wenn alle durch
        used = []

    topic = available[0]

    # Topic als benutzt markieren
    all_used = {}
    if log_file.exists():
        with open(log_file) as f:
            all_used = json.load(f)
    all_used[portal_id] = used + [topic]
    with open(log_file, "w") as f:
        json.dump(all_used, f, ensure_ascii=False, indent=2)

    if dry_run:
        return {
            "hook": f"Die 5 Fehler die Anfänger bei {topic.split('—')[0].strip()} machen",
            "topic": topic,
            "article_url": f"{portal['site_url']}/{portal_id}/"
        }

    # Claude generiert den besten Hook für das Topic
    prompt = f"""Du erstellst TikTok-Hooks für {portal['niche']}.

Thema: {topic}
Zielgruppe: Deutsche TikTok-Nutzer (18–45) die sich für {portal['niche']} interessieren

Erfolgreiche Hook-Formeln aus der Vergangenheit:
{chr(10).join(f"- {h}" for h in best_hooks)}

Erstelle einen neuen viralen Hook (max 60 Zeichen) der:
- Neugier weckt oder ein Problem anspricht
- Auf Deutsch ist
- Zum Thema passt

Antworte NUR mit dem Hook-Text, nichts weiter."""

    try:
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True, text=True, timeout=30
        )
        hook = result.stdout.strip().strip('"').strip("'")
    except Exception:
        hook = f"Das musst du über {topic.split('—')[0].strip()} wissen"

    return {
        "hook": hook,
        "topic": topic,
        "article_url": f"{portal['site_url']}/{portal_id}/"
    }

def generate_slide_concept(hook_data: dict, portal: dict, config: dict, dry_run: bool = False) -> dict:
    """Generiert vollständiges 6-Slide-Konzept"""

    if dry_run:
        return {
            "title": hook_data["hook"],
            "hook": hook_data["hook"],
            "topic": hook_data["topic"],
            "slides": [
                {"text": hook_data["hook"], "detail": "Hook-Slide"},
                {"text": "Punkt 1", "detail": "Erster Tipp"},
                {"text": "Punkt 2", "detail": "Zweiter Tipp"},
                {"text": "Punkt 3", "detail": "Dritter Tipp"},
                {"text": "Punkt 4", "detail": "Vierter Tipp"},
                {"text": f"Mehr auf {portal['site_url']}", "detail": "CTA"},
            ],
            "image_style": portal.get("style", "lifestyle photography"),
            "caption_hook": hook_data["hook"],
            "caption_body": f"Alles über {hook_data['topic'].split('—')[0].strip()} auf {portal['site_url']}"
        }

    prompt = f"""Du erstellst ein TikTok Slideshow-Konzept für {portal['niche']}.

Hook: {hook_data['hook']}
Thema: {hook_data['topic']}
Style: {portal.get('style', 'lifestyle')}

Erstelle exakt 6 Slides. Antworte als JSON:
{{
  "title": "Hook-Text",
  "slides": [
    {{"text": "HOOK (max 8 Wörter, großer Text)", "detail": "Was auf dem Bild zu sehen ist"}},
    {{"text": "Punkt 1 (max 6 Wörter)", "detail": "Bild-Beschreibung"}},
    {{"text": "Punkt 2 (max 6 Wörter)", "detail": "Bild-Beschreibung"}},
    {{"text": "Punkt 3 (max 6 Wörter)", "detail": "Bild-Beschreibung"}},
    {{"text": "Punkt 4 (max 6 Wörter)", "detail": "Bild-Beschreibung"}},
    {{"text": "👉 Link in Bio", "detail": "Einladender CTA mit Site-URL"}}
  ],
  "caption_hook": "Erste Zeile der Caption (Neugier wecken)",
  "caption_body": "2-3 Sätze Story-Style, natürliche Erwähnung der Site"
}}"""

    try:
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True, text=True, timeout=45
        )
        raw = result.stdout.strip()
        # JSON extrahieren
        start = raw.find("{")
        end = raw.rfind("}") + 1
        concept = json.loads(raw[start:end])
        concept["hook"] = hook_data["hook"]
        concept["topic"] = hook_data["topic"]
        concept["image_style"] = portal.get("style", "lifestyle photography")
        return concept
    except Exception as e:
        print(f"[WARN] Concept-Generierung Fallback: {e}")
        return {
            "title": hook_data["hook"],
            "hook": hook_data["hook"],
            "topic": hook_data["topic"],
            "slides": [{"text": f"Slide {i+1}", "detail": "lifestyle photo"} for i in range(6)],
            "image_style": portal.get("style", "lifestyle"),
            "caption_hook": hook_data["hook"],
            "caption_body": ""
        }
