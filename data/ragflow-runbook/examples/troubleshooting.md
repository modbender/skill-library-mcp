# RAGFlow Troubleshooting Guide

## Quick Diagnosis

### 1) Service does not start

Symptom: `docker compose up -d` completes but services are not running

Checklist:

```bash
# 1) Container status
docker compose ps

# 2) Logs
docker compose logs

# 3) Resource usage
docker stats

# 4) Disk space
df -h
```

Common causes:
- Not enough RAM (recommend >= 16GB)
- Not enough disk (recommend >= 50GB)
- `vm.max_map_count < 262144` (Linux/WSL2 with Elasticsearch/OpenSearch)

---

### 2) Elasticsearch unhealthy / crash loop

Symptom: the ES container shows `unhealthy` or restarts repeatedly

```bash
cat /proc/sys/vm/max_map_count

docker compose ps
# Replace with your actual backend service name
# docker compose logs --tail=200 <backend-service>
```

Fix (Linux/WSL2):

```bash
sudo sysctl -w vm.max_map_count=262144

# Permanent (Linux)
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

---

### 3) Database connectivity issues

Symptom: RAGFlow logs show DB connection errors

```bash
# Replace with your actual service name
# docker compose logs --tail=200 <db-service>
```

Fix:

```bash
docker compose restart <db-service>
```

If you still cannot recover, consider a clean rebuild (data loss risk):

```bash
# WARNING: this may delete data volumes depending on how you run it
# docker compose down -v
# docker compose up -d
```

---

### 4) RAGFlow container starts but UI/API returns errors

```bash
# Logs
docker compose logs --tail=200 <ragflow-service>

# Liveness (no auth)
curl -i http://localhost:9380/openapi.json

# If you are behind a reverse proxy, verify you are hitting the API port (SVR_HTTP_PORT)
```

Common causes:
- You are calling the UI port instead of the API port
- Reverse proxy misconfiguration
- API path prefix mismatch (`v1/...` vs `api/v1/...`)

Fix:
- Check `openapi.json` first, then align your API calls with the paths defined there

---

### 5) Port conflicts

Symptom: compose fails with "Address already in use"

Find the process:

```bash
# Linux/WSL2
ss -ltnp | grep -E ':80|:9380|:9381|:9382' || true
lsof -i :80 || true
lsof -i :9380 || true
```

Fix:
- Edit `docker/.env` and change the exposed ports, e.g.:
  - `SVR_WEB_HTTP_PORT=8080`
  - `SVR_HTTP_PORT=9380` (or another free port)
- Restart:

```bash
docker compose down
docker compose up -d
```

---

## Debug Tools

### Collect logs bundle

```bash
#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="./ragflow-logs-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$LOG_DIR"

echo "Collecting logs into: $LOG_DIR"

docker compose ps > "$LOG_DIR/ps.txt"
docker compose logs > "$LOG_DIR/all.log"
docker stats --no-stream > "$LOG_DIR/stats.txt"

echo "Done. Attach the folder when reporting issues."
```

---

## When Asking For Help

Share:
- `docker compose ps`
- `docker compose logs --tail=200 <ragflow-service>`
- OS + RAM + disk
- Your `RAGFLOW_BASE_URL` (without secrets)
- The exact HTTP status code + endpoint you called

References:
- Upstream docs: https://ragflow.io/docs/
- GitHub issues: https://github.com/infiniflow/ragflow/issues
- Community: https://discord.gg/ragflow
