# Bring Inspirations API Reference (node-bring-api)

## Purpose

Use the Bring! inspirations endpoints to retrieve recipe suggestions and filters. This skill is optimized for seasonal recipe ideas and can optionally add selected dish names to a shopping list.

## Auth flow

1. POST `https://api.getbring.com/rest/v2/bringauth`
   - Body: `email`, `password` (URL-encoded)
   - Response includes `uuid`, `access_token`, `refresh_token`, `publicUuid`
2. Set headers for subsequent calls:
   - `X-BRING-API-KEY`: `<public client key from bring-shopping npm package>`
   - `X-BRING-CLIENT`: `webApp`
   - `X-BRING-CLIENT-SOURCE`: `webApp`
   - `X-BRING-COUNTRY`: `DE` (use user locale country if known)
   - `X-BRING-USER-UUID`: `<uuid from login>`
   - `Authorization`: `Bearer <access_token>`

## Inspirations

- **Filters list**: `GET /bringusers/{uuid}/inspirationstreamfilters`
  - Use to discover available filter tags (season, diet, cuisine, etc.).
- **Inspirations**: `GET /bringusers/{uuid}/inspirations?filterTags=<tags>&offset=0&limit=2147483647`
  - `filterTags` is passed as a string. Use the tags from the filters endpoint.
  - Each entry includes `content.contentSrcUrl` for fetching full recipe data.
  - Fetch `contentSrcUrl` with the same headers to get `items[]` (ingredient list).

## Lists (optional for adding dishes)

- **Lists**: `GET /bringusers/{uuid}/lists`
- **Add item**: `PUT /bringlists/{listUuid}`
  - Body (URL-encoded): `purchase=<item>&recently=&specification=&remove=&sender=null`

## Recipe content details

- `GET https://api.getbring.com/rest/v2/bringtemplates/content/<contentUuid>`
  - Requires auth headers (same as other endpoints).
  - Response includes `items[]` with `itemId` and `spec` per ingredient.

## Notes

- The inspirations response structure is not documented here; inspect the JSON payload at runtime and map fields to the user-facing output.
- Prefer calling the filters endpoint first, then choose seasonal tags based on the returned list.
- Keep output lightweight: propose 3-7 recipes, include name and short description if available.
