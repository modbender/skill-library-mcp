---
name: perplexity-research
description: Conduct deep research using Perplexity Agent API with web search, reasoning, and multi-model analysis. Use when the user needs current information, market research, trend analysis, investment insights, or comprehensive research on any topic requiring web search and reasoning capabilities.
---

# Perplexity Research

Research assistant powered by Perplexity Agent API with web search and reasoning capabilities.

## Quick Start

The Perplexity client is available at `scripts/perplexity_client.py` in this skill folder.

**Default model**: `openai/gpt-5.2` (GPT latest)

**Key capabilities**:
- Web search for current information
- High reasoning effort for deep analysis
- Multi-model comparison
- Streaming responses
- Cost tracking

## Common Research Patterns

### 1. Deep Research Query

Use for comprehensive analysis requiring web search and reasoning:

```python
# Import from skill scripts folder
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))
from perplexity_client import PerplexityClient

client = PerplexityClient()
result = client.research_query(
    query="Your research question here",
    model="openai/gpt-5.2",
    reasoning_effort="high",
    max_tokens=2000
)

if "error" not in result:
    print(result["answer"])
    print(f"Tokens: {result['tokens']}, Cost: ${result['cost']}")
```

### 2. Quick Web Search

Use for time-sensitive or current information:

```python
result = client.search_query(
    query="Your question about current events",
    model="openai/gpt-5.2",
    max_tokens=1000
)
```

### 3. Model Comparison

Use when output quality is critical:

```python
results = client.compare_models(
    query="Your question",
    models=["openai/gpt-5.2", "anthropic/claude-3-5-sonnet", "google/gemini-2.0-flash"],
    max_tokens=300
)

for result in results:
    if "error" not in result:
        print(f"\n{result['model']}: {result['answer']}")
```

### 4. Streaming for Long Responses

Use for better UX with lengthy analysis:

```python
client.stream_query(
    query="Your question",
    model="openai/gpt-5.2",
    use_search=True,
    max_tokens=2000
)
```

## Research Workflow

When conducting research:

1. **Initial exploration**: Use `research_query()` with web search enabled
2. **Validate findings**: Compare key insights across models with `compare_models()`
3. **Deep dive**: Use streaming for detailed analysis on specific aspects
4. **Cost-aware**: Monitor token usage and costs in results

## Model Selection

**Default: `openai/gpt-5.2`** (Latest GPT model)

Alternative models:
- `anthropic/claude-3-5-sonnet` - Strong reasoning, balanced performance
- `google/gemini-2.0-flash` - Fast, cost-effective
- `meta/llama-3.3-70b` - Open source alternative

Switch models based on:
- Quality needs (GPT-5.2 for best results)
- Speed requirements (Gemini Flash for quick answers)
- Cost constraints (compare costs in results)

## Reasoning Effort Levels

Control analysis depth with `reasoning_effort`:

- `"low"` - Quick answers, minimal reasoning
- `"medium"` - Balanced reasoning (default for most queries)
- `"high"` - Deep analysis, comprehensive research (recommended for research)

## Environment Setup

Ensure `PERPLEXITY_API_KEY` is set:

```bash
export PERPLEXITY_API_KEY='your_api_key_here'
```

Or create `.env` file in the skill's `scripts/` directory:

```
PERPLEXITY_API_KEY=your_api_key_here
```

## Error Handling

All methods return error information:

```python
result = client.research_query("Your question")

if "error" in result:
    print(f"Error: {result['error']}")
    # Handle error appropriately
else:
    # Process successful result
    print(result["answer"])
```

## Cost Optimization

- Use `max_tokens` to limit response length
- Start with lower reasoning effort, increase if needed
- Use `search_query()` instead of `research_query()` for simpler questions
- Monitor costs via `result["cost"]` field

## Integration Examples

### Investment Research

```python
client = PerplexityClient()

# Market analysis
result = client.research_query(
    query="Analyze recent developments in AI chip market and key competitors",
    reasoning_effort="high"
)

# Company deep dive
result = client.search_query(
    query="Latest earnings report for NVIDIA Q4 2025"
)

# Multi-model validation
results = client.compare_models(
    query="What are the biggest risks in the semiconductor industry?",
    models=["openai/gpt-5.2", "anthropic/claude-3-5-sonnet"]
)
```

### Trend Analysis

```python
# Current trends with web search
result = client.research_query(
    query="Emerging trends in sustainable investing and ESG adoption rates",
    reasoning_effort="high",
    max_tokens=2000
)

# Stream for real-time updates
client.stream_query(
    query="Latest developments in quantum computing commercialization",
    use_search=True
)
```

### Multi-Turn Research

```python
# Build context across multiple queries
messages = [
    {"role": "user", "content": "What is the current state of fusion energy?"},
    {"role": "assistant", "content": "...previous response..."},
    {"role": "user", "content": "Which companies are leading in this space?"}
]

result = client.conversation(
    messages=messages,
    use_search=True
)
```

## Best Practices

1. **Default to research_query()** for most research tasks - it combines web search with high reasoning
2. **Use streaming** for user-facing applications to show progress
3. **Compare models** for critical decisions or when quality is paramount
4. **Set reasonable max_tokens** - 1000 for summaries, 2000+ for deep analysis
5. **Track costs** - access via `result["cost"]` and `result["tokens"]`
6. **Handle errors gracefully** - always check for "error" key in results

## API Reference

See [reference.md](reference.md) for complete API documentation, or `scripts/perplexity_client.py` for:
- Full method signatures
- Additional parameters
- CLI usage examples
- Implementation details

## Command Line Usage

Run from the skill directory:

```bash
# Research mode
python scripts/perplexity_client.py research "Your question"

# Web search
python scripts/perplexity_client.py search "Your question"

# Streaming
python scripts/perplexity_client.py stream "Your question"

# Compare models
python scripts/perplexity_client.py compare "Your question"
```
