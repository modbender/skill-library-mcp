# Praxis-Beispiele — Typische OpenClaw-Setups

## Beispiel 1: Minimal-Setup für Einsteiger (VPS + Telegram)

**Szenario**: Contabo VPS, Telegram als einziger Kanal, Claude als Modell.

### Config
```json5
// ~/.openclaw/openclaw.json
{
  gateway: {
    bind: "loopback",
    auth: {
      mode: "token",
      token: "$(openssl rand -hex 32)",
    },
  },
  channels: {
    telegram: {
      enabled: true,
      adapter: "telegram",
      // Token via: @BotFather → /newbot
    },
  },
  models: {
    default: "anthropic/claude-sonnet-4-20250514",
  },
  agent: {
    heartbeat: {
      enabled: false,           // Anfangs deaktiviert (spart Tokens)
    },
  },
}
```

### AGENTS.md (minimal)
```markdown
# Betriebsanweisungen

Du bist mein persönlicher Assistent. Antworte auf Deutsch.
Sei hilfreich, präzise und freundlich.
Bestätige destruktive Aktionen vor der Ausführung.
```

### SOUL.md (minimal)
```markdown
# Persönlichkeit
- Professionell, freundlich, direkt
- Deutsch als Standard
- Verwende gelegentlich das Lobster-Emoji 🦞
```

### Erste Schritte
```bash
# 1. Installieren
curl -fsSL https://get.openclaw.ai | bash

# 2. Wizard durchlaufen (Token, Model, Telegram-Bot)
openclaw setup

# 3. Gateway starten
openclaw gateway install   # systemd service
openclaw gateway start

# 4. Health Check
openclaw doctor
openclaw channels status --probe

# 5. In Telegram Bot anschreiben → Fertig!
```

---

## Beispiel 2: VPS + Tailscale + MacBook-Node

**Szenario**: Gateway auf Hetzner VPS, MacBook als Node für Browser-Automation.

### VPS-Setup
```bash
# Tailscale installieren
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
tailscale ip -4   # z.B. 100.64.x.x
```

### Config auf VPS
```json5
{
  gateway: {
    bind: "loopback",
    tailscale: {
      mode: "serve",
      resetOnExit: false,
    },
    auth: {
      mode: "token",
      token: "<token>",
      allowTailscale: true,
    },
    controlUi: {
      enabled: true,
    },
  },
  channels: {
    telegram: { enabled: true, adapter: "telegram" },
    whatsapp: { enabled: true, adapter: "whatsapp" },
  },
  models: {
    default: "anthropic/claude-sonnet-4-20250514",
    heartbeat: "anthropic/claude-haiku-3-20250307",  // Günstig für Heartbeat
  },
}
```

### MacBook einrichten
```bash
# 1. Tailscale installieren + einloggen
brew install tailscale
tailscale up

# 2. OpenClaw macOS App installieren
brew install --cask openclaw

# 3. App öffnen → Settings → Gateway
#    URL: https://<vps>.your-tailnet.ts.net
#    → Connect → Pairing-Request wird erstellt

# 4. Auf VPS genehmigen:
openclaw devices list
openclaw devices approve <requestId>

# 5. Prüfen:
openclaw nodes status
# → MacBook sollte "connected" sein mit canvas.*, system.* Capabilities
```

### Browser-Automation testen
```
# In Telegram dem Bot schreiben:
"Öffne google.de und suche nach 'OpenClaw Tailscale Setup'"
# → Gateway sendet browser.* Befehle an MacBook-Node
```

---

## Beispiel 3: VPS + iPhone + Raspberry Pi

**Szenario**: Zentraler Gateway, iPhone für unterwegs, Pi für Smart-Home-Kontrolle.

