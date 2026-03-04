---
name: hevy-cli
description: Interact with the Hevy fitness app via the hevy-cli command-line tool. Use when the user wants to view, create, or update workouts, routines, exercise templates, or routine folders in their Hevy account. Triggers on requests involving workout tracking, exercise history, routine management, or any Hevy-related data operations.
---

# Hevy CLI

Use the `hevy` CLI to interact with Hevy fitness app data. Requires `HEVY_API_KEY` env var to be set.

## Quick Start

```bash
# Verify access
hevy workouts count

# List recent workouts
hevy workouts list --page-size 10

# Raw JSON output for any command
hevy -j workouts list
```

## Common Tasks

### View workout history

```bash
hevy workouts list --page 1 --page-size 10
hevy workouts get <workout-id>
```

### Check exercise progress

```bash
# Find the exercise template ID first
hevy exercises list --page-size 100

# Then get history for that exercise
hevy exercises history <template-id>
hevy exercises history <template-id> --start-date 2025-01-01 --end-date 2025-02-01
```

### Create a workout

```bash
hevy workouts create \
  --title "Push Day" \
  --start-time 2025-01-15T08:00:00Z \
  --end-time 2025-01-15T09:00:00Z \
  --exercises-json '[{"exercise_template_id":"79D0BB3A","sets":[{"type":"normal","weight_kg":60,"reps":8}]}]'
```

For complex exercises, use a file: `--exercises-json @exercises.json`

### Manage routines

```bash
hevy routines list
hevy routines create --title "Upper Body" --exercises-json @routine.json
hevy routines update <routine-id> --title "Updated Name"
```

### Organize with folders

```bash
hevy folders list
hevy folders create --name "Hypertrophy Block"
```

## Key Patterns

- All list commands accept `--page` and `--page-size` for pagination.
- Use `-j` flag before the subcommand for JSON output: `hevy -j workouts list`.
- Exercise data for create/update uses `--exercises-json` accepting inline JSON or `@filepath`.
- Set types: `normal`, `warmup`, `failure`, `dropset`.
- IDs are returned in list/get responses -- use JSON mode (`-j`) to get exact IDs for subsequent commands.

## Full Command Reference

See [references/commands.md](references/commands.md) for complete command syntax, all flag options, enum values for exercise types/equipment/muscle groups, and the exercises JSON schema.
