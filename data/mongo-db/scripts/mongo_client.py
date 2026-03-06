#!/usr/bin/env python3
"""
MongoDB CLI client for the mongo-db OpenClaw skill.

Usage:
    python3 mongo_client.py '<json_payload>'

The JSON payload must include "operation" and (for most ops) "collection".
All output is JSON written to stdout. Errors are JSON on stderr with exit code 1.

Connection resolution order:
  1. MONGO_URI env var  (full connection string)
  2. skills/mongo-db/config.json  (relative to workspace root or SKILL_DIR)
  3. Individual env vars: MONGO_HOST, MONGO_PORT, MONGO_USER, MONGO_PASSWORD, MONGO_DB
"""

import json
import os
import sys
from pathlib import Path
from typing import Any


def _find_config_path() -> Path | None:
    """Search for config.json starting from the script directory up to workspace root."""
    candidates = [
        Path(__file__).parent.parent / "config.json",
        Path.cwd() / "skills" / "mongo-db" / "config.json",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def _build_uri_from_parts() -> str:
    host = os.environ.get("MONGO_HOST", "localhost")
    port = os.environ.get("MONGO_PORT", "27017")
    user = os.environ.get("MONGO_USER", "")
    password = os.environ.get("MONGO_PASSWORD", "")
    if user and password:
        return f"mongodb://{user}:{password}@{host}:{port}"
    return f"mongodb://{host}:{port}"


def _resolve_connection() -> tuple[str, str]:
    """Returns (uri, default_database)."""
    uri = os.environ.get("MONGO_URI", "")
    database = os.environ.get("MONGO_DB", "")

    if uri:
        return uri, database

    config_path = _find_config_path()
    if config_path:
        with open(config_path) as f:
            cfg = json.load(f)
        uri = cfg.get("uri", "")
        if not uri:
            user = cfg.get("username", "") or cfg.get("user", "")
            password = cfg.get("password", "")
            host = cfg.get("host", "localhost")
            port = cfg.get("port", 27017)
            if user and password:
                uri = f"mongodb://{user}:{password}@{host}:{port}"
            else:
                uri = f"mongodb://{host}:{port}"
        database = database or cfg.get("database", "")
        return uri, database

    return _build_uri_from_parts(), database


def _error(msg: str, **extra: Any) -> None:
    print(json.dumps({"success": False, "error": msg, **extra}), file=sys.stderr)
    sys.exit(1)


def _success(data: Any) -> None:
    print(json.dumps(data, default=str))


def _get_collection(db, name: str):
    if not name:
        _error("'collection' field is required for this operation")
    return db[name]


def _serialize_doc(doc: Any) -> Any:
    """Recursively convert non-JSON-serializable types (ObjectId, datetime) to strings."""
    if doc is None:
        return None
    if isinstance(doc, dict):
        return {k: _serialize_doc(v) for k, v in doc.items()}
    if isinstance(doc, list):
        return [_serialize_doc(i) for i in doc]
    try:
        json.dumps(doc)
        return doc
    except (TypeError, ValueError):
        return str(doc)


def run(payload: dict) -> None:
    try:
        from pymongo import MongoClient, ASCENDING, DESCENDING
        from pymongo.errors import PyMongoError
    except ImportError:
        _error(
            "pymongo is not installed. Run: bash skills/mongo-db/scripts/setup.sh",
            hint="or: pip install pymongo",
        )

    op = payload.get("operation", "").strip()
    if not op:
        _error("'operation' field is required")

    uri, default_db = _resolve_connection()
    if not uri:
        _error(
            "No MongoDB connection configured. Set MONGO_URI or create skills/mongo-db/config.json"
        )

    db_name = payload.get("database") or default_db
    collection_name = payload.get("collection", "")

    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        db = client[db_name] if db_name else None

        # ── Database-level operations ─────────────────────────────────────────

        if op == "list_databases":
            dbs = [d["name"] for d in client.list_databases()]
            return _success({"success": True, "databases": dbs})

        if op == "list_collections":
            if db is None:
                _error("'database' is required for list_collections")
            cols = db.list_collection_names()
            return _success({"success": True, "database": db_name, "collections": cols})

        if op == "create_collection":
            if db is None:
                _error("'database' is required for create_collection")
            if not collection_name:
                _error("'collection' is required for create_collection")
            kwargs: dict[str, Any] = {}
            validator = payload.get("validator")
            if validator:
                kwargs["validator"] = validator
            capped = payload.get("capped")
            if capped:
                kwargs["capped"] = True
                kwargs["size"] = payload.get("size", 10_000_000)
                if "max" in payload:
                    kwargs["max"] = payload["max"]
            db.create_collection(collection_name, **kwargs)
            return _success(
                {
                    "success": True,
                    "message": f"Collection '{collection_name}' created in '{db_name}'",
                }
            )

        if op == "drop_collection":
            if db is None:
                _error("'database' is required for drop_collection")
            if not collection_name:
                _error("'collection' is required for drop_collection")
            if not payload.get("confirm"):
                _error(
                    "drop_collection requires explicit confirmation",
                    hint="Add 'confirm': true to the payload after confirming with the user",
                )
            db.drop_collection(collection_name)
            return _success(
                {"success": True, "message": f"Collection '{collection_name}' dropped from '{db_name}'"}
            )

        if op == "create_index":
            if db is None:
                _error("'database' is required for create_index")
            col = _get_collection(db, collection_name)
            keys_raw = payload.get("keys")
            if not keys_raw:
                _error("'keys' is required for create_index — dict of {field: 1|-1} or [[field, order], ...]")
            if isinstance(keys_raw, dict):
                keys = list(keys_raw.items())
            else:
                keys = [(k, v) for k, v in keys_raw]
            index_opts: dict[str, Any] = {}
            for opt in ("unique", "sparse", "name", "expireAfterSeconds", "background"):
                if opt in payload:
                    index_opts[opt] = payload[opt]
            index_name = col.create_index(keys, **index_opts)
            return _success({"success": True, "index_name": index_name, "collection": collection_name})

        # ── Collection required from here ─────────────────────────────────────

        if db is None:
            _error("'database' is required for this operation")

        col = _get_collection(db, collection_name)

        if op == "count":
            filt = payload.get("filter", {})
            n = col.count_documents(filt)
            return _success({"success": True, "count": n, "filter": filt})

        if op == "find":
            filt = payload.get("filter", {})
            projection = payload.get("projection")
            limit = int(payload.get("limit", 0))
            sort_raw = payload.get("sort")
            cursor = col.find(filt, projection)
            if sort_raw:
                if isinstance(sort_raw, dict):
                    sort_list = [(k, v) for k, v in sort_raw.items()]
                else:
                    sort_list = [(k, v) for k, v in sort_raw]
                cursor = cursor.sort(sort_list)
            if limit:
                cursor = cursor.limit(limit)
            docs = [_serialize_doc(d) for d in cursor]
            return _success({"success": True, "count": len(docs), "documents": docs})

        if op == "find_one":
            filt = payload.get("filter", {})
            projection = payload.get("projection")
            doc = col.find_one(filt, projection)
            return _success({"success": True, "document": _serialize_doc(doc)})

        if op == "insert_one":
            document = payload.get("document")
            if document is None:
                _error("'document' is required for insert_one")
            result = col.insert_one(document)
            return _success(
                {"success": True, "inserted_id": str(result.inserted_id)}
            )

        if op == "insert_many":
            documents = payload.get("documents")
            if not documents:
                _error("'documents' (non-empty list) is required for insert_many")
            result = col.insert_many(documents)
            return _success(
                {
                    "success": True,
                    "inserted_count": len(result.inserted_ids),
                    "inserted_ids": [str(i) for i in result.inserted_ids],
                }
            )

        if op == "update_one":
            filt = payload.get("filter")
            update = payload.get("update")
            if filt is None or update is None:
                _error("'filter' and 'update' are required for update_one")
            upsert = payload.get("upsert", False)
            result = col.update_one(filt, update, upsert=upsert)
            return _success(
                {
                    "success": True,
                    "matched_count": result.matched_count,
                    "modified_count": result.modified_count,
                    "upserted_id": str(result.upserted_id) if result.upserted_id else None,
                }
            )

        if op == "update_many":
            filt = payload.get("filter")
            update = payload.get("update")
            if filt is None or update is None:
                _error("'filter' and 'update' are required for update_many")
            upsert = payload.get("upsert", False)
            result = col.update_many(filt, update, upsert=upsert)
            return _success(
                {
                    "success": True,
                    "matched_count": result.matched_count,
                    "modified_count": result.modified_count,
                    "upserted_id": str(result.upserted_id) if result.upserted_id else None,
                }
            )

        if op == "replace_one":
            filt = payload.get("filter")
            replacement = payload.get("replacement")
            if filt is None or replacement is None:
                _error("'filter' and 'replacement' are required for replace_one")
            upsert = payload.get("upsert", False)
            result = col.replace_one(filt, replacement, upsert=upsert)
            return _success(
                {
                    "success": True,
                    "matched_count": result.matched_count,
                    "modified_count": result.modified_count,
                    "upserted_id": str(result.upserted_id) if result.upserted_id else None,
                }
            )

        if op == "delete_one":
            filt = payload.get("filter")
            if filt is None:
                _error("'filter' is required for delete_one")
            if not payload.get("confirm"):
                _error(
                    "delete_one requires explicit confirmation",
                    hint="Add 'confirm': true after confirming the deletion with the user",
                )
            result = col.delete_one(filt)
            return _success({"success": True, "deleted_count": result.deleted_count})

        if op == "delete_many":
            filt = payload.get("filter")
            if filt is None:
                _error("'filter' is required for delete_many")
            if not payload.get("confirm"):
                _error(
                    "delete_many requires explicit confirmation",
                    hint="Add 'confirm': true after confirming the deletion with the user",
                )
            result = col.delete_many(filt)
            return _success({"success": True, "deleted_count": result.deleted_count})

        if op == "aggregate":
            pipeline = payload.get("pipeline")
            if not isinstance(pipeline, list):
                _error("'pipeline' (list of stage objects) is required for aggregate")
            docs = [_serialize_doc(d) for d in col.aggregate(pipeline)]
            return _success({"success": True, "count": len(docs), "documents": docs})

        _error(
            f"Unknown operation '{op}'",
            supported=[
                "list_databases", "list_collections", "create_collection", "drop_collection",
                "create_index", "count",
                "find", "find_one",
                "insert_one", "insert_many",
                "update_one", "update_many", "replace_one",
                "delete_one", "delete_many",
                "aggregate",
            ],
        )

    except Exception as exc:  # noqa: BLE001
        _error(str(exc), operation=op)


def main() -> None:
    if len(sys.argv) < 2:
        _error(
            "Usage: mongo_client.py '<json_payload>'",
            example='{"operation":"list_databases"}',
        )
    try:
        payload = json.loads(sys.argv[1])
    except json.JSONDecodeError as exc:
        _error(f"Invalid JSON payload: {exc}")

    run(payload)


if __name__ == "__main__":
    main()
