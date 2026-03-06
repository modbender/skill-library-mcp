---
name: openclaw-expert
description: >
  Expert skill for OpenClaw (formerly Clawdbot/MoltBot) — the self-hosted AI agent framework.
  ALWAYS use when user mentions OpenClaw, Clawdbot, MoltBot, openclaw.json, openclaw gateway,
  openclaw channels, openclaw nodes, openclaw models, openclaw skills, openclaw doctor,
  AGENTS.md, SOUL.md, USER.md, HEARTBEAT.md, MEMORY.md, IDENTITY.md, TOOLS.md, BOOTSTRAP.md,
  ClawHub, clawhub, openclaw workspace, openclaw config, openclaw sessions, openclaw pairing,
  openclaw docker, openclaw sandbox, openclaw heartbeat, openclaw compaction, memorySearch,
  multi-agent, bindings, dmPolicy. Covers installation, configuration, troubleshooting,
  security hardening, channel setup, skill development, memory tuning, Docker deployment.
  Also trigger for "my bot", "my agent", "Lobster", or agent issues after config changes.
---

# OpenClaw Expert Skill

## Kernprinzip: Docs-First + Backup-First

OpenClaw verwendet CalVer-Versioning (YYYY.M.D-N) und ändert sich häufig.
**Vor jeder Änderung** diese Checkliste abarbeiten:

1. **Version prüfen**: `openclaw --version`
2. **Live-Docs holen** — `web_fetch` auf relevante Docs-Seiten (URLs in Referenzdateien)
3. **Community-Tipps suchen** — `web_search` nach aktuellen Workarounds
4. **Backup anlegen** — Niemals Konfig ohne Backup ändern
5. **Änderung durchführen**
6. **Validieren** — `openclaw doctor` vor und nach jeder Änderung
7. **Gateway neu starten** — `systemctl --user restart openclaw-gateway`
8. **Testen** — `openclaw status` + Kanal-Test

---

## Architektur auf einen Blick

```
Messaging-Kanäle (WhatsApp, Telegram, Slack, Discord, Signal, iMessage, Teams, Matrix, Google Chat, Zalo, WebChat…)
        │
        ▼
┌───────────────────────────────┐
│          Gateway              │  ← ws://127.0.0.1:18789
│     (Control-Plane, RPC)      │  ← Config: ~/.openclaw/openclaw.json (JSON5)
│     systemd user service      │  ← Dashboard: http://127.0.0.1:18789
└──────────────┬────────────────┘
               │
        ┌──────┴──────┐
        │  Agent(s)   │  ← Workspace: ~/.openclaw/workspace/
        │  Runtime    │  ← Sessions: ~/.openclaw/agents/<id>/sessions/
        └──────┬──────┘
               │
        ┌──────┴──────────────────────────┐
        │  Nodes (optional)               │
        │  iOS / Android / macOS / Pi     │
        │  + Canvas / A2UI                │
        └─────────────────────────────────┘
```

### Verzeichnisstruktur
```
~/.openclaw/
├── openclaw.json          # Haupt-Config (JSON5 – Kommentare + trailing commas!)
├── credentials/           # API-Keys (chmod 600!)
│   ├── anthropic
│   ├── openai
│   └── openrouter
├── agents/
│   └── <agentId>/
│       └── sessions/      # Session-Logs (*.jsonl)
├── skills/                # Managed/lokale Skills
└── workspace/             # Agent-Workspace (= das "Gehirn")
    ├── AGENTS.md          # Betriebsanweisungen (in JEDER Session geladen)
    ├── SOUL.md            # Persönlichkeit, Ton, Grenzen (jede Session)
    ├── USER.md            # Nutzerprofil (jede Session)
    ├── TOOLS.md           # Tool-Hinweise (jede Session)
    ├── IDENTITY.md        # Name, Emoji, Vibe
    ├── HEARTBEAT.md       # Scheduled-Tasks / Cron-Checkliste
    ├── MEMORY.md          # Langzeit-Gedächtnis (nur private Sessions!)
    ├── BOOTSTRAP.md       # Einmal-Setup (nach Ausführung gelöscht)
    ├── memory/            # Tages-Logs (YYYY-MM-DD.md)
    ├── skills/            # Workspace-Skills
    └── .git/              # Git-Backup (empfohlen!)
```

