# Perplexity Client API Reference

Complete reference documentation for `PerplexityClient` class.

## Class: PerplexityClient

Located at `scripts/perplexity_client.py` in this skill folder.

```python
# Import setup
import sys
from pathlib import Path

# Add scripts directory to path
skill_dir = Path(".cursor/skills/perplexity-research")
sys.path.insert(0, str(skill_dir / "scripts"))

from perplexity_client import PerplexityClient
```

### Constructor

```python
PerplexityClient(api_key: Optional[str] = None)
```

**Parameters:**
- `api_key` (optional): Perplexity API key. Defaults to `PERPLEXITY_API_KEY` environment variable.

**Example:**
```python
# Use environment variable
client = PerplexityClient()

# Or provide key explicitly
client = PerplexityClient(api_key="your_key_here")
```

---

## Methods

### simple_query()

Execute a query without tools (no web search).

```python
simple_query(
    query: str,
    model: str = "openai/gpt-5.2",
    max_tokens: int = 1000
) -> Dict
```

**Parameters:**
- `query`: The question or prompt
- `model`: Model identifier (default: "openai/gpt-5.2")
- `max_tokens`: Maximum output tokens

**Returns:**
```python
{
    "answer": str,      # Response text
    "tokens": int,      # Total tokens used
    "cost": float,      # Cost in dollars
    "model": str        # Model used
}
# Or on error:
{
    "error": str        # Error message
}
```

**Use when:**
- You don't need web search
- Working with general knowledge
- Cost optimization is priority

---

### search_query()

Execute a query with web search enabled.

```python
search_query(
    query: str,
    model: str = "openai/gpt-5.2",
    location: Optional[Dict] = None,
    max_tokens: int = 1000
) -> Dict
```

**Parameters:**
- `query`: The question or prompt
- `model`: Model identifier
- `location`: Optional location context
- `max_tokens`: Maximum output tokens

**Location format:**
```python
{
    "latitude": float,
    "longitude": float,
    "city": str,
    "region": str,
    "country": str
}
```

**Returns:** Same format as `simple_query()`

**Use when:**
- Need current information
- Researching recent events
- Time-sensitive queries

---

### stream_query()

Execute a streaming query with real-time output.

```python
stream_query(
    query: str,
    model: str = "openai/gpt-5.2",
    use_search: bool = False,
    max_tokens: int = 2000
) -> None
```

**Parameters:**
- `query`: The question or prompt
- `model`: Model identifier
- `use_search`: Enable web search tool
- `max_tokens`: Maximum output tokens

**Returns:** None (prints output to console)

**Use when:**
- Building user-facing applications
- Long responses expected
- Want to show progress

**Note:** Prints formatted output directly. Not suitable for programmatic result processing.

---

### research_query()

Execute a research query with web search and high reasoning.

```python
research_query(
    query: str,
    model: str = "openai/gpt-5.2",
    reasoning_effort: str = "high",
    max_tokens: int = 2000
) -> Dict
```

**Parameters:**
- `query`: The research question
- `model`: Model identifier
- `reasoning_effort`: "low", "medium", or "high"
- `max_tokens`: Maximum output tokens

**Returns:** Same format as `simple_query()`

**Use when:**
- Conducting comprehensive research
- Need deep analysis with reasoning
- Quality more important than speed
- Working with complex questions

**Recommended for:** Most research tasks in this project.

---

### conversation()

Execute a multi-turn conversation.

```python
conversation(
    messages: List[Dict],
    model: str = "openai/gpt-5.2",
    use_search: bool = False,
    max_tokens: int = 1000
) -> Dict
```

**Parameters:**
- `messages`: List of message dicts with 'role' and 'content'
- `model`: Model identifier
- `use_search`: Enable web search
- `max_tokens`: Maximum output tokens

**Message format:**
```python
[
    {"role": "user", "content": "First question"},
    {"role": "assistant", "content": "First response"},
    {"role": "user", "content": "Follow-up question"}
]
```

**Returns:** Same format as `simple_query()`

**Use when:**
- Building on previous context
- Multi-step research
- Iterative analysis

---

### compare_models()

Compare responses from multiple models.

```python
compare_models(
    query: str,
    models: List[str] = None,
    max_tokens: int = 300
) -> List[Dict]
```

**Parameters:**
- `query`: The question or prompt
- `models`: List of model identifiers (defaults to GPT-5.2, Claude, Gemini)
- `max_tokens`: Maximum output tokens per model

**Default models:**
```python
[
    "openai/gpt-5.2",
    "anthropic/claude-3-5-sonnet",
    "google/gemini-2.0-flash"
]
```

**Returns:**
```python
[
    {
        "model": str,
        "answer": str,
        "tokens": int,
        "cost": float
    },
    # ... one per model
]
```

**Use when:**
- Critical decisions need validation
- Comparing model strengths
- Ensuring comprehensive coverage
- Quality is paramount

---

### use_preset()

Execute a query using preset configuration.

```python
use_preset(
    query: str,
    preset: str = "pro-search"
) -> Dict
```

**Parameters:**
- `query`: The question or prompt
- `preset`: Preset identifier

**Available presets:**
- `"pro-search"` - Optimized for comprehensive web search

**Returns:** Same format as `simple_query()`

