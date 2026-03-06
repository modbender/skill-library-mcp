#!/usr/bin/env python3
"""
setup.py - Wizard interactif d'initialisation et de gestion du skill veille.

Modes :
  python3 setup.py                   # wizard initial (creation config + dirs)
  python3 setup.py --manage-sources  # gestion interactive des sources RSS
  python3 setup.py --manage-outputs  # gestion interactive des sorties (dispatch)
  python3 setup.py --setup-cron      # configure le cron job quotidien (ecrit cron.json)
  python3 setup.py --non-interactive

Actions du wizard initial :
  1. Cree ~/.openclaw/config/veille/ et ~/.openclaw/data/veille/
  2. Copie config.example.json -> config.json si absent
  3. Propose hours_lookback, max_articles_per_source, language, timezone

Actions du menu sources :
  - Affiche toutes les sources disponibles (actives + desactivees)
  - Permet de basculer chaque source entre active et desactivee
  - Sauvegarde le config.json mis a jour

Actions du menu outputs :
  - Affiche les sorties configurees (telegram_bot, mail-client, nextcloud, file)
  - Permet d'activer/desactiver, ajouter ou supprimer des sorties
  - Sauvegarde le config.json mis a jour

Actions du wizard cron :
  - Demande heure/frequence, modele LLM, chat_id Telegram
  - Ecrit cron.json dans le repertoire du skill (gitignore)
  - L agent lit cron.json + references/cron_prompt.md et cree le cron OpenClaw
"""

import argparse
import json
import sys
from pathlib import Path

# ---- Paths ------------------------------------------------------------------

SKILL_DIR    = Path(__file__).resolve().parent.parent
_CONFIG_DIR  = Path.home() / ".openclaw" / "config" / "veille"
_DATA_DIR    = Path.home() / ".openclaw" / "data" / "veille"
CONFIG_FILE  = _CONFIG_DIR / "config.json"
EXAMPLE_FILE = SKILL_DIR / "config.example.json"


# ---- Helpers ----------------------------------------------------------------


def _ask(prompt: str, default: str, interactive: bool) -> str:
    if not interactive:
        return default
    try:
        answer = input(f"{prompt} [{default}]: ").strip()
        return answer if answer else default
    except (EOFError, KeyboardInterrupt):
        print()
        return default


def _confirm(prompt: str, interactive: bool) -> bool:
    if not interactive:
        return False
    try:
        answer = input(f"{prompt} [y/N]: ").strip().lower()
        return answer in ("y", "yes", "o", "oui")
    except (EOFError, KeyboardInterrupt):
        print()
        return False