---

## Referenzdateien — Wann was lesen

Dieses Skill-Paket enthält detaillierte Referenzdateien. **Lies die relevante Datei
BEVOR du eine Aktion durchführst.** Die Dateien liegen unter `references/` im Skill-Verzeichnis.

| Aufgabe | Referenzdatei | Inhalt |
|---|---|---|
| Installation & erste Schritte | `references/installation.md` | npm/pnpm, Docker, VPS-Setup, Onboarding-Wizard |
| openclaw.json bearbeiten | `references/config-reference.md` | Vollständige Feld-Referenz basierend auf realer Config (auth, models, agents, tools, gateway…) |
| Dashboard (Control UI) | `references/dashboard.md` | Alle Dashboard-Bereiche, Zugriff, Troubleshooting |
| Workspace-Dateien schreiben | `references/workspace-files.md` | AGENTS.md, SOUL.md, USER.md, HEARTBEAT.md, MEMORY.md Templates |
| Channels einrichten | `references/channels.md` | Telegram (komplett!), WhatsApp, Discord, Slack, Signal + Troubleshooting |
| Memory & Compaction tunen | `references/memory-system.md` | memoryFlush, memorySearch, Compaction, Semantic Search, Decay |
| Docker-Deployment | `references/docker-setup.md` | docker-compose, Sandbox, alpine/openclaw, Permissions |
| Security-Hardening | `references/security-hardening.md` | dmPolicy, Token-Rotation, Allowlists, Sandboxing, CIS-Style |
| Skills entwickeln/installieren | `references/skills-guide.md` | SKILL.md-Format, ClawHub, Workspace-Skills, Security-Review |
| Multi-Agent-Routing | `references/multi-agent.md` | agents.list, bindings, accountId, agentId, Isolation |
| CLI-Referenz | `references/cli-reference.md` | Alle Befehle mit Syntax und Beispielen |
| Dashboard / Control UI | `references/dashboard.md` | Sidebar-Navigation, Bereiche, CORS, Config, Troubleshooting |
| Nodes & Remote-Zugriff | `references/nodes-and-remote.md` | Node-Typen, Pairing, Headless-Nodes, Bonjour/mDNS, Exec-Approvals |
| Tailscale-Integration | `references/tailscale-integration.md` | Serve vs Funnel vs Tailnet-Bind, SSH-Tunnel, Auth, Config-Beispiele |
| Praxis-Beispiele | `references/examples.md` | 7 vollständige Setup-Szenarien (Einsteiger → Multi-Agent → Kosten-optimiert) |
| Troubleshooting | `references/troubleshooting.md` | Häufige Fehler, Logs, Diagnose-Schritte |
| Tricks & Power-User | `references/tricks-and-hacks.md` | Community-Tipps, Cost-Saving, Obsidian, Surge, Watchdog |

---

## Schnellreferenz: Wichtigste CLI-Befehle

