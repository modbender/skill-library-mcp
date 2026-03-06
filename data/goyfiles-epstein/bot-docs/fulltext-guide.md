# GOYFILES Fulltext and Cypher Guide

Use this when `document_search` is not sufficient and you need direct fulltext search through `neo4j_read_cypher`.

## Hard rule

Every Cypher query passed to `neo4j_read_cypher` must include `LIMIT`.

## Fulltext indexes

- `document_fulltext`
  - Label: `Document`
  - Property: `full_text`
  - Granularity: document-level

- `rp_fulltext`
  - Label: `ReconstructedPage`
  - Property: `reconstructed_text`
  - Granularity: page-level OCR

## Call pattern

```json
{
  "message": "fulltext query",
  "toolCalls": [
    {
      "name": "neo4j_read_cypher",
      "args": {
        "query": "CALL db.index.fulltext.queryNodes('document_fulltext', 'maxwell') YIELD node, score RETURN node.id AS id, node.source_dataset AS source_dataset, score, substring(node.full_text,0,400) AS snippet ORDER BY score DESC LIMIT 25"
      }
    }
  ]
}
```

## Query templates

### 1) Basic keyword search

```cypher
CALL db.index.fulltext.queryNodes('document_fulltext', 'maxwell')
YIELD node, score
RETURN node.id AS id,
       node.source_dataset AS source_dataset,
       score,
       substring(node.full_text, 0, 400) AS snippet
ORDER BY score DESC
LIMIT 50
```

### 2) Exact phrase

```cypher
CALL db.index.fulltext.queryNodes('document_fulltext', '"sole beneficial owner"')
YIELD node, score
RETURN node.id AS id,
       node.source_dataset AS source_dataset,
       score,
       substring(node.full_text, 0, 400) AS snippet
ORDER BY score DESC
LIMIT 50
```

### 3) Scope to one dataset

```cypher
CALL db.index.fulltext.queryNodes('document_fulltext', 'interlochen')
YIELD node, score
WHERE node.source_dataset = 'doj-epstein-files'
RETURN node.id AS id,
       node.source_dataset AS source_dataset,
       score
ORDER BY score DESC
LIMIT 50
```

### 4) Score-based pagination

```cypher
CALL db.index.fulltext.queryNodes('document_fulltext', 'maxwell')
YIELD node, score
WHERE score < 8.5
RETURN node.id AS id,
       node.source_dataset AS source_dataset,
       score
ORDER BY score DESC
LIMIT 100
```

### 5) Page-level OCR search (`rp_fulltext`)

```cypher
CALL db.index.fulltext.queryNodes('rp_fulltext', 'interlochen')
YIELD node, score
RETURN node.id AS id,
       node.efta_number AS efta_number,
       node.page_number AS page_number,
       score,
       substring(node.reconstructed_text, 0, 400) AS snippet
ORDER BY score DESC
LIMIT 50
```

## Lucene syntax reminders

- AND: `epstein AND interlochen`
- OR: `barak OR nikolic`
- NOT: `epstein AND NOT maxwell`
- Exact phrase: `"sole beneficial owner"`
- Prefix wildcard: `carbyn*`
- Escape colon: `RE\: meeting`

## Recommended workflow

1. Use `document_id_schema` and `document_list` to get valid IDs.
2. Use `document_fetch` for canonical metadata + bounded text.
3. Use `neo4j_read_cypher` fulltext only when you need precision recall or custom ranking logic.