def _load_json(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[WARN] Could not read {path}: {e}", file=sys.stderr)
    return {}


def _save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _real_sources(sources: dict) -> dict:
    """Retourne les sources sans les cles _comment_*."""
    return {k: v for k, v in sources.items() if not k.startswith("_")}


# ---- Initial setup ----------------------------------------------------------


def run_setup(interactive: bool = True):
    print()
    print("=" * 52)
    print("  OpenClaw Skill Veille - Setup")
    print("=" * 52)

    # Step 1: Create directories
    print()
    print("[1/3] Creating directories...")
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"  OK  {_CONFIG_DIR}")
    print(f"  OK  {_DATA_DIR}")

    # Load example config as base
    if not EXAMPLE_FILE.exists():
        print(f"\n[ERROR] config.example.json not found at {EXAMPLE_FILE}", file=sys.stderr)
        sys.exit(1)

    example_cfg = _load_json(EXAMPLE_FILE)

    # Step 2: Configuration options
    print()
    print("[2/3] Configuration...")
    default_hours = str(example_cfg.get("hours_lookback", 24))
    hours_str = _ask("  Lookback window (hours)", default_hours, interactive)
    try:
        hours = int(hours_str)
    except ValueError:
        hours = int(default_hours)
    example_cfg["hours_lookback"] = hours

    default_max = str(example_cfg.get("max_articles_per_source", 20))
    max_str = _ask("  Max articles per source", default_max, interactive)
    try:
        max_arts = int(max_str)
    except ValueError:
        max_arts = int(default_max)
    example_cfg["max_articles_per_source"] = max_arts

    # Language
    default_lang = example_cfg.get("language", "fr")
    lang = _ask("  Language (fr / en)", default_lang, interactive).strip().lower()
    if lang not in ("fr", "en"):
        print(f"  [WARN] Unknown language '{lang}', using 'fr'")
        lang = "fr"
    example_cfg["language"] = lang

    # Timezone
    system_tz = ""
    try:
        etc_tz = Path("/etc/timezone")
        if etc_tz.exists():
            system_tz = etc_tz.read_text(encoding="utf-8").strip()
    except Exception:
        pass
    default_tz = example_cfg.get("timezone", system_tz or "UTC")
    tz_val = _ask("  Timezone (e.g. Europe/Paris)", default_tz, interactive).strip()
    example_cfg["timezone"] = tz_val or default_tz

    # Step 3: Write config
    print()
    print("[3/3] Writing config file...")
    if CONFIG_FILE.exists():
        print(f"  [WARN] Config already exists: {CONFIG_FILE}")
        if _confirm("  Overwrite with defaults?", interactive):
            _save_json(CONFIG_FILE, example_cfg)
            print(f"  OK  {CONFIG_FILE} (overwritten)")
        else:
            print(f"  SKIP {CONFIG_FILE} (kept existing)")
    else:
        _save_json(CONFIG_FILE, example_cfg)
        print(f"  OK  {CONFIG_FILE} (created)")

    # Summary
    print()
    print("=" * 52)
    print("  Setup complete!")
    print()
    print(f"  Config : {CONFIG_FILE}")
    print(f"  Data   : {_DATA_DIR}/")
    print()
    print("  Next steps:")
    print("    python3 init.py                          # validate")
    print("    python3 setup.py --manage-sources        # toggle RSS feeds")
    print("    python3 veille.py fetch --hours 24")
    print("=" * 52)
    print()


# ---- Source management ------------------------------------------------------


def _build_catalog(example_cfg: dict, user_cfg: dict) -> list:
    """
    Construit le catalogue complet des sources avec leur statut.
    Retourne une liste de dicts :
      { "name": str, "url": str, "active": bool, "category": str }
    """
    catalog = []
    current_category = "General"

    example_sources  = example_cfg.get("sources", {})
    example_disabled = example_cfg.get("sources_disabled", {})
    user_sources     = user_cfg.get("sources", {})
    user_disabled    = user_cfg.get("sources_disabled", {})

    # Active in user config: source is in user sources (non-comment keys)
    user_active_names = set(_real_sources(user_sources).keys())

    # All known sources = example sources + example disabled + user custom
    all_known: dict = {}

    for name, val in example_sources.items():
        if name.startswith("_comment"):
            # Extract category label from comment value
            current_category = val.strip("- ").strip()
            continue
        all_known[name] = {"url": val, "category": current_category}

    current_category = "Autres"
    for name, val in example_disabled.items():
        if name.startswith("_comment"):
            current_category = val.strip("- ").strip()
            continue
        if name.startswith("_"):
            continue
        if name not in all_known:
            all_known[name] = {"url": val, "category": current_category}

    # User custom sources not in example
    for name, val in _real_sources(user_sources).items():
        if name not in all_known:
            all_known[name] = {"url": val, "category": "Custom"}
    for name, val in _real_sources(user_disabled).items():
        if name not in all_known:
            all_known[name] = {"url": val, "category": "Custom"}

    # Build catalog list
    for name, info in all_known.items():
        catalog.append({
            "name":     name,
            "url":      info["url"],
            "active":   name in user_active_names,
            "category": info["category"],
        })

    return catalog


