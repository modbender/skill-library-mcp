# Dievio API Reference (Condensed)

## Base and Endpoints

- Base host: `https://dievio.com`
- Lead Search: `POST /api/public/search`
- LinkedIn Lookup: `POST /api/linkedin/lookup`

## Authentication

Supported header styles:

- `Authorization: Bearer <API_KEY>`
- `X-API-Key: <API_KEY>`

## Lead Search Request

Endpoint:

```text
POST https://dievio.com/api/public/search
```

Pagination fields:

- `_page` (default `1`)
- `_per_page` (default `25`)
- `max_results` (default `500`, max `100000`)

Output flags:

- `_include_raw` (default `true`)
- `include_emails` (default `true`)
- `include_phones` (default `false`)
- `email_status` (`all` | `verified` | `likely`, default `all`)

Response keys:

- `success`, `count`, `preview_count`, `preview_data`
- `page`, `per_page`, `total_pages`, `total_count`
- `has_more`, `next_page`, `max_results`

## LinkedIn Lookup Request

Endpoint:

```text
POST https://dievio.com/api/linkedin/lookup
```

Required:

- `linkedinUrls` (array, up to `100000` URLs)

Options:

- `includeWorkEmails` (default `true`)
- `includePersonalEmails` (default `true`)
- `onlyWithEmails` (default `true`)
- `includePhones` (default `false`)
- `_page` (default `1`)
- `_per_page` (default `100`)
- `max_results` (max `100000`)

Response keys:

- `success`, `count`, `data`
- `page`, `per_page`, `total_pages`, `total_count`
- `has_more`, `next_page`, `max_results`

## Credit Model

- Public API uses API credits.
- 1 credit = 1 lead/result returned.
- If balance is lower than requested page size, fewer rows can be returned.
