# Dievio Pagination

Dievio uses page-based pagination.

## Request Fields

- `_page`: page number, default `1`
- `_per_page`: rows per page, default `25` for search, `100` for LinkedIn lookup
- `max_results`: cap on total rows across pages, default `500`, max `100000`

## Response Fields

- `page`
- `per_page`
- `total_pages`
- `total_count`
- `has_more`
- `next_page` (null when no next page)

## Loop Pattern

1. Start with `_page=1`.
2. Execute request.
3. Append `preview_data` (search) or `data` (LinkedIn lookup).
4. Stop when `has_more=false` or `next_page` is null.
5. Otherwise set `_page=next_page` and continue.

## Important Notes

- Credits are charged by rows returned.
- If credits are low, pages may return fewer rows than requested.
- Keep `max_results` explicit for predictable billing.
