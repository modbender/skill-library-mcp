# Funda Gateway Workflow

Short operating guide for agents managing the local Funda gateway.

## Rules

- Default bind: `127.0.0.1` (loopback)
- Start gateway on `127.0.0.1` only
- For periodic tasks in OpenClaw / ClawHub, use **Heartbeat** (not cron)
- Reuse a healthy running gateway; do not restart on every request
- Restart only after skill update or when unhealthy
- Do not expose the gateway publicly (no auth / no rate limiting)

Heartbeat docs:
- https://docs.openclaw.ai/gateway/heartbeat

## 1. Check Running Gateway

Check process first:

```bash
pgrep -af "python.*scripts/funda_gateway.py"
```

Optional health check:

```bash
curl -s http://127.0.0.1:9090/search_listings >/dev/null
```

If healthy, reuse it.

## 2. Prepare Environment (if needed)

From the Funda skill local folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r scripts/requirements.txt
```

If `.venv` already exists:

```bash
source .venv/bin/activate
```

## 3. Start Gateway

Run from the Funda skill local folder:

```bash
python scripts/funda_gateway.py --port 9090 --timeout 10
```

Notes:
- Gateway binds to `127.0.0.1` only
- Startup stops if `127.0.0.1:9090` is already occupied by the gateway

## 4. Health Check After Start

```bash
curl -sG "http://127.0.0.1:9090/search_listings" \
  --data-urlencode "location=Amsterdam" \
  --data-urlencode "page=0"
```

Expect HTTP 200 + JSON object (possibly empty).

## 5. Stop Gateway (if needed)

Foreground process: `Ctrl+C`

Background process:

```bash
pgrep -af "python.*scripts/funda_gateway.py"
pkill -f "python.*scripts/funda_gateway.py"
```

Port troubleshooting only:

```bash
lsof -iTCP:9090 -sTCP:LISTEN -n -P
```
