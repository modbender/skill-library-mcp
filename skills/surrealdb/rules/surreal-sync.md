# Surreal-Sync -- Data Migration and Synchronization

Surreal-Sync is SurrealDB's data migration and synchronization tool. It enables full and incremental data transfer from external databases and streaming sources into SurrealDB, supporting both one-time migrations and continuous synchronization.

---

## Supported Sources

| Source | Sync Type | Method | Incremental Tracking |
|--------|-----------|--------|---------------------|
| MongoDB | Full + incremental | Change streams | Resume token |
| MySQL | Full + incremental | Trigger-based CDC + sequence checkpoints | Trigger tables |
| PostgreSQL (triggers) | Full + incremental | Trigger-based CDC | Trigger tables |
| PostgreSQL (wal2json) | Full + incremental | Logical replication | LSN position |
| Neo4j | Full + incremental | Timestamp-based tracking | Timestamp watermark |
| JSONL | Bulk import | JSON Lines file processing | N/A (one-time) |
| Kafka | Streaming | Consumer subscriptions with deduplication | Consumer offset |

---

## CLI Usage

### General Syntax

```bash
surreal-sync from <SOURCE> <COMMAND> \
  --connection-string <CONN_STRING> \
  --surreal-endpoint <ENDPOINT> \
  --surreal-username <USER> \
  --surreal-password <PASS> \
  --to-namespace <NS> \
  --to-database <DB>
```

### Common Flags

| Flag | Description | Required |
|------|-------------|----------|
| `--connection-string` | Source database connection string | Yes |
| `--surreal-endpoint` | SurrealDB endpoint URL | Yes |
| `--surreal-username` | SurrealDB username | Yes |
| `--surreal-password` | SurrealDB password | Yes |
| `--to-namespace` | Target SurrealDB namespace | Yes |
| `--to-database` | Target SurrealDB database | Yes |
| `--batch-size` | Records per batch (default varies by source) | No |
| `--tables` | Comma-separated list of tables to sync | No |
| `--exclude-tables` | Comma-separated list of tables to exclude | No |

---

## Source-Specific Guides

### MongoDB

MongoDB synchronization uses change streams for incremental updates, which requires a replica set or sharded cluster.

**Prerequisites:**
- MongoDB 3.6+ with replica set enabled
- Read access to the source database
- Change stream access for incremental sync

**Full Sync:**

```bash
surreal-sync from mongodb full \
  --connection-string "mongodb://user:pass@host:27017/mydb?replicaSet=rs0" \
  --surreal-endpoint "http://localhost:8000" \
  --surreal-username root \
  --surreal-password root \
  --to-namespace production \
  --to-database app
```

**Incremental Sync (Change Streams):**

```bash
surreal-sync from mongodb watch \
  --connection-string "mongodb://user:pass@host:27017/mydb?replicaSet=rs0" \
  --surreal-endpoint "http://localhost:8000" \
  --surreal-username root \
  --surreal-password root \
  --to-namespace production \
  --to-database app
```

**Data Mapping:**
- MongoDB collections map to SurrealDB tables
- BSON `ObjectId` maps to SurrealDB string IDs
- Nested documents are preserved as SurrealDB objects
- Arrays are preserved as SurrealDB arrays
- BSON types (Date, Decimal128, etc.) are converted to appropriate SurrealQL types

**Example Schema Mapping:**

```
MongoDB                          SurrealDB
------                           ---------
db.users (collection)     ->     users (table)
_id: ObjectId("abc123")   ->     users:abc123 (record ID)
{ name: "Alice",          ->     { name: "Alice",
  address: {              ->       address: {
    city: "NYC"           ->         city: "NYC"
  },                      ->       },
  tags: ["admin"]         ->       tags: ["admin"]
}                         ->     }
```

### PostgreSQL (Trigger-Based CDC)

Trigger-based CDC installs database triggers on source tables to capture INSERT, UPDATE, and DELETE operations.

**Prerequisites:**
- PostgreSQL 10+
- Permission to create triggers and tables on the source database
- Surreal-sync will create a CDC tracking table

**Setup:**

```bash
# Install triggers on specified tables
surreal-sync from postgres-triggers setup \
  --connection-string "postgresql://user:pass@host:5432/mydb" \
  --tables "users,orders,products"
```

