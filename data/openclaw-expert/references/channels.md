# Channels — Messaging-Kanäle einrichten & troubleshooten

## Übersicht

| Kanal | Adapter | Schwierigkeit | Besonderheiten |
|---|---|---|---|
| **Telegram** | grammY | ⭐ Einfach | Streaming, Reactions, Forum-Topics, Empfohlen |
| **WhatsApp** | Baileys | ⭐⭐ Mittel | QR-Pairing, selfChatMode, globale dmPolicy |
| **Discord** | discord.js | ⭐⭐ Mittel | Message Content Intent nötig |
| **Slack** | Bolt | ⭐⭐ Mittel | Socket Mode oder Events API |
| **Signal** | signal-cli | ⭐⭐⭐ Schwer | Java-Dependency, CLI-basiert |
| **iMessage** | BlueBubbles | ⭐⭐⭐ Schwer | Braucht Mac mit Messages-Login |
| **Teams** | Extension | ⭐⭐⭐ Schwer | Entra ID App-Registration |
| **Google Chat** | Chat API | ⭐⭐ Mittel | Google Cloud Projekt nötig |
| **Matrix** | Extension | ⭐⭐ Mittel | Homeserver + Access-Token |
| **WebChat** | Built-in | ⭐ Einfach | Im Dashboard integriert |

---

## Telegram — Vollständige Anleitung

### 1. Bot erstellen
1. `@BotFather` öffnen → `/newbot`
2. Name + Username (muss auf `bot` enden)
3. **Token sicher kopieren** (kein trailing Space!)
4. BotFather-Einstellungen:
```
/setdescription   → Kurzbeschreibung
/setabouttext      → About-Text
/setuserpic        → Profilbild
/setcommands       → start, new, status, help
/setprivacy        → Disable (für Gruppen ohne @mention)
/setjoingroups     → Enable
```

### 2. Minimal-Config
```json5
{
  channels: {
    telegram: {
      enabled: true,
      botToken: "123456789:AAH...",
      dmPolicy: "pairing",           // Default: Pairing-Flow
      groups: { "*": { requireMention: true } },
    },
  },
}
```

Env-Fallback: `TELEGRAM_BOT_TOKEN=...` (nur für Default-Account).
Telegram nutzt NICHT `openclaw channels login telegram`!

### 3. Vollständige Config (alle Felder)
```json5
{
  channels: {
    telegram: {
      enabled: true,
      botToken: "123:abc",
      dmPolicy: "allowlist",          // "pairing" | "allowlist" | "open" | "disabled"
      allowFrom: [7403482253],        // Numerische User-IDs! NICHT @username
      groupPolicy: "allowlist",       // "allowlist" | "open" | "disabled"
      groupAllowFrom: [7403482253],   // Separat von allowFrom (seit 2026.2.25)

      // Streaming
      streaming: "partial",           // "off" | "partial" | "block" | "progress"

      // Nachrichten-Formatierung
      textChunkLimit: 4000,           // Telegram-Limit (max 4096)
      chunkMode: "newline",           // "newline" = Absatz-Grenzen bevorzugen

      // Media
      mediaMaxMb: 50,                 // Default: 5 MB — erhöhen!

      // Timeouts & Retries
      timeoutSeconds: 30,             // Telegram API Timeout
      retry: { maxRetries: 3 },       // Outbound-API-Retries

      // History
      historyLimit: 50,               // Gruppen-Context-History (0 = aus)
      dmHistoryLimit: 100,            // DM-History

      // Reactions
      // ackReaction: "👀",           // Bestätigungs-Emoji beim Verarbeiten
      // "" = deaktiviert

      // Webhook (optional, statt Long-Polling)
      // webhookUrl: "https://yourdomain.com/telegram-webhook",
      // webhookSecret: "<secret>",
      // webhookPort: 8787,           // Default, lokal
      // webhookHost: "0.0.0.0",      // Nur wenn externer Ingress nötig

      // Sonstiges
      // linkPreview: false,          // Link-Vorschau deaktivieren
      // proxy: "http://proxy:8080",  // IPv6-Workaround
      // configWrites: true,          // Channel kann Config schreiben (Default)
    },
  },
}
```

