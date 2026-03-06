#!/usr/bin/env python3
"""
restart-guard: discover_channels.py
Discover enabled notification channels and notify modes.
"""

import argparse
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    parser = argparse.ArgumentParser(description="Discover available notification channels")
    parser.add_argument("--config", required=True, help="Path to restart-guard.yaml")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    cfg = load_config(args.config)
    channels = discover_channels(cfg)

    if args.json:
        print(json.dumps(channels, ensure_ascii=False, indent=2))
        return

    print("Available notification channels:")
    for item in channels.get("choices", []):
        label = item.get("label", item.get("id", ""))
        cid = item.get("id", "")
        tgt = item.get("suggestedTarget", "")
        req = "yes" if item.get("requiresTarget", False) else "no"
        enabled = "yes" if item.get("enabled", False) else "no"
        note = item.get("note", "")
        line = f"- {cid}: {label} | enabled={enabled} | requiresTarget={req}"
        if tgt:
            line += f" | suggestedTarget={tgt}"
        if note:
            line += f" | note={note}"
        print(line)

    default_choice = channels.get("default", "webui")
    print(f"default_channel={default_choice}")
    print(f"default_mode={channels.get('defaultMode', 'origin')}")


def discover_channels(restart_cfg):
    notif = restart_cfg.get("notification", {}) if isinstance(restart_cfg, dict) else {}
    paths = restart_cfg.get("paths", {}) if isinstance(restart_cfg, dict) else {}

    openclaw_cfg_path = expand(paths.get("openclaw_config", "~/.openclaw/openclaw.json"))
    oc = {}
    try:
        with open(openclaw_cfg_path, "r", encoding="utf-8") as f:
            oc = json.load(f)
    except Exception:
        oc = {}

    choices = []
    seen_ids = set()

    def add_choice(item):
        cid = str(item.get("id", "")).strip().lower()
        if not cid:
            return
        item["id"] = cid
        if cid in seen_ids:
            return
        seen_ids.add(cid)
        choices.append(item)

    # webui is always valid. In origin mode, guardian will ACK to the same session.
    add_choice({
        "id": "webui",
        "label": "Web UI (origin session)",
        "enabled": True,
        "requiresTarget": False,
        "suggestedTarget": "",
        "note": "Guardian ACK returns to origin session; net reports in the same thread",
    })

    channels_cfg = oc.get("channels", {}) if isinstance(oc, dict) else {}
    bindings = oc.get("bindings", []) if isinstance(oc, dict) else []

    configured_channel = str((notif.get("openclaw", {}) or {}).get("channel", "")).strip().lower()
    configured_target = str((notif.get("openclaw", {}) or {}).get("target", "") or (notif.get("openclaw", {}) or {}).get("to", "")).strip()

    for name, ch_cfg in sorted(channels_cfg.items()):
        if not isinstance(ch_cfg, dict):
            continue
        if ch_cfg.get("enabled") is not True:
            continue

        targets = []
        if configured_channel == name and configured_target:
            targets.append(configured_target)

        allow_from = ch_cfg.get("allowFrom", [])
        if isinstance(allow_from, list):
            for x in allow_from:
                sx = str(x).strip()
                if sx and sx not in targets:
                    targets.append(sx)

        bound_to_main = False
        if isinstance(bindings, list):
            for b in bindings:
                if not isinstance(b, dict):
                    continue
                if str(b.get("agentId", "")).strip() != "main":
                    continue
                match = b.get("match", {})
                if isinstance(match, dict) and str(match.get("channel", "")).strip() == name:
                    bound_to_main = True
                    break

        note = ""
        if bound_to_main:
            note = "Bound to main agent"

        add_choice({
            "id": name,
            "label": name,
            "enabled": True,
            "requiresTarget": True,
            "suggestedTarget": targets[0] if targets else "",
            "suggestedTargets": targets,
            "boundToMain": bound_to_main,
            "note": note,
        })

    for ch in _normalize_channels(notif.get("channels", [])):
        if ch in {"webui", "none", "off", "disabled"}:
            continue
        suggested = ""
        requires = ch not in {"webhook"}
        if ch == "telegram":
            suggested = str((notif.get("telegram", {}) or {}).get("chat_id", "")).strip()
        elif isinstance(notif.get(ch), dict):
            suggested = str((notif.get(ch, {}) or {}).get("target", "")).strip()
        add_choice(
            {
                "id": ch,
                "label": ch,
                "enabled": True,
                "requiresTarget": requires,
                "suggestedTarget": suggested,
                "suggestedTargets": [suggested] if suggested else [],
                "boundToMain": False,
                "note": "Configured in restart-guard notification.channels",
            }
        )

    fallback = str(notif.get("fallback", "")).strip().lower()
    if fallback and fallback not in {"webui", "none", "off", "disabled"}:
        add_choice(
            {
                "id": fallback,
                "label": fallback,
                "enabled": True,
                "requiresTarget": fallback not in {"webhook"},
                "suggestedTarget": "",
                "suggestedTargets": [],
                "boundToMain": False,
                "note": "Legacy notification.fallback",
            }
        )

    default_choice = "webui"
    primary = str(notif.get("primary", "")).strip().lower()
    if primary == "openclaw" and configured_channel:
        default_choice = configured_channel

    external_channels = [
        str(item.get("id", "")).strip().lower()
        for item in choices
        if str(item.get("id", "")).strip().lower() not in {"", "webui", "none", "off", "disabled"}
    ]
    external_targets = {
        str(item.get("id", "")).strip().lower(): str(item.get("suggestedTarget", "")).strip()
        for item in choices
        if str(item.get("id", "")).strip().lower() not in {"", "webui", "none", "off", "disabled"}
        and str(item.get("suggestedTarget", "")).strip()
    }

    return {
        "openclawConfig": openclaw_cfg_path,
        "notifyModes": [
            {
                "id": "origin",
                "label": "Origin Session",
                "note": "Recommended. Guardian sends ACK back to the initiating session.",
            },
            {
                "id": "selected",
                "label": "Selected Channel",
                "note": "Use only the chosen channel/target for notifications.",
            },
            {
                "id": "all",
                "label": "All Enabled Channels",
                "note": "Broadcast to all configured external channels.",
            },
        ],
        "defaultMode": "origin",
        "default": default_choice,
        "choices": choices,
        "externalChannels": external_channels,
        "externalTargets": external_targets,
    }


def expand(p):
    return os.path.expanduser(p) if p else p


def load_config(path):
    sys.path.insert(0, SCRIPT_DIR)
    from write_context import load_config as _load
    return _load(path)


def _normalize_channels(raw):
    if isinstance(raw, list):
        return [str(x).strip().lower() for x in raw if str(x).strip()]
    if isinstance(raw, str):
        v = raw.strip()
        if not v:
            return []
        return [x.strip().lower() for x in v.split(",") if x.strip()]
    return []


if __name__ == "__main__":
    main()
