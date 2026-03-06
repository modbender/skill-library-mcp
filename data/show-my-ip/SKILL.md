---
name: show-my-ip
description: Show the current public IP address of the server. Use when asked about IP, public IP, or network identity.
---

# Show My IP

Quickly check the public IP address of the machine running your agent. Useful for debugging network issues, verifying VPN connections, confirming server identity, or setting up firewall rules.

## Usage

```bash
bash scripts/get-ip.sh
```

## Output

Returns the public **IPv4** address (and **IPv6** if available) by querying `ifconfig.me`.

Example output:
```
=== Public IP ===
IPv4: 203.0.113.42
IPv6: 2001:db8::1
```

## When to Use

- User asks "what's my IP?" or "show my public IP"
- Verifying outbound IP for allowlisting
- Checking if a VPN or proxy is active
- Confirming server network identity

## Requirements

- `curl` (pre-installed on most systems)
- Internet access
