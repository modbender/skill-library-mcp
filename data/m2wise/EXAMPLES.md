# M2Wise Examples

## Basic Examples

### Example 1: Minimal Setup

```python
from m2wise import M2Wise, M2WiseConfig

# Create engine
engine = M2Wise(config=M2WiseConfig())

# Add single message
engine.add([{"role": "user", "content": "I like coffee"}], user_id="bob")

# Search
bundle = engine.search("drinks", user_id="bob")
```

### Example 2: Full Workflow

```python
from m2wise import M2Wise, M2WiseConfig

engine = M2Wise(config=M2WiseConfig(data_dir="./data"))

# Add conversation history
conversations = [
    {"role": "user", "content": "I prefer short responses"},
    {"role": "assistant", "content": "Got it!"},
    {"role": "user", "content": "Don't use technical jargon"},
    {"role": "assistant", "content": "Understood"},
    {"role": "user", "content": "Examples help me learn"},
]
engine.add(conversations, user_id="alice")

# Generate wisdom
engine.sleep(user_id="alice")

# Publish wisdom
engine.dream(user_id="alice")

# List wisdom
for w in engine.list_wisdom(user_id="alice"):
    print(f"[{w.kind}] {w.statement}")
```

### Example 3: Using SDK

```python
from m2wise_sdk import M2WiseSDK

sdk = M2WiseSDK()

# Simple message addition
sdk.add_message("alice", "I'm a Python developer")
sdk.add_message("alice", "I work on backend")

# Get context for response generation
context = sdk.get_context("alice", "user is asking about APIs")

# Trigger wisdom
sdk.trigger_sleep("alice")
sdk.trigger_dream("alice")

# Get stats
stats = sdk.get_stats("alice")
print(f"Memory count: {stats['memory_count']}")
```

## Configuration Examples

### Example 4: SiliconFlow (Chinese Models)

```python
from m2wise import M2Wise, M2WiseConfig
import os

config = M2WiseConfig(
    data_dir="./data",
    embedder="siliconflow",
    embedder_model="BAAI/bge-large-zh-v1.5",
    vector_store="faiss",
    similarity_threshold=0.7,
)

os.environ["M2WISE_SILICONFLOW_API_KEY"] = "your-api-key"
engine = M2Wise(config=config)
```

### Example 5: PostgreSQL with pgvector

```python
from m2wise import M2Wise, M2WiseConfig

config = M2WiseConfig(
    data_dir="./data",
    embedder="openai",
    vector_store="postgres",
    # PostgreSQL connection
    db_host="localhost",
    db_port=5432,
    db_name="m2wise",
    db_user="user",
    db_password="password",
)

engine = M2Wise(config=config)
```

### Example 6: Custom Embedder

```python
from m2wise import M2Wise, M2WiseConfig
from m2wise.llm import LocalEmbedder

embedder = LocalEmbedder(
    base_url="http://localhost:11434",
    model="mxbai-embed-large"
)

config = M2WiseConfig(
    data_dir="./data",
    embedder=embedder,
)

engine = M2Wise(config=config)
```

## Advanced Examples

### Example 7: Memory Filtering

```python
from m2wise import M2Wise, M2WiseConfig

engine = M2Wise(config=M2WiseConfig(data_dir="./data"))

# Add various memories
engine.add([{"role": "user", "content": "I love coffee"}], user_id="bob")
engine.add([{"role": "user", "content": "I'm a designer"}], user_id="bob")
engine.add([{"role": "user", "content": "Remember: I hate spam"}], user_id="bob")

# Search specific type
bundle = engine.search("drinks", user_id="bob")

# Filter results
preferences = [m for m in bundle.memories if m.type == "preference"]
facts = [m for m in bundle.memories if m.type == "fact"]
```

### Example 8: Wisdom Application

```python
from m2wise import M2Wise, M2WiseConfig

engine = M2Wise(config=M2WiseConfig(data_dir="./data"))

# Ensure wisdom exists
engine.sleep(user_id="alice")
engine.dream(user_id="alice")

# When generating response
def generate_response(query, user_id):
    bundle = engine.search(query, user_id=user_id)

    # Apply principles
    principles = [w for w in bundle.wisdom if w.kind == "principle"]
    for p in principles:
        if evaluate_condition(p.applicability.when, query):
            apply_wisdom(p)

    # Build context
    context = bundle.as_prompt()
    return context
```

