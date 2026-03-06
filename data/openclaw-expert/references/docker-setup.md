# Docker-Deployment — Deep Dive

## Wann Docker?

| Szenario | Docker? | Begründung |
|---|---|---|
| VPS/Server (24/7) | ✅ Ja | Isolation, Reproduzierbarkeit |
| macOS lokal | ❌ Nein | VM-Overhead, npm direkt schneller |
| Sandbox für Tools | ✅ Ja | Gateway lokal, Tools in Container |
| Erstmalig testen | ✅ Ja | Sicher, leicht entfernbar |

---

## Offizielles Docker-Setup

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
bash docker-setup.sh
```

### docker-setup.sh macht:
1. Baut Docker-Image (`openclaw:local`)
2. Startet Onboarding-Wizard (interaktiv)
3. Setzt Control-UI CORS-Origins
4. Gibt Befehle für Channel-Setup aus

### Wizard-Empfehlungen im Docker:
- Gateway bind: **lan** (innerhalb Docker-Netzwerk)
- Gateway auth: **token**
- Tailscale: **Off**
- Gateway daemon: **No** (Docker managed den Lifecycle)

---

## Docker Compose

```yaml
services:
  openclaw-gateway:
    image: openclaw:local
    restart: unless-stopped
    ports:
      - "18789:18789"
    volumes:
      - ~/.openclaw:/home/node/.openclaw
      - ~/openclaw/workspace:/home/node/.openclaw/workspace
    # Optional: User-Mapping
    # user: "1000:1000"

  openclaw-cli:
    image: openclaw:local
    volumes:
      - ~/.openclaw:/home/node/.openclaw
      - ~/openclaw/workspace:/home/node/.openclaw/workspace
    profiles: ["cli"]
    entrypoint: ["openclaw"]
```

### CLI via Docker Compose
```bash
docker compose run --rm openclaw-cli doctor
docker compose run --rm openclaw-cli channels add --channel telegram --token <TOKEN>
docker compose run --rm openclaw-cli channels login     # WhatsApp QR
docker compose run --rm openclaw-cli dashboard --no-open
```

---

## Container-Image Details

Das Default-Image ist **security-first** (non-root `node` User):
- Kein Chromium/Playwright vorinstalliert
- Kein sudo
- Minimale Angriffsfläche

### Playwright/Browser installieren
```bash
docker compose exec openclaw-gateway \
  node /app/node_modules/playwright-core/cli.js install chromium
```

### Extra-Pakete installieren
```bash
# Option 1: Zur Buildzeit (persistiert)
export OPENCLAW_DOCKER_APT_PACKAGES="ripgrep jq"
bash docker-setup.sh   # Rebuild

# Option 2: Zur Laufzeit (geht bei Container-Neustart verloren)
docker compose exec -u root openclaw-gateway bash
apt-get update && apt-get install -y ripgrep
```

---

## Permissions-Probleme (häufig!)

```bash
# Option 1 (empfohlen): Ownership auf UID 1000
sudo chown -R 1000:$(id -g) ~/.openclaw
sudo chmod -R u+rwX,g+rwX,o-rwx ~/.openclaw

# Option 2: Gruppe beschreibbar
chmod -R 775 ~/.openclaw

# Option 3 (LETZTER AUSWEG): World-Writable
chmod -R 777 ~/.openclaw
```

---

## Docker + Ollama (lokale Modelle)

```json5
models: {
  providers: {
    ollama: {
      // macOS Docker Desktop:
      baseUrl: "http://host.docker.internal:11434",
      // Linux (Docker-Bridge-IP):
      baseUrl: "http://172.17.0.1:11434",
      apiKey: "ollama-local",
      api: "openai-completions",
    },
  },
},
```

---

## Agent-Sandbox (Gateway lokal, Tools in Docker)

Separate Sandbox NUR für Tool-Ausführung (nicht den ganzen Gateway):

```json5
tools: {
  exec: {
    host: "sandbox",  // Tools in Docker-Container ausführen
  },
},
docker: {
  network: "none",    // Kein Netzwerk in Sandbox
},
```

- Container wird automatisch erstellt/recycled
- `setupCommand` ändern → Container wird neu erstellt (~5min Cooldown)
- `network: "none"` = kein Internet für Tools (sicherste Option)

---

## Troubleshooting Docker

| Problem | Lösung |
|---|---|
| Build OOM-Killed (exit 137) | Mindestens 2 GB RAM |
| Workspace nicht sichtbar | Volume-Mount prüfen in docker-compose.yml |
| "Cannot connect to Docker daemon" | `sudo systemctl start docker` |
| Slow auf macOS | VM-Overhead — npm direkt nutzen |
| Permission denied | Ownership/Permissions oben prüfen |
| Container startet nicht nach Config-Änderung | `docker compose run --rm openclaw-cli doctor` |
