# Translink CLI Commands

## Surfaces

- Shell: `translink_*`
- Plugin slash: `/translink_*`
- Aggregated plugin command: `/translink <command> [args...]`

## Schedule (static GTFS)

- `translink_schedule_agency`
- `translink_schedule_calendar`
- `translink_schedule_calendar_dates`
- `translink_schedule_feed_info`
- `translink_schedule_routes`
- `translink_schedule_shapes`
- `translink_schedule_stops`
- `translink_schedule_stop_times`
- `translink_schedule_trips`
- `translink_schedule_refresh`

## Realtime (GTFS-RT)

- `translink_tripupdates`
- `translink_vehiclepositions`
- `translink_alerts`

## Shared parameters (all commands)

- `--where field=value` (repeatable)
- `--contains field=text` (repeatable)
- `--in field=v1,v2,...` (repeatable)
- `--fields a,b,c`
- `--sort field`
- `--order asc|desc` (default `asc`)
- `--page N` (default `1`)
- `--per-page N` (default `20`, max `200`)
- `--format table|json|csv` (default `table`)
- `--count-only`
- `--help`

Schedule extras:
- `--refresh` force static cache refresh first
- `--schema` print current columns (+ inferred details when available)

Realtime extras:
- `--expand` add nested JSON expansion fields
- `--raw` add full raw entity JSON per row
- `--time epoch|iso` render timestamps as epoch (default) or ISO

## Strict LLM-friendly error contract

Invalid fields return structured JSON:
- `error.code`
- `error.message`
- `error.invalid`
- `error.suggestions` (fuzzy)
- `error.valid_fields`
- `error.example`

## Success response contract

List responses:
- `data: []`
- `meta.page`
- `meta.per_page`
- `meta.total`
- `meta.total_pages`
- `meta.has_next`
