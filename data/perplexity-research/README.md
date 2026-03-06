# Perplexity Research Skill

AI agent skill for conducting deep research using Perplexity Agent API with web search, reasoning, and multi-model analysis capabilities.

## Structure

```
perplexity-research/
├── SKILL.md              # Main skill instructions for the AI agent
├── examples.md           # Practical usage examples
├── reference.md          # Complete API reference documentation
├── README.md            # This file
└── scripts/
    ├── perplexity_client.py  # Perplexity API client implementation
    └── .env.example          # Environment variable template
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install perplexity python-dotenv
   ```

2. **Configure API key:**
   
   Create `.env` file in the `scripts/` directory:
   ```bash
   cd .cursor/skills/perplexity-research/scripts
   cp .env.example .env
   # Edit .env and add your actual API key
   ```
   
   Or export as environment variable:
   ```bash
   export PERPLEXITY_API_KEY='your_api_key_here'
   ```

3. **Get your API key:**
   - Sign up at [Perplexity API](https://www.perplexity.ai/api)
   - Generate an API key from your dashboard

## Quick Usage

### As CLI Tool

```bash
cd .cursor/skills/perplexity-research

# Research mode (recommended for deep analysis)
python scripts/perplexity_client.py research "What are the latest developments in AI chip manufacturing?"

# Quick web search
python scripts/perplexity_client.py search "NVIDIA latest earnings report"

# Streaming response
python scripts/perplexity_client.py stream "Explain quantum computing"

# Compare multiple models
python scripts/perplexity_client.py compare "What are the risks in semiconductor industry?"
```

### As Python Library

```python
import sys
from pathlib import Path

# Add scripts to path
skill_dir = Path(".cursor/skills/perplexity-research")
sys.path.insert(0, str(skill_dir / "scripts"))

from perplexity_client import PerplexityClient

# Initialize client
client = PerplexityClient()

# Conduct research
result = client.research_query(
    query="Analyze the competitive landscape in EV battery technology",
    model="openai/gpt-5.2",
    reasoning_effort="high",
    max_tokens=2000
)

if "error" not in result:
    print(result["answer"])
    print(f"Cost: ${result['cost']:.6f}")
```

## Key Features

- **Web Search**: Access to real-time web search for current information
- **High Reasoning**: Deep analysis with adjustable reasoning effort levels
- **Multi-Model Support**: Compare results across GPT, Claude, Gemini, and Llama models
- **Streaming**: Real-time response streaming for better UX
- **Cost Tracking**: Automatic token and cost tracking for all queries
- **Error Handling**: Robust error handling with detailed error messages

## Default Model

**GPT-5.2** (`openai/gpt-5.2`) - Latest GPT model with best overall performance for research tasks.

## Documentation

- **[SKILL.md](SKILL.md)** - Main instructions for the AI agent
- **[examples.md](examples.md)** - Practical examples for common use cases
- **[reference.md](reference.md)** - Complete API reference

## For AI Agents

This is a Cursor agent skill. When invoked by the user requesting research, current information, or analysis requiring web search, the agent will automatically use this skill to:

1. Access the Perplexity Agent API
2. Conduct web searches with reasoning
3. Compare results across multiple models when needed
4. Track costs and token usage
5. Return comprehensive, sourced research results

The skill is optimized for investment research, market analysis, technology trends, and any research requiring current information with reasoning capabilities.
