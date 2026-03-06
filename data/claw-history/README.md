# claw-history

`claw-history` provides a chronological history of the agent’s actions from earliest available records (“birth marker”) to now.

## Beginner quick start

Just tell your OpenClaw to install this skill and run it.

## Important: Data quality for full-lifetime history

The skill works **without** extra hooks, but timeline completeness is much better when these hooks are enabled:

- **`session-memory`** (recommended): saves session context on `/new` into `workspace/memory/...`
- **`command-logger`** (strongly recommended): writes command events to `~/.openclaw/logs/commands.log`
- **`boot-md`** (optional): startup automation; not required for timeline reconstruction

## Enable recommended hooks

```bash
openclaw hooks enable session-memory
openclaw hooks enable command-logger
```

## Verify

```bash
openclaw hooks info session-memory
openclaw hooks info command-logger
```

## Notes

- `command-logger` is **not mandatory** for `claw-history`, but is useful for auditable command-level history.
- If source coverage is incomplete (missing old logs, disabled hooks, inaccessible sessions), `claw-history` reports gaps explicitly.

## Credits

- **Author:** C1 (OpenClaw) 🛠️
- **Project direction & validation:** B3 (BlueBirdBack)

## Build metadata

- **Initial packaging model:** `gpt-5.3-codex`
- **Model note:** model/runtime is environment-dependent and may change across releases.

## Contact

- Please use GitHub Issues on this repository for feedback and requests.
