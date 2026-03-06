# Translink CLI usage

## Static schedule examples

```bash
translink_schedule_routes --page 1 --per-page 20
translink_schedule_stops --where stop_id=120002 --fields stop_id,stop_name,stop_lat,stop_lon
translink_schedule_stops --where stop_id=010824 --fields stop_id,stop_name,stop_lat,stop_lon
translink_schedule_routes --contains route_long_name=stationlink --page 1 --per-page 10
translink_schedule_routes --where route_short_name=M1 --fields route_id,route_short_name,route_long_name
translink_schedule_trips --in direction_id=0,1 --sort trip_id --order asc --page 1 --per-page 10
translink_schedule_routes --schema
```

## Realtime examples

```bash
translink_tripupdates --page 1 --per-page 10 --time iso
translink_tripupdates --expand --fields entity_id,trip_id,route_id,timestamp,stop_time_updates_json --page 1 --per-page 5 --format json
translink_vehiclepositions --raw --fields entity_id,vehicle_id,raw_json --page 1 --per-page 3 --format json
translink_alerts --contains header=closure --expand --time iso --page 1 --per-page 10
```

## Plugin slash command examples

```text
/translink_schedule_routes --page 1 --per-page 5
/translink translink_tripupdates --page 1 --per-page 3 --time iso
```

## Refresh + schema drift

```bash
translink_schedule_refresh
```

Returns:
- `schema_version`
- `drift[]` (added/removed/type changes)
- generated schema-doc locations

## Invalid field recovery

```bash
translink_schedule_routes --where routeid=19
```

Returns `INVALID_FIELD` with fuzzy suggestions (e.g., `route_id`).
