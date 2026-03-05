---
name: zededa
description: Complete ZEDEDA edge management API client — 473 endpoints across 11 service domains for edge node, application, cluster, storage, network, Kubernetes, diagnostics, and user management.
author: Kristopher Clark
version: 1.0.0
homepage: https://github.com/krisclarkdev/zededa
license: MIT
files: ["scripts/*"]
metadata:
  clawdbot:
    requires:
      env:
        - ZEDEDA_API_TOKEN
    optional_env:
      - ZEDEDA_BASE_URL
      - ZEDEDA_LOG_LEVEL
---

# ZEDEDA Skill

Complete API client for the ZEDEDA edge computing management platform. Implements **473 endpoints** across 11 service domains with Bearer token authentication, custom error types, structured logging, and retry logic.

**Author:** Kristopher Clark  
**License:** MIT  
**Version:** 1.0.0

## Setup

```bash
export ZEDEDA_API_TOKEN="your_api_token_here"

# Optional overrides:
export ZEDEDA_BASE_URL="https://zedcontrol.zededa.net/api"   # default
export ZEDEDA_LOG_LEVEL="INFO"                                # DEBUG | INFO | WARNING | ERROR
```

The primary tool is `scripts/zededa.py`. Run any command via:

```bash
python3 -m scripts.zededa <service> <command> [--id ID] [--name NAME] [--body '{}'] [--body-file path.json]
```

## Services & Commands

### Node Service (`node`) — 91 endpoints

Manage edge nodes, hardware models, projects, brands, and PCR templates.

```bash
python3 -m scripts.zededa node list-devices
python3 -m scripts.zededa node get-device --id <device_id>
python3 -m scripts.zededa node get-device-by-serial --serial <serial>
python3 -m scripts.zededa node device-status --id <device_id>
python3 -m scripts.zededa node reboot-device --id <device_id>
python3 -m scripts.zededa node list-models
python3 -m scripts.zededa node list-projects
```

### App Service (`app`) — 123 endpoints

Manage application bundles, instances (v1+v2), images, artifacts, datastores, volumes, and patch envelopes.

```bash
python3 -m scripts.zededa app list-bundles
python3 -m scripts.zededa app list-instances
python3 -m scripts.zededa app activate-instance --id <inst_id>
python3 -m scripts.zededa app instance-logs --id <inst_id>
python3 -m scripts.zededa app list-images
python3 -m scripts.zededa app list-datastores
python3 -m scripts.zededa app list-volumes
```

### User Service (`user`) — 67 endpoints

IAM: users, roles, realms, enterprises, sessions, login, credentials, reports.

```bash
python3 -m scripts.zededa user whoami
python3 -m scripts.zededa user list-users
python3 -m scripts.zededa user list-roles
python3 -m scripts.zededa user enterprise-self
python3 -m scripts.zededa user list-sessions
```

### Storage Service (`storage`) — 33 endpoints

Patch envelopes, attestation policies, and deployment policies.

```bash
python3 -m scripts.zededa storage list-patches
python3 -m scripts.zededa storage list-attestation
python3 -m scripts.zededa storage list-deployment-policies
```

### Orchestration Service (`orchestration`) — 37 endpoints

Cluster instances, data streams, plugins, Azure deployments, API usage.

```bash
python3 -m scripts.zededa orchestration list-clusters
python3 -m scripts.zededa orchestration list-plugins
python3 -m scripts.zededa orchestration api-usage
```

### Kubernetes Service (`k8s`) — 36 endpoints

Deployments, GitOps, Helm charts/repos, secrets, ZKS clusters.

```bash
python3 -m scripts.zededa k8s list-deployments
python3 -m scripts.zededa k8s list-helm-charts
python3 -m scripts.zededa k8s list-zks
```

### Diagnostics Service (`diag`) — 21 endpoints

Device twin config, events, metrics, cloud health.

```bash
python3 -m scripts.zededa diag device-config --id <device_id>
python3 -m scripts.zededa diag events
python3 -m scripts.zededa diag health
```

### App Profile Service (`app-profile`) — 19 endpoints

Application policies and their status.

```bash
python3 -m scripts.zededa app-profile list-policies
```

### Network Service (`network`) — 16 endpoints

Network configurations and status.

```bash
python3 -m scripts.zededa network list-networks
```

### Job Service (`job`) — 17 endpoints

Bulk operations for devices, applications, and hardware models.

```bash
python3 -m scripts.zededa job list-jobs
python3 -m scripts.zededa job create-job --body '{"name":"upgrade-all","type":"BASEOS_UPGRADE"}'
```

### Edge Node Cluster Service (`cluster`) — 13 endpoints

Edge node cluster configuration and status.

```bash
python3 -m scripts.zededa cluster list-clusters
```

## Programmatic Usage

All 473 endpoints are accessible via the Python service classes:

```python
from scripts.client import ZededaClient
from scripts.node_service import NodeService
from scripts.app_service import AppService
from scripts.errors import ZededaAuthError

client = ZededaClient(token="your_token")
nodes = NodeService(client)

# List all devices
devices = nodes.query_edge_nodes()

# Get by serial
device = nodes.get_edge_node_by_serial("1234567890")

# Error handling
try:
    nodes.delete_edge_node("nonexistent")
except ZededaAuthError as e:
    print(f"Auth failed: {e}")
```

## Security & Privacy

### External Endpoints

| URL | Data Sent | Purpose |
|:----|:----------|:--------|
| `https://zedcontrol.zededa.net/api` (configurable) | API Token, request payloads | ZEDEDA API operations |

### Data Handling

Only data provided as arguments and the `ZEDEDA_API_TOKEN` env var are sent to the ZEDEDA API. The token is sanitised in all log output. No local files are read or written unless `--body-file` is used.

### Model Invocation Note

This skill is designed to be autonomously invoked by the OpenClaw agent. You can opt-out by disabling this skill.

### Trust Statement

By using this skill, data sent is limited to the arguments provided and sent directly to ZEDEDA. Only install this skill if you trust ZEDEDA with the information you provide.

## Author Verification

This skill is authored by Kristopher Clark. Identity verified via [Keybase](https://keybase.io/krisclarkdev).

<details>
<summary>Signed Proof (Keybase Saltpack)</summary>

```
BEGIN KEYBASE SALTPACK SIGNED MESSAGE. kXR7VktZdyH7rvq v5weRa0zkEnlTg9 7yljWmR5TurQlor ZjIVwF7oYGpzraX 38PX2G5XcuQ22d6 ja45ksU1WM3A9Bv UKMgb92s3JRaWg5 d6TsXlHuiZ5ALHT w0K8psUX0w9L63Z zQJMoNyTNwZDvXh Kz0a39QK3NslDMf Tr0kSja6eH0ydSq OHsUMC1ikOHG7Jo RaeFSBz5AnKZPaP DhT0VR85z64bQsk qA4R3n2sQwUmIxZ 4tHmaSRJ1KjBFAi KIeOkpHLzCtG8au 7esD10Mlhxt0xH9 xSq6jXUCDjtwYLi 8QfFjYvRv0DLNpm vgjAuWlnPRedo9i yVWeeQRl0bZfDYO 2g1liT1mUlWymvK YjV4fmOPjnFzt0Y Hj6ldtNcr3Ls1PV xop8sB9nO3Qnb53 pnGCWx1wghTuDAg QMx4. END KEYBASE SALTPACK SIGNED MESSAGE.
```

Verify with `keybase verify` or at [keybase.io/verify](https://keybase.io/verify).

</details>
