---
name: truthcheck
description: "Verify claims, fact-check content, check URL trustworthiness, and trace claims to their origin using the TruthCheck CLI. Use when: (1) user asks to fact-check or verify a claim, (2) user wants to check if a URL/source is trustworthy, (3) user wants to trace where a claim originated, (4) user asks about misinformation or content verification. Requires: pip install truthcheck"
metadata: { "openclaw": { "emoji": "🔍", "requires": { "bins": ["truthcheck"] } } }
---

# TruthCheck Skill

AI content verification CLI. Verify claims, check URLs, and trace misinformation.

## Commands

### Verify a claim
```bash
truthcheck verify "claim text" --llm gemini
```
- Returns TruthScore 0-100 with breakdown (publisher, content, corroboration, fact-checks)
- `--llm` is optional but improves accuracy
- Add `--json` for structured output

### Check URL trustworthiness
```bash
truthcheck check https://example.com
truthcheck check "text with multiple URLs"
truthcheck check -f file.txt
```
- Detects hallucinated URLs that don't exist
- Rates publisher credibility

### Trace a claim to its origin
```bash
truthcheck trace "claim text"           # balanced, ~1-2 min
truthcheck trace "claim text" --quick   # fast, ~30 sec
truthcheck trace "claim text" --deep    # thorough, ~3-5 min
```
- Finds original source and builds propagation tree

### Look up a publisher
```bash
truthcheck lookup "publisher name"
```

### Sync publisher database
```bash
truthcheck sync
```
Run periodically to keep publisher ratings current.

## Interpreting TruthScore

| Score | Label | Meaning |
|-------|-------|---------|
| 80-100 | TRUE | Strong evidence supports the claim |
| 60-79 | POSSIBLY TRUE | Some supporting evidence, inconclusive |
| 40-59 | UNCERTAIN | Mixed or insufficient evidence |
| 20-39 | POSSIBLY FALSE | Evidence leans against the claim |
| 0-19 | FALSE | Strong evidence contradicts the claim |

## LLM Integration (Optional)

TruthCheck works without any LLM, but adding `--llm` improves content analysis accuracy.

```bash
truthcheck verify "some claim" --llm gemini    # recommended, fast & free tier
truthcheck verify "some claim" --llm openai    # GPT models
truthcheck verify "some claim" --llm anthropic # Claude models
truthcheck verify "some claim" --llm ollama    # local models, fully offline
```

**Privacy:** API keys are stored in your local environment only. TruthCheck never sends your keys to any external service — they are used solely for direct API calls to the respective LLM provider.

## Environment Variables

| Variable | When needed | Description |
|----------|-------------|-------------|
| `GEMINI_API_KEY` | `--llm gemini` | Google AI API key (free tier available) |
| `OPENAI_API_KEY` | `--llm openai` | OpenAI API key |
| `ANTHROPIC_API_KEY` | `--llm anthropic` | Anthropic API key |
| `BRAVE_API_KEY` | `--search brave` | Brave Search API key |

No keys needed for `--llm ollama` (runs locally) or default DuckDuckGo search.

## Tips
- Verify commands can take 15-60 seconds depending on search results
- Without `--llm`: basic scoring using publisher reputation, corroboration, and fact-checks
- With `--llm`: adds AI content analysis for better accuracy
- `--search brave` gives better search results than default DuckDuckGo
- For batch verification, loop through claims individually
