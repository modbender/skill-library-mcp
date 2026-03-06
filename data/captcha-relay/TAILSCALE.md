# Tailscale Setup for CAPTCHA Relay

Tailscale creates a private mesh VPN (Tailnet) between your devices. With it, the relay server is directly accessible from your phone — no tunneling, no splash pages, no TLS issues.

## Why Tailscale?

| Approach | Pros | Cons |
|----------|------|------|
| localtunnel | Free, no setup | Splash page, unreliable, public URL |
| cloudflared | Fast | Heavy binary, resource-hungry |
| **Tailscale** | Always-on, private, fast, no splash | Requires install on both devices |

## Setup

### 1. Server (Ubuntu Linux)

```bash
# Install
curl -fsSL https://tailscale.com/install.sh | sh

# Start and authenticate
sudo tailscale up

# Note your Tailscale IP
tailscale ip -4
# e.g., 100.x.y.z
```

The machine gets a stable `100.x.y.z` Tailscale IP on your private Tailnet.

### 2. Phone (iOS/Android)

1. Install Tailscale from App Store / Play Store
2. Sign in with the same account (Google, Microsoft, GitHub, etc.)
3. Enable the VPN toggle
4. Both devices are now on the same Tailnet

### 3. Integration with captcha-relay

Run with `--no-tunnel` and use the Tailscale IP:

```bash
# On the server
TAILSCALE_IP=$(tailscale ip -4)
node index.js --no-tunnel
# The relay URL will be http://100.x.y.z:PORT
```

Or in module mode:

```js
const result = await solveCaptcha({
  useTunnel: false,  // no tunnel needed
});
// result.relayUrl will be http://<local-ip>:PORT
// With Tailscale, <local-ip> should resolve to the Tailscale IP
```

**Note**: The `getLocalIp()` function in tunnel.js returns the first non-internal IPv4 address. If Tailscale is active, you may want to explicitly use the `tailscale ip -4` output. A future enhancement could auto-detect the Tailscale interface (`tailscale0`).

### 4. MagicDNS (Optional)

Tailscale assigns human-readable names to devices:

```
http://clankys-house:PORT
```

Enable MagicDNS in the Tailscale admin console for this to work.

## Free Tier

Tailscale's free "Personal" plan includes:
- **Up to 3 users**
- **Up to 100 devices**
- All core features (MagicDNS, HTTPS, ACLs)
- No bandwidth limits
- No time limits

This is more than enough for personal use.

## Security

- Traffic is encrypted end-to-end (WireGuard)
- The relay server is only accessible to devices on your Tailnet
- No public URLs — unlike localtunnel/cloudflared, nothing is exposed to the internet
- This is actually more secure than the tunnel approaches

## Pros/Cons Summary

**Pros:**
- Always-on — no need to start/stop tunnels per CAPTCHA
- No splash pages or interstitials
- Private and encrypted
- Reliable — no dependency on third-party tunnel services
- Fast — direct WireGuard connection
- Free for personal use

**Cons:**
- One-time setup required on each device
- Adds a background service/VPN on the phone
- Need same auth account on both devices
- If Tailscale service is down (rare), no connectivity

## Recommendation

For development/testing: use localtunnel (zero setup).
For production/daily use: set up Tailscale once and forget about tunneling forever.
