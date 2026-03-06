---
name: digiforma
description: Query Digiforma training management platform via GraphQL API. Use when asked about trainees, sessions, invoices, programs, trainers, or any training data.
metadata: {"clawdbot":{"emoji":"🎓"}}
---
# Digiforma GraphQL API

Digiforma is a French training management platform (centre de formation). Query it via GraphQL.

## Authentication

All requests use Bearer token auth. The API key is stored in environment variable `DIGIFORMA_API_KEY`.

## Endpoint

POST https://app.digiforma.com/api/v1/graphql

## How to query

Use curl:
```bash
curl -s -X POST https://app.digiforma.com/api/v1/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $DIGIFORMA_API_KEY" \
  -d '{"query": "YOUR_GRAPHQL_QUERY"}'
```

## Common queries

### List trainees (stagiaires)
```graphql
{ trainees(perPage: 20, page: 1) { items { id firstName lastName email phone } pagination { totalItems totalPages } } }
```

### Search trainee by name
```graphql
{ trainees(perPage: 10, page: 1, search: "NOM") { items { id firstName lastName email phone } } }
```

### List training sessions
```graphql
{ trainingSessions(perPage: 20, page: 1) { items { id name status startDate endDate program { name } } pagination { totalItems totalPages } } }
```

### List programs
```graphql
{ programs(perPage: 20, page: 1) { items { id name duration } pagination { totalItems totalPages } } }
```

### List invoices
```graphql
{ invoices(perPage: 20, page: 1) { items { id number amount status dueDate company { name } } pagination { totalItems totalPages } } }
```

### List trainers (formateurs)
```graphql
{ trainers(perPage: 20, page: 1) { items { id firstName lastName email } pagination { totalItems totalPages } } }
```

### Training session details
```graphql
{ trainingSession(id: ID) { id name status startDate endDate program { name } trainees { firstName lastName email } trainer { firstName lastName } } }
```

## Pagination
Always use perPage and page. Check pagination.totalPages to know if more pages exist.

## Important notes
- All dates are ISO format
- Status values: draft, planned, ongoing, completed, cancelled
- Always paginate large results (perPage max ~50)
- For complex filters, combine search with status filters