### Architektur
```
Internet / Tailscale
        │
  ┌─────┴──────────────┐
  │  Hetzner VPS       │  Gateway + Telegram + WhatsApp
  │  100.64.0.1        │  Tailscale Serve
  └─────┬──────────────┘
        │
   ┌────┴──────────────────────┐
   │                           │
┌──┴───────────┐  ┌────────────┴──────┐
│  iPhone      │  │  Raspberry Pi 5   │
│  iOS App     │  │  Headless Node    │
│  100.64.0.2  │  │  100.64.0.3       │
│  Kamera,     │  │  system.run,      │
│  Canvas,     │  │  GPIO, Sensoren   │
│  Voice       │  │  Smart-Home       │
└──────────────┘  └───────────────────┘
```

### Pi als Headless Node einrichten
```bash
# 1. Raspberry Pi OS Lite (64-bit) installieren
# 2. SSH aktivieren, Updates
sudo apt update && sudo apt upgrade -y

# 3. Node.js 22+ installieren
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo bash -
sudo apt install -y nodejs

# 4. Tailscale
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# 5. OpenClaw (nur Node-Host, kein Gateway!)
npm install -g openclaw@latest

# 6. Node-Host starten
openclaw node host \
  --gateway wss://<vps>.your-tailnet.ts.net \
  --token <gateway-token>

# 7. Auf VPS genehmigen:
openclaw devices approve <requestId>
```

### Pi Node als systemd-Service
```ini
# ~/.config/systemd/user/openclaw-node.service
[Unit]
Description=OpenClaw Node Host
After=network-online.target

[Service]
ExecStart=%h/.npm-global/bin/openclaw node host \
  --gateway wss://<vps>.your-tailnet.ts.net \
  --token <gateway-token>
Restart=always
RestartSec=10
Environment=NODE_ENV=production

[Install]
WantedBy=default.target
```

```bash
# loginctl enable-linger nötig für --user services!
loginctl enable-linger $USER
systemctl --user daemon-reload
systemctl --user enable --now openclaw-node
```

### iPhone verbinden
1. OpenClaw iOS App installieren
2. Tailscale iOS App installieren + einloggen
3. In Telegram dem Bot schreiben: `/pair`
4. Setup-Code kopieren → iOS App → Settings → Gateway → Code einfügen
5. Auf VPS: `openclaw devices approve <requestId>`

---

## Beispiel 4: Multi-Agent mit getrennten Workspaces

**Szenario**: Ein persönlicher Agent + ein Arbeits-Agent auf demselben Gateway.

### Config
```json5
{
  agents: {
    list: [
      {
        agentId: "alex-privat",
        name: "Lobster 🦞",
        agentDir: "~/.openclaw/agents/alex-privat",
        workspaceDir: "~/.openclaw/workspaces/privat",
      },
      {
        agentId: "alex-arbeit",
        name: "WorkBot 🏢",
        agentDir: "~/.openclaw/agents/alex-arbeit",
        workspaceDir: "~/.openclaw/workspaces/arbeit",
      },
    ],
  },
  bindings: {
    // Telegram → Privat-Agent
    "telegram:*": { agentId: "alex-privat" },
    // Slack → Arbeits-Agent
    "slack:*": { agentId: "alex-arbeit" },
    // WhatsApp → Privat (default)
    "whatsapp:*": { agentId: "alex-privat" },
    // WhatsApp Arbeitsgruppe → Arbeits-Agent
    "whatsapp:group:ArbeitsGruppe": { agentId: "alex-arbeit" },
  },
}
```

**Regel**: Nie `workspaceDir` zwischen Agents teilen!

---

## Beispiel 5: Kosten-optimiertes Setup

**Szenario**: Monatliche API-Kosten unter 20€ halten.

### Strategie
```json5
{
  models: {
    // Hauptmodell: Gutes Preis-Leistung
    default: "anthropic/claude-sonnet-4-20250514",
    // Heartbeat: Billigstes Modell
    heartbeat: "anthropic/claude-haiku-3-20250307",
  },
  agent: {
    heartbeat: {
      enabled: true,
      interval: "4h",          // Nur alle 4 Stunden (statt default 1h)
    },
    session: {
      compaction: {
        maxTokens: 80000,       // Früher compacten
      },
    },
  },
}
```

