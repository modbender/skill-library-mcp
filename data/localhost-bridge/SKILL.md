---
name: localhost-bridge
description: "Bridge Docker containers to host localhost services via socat. Solves the #1 networking issue in containerized AI agent deployments: containers can't reach services bound to 127.0.0.1."
homepage: "https://casys.ai/blog/the-localhost-trap"
source: "https://github.com/Casys-AI/casys-pml-cloud"
author: "Erwan Lee Pesle (superWorldSavior)"
always: false
privileged: false
requires:
  - sudo access (systemd service creation, UFW rules)
  - Docker daemon access (docker inspect, docker network inspect)
  - socat package (apt install socat)
---

# localhost-bridge — Connect containers to host localhost services

## ⚠️ Security & Privileges

**This skill requires host-level privileges.** It must be reviewed and executed manually by an administrator — never autonomously by an agent.

What it does on the host:
- Creates a **systemd service** (persistent across reboots) that forwards traffic from a Docker bridge IP to localhost
- Adds a **UFW firewall rule** scoped to a specific Docker bridge interface
- Requires **sudo**, **Docker daemon access**, and **socat** from your distro's official package repository

**Before running any command:**
1. Review the generated `/etc/systemd/system/socat-<SOURCE_NETWORK>-<TARGET_SERVICE>-<PORT>.service` file — confirm `ExecStart` binds only to the intended Docker bridge IP (172.x.x.1), never 0.0.0.0
2. Review the UFW rule — confirm it targets the correct `br-<ID>` interface and port
3. After setup, verify the port is NOT reachable from the public network: `curl --connect-timeout 2 http://<PUBLIC_IP>:<PORT>/` must fail
4. Test from inside a container before deploying widely

**Do not grant an automated agent permissions to run these commands without human approval.**

---

## The Problem

A service on the host listens on `127.0.0.1` (AI gateway, MCP server, Ollama, database...). A Docker container needs to reach it. `localhost` inside the container points to the container itself, not the host. Requests either timeout silently (firewall drops packets) or get connection refused.

## The Solution

`socat` listens on the Docker bridge gateway IP and forwards to host loopback. Combined with a scoped firewall rule, this gives containers access without exposing the service externally.

## Setup (run manually as admin)

### 1. Find the Docker bridge gateway IP

```bash
# For a specific container
docker inspect <container_name> --format '{{json .NetworkSettings.Networks}}' \
  | python3 -c "
import json,sys
d = json.load(sys.stdin)
for net, info in d.items():
    print(f'{net}: gateway={info[\"Gateway\"]}')"
```

### 2. Create a systemd service

Replace `<GATEWAY_IP>`, `<PORT>`, `<SOURCE_NETWORK>`, and `<TARGET_SERVICE>` with your values.

**Naming convention:** `socat-<source_network>-<target_service>-<port>` — source network is the Docker network (consumer), target service is the host service. Self-documenting.

Examples: `socat-bridge-gateway-18789`, `socat-windmill_default-gateway-18789`, `socat-bridge-ollama-11434`

**Review the ExecStart line before enabling** — confirm it binds to the Docker bridge IP only.

```bash
sudo tee /etc/systemd/system/socat-<SOURCE_NETWORK>-<TARGET_SERVICE>-<PORT>.service > /dev/null << 'EOF'
[Unit]
Description=Socat bridge: <SOURCE_NETWORK> -> <TARGET_SERVICE>:<PORT>
After=network.target docker.service

[Service]
Type=simple
ExecStart=/usr/bin/socat TCP-LISTEN:<PORT>,bind=<GATEWAY_IP>,fork,reuseaddr TCP:127.0.0.1:<PORT>
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Review the file before enabling:
cat /etc/systemd/system/socat-<SOURCE_NETWORK>-<TARGET_SERVICE>-<PORT>.service

sudo systemctl daemon-reload
sudo systemctl enable --now socat-<SOURCE_NETWORK>-<TARGET_SERVICE>-<PORT>
```

### 3. Add firewall rule (MANDATORY)

Without this, socat listens but packets from the container are silently dropped — causing 30-second timeouts with no error.

**Review the bridge ID before applying** — a wrong ID can expose services.

```bash
# Find the Linux bridge interface for the Docker network
BRIDGE_ID=$(docker network inspect <network_name> --format '{{.Id}}' | cut -c1-12)

# Verify this is the right bridge
ip link show br-${BRIDGE_ID}

# Allow traffic only on that bridge interface
sudo ufw allow in on br-${BRIDGE_ID} to any port <PORT> proto tcp comment "<SOURCE_NETWORK>-<TARGET_SERVICE>-<PORT>"
```

### 4. Verify security

```bash
# MUST succeed (from inside a container)
docker exec <container_name> curl -s --connect-timeout 5 http://<GATEWAY_IP>:<PORT>/

# MUST fail (from the public network)
curl --connect-timeout 2 http://<PUBLIC_IP>:<PORT>/
```

## Multi-Network Workers

A container can be on multiple Docker networks. Each has its own bridge IP. You need a socat instance + firewall rule for **each network** the container uses. In practice, one network is usually enough.

Check all networks: `docker inspect <container> --format '{{json .NetworkSettings.Networks}}'`

## Common Use Cases

| Host service | Container client | Default port |
|---|---|---|
| AI gateway (OpenClaw, LiteLLM) | Workflow orchestrator (Windmill, n8n) | 18789 |
| MCP server | Dockerized agent | varies |
| Ollama | RAG pipeline, agent | 11434 |
| PostgreSQL | API server | 5432 |
| Redis | Any containerized app | 6379 |

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| 30s timeout, no error | Firewall dropping packets | Add UFW rule on the bridge interface |
| Connection refused | socat not running | `systemctl status socat-<SOURCE_NETWORK>-<TARGET_SERVICE>-<PORT>` |
| Works then stops after Docker restart | Bridge IP changed | Check new gateway IP, update socat bind |
| socat won't start after reboot | Docker not ready | Ensure `After=docker.service` in unit file |

## Alternatives

Depending on your security posture, consider:
- **Docker host networking** (`network_mode: host`) — simpler but removes all container network isolation
- **Running socat inside a minimal privileged container** — avoids host-level systemd changes
- **Configuring the host service to bind to the Docker bridge IP directly** — no socat needed, but the service must support custom bind addresses
- **`host.docker.internal`** (Docker Desktop) — works on Mac/Windows, not reliably on Linux

## Prerequisites

Install socat from your distro's official package repository:

```bash
sudo apt-get install -y socat  # Debian/Ubuntu
sudo dnf install -y socat      # Fedora/RHEL
```

## References

- Blog post: [The Localhost Trap](https://casys.ai/blog/the-localhost-trap) — why this problem exists and why it matters for AI infrastructure
- Source: [Casys-AI/casys-pml-cloud](https://github.com/Casys-AI/casys-pml-cloud)
- Docker docs: [Packet filtering and firewalls](https://docs.docker.com/engine/network/packet-filtering-firewalls/)
