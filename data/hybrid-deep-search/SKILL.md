---
name: hybrid-deep-search
description: Hybrid Deep Search - Intelligent routing between Brave API (free, fast) and OpenAI Codex (deep analysis, paid). Auto-selects optimal search strategy based on query complexity.
version: 1.0.0
author: Office_bot
tags: search, ai, research, brave, openai, codex, hybrid, routing
---

# Hybrid Deep Search 🚀

Intelligent three-tier search system that automatically routes queries between Brave API and OpenAI Codex for optimal cost and quality.

## Architecture

```
User Query
   ↓
Query Analyzer (router.py)
   ↓
   ├─→ Simple Questions → Brave API (web_search)     Fast, Free
   ├─→ Complex Questions → OpenAI Codex (gpt-5-codex)  Deep Analysis, Paid
   └─→ Manual Mode → User Specified
```

## Quick Start

### 1. Install Dependencies

```bash
pip install openai python-dotenv requests
```

### 2. Configure API Keys

#### Brave API (Already Built-in)
No extra configuration needed. Uses OpenClaw's built-in `web_search` tool.

#### OpenAI Codex API (Optional for Deep Search)
```bash
# Get API Key from: https://platform.openai.com/api-keys

export OPENAI_API_KEY="sk-your-openai-api-key"
export OPENAI_BASE_URL="https://api.openai.com/v1"  # Optional
```

## Usage

### Auto Mode (Recommended)
```bash
python3 scripts/deep_search.py "your query"
# System automatically analyzes complexity and chooses:
# - Simple questions → Brave API
# - Complex questions → OpenAI Codex
```

### Manual Mode
```bash
# Quick Search (Brave API)
python3 scripts/deep_search.py "what is OpenClaw?" --mode quick

# Deep Search (OpenAI Codex)
python3 scripts/deep_search.py "compare LangChain vs LlamaIndex" --mode codex
```

### Focus Modes
```bash
# Academic Search
python3 scripts/deep_search.py "AI agent frameworks research" --mode codex --focus academic

# News Search
python3 scripts/deep_search.py "latest AI news" --mode quick --focus news

# General Web Search
python3 scripts/deep_search.py "OpenClaw documentation" --mode quick --focus web
```

## Parameters

| Parameter | Description | Options | Default |
|-----------|-------------|----------|---------|
| query | Search query | Any text | - |
| --mode | Search mode | `quick`, `codex`, `auto` | `auto` |
| --focus | Search focus | `web`, `academic`, `news`, `youtube` | `web` |
| --max-results | Max results | 1-20 | 10 |
| --verbose | Verbose output | - | false |

## Complexity Routing Rules

Auto mode routes based on query analysis:

### → Brave API (quick)
- Simple factual queries (what/who/when/where)
- Definition lookups
- Quick fact-finding
- Single-topic searches

**Examples:**
- "what is OpenClaw?"
- "who created Python?"
- "latest AI news today"

### → OpenAI Codex (codex)
- Comparison analysis
- Deep reasoning
- Multi-source synthesis
- Complex questions
- Requires inference/summarization

**Examples:**
- "compare LangChain vs LlamaIndex in detail"
- "analyze impact of AI on job market"
- "explain quantum computing applications in healthcare"

## Cost Optimization

### Brave API
- ✅ Completely free
- ⚡ Fast response (<2s)
- 📊 Controllable result count

### OpenAI Codex (gpt-5-codex)
- 💰 Usage-based pricing
- 🧠 Deep reasoning capabilities
- ⏱️ Slower response (5-30s)
- 💡 Free tier available for new users

**Recommendation:** Use auto mode to let the system optimize costs for you.

## Technical Details

### Query Analyzer (router.py)
Analyzes query complexity using NLP rules:
- Keyword detection (compare/analyze/explain...)
- Sentence length
- Complexity scoring
- Automatic routing decisions

### Brave API Integration
Uses OpenClaw's built-in `web_search` tool:
- Called via Bash tool
- Handles requests automatically
- No extra authentication needed

### OpenAI Codex Integration
- Uses gpt-5-codex model
- Built-in web search tool
- OpenAI Chat Completions API format

## Example Use Cases

### Case 1: Quick Fact Lookup
```bash
python3 scripts/deep_search.py "OpenClaw version 2026"
# → Auto-uses Brave API
# → Result: Fast return, free
```

### Case 2: Deep Analysis
```bash
python3 scripts/deep_search.py "comprehensive analysis of AI agent architectures"
# → Auto-uses OpenAI Codex
# → Result: Deep analysis, multi-source synthesis
```

### Case 3: Academic Research
```bash
python3 scripts/deep_search.py "recent papers on multi-agent systems" --mode codex --focus academic
# → Uses OpenAI Codex
# → Result: Focused on academic literature
```

## Advanced Usage

### Batch Search
```bash
# Create queries.txt
echo "query 1" >> queries.txt
echo "query 2" >> queries.txt

# Batch execute
for query in $(cat queries.txt); do
  python3 scripts/deep_search.py "$query" --mode auto
done
```

### Format Output
```bash
# JSON output
python3 scripts/deep_search.py "query" --format json

# Markdown output (default)
python3 scripts/deep_search.py "query" --format markdown

# Plain text output
python3 scripts/deep_search.py "query" --format text
```

## Troubleshooting

### Brave API Not Responding
```bash
# Check OpenClaw web_search tool
# No extra configuration needed
```

### OpenAI Codex Authentication Failed
```bash
# Check environment variable
echo $OPENAI_API_KEY

# Reset
export OPENAI_API_KEY="sk-..."
```

### Python Dependencies
```bash
pip install --upgrade openai python-dotenv requests
```

## Complexity Scoring System

### Scoring Factors (0-10 total)

1. **Keyword Matching** (+6)
   - compare/analyze/explain/why/how...

2. **Query Length** (+2)
   - >15 words = +2
   - >8 words = +1

3. **Question Pattern** (+1)
   - Complex wh-questions

4. **Technical Terms** (+1)
   - API/framework/architecture...

5. **Simple Keyword Penalty** (-2)
   - what is/who is/list of...

### Decision Thresholds

- **0-2 score**: Brave API (quick)
- **3+ score**: OpenAI Codex (codex)

## Configuration

### Config File
```bash
cp config.json.example config.json
# Edit config.json with your settings
```

Example `config.json`:
```json
{
  "search_settings": {
    "default_mode": "auto",
    "default_focus": "web",
    "max_results": 10,
    "router_threshold": 3,
    "verbose": false
  },

  "openai_codex": {
    "enabled": true,
    "api_key": "YOUR_OPENAI_API_KEY_HERE",
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-5-codex",
    "max_tokens": 4096,
    "temperature": 0.7
  }
}
```

## Credits

- Built by **Office_bot**
- Powered by OpenClaw

## References

- [Brave Search API](https://brave.com/search/api/)
- [OpenAI GPT-5-Codex](https://platform.openai.com/docs/models/gpt-5-codex)
- [OpenAI API Docs](https://platform.openai.com/docs/api-reference)