def _display_catalog(catalog: list):
    """Affiche le catalogue avec numero, statut et categorie."""
    current_cat = None
    for i, entry in enumerate(catalog):
        if entry["category"] != current_cat:
            current_cat = entry["category"]
            print(f"\n  --- {current_cat} ---")
        status = "[ON] " if entry["active"] else "[off]"
        print(f"  {i + 1:2d}. {status} {entry['name']}")


def _apply_catalog(catalog: list, example_cfg: dict, user_cfg: dict) -> dict:
    """
    Reconstruit sources et sources_disabled a partir du catalogue.
    Preserve les cles _comment_* de l'exemple dans sources.
    """
    active_names   = {e["name"] for e in catalog if e["active"]}
    inactive_names = {e["name"] for e in catalog if not e["active"]}

    all_urls = {e["name"]: e["url"] for e in catalog}

    # Rebuild sources: keep _comment_ keys in order from example, add active
    new_sources: dict = {}
    example_sources = example_cfg.get("sources", {})
    # Preserve comment keys and order from example, include active sources
    for name, val in example_sources.items():
        if name.startswith("_comment"):
            new_sources[name] = val
        elif name in active_names:
            new_sources[name] = all_urls[name]

    # Custom active sources not in example
    for name in active_names:
        if name not in new_sources:
            new_sources[name] = all_urls[name]

    # Rebuild sources_disabled
    new_disabled: dict = {}
    example_disabled = example_cfg.get("sources_disabled", {})
    for name, val in example_disabled.items():
        if name.startswith("_"):
            new_disabled[name] = val
            continue
        if name in inactive_names:
            new_disabled[name] = all_urls[name]

    # Custom inactive sources not in example disabled
    for name in inactive_names:
        if name not in new_disabled:
            new_disabled[name] = all_urls[name]

    result = dict(user_cfg)
    result["sources"] = new_sources
    result["sources_disabled"] = new_disabled
    return result


