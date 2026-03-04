# Provider Configuration Guide

## Built-in Providers

These need only auth setup + model selection. No `models.providers` config required.

### Z.AI (GLM models)

```bash
openclaw onboard --auth-choice zai-api-key
openclaw models set zai/glm-4.7
openclaw models fallbacks add zai/glm-4.6
```

Config snippet:
```json
{ "agents": { "defaults": { "model": { "primary": "zai/glm-4.7" } } } }
```

Models: `glm-4.7`, `glm-4.6`
Auth: Bearer token via ZAI_API_KEY or auth-profiles

### Anthropic

```bash
openclaw onboard --auth-choice anthropic-api-key
openclaw models set anthropic/claude-opus-4-6
```

Models: `claude-opus-4-6`, `claude-sonnet-4-5`, `claude-haiku-4-5`

### OpenAI

```bash
openclaw models set openai/gpt-5.1
```

### OpenAI Codex (OAuth)

```bash
openclaw models auth login --provider openai-codex
openclaw models set openai-codex/gpt-5.3-codex
```

### OpenRouter

```bash
openclaw models set openrouter/<org>/<model>
```

Free models: use `openclaw models scan` to discover and rank.

### Ollama (local)

```bash
ollama pull llama3.3
openclaw models set ollama/llama3.3
```

Auto-detected at `http://127.0.0.1:11434/v1`.

## Custom Providers (OpenAI-compatible)

For NVIDIA NIM, LM Studio, vLLM, etc. — requires `models.providers` in openclaw.json.

Write config safely via python3 (never heredoc in tmux):

```python
python3 -c "
import json
# Read existing config
with open('/Users/<user>/.openclaw/openclaw.json') as f:
    config = json.load(f)

# Add custom provider
config.setdefault('models', {})['mode'] = 'merge'
config['models'].setdefault('providers', {})['nvidia'] = {
    'baseUrl': 'https://integrate.api.nvidia.com/v1',
    'apiKey': '<key>',
    'api': 'openai-completions',
    'models': [{
        'id': 'moonshotai/kimi-k2.5',
        'name': 'Kimi K2.5 (NVIDIA NIM)',
        'reasoning': True,
        'input': ['text'],
        'contextWindow': 131072,
        'maxTokens': 8192
    }]
}

# Write back
with open('/Users/<user>/.openclaw/openclaw.json', 'w') as f:
    json.dump(config, f, indent=2)
"
```

### NVIDIA NIM (free tier)

- Base URL: `https://integrate.api.nvidia.com/v1`
- API: `openai-completions`
- Warning: Free tier is often congested (150+ queue). Not practical for agent workflows.

### LM Studio (local)

- Base URL: `http://localhost:1234/v1`
- API: `openai-completions`

## Planning vs Execution Pattern

Set stronger model as primary, lighter as fallback:

```bash
openclaw models set zai/glm-4.7          # Planning (stronger)
openclaw models fallbacks add zai/glm-4.6 # Execution (lighter)
```

Users switch in-session with `/model zai/glm-4.6`.

For dedicated agents with separate models:

```json
{
  "agents": {
    "list": [
      { "id": "planner", "model": "zai/glm-4.7", "workspace": "~/.openclaw/workspace-planner" },
      { "id": "executor", "model": "zai/glm-4.6", "workspace": "~/.openclaw/workspace-executor" }
    ]
  }
}
```

## Common Model Reference

| Provider | Model IDs | Notes |
|----------|-----------|-------|
| zai | glm-4.7, glm-4.6 | Z.AI, Bearer auth, ~5s response |
| anthropic | claude-opus-4-6, claude-sonnet-4-5 | API key or CLI token |
| openai | gpt-5.1, gpt-5.2 | API key |
| openai-codex | gpt-5.3-codex | OAuth device flow |
| nvidia | moonshotai/kimi-k2.5 | Free but congested |
| openrouter | varies | Many free; use `openclaw models scan` |
| ollama | llama3.3, etc. | Local, no auth |
