# MTA Skill

NYC MTA transit OpenClaw skill — real-time subway arrivals (GTFS-RT protobuf), bus predictions (SIRI JSON), service alerts, and route info.

## Project Structure

```
scripts/mta.mjs    — Single entry point, all commands (~1,260 lines)
proto/             — GTFS-Realtime + NYCT subway extension protobuf schemas
SKILL.md           — OpenClaw skill manifest and LLM context
```

## Stack

- Node.js ES modules (requires Node 18+)
- Single dependency: `protobufjs` for decoding GTFS-RT protobuf feeds
- No build step, no TypeScript, no framework

## Commands

12 CLI commands: `arrivals`, `bus-arrivals`, `vehicles`, `bus-vehicles`, `alerts`, `routes`, `bus-routes`, `stops`, `bus-stops`, `route-info`, `refresh-gtfs`, plus `--help`.

Run via: `node scripts/mta.mjs <command> [options]`

## Data Sources

- **Subway + alerts**: MTA GTFS-RT protobuf feeds (no auth, open access)
- **Bus**: MTA BusTime SIRI JSON API (requires free `MTA_BUS_API_KEY`)
- **Static GTFS**: Downloaded to `~/.mta/gtfs/` via `refresh-gtfs` command

## Security Conventions

- `MTA_BUS_API_KEY` loaded from env or `.env` file, never hardcoded
- All user input passed through `encodeURIComponent()` before URL construction
- `execFileSync()` with array args only — no shell string interpolation
- No `eval()`, `Function()`, `shell: true`, or dynamic `require()`
- User input used for local filtering only, never in shell commands
- GTFS static URL uses HTTP intentionally (MTA redirects HTTPS back to HTTP)

## Development

```bash
npm install          # install protobufjs
node scripts/mta.mjs --help
```

No test suite currently. When adding tests, use the existing `npm test` script entry point.
