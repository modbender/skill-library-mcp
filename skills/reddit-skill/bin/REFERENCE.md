# ThreadPilot Binary Reference

This repository does not store `threadpilot` executables.

Runtime binaries are sourced from:

- Repository: `https://github.com/vood/threadpilot`
- Releases: `https://github.com/vood/threadpilot/releases`
- Download pattern:
  - `https://github.com/vood/threadpilot/releases/download/<version>/threadpilot-<os>-<arch>`

Defaults used by `scripts/threadpilot`:

- `THREADPILOT_VERSION=v0.1.0`
- `THREADPILOT_RELEASE_BASE_URL=https://github.com/vood/threadpilot/releases/download`

Override example:

```bash
THREADPILOT_VERSION=v0.1.0 scripts/threadpilot install
```
