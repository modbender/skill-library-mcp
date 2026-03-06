# Inspected Upstream Skills

Directly inspected from ClawHub:

- `shell-scripting` latest `1.0.0`
- `curl-http` latest `1.0.0`
- `wireguard` latest `1.0.0`
- `tailscale` latest `1.0.0`
- `dns` latest `1.0.0`
- `ipinfo` latest `1.0.0`
- `moltguard` latest `6.0.2`

## Relevant Capability Notes

- `shell-scripting` provides robust shell orchestration patterns (retries, error handling, cleanup).
- `curl-http` provides HTTP/IP verification primitives for before/after tunnel checks.
- `wireguard` focuses on tunnel correctness caveats (AllowedIPs, DNS, handshake/routing pitfalls).
- `tailscale` provides exit-node, diagnostics, and status workflows for overlay-network routing.
- `dns` provides DNS safety/debugging patterns useful for leak-risk interpretation.
- `ipinfo` provides IP geolocation verification; token is optional.
- `moltguard` is prompt/tool security (sanitization + injection detection), not a network tunnel engine.

## Scope Clarification

- Tunnel control is executed through local VPN/WireGuard/Tailscale CLI paths.
- DNS and geo checks are verification layers, not standalone bypass mechanisms.
- MoltGuard is a security guardrail for content/tool handling during the workflow.