def run_manage_sources():
    """Menu interactif de gestion des sources RSS."""
    print()
    print("=" * 52)
    print("  Veille - Gestion des sources RSS")
    print("=" * 52)

    if not CONFIG_FILE.exists():
        print(f"\n[WARN] {CONFIG_FILE} not found. Run setup.py first.", file=sys.stderr)
        if not EXAMPLE_FILE.exists():
            print("[ERROR] config.example.json not found either.", file=sys.stderr)
            sys.exit(1)
        print("Using config.example.json as base.\n")

    example_cfg = _load_json(EXAMPLE_FILE)
    user_cfg    = _load_json(CONFIG_FILE) if CONFIG_FILE.exists() else dict(example_cfg)

    catalog = _build_catalog(example_cfg, user_cfg)

    print(f"\n  Config : {CONFIG_FILE}")
    print("  Statut : [ON] = active, [off] = desactivee")
    print("  Action : entrer un ou plusieurs numeros (ex: 3 5 7) pour basculer")
    print("           'q' pour sauvegarder et quitter")
    print("           'r' pour reafficher la liste")

    while True:
        print()
        _display_catalog(catalog)
        print()

        try:
            raw = input("  Numeros a basculer (ou q/r): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            raw = "q"

        if raw.lower() == "q":
            break
        if raw.lower() == "r":
            continue
        if not raw:
            continue

        # Parse numbers
        changed = False
        for token in raw.replace(",", " ").split():
            try:
                idx = int(token) - 1
                if 0 <= idx < len(catalog):
                    catalog[idx]["active"] = not catalog[idx]["active"]
                    name = catalog[idx]["name"]
                    status = "ON" if catalog[idx]["active"] else "off"
                    print(f"  -> {name}: {status}")
                    changed = True
                else:
                    print(f"  [WARN] Numero {token} hors plage (1-{len(catalog)})")
            except ValueError:
                print(f"  [WARN] '{token}' n'est pas un nombre")

    # Save
    updated = _apply_catalog(catalog, example_cfg, user_cfg)
    _save_json(CONFIG_FILE, updated)

    active_count = sum(1 for e in catalog if e["active"])
    print()
    print(f"  Sauvegarde : {active_count} sources actives -> {CONFIG_FILE}")
    print()


# ---- Cron setup -------------------------------------------------------------

CRON_FILE         = SKILL_DIR / "cron.json"
CRON_EXAMPLE_FILE = SKILL_DIR / "cron.example.json"

_CRON_FREQUENCIES = {
    "1": ("daily",   "0 7 * * *"),
    "2": ("twice",   "0 7,19 * * *"),
    "3": ("hourly",  "0 * * * *"),
    "4": ("custom",  ""),
}

_CRON_MODELS = {
    "1": "anthropic/claude-haiku-4-5",
    "2": "anthropic/claude-sonnet-4-5",
    "3": "openai/gpt-4o-mini",
}


def run_setup_cron(interactive: bool = True):
    """Wizard de configuration du cron job quotidien."""
    print()
    print("=" * 52)
    print("  Veille - Configuration du cron job")
    print("=" * 52)
    print()
    print("  Ce wizard cree cron.json dans le repertoire du skill.")
    print("  L agent lit ensuite ce fichier pour creer le cron OpenClaw.")
    print()

    example = _load_json(CRON_EXAMPLE_FILE) if CRON_EXAMPLE_FILE.exists() else {}
    existing = _load_json(CRON_FILE) if CRON_FILE.exists() else {}
    cfg = dict(example)
    cfg.update(existing)

    # Name
    default_name = cfg.get("name", "veille-daily")
    cfg["name"] = _ask("  Nom du cron job", default_name, interactive)

    # Frequency
    print()
    print("  Frequence :")
    print("    1. Quotidien  (0 7 * * *)")
    print("    2. Deux fois  (0 7,19 * * *)")
    print("    3. Toutes les heures")
    print("    4. Expression cron personnalisee")
    freq_choice = _ask("  Choix", "1", interactive)
    label, default_expr = _CRON_FREQUENCIES.get(freq_choice, ("daily", "0 7 * * *"))
    if label == "custom":
        default_expr = cfg.get("schedule_cron", "0 7 * * *")
    if label == "daily":
        hour = _ask("  Heure (0-23)", "7", interactive)
        try:
            h = int(hour)
            default_expr = f"0 {h} * * *"
        except ValueError:
            default_expr = "0 7 * * *"
    cfg["schedule_cron"] = _ask("  Expression cron", default_expr, interactive) if label == "custom" else default_expr

    # Timezone
    tz_default = cfg.get("timezone", "Europe/Paris")
    cfg["timezone"] = _ask("  Timezone", tz_default, interactive)

    # Model
    print()
    print("  Modele LLM :")
    for k, v in _CRON_MODELS.items():
        print(f"    {k}. {v}")
    model_choice = _ask("  Choix", "1", interactive)
    cfg["model"] = _CRON_MODELS.get(model_choice, _CRON_MODELS["1"])

    # Timeout
    default_timeout = str(cfg.get("timeout_seconds", 180))
    t = _ask("  Timeout (secondes)", default_timeout, interactive)
    try:
        cfg["timeout_seconds"] = int(t)
    except ValueError:
        cfg["timeout_seconds"] = 180

    # Fetch args
    default_fetch = cfg.get("fetch_args", "--hours 24 --filter-seen --filter-topic")
    cfg["fetch_args"] = _ask("  Arguments fetch", default_fetch, interactive)

    # Telegram chat_id
    default_chat = cfg.get("telegram_chat_id", "")
    cfg["telegram_chat_id"] = _ask("  Telegram chat_id (laisser vide si non configure)", default_chat, interactive)

    cfg["enabled"] = True

    # Write cron.json
    _save_json(CRON_FILE, cfg)

    print()
    print("=" * 52)
    print("  cron.json cree.")
    print()
    print(f"  Fichier : {CRON_FILE}")
    print()
    print("  Prochaine etape : demander a l agent de lire cron.json")
    print("  et references/cron_prompt.md pour creer le cron OpenClaw.")
    print("  Commande : 'configure le cron veille depuis cron.json'")
    print("=" * 52)
    print()


# ---- Output management ------------------------------------------------------

_OUTPUT_TYPES = {
    "1": "telegram_bot",
    "2": "mail-client",
    "3": "nextcloud",
    "4": "file",
}

_OUTPUT_DEFAULTS = {
    "telegram_bot": {
        "type": "telegram_bot",
        "chat_id": "",
        "content": "recap",
        "enabled": True,
    },
    "mail-client": {
        "type": "mail-client",
        "mail_to": "",
        "subject": "Veille tech",
        "content": "full_digest",
        "enabled": True,
    },
    "nextcloud": {
        "type": "nextcloud",
        "path": "/Jarvis/veille-tech.md",
        "content": "full_digest",
        "enabled": True,
    },
    "file": {
        "type": "file",
        "path": "~/veille-digest.md",
        "content": "full_digest",
        "enabled": True,
    },
}

_OUTPUT_REQUIRED_FIELDS = {
    "telegram_bot": [("chat_id", "Telegram chat_id (your user or group ID)", "")],
    "mail-client":  [("mail_to", "Recipient email", "")],
    "nextcloud":    [("path", "Nextcloud path", "/Jarvis/veille-tech.md")],
    "file":         [("path", "Local file path", "~/veille-digest.md")],
}

_CONTENT_TYPES = {"1": "recap", "2": "full_digest"}


def _display_outputs(outputs: list):
    if not outputs:
        print("  (no outputs configured)")
        return
    for i, out in enumerate(outputs):
        status = "[ON] " if out.get("enabled", True) else "[off]"
        t = out.get("type", "?")
        details = []
        for k in ("chat_id", "mail_to", "path"):
            if k in out:
                details.append(f"{k}={out[k]}")
        content = out.get("content", "full_digest")
        details.append(f"content={content}")
        print(f"  {i + 1}. {status} {t}  ({', '.join(details)})")


def run_manage_outputs():
    """Menu interactif de gestion des sorties (dispatch)."""
    print()
    print("=" * 52)
    print("  Veille - Gestion des sorties (dispatch)")
    print("=" * 52)

    if not CONFIG_FILE.exists():
        print(f"\n[WARN] {CONFIG_FILE} not found. Run setup.py first.", file=sys.stderr)
        sys.exit(1)

    user_cfg = _load_json(CONFIG_FILE)
    outputs: list = user_cfg.get("outputs", [])

    print("\n  Types disponibles :")
    for k, v in _OUTPUT_TYPES.items():
        print(f"    {k}. {v}")
    print()
    print("  Commandes : t <n> = toggle, a = add, d <n> = delete, q = save & quit")

    while True:
        print()
        print("  Sorties configurees :")
        _display_outputs(outputs)
        print()

        try:
            raw = input("  Action (t/a/d/q) : ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            raw = "q"

        if not raw:
            continue

        parts = raw.split()
        cmd = parts[0].lower()

        if cmd == "q":
            break

        elif cmd == "t":
            # Toggle enable/disable
            if len(parts) < 2:
                print("  Usage: t <numero>")
                continue
            try:
                idx = int(parts[1]) - 1
                if 0 <= idx < len(outputs):
                    outputs[idx]["enabled"] = not outputs[idx].get("enabled", True)
                    status = "ON" if outputs[idx]["enabled"] else "off"
                    print(f"  -> {outputs[idx]['type']}: {status}")
                else:
                    print(f"  Numero hors plage (1-{len(outputs)})")
            except ValueError:
                print("  Numero invalide")

        elif cmd == "a":
            # Add new output
            print("  Type de sortie :")
            for k, v in _OUTPUT_TYPES.items():
                print(f"    {k}. {v}")
            try:
                choice = input("  Choix (1-4) : ").strip()
            except (EOFError, KeyboardInterrupt):
                continue
            out_type = _OUTPUT_TYPES.get(choice)
            if not out_type:
                print("  Choix invalide")
                continue

            new_out = dict(_OUTPUT_DEFAULTS[out_type])

            # Prompt for required fields
            for field, label, default in _OUTPUT_REQUIRED_FIELDS.get(out_type, []):
                try:
                    val = input(f"  {label} [{default}] : ").strip()
                    new_out[field] = val if val else default
                except (EOFError, KeyboardInterrupt):
                    new_out[field] = default

            # Content type
            print("  Contenu : 1. recap (court)  2. full_digest (complet)")
            try:
                ct = input("  Choix [2] : ").strip()
                new_out["content"] = _CONTENT_TYPES.get(ct, "full_digest")
            except (EOFError, KeyboardInterrupt):
                new_out["content"] = "full_digest"

            # telegram_bot: warn if no token
            if out_type == "telegram_bot":
                oc_cfg_path = Path.home() / ".openclaw" / "openclaw.json"
                if oc_cfg_path.exists():
                    try:
                        oc = json.loads(oc_cfg_path.read_text(encoding="utf-8"))
                        token = oc.get("channels", {}).get("telegram", {}).get("botToken", "")
                        if token:
                            print("  OK: bot_token auto-detected from OpenClaw config")
                        else:
                            print("  WARN: no bot_token in OpenClaw config (channels.telegram.botToken)")
                    except Exception:
                        pass
                else:
                    print("  WARN: OpenClaw config not found - bot_token will need manual config")

            outputs.append(new_out)
            print(f"  -> Added: {out_type}")

        elif cmd == "d":
            # Delete output
            if len(parts) < 2:
                print("  Usage: d <numero>")
                continue
            try:
                idx = int(parts[1]) - 1
                if 0 <= idx < len(outputs):
                    removed = outputs.pop(idx)
                    print(f"  -> Removed: {removed.get('type','?')}")
                else:
                    print(f"  Numero hors plage (1-{len(outputs)})")
            except ValueError:
                print("  Numero invalide")

        else:
            print("  Commandes : t <n>=toggle, a=add, d <n>=delete, q=save&quit")

    # Save
    user_cfg["outputs"] = outputs
    _save_json(CONFIG_FILE, user_cfg)
    print()
    print(f"  Sauvegarde : {len(outputs)} sortie(s) -> {CONFIG_FILE}")
    print()


# ---- Main -------------------------------------------------------------------


def cleanup():
    """Remove all persistent files written by this skill (config + data)."""
    print("Removing veille skill persistent files...")
    removed = []
    for path in [CONFIG_FILE,
                 _DATA_DIR / "seen_urls.json",
                 _DATA_DIR / "topic_seen.json"]:
        if path.exists():
            path.unlink()
            removed.append(str(path))
    for d in [_DATA_DIR, _CONFIG_DIR]:
        try:
            d.rmdir()
        except OSError:
            pass
    if removed:
        for p in removed:
            print(f"  Removed: {p}")
        print("Done. Re-run setup.py to reconfigure.")
    else:
        print("  Nothing to remove.")


def main():
    parser = argparse.ArgumentParser(description="OpenClaw veille - setup wizard")
    parser.add_argument("--manage-sources", action="store_true",
                        help="Gestion interactive des sources RSS (activer/desactiver)")
    parser.add_argument("--manage-outputs", action="store_true",
                        help="Gestion interactive des sorties (telegram, mail, nextcloud, file)")
    parser.add_argument("--setup-cron", action="store_true",
                        help="Configure le cron job quotidien (ecrit cron.json)")
    parser.add_argument("--non-interactive", action="store_true",
                        help="Utilise les valeurs par defaut sans prompts")
    parser.add_argument("--cleanup", action="store_true",
                        help="Remove all persistent files (config + data)")
    args = parser.parse_args()

    if args.cleanup:
        cleanup()
    elif args.manage_sources:
        run_manage_sources()
    elif args.manage_outputs:
        run_manage_outputs()
    elif args.setup_cron:
        run_setup_cron(interactive=not args.non_interactive)
    else:
        run_setup(interactive=not args.non_interactive)


if __name__ == "__main__":
    main()
