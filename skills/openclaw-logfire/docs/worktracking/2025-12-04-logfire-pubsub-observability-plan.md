# Logfire Observability Enhancement Plan for Pub/Sub Architecture

**Date:** 2025-12-04
**Linear Issue:** To be created (related to ULT-288, ULT-337)
**Status:** DRAFT - Awaiting Review

---

## Executive Summary

The new Multiplexed Event Bus architecture (ULT-337 Phases 1-4) introduces Redis Pub/Sub for real-time event streaming. While our core infrastructure (FastAPI, Temporal, Pydantic AI) is well-instrumented with Logfire, the **pub/sub event flow has zero observability**. This creates a blind spot in our trace chains.

---

## Current State Analysis

### What IS Instrumented (Working Well)

| Component | Instrumentation | Service Name |
|-----------|-----------------|--------------|
| FastAPI endpoints | `logfire.instrument_fastapi()` | `marketing-agent-api` |
| Pydantic AI agents | `logfire.instrument_pydantic_ai(version=3)` | `marketing-agent-*` |
| HTTP clients | `logfire.instrument_httpx(capture_all=True)` | `marketing-agent-*` |
| SQLAlchemy | `logfire.instrument_sqlalchemy(engine)` | `marketing-agent-api` |
| Temporal workflows | `LogfirePlugin` (ULT-332) | `marketing-agent-worker` |
| LiteLLM calls | Via httpx instrumentation | `marketing-agent-*` |

### What is NOT Instrumented (Gaps)

| Component | Current State | Impact |
|-----------|---------------|--------|
| **Redis Pub/Sub publish** | No spans in `publish_event_activity` | Cannot trace event publishing latency or failures |
| **Redis Pub/Sub subscribe** | No spans in `_event_generator` | SSE subscriptions invisible in traces |
| **SSE connections** | No spans in `/events/stream` | Cannot monitor connection lifecycle |
| **Qdrant operations** | Not instrumented | Vector storage latency invisible |
| **State recovery endpoints** | Spans exist but minimal attributes | Missing workflow_id, agent_type context |

---

## Proposed Solution

### Phase 1: Core Pub/Sub Instrumentation (Priority: HIGH)

Add Logfire spans to the critical paths in our event bus:

#### 1.1 Instrument `publish_event_activity`

**File:** `apps/marketing-agent/backend/app/activities/event_activities.py`

```python
import logfire

@activity.defn
async def publish_event_activity(
    user_id: str,
    agent_id: str,
    agent_type: str,
    event_type: str,
    payload: dict[str, object],
) -> bool:
    """Publish an agent event to the user's event channel."""
    channel = f"user:{user_id}:events"

    with logfire.span(
        "redis:publish_event",
        user_id=user_id,
        agent_id=agent_id,
        agent_type=agent_type,
        event_type=event_type,
        channel=channel,
    ) as span:
        # ... existing code ...

        num_subscribers = await redis.publish(channel, event.model_dump_json())

        # Add result attributes
        span.set_attribute("subscribers", num_subscribers)
        span.set_attribute("success", True)

        return True
```

**Benefit:** Every event published will appear in Logfire as a child span of the workflow, with:
- `user_id`, `agent_id`, `agent_type` for filtering
- `subscribers` count to detect when no SSE clients are connected
- Timing data for publish latency

#### 1.2 Instrument SSE Event Generator

**File:** `apps/marketing-agent/backend/app/routers/events.py`

```python
import logfire

async def _event_generator(user_id: str) -> AsyncGenerator[dict[str, str], None]:
    channel = f"user:{user_id}:events"

    with logfire.span(
        "sse:connection",
        user_id=user_id,
        channel=channel,
    ) as connection_span:
        # ... Redis connect and subscribe ...

        connection_span.set_attribute("status", "subscribed")

        while True:
            # Each message received gets its own span
            if message is not None and message["type"] == "message":
                with logfire.span(
                    "sse:event_received",
                    user_id=user_id,
                    channel=channel,
                ) as event_span:
                    # Parse and log event metadata
                    event_data = json.loads(message["data"])
                    event_span.set_attribute("agent_id", event_data.get("agent_id"))
                    event_span.set_attribute("event_type", event_data.get("type"))

                    yield {"event": "agent_event", "data": message["data"]}
```

**Benefit:** Complete visibility into:
- SSE connection lifecycle (connect/disconnect)
- Events received per connection
- Latency from Redis → SSE yield

#### 1.3 Add SSE Endpoint Span

**File:** `apps/marketing-agent/backend/app/routers/events.py`

```python
@router.get("/stream")
async def stream_events(
    user_id: str = Query(..., description="User ID for event channel subscription"),
) -> EventSourceResponse:
    with logfire.span(
        "api:sse_stream",
        user_id=user_id,
    ):
        return EventSourceResponse(
            _event_generator(user_id),
            media_type="text/event-stream",
        )
```

