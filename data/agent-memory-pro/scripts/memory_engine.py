#!/usr/bin/env python3
"""
AgxntSix Memory Engine — Mem0-powered unified memory with Qdrant + Neo4j + Langfuse tracing

Usage:
  memory_engine.py add <text> [--user agxntsix] [--agent agxntsix]
  memory_engine.py search <query> [--user agxntsix] [--limit 5]
  memory_engine.py history [--user agxntsix] [--limit 10]
  memory_engine.py get-all [--user agxntsix]
  memory_engine.py delete <memory_id>
  memory_engine.py stats
  memory_engine.py test
"""
import argparse
import json
import os
import sys
from datetime import datetime

# Langfuse tracing
os.environ.setdefault("LANGFUSE_SECRET_KEY", "sk-lf-115cb6b4-7153-4fe6-9255-bf28f8b115de")
os.environ.setdefault("LANGFUSE_PUBLIC_KEY", "pk-lf-8a9322b9-5eb1-4e8b-815e-b3428dc69bc4")
os.environ.setdefault("LANGFUSE_HOST", "http://langfuse-web:3000")

try:
    from langfuse import observe, get_client
    TRACING = True
except ImportError:
    TRACING = False
    def observe(**kwargs):
        def decorator(fn):
            return fn
        return decorator

def get_session_id():
    return datetime.now().strftime("session-%Y%m%d-%H")

DEFAULT_USER_ID = "agxntsix"

def get_config():
    """Build Mem0 config from environment variables."""
    config = {
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "host": os.environ.get("QDRANT_HOST", "localhost"),
                "port": int(os.environ.get("QDRANT_PORT", "6333")),
            }
        },
        "graph_store": {
            "provider": "neo4j",
            "config": {
                "url": os.environ.get("NEO4J_URL", "bolt://localhost:7687"),
                "username": os.environ.get("NEO4J_USERNAME", "neo4j"),
                "password": os.environ.get("NEO4J_PASSWORD", "agxntsix2026"),
            }
        },
        "version": "v1.1"
    }
    
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    if openrouter_key:
        # Use Langfuse OpenAI drop-in proxy for traced LLM calls
        try:
            from langfuse.openai import OpenAI
            # Create a traced client — Mem0 doesn't accept a client object directly,
            # so we trace via the Langfuse SDK's @observe decorator on our wrapper functions
        except ImportError:
            pass

        config["llm"] = {
            "provider": "openai",
            "config": {
                "api_key": openrouter_key,
                "openai_base_url": "https://openrouter.ai/api/v1",
                "model": "google/gemini-2.0-flash-lite-001",
                "temperature": 0.1,
            }
        }
        config["embedder"] = {
            "provider": "openai",
            "config": {
                "api_key": openrouter_key,
                "openai_base_url": "https://openrouter.ai/api/v1",
                "model": "openai/text-embedding-3-small",
            }
        }
    elif os.environ.get("OPENAI_API_KEY"):
        config["llm"] = {
            "provider": "openai",
            "config": {
                "model": "gpt-4.1-nano",
                "temperature": 0.1,
            }
        }
    
    return config

def get_memory():
    from mem0 import Memory
    config = get_config()
    return Memory.from_config(config)

def _update_trace(operation, **kwargs):
    """Update current Langfuse trace with session/user info."""
    if not TRACING:
        return
    try:
        lf = get_client()
        lf.update_current_trace(
            session_id=get_session_id(),
            user_id=DEFAULT_USER_ID,
            tags=[f"memory-{operation}"],
            metadata=kwargs
        )
    except Exception:
        pass

@observe(name="memory-add")
def add_memory(args):
    _update_trace("add", text_length=len(args.text))
    memory = get_memory()
    messages = [{"role": "user", "content": args.text}]
    result = memory.add(messages, user_id=args.user, agent_id=args.agent)
    print(json.dumps(result, indent=2, default=str))

@observe(name="memory-search")
def search_memory(args):
    _update_trace("search", query=args.query, limit=args.limit)
    memory = get_memory()
    results = memory.search(args.query, user_id=args.user, limit=args.limit)
    print(json.dumps(results, indent=2, default=str))

@observe(name="memory-get-all")
def get_all(args):
    _update_trace("get-all")
    memory = get_memory()
    results = memory.get_all(user_id=args.user)
    print(json.dumps(results, indent=2, default=str))

@observe(name="memory-history")
def get_history(args):
    _update_trace("history")
    memory = get_memory()
    results = memory.history(user_id=args.user, limit=args.limit)
    print(json.dumps(results, indent=2, default=str))

@observe(name="memory-delete")
def delete_memory(args):
    _update_trace("delete", memory_id=args.memory_id)
    memory = get_memory()
    memory.delete(args.memory_id)
    print(json.dumps({"status": "deleted", "id": args.memory_id}))

def stats(args):
    memory = get_memory()
    all_memories = memory.get_all()
    print(json.dumps({
        "total_memories": len(all_memories.get("results", [])),
        "qdrant_host": os.environ.get("QDRANT_HOST", "localhost"),
        "neo4j_url": os.environ.get("NEO4J_URL", "bolt://localhost:7687"),
    }, indent=2))

def test_connections(args):
    results = {}
    
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(
            host=os.environ.get("QDRANT_HOST", "localhost"),
            port=int(os.environ.get("QDRANT_PORT", "6333"))
        )
        collections = client.get_collections()
        results["qdrant"] = {"status": "connected", "collections": len(collections.collections)}
    except Exception as e:
        results["qdrant"] = {"status": "error", "error": str(e)}
    
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(
            os.environ.get("NEO4J_URL", "bolt://localhost:7687"),
            auth=(
                os.environ.get("NEO4J_USERNAME", "neo4j"),
                os.environ.get("NEO4J_PASSWORD", "agxntsix2026")
            )
        )
        with driver.session() as session:
            result = session.run("RETURN 1 AS test")
            result.single()
        driver.close()
        results["neo4j"] = {"status": "connected"}
    except Exception as e:
        results["neo4j"] = {"status": "error", "error": str(e)}
    
    try:
        import sqlite3
        conn = sqlite3.connect(":memory:")
        conn.execute("SELECT 1")
        conn.close()
        results["sqlite"] = {"status": "connected"}
    except Exception as e:
        results["sqlite"] = {"status": "error", "error": str(e)}
    
    # Test Langfuse
    if TRACING:
        try:
            lf = get_client()
            results["langfuse"] = {"status": "connected", "session_id": get_session_id()}
        except Exception as e:
            results["langfuse"] = {"status": "error", "error": str(e)}
    
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AgxntSix Memory Engine (Mem0)")
    sub = parser.add_subparsers(dest="command")
    
    a = sub.add_parser("add")
    a.add_argument("text")
    a.add_argument("--user", default="agxntsix")
    a.add_argument("--agent", default="agxntsix")
    
    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("--user", default="agxntsix")
    s.add_argument("--limit", type=int, default=5)
    
    g = sub.add_parser("get-all")
    g.add_argument("--user", default="agxntsix")
    
    h = sub.add_parser("history")
    h.add_argument("--user", default="agxntsix")
    h.add_argument("--limit", type=int, default=10)
    
    d = sub.add_parser("delete")
    d.add_argument("memory_id")
    
    sub.add_parser("stats")
    sub.add_parser("test")
    
    args = parser.parse_args()
    commands = {
        "add": add_memory, "search": search_memory, "get-all": get_all,
        "history": get_history, "delete": delete_memory, "stats": stats,
        "test": test_connections
    }
    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()
    
    if TRACING:
        try:
            get_client().flush()
        except:
            pass
