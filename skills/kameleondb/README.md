# KameleonDB Skill

**Agent-native database for dynamic schema evolution**

This OpenClaw skill provides agents full control over data lifecycle: schema design, ingestion, evolution, and querying - all without migrations or DDL.

## Features

- **Dynamic Schema Evolution** - Add fields at runtime, zero lock operations
- **Agent Hints Pattern** - Queries return optimization suggestions inline
- **Hybrid Storage** - Flexible JSONB or dedicated typed tables
- **Full Audit Trail** - Every schema change tracked with reasoning
- **JSON I/O** - All operations support `--json` for machine-readable output

## Installation

```bash
pip install kameleondb[postgresql]
```

## Configuration

Set `KAMELEONDB_URL` in OpenClaw config or environment:

```json
{
  "env": {
    "KAMELEONDB_URL": "postgresql://localhost/kameleondb"
  }
}
```

For development, use SQLite:
```json
{
  "env": {
    "KAMELEONDB_URL": "sqlite:///./kameleondb.db"
  }
}
```

## Quick Start

```bash
# Initialize
kameleondb admin init

# Create entity
kameleondb --json schema create Contact \
  --field "name:string:required" \
  --field "email:string:unique"

# Insert data
kameleondb --json data insert Contact '{"name":"Alice","email":"alice@example.com"}'

# Query
kameleondb --json data list Contact
```

See [SKILL.md](SKILL.md) for complete documentation.

## Use Cases

- **Data Ingestion Agents** - Discover schema needs, create entities, batch insert
- **Enrichment Agents** - Add fields as new data sources discovered
- **Query Agents** - Generate SQL with schema context, optimize based on hints
- **Data Modeling Agents** - Design relationships, materialize for performance

## Why KameleonDB?

Traditional databases force agents to work within rigid schemas designed by humans. KameleonDB **makes agents the data engineers** - they design schemas, evolve them as they reason, and optimize storage based on usage patterns.

**Schema-on-Reason**: Schema emerges from continuous agent reasoning, not upfront human design.

## Links

- [GitHub Repository](https://github.com/marcosnataqs/kameleondb)
- [PyPI Package](https://pypi.org/project/kameleondb/)
- [First Principles](https://github.com/marcosnataqs/kameleondb/blob/main/FIRST-PRINCIPLES.md)
- [Architecture Guide](https://github.com/marcosnataqs/kameleondb/blob/main/docs/ARCHITECTURE.md)
