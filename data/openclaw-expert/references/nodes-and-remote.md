# Nodes & Remote Access — Geräte als Nodes anschließen

## Was ist ein Node?

Ein Node ist ein **Companion-Gerät** (macOS, iOS, Android, Headless-Linux), das sich per WebSocket
mit dem Gateway verbindet und lokale Aktionen ausführt (Kamera, Screen, Canvas, Shell-Befehle).

**Nodes sind KEINE Gateways.** Messaging-Kanäle (Telegram, WhatsApp etc.) laufen auf dem Gateway,
nicht auf Nodes. Nodes sind Peripheriegeräte.

```
┌─────────────────────────────────┐
│  Gateway (VPS/Server)           │  ← Messaging, Sessions, Brain
│  ws://127.0.0.1:18789          │
└──────────┬──────────────────────┘
           │ WebSocket (Tailscale/LAN)
    ┌──────┴──────────────────────┐
    │  Node: MacBook (macOS App)  │  ← Browser-Control, Canvas, Voice Wake
    │  Node: iPhone (iOS App)     │  ← Kamera, Screen Recording, Canvas
    │  Node: Android Phone        │  ← Kamera, Screen Recording, SMS
    │  Node: Raspberry Pi         │  ← system.run, Hardware-Control
    │  Node: Headless Linux       │  ← system.run, system.which
    └─────────────────────────────┘
```

---

## Node-Typen & Fähigkeiten

| Node-Typ | Fähigkeiten | Pairing |
|---|---|---|
| macOS Menübar-App | Voice Wake, PTT, WebChat, Canvas, Browser-Control, Debug | Bonjour/mDNS |
| iOS App | Canvas, Voice Wake, Talk Mode, Kamera, Screen Recording | QR-Code / Deep Link |
| Android App | Canvas, Talk Mode, Kamera, Screen Recording, SMS | QR-Code |
| macOS Node-Mode | system.run, system.notify, Canvas, Kamera | Bonjour/mDNS |
| Headless Node | system.run, system.which (kein UI) | CLI-Pairing |

---

## Szenario: Gateway auf VPS + MacBook als Node

### Voraussetzungen
- Gateway läuft auf VPS (Contabo, Hetzner, etc.)
- Tailscale auf beiden Geräten installiert und eingeloggt
- Beide im selben Tailnet

### Schritt 1: Tailscale auf VPS installieren
```bash
# Auf dem VPS:
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
# Tailscale-IP notieren: tailscale ip -4
```

### Schritt 2: Gateway für Tailscale konfigurieren
```json5
// ~/.openclaw/openclaw.json auf dem VPS:
{
  gateway: {
    bind: "loopback",           // Bleibt loopback!
    tailscale: {
      mode: "serve",            // Tailnet-only (empfohlen)
      // mode: "funnel",        // NUR wenn öffentlich nötig (GEFÄHRLICH!)
      resetOnExit: false,
    },
    auth: {
      mode: "token",
      token: "<64-zeichen-token>",
      allowTailscale: true,     // Tailscale-Identity-Auth erlauben
    },
  },
}
```

```bash
# Gateway neu starten
systemctl --user restart openclaw-gateway
```

### Schritt 3: macOS Menübar-App als Node verbinden
1. OpenClaw macOS App installieren
2. App öffnen → Settings → Gateway
3. Gateway-URL eingeben: `https://<vps-hostname>.your-tailnet.ts.net`
4. Token eingeben (oder Tailscale-Auth wenn `allowTailscale: true`)
5. Pairing-Request wird auf Gateway erstellt

### Schritt 4: Pairing auf Gateway genehmigen
```bash
# Auf dem VPS:
openclaw devices list              # Offene Pairing-Requests anzeigen
openclaw devices approve <requestId>
```

### Schritt 5: Verifizieren
```bash
openclaw nodes status              # Node sollte "connected" zeigen
openclaw nodes describe --all      # Fähigkeiten aller Nodes anzeigen
```

---

## Szenario: Gateway auf VPS + iPhone als Node

### Schritt 1: Gateway mit Tailscale Serve (wie oben)

### Schritt 2: iOS App installieren und verbinden
1. OpenClaw iOS App aus App Store installieren
2. App öffnen → Settings → Gateway
3. Zwei Optionen:
   - **QR-Code**: Im Gateway-Dashboard (WebChat) QR-Code generieren → Scannen
   - **Deep Link**: `openclaw://setup?code=<SETUP_CODE>` → In App öffnen
   - **Manuell**: Gateway-URL + Token eingeben

