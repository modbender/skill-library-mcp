# GOYFILES External Bot Tool Reference

This companion doc expands the core contract in `/skill.md`.

Source of truth for names and enums: `dashboard/app/api/chatbot/route.ts`.

## Request envelope

Call:
- `POST /api/chatbot`
- Header: `X-Bot-Identity: <identityToken>`
- Body shape:

```json
{
  "message": "short operator intent",
  "toolCalls": [
    {
      "name": "document_list",
      "args": {
        "source_dataset": "pacer-courtlistener",
        "limit": 1
      }
    }
  ]
}
```

## Response envelope

Tool outputs are in:
- `toolResults[i].payload`

For text retrieval:
- `toolResults[0].payload.rows[0].text_excerpt`

## Allowed tool names

### Graph and search

| Tool | Required args | Common optional args | Notes |
|---|---|---|---|
| `web_search` | `query` | `max_results` | External web lookup. |
| `neo4j_graph_stats` | none | `source_limit` | High-level graph stats. |
| `neo4j_search_graph_nodes` | `query` | `label`, `source_dataset`, `exact_source_dataset`, `offset`, `limit` | Main graph node search. |
| `neo4j_search_entities` | `query` | `label`, `limit` | Legacy entity search (`Person`, `Organization`, `Location`). |
| `neo4j_search_person` | `query` | `limit` | Person-specific search. |
| `neo4j_get_node_profile` | `node_id` | none | Returns labels and trimmed properties. |
| `neo4j_node_neighbors` | `node_id` | `limit` | Any-node neighbors. |
| `neo4j_person_neighbors` | `person_id` | `limit` | Person neighbors. |
| `neo4j_shortest_path` | `from_id`, `to_id` | `max_hops` | Shortest path between two node IDs. |
| `neo4j_read_cypher` | `query` | `params` | Read-only Cypher. Query must include `LIMIT`. |

### Document tools

| Tool | Required args | Common optional args | Notes |
|---|---|---|---|
| `neo4j_search_documents` | none | `query`, `source_dataset`, `source_document_id`, `title`, `filename`, `partial_text`, `exact_source_dataset`, `offset`, `limit` | Legacy alias behavior for doc search. |
| `document_search` | none | `query`, `source_dataset`, `source_document_id`, `title`, `filename`, `partial_text`, `exact_source_dataset`, `offset`, `limit` | ID discovery and scoped text search. |
| `document_list` | `source_dataset` | `offset`, `limit` | First step for valid IDs in a dataset. |
| `document_id_schema` | none | `source_dataset`, `exact_source_dataset`, `limit`, `max_samples` | Returns real ID field patterns and examples. |
| `document_ingestion_status` | none | `source_dataset`, `exact_source_dataset`, `limit` | Coverage counts by source. |
| `document_fetch` | none | `id`, `document_id`, `efta_number`, `source_dataset`, `source_document_id`, `filename`, `limit`, `max_chars`, `include_text` | Primary metadata + text fetch tool. |
| `document_extract` | none | `document_id`, `efta_number`, `page`, `max_pages`, `max_chars` | Page-level extraction path (when available). |

### Findings archive tools

| Tool | Required args | Common optional args | Notes |
|---|---|---|---|
| `archive_findings_search` | `query` | `type` (`all|finding|citation`), `dateFrom`, `dateTo`, `limit`, `offset` | Search same findings/citation archive used by Findings tabs. |
| `archive_finding_evidence` | `finding_id` | `findingId`, `id` | Returns one finding + all linked evidence citations. |

### Investigation files and notes

| Tool | Required args | Common optional args | Notes |
|---|---|---|---|
| `list_investigation_files` | none | `scope`, `directory`, `recursive`, `max_files` | Lists readable files under safe scopes. |
| `search_investigation_files` | `query` | `scope`, `directory`, `max_matches` | Line-level text search in safe scopes. |
| `read_investigation_file` | `path` | `scope`, `start_line`, `max_lines` | Reads text file windows in safe scopes. |
| `write_markdown_file` | `path`, `content` | `mode` (`overwrite` or `append`) | Writes markdown note to persistent note store. |
| `read_markdown_file` | `path` | none | Reads markdown note content and metadata. |
| `list_markdown_files` | none | `directory` | Lists saved markdown notes. |

## Supported labels for `neo4j_search_graph_nodes`

- `Any`
- `Person`
- `Organization`
- `Location`
- `Event`
- `OffshoreEntity`
- `FinancialTransaction`
- `VisitRecord`
- `Document`
- `ReconstructedPage`
- `Transcript`
- `ImageEvidence`
- `JmailEmail`
- `Flight`
- `Officer`
- `SanctionedEntity`
- `VoteRecord`
- `WikiLeaksEmail`
- `Dossier`
- `Investigation`
- `RedactedEntity`

## Investigation scope enum

- `workspace`
- `output`
- `graph`
- `ingest`
- `etl`
- `correlation`
- `dashboard_public`
- `review`
- `shared`
- `docs`
- `data`

## Known production constraint (`goyfiles.com`)

`list_investigation_files`, `search_investigation_files`, and `read_investigation_file` are local-filesystem tools.

On Vercel serverless production, local corpus directories are not mounted. Expect explicit "not available on serverless" responses for those tools.

Markdown note tools remain available because they use persistent storage, not local corpus files.

## Common caller mistakes to avoid

- Use `query`, not `name`, in `neo4j_search_person`.
- Use `person_id`, not `name`, in `neo4j_person_neighbors`.
- Use `from_id` and `to_id`, not `from_name` and `to_name`, in `neo4j_shortest_path`.
- For `document_fetch`, use IDs returned by `document_list` or `document_search`; do not guess IDs.
- Always scope heavy document operations by `source_dataset` when possible.
- For `neo4j_read_cypher`, include `LIMIT` in every query.