### HEARTBEAT.md (Minimal!)
```markdown
## Heartbeat-Aufgaben
- [ ] Prüfe ob neue Nachrichten in meinen Channels warten
```
Mehr Tasks = mehr Token-Verbrauch pro Heartbeat!

### Kosten-Monitoring
```bash
# Token-Verbrauch aktueller Session
# In Telegram:
/status

# Historische Kosten (wenn vom Provider unterstützt)
openclaw sessions list --costs
```

### Spar-Tricks
1. **Heartbeat deaktivieren** wenn nicht nötig: `heartbeat.enabled: false`
2. **SSH statt Heartbeat** für Maintenance: Gateway direkt ansprechen
3. **Compaction-Limit senken**: Weniger Context = weniger Tokens
4. **Günstige Modelle für Routing**: `models.heartbeat` separat setzen
5. **Skills minimal halten**: Weniger geladene Skills = weniger System-Prompt-Tokens

---

## Beispiel 6: Sicheres Setup mit Docker-Sandbox

**Szenario**: Maximale Isolation — Agent kann Host nicht beschädigen.

### docker-compose.yml
```yaml
services:
  openclaw:
    image: ghcr.io/openclaw/openclaw:latest
    container_name: openclaw
    restart: unless-stopped
    user: "1000:1000"
    volumes:
      - ./data:/home/openclaw/.openclaw
    environment:
      - OPENCLAW_GATEWAY_TOKEN=${GATEWAY_TOKEN}
      - OPENCLAW_GATEWAY_PASSWORD=${GATEWAY_PASSWORD}
    ports:
      - "127.0.0.1:18789:18789"
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
    networks:
      - openclaw-net

networks:
  openclaw-net:
    driver: bridge
```

### Sandbox-Config
```json5
{
  gateway: {
    bind: "loopback",
    auth: { mode: "token" },
  },
  agent: {
    sandbox: {
      enabled: true,
      // Agent-Prozesse laufen im Docker-Container
      // Host-Zugriff ist vollständig blockiert
    },
  },
}
```

---

## Beispiel 7: iMessage via BlueBubbles + Linux Gateway

**Szenario**: Gateway auf Linux VPS, iMessage über einen Mac zuhause.

### Architektur
```
VPS (Linux)                    Mac mini (zuhause)
┌─────────────────┐           ┌─────────────────┐
│  OpenClaw       │◄──────────│  BlueBubbles     │
│  Gateway        │ Tailscale │  Server          │
│  (kein macOS    │           │  (signed into    │
│   nötig!)       │           │   Messages)      │
└─────────────────┘           └─────────────────┘
```

### Schritte
1. BlueBubbles auf Mac installieren (https://bluebubbles.app)
2. BlueBubbles-Server starten (Mac muss eingeloggt + online bleiben)
3. Beide Geräte im selben Tailnet
4. In openclaw.json:
```json5
{
  channels: {
    imessage: {
      enabled: true,
      adapter: "bluebubbles",
      // BlueBubbles-Server-URL über Tailscale
      host: "http://<mac-tailscale-ip>:1234",
      password: "<bluebubbles-password>",
    },
  },
}
```

---

## Cheat-Sheet: Welches Setup für welchen Zweck?

| Zweck | Gateway | Nodes | Channels | Tailscale |
|---|---|---|---|---|
| Einsteiger / Test | Lokal oder VPS | Keine | Telegram | Optional |
| Always-On Assistant | VPS | MacBook + iPhone | Telegram + WhatsApp | ✅ Serve |
| Smart Home | Raspberry Pi | Weitere Pi's | Telegram | ✅ Serve |
| Max Security | Docker auf VPS | Keine | WebChat only | ✅ Serve |
| Multi-Device | VPS | Mac + iPhone + Pi | Alle | ✅ Serve |
| Kosten-Mini | VPS (1€/Monat) | Keine | Telegram | SSH-Tunnel |
| iMessage | VPS (Linux) | Mac (BlueBubbles) | iMessage + Telegram | ✅ Serve |
