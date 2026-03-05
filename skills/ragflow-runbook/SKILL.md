---
name: ragflow-runbook
version: 0.1.4
description: End-to-end runbook for deploying, operating, troubleshooting, and monitoring RAGFlow (runtime ops only).

# Compatibility: some registries/security scanners only detect env vars if they are declared
# at the document top-level or under `metadata.env`. We keep the OpenClaw namespace too.
env:
  required: [RAGFLOW_BASE_URL]
  optional: [RAGFLOW_API_KEY, OPENCLAW_PRIMARY_CHAT_ID]

metadata:
  env:
    required: [RAGFLOW_BASE_URL]
    optional: [RAGFLOW_API_KEY, OPENCLAW_PRIMARY_CHAT_ID]
  openclaw:
    requires:
      bins: [python3, docker, curl]
      optional_bins: [git, openclaw]
    env:
      required: [RAGFLOW_BASE_URL]
      optional: [RAGFLOW_API_KEY, OPENCLAW_PRIMARY_CHAT_ID]
---

# ragflow-runbook Skill

A practical runbook for deploying, operating, troubleshooting, and calling RAGFlow (Retrieval-Augmented Generation).

Goal: any agent should be able to bring RAGFlow up, diagnose failures, and call the API safely even without knowing the deployment details up front.

---

## 1) When To Use

- Deploy RAGFlow (Docker / Windows / Linux / WSL2).
- Troubleshoot failures: startup issues, unhealthy backend services, port conflicts, performance problems.
- Use the API for operations purposes: validate liveness/readiness, verify auth, and check system endpoints.
- Run health checks, automate smoke tests, or prepare backup/restore.

## 2) What The Agent Must Ask First (Minimum Inputs)

Before running any commands, confirm the following (missing any of these often leads to wrong assumptions):

- Deployment environment: `Windows / WSL2 / Linux / macOS (client only)`
- Install directory (the directory that contains `docker-compose.yml`)
- Access method:
  - `RAGFLOW_BASE_URL` (e.g. `http://localhost:9380` or an internal/Tailscale address)
  - Whether there is an Nginx/reverse proxy in front (and whether Web UI uses port 80/8080)
- Whether an API key already exists (do NOT paste secrets into chat; use env vars / secret manager)
- Current symptom:
  - "does not start" vs "starts but UI/API errors" vs "retrieval quality is poor"

> Security: never store or share API keys / DB passwords in plaintext (docs, repo, or chat).

---

## 3) Canonical Environment Variables (Recommended)

Use environment variables so all agents can run the same commands:

- `RAGFLOW_BASE_URL`: prefer an internal/Tailscale URL, e.g. `http://100.x.y.z:9380`
- `RAGFLOW_API_KEY`: Bearer token (created in the RAGFlow Web UI)

Quick verification (separate liveness / readiness / auth; tolerate path differences across versions):

- Liveness (usually no auth; try in order, any 200 is OK):
  - `GET $RAGFLOW_BASE_URL/openapi.json`
  - `GET $RAGFLOW_BASE_URL/api/v1/openapi.json`
  - `GET $RAGFLOW_BASE_URL/v1/system/ping`
- Readiness (often requires auth; try in order):
  - `GET $RAGFLOW_BASE_URL/v1/system/status`
  - `GET $RAGFLOW_BASE_URL/v1/system/ping`

If these do not match your deployment: treat the returned `openapi.json` as the source of truth.

This skill ships with its own ops helpers under `scripts/`:

- `scripts/ragflow_ping.py`: liveness + readiness
- `scripts/ragflow_smoke.py`: auth + API smoke (system-level only)
- `scripts/ragflow_status.py`: compact status summary
- `scripts/ragflow_alert.py`: send an ops alert via OpenClaw messaging

This skill is intentionally decoupled from any workspace-specific application content. It focuses only on RAGFlow runtime operations.

---

## 4) Bootstrap (Fresh Install; Windows/WSL2 + Linux)

