# GOYFILES Dataset and Source Reference

This companion doc expands `/skill.md` with source identity rules.

Source of truth: `dashboard/lib/source-registry.ts`.

## Canonical source contract

- All source routing uses canonical `source_dataset` names.
- Legacy aliases are normalized to canonicals.
- Always pass canonical names when possible.

## Canonical source list (current)

1. `cbp-records`
2. `congress-votes`
3. `contact-book`
4. `doj-epstein-files`
5. `doj-ogr`
6. `dancing-israelis`
7. `dugganusa`
8. `efta-analysis-v1`
9. `efta-db`
10. `epstein-doc-explorer`
11. `epstein-files`
12. `epstein-network`
13. `fbi-vault`
14. `gdelt`
15. `gif-dossiers`
16. `gif-fulltext-link`
17. `heystack-flights`
18. `house-oversight`
19. `icij-offshore`
20. `icij-reconciliation`
21. `indexofepstein`
22. `jmail`
23. `jmail-amazon`
24. `jmail-flights`
25. `nydfs-db-order`
26. `open-sanctions`
27. `pacer-courtlistener`
28. `rhowardstone-corpus`
29. `rhowardstone-images`
30. `rhowardstone-kg`
31. `rhowardstone-redaction`
32. `rhowardstone-transcripts`
33. `sba-ppp`
34. `sec-edgar`
35. `spacy-ner`
36. `svetimfm`
37. `uk-court-circular`
38. `wh-visitor-logs`
39. `wh-visitor-logs-biden`
40. `wikidata`
41. `wyden-memo`

## Text strategy by source

### Native

- `dancing-israelis`
- `doj-ogr`
- `dugganusa`
- `jmail`
- `rhowardstone-corpus`
- `rhowardstone-images`
- `rhowardstone-kg`
- `rhowardstone-transcripts`

### Pointer

- `cbp-records`
- `efta-analysis-v1`
- `fbi-vault`
- `house-oversight`
- `nydfs-db-order`
- `pacer-courtlistener`
- `wyden-memo`

### SQLite

- `doj-epstein-files`
- `efta-db`

### Generated metadata fallback

- `congress-votes`
- `contact-book`
- `epstein-doc-explorer`
- `epstein-files`
- `epstein-network`
- `gdelt`
- `gif-dossiers`
- `gif-fulltext-link`
- `heystack-flights`
- `icij-offshore`
- `icij-reconciliation`
- `indexofepstein`
- `jmail-amazon`
- `jmail-flights`
- `open-sanctions`
- `rhowardstone-redaction`
- `sba-ppp`
- `sec-edgar`
- `spacy-ner`
- `svetimfm`
- `uk-court-circular`
- `wh-visitor-logs`
- `wh-visitor-logs-biden`
- `wikidata`

## Common legacy aliases

- `pacer` -> `pacer-courtlistener`
- `fbi` -> `fbi-vault`
- `nydfs` -> `nydfs-db-order`
- `cbp` -> `cbp-records`
- `wyden` -> `wyden-memo`
- `heystack` -> `heystack-flights`
- `blackbook` -> `indexofepstein`
- `opensanctions` -> `open-sanctions`
- `congress` -> `congress-votes`
- `ppp` -> `sba-ppp`
- `doj` or `efta` -> `doj-epstein-files`

## Always use ID discovery before fetch

### Step 1: Check dataset ID shapes

```bash
curl -sS -X POST "https://goyfiles.com/api/chatbot" \
  -H "Content-Type: application/json" \
  -H "X-Bot-Identity: $IDENTITY_TOKEN" \
  -d '{"message":"schema","toolCalls":[{"name":"document_id_schema","args":{"source_dataset":"pacer-courtlistener","max_samples":5}}]}'
```

### Step 2: List real records

```bash
curl -sS -X POST "https://goyfiles.com/api/chatbot" \
  -H "Content-Type: application/json" \
  -H "X-Bot-Identity: $IDENTITY_TOKEN" \
  -d '{"message":"list","toolCalls":[{"name":"document_list","args":{"source_dataset":"pacer-courtlistener","limit":5}}]}'
```

### Step 3: Fetch with valid ID from list

```bash
curl -sS -X POST "https://goyfiles.com/api/chatbot" \
  -H "Content-Type: application/json" \
  -H "X-Bot-Identity: $IDENTITY_TOKEN" \
  -d '{"message":"fetch","toolCalls":[{"name":"document_fetch","args":{"id":"pacer-doc-ar001498","max_chars":6000}}]}'
```

## Practical notes

- If `document_fetch` returns zero rows, the lookup key does not match that source scope.
- Many structured sources are metadata-first; generated text fallback is expected there.
- For deep content search, use `neo4j_read_cypher` plus fulltext indexes. See `/bot-docs/fulltext-guide.md`.
