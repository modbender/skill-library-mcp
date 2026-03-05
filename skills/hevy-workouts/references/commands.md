# Hevy CLI Command Reference

## Authentication

The API key must be available as `HEVY_API_KEY` env var or passed via `--api-key`.

```bash
export HEVY_API_KEY=<key>
```

## Global Flags

| Flag | Description |
|------|-------------|
| `--api-key TEXT` | Hevy API key (overrides env var) |
| `-j` / `--json-output` | Raw JSON output instead of tables |

## Workouts

```bash
hevy workouts list [--page N] [--page-size 1-10]
hevy workouts get <workout-id>
hevy workouts count
hevy workouts events [--page N] [--page-size 1-10] [--since ISO-8601]
hevy workouts create --title TEXT --start-time ISO --end-time ISO [--description TEXT] [--is-private] [--exercises-json JSON|@FILE]
hevy workouts update <workout-id> [--title TEXT] [--description TEXT] [--start-time ISO] [--end-time ISO] [--is-private BOOL] [--exercises-json JSON|@FILE]
```

## Routines

```bash
hevy routines list [--page N] [--page-size 1-10]
hevy routines get <routine-id>
hevy routines create --title TEXT [--folder-id INT] [--notes TEXT] [--exercises-json JSON|@FILE]
hevy routines update <routine-id> [--title TEXT] [--notes TEXT] [--exercises-json JSON|@FILE]
```

## Exercise Templates

```bash
hevy exercises list [--page N] [--page-size 1-100]
hevy exercises get <template-id>
hevy exercises history <template-id> [--start-date ISO] [--end-date ISO]
hevy exercises create --title TEXT --exercise-type TYPE --equipment EQUIP --muscle-group GROUP [--other-muscles GROUP ...]
```

### Exercise type values
`weight_reps`, `reps_only`, `bodyweight_reps`, `bodyweight_assisted_reps`, `duration`, `weight_duration`, `distance_duration`, `short_distance_weight`

### Equipment values
`none`, `barbell`, `dumbbell`, `kettlebell`, `machine`, `plate`, `resistance_band`, `suspension`, `other`

### Muscle group values
`abdominals`, `shoulders`, `biceps`, `triceps`, `forearms`, `quadriceps`, `hamstrings`, `calves`, `glutes`, `abductors`, `adductors`, `lats`, `upper_back`, `traps`, `lower_back`, `chest`, `cardio`, `neck`, `full_body`, `other`

## Routine Folders

```bash
hevy folders list [--page N] [--page-size 1-10]
hevy folders get <folder-id>
hevy folders create --name TEXT
```

## Exercises JSON Format

For `--exercises-json`, pass inline JSON or `@filepath`. Each exercise object:

```json
{
  "exercise_template_id": "79D0BB3A",
  "notes": "optional",
  "superset_id": null,
  "sets": [
    {
      "type": "normal",
      "weight_kg": 60,
      "reps": 8,
      "distance_meters": 0,
      "duration_seconds": 0,
      "rpe": null
    }
  ]
}
```

### Set types
`normal`, `warmup`, `failure`, `dropset`
