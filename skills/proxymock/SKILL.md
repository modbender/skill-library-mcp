---
name: proxymock
description: Record, inspect, mock, replay, and generate API traffic using the proxymock CLI. Use when the user wants to capture HTTP/gRPC/database traffic, create mocks from real traffic or OpenAPI specs, replay traffic for testing, compare traffic snapshots, run mock servers, or manage proxymock RRPair files. Also use for load testing, regression testing, CI pipeline integration, or any task involving proxymock or Speedscale traffic replay.
metadata: {"openclaw":{"requires":{"binaries":["proxymock"]}}}
---

# proxymock

proxymock captures real API and database traffic via a transparent proxy, then uses it to create mocks and tests — no code changes required.

## Core Workflow

```
record → inspect → mock / replay
```

1. **Record** traffic with `proxymock record -- <app-command>`
2. **Inspect** captured RRPairs with `proxymock inspect`
3. **Mock** dependencies with `proxymock mock -- <app-command>`
4. **Replay** recorded tests with `proxymock replay --test-against <url>`

## Key Commands

### Record Traffic

```bash
# Record while running app as child process (recommended)
proxymock record -- go run .
proxymock record -- npm start

# Custom output dir
proxymock record --out my-recording -- python app.py

# Record database traffic via reverse proxy
proxymock record --map 65432=postgres://localhost:5432 -- ./my-app

# Record with custom app port
proxymock record --app-port 3000 -- ./my-app
```

Architecture: inbound proxy on `:4143` → app on `--app-port` (default 8080), outbound proxy on `:4140` captures egress.

### Mock Server

```bash
# Start mock server, launch app as child
proxymock mock -- go run .

# Source mocks from specific dir
proxymock mock --in ./my-recordings -- npm start

# Fast mode (no simulated latency)
proxymock mock --fast -- ./my-app

# Don't write observed traffic to disk
proxymock mock --no-out -- ./my-app

# Database mock via reverse proxy
proxymock mock --map 65432=localhost:5432 -- ./my-app
```

When mocking, app connects to external services through proxy on `:4140`. Matched requests return recorded responses; unmatched requests pass through to real backends.

### Replay / Load Test

```bash
# Replay recorded tests against app
proxymock replay --test-against http://localhost:8080

# Load test: 10 virtual users for 5 minutes
proxymock replay --test-against http://localhost:8080 --vus 10 --for 5m

# Run tests 3 times
proxymock replay --test-against http://localhost:8080 --times 3

# Fail on conditions (CI-friendly)
proxymock replay --test-against http://localhost:8080 \
  --fail-if "requests.failed!=0" \
  --fail-if "latency.p99>100"

# Multi-service routing
proxymock replay \
  --test-against auth=auth.example.com \
  --test-against frontend=http://localhost:8080 \
  --test-against http://localhost:9000
```

Validation metrics: `latency.{avg,p50,p90,p95,p99,max,min}`, `requests.{total,succeeded,failed,per-second,per-minute,response-pct,result-match-pct}`.

### Inspect (TUI)

```bash
proxymock inspect                    # Current directory
proxymock inspect --in ./my-recording
proxymock inspect --demo             # Demo data
```

Note: `inspect` launches a terminal UI — run with `pty=true` in exec.

### Generate Mocks from OpenAPI

```bash
proxymock generate api-spec.yaml
proxymock generate --out ./mocks --host api.staging.com api-spec.yaml
proxymock generate --tag-filter "users,orders" api-spec.yaml
proxymock generate --include-optional --examples-only api-spec.yaml
```

### File Utilities

```bash
# Compare RRPair files for differences
proxymock files compare --in recorded/ --in replayed/

# Convert between formats
proxymock files convert --in proxymock --out-format json

# Update mock signatures after editing RRPairs
proxymock files update-mocks --in ./my-mocks
```

### Cloud (Enterprise)

```bash
proxymock cloud push snapshot    # Push to Speedscale cloud
proxymock cloud pull snapshot    # Pull from cloud
```

### Import Traffic

```bash
# Import traffic from a snapshot file
proxymock import snapshot.json
proxymock import --in ./snapshots snapshot.tar.gz
```

### MCP Server

```bash
# Start Model Context Protocol (MCP) server for AI tool integration
proxymock mcp
```

### Other

```bash
proxymock send-one path/to/test.md http://localhost:8080   # Send single request
proxymock init --api-key <key>                              # Initialize config
proxymock certs                                             # Manage TLS certs
proxymock version                                           # Version info
proxymock completion bash                                   # Generate shell completions (bash/zsh/fish/powershell)
```

## RRPair Files

Traffic is stored as RRPair (request/response pair) markdown files under `proxymock/` directory. Each file contains:
- `### REQUEST (TEST) ###` or `### REQUEST (MOCK) ###` — the captured request
- `### RESPONSE ###` — the captured response
- `### SIGNATURE ###` — mock matching criteria (for mocks)

Files are human and LLM readable. Edit them directly to modify test data or mock responses, then run `proxymock files update-mocks` if you changed request details that affect the signature.

## Proxy Environment

When not using `-- <command>` child process mode, set proxy env vars manually:

```bash
# HTTP/HTTPS/gRPC
export http_proxy=http://localhost:4140
export https_proxy=http://localhost:4140
export grpc_proxy=http://$(hostname):4140

# Database (SOCKS)
export all_proxy=socks5h://localhost:4140
```

See [language reference](https://docs.speedscale.com/proxymock/getting-started/language-reference/) for language-specific setup.

## Reference

For signature matching, architecture details, and advanced usage: see `references/cli-reference.md`.