**Use when:**
- Want optimized configurations
- Presets match your use case
- Simplifying configuration

---

## Model Identifiers

### Recommended Models

**GPT Models (Default):**
- `openai/gpt-5.2` - Latest GPT, best overall performance
- `openai/gpt-4o` - High capability, balanced cost

**Anthropic Models:**
- `anthropic/claude-3-5-sonnet` - Strong reasoning
- `anthropic/claude-3-5-haiku` - Fast, economical

**Google Models:**
- `google/gemini-2.0-flash` - Fast, cost-effective
- `google/gemini-pro` - Higher capability

**Meta Models:**
- `meta/llama-3.3-70b` - Open source alternative
- `meta/llama-3.1-405b` - Largest open model

### Model Selection Guide

| Use Case | Recommended Model | Why |
|----------|------------------|-----|
| Deep research | `openai/gpt-5.2` | Best reasoning, web search integration |
| Quick answers | `google/gemini-2.0-flash` | Speed, cost efficiency |
| Balanced | `anthropic/claude-3-5-sonnet` | Quality, reliability |
| Cost-sensitive | `google/gemini-2.0-flash` | Lowest cost per token |
| Open source | `meta/llama-3.3-70b` | No vendor lock-in |

---

## Reasoning Effort Levels

Control analysis depth with `reasoning_effort` parameter:

| Level | Use Case | Speed | Quality | Cost |
|-------|----------|-------|---------|------|
| `"low"` | Quick facts, simple questions | Fast | Basic | Low |
| `"medium"` | Standard queries, balanced needs | Medium | Good | Medium |
| `"high"` | Deep analysis, research | Slow | Best | High |

**Recommendation:** Use `"high"` for research queries (it's the default in `research_query()`).

---

## Response Format

All non-streaming methods return consistent format:

**Success:**
```python
{
    "answer": "Response text...",
    "tokens": 1234,
    "cost": 0.005678,
    "model": "openai/gpt-5.2"
}
```

**Error:**
```python
{
    "error": "Error description"
}
```

**Always check for errors:**
```python
result = client.research_query("...")

if "error" in result:
    # Handle error
    print(f"Error: {result['error']}")
else:
    # Process result
    print(result["answer"])
```

---

## Cost Information

Costs are returned in USD for every query.

**Track costs:**
```python
total_cost = 0

result = client.research_query("Query 1")
if "error" not in result:
    total_cost += result["cost"]

result = client.search_query("Query 2")
if "error" not in result:
    total_cost += result["cost"]

print(f"Total cost: ${total_cost:.6f}")
```

**Token usage:**
```python
result = client.research_query("...")
print(f"Tokens used: {result['tokens']}")
print(f"Cost: ${result['cost']:.6f}")
print(f"Cost per token: ${result['cost'] / result['tokens']:.8f}")
```

---

## Environment Variables

**Required:**
- `PERPLEXITY_API_KEY` - Your Perplexity API key

**Setting up:**

**Option 1: Export in shell**
```bash
export PERPLEXITY_API_KEY='your_key_here'
```

**Option 2: .env file**

Create `.env` in the skill's `scripts/` directory:
```
PERPLEXITY_API_KEY=your_key_here
```

The client automatically loads `.env` files using `python-dotenv` if present in the script's directory.

---

## Error Handling

### Common Errors

**API Key Missing:**
```python
{"error": "API Error: Unauthorized (Status: 401)"}
```
→ Set `PERPLEXITY_API_KEY` environment variable

**Rate Limit:**
```python
{"error": "API Error: Rate limit exceeded (Status: 429)"}
```
→ Wait and retry, or implement exponential backoff

**Invalid Model:**
```python
{"error": "API Error: Model not found (Status: 404)"}
```
→ Check model identifier spelling

**Network Issues:**
```python
{"error": "Unexpected error: Connection timeout"}
```
→ Check network connection, retry

### Best Practices

1. **Always check for errors:**
```python
if "error" in result:
    # Handle appropriately
```

2. **Implement retries for transient errors:**
```python
def query_with_retry(client, query, max_retries=3):
    for attempt in range(max_retries):
        result = client.research_query(query)
        if "error" not in result:
            return result
        if "rate limit" in result["error"].lower():
            time.sleep(2 ** attempt)  # Exponential backoff
    return result
```

3. **Log costs for monitoring:**
```python
import logging

result = client.research_query("...")
if "error" not in result:
    logging.info(f"Query cost: ${result['cost']:.6f}")
```

---

## CLI Usage

The client can be used from command line. Run from the skill directory or provide full path:

```bash
# From skill directory
cd .cursor/skills/perplexity-research

# Research mode
python scripts/perplexity_client.py research "Your question"

# Web search
python scripts/perplexity_client.py search "Your question"

# Streaming
python scripts/perplexity_client.py stream "Your question"

# Compare models
python scripts/perplexity_client.py compare "Your question"

# Use preset
python scripts/perplexity_client.py preset "Your question"

# Simple query
python scripts/perplexity_client.py query "Your question"
```

---

## Dependencies

Required packages:
- `perplexity` - Perplexity SDK
- `python-dotenv` - Environment variable loading (optional)

Install:
```bash
pip install perplexity python-dotenv
```