### 4. Pairing-Workflow
```bash
# Gateway starten
openclaw gateway start

# Bot anschreiben → Pairing-Code erhalten
# Format: "Your Telegram user id: 123456789 Pairing code: ABCD1234"

# Genehmigen:
openclaw pairing approve telegram ABCD1234
# ODER mit User-ID:
openclaw pairing approve telegram:123456789 ABCD1234

# Code verfällt nach 1 Stunde!
```

Danach: Auf `allowlist` wechseln und User-ID in `allowFrom` eintragen.

### 5. User-ID herausfinden
```bash
# Methode 1: Logs lesen
openclaw logs --follow
# → "from.id" in Log-Ausgabe

# Methode 2: Updates API
curl "https://api.telegram.org/bot<TOKEN>/getUpdates" | jq '.result[-1].message.from.id'

# Methode 3: @userinfobot oder @getidsbot anschreiben
```

### 6. Gruppen einrichten

**Privacy Mode** (WICHTIG):

| Privacy Mode | Bot sieht in Gruppen |
|---|---|
| Enabled (Default) | Nur /commands und @mentions |
| Disabled | Alle Nachrichten |
| Bot ist Admin | Alle Nachrichten (unabhängig) |

```
@BotFather → /setprivacy → Disable
# DANN: Bot aus Gruppe entfernen + neu hinzufügen!
```

**Gruppen-Config**:
```json5
{
  channels: {
    telegram: {
      groups: {
        "*": { requireMention: true },       // Alle Gruppen: nur @mention
        "-1001234567890": {                   // Spezifische Gruppe
          requireMention: false,
          groupPolicy: "open",                // Jeder in dieser Gruppe
          allowFrom: [7403482253],
        },
      },
    },
  },
}
```

**Gruppen-ID finden**:
- Nachricht in Gruppe senden → `openclaw logs --follow` → Chat-ID ablesen
- Reguläre Gruppe: `-123456789`
- Supergruppe: `-1001234567890` (100-Prefix nach dem Minus!)
- **ID ändert sich bei Upgrade** auf Supergruppe! → Neues Pairing nötig

**Forum-Gruppen (Topics)**:
- Jedes Topic wird isoliert mit Thread-ID
- Per-Topic-Config-Overrides möglich
- General-Topic = `:topic:1`

### 7. Gruppen-Auth (seit 2026.2.25)
- `groupAllowFrom` ist separat von `allowFrom`
- Gruppen-Auth erbt NICHT DM-Pairing-Approvals
- Commands brauchen Auth auch bei `groupPolicy: "open"`

### 8. Streaming-Modi

| Modus | Verhalten |
|---|---|
| `off` | Keine Vorschau |
| `partial` | Nachricht wird progressiv editiert |
| `block` | Chunked als komplette Blöcke |
| `progress` | = `partial` (Kompatibilität) |

Reasoning-Stream: `/reasoning stream` → Reasoning in Live-Preview, finale Antwort ohne.

### 9. Long-Polling vs. Webhook

| | Long-Polling (Default) | Webhook |
|---|---|---|
| Setup | Kein public URL nötig | HTTPS-Endpoint nötig |
| NAT/Firewall | Funktioniert überall | Braucht offenen Port |
| Latenz | Etwas höher | Niedriger |
| Config | Keine | webhookUrl + webhookSecret |
| Empfehlung | ✅ Für die meisten | Produktion mit Tailscale |

### 10. Telegram Troubleshooting

| Problem | Ursache | Lösung |
|---|---|---|
| 401 Unauthorized | Token falsch/abgelaufen | BotFather → neuen Token → Config → restart |
| Token mit Space kopiert | Trailing Space | Token trimmen, neu einfügen |
| Bot antwortet nicht | User nicht autorisiert | User-ID zu `allowFrom` (als Zahl!) |
| `@username` statt User-ID | Falsches Format | Numerische ID nutzen, nicht @handle |
| Bot schweigt in Gruppen | Privacy Mode enabled | `/setprivacy` Disable → Bot re-adden |
| "plugin not found: telegram" | Falsche Config-Stelle | In `channels.telegram`, NICHT `plugins.entries` |
| Pairing-Code läuft ab | 1h Timeout | Erneut anschreiben → neuer Code |
| Gruppen-ID geändert | Upgrade auf Supergruppe | Neue -100-ID in Config/Pairing |
| `TypeError: fetch failed` | IPv6-Problem auf VPS | IPv4 erzwingen (s.u.) |
| Nachrichten abgeschnitten | 4000-Zeichen-Limit | `chunkMode: "newline"` |
| Bot nach Update tot | Alter Prozess läuft noch | `ps aux \| grep openclaw` → killen |
| Migration Clawdbot→OpenClaw | Alte Config/Prozesse | `cp -r ~/.clawdbot/* ~/.openclaw/` + alte stoppen |
| "access not configured" | Pairing OK, aber nicht autorisiert | `dmPolicy: "allowlist"` + `allowFrom` setzen |