**Full Sync:**

```bash
surreal-sync from postgres-triggers full \
  --connection-string "postgresql://user:pass@host:5432/mydb" \
  --surreal-endpoint "http://localhost:8000" \
  --surreal-username root \
  --surreal-password root \
  --to-namespace production \
  --to-database app
```

**Incremental Sync:**

```bash
surreal-sync from postgres-triggers watch \
  --connection-string "postgresql://user:pass@host:5432/mydb" \
  --surreal-endpoint "http://localhost:8000" \
  --surreal-username root \
  --surreal-password root \
  --to-namespace production \
  --to-database app
```

### PostgreSQL (wal2json)

Logical replication with wal2json provides CDC without modifying the source database schema (no triggers needed).

**Prerequisites:**
- PostgreSQL 9.4+ with `wal2json` extension installed
- `wal_level = logical` in postgresql.conf
- Replication slot permissions

**Configure PostgreSQL:**

```sql
-- postgresql.conf
-- wal_level = logical
-- max_replication_slots = 4
-- max_wal_senders = 4

-- Create a replication slot
SELECT pg_create_logical_replication_slot('surreal_sync', 'wal2json');
```

**Sync:**

```bash
surreal-sync from postgres-wal full \
  --connection-string "postgresql://user:pass@host:5432/mydb" \
  --replication-slot "surreal_sync" \
  --surreal-endpoint "http://localhost:8000" \
  --surreal-username root \
  --surreal-password root \
  --to-namespace production \
  --to-database app

surreal-sync from postgres-wal watch \
  --connection-string "postgresql://user:pass@host:5432/mydb" \
  --replication-slot "surreal_sync" \
  --surreal-endpoint "http://localhost:8000" \
  --surreal-username root \
  --surreal-password root \
  --to-namespace production \
  --to-database app
```

### MySQL

MySQL synchronization uses trigger-based CDC with sequence checkpoints for incremental tracking.

**Prerequisites:**
- MySQL 5.7+
- Permission to create triggers and tables
- Surreal-sync will create CDC tracking tables

**Setup:**

```bash
surreal-sync from mysql setup \
  --connection-string "mysql://user:pass@host:3306/mydb" \
  --tables "users,orders,products"
```

**Full Sync:**

```bash
surreal-sync from mysql full \
  --connection-string "mysql://user:pass@host:3306/mydb" \
  --surreal-endpoint "http://localhost:8000" \
  --surreal-username root \
  --surreal-password root \
  --to-namespace production \
  --to-database app
```

**Incremental Sync:**

```bash
surreal-sync from mysql watch \
  --connection-string "mysql://user:pass@host:3306/mydb" \
  --surreal-endpoint "http://localhost:8000" \
  --surreal-username root \
  --surreal-password root \
  --to-namespace production \
  --to-database app
```

### Neo4j

Neo4j synchronization maps nodes and relationships to SurrealDB records and edges.

**Prerequisites:**
- Neo4j 4.0+
- Read access to the source database
- Nodes should have a timestamp property for incremental sync

**Full Sync:**

```bash
surreal-sync from neo4j full \
  --connection-string "bolt://user:pass@host:7687" \
  --surreal-endpoint "http://localhost:8000" \
  --surreal-username root \
  --surreal-password root \
  --to-namespace production \
  --to-database app
```

**Incremental Sync:**

```bash
surreal-sync from neo4j watch \
  --connection-string "bolt://user:pass@host:7687" \
  --timestamp-field "updatedAt" \
  --surreal-endpoint "http://localhost:8000" \
  --surreal-username root \
  --surreal-password root \
  --to-namespace production \
  --to-database app
```

**Data Mapping:**

```
Neo4j                            SurrealDB
-----                            ---------
(:Person {name: "Alice"})  ->    person:xxx { name: "Alice" }
(:Company {name: "Acme"})  ->    company:xxx { name: "Acme" }
-[:WORKS_AT {since: 2020}]->    works_at:xxx { since: 2020, in: person:xxx, out: company:xxx }
```

- Neo4j node labels map to SurrealDB table names (lowercased)
- Neo4j relationship types map to SurrealDB edge table names (lowercased)
- Properties are preserved
- Graph structure is maintained through SurrealDB's graph edge model

### JSONL (JSON Lines)

