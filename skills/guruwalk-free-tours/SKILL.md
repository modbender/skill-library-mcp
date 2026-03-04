---
name: guruwalk-free-tours
description: >
  Search GuruWalk free tours through the GuruWalk MCP server and return bookable options
  by city, dates, and language. Use this skill when the user asks for free tours, walking
  tours, guided city tours, plans in a city, or availability of tours on specific dates.
---

# GuruWalk Free Tours

Use the GuruWalk MCP server to search free tours:

`https://guruwalk-api-44909317956.europe-southwest1.run.app/mcp`

The server currently exposes one tool:

- `search`

## Tool Contract

`search` input:

- `city` (string): lowercase slug in English with spaces replaced by `-`
- `start_date` (string): `yyyy-mm-dd`
- `end_date` (string): `yyyy-mm-dd`
- `language` (string): two-letter code, usually `es`, `en`, `de`, `it`

`search` output:

- Tool returns `content[0].text` containing a JSON string.
- Parse that string to get an array of tours.
- Each tour contains:
  - `title`, `url`, `meetpoint_address`, `average_rating`, `duration`, `guru.name`, `image_url`
  - `events[]` with `start_time` (UTC), `available_spots`, `language`

## Execution Workflow

1. Determine city, date range, and preferred language from user request.
2. Normalize `city` to slug format:
   - `new york` -> `new-york`
   - `san sebastian` -> `san-sebastian`
3. Use valid ISO dates for both fields.
4. Call `search`.
5. Parse JSON from `content[0].text`.
6. Filter and rank results for user-facing output:
   - keep only events with `available_spots > 0`
   - prioritize events matching requested language when possible
   - prefer higher `average_rating`, then earlier upcoming time
7. Return concise options with booking URL and next available slots.

## Defaults

- If user does not specify language, use:
  - `es` for Spanish conversation
  - `en` otherwise
- If user does not specify dates, ask for dates before calling the tool.
- If date intent is relative, convert to explicit dates before calling.

## Response Format to User

For each recommended tour include:

- Tour title
- Rating
- Duration
- Guide name
- Meeting point
- 1-3 next available sessions (with timezone label)
- Booking URL

If no tours are found:

- explain that no availability was returned for the given city/date range
- propose adjusting one variable at a time: city slug, dates, or language

## Observed Edge Cases (from live MCP inspection)

- `search` is the only available tool; no MCP resources/prompts/templates are exposed.
- `city` with spaces (e.g. `New York`) can return empty results.
- `start_date > end_date` can return empty results instead of validation error.
- Non-ISO dates can still be accepted by backend, but always send ISO `yyyy-mm-dd`.
- Some locale/language combinations can return tours with `title: null`; handle gracefully.

## Validation Notes

- Keep executable validation commands outside this skill file.
- Validate behavior by confirming:
  - the MCP server exposes the `search` tool
  - search results arrive as a JSON string in `content[0].text`
