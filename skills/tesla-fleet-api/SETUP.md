# Tesla Fleet API Skill — Setup Guide

This guide covers **setup + configuration** for the Tesla Fleet API skill.

If you just want the CLI command reference, see `SKILL.md`.

---

## Prerequisites

- Tesla Developer Account + an app created
- A domain you control (for public key hosting + virtual key enrollment)
- `python3`
- `openssl` (for key generation + TLS certs)
- macOS (scripts tested on macOS)
- For proxy setup: `go` (on macOS: `brew install go`) — only needed once to compile the proxy binary

---

## State / Files

All runtime state lives in your workspace:

`{workspace}/tesla-fleet-api/`

Files:
- `config.json` — provider creds (client id/secret), non-token config (audience, base_url, ca_cert, redirect_uri, domain)
- `auth.json` — tokens (access/refresh)
- `vehicles.json` — cached vehicle list
- `places.json` — named locations (`{"home": {"lat": ..., "lon": ...}}`)
- `proxy/` — TLS material for the signing proxy
- `private-key.pem` — your Tesla EC private key (fixed name)

Credentials come from `config.json` or environment variables (`TESLA_CLIENT_ID`, `TESLA_CLIENT_SECRET`). No `.env` file loading.

---

## 1) Create & host your EC keypair

```bash
# Generate P-256 keypair
openssl ecparam -name prime256v1 -genkey -noout -out private-key.pem
openssl ec -in private-key.pem -pubout -out public-key.pem

# Host public key at:
# https://YOUR_DOMAIN/.well-known/appspecific/com.tesla.3p.public-key.pem
```

Store your private key in the workspace with a fixed name:
`{workspace}/tesla-fleet-api/private-key.pem`

---

## 2) Configure provider credentials

```bash
python3 scripts/auth.py config set \
  --client-id "YOUR_CLIENT_ID" \
  --client-secret "YOUR_CLIENT_SECRET" \
  --redirect-uri "http://localhost:18080/callback" \
  --audience "https://fleet-api.prd.eu.vn.cloud.tesla.com"
```

This writes to `{workspace}/tesla-fleet-api/config.json`.

---

## 3) OAuth login (creates auth.json)

Interactive login (manual code paste):

```bash
python3 scripts/auth.py login
```

Automatic login via local callback server:

```bash
python3 scripts/tesla_oauth_local.py --prompt-missing-scopes
```

---

## 4) Register domain + enroll virtual key

```bash
python3 scripts/auth.py register --domain YOUR_DOMAIN.com
```

Then, on your phone (Tesla app installed):

`https://tesla.com/_ak/YOUR_DOMAIN.com`

---

## 5) Proxy Setup (for signed commands only)

> **Note:** The proxy is only needed for **sending signed commands** to the vehicle (climate, locks, charging, honk, etc.). Reading vehicle data (battery, location, temperatures) works without the proxy — those requests go directly to the Tesla Fleet API.

### Install tesla-http-proxy

Requires Go (`brew install go` on macOS).

```bash
# Pin to a specific version for supply-chain safety
go install github.com/teslamotors/vehicle-command/cmd/tesla-http-proxy@v0.4.1
```

This installs `tesla-http-proxy` to `~/go/bin/`.

### Generate TLS certificates

```bash
mkdir -p {workspace}/tesla-fleet-api/proxy
cd {workspace}/tesla-fleet-api/proxy

openssl req -x509 -newkey rsa:4096 \
  -keyout tls-key.pem -out tls-cert.pem \
  -days 365 -nodes -subj "/CN=localhost"

chmod 600 tls-key.pem
```

### Configure scripts to use the proxy

```bash
python3 scripts/auth.py config set \
  --base-url "https://localhost:4443" \
  --ca-cert "proxy/tls-cert.pem"
```

The `ca_cert` path is stored relative to the config directory and resolved at runtime.

### Start / stop the proxy

Use the convenience scripts:

```bash
# Start (uses {workspace}/tesla-fleet-api/private-key.pem)
./scripts/start_proxy.sh

# Stop
./scripts/stop_proxy.sh
```

The proxy runs in the background on `https://localhost:4443`. Logs go to `{workspace}/tesla-fleet-api/proxy/proxy.log`.

---

## 6) Test

```bash
# Data (no proxy needed)
python3 scripts/vehicles.py
python3 scripts/vehicle_data.py -c

# Commands (proxy required)
python3 scripts/command.py honk
```

---

## Places (named lat/lon)

```bash
# list
python3 scripts/command.py places list

# set explicit coords
python3 scripts/command.py places set home --lat 48.10033 --lon 17.04217

# set from current vehicle location
python3 scripts/command.py places set school --here

# use in precondition
python3 scripts/command.py precondition add -t 08:00 -d weekdays --place home
```

---

## Regional Base URLs

| Region | Audience URL |
|--------|--------------|
| Europe | `https://fleet-api.prd.eu.vn.cloud.tesla.com` |
| North America | `https://fleet-api.prd.na.vn.cloud.tesla.com` |
| China | `https://fleet-api.prd.cn.vn.cloud.tesla.cn` |

OAuth token endpoint (all regions):
```
https://fleet-auth.prd.vn.cloud.tesla.com/oauth2/v3/token
```

---

## Troubleshooting

- **Token expired (401):**
  ```bash
  python3 scripts/auth.py refresh
  ```

- **Vehicle asleep / unavailable:**
  ```bash
  python3 scripts/command.py wake
  ```

- **Command not signed / rejected:**
  Ensure the proxy is running and `base_url` + `ca_cert` are configured (step 5).
