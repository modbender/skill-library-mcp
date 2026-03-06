#!/usr/bin/env python3
"""
github-watch setup.py
Configure token path, recipient, outputs.
Usage:
  setup.py             Interactive
  setup.py --show      Print current config
  setup.py --cleanup   Remove config
"""

import sys
import json
import os

CONFIG_DIR  = os.path.expanduser("~/.openclaw/config/github-watch")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
DATA_DIR    = os.path.expanduser("~/.openclaw/data/github-watch")

DEFAULTS = {
    "token_path": "~/.openclaw/secrets/github_token",
    "recipient":  "romain@rwx-g.fr",
    "nc_path":    "/Jarvis/github-watch.md",
    "outputs":    ["email", "nextcloud"],
    "since":      "weekly",
}


def load():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return dict(DEFAULTS)


def save(cfg):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    print(f"Config sauvegardee: {CONFIG_PATH}")


def interactive():
    cfg = load()
    print("=== GitHub Watch Setup ===\n")

    for key, label in [
        ("token_path", "Chemin token GitHub"),
        ("recipient",  "Email destinataire"),
        ("nc_path",    "Chemin Nextcloud"),
    ]:
        default = cfg.get(key, DEFAULTS[key])
        val = input(f"{label} [{default}]: ").strip()
        cfg[key] = val or default

    default_since = cfg.get("since", "weekly")
    val = input(f"Periode trending (daily/weekly/monthly) [{default_since}]: ").strip()
    if val in ("daily", "weekly", "monthly"):
        cfg["since"] = val
    else:
        cfg["since"] = default_since

    print(f"Outputs disponibles: email, nextcloud")
    current = ", ".join(cfg.get("outputs", []))
    val = input(f"Outputs [{current}]: ").strip()
    if val:
        cfg["outputs"] = [o.strip() for o in val.split(",") if o.strip()]

    save(cfg)
    print("\nSetup complet.")


def main():
    args = sys.argv[1:]

    if "--show" in args:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH) as f:
                print(f.read())
        else:
            print("Aucune config. Lance setup.py d'abord.")
        return

    if "--cleanup" in args:
        if os.path.exists(CONFIG_PATH):
            os.remove(CONFIG_PATH)
            print(f"Supprime: {CONFIG_PATH}")
        return

    interactive()


if __name__ == "__main__":
    main()
