# Column Meanings + Data Format (Current Static Feed)

This maps the currently-present columns to GTFS meaning and expected format.

## agency.txt

| Column | Format | Meaning |
|---|---|---|
| `agency_id` | integer/string id | Unique agency key; joins with `routes.agency_id`. |
| `agency_name` | text | Public agency name. |
| `agency_url` | URL | Agency website. |
| `agency_timezone` | IANA tz string | Timezone for agency times. |
| `agency_lang` | BCP-47/lang code | Default language for text fields. |
| `agency_phone` | text | Customer contact phone. |

## calendar.txt

| Column | Format | Meaning |
|---|---|---|
| `service_id` | string id | Service pattern key; joins with `trips.service_id`. |
| `monday`..`sunday` | 0/1 integer | Whether service normally runs on that weekday. |
| `start_date` | YYYYMMDD | First date this weekly pattern is active. |
| `end_date` | YYYYMMDD | Last date this weekly pattern is active. |

## calendar_dates.txt

| Column | Format | Meaning |
|---|---|---|
| `service_id` | string id | Service key affected by exception. |
| `date` | YYYYMMDD | Exception date. |
| `exception_type` | enum int | `1` add service, `2` remove service. |

## feed_info.txt

| Column | Format | Meaning |
|---|---|---|
| `feed_publisher_name` | text | Feed publisher name. |
| `feed_publisher_url` | URL | Feed publisher URL. |
| `feed_lang` | lang code | Default language for feed text. |
| `feed_start_date` | YYYYMMDD | Earliest date covered by this feed. |
| `feed_end_date` | YYYYMMDD | Latest date covered by this feed. |

## routes.txt

| Column | Format | Meaning |
|---|---|---|
| `route_id` | string id | Unique route key; joins to `trips.route_id`. |
| `agency_id` | id | Owning agency (`agency.agency_id`). |
| `route_short_name` | text/number | Public short route label/number. |
| `route_long_name` | text | Public long route name/description line. |
| `route_desc` | text | Optional route description text. |
| `route_type` | enum int | GTFS mode (e.g., bus/tram/train/ferry). |
| `route_url` | URL | Route info page. |
| `route_color` | RRGGBB | Route branding color (hex, no #). |
| `route_text_color` | RRGGBB | Preferred text color on route color. |

## shapes.txt

| Column | Format | Meaning |
|---|---|---|
| `shape_id` | id | Shape key referenced by `trips.shape_id`. |
| `shape_pt_lat` | float | Point latitude. |
| `shape_pt_lon` | float | Point longitude. |
| `shape_pt_sequence` | integer | Point order along the polyline. |

## stop_times.txt

| Column | Format | Meaning |
|---|---|---|
| `trip_id` | id | Trip key (`trips.trip_id`). |
| `arrival_time` | HH:MM:SS | Scheduled arrival at stop. |
| `departure_time` | HH:MM:SS | Scheduled departure from stop. |
| `stop_id` | id | Stop key (`stops.stop_id`). |
| `stop_sequence` | integer | Sequence of stop within trip. |
| `pickup_type` | enum int | Pickup policy at stop (regular/no pickup/etc.). |
| `drop_off_type` | enum int | Drop-off policy at stop. |
| `timepoint` | enum int | Whether time is exact timepoint vs approximate. |

## stops.txt

| Column | Format | Meaning |
|---|---|---|
| `stop_id` | id | Unique stop/platform/station key. |
| `stop_code` | text | Rider-facing short stop code. |
| `stop_name` | text | Public stop/station name. |
| `stop_desc` | text | Optional extra stop description. |
| `stop_lat` | float | Latitude. |
| `stop_lon` | float | Longitude. |
| `zone_id` | id | Fare/zone identifier. |
| `stop_url` | URL | Stop information page. |
| `location_type` | enum int | Stop/station type (platform/station/etc.). |
| `parent_station` | id | Parent station for child stops/platforms. |
| `platform_code` | text | Platform/bay code shown to riders. |

## trips.txt

| Column | Format | Meaning |
|---|---|---|
| `route_id` | id | Route key (`routes.route_id`). |
| `service_id` | id | Service pattern (`calendar.service_id`). |
| `trip_id` | id | Unique trip key; joins to `stop_times.trip_id`. |
| `trip_headsign` | text | Rider-facing destination/headsign. |
| `direction_id` | 0/1 int | Direction variant (agency-defined semantics). |
| `block_id` | id | Vehicle block/interlining key. |
| `shape_id` | id | Shape key (`shapes.shape_id`). |
