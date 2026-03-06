# Tricks & Hacks — Power-User-Tipps

## Kosten-Optimierung

### Token-Verbrauch senken
```json5
agent: {
  heartbeat: {
    every: "6h",     // Statt "30m" → spart 90%+ der Heartbeat-Kosten
  },
},
agents: {
  defaults: {
    compaction: {
      mode: "safeguard",       // Kompaktiert intelligent
      reserveTokensFloor: 20000,
    },
  },
}
```

### Hybrid-Modell-Strategie
- **Heartbeat + Simple Tasks**: Günstiges lokales Model (Ollama/llama3.2)
- **Komplexe Aufgaben**: Claude Sonnet/Opus via API
- **ACHTUNG**: heartbeat.model Bug kann in main-Session bluten (Issue #22133)

### Zero-Token-Wartung
Direkt per SSH/VS Code Dateien bearbeiten statt Bot-Befehle:
```bash
# SSH-Zugriff für Cursor/VS Code:
# File → New Window → Connect with SSH → user@server
# Dann SOUL.md, Skills, Configs direkt editieren = 0 Token-Kosten
```

---

## Produktivitäts-Hacks

### Web-Prototyping on the go
```
Prompt an Bot: "Recherchiere X, mach mir eine HTML-Seite und hoste sie auf Surge"
```
→ Bot erstellt und deployed eine Webseite, teilbar per Link

### Obsidian-Integration
- Obsidian Vault ($5/mo) auf OpenClaw-Maschine einrichten
- Agent kann in Vault lesen und schreiben
- Persönlicher Knowledge-Graph + Task-Management per Chat
→ WhatsApp/Voicenote → Agent durchsucht Vault → Antwort

### Session-Management
```
/status    — Was läuft gerade? (Model, Tokens, Kosten)
/new       — Frische Session (bei verwirrendem Kontext)
/compact   — Manuell kompaktieren (bei langer Session)
```

### Memory-Tricks
```
# Explizit Memory schreiben lassen:
"Merke dir in USER.md, dass ich kurze Antworten mit Code-Beispielen will"
"Schreibe in MEMORY.md: Projekt X nutzt Docker Compose auf Contabo"
"Aktualisiere memory/ mit der heutigen Entscheidung zu Y"

# Memory-Review forcieren:
"Lies MEMORY.md und entferne alles was veraltet ist"
"Konsolidiere die letzten 7 Tage aus memory/ in MEMORY.md"
```

---

## Fortgeschrittene Config-Tricks

### Mehrere Workspaces testen
```bash
# Workspace-A für Produktion, Workspace-B zum Testen
cp -r ~/.openclaw/workspace ~/.openclaw/workspace-test
# In openclaw.json temporär umschalten:
# agents.defaults.workspace: "~/.openclaw/workspace-test"
# ACHTUNG: Nur EIN aktiver Workspace — sonst State-Drift!
```

### Custom System-Prompt über AGENTS.md
```markdown
# In AGENTS.md hinzufügen:
## Antwort-Format
- Immer zuerst eine Zusammenfassung in einem Satz
- Dann technische Details
- Code-Beispiele mit Kommentaren
- Sprache: Deutsch, Tech-Begriffe auf Englisch OK
```

### Crash-Recovery-Watchdog
```bash
# systemd-Watchdog (automatischer Neustart bei Crash):
# ~/.config/systemd/user/openclaw-gateway.service
[Service]
Restart=always
RestartSec=10
WatchdogSec=300
```

### Logging nach Supabase
- Supabase Free-Tier als Logging-Backend
- Dashboard zeigt jede Interaktion
- Kosten-Monitoring bei API-Key-Kompromittierung
- Bot kann Supabase-Setup selbst konfigurieren

---

## Workspace Git-Workflow

```bash
# Automatisches Backup nach jeder Änderung
cd ~/.openclaw/workspace

# .gitignore für sensible Daten
cat > .gitignore << 'EOF'
# Keine Credentials committen!
*.key
*.token
*.secret
EOF

# Pre-Commit-Hook für automatische Backups
cat > .git/hooks/post-commit << 'EOF'
#!/bin/bash
git push origin main 2>/dev/null || true
EOF
chmod +x .git/hooks/post-commit
```

---

## Nützliche Einzeiler

```bash
# Alle aktiven Sessions mit Kosten anzeigen
openclaw sessions list

# Config-Diff nach Änderung
diff ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak

# Memory-Größe prüfen
wc -l ~/.openclaw/workspace/MEMORY.md
du -sh ~/.openclaw/workspace/memory/

# Alte Memory-Dateien aufräumen (älter als 30 Tage)
find ~/.openclaw/workspace/memory/ -name "*.md" -mtime +30 -ls

# Gateway-Health-Check (API)
curl -s http://127.0.0.1:18789/health

# Alle Channels auf einmal testen
openclaw channels status --probe

# Exposed Secrets finden
grep -rn "sk-\|api_key\|token\|secret" ~/.openclaw/workspace/ --include="*.md"
```

---

## Integration mit anderen Tools

### n8n-Webhooks
- OpenClaw kann Webhooks empfangen/senden
- n8n-Workflow → Webhook → OpenClaw verarbeitet → Antwort an Channel
- Nützlich für: E-Mail-Zusammenfassungen, RSS-Alerts, Monitoring

### Tailscale für Remote-Zugriff
```json5
gateway: {
  mode: "tailscale",
  bind: "tailscale",    // Nur über Tailscale-Netzwerk erreichbar
}
```
→ Dashboard + WebChat von überall erreichbar, aber sicher

### Docker Model Runner (komplett lokale LLMs)
```bash
# Docker Model Runner + OpenClaw in Docker Sandbox
# = 0 API-Kosten, volle Privatsphäre
docker model pull llama3.2:latest
# OpenClaw zeigt alle Docker Model Runner Modelle automatisch
```

---

## "Erste Woche"-Leitfaden

1. **Tag 1-2**: Nur chatten. Wetter fragen, Artikel zusammenfassen, Smalltalk.
2. **Tag 3**: SOUL.md und USER.md anpassen. Ton und Präferenzen definieren.
3. **Tag 4**: Erste echte Aufgabe: E-Mail-Draft, Code-Review, Recherche.
4. **Tag 5**: HEARTBEAT.md einrichten. Regelmäßige Check-ins definieren.
5. **Tag 6**: Memory-System testen. "Merke dir X", am nächsten Tag prüfen.
6. **Tag 7**: Ersten Custom-Skill erstellen oder ClawHub-Skill installieren.

→ Nach einer Woche Korrekturen klingt dein Agent komplett anders als am Anfang.
   **Das ist der Punkt.**

---

## Bekannte Gotchas (Stand 02/2026)

1. **heartbeat.model Bug** → Kann main-Session-Model überschreiben (#22133)
2. **Skills nur in neuer Session** → Nach install/reload: Gateway restart ODER /new
3. **Mehrere Workspaces** → `openclaw doctor` warnt, nur einen aktiv halten
4. **WhatsApp DM-Policy** → Global pro Account, nicht pro Agent
5. **MEMORY.md in Groups** → Sollte nie passieren, falls doch: Update + Doctor
6. **Docker macOS** → Langsamer als npm direkt, nur nutzen wenn Isolation nötig
7. **Context-Window** → Heartbeat kann mit 16k Model Context-Compaction-Loop auslösen
8. **Supabase-Leak (historisch)** → Moltbook-Incident Januar 2026, inzwischen gefixt
