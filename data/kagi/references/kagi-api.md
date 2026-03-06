# Kagi API quick reference

Source: https://help.kagi.com/kagi/api/

## Auth

Kagi uses an HTTP Authorization header:

```
Authorization: Bot <KAGI_API_TOKEN>
```

Tokens are created at: https://kagi.com/settings/api

## Base URL

- `https://kagi.com/api/v0`

## Endpoints used by this skill

### Search API

- `GET /search?q=<query>`
- Returns `meta` + `data[]` results (url/title/snippet/etc.)

Example:

```bash
curl -H "Authorization: Bot $KAGI_API_TOKEN" \
  "https://kagi.com/api/v0/search?q=steve+jobs"
```

### FastGPT

- `POST /fastgpt`
- JSON body: `{ "query": "…", "cache": true }`

Example:

```bash
curl -H "Authorization: Bot $KAGI_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"query":"Python 3.11"}' \
  https://kagi.com/api/v0/fastgpt
```
