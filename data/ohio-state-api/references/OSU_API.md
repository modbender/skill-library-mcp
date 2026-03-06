# OSU Contents API Reference 

It is not an official documentation.

## Athletics

Base URL: `https://content.osu.edu/v3/athletics`

- `GET /all`  
  Returns athletics programs and schedules.

## Buildings

Base URL: `https://content.osu.edu/v2/api/buildings`

- `GET /`  
  Returns building data including addresses, departments, and room metadata.

## Bus Transportation

Base URL: `https://content.osu.edu/v2/bus`

- `GET /routes/`  
  Returns all bus routes/lines.
- `GET /routes/{route_code}`  
  Returns stop and route details for a specific line.
- `GET /routes/{route_code}/vehicles`  
  Returns real-time vehicle locations for a specific line.

## Academic Calendar & Holidays

Base URL: `https://content.osu.edu/v2/calendar`

- `GET /academic`  
  Returns academic calendar events.
- `GET /holidays`  
  Returns university holidays.

## Classes

Base URL: `https://content.osu.edu/v2/classes`

- `GET /search`  
  Query parameters:
  - `q` (required): search string
  - `p`: page number (default 1)
  - `term`: term code (e.g. 1162, 1164, 1168)
  - `campus`: campus code (e.g. COL, LMA, MAN, MRN, NWK)
  - `subject`: subject code (e.g. CSE, MATH, ENGR)
  - `academic-career`: UGRD, GRAD, DENT, LAW, MED, VET
  - `academic-program`: program code (e.g. ENG, ASC, AGR)
  - `component`: LEC, LAB, REC, SEM, IND, CLN, FLD
  - `catalog-number`: catalog number range (e.g. 1xxx, 2xxx)
  - `instruction-mode`: P, DL, BL

## Directory & People Search

Base URL: `https://content.osu.edu`

- `GET /v3/managed-json/universityDirectory`  
  Returns the university directory data set.
- `GET /v2/people/search?firstname={firstname}&lastname={lastname}`  
  Returns people search results. At least one of `firstname` or `lastname` is required.

## Campus Events

Base URL: `https://content.osu.edu/v2/events`

- `GET /`  
  Returns campus event listings.

## Dining

Base URL: `https://content.osu.edu/v2/api/v1/dining`

- `GET /locations`  
  Returns dining locations.
- `GET /locations/menus`  
  Returns locations with menu section metadata.
- `GET /full/menu/section/{section_id}`  
  Returns menu items for a section.

## Food Trucks

Base URL: `https://content.osu.edu/v2/foodtruck`

- `GET /events`  
  Returns food truck events.

## Library Services

Base URL: `https://content.osu.edu/v2/library`

- `GET /locations`  
  Returns library locations.
- `GET /roomreservation/api/v1/rooms`  
  Returns study rooms and reservation metadata.

## BuckID Merchants

Base URL: `https://content.osu.edu/v2/merchants`

- `GET /`  
  Returns merchant listings and metadata.

## Parking

Base URL: `https://content.osu.edu/v2/parking/garages`

- `GET /availability`  
  Returns real-time garage availability.

## Recreation Sports

Base URL: `https://content.osu.edu/v3/recsports`

- `GET /`  
  Returns recreation facilities, hours, and events.

## Student Organizations

Base URL: `https://content.osu.edu/v2/student-org`

- `GET /all`  
  Returns student organization listings and metadata.
