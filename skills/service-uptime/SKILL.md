---
name: service-uptime
description: Monitor website uptime, measure response times, and check HTTP
  status codes for any URL.
---


# Uptime Monitor

Check website availability, response times, and HTTP status codes.

## Requirements

- `curl` (pre-installed on most systems)
- No API keys needed

## Instructions

### Single URL check
```bash
curl -o /dev/null -s -w "HTTP %{http_code} | DNS: %{time_namelookup}s | Connect: %{time_connect}s | TLS: %{time_appconnect}s | Total: %{time_total}s\n" -L --max-time 10 https://example.com
```

### Bulk check (multiple URLs)
```bash
for url in https://example.com https://google.com https://github.com; do
  result=$(curl -o /dev/null -s -w "%{http_code} %{time_total}" -L --max-time 10 "$url" 2>/dev/null)
  code=$(echo $result | awk '{print $1}')
  time=$(echo $result | awk '{print $2}')
  echo "$url: HTTP $code (${time}s)"
done
```

### Repeated monitoring
```bash
# Check every 30 seconds for 5 minutes (10 checks)
for i in $(seq 1 10); do
  curl -o /dev/null -s -w "%{http_code} %{time_total}s" --max-time 10 https://example.com
  echo " [$(date +%H:%M:%S)]"
  sleep 30
done
```

### Output format
```
## 🌐 Uptime Report — <timestamp>

| URL | Status | Code | DNS | Connect | TLS | Total |
|-----|--------|------|-----|---------|-----|-------|
| example.com | 🟢 Up | 200 | 0.012s | 0.034s | 0.089s | 0.145s |
| broken.com | 🔴 Down | 000 | — | — | — | timeout |
| slow.com | 🟡 Slow | 200 | 0.015s | 0.040s | 0.095s | 3.210s |

**Thresholds**: 🟢 < 1s | 🟡 1–3s | 🔴 > 3s or error
```

## Edge Cases

- **Redirects**: Use `-L` to follow redirects. Report final URL if different from input.
- **Timeout**: Use `--max-time 10` to avoid hanging. Report as 🔴 Down.
- **Self-signed certs**: Use `-k` flag only if user explicitly requests (insecure).
- **Non-HTTP**: This tool checks HTTP/HTTPS only. For TCP/ping, use `nc` or `ping`.
- **DNS failure**: curl returns code 000 — report as DNS resolution failure.
- **HTTP auth required**: 401/403 doesn't mean "down" — note the distinction.

## Security

- Only performs GET requests — no data modification.
- Don't monitor URLs that require authentication tokens in the URL (they'd be logged).
- Validate URL format before making requests.
