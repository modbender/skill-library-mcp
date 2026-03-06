wol-sleep-pc
===============

A small OpenClaw AgentSkill providing scripts to send Wake-on-LAN (WOL) and Sleep-on-LAN (SOL) magic packets.

Features
- send_wol.py — Send WOL magic packet (configurable)
- send_sleep.py — Send SOL (inverted MAC) magic packet (configurable)
- Config file support: ~/.config/wol-sleep-pc/config.json (ignored by .gitignore)

Defaults
- Scripts default to zeroed values (MAC 00:00:00:00:00:00, broadcast 0.0.0.0). Configure via config file or CLI flags.

Install
1. Clone the repo.
2. Ensure Python 3 is available.
3. Make scripts executable if needed: chmod +x scripts/*.py

Usage
- Send WOL (CLI override):
  python3 scripts/send_wol.py --mac 24:4B:FE:CA:90:99 --broadcast 192.168.1.255

- Send SOL (CLI override):
  python3 scripts/send_sleep.py --mac 99:90:CA:FE:4B:24 --broadcast 192.168.1.255

Config file
Create ~/.config/wol-sleep-pc/config.json with keys:
{
  "mac": "24:4B:FE:CA:90:99",
  "sleep_mac": "99:90:CA:FE:4B:24",
  "broadcast": "192.168.1.255",
  "port": 9
}

Security & privacy
- This repository intentionally does not include user MAC/IP defaults. The config file is ignored by .gitignore; keep your secrets local.

License
- Add a license file as needed before publishing widely.
