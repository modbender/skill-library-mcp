---
name: claw-relay
description: Route AI agent traffic through a residential IP using Tailscale exit nodes — no custom code, no proxies, just WireGuard.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins:
        - tailscale
    emoji: "🏠"
    homepage: https://clawrelay.ai
---

# claw-relay

You are helping a human set up **claw-relay** — a method for routing AI agent traffic through a residential IP address using Tailscale exit nodes. No custom relay, no daemon, no proxy software. Just Tailscale.

## Architecture

There are two nodes connected by a Tailscale tunnel:

```
┌──────────────────────┐          ┌──────────────────────┐
│   CLOUD NODE         │          │   RESIDENTIAL NODE   │
│   (datacenter IP)    │          │   (home IP)          │
│                      │          │                      │
│   AI Agent           │          │   Tailscale          │
│     ↓                │          │   (exit node)        │
│   Tailscale ─────────┼── WG ───▶│     ↓                │
│   (use exit node)    │          │   Internet           │
│                      │          │   (exits from home)  │
└──────────────────────┘          └──────────────────────┘
```

- **Cloud node**: A VPS running the AI agent. Tailscale routes its traffic through the exit node.
- **Residential node**: The human's laptop running Tailscale as an exit node. Traffic exits from this IP.
- Tailscale connects the two over an encrypted WireGuard tunnel. No custom code needed.

## Which node are you setting up?

Ask the human which side they need to configure. They may need to do both, but walk through one at a time.

---

## Residential Node Setup (human's laptop — do this first)

The human's laptop becomes a Tailscale exit node, allowing the VPS to route traffic through it.

### Prerequisites

- A Tailscale account (free at https://tailscale.com)

### 1. Install Tailscale

**macOS:**
```bash
brew install tailscale
```

**Linux:**
```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

### 2. Enable as exit node

```bash
sudo tailscale up --advertise-exit-node
```

### 3. Approve the exit node

Go to the Tailscale admin console at https://login.tailscale.com/admin/machines — find the laptop and approve it as an exit node by clicking the three-dot menu → "Edit route settings" → enable "Use as exit node".

Alternatively, if you have `--accept-routes` on your policy, this happens automatically.

### Test

```bash
tailscale status
```

The laptop should show as an exit node in the tailnet.

---

## Cloud Node Setup (VPS)

This is the server running your AI agent. It joins the same tailnet and routes all traffic through the residential exit node.

### Prerequisites

- A VPS or cloud server (any provider — DigitalOcean, Hetzner, AWS, etc.)
- The residential node must already be set up as an exit node

### 1. Install Tailscale

```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

### 2. Join the tailnet and set exit node

Find the residential node's Tailscale hostname or IP:

```bash
tailscale status
```

Then set it as the exit node:

```bash
sudo tailscale up --exit-node=<laptop-hostname-or-ip>
```

Replace `<laptop-hostname-or-ip>` with the Tailscale IP (e.g., `100.64.x.x`) or hostname of the laptop.

### 3. Verify

```bash
curl https://httpbin.org/ip
```

The response should show the **residential IP** (the laptop's public IP), not the VPS IP.

---

## Agent Configuration

Once the exit node is set, **all traffic from the VPS routes through the laptop automatically**. No proxy configuration needed in your agent code — it's transparent at the network level.

Your agent code doesn't change at all:

```python
import requests

r = requests.get("https://httpbin.org/ip")
print(r.json())  # Shows the residential IP
```

```javascript
const res = await fetch("https://httpbin.org/ip");
console.log(await res.json()); // Shows the residential IP
```

```bash
curl https://httpbin.org/ip  # Shows the residential IP
```

### Per-process control (optional)

If you want only specific processes to use the exit node instead of all VPS traffic, you can use Tailscale's `--exit-node` with app-specific routing or configure `HTTPS_PROXY` with a local proxy that routes through Tailscale.

---

## Advanced: Isolation with Tailscale ACLs

For production setups, use Tailscale ACLs to control which machines can use which exit nodes:

```json
{
  "tagOwners": {
    "tag:agent": ["autogroup:admin"],
    "tag:exitnode": ["autogroup:admin"]
  },
  "acls": [
    {
      "action": "accept",
      "src": ["tag:agent"],
      "dst": ["tag:exitnode:*"]
    }
  ]
}
```

Tag your VPS as `tag:agent` and your laptop as `tag:exitnode` to restrict access.

---

## Advanced: Headscale (fully self-hosted)

If you want zero dependency on Tailscale's coordination server, use [Headscale](https://github.com/juanfont/headscale) — an open-source, self-hosted implementation of the Tailscale control server.

1. Deploy Headscale on a server you control
2. Point both nodes to your Headscale instance instead of Tailscale's servers
3. Everything else works the same — WireGuard tunnels, exit nodes, ACLs

This gives you a fully self-hosted solution with no third-party dependencies.

---

## Troubleshooting

- **Exit node not showing**: Make sure you approved it in the admin console
- **VPS still shows datacenter IP**: Run `tailscale status` to verify the exit node is connected, then `sudo tailscale up --exit-node=<laptop>` again
- **Connection drops**: Check that the laptop has internet access and Tailscale is running
- **Laptop went to sleep**: Tailscale reconnects automatically when the laptop wakes up, but the VPS will lose internet access while the laptop is offline