### Example 9: Privacy / Forget

```python
from m2wise import M2Wise, M2WiseConfig

engine = M2Wise(config=M2WiseConfig(data_dir="./data"))

# Add sensitive data
engine.add([{"role": "user", "content": "My password is secret123"}], user_id="alice")

# Find it
bundle = engine.search("password", user_id="alice")
memory_id = bundle.memories[0].id if bundle.memories else None

# Delete
if memory_id:
    engine.forget(user_id="alice", memory_id=memory_id)

# Or delete all wisdom
# engine.forget(user_id="alice", wisdom_id="all")
```

### Example 10: Event Graph

```python
from m2wise import M2Wise, M2WiseConfig

engine = M2Wise(config=M2WiseConfig(data_dir="./data"))

# Add conversation with events
engine.add([
    {"role": "user", "content": "I started learning Python"},
    {"role": "user", "content": "Now I'm building a web app"},
    {"role": "user", "content": "The app uses Flask"},
], user_id="alice")

# Search with event expansion
bundle = engine.search(
    query="programming",
    user_id="alice",
    expand_events=True  # Enable graph expansion
)
```

### Example 11: Async Processing

```python
import asyncio
from m2wise import M2Wise, M2WiseConfig
from m2wise.wisdom.performance import AsyncProcessor

async def process_users():
    engine = M2Wise(config=M2WiseConfig(data_dir="./data"))
    processor = AsyncProcessor(max_concurrent=10)

    users = ["alice", "bob", "charlie"]
    queries = ["hello", "help", "update"]

    # Create search tasks
    tasks = [
        engine.search(q, u)
        for u in users
        for q in queries
    ]

    # Process in parallel
    results = await processor.process_batch_async(tasks)
    return results

results = asyncio.run(process_users())
```

### Example 12: FastAPI Integration

```python
from fastapi import FastAPI
from m2wise import M2Wise, M2WiseConfig

app = FastAPI()
engine = M2Wise(config=M2WiseConfig(data_dir="./data"))

@app.post("/memory/add")
def add_memory(user_id: str, message: str):
    engine.add([{"role": "user", "content": message}], user_id=user_id)
    return {"status": "ok"}

@app.get("/memory/search")
def search_memory(user_id: str, query: str):
    bundle = engine.search(query, user_id=user_id)
    return {
        "memories": [m.dict() for m in bundle.memories],
        "wisdom": [w.dict() for w in bundle.wisdom]
    }

@app.post("/wisdom/sleep")
def sleep(user_id: str):
    return engine.sleep(user_id).__dict__

@app.post("/wisdom/dream")
def dream(user_id: str):
    return engine.dream(user_id).__dict__
```

### Example 13: Adapter Usage

```python
from m2wise.adapter import AdapterManager, Mem0Adapter, LettaAdapter

# Register adapters
manager = AdapterManager()
manager.register("mem0", Mem0Adapter())
manager.register("letta", LettaAdapter())

# Convert from mem0 format
mem0_memory = {"user_id": "alice", "content": "I like coffee"}
standard = manager.to_standard("mem0", mem0_memory)

# Convert to Letta format
wisdom = engine.list_wisdom(user_id="alice")[0]
letta_format = manager.from_standard("letta", wisdom)
```

### Example 14: MCP Tools

When using MCP server:

```
# Add memory
m2wise_add(user_id="alice", message="I prefer Chinese responses")

# Search
m2wise_search(user_id="alice", query="programming")

# Generate wisdom
m2wise_sleep(user_id="alice")

# Publish wisdom
m2wise_dream(user_id="alice")

# List wisdom
m2wise_list_wisdom(user_id="alice")

# Get statistics
m2wise_stats(user_id="alice")

# Delete memory
m2wise_forget(user_id="alice", memory_id="mem_xxx")
```

### Example 15: Custom Confidence Evaluation

```python
from m2wise.wisdom.performance import CachedSimilarityCalculator
from m2wise.schema.memory import MemoryScores

def custom_confidence(memory, user_history):
    # Base confidence
    base = memory.scores.confidence

    # Boost from repeated mentions
    frequency_bonus = min(0.1, user_history.count(memory.content) * 0.02)

    # Recency boost
    recency_bonus = 0.05 if memory.updated_at > last_week else 0

    return min(1.0, base + frequency_bonus + recency_bonus)
```
