# Math Model Rankings

This file is the **bundled fallback** used when the hosted model config cannot be fetched.
The live version is maintained at:
  https://raw.githubusercontent.com/stellawuellner/math-worksheets-skill/main/references/model-rankings.json

Last updated: 2026-02-22
Update this file when the hosted JSON is also updated.

## Current Rankings (K-12 Math Generation)

### Tier 1 — Reasoning Models (FOUND_REASONING)
Step-by-step internal reasoning. Highest math accuracy. Use for problem generation + answer keys.

| Model ID pattern | Alias | Notes |
|---|---|---|
| `openai/o3` | o3 | Best overall math as of early 2026 |
| `openai/o1` | o1 | Strong reasoning, more accessible than o3 |
| `gemini-2.5-pro-deepthink` | deepthink | Google's reasoning model, excellent |
| `gemini-2.0-pro-deepthink` | deepthink | Previous generation, still solid |
| `deepseek-r1` | deepseek | Open source, competitive with o1 |
| `deepseek/deepseek-r1` | deepseek | Full model ID variant |

### Tier 2 — Strong Non-Reasoning (FOUND_STRONG)
No step-by-step reasoning, but high quality. Excellent LaTeX and pedagogical judgment.
Use when no Tier 1 is available. SymPy verification compensates for accuracy gap.

| Model ID pattern | Alias | Notes |
|---|---|---|
| `claude-opus-4` | opus | Excellent math + best LaTeX quality |
| `claude-opus-3-5` | opus | Previous generation Opus, still strong |

### Tier 3 — Standard Models (NONE → show recommendation)
Capable but not recommended for complex algebra. SymPy verification is essential.

| Model ID pattern | Notes |
|---|---|
| `claude-sonnet-4` | Good for basic problems, weaker on multi-step |
| `gemini-2.5-flash` | Fast, adequate for Pre-Algebra level |
| `openai/gpt-4o` | Decent, not specialized for math |

## How to Update

When new models ship that should be Tier 1 or Tier 2:

1. Update the hosted `models.json` at the GitHub URL above
2. Update this file (bundled fallback)
3. Bump `last_updated` in `models.json`
4. Submit a skill update to ClawhHub

Key signals a model deserves Tier 1 promotion:
- Scores >80% on MATH benchmark or AIME
- Has documented chain-of-thought / reasoning architecture
- Consistently outperforms Sonnet-class on algebra in community testing

Resources for staying current:
- https://livebench.ai — live model benchmarks
- https://arxiv.org/list/cs.LG/recent — new model papers
- https://lmsys.org/blog — LMSYS Chatbot Arena (math category)
