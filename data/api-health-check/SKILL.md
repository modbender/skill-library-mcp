---
name: api-health-check
description: Monitor API endpoints, measure response times, and diagnose
  connectivity issues.
---


# API Health Check

Monitor API endpoints and diagnose connectivity issues.

## Instructions

1. Accept endpoint URLs from the user. If a single base URL is given, check common paths: `/`, `/health`, `/healthz`, `/api/status`, `/ping`.
2. For each endpoint, run:
   ```bash
   curl -s -o /dev/null -w "HTTP %{http_code} | %{time_total}s | %{size_download}B" -m 10 <URL>
   ```
3. Classify results:
   - 🟢 **Healthy** — 2xx, <1s
   - 🟡 **Slow** — 2xx, >1s
   - 🔴 **Down** — Non-2xx, timeout, or connection refused
4. Present summary table:
   ```
   | Endpoint | Status | Time (ms) | Verdict |
   |----------|--------|-----------|---------|
   | /health  | 200    | 142       | 🟢      |
   ```
5. For failed endpoints, diagnose:
   - DNS resolution: `dig <host> +short`
   - Port connectivity: `nc -zw3 <host> <port>`
   - SSL issues: `curl -vI https://... 2>&1 | grep -i ssl`
6. For repeated monitoring: `watch -n <interval> curl -s -o /dev/null -w "%{http_code}" <URL>`

## Security

- **Never log or display auth tokens** in output — mask as `Bearer ****`
- Accept custom headers via user input, but redact them in reports
- **SSRF prevention**: Reject requests to private/internal IPs (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.0.0/16`, `127.0.0.0/8`) unless the user explicitly confirms the target is intentional (e.g., homelab monitoring)

## Edge Cases

- **Self-signed SSL**: Use `curl -k` only if user explicitly approves
- **Redirects**: Use `curl -L` to follow; report redirect chain
- **IPv6**: Test both A and AAAA if DNS returns both
- **Rate limiting**: Space requests with 1s delay if checking many endpoints

## Requirements

- `curl` (pre-installed on most systems)
- Optional: `dig`, `nc` for deeper diagnostics
- No API keys needed
