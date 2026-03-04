---
name: observability-lgtm
version: 1.2.0
description: Set up a full local LGTM observability stack (Loki + Grafana + Tempo + Prometheus + Alloy) for FastAPI apps. One Docker Compose, one Python import, unified dashboards.
homepage: https://github.com/reddinft/skill-observability-lgtm
metadata:
  {
    "openclaw": {
      "emoji": "📊",
      "requires": { "bins": ["docker", "docker-compose"], "env": [] },
      "network": { "outbound": false, "reason": "All services run locally in Docker. No external network calls. Grafana/Prometheus/Loki/Tempo are self-hosted only." }
    }
  }
---

# observability-lgtm

Set up a full local observability stack (Loki + Grafana + Tempo + Prometheus + Alloy)
for FastAPI apps on macOS (Apple Silicon) or Linux. One command to start, one import
to instrument any app. Logs → Loki, metrics → Prometheus, traces → Tempo, all
unified in Grafana.

## When to use
- User is building a FastAPI web app and wants logs, metrics, and traces
- User wants a local Grafana dashboard without setting up ELK (too heavy)
- User wants to correlate logs ↔ traces ↔ metrics in one UI
- User has multiple local apps and wants universal observability

## When NOT to use
- Production cloud deployments (use managed Grafana Cloud or Datadog instead)
- Non-Python apps (the Python lib only works for FastAPI; the stack itself is language-agnostic)
- When Docker is not available

## Prerequisites
- Docker + Docker Compose v2 installed
- Python 3.10+ (for the instrumentation lib)
- FastAPI app to instrument

## What gets installed
| Service | Port | Purpose |
|---|---|---|
| Grafana | 3000 | Dashboards — no login in dev mode |
| Prometheus | 9091 | Metrics scraping (avoids 9090 if MinIO running) |
| Loki | 3300 | Log storage (avoids 3100 if Langfuse running) |
| Tempo gRPC | 4317 | OTLP trace receiver |
| Tempo HTTP | 4318 | OTLP HTTP alternative |
| Alloy UI | 12345 | Agent status |

## Steps

### Step 1 — Check for port conflicts

```bash
lsof -iTCP -sTCP:LISTEN -n -P 2>/dev/null | grep -E ":(3000|3300|9091|4317|4318|12345)" | awk '{print $9, $1}'
```

If any of the ports above are in use, update the relevant port in docker-compose.yml
and the matching `url:` in config/grafana/provisioning/datasources/datasources.yml.
Common conflicts: Langfuse on 3100, MinIO on 9090.

### Step 2 — Copy the stack

Copy these files from the skill directory into a `projects/observability/` folder
in the workspace:
- `assets/docker-compose.yml`
- `assets/config/` (entire directory tree)
- `assets/lib/observability.py`
- `assets/scripts/register_app.sh`

```bash
mkdir -p projects/observability
cp -r SKILL_DIR/assets/* projects/observability/
mkdir -p projects/observability/logs
touch projects/observability/logs/.gitkeep
chmod +x projects/observability/scripts/register_app.sh
```

### Step 3 — Start the stack

```bash
cd projects/observability
docker compose up -d
```

Wait ~15 seconds for all services to start, then verify:

```bash
curl -s -o /dev/null -w "Grafana: %{http_code}\n"    http://localhost:3000/api/health
curl -s -o /dev/null -w "Prometheus: %{http_code}\n" http://localhost:9091/-/healthy
curl -s -o /dev/null -w "Loki: %{http_code}\n"       http://localhost:3300/ready
curl -s -o /dev/null -w "Tempo: %{http_code}\n"      http://localhost:4318/ready
```

All should return 200. If Loki or Tempo return 503, wait 10 more seconds and retry
(they have a slower startup than Grafana/Prometheus).

### Step 4 — Install Python deps for the app

```bash
pip install \
  "prometheus-fastapi-instrumentator>=7.0.0" \
  "opentelemetry-sdk>=1.25.0" \
  "opentelemetry-exporter-otlp-proto-grpc>=1.25.0" \
  "opentelemetry-instrumentation-fastapi>=0.46b0" \
  "python-json-logger>=2.0.7"
```

### Step 5 — Instrument the FastAPI app

Add to the app's `app.py` (or `main.py`), just after `app = FastAPI(...)`:

```python
import sys
sys.path.insert(0, "path/to/projects/observability/lib")
from observability import setup_observability
logger = setup_observability(app, service_name="my-service-name")
```

That's it. The app now:
- Exposes `/metrics` for Prometheus
- Writes JSON logs to `projects/observability/logs/my-service-name/app.log`
- Sends traces to Tempo on localhost:4317

### Step 6 — Register with Prometheus

```bash
cd projects/observability
./scripts/register_app.sh my-service-name <port>
# e.g.: ./scripts/register_app.sh image-gen-studio 7860
```

Prometheus hot-reloads the target within 30 seconds. Verify:

```bash
curl -s "http://localhost:9091/api/v1/targets" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for t in data['data']['activeTargets']:
    svc = t['labels'].get('service', '')
    print(svc, '->', t['health'])
"
```

### Step 7 — Open Grafana

Open http://localhost:3000

The **FastAPI — App Overview** dashboard is pre-loaded. Select your service from
the dropdown at the top. You'll see:
- Request rate (req/s)
- Error rate (%)
- Latency p50/p95/p99
- Requests by endpoint
- HTTP status codes
- Live log panel (Loki)

To jump from a log line to its trace: click the trace_id link in the log detail panel.
It opens the full trace in Tempo automatically (datasource pre-wired).

### Step 8 — Import additional dashboards (optional)

In Grafana → Dashboards → Import:
- **16110** — FastAPI Observability (richer alternative to the built-in)
- **13407** — Loki Logs Overview
- **16112** — Tempo Service Graph (service dependency map)

## Useful commands

```bash
# Reload Prometheus config after registering a new app:
curl -s -X POST http://localhost:9091/-/reload

# Restart a single service without losing data:
docker compose -f projects/observability/docker-compose.yml restart grafana

# Stop everything (data volumes preserved):
docker compose -f projects/observability/docker-compose.yml down

# Nuclear reset (wipes all stored data):
docker compose -f projects/observability/docker-compose.yml down -v

# Check Alloy log shipping status:
open http://localhost:12345
```

## Manual tracing (optional)

```python
from observability import get_tracer
tracer = get_tracer(__name__)

@app.get("/expensive-endpoint")
async def handler():
    with tracer.start_as_current_span("db-query") as span:
        span.set_attribute("db.table", "users")
        result = await db.query(...)
    return result
```

## Log/trace correlation

The OTel instrumentation injects `trace_id` into every log record. Grafana Loki
is pre-configured with a derived field that turns `"trace_id":"abc123"` into a
clickable link to the Tempo trace.

To manually include trace context in your own log calls:

```python
from opentelemetry import trace

def trace_ctx() -> dict:
    ctx = trace.get_current_span().get_span_context()
    return {"trace_id": format(ctx.trace_id, "032x")} if ctx.is_valid else {}

logger.info("Processing request", extra=trace_ctx())
```

## Notes

- Logs are written to `projects/observability/logs/<service>/app.log` as JSON.
  Alloy tails these files and ships to Loki — no code changes needed beyond setup_observability().
- All observability is local — no data leaves the machine.
- `data_classification: LOCAL_ONLY` is the default for all traces/logs.
- The Alloy config drops DEBUG-level logs by default. Edit `config/alloy/config.alloy`
  to remove the `stage.drop` block if you need debug logs.
