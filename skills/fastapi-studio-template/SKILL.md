---
name: fastapi-studio-template
version: 1.2.0
description: Bootstrap a dark-themed FastAPI+HTMX studio app with SSE real-time progress, blind test mode, SQLite ratings, and Langfuse tracing. Based on the image-gen-studio architecture.
homepage: https://github.com/reddinft/skill-fastapi-studio-template
metadata:
  {
    "openclaw": {
      "emoji": "🎨",
      "requires": {
        "bins": ["python3"],
        "env": ["LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"]
      },
      "primaryEnv": "LANGFUSE_PUBLIC_KEY",
      "network": {
        "outbound": true,
        "reason": "Sends traces to Langfuse (self-hosted or cloud) for LLM observability. No other external calls."
      }
    }
  }
---

# FastAPI Studio Template

Bootstrap a dark-themed FastAPI + HTMX studio app for generative AI comparison, A/B testing, and human evaluation with real-time progress streaming.

## When to Use

- Any "studio" app: image generation comparison, text model A/B testing, human evaluation UI
- Apps needing real-time progress updates (generation can take 30s–15min)
- Blind test / evaluation interfaces where raters shouldn't know which model produced which output
- Rapid prototyping of gen AI comparison tools

## When NOT to Use

- Simple CRUD apps (use standard FastAPI + Jinja2)
- Apps that don't need real-time progress (SSE adds complexity)
- Production-scale apps with 100+ concurrent users (use WebSockets instead of SSE)

## Core Patterns

### SSE Async Pattern (Critical)

**MUST use `threading.SimpleQueue` + asyncio polling.** Do NOT use `run_in_executor` with blocking reads — it deadlocks the event loop.

```python
import asyncio
import threading
from queue import SimpleQueue

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

async def event_stream(queue: SimpleQueue):
    """Yield SSE events from a thread-safe queue."""
    while True:
        try:
            msg = queue.get_nowait()
        except Exception:
            await asyncio.sleep(0.1)
            continue
        if msg is None:  # sentinel
            yield f"data: {{\"done\": true}}\n\n"
            break
        yield f"data: {msg}\n\n"

@app.get("/generate/stream")
async def generate_stream(prompt: str, model: str):
    queue = SimpleQueue()

    def _run():
        # Heavy generation work in background thread
        for step in range(10):
            import time; time.sleep(1)
            queue.put(f'{{"step": {step}, "total": 10}}')
        queue.put(None)  # done sentinel

    threading.Thread(target=_run, daemon=True).start()
    return StreamingResponse(event_stream(queue), media_type="text/event-stream")
```

**Why not `run_in_executor`?** FastAPI's executor runs on a thread pool, but SSE needs to yield events incrementally. Blocking in the executor means you can't stream partial progress — you'd have to wait for the entire generation to finish. The queue pattern decouples generation from streaming.

### Blind Test Mode

Generate N variants (one per model), randomise display order, reveal model identity only after the user rates all variants.

```python
import random
import uuid

def create_blind_test(prompt: str, models: list[str]) -> dict:
    test_id = str(uuid.uuid4())
    variants = []
    for model in models:
        variants.append({
            "variant_id": str(uuid.uuid4()),
            "model": model,  # hidden from UI until reveal
            "prompt": prompt,
        })
    random.shuffle(variants)
    return {
        "test_id": test_id,
        "variants": variants,
        "display_order": [v["variant_id"] for v in variants],
    }
```

In the HTMX frontend, render variants as "Option A", "Option B", etc. On rating submission, return the mapping from option letters to model names.

### Hot-Loaded Model Singleton (ModelRegistry)

Cold-loading SDXL or similar models takes 6–14 minutes. Cache loaded models in a registry singleton.

```python
class ModelRegistry:
    _instance = None
    _models: dict = {}
    _lock = threading.Lock()

    @classmethod
    def get(cls, model_name: str):
        with cls._lock:
            if model_name not in cls._models:
                cls._models[model_name] = cls._load_model(model_name)
            return cls._models[model_name]

    @classmethod
    def _load_model(cls, name: str):
        # Import and load the model
        if name == "sdxl":
            from mflux import Flux1
            return Flux1.from_alias("schnell", quantize=8)
        raise ValueError(f"Unknown model: {name}")
```

**Preload at startup** via the FastAPI lifespan hook for models you know you'll need.

### float32 Requirement for SDXL on MPS

