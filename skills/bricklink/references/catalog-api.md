# BrickLink Catalog Item API (Store v1)

Base URL: `https://api.bricklink.com/api/store/v1`

## Get Item

- `GET /items/{type}/{no}`
  - `type`: MINIFIG, PART, SET, BOOK, GEAR, CATALOG, INSTRUCTION, UNSORTED_LOT, ORIGINAL_BOX
  - `no`: item number (e.g. `3001old`, `7644-1`)

## Get Supersets

- `GET /items/{type}/{no}/supersets`
  - optional query: `color_id`

## Get Subsets

- `GET /items/{type}/{no}/subsets`
  - optional query:
    - `color_id` (only valid for PART)
    - `box` (Boolean)
    - `instruction` (Boolean)
    - `break_minifigs` (Boolean)
    - `break_subsets` (Boolean)

## Get Price Guide

- `GET /items/{type}/{no}/price`
  - optional query:
    - `color_id`
    - `guide_type`: `stock` (default) or `sold`
    - `new_or_used`: `N` (default) or `U`
    - `country_code`
    - `region`: asia, africa, north_america, south_america, middle_east, europe, eu, oceania
    - `currency_code`
    - `vat`: `N` (default), `Y`, `O`

## Get Known Colors

- `GET /items/{type}/{no}/colors`

## Resource representations

See:
- https://www.bricklink.com/v3/api.page?page=resource-representations-catalog

Covers: Item resource, Superset Entry, Subset Entry, Price Guide, Price Detail, Known Color.
