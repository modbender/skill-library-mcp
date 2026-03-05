# Network Security Checks

## What to Examine

Network-related settings from config.

## Check 1: Gateway Binding

**Location**: `gateway.bind`

| Value | Risk Level | Notes |
|-------|------------|-------|
| `localhost` / `127.0.0.1` | 🟢 Low | Local only |
| `lan` | 🟡 Medium | LAN accessible |
| `0.0.0.0` | 🟠 High | All interfaces |
| (specific IP) | Varies | Check if public |

**If binding to non-localhost**:
- Check authentication is enabled
- Check if behind firewall/VPN

## Check 2: Gateway Authentication

**Location**: `gateway.auth`

| Mode | Risk Level | Notes |
|------|------------|-------|
| `token` | 🟢 Good | Requires token |
| `password` | 🟢 Good | Requires password |
| `none` / disabled | 🔴 Critical | No auth |

**Weak token check** (entropy-based):
- Token is common word/phrase: 🔴 Critical
- Token < 16 chars with low entropy: 🟠 High
- Token 16-24 chars with high entropy: 🟢 OK
- Token 24+ chars: 🟢 OK regardless

**Note**: A high-entropy 24-char token is fine. Don't flag based on length alone.

## Check 3: Control UI Security

**Location**: `gateway.controlUi`

| Setting | Risk |
|---------|------|
| `allowInsecureAuth: true` | 🟡 Medium - No device pairing |
| `dangerouslyDisableDeviceAuth: true` | 🔴 Critical |
| Missing `allowedOrigins` | 🟡 Medium |

**HTTPS check**:
- Control UI over HTTP (not localhost): 🟠 High
- Token visible in URL parameters: 🟡 Medium

## Check 4: Tailscale Configuration

**Location**: `gateway.tailscale`

| Mode | Notes |
|------|-------|
| `off` | Not using Tailscale |
| `serve` | Tailscale serving (good for security) |
| `funnel` | Public exposure via Tailscale |

**If funnel enabled**:
- Bot accessible from internet
- Verify authentication is strong
- 🟠 High if combined with powerful tools

## Check 5: Trusted Proxies

**Location**: `gateway.trustedProxies`

**If behind reverse proxy**:
- Should list proxy IPs
- Missing config = IP spoofing possible

**No trustedProxies + reverse proxy detected**: 🟡 Medium

## Check 6: Plugin Network Access

**Location**: `plugins.entries`

Some plugins may open additional network surfaces:
- `voice-call`: Opens telephony connection
- Custom plugins: Check their network usage

## Context-Aware Assessment

### VPN/Private Network Verification

Don't just trust user claims. Do a quick check:

```bash
# Check for VPN interfaces
ip link | grep -E "wg[0-9]|tailscale|tun[0-9]"

# Check if Tailscale is active
tailscale status 2>/dev/null | head -1

# Check for WireGuard
wg show 2>/dev/null | head -1
```

**If VPN detected**:
- Reduce severity of LAN binding warnings
- Network exposure less critical

**If no VPN but user claims private network**:
- Note the discrepancy
- Still reduce severity but mention assumption

**Always check regardless of VPN**:
- Authentication enabled
- Control UI security
- Token strength (entropy-based, not length-based)

### User claims single-user personal use:

**Reduce concern for**:
- Session isolation (only one user)
- DM scope settings

**Still important**:
- Auth tokens
- Tool permissions (self-protection)

## Quick Network Audit Commands

Suggest user run (if they want to verify):

```bash
# Check what's listening
ss -tlnp | grep -E "(18789|openclaw)"

# Check firewall status
sudo ufw status

# Check if port is accessible externally
# (only if user consents to external check)
```

## Recommendations by Risk

| Finding | Recommendation |
|---------|----------------|
| No auth + LAN bind | Enable token or password auth immediately |
| Public exposure | Use Tailscale Serve instead of direct exposure |
| Weak token | Generate new token: `openclaw gateway token --rotate` |
| Control UI insecure | Switch to HTTPS or Tailscale |
