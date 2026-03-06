# Tailscale-Integration — Remote-Zugriff richtig konfigurieren

## Überblick: Drei Zugriffsmodi

| Modus | Wer kann zugreifen | HTTPS | Config |
|---|---|---|---|
| `serve` (empfohlen) | Nur Tailnet-Geräte | ✅ automatisch | `tailscale.mode: "serve"` |
| `funnel` (vorsicht!) | Öffentliches Internet | ✅ automatisch | `tailscale.mode: "funnel"` + Password |
| `tailnet` bind | Tailnet-Geräte | ❌ manuell | `gateway.bind: "tailnet"` |
| SSH-Tunnel | Wer SSH-Zugang hat | ❌ | Kein Config nötig |

**Empfehlung für 99% der Fälle: `serve`**

---

## Tailscale Serve (Tailnet-only, empfohlen)

Gateway bleibt auf `127.0.0.1`, Tailscale proxied HTTPS-Traffic.
Nur Geräte im selben Tailnet können zugreifen.

### Config
```json5
{
  gateway: {
    bind: "loopback",
    tailscale: {
      mode: "serve",
      resetOnExit: false,     // true = tailscale serve reset bei Shutdown
    },
    auth: {
      mode: "token",
      token: "<dein-token>",
      allowTailscale: true,   // Tailscale-Identity-Auth erlauben
    },
  },
}
```

### CLI-Alternative
```bash
openclaw gateway --tailscale serve
```

### Zugriff
```
https://<hostname>.your-tailnet.ts.net
```

### Auth-Optionen bei Serve
- **allowTailscale: true** → Tailscale-User werden automatisch erkannt (kein Token nötig)
- **allowTailscale: false** → Token/Password trotzdem erforderlich
- OpenClaw verifiziert Tailscale-Identity über `tailscale whois` + Header-Prüfung

---

## Tailscale Funnel (öffentlich, VORSICHT!)

Macht den Gateway über das öffentliche Internet erreichbar.
**Nur nutzen wenn wirklich nötig!**

### Config
```json5
{
  gateway: {
    bind: "loopback",
    tailscale: {
      mode: "funnel",
    },
    auth: {
      mode: "password",       // PFLICHT bei Funnel!
      password: "starkes-passwort-hier",
    },
  },
}
```

**Besser**: Password über Environment-Variable:
```bash
export OPENCLAW_GATEWAY_PASSWORD="starkes-passwort-hier"
```

### CLI-Alternative
```bash
openclaw gateway --tailscale funnel --auth password
```

### Funnel-Voraussetzungen
- Tailscale v1.38.3+
- MagicDNS aktiviert
- HTTPS aktiviert für das Tailnet
- `funnel` Node-Attribut gesetzt
- Nur Ports 443, 8443, 10000 (TLS)
- macOS: Open-Source Tailscale App-Variante nötig

### Sicherheits-Hinweis
- **Funnel injiziert KEINE Identity-Headers** (anders als Serve)
- Deshalb: Password-Auth PFLICHT
- Funnel weigert sich zu starten ohne `auth.mode: "password"`

---

## Direct Tailnet Bind (ohne Serve/Funnel)

Gateway hört direkt auf der Tailscale-IP — kein HTTPS, kein Proxy.

```json5
{
  gateway: {
    bind: "tailnet",          // Bindet auf Tailscale-IP
    auth: {
      mode: "token",
      token: "<dein-token>",
    },
  },
}
```

### Zugriff
```
http://<tailscale-ip>:18789
ws://<tailscale-ip>:18789
```

**Achtung**: `http://127.0.0.1:18789` funktioniert in diesem Modus NICHT!

---

## SSH-Tunnel (ohne Tailscale-Config)

Kein Config-Change nötig — Gateway bleibt auf loopback:

```bash
# Von deinem Laptop:
ssh -L 18789:127.0.0.1:18789 user@vps-ip

# Dann lokal zugreifen:
# http://127.0.0.1:18789
```

### Permanenter SSH-Tunnel (systemd)
```bash
# ~/.config/systemd/user/openclaw-ssh-tunnel.service
[Unit]
Description=OpenClaw SSH Tunnel
After=network-online.target

[Service]
ExecStart=/usr/bin/ssh -N -L 18789:127.0.0.1:18789 user@vps-ip
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

```bash
systemctl --user enable --now openclaw-ssh-tunnel
```

**Wichtig**: Auch über SSH-Tunnel muss `gateway.auth.token` gesetzt sein!

---

## Praxis-Szenario: VPS + Tailscale + Nodes

### Setup-Reihenfolge

#### 1. Tailscale auf VPS installieren
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --ssh    # Optional: SSH über Tailscale
tailscale ip -4            # IP notieren
tailscale status           # Prüfen
```

#### 2. Tailscale auf allen Nodes installieren
```bash
# MacBook:
brew install tailscale
# iPhone/Android: App Store / Play Store
# Raspberry Pi:
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

#### 3. Gateway konfigurieren
```json5
// Auf dem VPS: ~/.openclaw/openclaw.json
{
  gateway: {
    bind: "loopback",
    tailscale: { mode: "serve" },
    auth: {
      mode: "token",
      token: "<64-zeichen-token>",
      allowTailscale: true,
    },
  },
}
```

```bash
systemctl --user restart openclaw-gateway
```

#### 4. Dashboard testen
```
https://<vps-hostname>.your-tailnet.ts.net
```
→ Token eingeben → Dashboard sollte laden

#### 5. macOS Node verbinden
- OpenClaw macOS App → Settings → Gateway
- URL: `https://<vps-hostname>.your-tailnet.ts.net`
- Verbinden → Pairing-Request

#### 6. Pairing genehmigen
```bash
# Auf VPS:
openclaw devices list
openclaw devices approve <requestId>
```

#### 7. Verifizieren
```bash
openclaw nodes status        # Node connected?
openclaw channels status --probe  # Channels OK?
```

---

## Troubleshooting Tailscale

| Problem | Lösung |
|---|---|
| "Serve requires HTTPS" | HTTPS im Tailscale Admin Panel aktivieren |
| Funnel startet nicht | Password-Auth fehlt, oder Tailscale < v1.38.3 |
| Node findet Gateway nicht | `tailscale status` auf beiden Seiten prüfen |
| "device identity required" | HTTPS nötig — SSH-Tunnel oder Tailscale Serve nutzen |
| Dashboard nicht erreichbar | `tailscale serve status` prüfen, Firewall checken |
| allowTailscale funktioniert nicht | Nur bei `serve` Mode, nicht bei `funnel` |

### Diagnose-Befehle
```bash
tailscale status                  # Tailscale-Verbindung prüfen
tailscale serve status            # Serve-Config anzeigen
tailscale ping <hostname>         # Erreichbarkeit testen
tailscale whois <ip>              # Identity prüfen
```
