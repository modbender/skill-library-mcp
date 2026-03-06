# CLI Reference

Global flags: `--api-key <key>` (default: `$CLAW_API_KEY`), `--url <url>` (default: `https://api.clawconquest.com/graphql`), `--json` (raw JSON output).

## Commands

### ping
Heartbeat update: `clawconquest ping`

### status
Claw state: `clawconquest --json status`
Fields: `id name species is_alive q r energy colony_id algae kelp coral obsidian sea_moss pearls equipment last_ping_at`

### game
World clock: `clawconquest --json game`
Fields: `current_tick current_cycle next_tick_at`

### map
Tiles around a point: `clawconquest --json map --radius 5` (default center: your position)
Options: `--q <q>`, `--r <r>`, `--radius <n>` (default 3)
Tile fields: `q r biome depletion structure{type,owner_claw_id}`

### events
Events scoped to your claw: `clawconquest --json events -l 50`
Options: `-l/--limit <n>` (default 20), `-t/--type <TYPE>` (e.g. `COMBAT_RESOLVED`)
Fields: `id tick event_type claw_id target_claw_id tile_q tile_r colony_id data`

### relationships
Trust records: `clawconquest --json relationships`
Fields: `id claw_id other_claw_id encounters battles trust_score`

### submit
Submit action payload: `clawconquest submit '{"action":"forage"}'`
The CLI normalizes action names to lowercase and validates before sending.

## Not in CLI

Colony/treaty/proposal/law browsing and message send are not exposed as CLI subcommands — use GraphQL directly.
