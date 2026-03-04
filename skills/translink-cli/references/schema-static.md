# Translink GTFS Static Schema (Current Feed)

## agency.txt

| Column | Observed type | Notes |
|---|---|---|
| `agency_id` | `integer` | |
| `agency_name` | `string` | |
| `agency_url` | `url` | |
| `agency_timezone` | `string` | |
| `agency_lang` | `string` | |
| `agency_phone` | `string` | |

## calendar.txt

| Column | Observed type | Notes |
|---|---|---|
| `service_id` | `string` | |
| `monday` | `integer` | |
| `tuesday` | `integer` | |
| `wednesday` | `integer` | |
| `thursday` | `integer` | |
| `friday` | `integer` | |
| `saturday` | `integer` | |
| `sunday` | `integer` | |
| `start_date` | `date_yyyymmdd` | |
| `end_date` | `date_yyyymmdd` | |

## calendar_dates.txt

| Column | Observed type | Notes |
|---|---|---|
| `service_id` | `string` | |
| `date` | `date_yyyymmdd` | |
| `exception_type` | `integer` | |

## feed_info.txt

| Column | Observed type | Notes |
|---|---|---|
| `feed_publisher_name` | `string` | |
| `feed_publisher_url` | `url` | |
| `feed_lang` | `string` | |
| `feed_start_date` | `date_yyyymmdd` | |
| `feed_end_date` | `date_yyyymmdd` | |

## routes.txt

| Column | Observed type | Notes |
|---|---|---|
| `route_id` | `string` | |
| `agency_id` | `integer` | |
| `route_short_name` | `integer` | |
| `route_long_name` | `string` | |
| `route_desc` | `string` | |
| `route_type` | `integer` | |
| `route_url` | `url` | |
| `route_color` | `color_hex` | |
| `route_text_color` | `color_hex` | |

## shapes.txt

| Column | Observed type | Notes |
|---|---|---|
| `shape_id` | `integer` | |
| `shape_pt_lat` | `float` | |
| `shape_pt_lon` | `float` | |
| `shape_pt_sequence` | `integer` | |

## stop_times.txt

| Column | Observed type | Notes |
|---|---|---|
| `trip_id` | `string` | |
| `arrival_time` | `time_hhmmss` | |
| `departure_time` | `time_hhmmss` | |
| `stop_id` | `integer` | |
| `stop_sequence` | `integer` | |
| `pickup_type` | `integer` | |
| `drop_off_type` | `integer` | |
| `timepoint` | `integer` | |

## stops.txt

| Column | Observed type | Notes |
|---|---|---|
| `stop_id` | `integer` | |
| `stop_code` | `integer` | |
| `stop_name` | `string` | |
| `stop_desc` | `string` | |
| `stop_lat` | `float` | |
| `stop_lon` | `float` | |
| `zone_id` | `integer` | |
| `stop_url` | `url` | |
| `location_type` | `integer` | |
| `parent_station` | `string` | |
| `platform_code` | `string` | |

## trips.txt

| Column | Observed type | Notes |
|---|---|---|
| `route_id` | `string` | |
| `service_id` | `string` | |
| `trip_id` | `string` | |
| `trip_headsign` | `string` | |
| `direction_id` | `integer` | |
| `block_id` | `string` | |
| `shape_id` | `string` | |