Bulk import from JSON Lines files.

```bash
surreal-sync from jsonl import \
  --file /path/to/data.jsonl \
  --table "my_table" \
  --surreal-endpoint "http://localhost:8000" \
  --surreal-username root \
  --surreal-password root \
  --to-namespace production \
  --to-database app \
  --batch-size 1000
```

**JSONL Format:**

Each line is a complete JSON object:

```json
{"name": "Alice", "age": 30, "email": "alice@example.com"}
{"name": "Bob", "age": 25, "email": "bob@example.com"}
{"name": "Charlie", "age": 35, "email": "charlie@example.com"}
```

### Kafka

Streaming sync from Kafka topics with deduplication support.

**Prerequisites:**
- Kafka 2.0+
- Topic must contain JSON messages
- Consumer group permissions

```bash
surreal-sync from kafka subscribe \
  --brokers "broker1:9092,broker2:9092" \
  --topic "events" \
  --group-id "surreal-sync-group" \
  --table "events" \
  --surreal-endpoint "http://localhost:8000" \
  --surreal-username root \
  --surreal-password root \
  --to-namespace production \
  --to-database app
```

**Deduplication:**

Surreal-sync tracks Kafka message offsets and can use a configurable deduplication key to prevent duplicate records:

```bash
surreal-sync from kafka subscribe \
  --brokers "broker1:9092" \
  --topic "events" \
  --group-id "surreal-sync-group" \
  --table "events" \
  --dedup-key "event_id" \
  --surreal-endpoint "http://localhost:8000" \
  --surreal-username root \
  --surreal-password root \
  --to-namespace production \
  --to-database app
```

---

## Schema Mapping Strategies

### Automatic Table Creation

By default, Surreal-sync creates tables automatically based on the source schema. Tables are created in the target namespace and database as needed during sync.

### Field Type Mapping

| Source Type | SurrealDB Type |
|-------------|---------------|
| String/VARCHAR/TEXT | `string` |
| Integer/INT/BIGINT | `int` |
| Float/DOUBLE/DECIMAL | `float` or `decimal` |
| Boolean | `bool` |
| Date/DateTime/Timestamp | `datetime` |
| JSON/JSONB | `object` |
| Array | `array` |
| Binary/BLOB | `bytes` |
| NULL | `NONE` |
| UUID | `string` |

### Relationship Preservation

Surreal-sync attempts to preserve relationships from the source:
- Foreign keys in SQL databases become record links in SurrealDB
- Neo4j relationships become graph edges
- MongoDB document references (DBRef) are converted to record links where detectable

### Index Recreation

Primary keys and unique indexes from the source database are recreated as SurrealDB indexes. Non-unique indexes are created based on a best-effort mapping.

---

## Best Practices

### Test Migrations with a Subset

Always test with a limited dataset before running a full migration:

```bash
surreal-sync from postgres-triggers full \
  --connection-string "postgresql://user:pass@host:5432/mydb" \
  --tables "users" \
  --batch-size 100 \
  --limit 1000 \
  --surreal-endpoint "http://localhost:8000" \
  --surreal-username root \
  --surreal-password root \
  --to-namespace staging \
  --to-database migration_test
```

### Monitor CDC Lag

For incremental sync, monitor the lag between the source database and SurrealDB:

- Check the sync checkpoint position against the source's current position
- Set up alerts if lag exceeds acceptable thresholds
- For Kafka, monitor consumer group lag using standard Kafka tools

### Handle Schema Drift

When the source schema changes during continuous sync:

- New columns/fields are automatically added to SurrealDB records
- Removed columns result in the field being absent from new records (old records retain it)
- Type changes may require manual intervention; monitor sync logs for type conversion errors

### Plan for Cutover

For production migrations with minimal downtime:

1. Run full sync to establish baseline data in SurrealDB.
2. Start incremental sync to capture changes during migration.
3. Monitor lag until incremental sync is caught up.
4. Pause writes to the source database.
5. Wait for final incremental sync to complete.
6. Switch application connections to SurrealDB.
7. Resume normal operations.

### Rollback Strategies

- Keep the source database running during migration (do not decommission immediately)
- Export the SurrealDB data after migration as a checkpoint
- If issues are found, switch application connections back to the source
- For incremental sync, the source database remains the authoritative copy until cutover