### Schritt 3: Pairing via Telegram (bequemster Weg)
```
# Im Telegram-Chat mit dem Bot:
/pair
# → Bot antwortet mit Setup-Code
# → Code in iOS App → Settings → Gateway einfügen
```

### Schritt 4: Genehmigen
```bash
openclaw devices approve <requestId>
```

---

## Szenario: Headless Node (Linux/Pi)

Für Maschinen ohne GUI — nur `system.run` und `system.which`:

```bash
# Auf dem Node-Rechner:
npm install -g openclaw@latest

# Headless Node starten:
openclaw node host --gateway wss://<vps-hostname>.your-tailnet.ts.net \
  --token <gateway-token>

# Oder mit TLS:
openclaw node host --gateway wss://<hostname>:18789 \
  --tls --tls-fingerprint <fingerprint>
```

Node-Config wird gespeichert in: `~/.openclaw/node.json`
Exec-Approvals: `~/.openclaw/exec-approvals.json`

---

## Szenario: Raspberry Pi als immer-on Node

```bash
# Auf dem Pi:
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

npm install -g openclaw@latest

# Als systemd-Service:
cat > ~/.config/systemd/user/openclaw-node.service << 'EOF'
[Unit]
Description=OpenClaw Node Host
After=network-online.target

[Service]
ExecStart=%h/.npm-global/bin/openclaw node host \
  --gateway wss://<vps-hostname>.your-tailnet.ts.net \
  --token <gateway-token>
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now openclaw-node
```

---

## Node-Discovery (Bonjour/mDNS)

### Lokales Netzwerk (LAN)
- Gateway advertised sich via `_openclaw-gw._tcp` (Bonjour/mDNS)
- macOS/iOS Nodes entdecken Gateway automatisch im LAN
- Kein manuelles URL-Eingeben nötig

### Tailscale-Netzwerk
- mDNS-Broadcasts propagieren nicht über Tailscale
- **Lösung**: DNS-SD über Unicast-DNS (Tailscale DNS-Server)
- Android nutzt `dnsjava` Library für Unicast-DNS-SD
- iOS nutzt QR-First-Pairing wenn kein lokaler Gateway gefunden

---

## Node-Befehle ausführen

```bash
# Befehl auf einem spezifischen Node ausführen
openclaw nodes run --node <idOrNameOrIp> -- echo "Hello from node"

# Benachrichtigung auf Node senden
openclaw nodes notify --node <idOrNameOrIp> \
  --title "Ping" --body "Gateway ready" \
  --priority active   # passive | active | timeSensitive

# Node-Details anzeigen
openclaw nodes describe --node <id>

# Alle Nodes anzeigen
openclaw nodes status
```

---

## Browser-Control über Node

Für Gateway auf Server + Browser auf MacBook:

1. Gateway auf VPS (Tailscale Serve)
2. macOS Node auf MacBook (Menübar-App, selbes Tailnet)
3. Gateway proxied Browser-Aktionen zum Node
4. **Kein separater Serve-URL** nötig
5. **Kein Funnel** für Browser-Control nutzen!

---

## Exec-Approvals (Sicherheit)

Nodes können Shell-Befehle ausführen — das muss kontrolliert werden:

```json5
// ~/.openclaw/exec-approvals.json (auf dem Node)
{
  "mode": "ask",          // "ask" | "allowlist" | "full"
  // ask = Jeder Befehl muss bestätigt werden
  // allowlist = Nur bestimmte Befehle erlaubt
  // full = Alles erlaubt (GEFÄHRLICH!)
}
```

macOS App: Settings → Exec Approvals (gleiche Modi)

---

## Wichtige Regeln

1. **Nodes sind Peripherie** — Messaging geht über Gateway, nicht über Nodes
2. **Pairing = Vertrauens-Akt** — Setup-Code wie Passwort behandeln!
3. **Kein Funnel für Nodes** — Nur Tailscale Serve oder LAN
4. **exec-approvals** — Auf jedem Node konfigurieren
5. **Node-ID persistent** — Gespeichert in `~/.openclaw/node.json`
6. **PATH-Overrides ignoriert** — Tools in Standard-Locations installieren