This section targets a brand-new machine. Goal: get to a working UI + API quickly:
clone upstream docker bundle -> start -> create API key in UI -> validate via curl/scripts.

### 4.1 Choose Install Mode (Default)

- Primary path (best for most desktop / Windows users): Windows + WSL2
- Alternate path: a Linux server (Ubuntu/Debian/CentOS/etc.)

### 4.1.1 Fresh Install: Copy/Paste (WSL2 / Linux)

WSL2 (recommended: store files on a Windows drive like `D:`; run commands inside WSL2):

```bash
# WSL2
cd /mnt/d

git clone https://github.com/infiniflow/ragflow.git
cd ragflow/docker

# Common requirement for some document engine profiles
sudo sysctl -w vm.max_map_count=262144 || true

# Default .env = elasticsearch + cpu
# To change ports/passwords/image versions: edit docker/.env

docker compose up -d

docker compose ps
```

Linux:

```bash
# Linux
sudo mkdir -p /opt && cd /opt
sudo chown -R "$USER" /opt

git clone https://github.com/infiniflow/ragflow.git
cd ragflow/docker

sudo sysctl -w vm.max_map_count=262144 || true

docker compose up -d

docker compose ps
```

Next: open Web UI (default `http://<host>:80`), finish initialization, create an API key, then validate using `## 3` + `## 8`.

### 4.2 Get The Official Docker Compose Bundle (Robust; Verified Against Upstream)

To avoid missing files or mismatched versions, use `git clone` and run from the upstream `docker/` directory:

```bash
git clone https://github.com/infiniflow/ragflow.git
cd ragflow/docker

# Optional: pin to a tag/commit for production
# git checkout <tag-or-commit>
```

The upstream `docker/` folder typically includes:

- `docker-compose.yml` (often `include: ./docker-compose-base.yml`)
- `docker-compose-base.yml` (backend services: database + cache + object storage + document engine)
- `.env` (default ports/passwords; change for production)
- `service_conf.yaml.template` (used to generate `service_conf.yaml` at container startup)
- `entrypoint.sh` (commonly started with flags like `--enable-adminserver` / `--enable-mcpserver`)
- `nginx/` (for built-in Web UI / reverse proxy)
- `README.md` (docker-specific docs)

Note: upstream explicitly warns that some compose variants (e.g. `docker-compose-macos.yml`) are not actively maintained. Do not use them unless you know why.

### 4.3 First Bring-Up (Upstream `COMPOSE_PROFILES`)

Upstream `.env` defaults:

- `COMPOSE_PROFILES` is derived from selected backend profiles (e.g. document engine + compute device)

So you typically do not need to pass `--profile` manually. `docker compose up -d` will pick profiles from `.env`.

Before starting (Linux/WSL2, for some document engine profiles):

```bash
cat /proc/sys/vm/max_map_count || true
sudo sysctl -w vm.max_map_count=262144 || true
```

Start:

```bash
# In ragflow/docker
# Optional: explicit profiles if you do not want to rely on COMPOSE_PROFILES
# docker compose --profile elasticsearch --profile cpu up -d

docker compose up -d

docker compose ps
```

Switch CPU/GPU (examples):

```bash
# Option 1: edit docker/.env
# DEVICE=gpu

# Option 2: override temporarily (do not modify files)
DEVICE=gpu docker compose up -d
```

Enable embeddings service (TEI): upstream suggests adding a tei profile to `COMPOSE_PROFILES`:

```bash
# Example:
# COMPOSE_PROFILES=${COMPOSE_PROFILES},tei-cpu
# or:
# COMPOSE_PROFILES=${COMPOSE_PROFILES},tei-gpu

docker compose up -d
```