**torch 2.10 on Apple Silicon (MPS) produces NaN outputs with float16 for SDXL.** Force float32:

```python
import torch
torch.set_default_dtype(torch.float32)
# or per-model: model = model.to(dtype=torch.float32)
```

This doubles VRAM usage but is the only reliable option until the MPS float16 bug is fixed.

### SQLite Schema for Ratings

```sql
CREATE TABLE ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id TEXT NOT NULL,
    variant_id TEXT NOT NULL,
    model TEXT NOT NULL,
    rater TEXT DEFAULT 'anonymous',
    score INTEGER CHECK(score BETWEEN 1 AND 5),
    preferred BOOLEAN DEFAULT FALSE,  -- winner of pairwise comparison
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ratings_test ON ratings(test_id);
CREATE INDEX idx_ratings_model ON ratings(model);
```

### Langfuse Tracing

Wrap generation calls with Langfuse traces for cost tracking and latency monitoring:

```python
from langfuse import Langfuse

langfuse = Langfuse()

def generate_with_trace(prompt, model_name):
    trace = langfuse.trace(name="studio-generation", metadata={"model": model_name})
    span = trace.span(name="generate", input={"prompt": prompt})
    result = ModelRegistry.get(model_name).generate(prompt)
    span.end(output={"length": len(result)})
    return result
```

## Worked Example: Minimal Studio App

```python
"""Minimal FastAPI+HTMX studio with SSE progress."""
import asyncio
import json
import threading
from queue import SimpleQueue
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Studio</title>
    <script src="https://unpkg.com/htmx.org@1.9.12"></script>
    <script src="https://unpkg.com/htmx.org@1.9.12/dist/ext/sse.js"></script>
    <style>
        body { background: #1a1a2e; color: #e0e0e0; font-family: system-ui; padding: 2rem; }
        .card { background: #16213e; border-radius: 8px; padding: 1.5rem; margin: 1rem 0; }
        button { background: #0f3460; color: white; border: none; padding: 0.75rem 1.5rem;
                 border-radius: 4px; cursor: pointer; }
        button:hover { background: #533483; }
        input, textarea { background: #0f3460; color: white; border: 1px solid #333;
                          padding: 0.5rem; border-radius: 4px; width: 100%; }
        #progress { color: #e94560; }
    </style>
</head>
<body>
    <h1>🎨 Studio</h1>
    <div class="card">
        <textarea id="prompt" placeholder="Enter prompt..." rows="3"></textarea>
        <br><br>
        <button onclick="startGeneration()">Generate</button>
    </div>
    <div id="progress" class="card" style="display:none"></div>
    <div id="results" class="card" style="display:none"></div>
    <script>
    function startGeneration() {
        const prompt = document.getElementById('prompt').value;
        const progress = document.getElementById('progress');
        progress.style.display = 'block';
        progress.textContent = 'Starting...';

        const source = new EventSource('/generate/stream?prompt=' + encodeURIComponent(prompt));
        source.onmessage = (e) => {
            const data = JSON.parse(e.data);
            if (data.done) {
                source.close();
                progress.textContent = 'Done!';
            } else {
                progress.textContent = `Step ${data.step}/${data.total}`;
            }
        };
    }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML

async def event_stream(queue: SimpleQueue):
    while True:
        try:
            msg = queue.get_nowait()
        except Exception:
            await asyncio.sleep(0.1)
            continue
        if msg is None:
            yield f"data: {json.dumps({'done': True})}\n\n"
            break
        yield f"data: {msg}\n\n"

@app.get("/generate/stream")
async def generate_stream(prompt: str):
    queue = SimpleQueue()
    def _run():
        import time
        for i in range(10):
            time.sleep(0.5)
            queue.put(json.dumps({"step": i + 1, "total": 10}))
        queue.put(None)
    threading.Thread(target=_run, daemon=True).start()
    return StreamingResponse(event_stream(queue), media_type="text/event-stream")
```

Run with: `uvicorn app:app --reload --port 8000`

## Tips

- **Dark theme first** — gen AI studios are used in long sessions; light themes cause eye strain
- **Always show progress** — users will close the tab if they think it's frozen
- **Log every generation** — Langfuse traces are invaluable for debugging quality issues
- **Rate-limit generation** — SDXL on MPS can only do one image at a time; queue requests
- **Export ratings as CSV** — researchers need data in portable formats
