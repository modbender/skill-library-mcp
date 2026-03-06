# Translink GTFS schema (current feed)

Source: `~/.openclaw/cache/translink/current/*.txt`

Only columns currently present in feed are documented below.

## Data format rules

- IDs (`*_id`) are opaque strings; compare as exact text.
- Dates in static GTFS are `YYYYMMDD`.
- Times in `stop_times` are `HH:MM:SS` (may exceed 24h in GTFS generally).
- Lat/lon are decimal degrees.
- Enums are often numeric strings in CSV.

---

## agency.txt
Columns:
- `agency_id` (string, PK-ish in feed)
- `agency_name` (text)
- `agency_url` (URL)
- `agency_timezone` (IANA tz)
- `agency_lang` (language code)
- `agency_phone` (text)

Keys:
- PK: `agency_id` (feed-level unique expected)
- FK target from `routes.agency_id`

## calendar.txt
Columns:
- `service_id` (string)
- `monday`..`sunday` (`0|1`)
- `start_date` (`YYYYMMDD`)
- `end_date` (`YYYYMMDD`)

Keys:
- PK: `service_id`
- FK target from `trips.service_id`

## calendar_dates.txt
Columns:
- `service_id` (string)
- `date` (`YYYYMMDD`)
- `exception_type` (`1`=added service, `2`=removed service)

Keys:
- Composite key (practical): `service_id + date`
- FK: `service_id -> calendar.service_id` (or standalone service when calendar omitted)

## feed_info.txt
Columns:
- `feed_publisher_name` (text)
- `feed_publisher_url` (URL)
- `feed_lang` (language code)
- `feed_start_date` (`YYYYMMDD`)
- `feed_end_date` (`YYYYMMDD`)

Keys:
- Usually one-row metadata table.

## routes.txt
Columns:
- `route_id` (string)
- `agency_id` (string)
- `route_short_name` (text)
- `route_long_name` (text)
- `route_desc` (text)
- `route_type` (GTFS route type enum)
- `route_url` (URL)
- `route_color` (hex without `#`)
- `route_text_color` (hex without `#`)

Keys:
- PK: `route_id`
- FK: `agency_id -> agency.agency_id`
- FK target from `trips.route_id`

## shapes.txt
Columns:
- `shape_id` (string)
- `shape_pt_lat` (float)
- `shape_pt_lon` (float)
- `shape_pt_sequence` (int, ordering)

Keys:
- Composite key: `shape_id + shape_pt_sequence`
- FK target from `trips.shape_id`

## stops.txt
Columns:
- `stop_id` (string)
- `stop_code` (text)
- `stop_name` (text)
- `stop_desc` (text)
- `stop_lat` (float)
- `stop_lon` (float)
- `zone_id` (string)
- `stop_url` (URL)
- `location_type` (enum, e.g. stop/station)
- `parent_station` (string stop_id)
- `platform_code` (text)

Keys:
- PK: `stop_id`
- Self-FK: `parent_station -> stops.stop_id`
- FK target from `stop_times.stop_id`

## stop_times.txt
Columns:
- `trip_id` (string)
- `arrival_time` (`HH:MM:SS`)
- `departure_time` (`HH:MM:SS`)
- `stop_id` (string)
- `stop_sequence` (int)
- `pickup_type` (enum)
- `drop_off_type` (enum)
- `timepoint` (enum)

Keys:
- Composite key: `trip_id + stop_sequence`
- FK: `trip_id -> trips.trip_id`
- FK: `stop_id -> stops.stop_id`

## trips.txt
Columns:
- `route_id` (string)
- `service_id` (string)
- `trip_id` (string)
- `trip_headsign` (text)
- `direction_id` (enum)
- `block_id` (string)
- `shape_id` (string)

Keys:
- PK: `trip_id`
- FK: `route_id -> routes.route_id`
- FK: `service_id -> calendar.service_id`
- FK: `shape_id -> shapes.shape_id`

---

## Core join map (PK/FK)

- `routes.route_id = trips.route_id`
- `trips.trip_id = stop_times.trip_id`
- `stops.stop_id = stop_times.stop_id`
- `trips.service_id = calendar.service_id`
- `calendar.service_id = calendar_dates.service_id`
- `trips.shape_id = shapes.shape_id`
- `routes.agency_id = agency.agency_id`
- `stops.parent_station = stops.stop_id` (self join)

## Realtime normalized output fields

### translink_tripupdates
- `entity_id`, `trip_id`, `route_id`, `start_time`, `start_date`, `schedule_relationship`, `vehicle_id`, `vehicle_label`, `stop_time_updates_count`, `timestamp`

### translink_vehiclepositions
- `entity_id`, `vehicle_id`, `vehicle_label`, `trip_id`, `route_id`, `current_stop_sequence`, `stop_id`, `current_status`, `timestamp`, `latitude`, `longitude`, `bearing`, `speed`, `occupancy_status`

### translink_alerts
- `entity_id`, `informed_entities_count`, `active_period_start`, `active_period_end`, `cause`, `effect`, `severity_level`, `header`, `description`, `url`
