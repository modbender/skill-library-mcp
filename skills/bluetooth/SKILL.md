---
name: Bluetooth
description: Discover, connect, and control Bluetooth devices with automatic profile learning, cross-platform tools, and device management.
---

## Core Workflow

1. **Scan** — Discover nearby devices
2. **Identify** — Match against known profiles or learn new device
3. **Connect** — Establish link with appropriate protocol
4. **Execute** — Send commands, read data, manage state
5. **Learn** — Update device profile based on interaction success/failure

---

## Quick Reference

| Need | Load |
|------|------|
| CLI commands by platform | `tools.md` |
| Device profile management | `profiles.md` |
| Security rules and warnings | `security.md` |
| Patterns by use case | `use-cases.md` |

---

## Workspace

Store device profiles and interaction history:

```
~/bluetooth/
├── profiles/         # Known device configs (one file per device)
├── history.md        # Interaction log with success/failure
└── pending.md        # Devices discovered but not profiled
```

---

## Critical Rules

1. **Never auto-connect** to unknown devices — require explicit user confirmation
2. **Whitelist first** — only interact with pre-authorized devices
3. **Log everything** — every connection attempt, command, result
4. **Fail gracefully** — if device unreachable, retry with backoff, then report
5. **Profile learning** — when something works, save it; when it fails, note why

---

## Platform Detection

| OS | Primary Tool | Fallback |
|----|--------------|----------|
| Linux | `bluetoothctl` | `hcitool`, `gatttool` |
| macOS | `blueutil` | `system_profiler`, CoreBluetooth |
| Windows | WinRT/PowerShell | `pnputil` for enumeration |
| Cross-platform | Bleak (Python) | Noble (Node.js) |

---

## Device Interaction Pattern

```
1. Check ~/bluetooth/profiles/ for device
2. If known → load profile, use saved commands
3. If unknown → scan characteristics, discover capabilities
4. Execute requested action
5. Verify result (read state, check acknowledgment)
6. Update profile: what worked, what failed, timing
```
