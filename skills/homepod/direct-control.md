# HomePod Direct Control Runbook

Use this runbook when the user asks for active device control, not only diagnostics.

## Control Preconditions

- Confirm the user explicitly wants command execution.
- Confirm `atvremote` is available on PATH before issuing control commands.
- Confirm one unambiguous target (`name`, `ip`, or `id`) before mutating playback state.

## Connection Flow

1. Discover reachable devices:
```bash
atvremote scan
```

2. Select one canonical target:
```bash
atvremote -n "Kitchen HomePod" device_info
```

3. Validate current state before changes:
```bash
atvremote -n "Kitchen HomePod" playing
atvremote -n "Kitchen HomePod" volume
```

## Safe Command Ladder

Run commands from top to bottom and stop as soon as the user goal is met.

| Step | Command | Type | Purpose |
|------|---------|------|---------|
| 1 | `atvremote -n "<target>" playing` | Read-only | Verify current media state |
| 2 | `atvremote -n "<target>" play_pause` | Mutating | Toggle playback quickly |
| 3 | `atvremote -n "<target>" set_volume=<0-100>` | Mutating | Set exact output level |
| 4 | `atvremote -n "<target>" next` | Mutating | Advance to next track |
| 5 | `atvremote -n "<target>" stop` | Mutating | End active playback session |

## Stream Injection

Only run with explicit user confirmation of URL or local file source.

```bash
atvremote -n "<target>" play_url="https://example.com/audio.mp3"
atvremote -n "<target>" stream_file="/absolute/path/to/file.mp3"
```

## Pairing and Auth Notes

- Some devices work with `Pairing: NotNeeded`.
- If pairing is required:
```bash
atvremote -n "<target>" pair
```
- Never store pairing secrets in skill memory.

## Failure Handling

| Symptom | First Action | Next Action |
|---------|--------------|-------------|
| Command times out | Re-run `scan` and verify same subnet | Retry with `-s <ip>` |
| Target not found | Confirm exact device name in scan output | Use `-i <identifier>` |
| Playback command returns no change | Check `playing` and current app state | Reproduce with `play_pause` |
| Volume command ignored | Verify target is active output device | Re-validate on device and retry |

## Guardrails

- Never run wildcard or broad-scoped commands.
- Never issue `stop` or volume changes across multiple targets in one step.
- Capture pre and post command state for reproducibility in `automation-log.md`.
