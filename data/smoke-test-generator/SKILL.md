---
name: smoke-test-generator
description: Generate comprehensive API smoke test suites — categorised tests for auth, CRUD, integrations, cached vs live endpoints, with summary reporting. Use when validating API deployments, CI smoke checks, or pre-demo verification. Works with any HTTP API.
version: 1.0.0
metadata:
  {
      "openclaw": {
            "emoji": "\ud83e\uddea",
            "requires": {
                  "bins": [],
                  "env": []
            },
            "primaryEnv": null,
            "network": {
                  "outbound": true,
                  "reason": "Sends HTTP requests to the API under test (typically localhost). No external service calls."
            }
      }
}
---

# Smoke Test Generator

A structured pattern for API smoke testing with categorised test suites and summary reporting. Adapted from a production test suite that verified 34 endpoints across auth, CRUD, cached audio, story generation, ElevenLabs, and Mistral agent APIs.

## Test Categories

| Category | What It Tests | Fail = |
|---|---|---|
| Auth | Login, token validation, protected routes | Nothing else works |
| CRUD | Create, read, update, delete operations | Data layer broken |
| Cached | Pre-cached content serves correctly | Demo will fail |
| Live | Real API calls complete successfully | External dependency down |
| Integration | End-to-end workflows across services | Pipeline broken |

## Pattern

```python
import httpx
import asyncio

BASE_URL = "http://localhost:8000"
results = {"pass": 0, "fail": 0, "skip": 0}

async def test(name: str, category: str, fn):
    try:
        await fn()
        results["pass"] += 1
        print(f"  ✅ [{category}] {name}")
    except Exception as e:
        results["fail"] += 1
        print(f"  ❌ [{category}] {name}: {e}")

async def run_smoke_tests():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as client:
        # Auth
        await test("Login with valid creds", "auth",
            lambda: assert_status(client.post("/login", json={"email": "test@test.com", "password": "test"}), 200))
        
        # CRUD
        await test("Create item", "crud",
            lambda: assert_status(client.post("/api/items", json={"name": "test"}), 201))
        
        # Cached
        await test("Cached content returns 200", "cached",
            lambda: assert_status(client.get("/api/cached/1"), 200))
        
        # Integration
        await test("Full pipeline completes", "integration",
            lambda: assert_status(client.post("/api/pipeline", json={...}), 200))
    
    total = results["pass"] + results["fail"]
    print(f"\n{'='*40}")
    print(f"Results: {results['pass']}/{total} passed")
    if results["fail"] > 0:
        print(f"⚠️ {results['fail']} failures — do not demo!")
```

## Files

- `scripts/smoke_test.py` — Example smoke test suite with all categories
