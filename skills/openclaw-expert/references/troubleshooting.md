# Troubleshooting — Häufige Probleme & Lösungen

## Diagnose-Grundlagen

```bash
# IMMER zuerst:
openclaw --version
openclaw doctor
openclaw status

# Logs lesen:
journalctl --user -u openclaw-gateway -n 50 --no-pager
# oder:
tail -n 120 /tmp/openclaw-gateway.log
# Docker:
docker compose logs -f openclaw-gateway
```

---

## Gateway startet nicht nach Config-Änderung

```bash
# 1. Config validieren
openclaw doctor

# 2. JSON5-Syntax prüfen
node -e "require('fs').readFileSync(process.env.HOME+'/.openclaw/openclaw.json','utf8')" && echo "OK"

# 3. Logs analysieren
journalctl --user -u openclaw-gateway -n 50 --no-pager
tail -n 120 /tmp/openclaw-gateway.log

# 4. Port belegt?
ss -ltnp | grep 18789

# 5. Backup wiederherstellen
cp ~/.openclaw/openclaw.json.bak ~/.openclaw/openclaw.json
systemctl --user restart openclaw-gateway
```

**Häufigste Ursache**: Unbekannter Key oder falscher Typ in openclaw.json.
JSON5 erlaubt Kommentare, aber keine unbekannten Felder!

---

## "systemctl --user unavailable"

```bash
# Falsch: Als root eingeloggt
# Richtig: Als openclaw-User einloggen
ssh openclaw@<server-ip>

# Dann:
openclaw gateway install
systemctl --user start openclaw-gateway
systemctl --user enable openclaw-gateway

# Wenn lingering fehlt:
loginctl enable-linger openclaw
```

---

## Modell hinzufügen schlägt fehl

```bash
# Fallstricke:
# 1. "id" muss "provider/model-name" Format haben
# 2. Bei OpenRouter-Style IDs: Provider-Prefix dazu!
#    z.B. "openrouter/moonshotai/kimi-k2"
# 3. "api": "openai-completions" vs "openai-responses" (versionsabhängig!)
# 4. "contextWindow" und "maxTokens" müssen Zahlen sein, keine Strings!
# 5. Ollama in Docker: baseUrl = "http://host.docker.internal:11434"
```

---

## Node verbindet nicht

```bash
openclaw nodes status
openclaw channels status --probe

# Gateway muss von Node erreichbar sein:
# - Tailscale: gateway.bind auf "tailscale" setzen
# - Lokales Netz: gateway.bind auf "lan" (nur mit VPN!)
# - Port 18789 muss erreichbar sein
```

---

## Skills werden nicht geladen

```bash
# Skills erst in neuer Session aktiv!
openclaw gateway restart

# Dann prüfen:
openclaw skills list

# Skill-Verzeichnisse prüfen:
ls ~/.openclaw/workspace/skills/    # Workspace-Skills
ls ~/.openclaw/skills/              # Managed-Skills

# Nur 1 von N Skills sichtbar?
# → SKILL.md prüfen:
#   - YAML-Frontmatter mit name + description?
#   - Kein Syntax-Fehler im YAML?
#   - Doppelpunkte in description mit Quotes escapen!
```

---

## Heartbeat-Probleme

### Heartbeat-Model-Bug (Issue #22133)
```
Symptom: Main-Session plötzlich mit 16k Context statt 200k
Ursache: heartbeat.model überschreibt main-Session-Model
Fix: heartbeat.model entfernen oder auf gleiches Model setzen
Workaround: /new in Telegram → Modell wird zurückgesetzt
```

### Heartbeat verbraucht zu viele Tokens
```json5
agent: {
  heartbeat: {
    every: "6h",       // Von "30m" auf "6h" reduzieren
    // oder:
    every: "off",      // Heartbeat komplett deaktivieren
  },
}
```

---

## Memory-Probleme

### Memory wird nicht gefunden
```bash
# memorySearch aktiv?
openclaw config get agents.defaults.memorySearch.enabled

# Embedding-Provider konfiguriert?
# Auto-Detect: local → openai → gemini
# Manuell prüfen: API-Key für Embeddings vorhanden?

# Erster Aufruf langsam → QMD lädt GGUF-Modelle herunter
```

### Memory geht bei Compaction verloren
```json5
// memoryFlush aktivieren:
agents: {
  defaults: {
    compaction: {
      memoryFlush: { enabled: true },
    },
  },
}
```

### MEMORY.md wird in Gruppen geladen (Datenschutz!)
→ Das sollte NICHT passieren. MEMORY.md wird nur in privaten Sessions geladen.
Falls doch: `openclaw doctor` + Version updaten.

---

## WhatsApp-Probleme

| Problem | Lösung |
|---|---|
| QR-Code abgelaufen | `openclaw channels login` erneut |
| Bot antwortet nicht | `openclaw channels status --probe` |
| Fremde können schreiben | `dmPolicy: "allowlist"` + `allowFrom` prüfen |
| Bot in Gruppen zu geschwätzig | Gruppen-Verhalten in AGENTS.md regeln |

---

## Performance-Probleme

| Problem | Lösung |
|---|---|
| Langsame Antworten | Model-Latenz prüfen, ggf. kleineres Model |
| Hohe Kosten | Heartbeat-Intervall erhöhen, günstigeres Model |
| Docker langsam auf macOS | npm-Installation statt Docker nutzen |
| Context-Compaction zu häufig | Größeres Model-Context-Window nutzen |
| Memory-Search langsam | Erster Aufruf = Model-Download, danach schneller |

---

## Notfall: Komplett zurücksetzen

```bash
# 1. Gateway stoppen
systemctl --user stop openclaw-gateway

# 2. Backup (!)
tar czf ~/openclaw-emergency-backup-$(date +%Y%m%d).tar.gz ~/.openclaw/

# 3. Config zurücksetzen
openclaw onboard    # Wizard erneut durchlaufen

# 4. Oder: Backup-Config wiederherstellen
cp ~/.openclaw/openclaw.json.bak ~/.openclaw/openclaw.json

# 5. Neu starten
systemctl --user start openclaw-gateway
openclaw doctor
```
