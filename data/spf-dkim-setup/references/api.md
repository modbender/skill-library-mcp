# Cloudflare DNS API Reference

Base URL: `https://api.cloudflare.com/client/v4`

Auth: `Authorization: Bearer $CLOUDFLARE_API_TOKEN`

## List DNS Records
`GET /zones/{zone_id}/dns_records`

Query params: `type`, `name`, `content`, `page`, `per_page` (default 20, max 50000), `order` (type/name/content/ttl/proxied), `direction` (asc/desc), `match` (any/all)

## Get DNS Record
`GET /zones/{zone_id}/dns_records/{dns_record_id}`

## Create DNS Record
`POST /zones/{zone_id}/dns_records`

```json
{
  "type": "A|AAAA|CNAME|TXT|MX|NS|SRV|CAA",
  "name": "example.com",
  "content": "value",
  "ttl": 3600,
  "proxied": false,
  "comment": "optional comment",
  "tags": ["optional:tag"]
}
```

Notes:
- A/AAAA cannot coexist with CNAME on the same name
- NS cannot coexist with any other type on the same name
- For MX: include `priority` field
- For SRV: use `data` object with `priority`, `weight`, `port`, `target`

## Update DNS Record (Patch)
`PATCH /zones/{zone_id}/dns_records/{dns_record_id}`

Send only fields to update.

## Overwrite DNS Record (Put)
`PUT /zones/{zone_id}/dns_records/{dns_record_id}`

Send all fields (full replacement).

## Delete DNS Record
`DELETE /zones/{zone_id}/dns_records/{dns_record_id}`

## Export DNS Records
`GET /zones/{zone_id}/dns_records/export`

Returns BIND format.

## Import DNS Records
`POST /zones/{zone_id}/dns_records/import`

Upload BIND config file via multipart form.

## Batch DNS Records
`POST /zones/{zone_id}/dns_records/batch`

Create, update, or delete multiple records in one call:

```json
{
  "posts": [{"type": "TXT", "name": "example.com", "content": "value"}],
  "puts": [{"id": "record_id", "type": "TXT", "name": "example.com", "content": "new-value"}],
  "deletes": [{"id": "record_id"}]
}
```

## List Zones (find zone_id)
`GET /zones?name=example.com`

Returns zone details including `id` (the zone_id).

## Response Format

All responses:
```json
{
  "success": true,
  "errors": [],
  "messages": [],
  "result": { ... }
}
```

Pagination (list endpoints):
```json
{
  "result_info": {
    "page": 1,
    "per_page": 20,
    "count": 1,
    "total_count": 1,
    "total_pages": 1
  }
}
```
