# Dashboard / Control UI — Vollständige Referenz

## Zugriff

```
http://127.0.0.1:18789/         # Lokal
https://<host>.ts.net/           # Via Tailscale Serve
```

Config: `gateway.controlUi.enabled: true` (Default)

---

## Sidebar-Navigation

### 💬 Chat
WebChat direkt im Browser. Gleiche Funktionen wie Telegram/WhatsApp.
Nützlich für Tests, Debug und wenn kein Kanal eingerichtet ist.
Unterstützt Media-Upload, Slash-Commands, Streaming.

### Control-Bereich

**📊 Overview** — Gateway-Status, aktive Sessions, Channels, Primary Model, Uptime, Version, Token-Übersicht.

**🔗 Channels** — Liste aller Channels mit Status (connected/error/disabled). Aktionen: Restart, Disconnect. WhatsApp-QR für Pairing. Telegram-Webhook-Status.

**((o)) Instances** — Laufende Gateway-Instanzen mit PID, Startzeit. Meist nur 1 Instanz.

**📄 Sessions** — Aktive + archivierte Sessions. Filter nach Channel/Agent/Zeitraum. Pro Session: Model, Tokens, Kosten. Aktionen: Inspect, Compact, Clean.

**📊 Usage** — Token-Verbrauch pro Modell/Provider. Kosten-Aufschlüsselung. Heartbeat-Kosten separat.

**✨ Cron Jobs** — Heartbeat-Status, Verlauf, nächster geplanter Run. Webhook-Wakeups.

### Agent-Bereich

**📁 Agents** — Agent-Liste (Multi-Agent). Bindings (Channel → Agent). Workspace-Dateien anzeigen/editieren.

**⚡ Skills** — Installierte Skills (Bundled/Managed/Workspace). Status, ClawHub-Suche, Reload.

**🖥️ Nodes** — Verbundene Nodes mit Capabilities. Pairing genehmigen/ablehnen. Details: Typ, IP, Last Seen.

### Settings-Bereich

**⚙️ Config** — openclaw.json im Browser editieren. JSON5-Highlighting, Validierung, Hot-Reload.

**🔧 Debug** — Echtzeit-Event-Stream. Tool-Aufrufe mit I/O. Session-State. Agent-Reasoning.

**📋 Logs** — Gateway-Logs mit Level-Filter (error/warn/info/debug). Echtzeit-Streaming.

### Resources

**📖 Docs** — Link zur offiziellen Dokumentation.

---

## Dashboard-Konfiguration

### CORS für Tailscale (PFLICHT bei Serve!)
```json5
{
  gateway: {
    controlUi: {
      allowedOrigins: ["https://hostname.taildcb944.ts.net"],
    },
  },
}
```

### Custom Base Path
```json5
{ gateway: { controlUi: { basePath: "/dashboard/" } } }
```

### Assets bauen (Git-Installation)
```bash
pnpm install && pnpm build:control-ui
ls dist/control-ui/    # Prüfen: index.html vorhanden?
```

npm/pnpm-Installation: Assets bereits enthalten.

---

## Troubleshooting

| Problem | Lösung |
|---|---|
| Leere Seite | `pnpm build:control-ui` |
| CORS-Fehler | `allowedOrigins` setzen |
| Auth-Fehler | Token prüfen, `allowTailscale` + `trustedProxies` |
| "device identity required" | HTTPS nötig → Tailscale Serve |
| Port nicht erreichbar | `ss -tlnp \| grep 18789` |
| WebSocket-Fehler | `trustedProxies: ["100.64.0.0/10"]` |
