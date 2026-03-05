# Pipedrive API v1 Notes

## Base URL

Preferred:

- `https://{company}.pipedrive.com/api/v1`

Alternative global base (if account setup supports it):

- `https://api.pipedrive.com/api/v1`

## Authentication

- API token query param: `api_token=...`
- OAuth bearer token header: `Authorization: Bearer ...`

## Common Resources

- Persons: `/persons`
- Organizations: `/organizations`
- Deals: `/deals`
- Leads: `/leads`
- Activities: `/activities`
- Notes: `/notes`
- Pipelines: `/pipelines`
- Stages: `/stages`
- Users: `/users`
- Products: `/products`

## Common Query Patterns

- Pagination: `start`, `limit`
- Ownership/filtering varies by endpoint (`user_id`, `filter_id`, etc.)
- Search endpoints include `/search` or `/find` depending on resource

## Error Patterns

- `401/403`: invalid token or missing scopes
- `429`: rate-limited; retry with backoff
- `5xx`: transient server issue; retry

## Strategy for Full CRM Coverage

Use wrapped commands for high-frequency CRM operations.
Use the `request` command for less common endpoints so any UI-equivalent API action can be executed without waiting for script updates.
