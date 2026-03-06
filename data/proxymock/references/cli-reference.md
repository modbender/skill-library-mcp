# proxymock CLI Reference

## Default Ports

| Port | Purpose |
|------|---------|
| 4143 | Inbound proxy (client → your app) |
| 4140 | Outbound proxy (your app → external services) |
| 8080 | Default app port (`--app-port`) |

## Record Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--app-port` | 8080 | Port your app listens on |
| `--app-host` | localhost | Host where your app runs |
| `--proxy-in-port` | 4143 | Inbound proxy listen port |
| `--proxy-out-port` | 4140 | Outbound proxy listen port |
| `--out` | `proxymock/recorded-<timestamp>` | Output directory |
| `--out-format` | markdown | Output format: `markdown` or `json` |
| `--map` | - | Reverse proxy mapping `<listen>=<backend>` |
| `--app-health-endpoint` | - | Wait for health check before starting |
| `--app-log-to` | - | Redirect app output to file |
| `--log-to` | - | Redirect proxymock output to file |
| `--svc-name` | my-app | Service name for cloud snapshots |
| `--timeout` | 12h | Command timeout |
| `--health-port` | - | Expose health check endpoint |

## Mock Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--in` | `.` | Directories to read mock files from |
| `--out` | `proxymock/results/mocked-<timestamp>` | Output for observed traffic |
| `--no-out` | false | Don't write observed traffic |
| `--fast` | false | Skip simulated latency |
| `--proxy-out-port` | 4140 | Outbound proxy port |
| `--map` | - | Reverse proxy mapping |
| `--timeout` | 12h | Command timeout |

## Replay Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--test-against` | - | Target address(es) for replay |
| `--in` | `.` | Directories to read test files from |
| `--out` | `proxymock/results/replayed-<timestamp>` | Output directory |
| `--no-out` | false | Don't write results |
| `--vus` | 1 | Virtual users (parallel) |
| `--for` | - | Duration (e.g., `5m`, `1h`) |
| `--times` | 1 | Number of replay iterations |
| `--fail-if` | - | Fail conditions (repeatable) |
| `--output` | json | Output format: `pretty`, `json`, `yaml`, `csv` |
| `--performance` | false | Performance mode (sample failures only) |
| `--rewrite-host` | false | Rewrite HTTP Host header |
| `--timeout` | 12h | Command timeout |

## Replay --fail-if Metrics

**Latency (ms):** `latency.avg`, `latency.min`, `latency.max`, `latency.p50`, `latency.p75`, `latency.p90`, `latency.p95`, `latency.p99`

**Requests:** `requests.total`, `requests.succeeded`, `requests.failed`, `requests.per-second`, `requests.per-minute`, `requests.response-pct`, `requests.result-match-pct`

**Operators:** `==`, `!=`, `<`, `<=`, `>`, `>=`

## Generate Flags

| Flag | Description |
|------|-------------|
| `--out` | Output directory |
| `--host` | Override host from spec |
| `--port` | Override port |
| `--tag-filter` | Comma-separated OpenAPI tags |
| `--include-paths` | Path patterns to include |
| `--exclude-paths` | Path patterns to exclude |
| `--include-optional` | Include optional schema properties |
| `--examples-only` | Only generate from endpoints with examples |

## Signature Matching

Mock signatures determine how requests match recorded responses. Format in RRPair markdown:

```
### SIGNATURE ###
http:host is my-host
http:method is GET
http:path is /api/users
```

Edit signatures to broaden/narrow matching. Run `proxymock files update-mocks` after editing request content to regenerate signatures.

## Reverse Proxy (--map)

For languages with poor proxy env var support, or for database traffic:

```bash
# Map local port to remote backend
--map 65432=postgres://localhost:5432
--map 13306=mysql://localhost:3306
--map 18080=http://localhost:8080
```

Your app connects to the mapped local port instead of the real backend.

## Global Flags

| Flag | Description |
|------|-------------|
| `--config` | Config file path (default `~/.speedscale/config.yaml`) |
| `--context` | Named context from config |
| `--exit-zero` | Always exit 0 |
| `-v` / `--verbose` | Verbose output (stack for more) |
| `--app-url` | Speedscale app URL |
