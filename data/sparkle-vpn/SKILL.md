---
name: sparkle-vpn
description: Control Sparkle VPN - start, stop, manage system proxy, query status and switch nodes using Mihomo core directly.
---

# Sparkle VPN Control

This skill provides tools to control the Sparkle VPN using Mihomo core directly (no GUI interaction needed).

## Tools

### VPN Control
- `sparkle_vpn_start` - Start VPN core only (port 7890 available, no system proxy)
- `sparkle_vpn_start_with_proxy` - Start VPN and enable system-wide proxy
- `sparkle_vpn_stop` - Stop VPN and disable system proxy

### System Proxy Management
- `sparkle_vpn_enable_proxy` - Enable system-wide proxy settings (VPN must be running)
- `sparkle_vpn_disable_proxy` - Disable system-wide proxy settings

### Node Management
- `sparkle_vpn_status` - Query current VPN status, active node and available nodes list
- `sparkle_vpn_switch` - Switch to a different VPN node

## Implementation

Uses Mihomo core directly:
- Profile: `~/.config/sparkle/profiles/19c48c94cbb.yaml`
- Proxy port: `7890` (HTTP/HTTPS)
- Config dir: `~/.config/sparkle/`
- API port: `9090`

## Usage Examples

Start VPN with system proxy:
```bash
sparkle_vpn_start_with_proxy
```

Start VPN without system proxy (manual mode):
```bash
sparkle_vpn_start
```

Enable system proxy (after VPN is running):
```bash
sparkle_vpn_enable_proxy
```

Stop VPN:
```bash
sparkle_vpn_stop
```

Query status:
```bash
sparkle_vpn_status
```

Switch node:
```bash
sparkle_vpn_switch "香港-HKG-01-VL"
```

## Common Nodes

- `自动选择` - Auto select best node
- `故障转移` - Fallback mode
- `香港-HKG-01-VL` - Hong Kong node
- `香港-HKG-02-VL` - Hong Kong node 2
- `香港-HKT-01-VL` - Hong Kong HKT
- `新加坡-SIN-01-VL` - Singapore node
- `日本-TYO-01-VL` - Japan Tokyo node
- `美国-SJC-01-VL` - US San Jose node

## System Proxy Support

System proxy settings are applied via:
- GNOME gsettings (for GNOME/GTK desktops)
- Environment variables saved to `~/.config/sparkle/proxy.env`

To use proxy in current terminal session:
```bash
source ~/.config/sparkle/proxy.env
```
