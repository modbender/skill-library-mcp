# OpenClaw CLI-Referenz (Vollständig)

> Stand: Februar 2026. OpenClaw ändert sich häufig — bei unbekannten Flags `openclaw <command> --help` nutzen.

## Inhaltsverzeichnis
1. [Gateway](#gateway)
2. [Doctor & Diagnose](#doctor--diagnose)
3. [Channels](#channels)
4. [Nodes](#nodes)
5. [Models](#models)
6. [Skills & ClawHub](#skills--clawhub)
7. [Config](#config)
8. [Sessions](#sessions)
9. [Memory](#memory)
10. [Pairing](#pairing)
11. [Security](#security)
12. [Setup & Onboarding](#setup--onboarding)
13. [Update & Versioning](#update--versioning)
14. [Dashboard & TUI](#dashboard--tui)

---

## Gateway

```bash
openclaw gateway start                # Gateway starten
openclaw gateway stop                 # Gateway stoppen
openclaw gateway restart              # Neustart (NACH Config-Änderung!)
openclaw gateway status               # Status prüfen
openclaw gateway install              # Als systemd user-service installieren
openclaw gateway uninstall            # Service entfernen
openclaw gateway log                  # Logs anzeigen
# Äquivalent: journalctl --user -u openclaw-gateway -f
# Fallback-Log: tail -n 120 /tmp/openclaw-gateway.log
```

### systemd User-Service manuell
```bash
# WICHTIG: Immer als openclaw-User, NICHT als root!
ssh openclaw@<server-ip>
openclaw gateway install
systemctl --user start openclaw-gateway
systemctl --user enable openclaw-gateway
# Status: systemctl --user status openclaw-gateway
# Logs:   journalctl --user -u openclaw-gateway -f --no-pager
```

### Gateway-Port prüfen
```bash
ss -ltnp | grep 18789
# oder:
lsof -i :18789
```

---

## Doctor & Diagnose

```bash
openclaw doctor                       # Vollständiger Gesundheitscheck
openclaw doctor --fix                 # Auto-Fix versuchen
openclaw doctor --run doctor          # DM-Policy prüfen
openclaw status                       # Kompakter Status (Model, Tokens, Cost)
```

**GOLDENE REGEL**: `openclaw doctor` VOR und NACH jeder Config-Änderung ausführen.

---

## Channels

```bash
openclaw channels list                # Alle Kanäle anzeigen
openclaw channels status --probe      # Live-Check aller Kanäle
openclaw channels add                 # Kanal hinzufügen (interaktiver Wizard)
openclaw channels add --channel telegram --token <BOT_TOKEN>
openclaw channels add --channel discord --token <BOT_TOKEN>
openclaw channels login               # WhatsApp QR-Code-Login
openclaw channels remove <name>       # Kanal entfernen
openclaw channels restart <name>      # Kanal neu starten
```

### Unterstützte Kanäle (Stand 02/2026)
WhatsApp, Telegram, Slack, Discord, Google Chat, Signal,
BlueBubbles (iMessage), iMessage (legacy), Microsoft Teams,
Matrix, Zalo, Zalo Personal, WebChat, LINE, Mattermost

### Chat-Befehle (in WhatsApp/Telegram/Slack etc.)
```
/status    — Session-Status (Modell, Tokens, Kosten)
/new       — Neue Session starten
/compact   — Kontext manuell kompaktieren
```

---

## Nodes

```bash
openclaw nodes list                   # Alle Nodes anzeigen
openclaw nodes status                 # Node-Status
openclaw nodes pair <type>            # Node pairen (ios/android/mac/pi)
openclaw nodes remove <id>            # Node entfernen
```

Node-Typen: iOS, Android, macOS (Menübar-App), Raspberry Pi

---

## Models

```bash
openclaw models list                  # Verfügbare Modelle anzeigen
openclaw models set <model-id>        # Aktives Modell setzen
```

### Model-ID-Format
```
provider/model-name
```

Beispiele:
```
anthropic/claude-sonnet-4-5
anthropic/claude-opus-4-6
openai/gpt-4o
ollama/llama3.2:latest
openrouter/moonshotai/kimi-k2     # Bei / im Model-Name: Provider-Prefix!
```

**WICHTIG**: Wenn die Model-ID selbst `/` enthält (z.B. OpenRouter-Style),
MUSS der Provider-Prefix dabei sein: `openrouter/moonshotai/kimi-k2`

---

## Skills & ClawHub

```bash
openclaw skills list                  # Installierte Skills anzeigen
openclaw skills reload                # Skills neu laden (neue Session nötig!)

clawhub search <query>                # ClawHub durchsuchen
clawhub install <skill-name>          # Skill installieren
clawhub update <skill-name>           # Skill updaten
clawhub update --all                  # Alle Skills updaten
```

Skills werden erst in einer **neuen Session** aktiv — nach `openclaw skills reload`
oder `openclaw gateway restart`.

### Skill-Verzeichnisse
```
~/.openclaw/skills/            # Managed Skills (clawhub install)
~/.openclaw/workspace/skills/  # Workspace Skills (manuell)
```

---

## Config

```bash
openclaw config list                  # Alle Config-Werte anzeigen
openclaw config get <key>             # Einzelnen Wert lesen
openclaw config set <key> <value>     # Wert setzen (live, ohne Neustart)
openclaw config validate              # Config validieren (≈ doctor)
```

---

## Sessions

```bash
openclaw sessions list                # Aktive Sessions anzeigen
openclaw sessions clean               # Alte Sessions aufräumen
```

Session-Speicherort: `~/.openclaw/agents/<agentId>/sessions/<SessionId>.jsonl`

---

## Memory

```bash
openclaw memory flush                 # Gedächtnis in MEMORY.md schreiben
```

---

## Pairing

```bash
openclaw pairing list                            # Ausstehende Pairings
openclaw pairing approve telegram <CODE>         # Telegram-Pairing bestätigen
openclaw pairing approve whatsapp <CODE>         # WhatsApp-Pairing bestätigen
openclaw pairing approve discord <CODE>          # Discord-Pairing bestätigen
```

---

## Security

```bash
openclaw token:rotate --force --length 64        # Gateway-Token rotieren
openclaw security audit --deep                   # Tiefes Sicherheitsaudit
openclaw doctor --run doctor                     # DM-Policy prüfen

# Exposed-Secrets-Check (manuell):
grep -r "sk-" ~/.openclaw/                       # Sollte nichts in Logs finden
grep -r "ANTHROPIC_API_KEY" ~/.openclaw/workspace/
```

---

## Setup & Onboarding

```bash
openclaw onboard                      # Setup-Wizard erneut ausführen (interaktiv)
openclaw setup                        # Workspace-Dateien erstellen (AGENTS.md etc.)
openclaw setup --workspace <path>     # Fehlende Workspace-Dateien an bestimmtem Pfad erzeugen
```

---

## Update & Versioning

```bash
# Version anzeigen
openclaw --version
# Format: YYYY.M.D-N (CalVer)

# Update (pnpm empfohlen):
pnpm add -g openclaw@latest && pnpm approve-builds -g && openclaw doctor

# Alternative (npm):
npm install -g openclaw@latest && openclaw doctor

# Beta-Channel:
pnpm add -g openclaw@beta && pnpm approve-builds -g

# Release-Tags:
#   stable  = npm dist-tag "latest"   → getaggte Releases (vYYYY.M.D)
#   beta    = npm dist-tag "beta"     → Prerelease (vYYYY.M.D-beta.N)
#   dev     = main Branch (kein Tag)
```

---

## Dashboard & TUI

```bash
openclaw dashboard                    # Browser-UI öffnen (http://127.0.0.1:18789)
openclaw dashboard --no-open          # URL ausgeben ohne Browser zu öffnen
openclaw tui                          # Terminal-UI starten
```

Das Dashboard bietet:
- WebChat-Interface
- Session-Debugging
- Config-Verwaltung
- Health-Monitoring
- Token-Eingabe (Settings → Token)