Validation: wait for key services to be running/healthy in `docker compose ps`, then run liveness/readiness (## 3) and API prefix detection (## 8).

### 4.4 First-Time Setup Checklist (Aligned With Upstream `.env`)

In upstream `docker/.env` (main branch), exposed ports typically mean:

- Web UI / WebServer: `SVR_WEB_HTTP_PORT` (default 80), `SVR_WEB_HTTPS_PORT` (default 443)
- API (RAGFlow HTTP): `SVR_HTTP_PORT` (default 9380)
- Admin Server: `ADMIN_SVR_HTTP_PORT` (default 9381)
- MCP: `SVR_MCP_PORT` (default 9382)

Shortest path to a usable setup:

1) Open Web UI: `http://<host>:${SVR_WEB_HTTP_PORT}` (default `http://<host>:80`)
2) Complete initialization (admin/org setup depending on version)
3) Create an API key (usually under Settings/System/API Keys)
4) Set on the client side (recommended env vars):

- `RAGFLOW_BASE_URL=http://<host>:${SVR_HTTP_PORT}` (default `http://<host>:9380`)
- `RAGFLOW_API_KEY=ragflow-...` (Bearer token; do not paste secrets into chat)

Then validate with liveness/readiness in `## 3`.

> Production warning: upstream `.env` explicitly warns against using default passwords. At minimum change `ELASTIC_PASSWORD`, `MYSQL_PASSWORD`, `MINIO_PASSWORD`, and `REDIS_PASSWORD`.

---

## 5) Quick Start (Ops Checklist)

### 5.1 Prerequisites

- Docker Engine + Docker Compose v2 (`docker compose ...`)
- Resources (rule of thumb):
  - CPU >= 4 cores, RAM >= 16GB (32GB recommended)
  - Disk >= 50GB (depends on document volume + vector index size)
- Linux/WSL2: `vm.max_map_count >= 262144` (required by some document engine profiles)

Checks:

```bash
docker --version
docker compose version

# Linux/WSL2 only
cat /proc/sys/vm/max_map_count
```

Temporary fix (Linux/WSL2):

```bash
sudo sysctl -w vm.max_map_count=262144
```

### 5.2 Bring-Up (Docker Compose)

Prereq: you are in the directory that contains `docker-compose.yml`.

```bash
docker compose up -d
docker compose ps
```

Tail logs:

```bash
docker compose logs -f
```

---

## 6) Service Management (Day-2 Operations)

```bash
# Status
docker compose ps

# Start/stop
docker compose up -d
docker compose down

# Restart
docker compose restart

# Logs (all / last N lines / last 1h)
docker compose logs
docker compose logs --tail=200
docker compose logs --since=1h

# Resource usage
docker stats
```

Note: service names differ across compose versions. If you see "no such service", run `docker compose ps` and use the actual service name.

---

## 7) Health Checks (Common Root Causes)

### 7.1 Document engine unhealthy / crash loop

Common causes: `vm.max_map_count` too small, low RAM, disk full.

```bash
# Linux/WSL2
cat /proc/sys/vm/max_map_count
sudo sysctl -w vm.max_map_count=262144

docker compose ps
docker compose logs --tail=200 <es-service>
```

### 7.2 Database connection failures

```bash
docker compose ps
docker compose logs --tail=200 <mysql-service>
```

### 7.3 Port conflicts

- Symptom: containers fail to start or port mapping fails.
- Fix: find the process using the port, or change port mappings in `.env` / compose and restart.

---

## 8) API Usage (Agent-Safe Patterns)

### 8.1 Base URL + Auth

RAGFlow often exposes:

- Web UI (port 80/8080)
- API (commonly 9380, or a reverse-proxied path)

Recommended convention:

- `RAGFLOW_BASE_URL` points to the API root, e.g. `http://localhost:9380`
- Auth header: `Authorization: Bearer $RAGFLOW_API_KEY`

### 8.2 Minimal curl examples (Prefix Auto-Detect; Prefer `v1`)

Across versions/deployments, RAGFlow may have two API prefixes:

- `v1/...` (often system/user/token)
- `api/v1/...` (often application endpoints)

Use this template to auto-detect the prefix (prefer `v1`, fallback to `api/v1`).