**Note:** The span will be short-lived (just the response setup), but the generator spans inside will show the full connection duration.

### Phase 2: Enable Redis Auto-Instrumentation (Priority: MEDIUM)

Add Logfire's built-in Redis instrumentation for all Redis operations:

**File:** `apps/marketing-agent/backend/app/main.py`

```python
# Add to existing Logfire configuration
logfire.instrument_redis(
    capture_statement=False,  # Don't capture commands (may contain sensitive data)
)
```

**Benefit:** All Redis operations (GET, SET, PUBLISH, SUBSCRIBE) will automatically get spans without manual instrumentation.

### Phase 3: Qdrant Instrumentation (Priority: MEDIUM)

Add custom spans for vector operations since there's no built-in Qdrant instrumentation:

**File:** `apps/marketing-agent/backend/app/qdrant_repository.py`

```python
import logfire

async def upsert_point(self, collection: str, point: models.PointStruct) -> str:
    with logfire.span(
        "qdrant:upsert",
        collection=collection,
        point_id=str(point.id),
    ) as span:
        result = await self.client.upsert(collection, [point])
        span.set_attribute("status", result.status)
        return str(point.id)

async def search(self, collection: str, vector: list[float], limit: int = 10):
    with logfire.span(
        "qdrant:search",
        collection=collection,
        limit=limit,
    ) as span:
        results = await self.client.search(collection, vector, limit=limit)
        span.set_attribute("results_count", len(results))
        return results
```

### Phase 4: Enhanced State Recovery Spans (Priority: LOW)

Improve the spans in the new state recovery endpoints (ULT-341):

**File:** `apps/marketing-agent/backend/app/routers/agents.py`

Current spans have minimal context. Enhance with:
- `workflow_count` on `/agents/active`
- `workflow_status` on `/agents/{workflow_id}/state`
- Query timing for Temporal operations

---

## Implementation Order

| Phase | Description | Effort | Impact |
|-------|-------------|--------|--------|
| **1.1** | Instrument publish_event_activity | 30 min | HIGH - Core visibility |
| **1.2** | Instrument SSE event generator | 45 min | HIGH - Connection visibility |
| **1.3** | SSE endpoint span | 15 min | MEDIUM - Entry point |
| **2** | Enable logfire.instrument_redis() | 10 min | MEDIUM - Auto coverage |
| **3** | Qdrant custom spans | 1 hour | MEDIUM - Vector ops visibility |
| **4** | State recovery enhancements | 30 min | LOW - Polish |

**Total Estimated Effort:** ~3 hours

---

## Expected Trace Flow After Implementation

```text
HTTP Request: POST /v1/search/query
└── api:initiate_web_search (FastAPI span)
    └── temporal:start_workflow
        └── SearchWorkflow.run (Temporal span)
            ├── search_agent:run (Pydantic AI span)
            │   └── POST litellm.svc (httpx span)
            ├── redis:publish_event [NEW] (event_type="searching")
            │   └── subscribers=1
            ├── redis:publish_event [NEW] (event_type="candidates_found")
            │   └── subscribers=1
            └── redis:publish_event [NEW] (event_type="completed")
                └── subscribers=1

SSE Connection: GET /events/stream
└── sse:connection [NEW] (user_id="dev-user")
    ├── sse:event_received [NEW] (agent_id="search-abc", event_type="searching")
    ├── sse:event_received [NEW] (agent_id="search-abc", event_type="candidates_found")
    └── sse:event_received [NEW] (agent_id="search-abc", event_type="completed")
```

---

## Metrics & Alerts (Future Enhancement)

Once instrumentation is in place, we can set up:

1. **Event publish latency** - Alert if Redis publish > 100ms
2. **SSE connection count** - Track concurrent connections
3. **Zero subscribers** - Alert when events published with 0 listeners
4. **Event throughput** - Events/second per user

---

## Questions for Review

1. **Capture statements?** Should we enable `capture_statement=True` for Redis pub/sub? Events are already logged, but this would add command details to spans.

2. **Qdrant priority?** Is vector operation visibility important for this iteration, or defer to Phase 5?

3. **Frontend Logfire?** Should we add browser-side Logfire traces via the existing `/v1/client-traces` proxy endpoint?

4. **Alert thresholds?** What latency thresholds should trigger alerts for pub/sub operations?

---

## References

- [Logfire Redis Documentation](https://logfire.pydantic.dev/docs/integrations/databases/redis/)
- [Logfire Custom Spans](https://logfire.pydantic.dev/docs/reference/api/logfire/)
- [ULT-332: Fix Logfire trace grouping](https://linear.app/ultrathink-solutions/issue/ULT-332)
- [ULT-337: Multiplexed Event Bus Architecture](https://linear.app/ultrathink-solutions/issue/ULT-337)
- [ULT-288: Complete observability instrumentation](https://linear.app/ultrathink-solutions/issue/ULT-288)
