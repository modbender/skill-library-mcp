# GTFS Relationships (Current Files)

## Primary keys (practical)

- `agency.txt`: `agency_id`
- `routes.txt`: `route_id`
- `trips.txt`: `trip_id`
- `stops.txt`: `stop_id`
- `shapes.txt`: composite (`shape_id`, `shape_pt_sequence`)
- `stop_times.txt`: composite (`trip_id`, `stop_sequence`)
- `calendar.txt`: `service_id`
- `calendar_dates.txt`: composite (`service_id`, `date`)
- `feed_info.txt`: single-row metadata (no PK required)

## Foreign keys

- `routes.agency_id` -> `agency.agency_id`
- `trips.route_id` -> `routes.route_id`
- `trips.service_id` -> `calendar.service_id` (and `calendar_dates.service_id`)
- `trips.shape_id` -> `shapes.shape_id`
- `stop_times.trip_id` -> `trips.trip_id`
- `stop_times.stop_id` -> `stops.stop_id`

## Common joins

1. Service pattern for a route:
   - `routes` -> `trips` -> `stop_times` -> `stops`
2. Day-of-operation filter:
   - `trips.service_id` with `calendar` + `calendar_dates`
3. Shape path for a trip:
   - `trips.shape_id` -> `shapes.shape_id`
