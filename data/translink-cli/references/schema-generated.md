# Translink Schema (Auto-generated)

Generated: 2026-02-22T21:42:51.496Z
Schema version: `ea229eefe06a0e11`

## Drift since previous snapshot

- No schema changes detected.

## PK/FK relationships

- **agency.txt**
  - PK: agency_id
  - FK: (none)
- **calendar.txt**
  - PK: service_id
  - FK: (none)
- **calendar_dates.txt**
  - PK: service_id, date
  - FK: service_id -> calendar.service_id
- **feed_info.txt**
  - PK: (none/metadata)
  - FK: (none)
- **routes.txt**
  - PK: route_id
  - FK: agency_id -> agency.agency_id
- **shapes.txt**
  - PK: shape_id, shape_pt_sequence
  - FK: (none)
- **stops.txt**
  - PK: stop_id
  - FK: parent_station -> stops.stop_id
- **stop_times.txt**
  - PK: trip_id, stop_sequence
  - FK: trip_id -> trips.trip_id; stop_id -> stops.stop_id
- **trips.txt**
  - PK: trip_id
  - FK: route_id -> routes.route_id; service_id -> calendar.service_id; shape_id -> shapes.shape_id

## agency.txt

| column | inferred_type | format | nullable | purpose | examples |
|---|---|---|---|---|---|
| agency_id | integer | int | no | Agency identifier (joined by routes.agency_id). | 10 · 11 · 12 |
| agency_name | string | text | no | Public agency name. | Mt Gravatt Coach & Travel · Transdev · Park Ridge Transit |
| agency_url | string | url | no | Agency website URL. | http://www.mtgcoach.com.au/ · https://www.transdevbrisbane.com.au/ · https://www.busqld.com.au/ |
| agency_timezone | string | text | no | Agency timezone (IANA). | Australia/Brisbane |
| agency_lang | string | text | no | Default language code. | en |
| agency_phone | string | text | yes | Agency contact phone. | 07 3808 7800 · 07 3248 6100 · 07 3802 1233 |

## calendar.txt

| column | inferred_type | format | nullable | purpose | examples |
|---|---|---|---|---|---|
| service_id | string | text | no | Service pattern identifier (joined by trips.service_id). | GCLR 25_26-39424 · GCLR 25_26-39425 · GCLR 25_26-39426 |
| monday | integer | 0|1 | no | Service runs Monday (0/1). | 0 · 1 |
| tuesday | integer | 0|1 | no | Service runs Tuesday (0/1). | 0 · 1 |
| wednesday | integer | 0|1 | no | Service runs Wednesday (0/1). | 0 · 1 |
| thursday | integer | 0|1 | no | Service runs Thursday (0/1). | 0 · 1 |
| friday | integer | 0|1 | no | Service runs Friday (0/1). | 1 · 0 |
| saturday | integer | 0|1 | no | Service runs Saturday (0/1). | 0 · 1 |
| sunday | integer | 0|1 | no | Service runs Sunday (0/1). | 0 · 1 |
| start_date | string | YYYYMMDD | no | Service start date (YYYYMMDD). | 20260227 · 20260223 · 20260221 |
| end_date | string | YYYYMMDD | no | Service end date (YYYYMMDD). | 20260417 · 20260422 · 20260418 |

## calendar_dates.txt

| column | inferred_type | format | nullable | purpose | examples |
|---|---|---|---|---|---|
| service_id | string | text | no | Service identifier. | BBL 25_26-39417 · BCC 25_26-39837 · BCC 25_26-39840 |
| date | string | YYYYMMDD | no | Exception date (YYYYMMDD). | 20260403 · 20260406 · 20260404 |
| exception_type | string | mixed | no | 1=added service, 2=removed service. | 2 · 1 |

## feed_info.txt

| column | inferred_type | format | nullable | purpose | examples |
|---|---|---|---|---|---|
| feed_publisher_name | string | text | no | Feed publisher name. | Department of Transport and Main Roads - Translink Division |
| feed_publisher_url | string | url | no | Feed publisher URL. | https://www.translink.com.au/ |
| feed_lang | string | text | no | Feed default language code. | en |
| feed_start_date | string | YYYYMMDD | no | Feed coverage start date (YYYYMMDD). | 20260221 |
| feed_end_date | string | YYYYMMDD | no | Feed coverage end date (YYYYMMDD). | 20260422 |

## routes.txt

