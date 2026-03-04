# Installation & Erste Schritte

## Voraussetzungen
- Node.js 22+ (required)
- macOS, Linux, oder Windows (via WSL2, dringend empfohlen)
- 2 GB RAM minimum (4 GB empfohlen)
- 10 GB+ Disk

---

## Methode 1: npm/pnpm (empfohlen für lokale Nutzung)

```bash
# pnpm (empfohlen):
corepack enable
pnpm add -g openclaw@latest
pnpm approve-builds -g

# oder npm:
npm install -g openclaw@latest

# Onboarding-Wizard starten:
openclaw onboard
```

Der Wizard fragt ab:
1. Gateway bind-Modus (→ `loopback` wählen!)
2. Auth-Modus (→ `token` wählen!)
3. Gateway-Token
4. Tailscale? (→ Off, es sei denn du nutzt Tailscale)
5. AI-Provider (Anthropic/OpenAI/Ollama)
6. API-Key
7. Channel-Setup (WhatsApp/Telegram/Discord)
8. Gateway als Daemon installieren?

Nach dem Wizard:
```bash
openclaw doctor        # Check
openclaw status        # Status
openclaw dashboard     # Browser-UI
```

---

## Methode 2: Docker (empfohlen für VPS/Server)

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
bash docker-setup.sh
```

Das Script:
1. Baut das Docker-Image
2. Startet den Onboarding-Wizard (interaktiv)
3. Konfiguriert Docker Compose
4. Startet den Gateway-Container

### Docker-Compose-Befehle
```bash
# Gateway starten
docker compose up -d openclaw-gateway

# CLI-Befehle ausführen
docker compose run --rm openclaw-cli doctor
docker compose run --rm openclaw-cli channels add --channel telegram --token <TOKEN>
docker compose run --rm openclaw-cli dashboard --no-open

# Logs
docker compose logs -f openclaw-gateway

# Shell im Container
docker compose exec openclaw-gateway bash
# Als root (für Paketinstallation):
docker compose exec -u root openclaw-gateway bash
```

### Alternative Docker-Images
```bash
# Alpine-basiertes Community-Image:
docker pull alpine/openclaw:latest

# Phioranex Community-Image mit install-Script:
curl -fsSL https://raw.githubusercontent.com/phioranex/openclaw-docker/main/install.sh | sudo bash
```

### Docker-Volumes
```
~/.openclaw           → /home/node/.openclaw     (Config, Sessions, Credentials)
~/openclaw/workspace  → /home/node/.openclaw/workspace (Agent-Workspace)
```

### Docker + Ollama (lokale Modelle)
```json5
// In openclaw.json:
models: {
  providers: {
    ollama: {
      // Auf macOS mit Docker Desktop:
      baseUrl: "http://host.docker.internal:11434",
      // Auf Linux:
      baseUrl: "http://172.17.0.1:11434",
    },
  },
},
```

---

## Methode 3: DigitalOcean 1-Click

DigitalOcean bietet ein vorkonfiguriertes Droplet-Image mit:
- OpenClaw vorinstalliert
- Docker-Container-Isolation
- Non-Root-User-Execution
- Hardened Firewall

---

## Methode 4: Docker Sandbox (maximale Isolation)

```bash
docker sandbox create --name my-openclaw shell .
docker sandbox network proxy my-openclaw --allow-host localhost
docker sandbox run my-openclaw
# Im Sandbox:
npm install -g n && n 22
hash -r
npm install -g openclaw@latest
openclaw setup
```

Vorteile: Micro-VM-Isolation, API-Key-Injection über Network-Proxy (Keys nie im Container).

---

## Nach der Installation

1. **API-Key einrichten**: Provider wählen (Anthropic empfohlen)
2. **Channel verbinden**: Mindestens einen Messaging-Kanal einrichten
3. **Pairing durchführen**: `openclaw pairing approve <channel> <code>`
4. **Workspace personalisieren**: SOUL.md, USER.md, AGENTS.md anpassen
5. **Security-Check**: `openclaw doctor`, dmPolicy auf `allowlist` prüfen
6. **Test-Nachricht senden**: Im gewählten Kanal den Bot anschreiben

---

## Update

```bash
# pnpm (empfohlen):
pnpm add -g openclaw@latest && pnpm approve-builds -g && openclaw doctor

# npm:
npm install -g openclaw@latest && openclaw doctor

# Docker:
cd openclaw && git pull && bash docker-setup.sh
```

**Nach jedem Update**: `openclaw doctor` ausführen!
