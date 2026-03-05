# Security Model

## Why System Commands Exist

openclaw-whisperer is a diagnostic and repair tool for OpenClaw installations. Some fixes require system-level operations (restarting services, killing stuck processes, fixing file permissions, managing Docker containers).

## Safety Controls

### Command Execution
- All commands use `subprocess.run()` with **list arguments** (no `shell=True`)
- Command strings are split via `shlex.split()` for safe argument parsing
- No string interpolation into shell commands

### Fix Recipe Safety Levels
Each recipe in `data/fix-recipes.json` has a `safe_auto` flag:

| `safe_auto` | Behavior | Examples |
|-------------|----------|----------|
| `true` | Can run without user confirmation | Info messages, config reads, version checks |
| `false` | **Requires explicit user confirmation** | kill, chmod, systemctl, docker rm, config reset |

All recipes involving destructive or privileged operations (`kill -9`, `systemctl`, `chmod` on credentials, `docker rm`, config resets) are marked `safe_auto: false`.

### No Exfiltration
- No network calls to external services
- No data collection or telemetry
- All operations are local to the user's machine
- No prompt injection vectors in recipe data

## Flagged Patterns Explained

| Pattern | Context | Risk |
|---------|---------|------|
| `kill -9` | Terminate stuck gateway process | Guarded by `safe_auto: false` |
| `systemctl start docker` | Start Docker daemon | Guarded by `safe_auto: false` |
| `chmod 700/600` | Secure credentials directory | Guarded by `safe_auto: false` |
| `docker rm` | Reset sandbox container | Guarded by `safe_auto: false` |
| `docker system prune` | Cleanup unused resources | Guarded by `safe_auto: false` |

## Reporting Issues

If you discover a security concern, open an issue at:
https://github.com/PhenixStar/openclaw-skills-collection/issues