| column | inferred_type | format | nullable | purpose | examples |
|---|---|---|---|---|---|
| route_id | string | text | no | Route identifier (joined by trips.route_id). | 19-4660 · 19-4762 · 26-4660 |
| agency_id | integer | int | no | Agency identifier (agency.agency_id). | 4 · 11 · 10 |
| route_short_name | string | text | no | Public route short name. | 19 · 26 · 29 |
| route_long_name | string | text | no | Public route long name. | Salisbury - PA Hospital StationLink · Rocklea - PA Hospital StationLink · Upper Mt Gravatt - RBWH via Fortitude Valley |
| route_desc | text | empty | yes | Route description text. | - |
| route_type | string | mixed | no | GTFS route type enum. | 3 · 2 · 4 |
| route_url | string | url | no | Route URL. | https://jp.translink.com.au/plan-your-journey/timetables/bus/T/19 · https://jp.translink.com.au/plan-your-journey/timetables/bus/T/26 · https://jp.translink.com.au/plan-your-journey/timetables/bus/T/29 |
| route_color | string | text | no | Hex route color (without #). | E463A4 · FFD51F · D20000 |
| route_text_color | string | text | no | Hex text color (without #). | 000000 · FFFFFF |

## shapes.txt

| column | inferred_type | format | nullable | purpose | examples |
|---|---|---|---|---|---|
| shape_id | integer | int | no | Shape identifier (joined by trips.shape_id). | 190011 · 190012 · 190013 |
| shape_pt_lat | float | float | no | Shape point latitude. | -27.553364 · -27.553313 · -27.553222 |
| shape_pt_lon | float | float | no | Shape point longitude. | 153.023933 · 153.023604 · 153.023007 |
| shape_pt_sequence | integer | int | no | Shape point order within shape_id. | 10001 · 10002 · 10003 |

## stop_times.txt

| column | inferred_type | format | nullable | purpose | examples |
|---|---|---|---|---|---|
| trip_id | string | text | no | Trip identifier (trips.trip_id). | 35827515-ATS_HBL 26-41689 · 35827516-ATS_HBL 26-41689 · 35827517-ATS_HBL 26-41689 |
| arrival_time | string | HH:MM:SS | no | Arrival time HH:MM:SS. | 04:56:00 · 05:00:00 · 05:04:00 |
| departure_time | string | HH:MM:SS | no | Departure time HH:MM:SS. | 04:56:00 · 05:00:00 · 05:04:00 |
| stop_id | integer | int | no | Stop identifier (stops.stop_id). | 11329 · 3246 · 320365 |
| stop_sequence | string | mixed | no | Order within trip. | 1 · 2 · 3 |
| pickup_type | integer | 0|1 | no | Pickup behavior enum. | 0 · 1 |
| drop_off_type | integer | 0|1 | no | Drop-off behavior enum. | 0 · 1 |
| timepoint | integer | 0|1 | no | Timepoint indicator enum. | 1 · 0 |

## stops.txt

| column | inferred_type | format | nullable | purpose | examples |
|---|---|---|---|---|---|
| stop_id | string | mixed | no | Stop identifier (joined by stop_times.stop_id). | 1 · 10 · 100 |
| stop_code | integer | int | no | Public stop code. | 000001 · 000010 · 000100 |
| stop_name | string | text | no | Stop public name. | Herschel Street Stop 1 near North Quay · Ann Street Stop 11 at King George Square · Margaret St stop 93 at George St |
| stop_desc | text | empty | yes | Stop description. | - |
| stop_lat | string | text | no | Stop latitude. |  -27.467834 ·  -27.468003 ·  -27.473751 |
| stop_lon | string | text | no | Stop longitude. |  153.019079 ·  153.023970 ·  153.026745 |
| zone_id | integer | 0|1 | no | Fare zone identifier. | 1 |
| stop_url | string | url | yes | Stop URL. | https://translink.com.au/stop/000001/gtfs/ · https://translink.com.au/stop/000010/gtfs/ · https://translink.com.au/stop/000100/gtfs/ |
| location_type | integer | 0|1 | no | Stop/station type enum. | 0 |
| parent_station | string | text | yes | Parent station stop_id (self join). | place_qsbs · place_inteno · place_wynsta |
| platform_code | string | text | yes | Platform code/name. | 1e · 1f · 1g |

## trips.txt

| column | inferred_type | format | nullable | purpose | examples |
|---|---|---|---|---|---|
| route_id | string | text | no | Route identifier (routes.route_id). | R348-3745 · R609-4398 · R616-4398 |
| service_id | string | text | no | Service identifier (calendar.service_id). | ATS_HBL 26-41689 · ATS_HBL 26-41691 · ATS_KBL 26-41826 |
| trip_id | string | text | no | Trip identifier (joined by stop_times.trip_id). | 35827515-ATS_HBL 26-41689 · 35827516-ATS_HBL 26-41689 · 35827517-ATS_HBL 26-41689 |
| trip_headsign | string | text | no | Trip destination/sign text. | Northgate station · Shorncliffe station · Caboolture station |
| direction_id | integer | 0|1 | no | Direction enum. | 0 · 1 |
| block_id | text | empty | yes | Block identifier. | - |
| shape_id | string | text | no | Shape identifier (shapes.shape_id). | R3480261 · R3480260 · R6090044 |