**IPv6-Problem fix**:
```bash
# Prüfen:
dig +short api.telegram.org A
dig +short api.telegram.org AAAA

# Fix: IPv4 erzwingen via /etc/hosts
echo "$(dig +short api.telegram.org A | head -1) api.telegram.org" | sudo tee -a /etc/hosts

# Oder: proxy in Config setzen
```

---

## WhatsApp — Vollständige Anleitung

### Config
```json5
{
  channels: {
    whatsapp: {
      enabled: true,
      dmPolicy: "allowlist",
      selfChatMode: true,
      allowFrom: ["+4915568920209"],   // E.164 MIT + !
      groupPolicy: "allowlist",
      debounceMs: 0,                   // 0 = sofort
      mediaMaxMb: 50,
    },
  },
}
```

### QR-Code scannen
```bash
openclaw gateway start
# QR erscheint in Terminal oder Dashboard → Channels-Seite
# WhatsApp → Verknüpfte Geräte → QR scannen
```

### WhatsApp-Eigenheiten
- **dmPolicy ist GLOBAL** für den ganzen WhatsApp-Account (nicht per-Agent!)
- **selfChatMode**: Nachrichten an sich selbst = Bot-Befehle
- **Max 4 verknüpfte Geräte** (WhatsApp-Limit)
- **Baileys** = Reverse-Engineered, kein offizielles API → kann brechen

### WhatsApp Troubleshooting

| Problem | Lösung |
|---|---|
| QR erscheint nicht | Dashboard → Channels nutzen |
| "Connection closed" nach Scan | Gateway restart → erneut scannen |
| Bot antwortet nicht | `allowFrom` mit +Ländercode prüfen |
| Nachrichten verzögert | `debounceMs: 0` |
| Media nicht verarbeitet | `mediaMaxMb` erhöhen |
| Nach einigen Tagen getrennt | WhatsApp-App → Verknüpfte Geräte prüfen |

---

## Discord

```json5
{
  channels: {
    discord: {
      enabled: true,
      botToken: "<discord-bot-token>",
      dmPolicy: "allowlist",
    },
  },
}
```

**PFLICHT**: Discord Developer Portal → Bot → Privileged Gateway Intents → **Message Content Intent** aktivieren!

---

## Slack

```json5
{
  channels: {
    slack: {
      enabled: true,
      appToken: "xapp-...",    // Socket Mode Token
      botToken: "xoxb-...",    // Bot OAuth Token
    },
  },
}
```

---

## Signal

```json5
{
  channels: {
    signal: { enabled: true },
    // signal-cli muss installiert + registriert sein
    // Java 17+ nötig
  },
}
```

---

## iMessage (BlueBubbles)

```json5
{
  channels: {
    imessage: {
      enabled: true,
      adapter: "bluebubbles",
      host: "http://<mac-tailscale-ip>:1234",
      password: "<bluebubbles-password>",
    },
  },
}
```
Mac mit Messages eingeloggt + BlueBubbles-Server nötig.

---

## CLI: Channels verwalten

```bash
openclaw channels status              # Alle Channels
openclaw channels status --probe      # Mit Live-Check
openclaw channels restart telegram
openclaw channels restart whatsapp

# Nachricht senden
openclaw message send --channel telegram --target 7403482253 --message "Test"
openclaw message send --channel telegram --target @username --message "Test"
openclaw message send --channel whatsapp --target "+4915568920209" --message "Test"

# Logs
openclaw logs --follow --channel telegram
```

---

## Allgemeine Regeln

1. **dmPolicy immer `allowlist`** in Produktion
2. **allowFrom korrekt**: Telegram = Zahl, WhatsApp = E.164 String
3. **mediaMaxMb erhöhen** — Default ist oft nur 5 MB
4. **Nach Config-Änderung**: `openclaw channels restart <channel>`
5. **Streaming spart keine Tokens** — nur UX
6. **plugins.entries** ≠ **channels** — Channel-Config gehört in `channels`!
