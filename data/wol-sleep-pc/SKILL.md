---
name: wol-sleep-pc
description: Send Wake-on-LAN (magic packet) and Sleep-on-LAN (inverted MAC) packets for a specific PC. Use when the user asks to wake, check, or put the PC to sleep on the local LAN. Defaults are zeroed; configure the target IP, MAC, and inverted MAC via command-line flags or a config file.
---

# wol-sleep-pc

This skill provides two small, well-tested scripts to send Wake-on-LAN (WOL) and Sleep-on-LAN (SOL) magic packets to a target machine on the same LAN. The skill is intentionally configurable and does not ship with any real MAC/IP defaults — defaults are zeroed and must be provided via CLI flags or a local config file.

Files provided:
- scripts/send_wol.py — Send a standard WOL magic packet.
- scripts/send_sleep.py — Send a SOL (inverted-MAC) magic packet.
- README.md — Usage examples and install notes.
- .gitignore — Ensures local config is not committed.

Quick usage
- From the repository root:
  python3 scripts/send_wol.py --mac 24:4B:FE:CA:90:99 --broadcast 192.168.1.255

- Send SOL (inverted MAC):
  python3 scripts/send_sleep.py --mac 99:90:CA:FE:4B:24 --broadcast 192.168.1.255

Config file (recommended)
- Path: ~/.config/wol-sleep-pc/config.json
- Example content:
  {
    "mac": "24:4B:FE:CA:90:99",
    "sleep_mac": "99:90:CA:FE:4B:24",
    "broadcast": "192.168.1.255",
    "port": 9
  }
- Behavior: scripts load values from this file if present; any CLI flags override the config file values.
- The repository .gitignore ignores config files so secrets remain local.

Agent usage patterns
- "wake PC" — run send_wol.py with configured values.
- "sleep PC" — run send_sleep.py with configured inverted MAC.
- "send WOL now" / "send SOL now" — immediate send.

Design notes and safety
- Scripts require Python 3 and permission to send UDP broadcast packets from the runtime host.
- The skill assumes L2 connectivity to the target LAN; if running from a different network segment, configure the correct broadcast address or run the script from a host on the same LAN.
- Defaults are intentionally zeroed to avoid leaking sensitive addresses when the skill is published.

Publishing guidance
- The repo is safe to publish to ClawHub as-is because it contains no real MAC/IP values and ignores local config.
- Add a LICENSE if you want to publish under a specific license.

When to trigger this skill
- Trigger when the user explicitly requests waking or sleeping a machine on their LAN, or asks to save or update local WOL/SOL config. The scripts are small and deterministic; prefer executing the scripts rather than re-generating the packet code each time.
