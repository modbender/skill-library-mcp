<p align="center">
  <h1 align="center">⚡ ZEDEDA</h1>
  <p align="center">
    <strong>Complete API client for the ZEDEDA edge computing management platform</strong>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/version-1.0.0-blue?style=flat-square" alt="Version">
    <img src="https://img.shields.io/badge/endpoints-473-blue?style=flat-square" alt="Endpoints">
    <img src="https://img.shields.io/badge/services-11-green?style=flat-square" alt="Services">
    <img src="https://img.shields.io/badge/tests-638-brightgreen?style=flat-square" alt="Tests">
    <img src="https://img.shields.io/badge/python-3.10%2B-yellow?style=flat-square" alt="Python">
    <img src="https://img.shields.io/badge/dependencies-zero-orange?style=flat-square" alt="Zero Dependencies">
    <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="MIT License">
  </p>
</p>

---

An [OpenClaw](https://github.com/openclaw) skill that provides **473 methods** across **11 service domains** for the ZEDEDA REST API. Built entirely on Python's standard library — no third-party dependencies required.

**Author:** Kristopher Clark ([@krisclarkdev](https://github.com/krisclarkdev))  
**License:** MIT

## Table of Contents

- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Services](#services)
- [CLI Reference](#cli-reference)
- [Programmatic Usage](#programmatic-usage)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Security & Privacy](#security--privacy)
- [License](#license)

## Quick Start

### 1. Set your API token

```bash
export ZEDEDA_API_TOKEN="your_api_token_here"
```

### 2. Run a command

```bash
# List all edge nodes
python3 -m scripts.zededa node list-devices

# Get your identity
python3 -m scripts.zededa user whoami

# Check cloud health
python3 -m scripts.zededa diag health
```

### 3. Run the tests

```bash
ZEDEDA_API_TOKEN=test python3 -m unittest discover -s tests
```

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     CLI Entrypoint                           │
│                     (zededa.py)                              │
│                  argparse routing                            │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │   Node   │  │   App    │  │   User   │  │ Storage  │      │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │      │
│  │  (91)    │  │  (123)   │  │  (67)    │  │  (33)    │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │  Orch.   │  │   K8s    │  │   Diag   │  │App Prof. │      │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │      │
│  │  (37)    │  │  (36)    │  │  (21)    │  │  (19)    │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                    │
│  │ Network  │  │   Job    │  │ Cluster  │                    │
│  │ Service  │  │ Service  │  │ Service  │                    │
│  │  (16)    │  │  (17)    │  │  (13)    │                    │
│  └──────────┘  └──────────┘  └──────────┘                    │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│              Shared HTTP Client (client.py)                  │
│    Bearer auth · retry · logging · token redaction           │
├──────────────────────────────────────────────────────────────┤
│              Error Hierarchy (errors.py)                     │
│    6 HTTP errors + 11 per-service error classes              │
└──────────────────────────────────────────────────────────────┘
```

## Services

| Service | Methods | CLI Name | Covers |
|---------|---------|----------|--------|
| **Node** | 91 | `node` | Edge nodes, brands, hardware models, projects (v1+v2), PCR templates |
| **App** | 123 | `app` | Bundles, instances (v1+v2), images, artifacts, datastores, volumes, patch envelopes |
| **User / IAM** | 67 | `user` | Users, roles, realms, enterprises, sessions, auth profiles, credentials, reports |
| **Orchestration** | 37 | `orchestration` | Cluster instances, data streams, plugins, Azure deployments, API usage |
| **Kubernetes** | 36 | `k8s` | K8s deployments, GitOps repos, Helm charts/repos, secrets, ZKS clusters |
| **Storage** | 33 | `storage` | Patch envelopes, attestation policies, deployment policies |
| **Diagnostics** | 21 | `diag` | Device twin config, events timeline, resource metrics, cloud health |
| **App Profile** | 19 | `app-profile` | Application policies CRUD, status, events, metrics |
| **Job** | 17 | `job` | Bulk operations — app import/create/refresh, OS upgrades, tag updates |
| **Network** | 16 | `network` | Network configs, status, events, metrics, tags |
| **Node Cluster** | 13 | `cluster` | Edge node cluster CRUD, status, events, tags |

## CLI Reference

### General Syntax

```bash
python3 -m scripts.zededa <service> <command> [--id ID] [--name NAME] [--body '{}'] [--body-file path.json]
```

### Common Operations

```bash
# ── Edge Nodes ──────────────────────────────────────────────
python3 -m scripts.zededa node list-devices
python3 -m scripts.zededa node get-device --id <device_id>
python3 -m scripts.zededa node get-device-by-name --name <name>
python3 -m scripts.zededa node get-device-by-serial --serial <serial>
python3 -m scripts.zededa node device-status --id <device_id>
python3 -m scripts.zededa node reboot-device --id <device_id>
python3 -m scripts.zededa node create-device --body '{"name":"new-node"}'

# ── Applications ────────────────────────────────────────────
python3 -m scripts.zededa app list-bundles
python3 -m scripts.zededa app list-instances
python3 -m scripts.zededa app activate-instance --id <instance_id>
python3 -m scripts.zededa app deactivate-instance --id <instance_id>
python3 -m scripts.zededa app restart-instance --id <instance_id>
python3 -m scripts.zededa app instance-logs --id <instance_id>

# ── Users & IAM ─────────────────────────────────────────────
python3 -m scripts.zededa user whoami
python3 -m scripts.zededa user list-users
python3 -m scripts.zededa user list-roles
python3 -m scripts.zededa user enterprise-self

# ── Infrastructure ──────────────────────────────────────────
python3 -m scripts.zededa k8s list-deployments
python3 -m scripts.zededa orchestration list-clusters
python3 -m scripts.zededa network list-networks
python3 -m scripts.zededa storage list-patches
python3 -m scripts.zededa cluster list-clusters

# ── Diagnostics ─────────────────────────────────────────────
python3 -m scripts.zededa diag health
python3 -m scripts.zededa diag events
python3 -m scripts.zededa diag device-config --id <device_id>

# ── Jobs / Bulk ─────────────────────────────────────────────
python3 -m scripts.zededa job list-jobs
python3 -m scripts.zededa job create-job --body-file upgrade_spec.json
```

### Using JSON Body

Pass a request body inline or from a file:

```bash
# Inline JSON
python3 -m scripts.zededa node create-device --body '{"name":"edge-01","title":"Edge Node 01"}'

# From file
python3 -m scripts.zededa app create-bundle --body-file ./my-app-bundle.json
```

## Programmatic Usage

All 473 endpoints are accessible directly via the Python service classes:

```python
from scripts.client import ZededaClient
from scripts.node_service import NodeService
from scripts.app_service import AppService
from scripts.user_service import UserService
from scripts.errors import ZededaAuthError, ZededaNotFoundError

# Initialize client (reads ZEDEDA_API_TOKEN from env)
client = ZededaClient()

# ── Node operations ─────────────────────────────────────────
nodes = NodeService(client)
all_devices = nodes.query_edge_nodes(next_pageSize=50)
device = nodes.get_edge_node_by_serial("SN-12345")
nodes.reboot_edge_node(device["id"])

# ── App lifecycle ───────────────────────────────────────────
apps = AppService(client)
instances = apps.query_edge_application_instances()
apps.activate_edge_application_instance("instance-uuid")
logs = apps.get_edge_application_instance_logs("instance-uuid")

# ── User management ─────────────────────────────────────────
users = UserService(client)
me = users.get_user_self()
print(f"Logged in as: {me.get('name')}")

# ── Error handling ──────────────────────────────────────────
try:
    nodes.get_edge_node("nonexistent-id")
except ZededaNotFoundError as e:
    print(f"Device not found: {e}")
    print(f"Details: {e.to_dict()}")
except ZededaAuthError as e:
    print(f"Authentication failed: {e}")
```

### Custom Base URL

```python
client = ZededaClient(
    token="my-token",
    base_url="https://my-zedcontrol.example.com/api"
)
```

## Testing

### Run All Tests

```bash
ZEDEDA_API_TOKEN=test python3 -m unittest discover -s tests -v
```

### Test Suite Breakdown

| File | Tests | Covers |
|------|-------|--------|
| `test_errors.py` | 20 | Error hierarchy, field storage, `to_dict()`, HTTP status mapping |
| `test_client.py` | 18 | Init/auth validation, URL building, token sanitisation, retry logic, convenience wrappers |
| `test_services.py` | 105 | All 11 services — correct HTTP method, URL path, method count assertions |
| `test_cli.py` | 11 | JSON body loading, output formatting, help flags, command dispatch |
| **+ exhaustive per-method tests** | | **484** |
| **Grand Total** | | **638** |

All tests use `unittest.mock` to avoid real HTTP calls — no network or credentials needed.

## Project Structure

```
zededa/
├── SKILL.md                         # OpenClaw skill manifest & documentation
├── README.md                        # This file
├── LICENSE                          # MIT License
├── .gitignore
├── scripts/
│   ├── __init__.py                  # Package init
│   ├── client.py                    # Shared HTTP client (auth, retry, logging)
│   ├── errors.py                    # Custom error hierarchy (17 classes)
│   ├── zededa.py                    # CLI entrypoint (argparse)
│   ├── node_service.py              # Edge Node Service (91 methods)
│   ├── app_service.py               # Edge Application Service (123 methods)
│   ├── user_service.py              # User / IAM Service (67 methods)
│   ├── orchestration_service.py     # Orchestration Service (37 methods)
│   ├── kubernetes_service.py        # Kubernetes Service (36 methods)
│   ├── storage_service.py           # Storage Service (33 methods)
│   ├── diag_service.py              # Diagnostics Service (21 methods)
│   ├── app_profile_service.py       # App Profile Service (19 methods)
│   ├── job_service.py               # Job / Bulk Operations Service (17 methods)
│   ├── network_service.py           # Network Service (16 methods)
│   └── node_cluster_service.py      # Node Cluster Service (13 methods)
├── specs/                           # Downloaded ZEDEDA Swagger/OpenAPI specs
│   ├── zedge_node_service.swagger.json
│   ├── zedge_app_service.swagger.json
│   ├── zedge_user_service.swagger.json
│   └── ... (11 spec files)
└── tests/
    ├── __init__.py
    ├── test_errors.py               # Error hierarchy tests
    ├── test_client.py               # HTTP client tests
    ├── test_services.py             # All 11 service module tests
    └── test_cli.py                  # CLI entrypoint tests
```

## Configuration

| Environment Variable | Required | Default | Description |
|---------------------|----------|---------|-------------|
| `ZEDEDA_API_TOKEN` | **Yes** | — | Bearer token for API authentication |
| `ZEDEDA_BASE_URL` | No | `https://zedcontrol.zededa.net/api` | API base URL |
| `ZEDEDA_LOG_LEVEL` | No | `INFO` | Log verbosity: `DEBUG`, `INFO`, `WARNING`, `ERROR` |

### Getting an API Token

1. Log in to your ZEDEDA console at [zedcontrol.zededa.net](https://zedcontrol.zededa.net)
2. Navigate to **Administration → API Tokens**
3. Generate a new token with the appropriate scope
4. Export it: `export ZEDEDA_API_TOKEN="your-token"`

## Error Handling

The skill provides a structured error hierarchy for precise exception handling:

```
ZededaError (base)
├── ZededaAuthError          # 401 / 403
├── ZededaValidationError    # 400
├── ZededaNotFoundError      # 404
├── ZededaConflictError      # 409
├── ZededaRateLimitError     # 429
├── ZededaServerError        # 5xx
├── NodeServiceError
├── AppServiceError
├── UserServiceError
├── StorageServiceError
├── OrchestrationServiceError
├── KubernetesServiceError
├── DiagServiceError
├── AppProfileServiceError
├── NetworkServiceError
├── JobServiceError
└── NodeClusterServiceError
```

Every error includes:
- `message` — human-readable description
- `endpoint` — API path that failed
- `method` — HTTP method used
- `status_code` — HTTP status code
- `response_body` — raw API response
- `timestamp` — ISO 8601 timestamp
- `to_dict()` — serializable summary

## Key Features

- **Zero dependencies** — stdlib only (`urllib`, `json`, `argparse`)
- **Bearer token authentication** with automatic header injection
- **Retry logic** — automatic retries on 429 / 5xx with exponential backoff
- **Token redaction** — sensitive data is sanitised in all log output
- **Structured logging** — configurable with `ZEDEDA_LOG_LEVEL`
- **Full v1 + v2 API coverage** — includes beta and v2 app instance endpoints
- **154 unit tests** — complete test suite with zero network dependencies

## Security & Privacy

| URL | Data Sent | Purpose |
|-----|-----------|---------|
| `https://zedcontrol.zededa.net/api` (configurable) | API token + request payloads | ZEDEDA API operations |

- Only data provided as arguments and the `ZEDEDA_API_TOKEN` env var are transmitted
- The bearer token is redacted in all log output
- No local files are read unless `--body-file` is explicitly used
- No telemetry, analytics, or data collection of any kind

## Author Verification

This skill is authored by Kristopher Clark. Identity verified via [Keybase](https://keybase.io/krisclarkdev).

<details>
<summary>Signed Proof (Keybase Saltpack)</summary>

```
BEGIN KEYBASE SALTPACK SIGNED MESSAGE. kXR7VktZdyH7rvq v5weRa0zkEnlTg9 7yljWmR5TurQlor ZjIVwF7oYGpzraX 38PX2G5XcuQ22d6 ja45ksU1WM3A9Bv UKMgb92s3JRaWg5 d6TsXlHuiZ5ALHT w0K8psUX0w9L63Z zQJMoNyTNwZDvXh Kz0a39QK3NslDMf Tr0kSja6eH0ydSq OHsUMC1ikOHG7Jo RaeFSBz5AnKZPaP DhT0VR85z64bQsk qA4R3n2sQwUmIxZ 4tHmaSRJ1KjBFAi KIeOkpHLzCtG8au 7esD10Mlhxt0xH9 xSq6jXUCDjtwYLi 8QfFjYvRv0DLNpm vgjAuWlnPRedo9i yVWeeQRl0bZfDYO 2g1liT1mUlWymvK YjV4fmOPjnFzt0Y Hj6ldtNcr3Ls1PV xop8sB9nO3Qnb53 pnGCWx1wghTuDAg QMx4. END KEYBASE SALTPACK SIGNED MESSAGE.
```

Verify with `keybase verify` or at [keybase.io/verify](https://keybase.io/verify).

</details>

## License

MIT License — Copyright (c) 2026 Kristopher Clark

See [LICENSE](LICENSE) for full text.
