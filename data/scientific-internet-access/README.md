<div align="center">

# 🔬 Scientific Internet Access

### An OpenClaw Skill for AI-powered network access.

[![Install](https://img.shields.io/badge/clawhub_install-scientific--internet--access-FF6B6B?style=for-the-badge)](https://clawhub.ai/shadowrocketai/scientific-internet-access)
[![Version](https://img.shields.io/badge/version-1.7.1-blue?style=for-the-badge)]()
[![Website](https://img.shields.io/badge/Website-shadowrocket.ai-00C7B7?style=for-the-badge)](https://shadowrocket.ai)

```bash
clawhub install scientific-internet-access
```

</div>

---

## What It Does

Install this skill, and your OpenClaw AI agent becomes a network access specialist.

Users say "上不了Google" or "帮我翻墙" — your agent handles the entire flow:

```
Step 1: Ask device type (or detect from screenshot)
Step 2: Recommend client app with exact download link
Step 3: Auto-fetch fastest nodes (scraped + tested live)
Step 4: Guide import — one tap at a time
```

### Design Principles

1. **ONE step at a time.** Never dump 5 instructions. One action, wait for confirmation, next.
2. **Every instruction includes HOW.** Not "截图发我" but "同时按住电源键+音量上键，屏幕闪一下就截好了，然后发给我."
3. **Stuck = downgrade, never repeat.** User says 不懂 → rephrase simpler → teach screenshot → teach voice.

---

## How It Works

The skill bundles four Python scripts that work together:

| Script | Purpose |
|--------|---------|
| `scraper.py` | Monitors 10+ public node subscription sources, fetches and decodes nodes |
| `tester.py` | Runs 20 parallel TCP connectivity tests, ranks by latency |
| `formatter.py` | Outputs in 6 formats: Clash, V2Ray, Surge, Shadowrocket, Base64, plain text |
| `handler.py` | Orchestrates the flow: scrape → test → format → present to user |

All network connections are to **public node subscription URLs** (GitHub raw content, public APIs). The tester verifies connectivity to the parsed node endpoints. No credentials are required or stored.

### Security Notes

- No environment variables or credentials required
- All source URLs are public and auditable in `scraper.py`
- Node data is stored locally in `~/.openclaw/workspace/`
- No system-wide configuration changes
- Review the scripts yourself before installing: they're short and readable

---

## Numbers

| Metric | Value |
|--------|-------|
| Node sources monitored | 10+ |
| Parallel test threads | 20 |
| Output formats | 6 |
| Supported protocols | VMess, VLESS, Trojan, Shadowsocks |
| Scrape interval | Every 2 hours |
| Health check | Every 30 minutes |
| User setup steps | 3 |
| Cost | $0 |

---

## Architecture

```
~/.openclaw/skills/scientific-internet-access/
├── SKILL.md              # Agent instructions
├── scripts/
│   ├── handler.py        # Interaction orchestrator
│   ├── scraper.py        # Multi-source node scraper
│   ├── tester.py         # Parallel connectivity tester
│   └── formatter.py      # Multi-format output generator
└── .github/workflows/
    ├── publish.yml        # Tag → Release → ClawHub
    └── sync-magic.yml     # Mirror sync
```

---

## Protocols & Clients

| Protocol | iOS | Android | Windows | macOS |
|----------|-----|---------|---------|-------|
| VMess | Shadowrocket | v2rayNG | v2rayN / Clash Verge | ClashX / V2rayU |
| VLESS | Shadowrocket | v2rayNG | v2rayN | V2rayU |
| Trojan | Shadowrocket | v2rayNG | v2rayN | ClashX |
| Shadowsocks | Shadowrocket | v2rayNG | Clash Verge | ClashX |

---

## Mirror

[Magic Internet Access](https://github.com/shadowrocketai/Magic-Internet-Access) — same engine, auto-synced via GitHub Actions on every tag.

---

## Recommended Model

Claude follows the step-by-step instructions more reliably. Gemini tends to improvise.

---

## Install

```bash
clawhub install scientific-internet-access
```

Or manually:

```bash
git clone https://github.com/shadowrocketai/Scientific-Internet-Access.git ~/.openclaw/skills/scientific-internet-access
```

---

## License

MIT

