# OpenSubtitles API (Read-only) Reference

Base URL: `https://api.opensubtitles.com/api/v1`

## Required headers

- `Api-Key: <OPENSUBTITLES_API_KEY>`
- `User-Agent: <APP_NAME> <APP_VERSION>`
- For download requests: `Authorization: Bearer <TOKEN>`

## Key endpoints

### Search subtitles
`GET /subtitles`

Useful params:
- `query` (text)
- `languages` (comma-separated, alphabetical; e.g., `en,fr`)
- `imdb_id`, `tmdb_id`
- For TV: `parent_imdb_id` or `parent_tmdb_id` + `season_number` + `episode_number`

Notes:
- If you can provide IDs, prefer them over query strings.
- If a moviehash is available, include it.
- Avoid ordering unless needed; it reduces cache hits.
- Follow HTTP redirects for search (use `curl -L`).
- To reduce redirects, send sorted, lowercase parameters without defaults.

### Download link
`POST /download`

Body:
- `file_id` (required)
- Optional: `sub_format`, `file_name`, `in_fps`, `out_fps`, `timeshift`, `force_download`

Important:
- Must include **both** `Api-Key` and `Authorization` headers.
- Download link is temporary (~3 hours). Do not cache.
- Download count is incremented when requesting the link.

### Login / Logout (token)
`POST /login` (username + password) returns `token` and `base_url`.
`DELETE /logout` destroys token.

Rate limits for login: **1 req/sec, 10/min, 30/hour**. If 401, stop retrying.
If `base_url` is `vip-api.opensubtitles.com`, include JWT token on all requests.

## Formats
`GET /infos/formats` lists available subtitle formats.
