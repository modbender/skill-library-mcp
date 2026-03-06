---
name: mongo-db
description: Interact with a MongoDB database for persistent document storage. Supports full CRUD operations (find, insert, update, delete), aggregation pipelines, collection management, and index creation. Use when any agent needs to store or retrieve data in MongoDB — for example, persisting financial records, budgets, watchlists, or any structured data across sessions.
metadata: {"openclaw": {"requires": {"bins": ["python3"]}, "emoji": "🍃"}}
---

# MongoDB — Document Storage Skill

Use this skill whenever an agent needs to read or write persistent data to MongoDB. All operations are performed via a Python CLI script and return JSON output.

## When to use

- User asks to "save to the database", "store this in Mongo", "retrieve from MongoDB"
- An agent needs to persist data across sessions (budgets, transactions, summaries, watchlists)
- An agent needs to query, filter, or aggregate stored records
- A new collection or schema (validator) needs to be set up

---

## Setup (first run only)

**Local MongoDB:** If you need to install MongoDB on Ubuntu, see [INSTALL-UBUNTU.md](INSTALL-UBUNTU.md). For Atlas, use your connection string in config or env.

Run the setup script once from the workspace root to create a virtual environment and install `pymongo`:

```bash
bash skills/mongo-db/scripts/setup.sh
```

This creates `skills/mongo-db/scripts/.venv/` and installs dependencies there. After setup, invoke the client using the venv interpreter:

```bash
skills/mongo-db/scripts/.venv/bin/python3 skills/mongo-db/scripts/mongo_client.py '<json>'
```

---

## Configuration

Connection is resolved in this order (first match wins):

### Option 1 — Environment variable (recommended)
```
MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/mydb
MONGO_DB=mydb   # optional if the db is in the URI
```

### Option 2 — config.json (local file, gitignored)

Copy the example and fill in your values:
```bash
cp skills/mongo-db/config.example.json skills/mongo-db/config.json
```

Edit `skills/mongo-db/config.json`:
```json
{
  "uri": "mongodb://localhost:27017",
  "database": "mydb",
  "username": "optional",
  "password": "optional"
}
```

### Option 3 — Individual env vars
```
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_USER=myuser
MONGO_PASSWORD=mypassword
MONGO_DB=mydb
```

---

## CLI interface

All operations use a single JSON payload argument:

```bash
PYTHON=skills/mongo-db/scripts/.venv/bin/python3
$PYTHON skills/mongo-db/scripts/mongo_client.py '<json_payload>'
```

Payload schema:
```json
{
  "operation": "<op>",
  "database": "<optional override>",
  "collection": "<collection name>",
  ...operation-specific fields
}
```

Output is always JSON: `{"success": true, ...result_fields}` or `{"success": false, "error": "..."}`.

---

## Operations Reference

### List databases
```json
{"operation": "list_databases"}
```

### List collections in a database
```json
{"operation": "list_collections", "database": "mydb"}
```

### Create a collection (with optional JSON Schema validator)
```json
{
  "operation": "create_collection",
  "database": "mydb",
  "collection": "budgets",
  "validator": {
    "$jsonSchema": {
      "bsonType": "object",
      "required": ["period", "income"],
      "properties": {
        "period": {"bsonType": "string"},
        "income": {"bsonType": "number"}
      }
    }
  }
}
```

### Drop a collection
Always confirm with the user before dropping. Requires `"confirm": true`.
```json
{"operation": "drop_collection", "database": "mydb", "collection": "old_data", "confirm": true}
```

### Create an index
```json
{
  "operation": "create_index",
  "database": "mydb",
  "collection": "transactions",
  "keys": {"date": 1, "category": 1},
  "unique": false
}
```

---

### Find documents
```json
{
  "operation": "find",
  "database": "mydb",
  "collection": "transactions",
  "filter": {"category": "groceries"},
  "projection": {"_id": 0, "date": 1, "amount": 1, "description": 1},
  "sort": {"date": -1},
  "limit": 20
}
```

### Find one document
```json
{
  "operation": "find_one",
  "database": "mydb",
  "collection": "transactions",
  "filter": {"id": "txn_20260131_0001"}
}
```

### Count documents
```json
{
  "operation": "count",
  "database": "mydb",
  "collection": "transactions",
  "filter": {"type": "expense"}
}
```

---

### Insert one document
```json
{
  "operation": "insert_one",
  "database": "mydb",
  "collection": "transactions",
  "document": {
    "id": "txn_20260201_0001",
    "date": "2026-02-01",
    "description": "Supermarket",
    "amount": -85.50,
    "category": "groceries",
    "type": "expense"
  }
}
```

### Insert many documents
```json
{
  "operation": "insert_many",
  "database": "mydb",
  "collection": "transactions",
  "documents": [
    {"date": "2026-02-01", "description": "Coffee", "amount": -4.50, "category": "dining"},
    {"date": "2026-02-02", "description": "Salary", "amount": 5000, "category": "income"}
  ]
}
```

---

### Update one document
```json
{
  "operation": "update_one",
  "database": "mydb",
  "collection": "budget",
  "filter": {"period": "monthly"},
  "update": {"$set": {"income": 5500, "last_updated": "2026-02-01"}},
  "upsert": false
}
```

### Update many documents
```json
{
  "operation": "update_many",
  "database": "mydb",
  "collection": "transactions",
  "filter": {"category": "food"},
  "update": {"$set": {"category": "groceries"}}
}
```

### Replace one document
```json
{
  "operation": "replace_one",
  "database": "mydb",
  "collection": "budget",
  "filter": {"period": "monthly"},
  "replacement": {"period": "monthly", "income": 5500, "currency": "USD"},
  "upsert": true
}
```

---

### Delete one document
Always confirm with the user before deleting. Requires `"confirm": true`.
```json
{
  "operation": "delete_one",
  "database": "mydb",
  "collection": "transactions",
  "filter": {"id": "txn_20260131_0001"},
  "confirm": true
}
```

### Delete many documents
Always confirm with the user before deleting. Requires `"confirm": true`.
```json
{
  "operation": "delete_many",
  "database": "mydb",
  "collection": "transactions",
  "filter": {"source_file": "january_statement.pdf"},
  "confirm": true
}
```

---

### Aggregate
```json
{
  "operation": "aggregate",
  "database": "mydb",
  "collection": "transactions",
  "pipeline": [
    {"$match": {"type": "expense"}},
    {"$group": {"_id": "$category", "total": {"$sum": "$amount"}, "count": {"$sum": 1}}},
    {"$sort": {"total": 1}}
  ]
}
```

---

## Notes

- **Destructive operations** (`delete_one`, `delete_many`, `drop_collection`) require `"confirm": true` in the payload. Always ask the user to confirm before including this flag.
- **ObjectId** fields are serialized as strings in all output.
- **Database override**: the `"database"` field in the payload overrides the default database from config/env for that single call.
- **Schema validation**: use `create_collection` with a `"validator"` to enforce document structure at the MongoDB level. This is the recommended approach for agents that write structured data (e.g. the finance-budget agent's budget and transaction collections).
- **Upsert pattern**: for config-like documents (one per type), use `replace_one` with `"upsert": true` to create-or-replace atomically.
- If `pymongo` is missing, re-run `bash skills/mongo-db/scripts/setup.sh`.
