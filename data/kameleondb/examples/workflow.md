# Example: Agent-Driven Data Modeling Workflow

This example shows how an agent discovers, structures, and optimizes data using KameleonDB.

## Scenario: Agent Processing Customer Data

An agent receives unstructured customer data and needs to store it for analysis.

### Step 1: Discover Existing Schema

```bash
$ kameleondb --json schema list
{"entities": []}

# No entities yet - agent will create them
```

### Step 2: Create Initial Entity

```bash
$ kameleondb --json schema create Contact \
  --field "name:string:required" \
  --field "email:string:unique" \
  --created-by "ingestion-agent"

{"success": true, "entity": "Contact", "fields": ["name", "email"]}
```

### Step 3: Insert Data

```bash
$ kameleondb --json data insert Contact \
  '{"name":"Alice Johnson","email":"alice@acme.com"}' \
  --created-by "ingestion-agent"

{"success": true, "id": "550e8400-e29b-41d4-a716-446655440000"}
```

### Step 4: Agent Discovers More Fields

Agent processes more data and finds phone numbers and company info:

```bash
$ kameleondb --json schema add-field Contact "phone:string" \
  --reason "Found phone numbers in 45% of records" \
  --created-by "ingestion-agent"

{"success": true, "field": "phone"}

$ kameleondb --json schema add-field Contact "company_id:string:indexed" \
  --reason "Need to link to company entities" \
  --created-by "ingestion-agent"

{"success": true, "field": "company_id"}
```

### Step 5: Query with Schema Context

```bash
# Get schema context for SQL generation
$ kameleondb --json schema context --entity Contact

{
  "dialect": "postgresql",
  "entities": [{
    "name": "Contact",
    "entity_id": "uuid-here",
    "storage_mode": "shared",
    "table_name": "kdb_records",
    "fields": [
      {"name": "name", "type": "string", "required": true, "sql_access": "data->>'name'"},
      {"name": "email", "type": "string", "unique": true, "sql_access": "data->>'email'"},
      {"name": "phone", "type": "string", "sql_access": "data->>'phone'"},
      {"name": "company_id", "type": "string", "indexed": true, "sql_access": "data->>'company_id'"}
    ],
    "record_count": 156
  }],
  "example_queries": [
    "SELECT data->>'name', data->>'email' FROM kdb_records WHERE entity_id='uuid-here'"
  ]
}

# Agent generates and executes SQL
$ kameleondb --json query run \
  "SELECT data->>'name' as name, data->>'email' as email, data->>'phone' as phone \
   FROM kdb_records \
   WHERE entity_id='uuid-here' AND is_deleted=false \
   LIMIT 100" \
  --entity Contact

{
  "rows": [
    {"name": "Alice Johnson", "email": "alice@acme.com", "phone": "+1-555-0101"},
    ...
  ],
  "metrics": {
    "execution_time_ms": 52.3,
    "row_count": 156,
    "has_join": false
  },
  "suggestions": [
    {
      "entity_name": "Contact",
      "priority": "medium",
      "reason": "Entity has 156 records, consider materialization for better performance",
      "action": "kameleondb storage materialize Contact"
    }
  ]
}
```

### Step 6: Agent Optimizes Storage

```bash
$ kameleondb --json storage materialize Contact \
  --reason "Query optimization hint - 156 records with frequent queries" \
  --created-by "optimization-agent"

{
  "success": true,
  "entity_name": "Contact",
  "storage_mode": "dedicated",
  "table_name": "kdb_contact",
  "records_migrated": 156,
  "duration_seconds": 0.234
}

# Future queries now use typed columns and indexes
```

### Step 7: Batch Insert with Schema Evolution

```bash
# Agent discovers LinkedIn profiles and adds field
$ kameleondb --json schema add-field Contact "linkedin_url:string" \
  --reason "Found LinkedIn profiles in enrichment data" \
  --created-by "enrichment-agent"

# Batch insert enriched data
$ kameleondb --json data insert Contact \
  --from-file enriched_contacts.jsonl \
  --batch

{"success": true, "records_inserted": 42}
```

### Step 8: Check Storage Status

```bash
$ kameleondb --json storage status Contact

{
  "entity_name": "Contact",
  "storage_mode": "dedicated",
  "table_name": "kdb_contact",
  "record_count": 198,
  "query_stats": {
    "avg_execution_time_ms": 12.4,
    "total_queries": 47
  }
}
```

## Workflow Summary

This workflow demonstrates:

1. **Schema Discovery** - Agent checks what exists (`schema list`)
2. **Schema Creation** - Agent designs initial structure (`schema create`)
3. **Data Insertion** - Agent inserts records (`data insert`)
4. **Schema Evolution** - Agent adds fields as needs discovered (`schema add-field`)
5. **Context-Aware Querying** - Agent uses schema context for SQL generation (`schema context`)
6. **Performance Optimization** - Agent acts on hints to materialize (`storage materialize`)
7. **Iterative Enhancement** - Agent continues to evolve schema based on new data
8. **Monitoring** - Agent checks storage status (`storage status`)

**Key Takeaway**: The agent owns the entire data lifecycle - from initial schema design through optimization - without human intervention.
