---
name: telnyx-network
description: Private mesh networking and public IP exposure via Telnyx WireGuard infrastructure. Connect nodes securely or expose services to the internet.
metadata: {"openclaw":{"emoji":"🌐","requires":{"bins":["wg"],"env":["TELNYX_API_KEY"]},"primaryEnv":"TELNYX_API_KEY"}}
---

# Telnyx Network

Private mesh networking and public IP exposure via Telnyx WireGuard infrastructure.

## Requirements

- **Telnyx API Key** — [Get one free](https://portal.telnyx.com/#/app/api-keys)
- **WireGuard** installed on your machine

## Agent Use (OpenClaw)

WireGuard requires elevated permissions to create network interfaces. For OpenClaw to manage your mesh autonomously, run this **once**:

```bash
sudo ./setup-sudoers.sh
```

This adds a sudoers rule allowing WireGuard commands without password prompts. After setup, your agent can:

```bash
# Agent can now do all of this without password prompts:
./setup.sh --region ashburn-va
./join.sh --name "my-node" --apply
./register.sh --name "my-node"
./teardown.sh
```

**What it does:**
- Adds `/etc/sudoers.d/wireguard-<username>`
- Only allows `wg` and `wg-quick` commands (not blanket sudo)
- Can be removed anytime: `sudo rm /etc/sudoers.d/wireguard-*`

**Without this setup**, the agent can still create networks and generate configs, but you'll need to manually run `sudo wg-quick up <config>` to connect.

## Two Modes

### Mesh Mode (Private)
Connect multiple machines in a private network. Like Tailscale, but on Telnyx infrastructure.

```bash
./setup.sh --region ashburn-va
./join.sh --name "laptop"
./join.sh --name "server"  # run on server
# Now laptop and server can talk via 172.27.0.x
```

**Cost: $10/month** (WireGuard Gateway)

### Expose Mode (Public)
Get a public IP and expose services to the internet.

```bash
./setup.sh --region ashburn-va
./join.sh --name "server" --apply
./add-public-ip.sh
./expose.sh 443
# Now https://64.16.x.x:443 reaches your server
```

**Cost: $60/month** (WireGuard Gateway + Internet Gateway)

## Commands

| Command | Description |
|---------|-------------|
| `sudo ./setup-sudoers.sh` | Enable passwordless sudo for WireGuard (one-time, for agent use) |
| `./setup.sh --region <code>` | Create network + WireGuard gateway |
| `./join.sh --name <name>` | Add this machine to the mesh |
| `./peers.sh` | List all connected peers |
| `./add-public-ip.sh` | Add internet gateway (public IP) |
| `./expose.sh <port>` | Open a port |
| `./unexpose.sh <port>` | Close a port |
| `./status.sh` | Show full status |
| `./teardown.sh` | Delete everything |
| `./register.sh --name <name>` | Register node in mesh registry |
| `./discover.sh` | Discover other nodes on mesh |
| `./unregister.sh --name <name>` | Remove node from registry |

## Node Discovery

Nodes on the mesh can find each other using a registry stored in Telnyx Storage. This enables OpenClaw instances to automatically discover and communicate with each other.

### Register This Node

After joining the mesh, register your node so others can find it:

```bash
./register.sh --name "home-server"
```

### Discover Other Nodes

Find all registered nodes on the mesh:

```bash
./discover.sh

# Output:
# NAME            IP              HOSTNAME             REGISTERED
# home-server     172.27.0.1      macbook.local        2026-01-31 ✅
# work-laptop     172.27.0.2      thinkpad             2026-01-31 ✅

# JSON output for scripts
./discover.sh --json
```

### Unregister

Remove a node from the registry:

```bash
./unregister.sh --name "old-server"
```

### Use Case: Multi-OpenClaw Communication

```bash
# On OpenClaw A
./join.sh --name "openclaw-a" --apply
./register.sh --name "openclaw-a"

# On OpenClaw B
./join.sh --name "openclaw-b" --apply
./register.sh --name "openclaw-b"

# Either can now discover the other
./discover.sh
# → Shows both openclaw-a and openclaw-b with their mesh IPs

# Direct communication works via mesh IPs
curl http://172.27.0.2:18789/health  # OpenClaw B's gateway
```

This completes the "host-to-local node sessions" and "direct comms between OpenClaws" use cases.

## Regions

| Region | Code | Location |
|--------|------|----------|
| US East | `ashburn-va` | Ashburn, VA |
| US Central | `chicago-il` | Chicago, IL |
| EU | `frankfurt-de` | Frankfurt, DE |
| EU | `amsterdam-nl` | Amsterdam, NL |

Get full list:
```bash
./setup.sh --region help
```

## Safety

### Blocked Ports (need --force)
- 22 (SSH)
- 23 (Telnet)
- 3306 (MySQL)
- 5432 (PostgreSQL)
- 6379 (Redis)
- 27017 (MongoDB)

### Firewall
Only explicitly exposed ports accept traffic on the WireGuard interface. All other ports are blocked by default.

## Configuration

All state is stored in `config.json`:

```json
{
  "network_id": "...",
  "region": "ashburn-va",
  "wireguard_gateway": {
    "id": "...",
    "endpoint": "64.16.x.x:5107",
    "subnet": "172.27.0.1/24"
  },
  "internet_gateway": {
    "id": "...",
    "public_ip": "64.16.x.x"
  },
  "peers": [...],
  "exposed_ports": [443, 80]
}
```

## Use Cases

### 1. Connect OpenClaw Instances
```bash
# On main server
./setup.sh --region ashburn-va
./join.sh --name "openclaw-main" --apply

# On secondary server
./join.sh --name "openclaw-backup" --apply

# Now they can communicate securely
```

### 2. Expose Webhook Endpoint
```bash
./add-public-ip.sh
./expose.sh 443
# Configure your webhook URL as https://64.16.x.x/webhook
```

### 3. Multi-Region Mesh
```bash
./setup.sh --region ashburn-va
./join.sh --name "us-east-server"

# Same network, different region gateway
./setup.sh --region frankfurt-de --name same-network
./join.sh --name "eu-server"
```

## Pricing

| Component | Monthly Cost |
|-----------|--------------|
| WireGuard Gateway | $10 |
| Internet Gateway | $50 |
| Peers | Free |
| Traffic | Free (beta) |

## Troubleshooting

### "Gateway still provisioning"
Wait 5-10 minutes after setup for the gateway to be ready.

### "Connection refused"
- Check WireGuard is running: `sudo wg show`
- Check port is exposed: `./status.sh`
- Check firewall: `sudo iptables -L -n`

### "Permission denied"
WireGuard requires root. Run with `sudo` or use `--apply` flag.

## License

MIT
