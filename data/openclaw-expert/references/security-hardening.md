# Security-Hardening — OpenClaw absichern

## Threat Model

OpenClaw hat **volle Kontrolle über den Rechner** — kann Dateien erstellen/löschen,
Software installieren, Skripte ausführen, Internet-Dienste kontaktieren.
Deshalb: Isolation und Least-Privilege sind Pflicht.

---

## Checkliste (Minimum-Sicherheit)

```bash
# 1. Gateway nur lokal binden
openclaw config set gateway.bind loopback

# 2. DM-Policy auf Allowlist
openclaw config set dmPolicy.mode allowlist
# Eigene User-IDs eintragen!

# 3. Token rotieren (64+ Zeichen)
openclaw token:rotate --force --length 64

# 4. Credentials schützen
chmod 600 ~/.openclaw/credentials/*

# 5. Doctor prüft Security-Config
openclaw doctor
openclaw doctor --run doctor    # DM-Policy-Check
openclaw security audit --deep  # Tiefes Audit
```

---

## Gateway-Sicherheit

| Setting | Sicher | Gefährlich |
|---|---|---|
| `gateway.bind` | `loopback` | `lan`, `0.0.0.0` |
| `gateway.auth.mode` | `token` | `none` |
| `dmPolicy.mode` | `allowlist` | `open` |
| `tools.exec.host` | `sandbox` | `gateway` |
| `tools.exec.security` | `full` | `relaxed` |

### Remote-Zugriff (wenn nötig)
- **Tailscale** (empfohlen): `gateway.mode: "tailscale"`, `gateway.bind: "tailscale"`
- **SSH-Tunnel**: `ssh -L 18789:127.0.0.1:18789 user@server`
- **NIEMALS** Port 18789 direkt ins Internet exponieren!

---

## DM-Policy

```json5
dmPolicy: {
  mode: "allowlist",         // PFLICHT in Produktion
  allowed_ids: [             // Nur deine User-IDs
    "+491234567890",
    "telegram:123456789",
  ],
  reject_action: "silent_drop",  // Abgelehnte Nachrichten still verwerfen
  log_rejections: true,          // Für Audit-Log
}
```

**Bei `open`**: Jeder kann dem Bot schreiben und Befehle ausführen!

---

## Skill-Sicherheit

Skills sind die größte Angriffsfläche:
- **26% der Community-Skills** enthalten laut Cisco mindestens eine Schwachstelle
- Skills können Prompt-Injections, Tool-Poisoning, versteckte Malware enthalten

### Vor Installation:
1. Quellcode auf GitHub/ClawHub reviewen
2. "Hide Suspicious" auf ClawHub aktivieren
3. VirusTotal-Report auf der ClawHub-Seite prüfen
4. Code in Claude/GPT einfügen und nach Risiken fragen
5. Unbekannte Skills erst in Sandbox testen

### Skill-Sandbox:
```json5
tools: {
  exec: {
    host: "sandbox",     // Skills in Docker-Sandbox ausführen
  },
}
```

---

## API-Key-Management

```bash
# Keys NIE in Workspace-Dateien speichern!
# Keys NIE in öffentliche Repos pushen!

# Secrets-Check:
grep -r "sk-" ~/.openclaw/
grep -r "ANTHROPIC_API_KEY" ~/.openclaw/workspace/
# → Sollte nichts finden

# API-Spending-Limits beim Provider setzen!
# Heartbeat alle 30min kann $0.50-2.00/Tag kosten
```

### Für Fortgeschrittene: Doppler Secrets-Manager
- API-Keys nicht in Config hardcoden
- Über Environment-Variables injizieren
- `openclaw config set` für Key-Referenzen nutzen

---

## Betriebssystem-Härtung

```bash
# Eigenen User für OpenClaw anlegen
sudo adduser --system --home /home/openclaw openclaw

# Firewall (ufw)
sudo ufw default deny incoming
sudo ufw allow ssh
# Port 18789 NICHT freigeben (nur loopback!)

# Nicht als root betreiben!
# ssh openclaw@server, dann openclaw-Befehle
```

---

## Sandbox-Konfiguration

```json5
docker: {
  network: "none",           // Kein Netzwerk in Sandbox (sicherste Option)
  // Für Skills die Internet brauchen:
  // network: "bridge",
},

tools: {
  exec: {
    host: "sandbox",         // Tools in Docker-Container ausführen
    ask: "on",               // Bestätigung vor jeder Tool-Ausführung
    security: "full",
  },
},
```

### Sandbox-Limitierungen
- Default: kein Netzwerk (`network: "none"`)
- `setupCommand` braucht `network != "none"` und `user: "0:0"` für apt-get
- OpenClaw erstellt Container neu wenn sich `setupCommand` oder Docker-Config ändert

---

## Audit & Monitoring

```bash
# Regelmäßiger Security-Check
openclaw security audit --deep

# Logs überwachen
journalctl --user -u openclaw-gateway -f

# Rejected DMs prüfen (wenn log_rejections: true)
grep "reject" /tmp/openclaw-gateway.log

# Session-Kosten überwachen
# /status im Chat → zeigt Tokens und Kosten
```

---

## Empfohlene Architektur für VPS

```
VPS (Contabo/Hetzner/DO)
├── Docker-Container: openclaw-gateway
│   ├── Non-root user (node)
│   ├── Gateway bind: loopback
│   └── Sandbox für Tools
├── ufw: nur SSH erlaubt
├── Tailscale: für Remote-Dashboard-Zugriff
└── Separater User: kein Zugriff auf Prod-Daten
```
