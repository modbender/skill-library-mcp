# Paper Lookup & Notion API Reference

## Sources
- arXiv API: `https://export.arxiv.org/api/query?search_query=all:{query}`
- Crossref API: `https://api.crossref.org/works?query.title={query}`

## Notion API
- Version: `2025-09-03`
- Parent page creation: `POST /v1/pages` with `{"parent":{"page_id":"..."}}`
- Auth: `Authorization: Bearer ${NOTION_API_KEY}`
- Query existing pages: `POST /v1/search` with query title string
- Append blocks: `PATCH /v1/blocks/{page_id}/children` with `{"children": [...]}`
- Delete blocks: `DELETE /v1/blocks/{block_id}`

## Required env
- `NOTION_API_KEY` (or `~/.config/notion/api_key`)
- `NOTION_PARENT_PAGE_ID` (or `--parent-page-id` CLI arg)

## Notion block types used
- `heading_1`, `heading_2`, `heading_3`
- `paragraph`
- `bulleted_list_item`, `numbered_list_item`
- `equation` (KaTeX)
- `divider`
- `callout`

## Block limits
- Rich text content: max ~2000 chars per block (we use 1800 for safety)
- Children append: max 100 blocks per request (we use 80)