```bash
# Status & Diagnose
openclaw --version                    # CalVer-Version
openclaw doctor                       # Gesundheitscheck (IMMER!)
openclaw doctor --fix                 # Auto-Fix
openclaw status                       # Kurzer Status
openclaw dashboard                    # Browser-UI (Port 18789)

# Gateway
openclaw gateway start|stop|restart|status
openclaw gateway install              # systemd user service
openclaw gateway log                  # Logs (= journalctl --user -u openclaw-gateway -f)

# Channels
openclaw channels list|add|remove|restart
openclaw channels status --probe      # Live-Check

# Models
openclaw models list|set <provider/model>

# Skills
openclaw skills list|reload
clawhub search|install|update <name>

# Memory & Sessions
openclaw sessions list|clean
openclaw memory flush

# Update
pnpm add -g openclaw@latest && pnpm approve-builds -g && openclaw doctor

# Nodes & Devices
openclaw nodes status                 # Verbundene Nodes anzeigen
openclaw nodes describe --all         # Node-Capabilities auflisten
openclaw nodes run --node <id> -- <cmd>  # Befehl auf Node ausführen
openclaw devices list                 # Pairing-Requests anzeigen
openclaw devices approve <requestId>  # Node-Pairing genehmigen

# Channel-Pairing
openclaw pairing list|approve <channel> <code>

# Config
openclaw config list|get|set|validate

# Security
openclaw token:rotate --force --length 64
openclaw security audit --deep
```

---

## Sicherheits-Grundregeln (IMMER beachten!)

1. **Gateway bind: `loopback`** — Niemals `lan` oder `0.0.0.0` ohne Tailscale/VPN
2. **dmPolicy: `allowlist`** — Niemals `open` in Produktion
3. **Token: mindestens 64 Zeichen** — `openclaw token:rotate --force --length 64`
4. **Credentials: `chmod 600`** — `chmod 600 ~/.openclaw/credentials/*`
5. **Skills reviewen** — Vor Installation Quellcode prüfen, ClawHub "Hide Suspicious" nutzen
6. **Kein root** — OpenClaw als eigener User betreiben
7. **Workspace = privat** — Git-Backup in **privates** Repo, MEMORY.md nie in Groups laden
8. **API-Spending-Limits** — Beim Provider setzen, bevor Heartbeat aktiviert wird
9. **Sandbox für Tools** — `tools.exec.host: "sandbox"` wenn möglich

---

## Workflow: Docs nachschlagen

### Offizielle Docs-URLs (für web_fetch)
```
https://docs.openclaw.ai                          # Hauptseite
https://docs.openclaw.ai/install/docker           # Docker
https://docs.openclaw.ai/concepts/agent-workspace # Workspace
https://docs.openclaw.ai/concepts/memory          # Memory
https://docs.openclaw.ai/concepts/multi-agent     # Multi-Agent
https://docs.openclaw.ai/channels/<name>          # Channel-Guides
https://docs.openclaw.ai/models                   # Models
https://docs.openclaw.ai/tools/skills             # Skills
https://docs.openclaw.ai/security                 # Security
```

Alternative Docs-Mirror: `https://openclaw.im/docs/`

### Community-Suche (für web_search)
```
"openclaw <Thema> 2026 tips"
"openclaw <Problem> fix workaround github issue"
"openclaw.json <Section> advanced configuration"
```

Quellen-Priorität:
1. `github.com/openclaw/openclaw` (Issues, Discussions, AGENTS.md)
2. `docs.openclaw.ai` / `openclaw.im/docs`
3. Community-Guides (Simon Willison TIL, Substack, Medium)
4. Reddit r/selfhosted, Hacker News

---

## Backup-Strategie (IMMER vor Änderungen)

```bash
# Snapshot der Config
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak

# Versioniertes Backup
tar czf ~/openclaw-backup-$(date +%Y%m%d_%H%M%S).tar.gz ~/.openclaw/

# Git-Backup des Workspace (empfohlen)
cd ~/.openclaw/workspace && git add -A && git commit -m "backup: $(date +%Y%m%d_%H%M%S)"
```

---

## Protokoll: Sichere Config-Änderung

1. `openclaw --version` → Version notieren
2. Relevante Referenzdatei lesen (siehe Tabelle oben)
3. Live-Docs fetchen (URLs oben)
4. `cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak`
5. Änderung durchführen
6. `openclaw doctor`
7. `systemctl --user restart openclaw-gateway`
8. `openclaw status` + Funktionstest im Channel
9. Bei Fehler: `cp ~/.openclaw/openclaw.json.bak ~/.openclaw/openclaw.json && systemctl --user restart openclaw-gateway`