```bash
# 0) Ensure you are hitting the API port/host (not the UI port)
#    Any 200 is OK
curl -sS -o /dev/null -w "%{http_code}\n" "$RAGFLOW_BASE_URL/openapi.json"
curl -sS -o /dev/null -w "%{http_code}\n" "$RAGFLOW_BASE_URL/api/v1/openapi.json"

# 1) Auto-detect prefix (prefer v1)
RAGFLOW_API_PREFIX=""
if curl -sS -o /dev/null -w "%{http_code}" "$RAGFLOW_BASE_URL/v1/system/ping" | grep -q "200"; then
  RAGFLOW_API_PREFIX="v1"
elif curl -sS -o /dev/null -w "%{http_code}" "$RAGFLOW_BASE_URL/api/v1/openapi.json" | grep -q "200"; then
  RAGFLOW_API_PREFIX="api/v1"
else
  echo "Cannot detect API prefix. Check base URL / reverse proxy / firewall."
  exit 1
fi

echo "Detected prefix: $RAGFLOW_API_PREFIX"
```

Ops-only examples (no application-level endpoints):

Example 1: system ping (no secrets in output)

```bash
curl -sS -o /dev/null -w "%{http_code}\n" "$RAGFLOW_BASE_URL/v1/system/ping"
```

Example 2: system status (auth)

```bash
curl -sS -X GET "$RAGFLOW_BASE_URL/v1/system/status" \
  -H "Authorization: Bearer $RAGFLOW_API_KEY" | head
```

Example 3: fetch openapi schema (liveness)

```bash
curl -sS "$RAGFLOW_BASE_URL/openapi.json" | head
```

Note: If your deployment uses different paths, `openapi.json` is the source of truth. Avoid calling application-level endpoints from ops runbooks.

### 8.3 Agent Guidance

- Always fetch `openapi.json` first to confirm real paths/fields/version differences.
- If you get 404: suspect base URL (hitting UI port), reverse proxy misconfig, or a different path prefix.
- If you get 401/403: suspect missing/expired key or missing `Bearer` prefix.

---

## 9) Backup / Restore (Practical)

Principle: stop services first, then back up volumes, then back up compose configs.

Backup (example; volume names depend on your environment):

```bash
mkdir -p backup

docker run --rm \
  -v <mysql_volume>:/source \
  -v "$PWD/backup":/backup \
  alpine tar czf /backup/mysql-data.tar.gz -C /source .
```

Restore:

```bash
docker compose down

docker run --rm \
  -v <mysql_volume>:/target \
  -v "$PWD/backup":/backup \
  alpine tar xzf /backup/mysql-data.tar.gz -C /target

docker compose up -d
```

---

## 10) Security Baseline (Minimum)

- Do not use `latest` in production; pin image versions.
- API keys must be stored in env vars / secret manager only.
- Minimize exposure: allow only internal/Tailscale ranges to access API ports.
- If public access is required: add TLS + auth at reverse proxy, and restrict source IP ranges.

---

## 11) Troubleshooting Flow (Agent Playbook)

When a user says "RAGFlow is not working", use this order to reduce back-and-forth:

1) `docker compose ps` (which containers are unhealthy/exited)
2) `docker compose logs --tail=200 <unhealthy-service>` (capture the first actionable errors)
3) Resources: `docker stats`, disk, `vm.max_map_count` (Linux/WSL2)
4) Network: from the caller machine `curl $RAGFLOW_BASE_URL/openapi.json`
5) Auth: `ragflow_ping.py` or `GET /v1/system/status` (with Bearer)

---

## 12) OpenClaw Ops Integration

This section documents an end-to-end **operations** workflow for running RAGFlow with OpenClaw.
It is intentionally decoupled from any application-layer usage and focuses only on RAGFlow runtime operations.

### 12.1 Scope

Included:
- Host/service health verification (liveness/readiness)
- Basic auth verification (API key works)
- Smoke checks (API reachable, key endpoints respond)
- Alerting hooks (what to check, what to report)
- Scheduling (daily/periodic checks)

Excluded (by design):
- Any application-layer conventions
- Content parsing/chunking/index strategy
- Retrieval quality evaluation

### 12.2 Standard Environment Contract

