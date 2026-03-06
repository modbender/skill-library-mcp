---
name: wallhaven-downloader
description: Download wallpapers in batch from wallhaven.cc via API v1 with flexible query parameters (q, categories, purity, sorting, order, topRange, atleast, resolutions, ratios, colors, page, seed). Use when user asks to download one or many wallpapers from Wallhaven, especially with custom filters (e.g. purity/category/toplist/time range) and target folder requirements.
metadata: {"clawdbot":{"requires":{"commands":["python3","curl"],"env":["WALLHAVEN_API_KEY"]}}}
---

# Wallhaven Downloader

Use the bundled script to download wallpapers from Wallhaven API with custom parameters.

## Command

```bash
python3 {baseDir}/scripts/wallhaven_download.py \
  --apikey "<API_KEY>" \
  --count 20 \
  --out "/home/node/.openclaw/workspace/downloads/n1" \
  --categories 111 \
  --purity 001 \
  --sorting toplist \
  --order desc \
  --topRange 1M

# or parse directly from wallhaven search URL
python3 {baseDir}/scripts/wallhaven_download.py \
  --apikey "<API_KEY>" \
  --count 20 \
  --out "/home/node/.openclaw/workspace/downloads/n1" \
  --search-url "https://wallhaven.cc/search?categories=111&purity=001&sorting=toplist&order=desc&topRange=1M"
```

## Inputs

- `--apikey` (optional): Wallhaven API key. Required for NSFW (`purity` includes last bit = `1`) and private/user-filtered results.
- `--search-url` (optional): Paste a Wallhaven search URL; script auto-parses supported query parameters.
- `--count`: Total number of images to download.
- `--out`: Output directory.
- `--base-url`: API endpoint (default: `https://wallhaven.cc/api/v1/search`). Restricted to Wallhaven API hosts for safety.
- Any API search parameter as `--<name> <value>` (e.g. `--q`, `--categories`, `--purity`, `--sorting`, `--order`, `--topRange`, `--atleast`, `--resolutions`, `--ratios`, `--colors`, `--seed`, `--page`).
- When both `--search-url` and explicit `--<name> <value>` are provided, explicit args override URL values.

## Behavior

- Auto-paginates until requested count is reached or no more results.
- Reads `meta.last_page` and stops safely.
- Downloads from each result `path` URL after strict safety validation.
- Names files with index + wallpaper id: `01-wallhaven-<id>.<ext>`.
- Writes `manifest.json` with source query and downloaded items.

## Common Examples

```bash
# 1) Toplist (last month), NSFW only, download 20
python3 {baseDir}/scripts/wallhaven_download.py \
  --apikey "<API_KEY>" \
  --count 20 \
  --out "./downloads/n1" \
  --categories 111 \
  --purity 001 \
  --sorting toplist \
  --order desc \
  --topRange 1M

# 2) Keyword search (SFW), minimum resolution 2560x1440
python3 {baseDir}/scripts/wallhaven_download.py \
  --count 30 \
  --out "./downloads/city-night" \
  --q "city night" \
  --categories 100 \
  --purity 100 \
  --sorting relevance \
  --atleast 2560x1440

# 3) Random with seed (reproducible pagination)
python3 {baseDir}/scripts/wallhaven_download.py \
  --count 48 \
  --out "./downloads/random-set" \
  --sorting random \
  --seed abc123
```

## Parameter Guide (Wallhaven API)

- `q`: fuzzy query / advanced query operators (`+tag`, `-tag`, `@user`, `type:png`, `like:<id>`)
- `categories`: 3-bit switch (general/anime/people), e.g. `111`, `100`, `010`
- `purity`: 3-bit switch (sfw/sketchy/nsfw), e.g. `100`, `110`, `001` (NSFW needs valid API key)
- `sorting`: `date_added`, `relevance`, `random`, `views`, `favorites`, `toplist`
- `order`: `desc` or `asc`
- `topRange`: `1d`, `3d`, `1w`, `1M`, `3M`, `6M`, `1y` (works with `sorting=toplist`)
- `atleast`: minimum resolution (e.g. `1920x1080`)
- `resolutions`: exact resolutions, comma-separated
- `ratios`: aspect ratios, comma-separated (e.g. `16x9,21x9`)
- `colors`: hex color (no `#`, e.g. `ff6600`)
- `seed`: seed for random listing pagination
- `page`: manual start page (script will keep paginating)

## Output

- Downloaded files: `01-wallhaven-<id>.<ext>`, `02-...`
- Manifest: `<out>/manifest.json`
  - includes requested count, actual downloaded count, resolved params, and per-item metadata

## Notes

- API limit is 45 requests/min. Script inserts a small delay between page requests.
- Do not hardcode API keys in the skill/script. Pass via `--apikey` or `WALLHAVEN_API_KEY` only.
- Security guardrails: only `https://wallhaven.cc` API endpoints and `https://w.wallhaven.cc` image URLs are accepted; local/private/non-HTTPS hosts are rejected.
- If API returns errors, script exits with clear message.
- If fewer results exist than requested, script downloads available items and reports actual count.
