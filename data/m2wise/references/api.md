# M2Wise API Reference

## Core Classes

### M2Wise

Main engine class for memory and wisdom management.

```python
from m2wise import M2Wise, M2WiseConfig
```

#### Constructor

```python
M2Wise(config: M2WiseConfig)
```

#### Methods

##### add()

Add conversation messages to memory.

```python
def add(
    self,
    messages: list[dict],
    user_id: str,
    session_id: str | None = None
) -> None
```

**Parameters:**
- `messages`: List of message dicts with `role` and `content`
- `user_id`: Unique user identifier
- `session_id`: Optional session identifier

**Example:**
```python
engine.add(
    [
        {"role": "user", "content": "I prefer concise answers"},
        {"role": "assistant", "content": "OK, I'll keep it brief."}
    ],
    user_id="alice",
    session_id="chat_001"
)
```

##### search()

Search memories and wisdom.

```python
def search(
    self,
    query: str,
    user_id: str,
    top_k: int = 10
) -> RetrievalBundle
```

**Parameters:**
- `query`: Search query string
- `user_id`: User identifier
- `top_k`: Number of results to return

**Returns:** `RetrievalBundle` with `.memories`, `.wisdom`, `.as_prompt()`

##### sleep()

Generate wisdom drafts (Sleep phase).

```python
def sleep(
    self,
    user_id: str,
    force: bool = False
) -> SleepReport
```

**Parameters:**
- `user_id`: User identifier
- `force`: Force regeneration even if recent

**Returns:** `SleepReport` with `.drafts_created`, `.memories_processed`

##### dream()

Verify and publish wisdom (Dream phase).

```python
def dream(
    self,
    user_id: str
) -> DreamReport
```

**Parameters:**
- `user_id`: User identifier

**Returns:** `DreamReport` with `.published`, `.updated`, `.conflicts_resolved`

##### forget()

Delete memory or wisdom.

```python
def forget(
    self,
    user_id: str,
    memory_id: str | None = None,
    wisdom_id: str | None = None
) -> None
```

##### list_wisdom()

List all wisdom for user.

```python
def list_wisdom(
    self,
    user_id: str,
    kind: str | None = None
) -> list[WisdomObject]
```

---

### M2WiseConfig

Configuration for M2Wise engine.

```python
from m2wise import M2WiseConfig
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data_dir` | str | "./data" | Storage directory |
| `embedder` | str | "openai" | Embedding provider |
| `embedder_model` | str | "text-embedding-3-small" | Embedding model |
| `vector_store` | str | "faiss" | Vector storage backend |
| `graph_store` | str | "networkx" | Graph storage backend |
| `similarity_threshold` | float | 0.7 | Retrieval threshold (0.0-1.0) |
| `max_memories` | int | 100 | Max memories to retrieve |
| `auto_sleep` | bool | False | Auto-trigger sleep after add |
| `auto_dream` | bool | False | Auto-trigger dream after sleep |
| `cache_enabled` | bool | True | Enable caching |
| `cache_ttl` | int | 3600 | Cache TTL in seconds |

---

### RetrievalBundle

Return type for search operations.

```python
bundle = engine.search("query", user_id="alice")
```

**Properties:**
- `memories`: List[MemoryRecord]
- `wisdom`: List[WisdomObject]
- `as_prompt()`: str - Convert to prompt string

---

### SleepReport

Return type for sleep operation.

```python
report = engine.sleep(user_id="alice")
```

**Properties:**
- `drafts_created`: int - Number of drafts created
- `memories_processed`: int - Memories processed

---

### DreamReport

Return type for dream operation.

```python
report = engine.dream(user_id="alice")
```

**Properties:**
- `published`: int - Number of wisdoms published
- `updated`: int - Number of wisdoms updated
- `conflicts_resolved`: int - Conflicts resolved
