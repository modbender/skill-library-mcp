---
name: k-cinema-bridge
description: Query Korean multiplex (Lotte Cinema, CGV, Megabox) box office rankings and upcoming movie data enriched with KOBIS details. Use when the user asks about Korean movies currently showing, box office rankings, upcoming releases, or wants movie recommendations based on genre, director, actor, or rating.
homepage: https://uyeong.github.io/k-cinema-bridge/
allowed-tools: WebFetch
---

# k-cinema-bridge

A JSON API providing Korean multiplex (Lotte Cinema, CGV, Megabox) box office and upcoming movie data, enriched with detailed information such as genre, director, and cast from KOBIS (Korean Film Council). Data is automatically refreshed daily at 00:00 UTC.

## API Reference

- Base URL: `https://uyeong.github.io/k-cinema-bridge`
- All endpoints are accessible via `GET` requests without authentication.
- The `info` field may be `null`, so always perform a `null` check before accessing it.

| Endpoint | Description |
|---|---|
| GET /api/boxoffice.json | Combined box office from all sources (`{lotte, cgv, megabox}`) |
| GET /api/boxoffice/{source}.json | Box office by source (`BoxOfficeMovie[]`) |
| GET /api/upcoming.json | Combined upcoming movies from all sources (`{lotte, cgv, megabox}`) |
| GET /api/upcoming/{source}.json | Upcoming movies by source (`UpcomingMovie[]`) |

Valid source values: `lotte`, `cgv`, `megabox`

## Data Models

### BoxOfficeMovie

```
source: "lotte" | "cgv" | "megabox"
rank: number          -- Box office rank (starting from 1)
title: string         -- Movie title
rating: string        -- Audience rating
posterUrl: string     -- Poster image URL
info?: MovieInfo      -- KOBIS detailed info (may be null)
```

### UpcomingMovie

```
source: "lotte" | "cgv" | "megabox"
title: string         -- Movie title
rating: string        -- Audience rating
posterUrl: string     -- Poster image URL
releaseDate: string   -- Release date (YYYY-MM-DD, may be an empty string)
info?: MovieInfo      -- KOBIS detailed info (may be null)
```

### MovieInfo

```
code, title, englishTitle, originalTitle: string
runtime: string (minutes)
productionYear, openDate (YYYYMMDD), productionStatus, type: string
nations: string[]     -- Production countries
genres: string[]
directors: {name, englishName}[]
actors: {name, englishName, role, roleEnglish}[]
showTypes: {group, name}[]
companies: {code, name, englishName, part}[]
audits: {number, grade}[]
staff: {name, englishName, role}[]
```

## Instructions

### Recommending Popular Movies

When the user asks for movie recommendations or what's popular:

1. Fetch `GET {BASE_URL}/api/boxoffice.json` to retrieve combined box office data from all sources.
2. Identify movies that appear across multiple sources with low rank values — lower rank means higher popularity.
3. Present the top-ranked movies with their title, rating, and genre from `info.genres` if available.

### Announcing Upcoming Releases

When the user asks about upcoming or soon-to-be-released movies:

1. Fetch `GET {BASE_URL}/api/upcoming.json` to retrieve combined upcoming movie data.
2. Filter results by `releaseDate` (YYYY-MM-DD) to match the user's requested time range.
3. Provide details such as genre, directors, and actors from the `info` field if available.

### Searching by Genre, Director, or Actor

When the user asks about a specific genre, director, or actor:

1. Fetch both `GET {BASE_URL}/api/boxoffice.json` and `GET {BASE_URL}/api/upcoming.json`.
2. Filter results using the `info` field:
    - Genre: match against `info.genres`
    - Director: match against `info.directors[].name`
    - Actor: match against `info.actors[].name`
3. Always null-check the `info` field before accessing nested properties.

### Filtering by Audience Rating

When the user asks for age-appropriate movies:

1. Use the `rating` field to filter. This field is always present and does not require the `info` field.
2. Known rating values: "전체 관람가" (All ages), "12세 관람가" (12+), "15세 관람가" (15+), "청소년 관람불가" (Adults only).

### Querying a Specific Multiplex

When the user asks about a specific cinema chain:

1. Fetch `GET {BASE_URL}/api/boxoffice/{source}.json` or `GET {BASE_URL}/api/upcoming/{source}.json`.
2. Valid source values: `lotte`, `cgv`, `megabox`.

### Comparing Across Multiplexes

When the user asks to compare rankings between cinema chains:

1. Fetch `GET {BASE_URL}/api/boxoffice.json` to retrieve combined data.
2. Find movies with the same `title` across different sources and compare their `rank` values.

## Response Guidelines

- Respond in the same language the user is using.
- When presenting movie lists, include title, rank or release date, rating, and genre when available.
- If `info` is `null` for a movie, present only the base fields (title, rank, rating, posterUrl) without guessing missing details.
- When comparing across multiplexes, use a table format for clarity.
