# CLAUDE.md

## Project

OpenClaw skill that provides real-time London public transport data from the TfL Unified API. Single-file Node.js CLI with zero npm dependencies.

## Structure

- `SKILL.md` — skill manifest (YAML frontmatter) + agent prompt instructions
- `scripts/tfl.mjs` — entire implementation (all commands, embedded station data, API client)
- `README.md` — user-facing documentation
- `package.json` — npm metadata only, no dependencies

## Running

```bash
node scripts/tfl.mjs <command> [options]
# e.g. node scripts/tfl.mjs status --line northern
```

Commands: `status`, `arrivals`, `bus-arrivals`, `disruptions`, `routes`, `bus-routes`, `stops`, `route-info`, `journey`

## Key conventions

- **Zero dependencies.** Uses only Node.js builtins (`node:util`, `node:fs`, `node:path`) and native `fetch`. Do not add npm packages.
- **Single file.** All logic stays in `scripts/tfl.mjs`. Do not split into multiple modules.
- **ES modules.** `"type": "module"` in package.json, `.mjs` extension.
- **Node 18+** required (for native fetch and `parseArgs`).
- **Security:** Never interpolate user input into shell commands. Always `encodeURIComponent()` user input in API URLs. No eval, no child_process.
- **API key is optional.** `TFL_API_KEY` env var or `.env` file. Never hardcode keys.
- **Read-only.** The skill only makes GET requests to `api.tfl.gov.uk`. No writes, no side effects, no local file storage.

## Embedded data

The script contains hardcoded data for offline/fast lookup:
- 11 Tube lines + 9 other modes (DLR, Overground lines, Elizabeth, trams) with IDs, names, emojis, terminals
- 41 major stations with NaPTAN IDs and aliases
- 30+ line aliases for fuzzy matching

When adding stations, use correct NaPTAN IDs from TfL's API. Verify with: `https://api.tfl.gov.uk/StopPoint/Search/{name}`

## Tests

No test suite yet. `npm test` is a no-op.
