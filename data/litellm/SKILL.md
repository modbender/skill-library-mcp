---
name: litellm
description: Call 100+ LLM providers through LiteLLM's unified API. Use when you need to call a different model than your primary (e.g., use GPT-4 for code review while running on Claude), compare outputs from multiple models, route to cheaper models for simple tasks, or access models your runtime doesn't natively support.
---

# LiteLLM - Multi-Model LLM Calls

Use LiteLLM when you need to call LLMs beyond your primary model.

## When to Use

- **Model comparison**: Get outputs from multiple models and compare
- **Specialized routing**: Use code-optimized models for code, writing models for prose
- **Cost optimization**: Route simple queries to cheaper models
- **Fallback access**: Access models your runtime doesn't support

## Quick Start

```python
import litellm

# Call any model with unified API
response = litellm.completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Explain this code"}]
)
print(response.choices[0].message.content)
```

## Common Patterns

### Compare Multiple Models

```python
import litellm

prompt = [{"role": "user", "content": "What's the best approach to X?"}]

models = ["gpt-4o", "claude-sonnet-4-20250514", "gemini/gemini-1.5-pro"]
for model in models:
    resp = litellm.completion(model=model, messages=prompt)
    print(f"{model}: {resp.choices[0].message.content[:200]}...")
```

### Route by Task Type

```python
import litellm

def smart_call(task_type: str, prompt: str) -> str:
    model_map = {
        "code": "gpt-4o",           # Strong at code
        "writing": "claude-sonnet-4-20250514",  # Strong at prose
        "simple": "gpt-4o-mini",    # Cheap for simple tasks
        "reasoning": "o1-preview",  # Deep reasoning
    }
    model = model_map.get(task_type, "gpt-4o")
    resp = litellm.completion(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content
```

### Use LiteLLM Proxy (Recommended)

If a LiteLLM proxy is available, point to it for caching, rate limiting, and observability:

```python
import litellm

litellm.api_base = "https://your-litellm-proxy.com"
litellm.api_key = "sk-your-key"

response = litellm.completion(
    model="gpt-4o",  # Proxy routes to configured provider
    messages=[{"role": "user", "content": "Hello"}]
)
```

## Environment Setup

Ensure `litellm` is installed and API keys are set:

```bash
pip install litellm

# Set provider keys (or configure in proxy)
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-..."
```

## Model Reference

Common model identifiers:
- **OpenAI**: `gpt-4o`, `gpt-4o-mini`, `o1-preview`, `o1-mini`
- **Anthropic**: `claude-sonnet-4-20250514`, `claude-opus-4-20250514`
- **Google**: `gemini/gemini-1.5-pro`, `gemini/gemini-1.5-flash`
- **Mistral**: `mistral/mistral-large-latest`

Full list: https://docs.litellm.ai/docs/providers