On the machine running OpenClaw, set:

- `RAGFLOW_BASE_URL` (prefer an internal/Tailscale address)
- `RAGFLOW_API_KEY` (Bearer token; never commit; do not paste into chat)

Recommended ops endpoints:

- Liveness (no auth): `GET $RAGFLOW_BASE_URL/openapi.json`
- Readiness (auth): `GET $RAGFLOW_BASE_URL/v1/system/status`

If paths differ in your deployment, use `openapi.json` as the source of truth.

### 12.3 Local Workspace Helpers (Preferred)

This skill includes built-in helpers under `scripts/`.
They are designed to be:
- non-interactive
- safe to run repeatedly
- machine-readable (short output + non-zero exit code on failure)

Helpers:

- `scripts/ragflow_ping.py`
  - Purpose: liveness + readiness checks.
- `scripts/ragflow_smoke.py`
  - Purpose: auth verification + minimal API smoke calls.
  - Note: it only uses system endpoints. It does not depend on any application-level data.
- `scripts/ragflow_status.py`
  - Purpose: fetch `/v1/system/status` and print a compact key summary.
- `scripts/ragflow_alert.py`
  - Purpose: send an ops alert to Telegram via the `openclaw message send` CLI.

(Prefer the skill-local scripts so the runbook works in any environment.)

### 12.3.1 Script Contracts (Inputs / Outputs / Exit Codes)

`scripts/ragflow_ping.py`
- Required env:
  - `RAGFLOW_BASE_URL`
- Optional env:
  - `RAGFLOW_API_KEY` (if set, readiness check is performed)
- Network calls:
  - `GET {base_url}/openapi.json` (no auth)
  - `GET {base_url}/v1/system/status` (Bearer auth)
- Output (examples):
  - `OK_LIVE (no api key set)`
  - `OK_READY keys=...`
  - `LIVENESS_FAIL ...`
  - `READINESS_FAIL ...`
- Exit codes:
  - `0` OK
  - `2` liveness failed
  - `3` readiness failed

`scripts/ragflow_smoke.py`
- Required env:
  - `RAGFLOW_BASE_URL`
  - `RAGFLOW_API_KEY`
- Network calls:
  - `GET {base_url}/v1/system/status` (auth)
  - `GET {base_url}/v1/system/ping` (auth or no-auth depending on deployment)
- Output (examples):
  - `OK smoke`
  - `FAIL system/status ...`
  - `FAIL system/ping ...`
- Exit codes:
  - `0` OK
  - `2` system/status failed
  - `3` system/ping failed

`scripts/ragflow_status.py`
- Required env:
  - `RAGFLOW_BASE_URL`
  - `RAGFLOW_API_KEY`
- Network calls:
  - `GET {base_url}/v1/system/status`
- Output (example):
  - `OK keys=key1,key2,...` (compact, no secrets)
- Exit codes:
  - `0` OK
  - `2` HTTP failure
  - `3` invalid JSON

`scripts/ragflow_alert.py`
- Purpose: notify humans when ping/smoke fails.
- Inputs:
  - CLI flags: `--title` (required), `--details` (optional)
  - Optional env: `OPENCLAW_PRIMARY_CHAT_ID` (default target)
- Behavior:
  - Sends a Telegram message via `openclaw message send ...`.
- Notes:
  - Do not include secrets in `--details`.


### 12.4 Ops Workflow (Suggested)

1) **Connectivity**
   - Confirm OpenClaw host can reach `RAGFLOW_BASE_URL` over the network.

2) **Liveness**
   - Check `openapi.json` responds with HTTP 200.

3) **Readiness**
   - Check `v1/system/status` responds with HTTP 200 when authenticated.

4) **Smoke**
   - Run the skill-local smoke helper: `scripts/ragflow_smoke.py` (system endpoints only).

5) **Escalation artifacts**
   - Collect:
     - `docker compose ps`
     - `docker compose logs --tail=200 <ragflow-service>`
     - the exact endpoint + HTTP code observed from the OpenClaw side

### 12.5 Scheduling (Copy/Paste Examples)

Goal: provide copy/paste recipes. An agent can create these tasks when needed.

#### 12.5.1 cron (Linux)

Ping every 10 minutes and alert on failure:

```cron
*/10 * * * * RAGFLOW_BASE_URL="http://127.0.0.1:9380" RAGFLOW_API_KEY="${RAGFLOW_API_KEY}" /usr/bin/python3 /path/to/skills/ragflow-runbook/scripts/ragflow_ping.py || /usr/bin/python3 /path/to/skills/ragflow-runbook/scripts/ragflow_alert.py --title "ping failed" --details "ragflow_ping.py exit=$?"
```

Smoke once per day at 06:05 and alert on failure:

```cron
5 6 * * * RAGFLOW_BASE_URL="http://127.0.0.1:9380" RAGFLOW_API_KEY="${RAGFLOW_API_KEY}" /usr/bin/python3 /path/to/skills/ragflow-runbook/scripts/ragflow_smoke.py || /usr/bin/python3 /path/to/skills/ragflow-runbook/scripts/ragflow_alert.py --title "smoke failed" --details "ragflow_smoke.py exit=$?"
```

Notes:
- Replace `/path/to/skills/...` with the real absolute path.
- Prefer sourcing secrets from a root-owned env file, or use your secret manager. Avoid putting API keys directly into crontab.

#### 12.5.2 launchd (macOS)

Create two plist files (one for ping, one for smoke) and load them with `launchctl`.

Ping (every 10 minutes):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>ai.openclaw.ragflow.ping</string>

    <key>ProgramArguments</key>
    <array>
      <string>/usr/bin/python3</string>
      <string>/ABS/PATH/skills/ragflow-runbook/scripts/ragflow_ping.py</string>
    </array>

    <key>StartInterval</key>
    <integer>600</integer>

    <key>EnvironmentVariables</key>
    <dict>
      <key>RAGFLOW_BASE_URL</key>
      <string>http://127.0.0.1:9380</string>
      <key>RAGFLOW_API_KEY</key>
      <string>${RAGFLOW_API_KEY}</string>
    </dict>

    <key>StandardOutPath</key>
    <string>/tmp/ragflow-ping.out</string>
    <key>StandardErrorPath</key>
    <string>/tmp/ragflow-ping.err</string>

    <key>RunAtLoad</key>
    <true/>
  </dict>
</plist>
```

Smoke (daily at 06:05):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>ai.openclaw.ragflow.smoke</string>

    <key>ProgramArguments</key>
    <array>
      <string>/usr/bin/python3</string>
      <string>/ABS/PATH/skills/ragflow-runbook/scripts/ragflow_smoke.py</string>
    </array>

    <key>StartCalendarInterval</key>
    <dict>
      <key>Hour</key>
      <integer>6</integer>
      <key>Minute</key>
      <integer>5</integer>
    </dict>

    <key>EnvironmentVariables</key>
    <dict>
      <key>RAGFLOW_BASE_URL</key>
      <string>http://127.0.0.1:9380</string>
      <key>RAGFLOW_API_KEY</key>
      <string>${RAGFLOW_API_KEY}</string>
    </dict>

    <key>StandardOutPath</key>
    <string>/tmp/ragflow-smoke.out</string>
    <key>StandardErrorPath</key>
    <string>/tmp/ragflow-smoke.err</string>

    <key>RunAtLoad</key>
    <true/>
  </dict>
</plist>
```

Notes:
- Replace `/ABS/PATH/...` with the real absolute path.
- Prefer storing secrets outside the plist and injecting them safely; do not commit plists with secrets.

### 12.6 Security Notes

- Do not expose `SVR_HTTP_PORT` to the public internet.
- Prefer allowlisting internal/Tailscale ranges.
- Store `RAGFLOW_API_KEY` in env/secret manager only.

---

## References

- RAGFlow Docs: https://ragflow.io/docs/
- GitHub: https://github.com/infiniflow/ragflow
