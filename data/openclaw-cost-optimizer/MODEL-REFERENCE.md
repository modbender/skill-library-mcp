# Cost Optimizer — Quick Reference

**v1.1.0** | Built by Jeff J Hunter | https://jeffjhunter.com

## Commands

| Action | Command | Where |
|--------|---------|-------|
| Switch model | `/model aliasname` | Chat |
| Reset to default | `/model` | Chat |
| List available | `/model list` | Chat |
| Model details | `/model status` | Chat |
| Turn off advisor | "advisor off" | Chat |
| Turn on advisor | "advisor on" | Chat |
| See your savings | "how much have I saved?" | Chat |
| Estimate monthly cost | "estimate my monthly costs" | Chat |
| Build custom preset | "mix and match" | Chat |
| Reset savings tracker | "reset my savings tracker" | Chat |
| Add a model | "add [model] to my models" | Chat |
| Remove a model | "remove [alias]" | Chat |
| Switch preset | "switch me to [preset]" | Chat |

---

## All Models by Price

### FREE ⚠️ (unreliable — cold starts, rate limits, downtime)

| Alias | Model | `/model` command |
|-------|-------|-----------------|
| `mimo` | MiMo v2 Flash | `/model mimo` |
| `devfree` | Devstral Small Free | `/model devfree` |
| `glm` | GLM-Z1 Free | `/model glm` |

### ¢ — Under $0.50 per million tokens

| Alias | Model | Input/Output | `/model` command |
|-------|-------|-------------|-----------------|
| `devstral` | Devstral Small (paid) | $0.05/$0.22 | `/model devstral` |
| `flashlite` | Gemini 2.5 Flash-Lite | $0.10/$0.40 | `/model flashlite` |
| `deepseek` | DeepSeek V3 | $0.14/$0.28 | `/model deepseek` |
| `qwen3` | Qwen3 235B | $0.14/$0.28 | `/model qwen3` |
| `flash` | Gemini 2.5 Flash | $0.15/$0.60 | `/model flash` |
| `seed` | Seed Coder 200K | $0.20/$0.60 | `/model seed` |
| `minimax` | MiniMax M2.1 | $0.28/$1.20 | `/model minimax` |
| `mini` | GPT-5 Mini | $0.30/$1.20 | `/model mini` |

### ¢¢ — Under $2 per million tokens

| Alias | Model | Input/Output | `/model` command |
|-------|-------|-------------|-----------------|
| `gem3flash` | Gemini 3 Flash | $0.50/$2.00 | `/model gem3flash` |
| `kimi25` | Kimi K2.5 | $0.50/$2.00 | `/model kimi25` |
| `r1` | DeepSeek R1 | $0.55/$2.19 | `/model r1` |
| `haiku` | Claude Haiku 4.5 | $0.80/$4.00 | `/model haiku` |
| `gem3pro` | Gemini 3 Pro 1M | $1.25/$10.00 | `/model gem3pro` |

### $$ — $2-15 per million tokens

| Alias | Model | Input/Output | `/model` command |
|-------|-------|-------------|-----------------|
| `gpt51` | GPT-5.1 | $2.00/$8.00 | `/model gpt51` |
| `gpt52` | GPT-5.2 | $2.00/$10.00 | `/model gpt52` |
| `codex52` | GPT-5.2 Codex | $2.00/$10.00 | `/model codex52` |
| `grok4` | Grok 4 | $2.00/$10.00 | `/model grok4` |
| `grokfast` | Grok 4.1 Fast 2M | $2.00/$10.00 | `/model grokfast` |
| `sonnet` | Claude Sonnet 4.5 | $3.00/$15.00 | `/model sonnet` |

### $$$ — $15+ per million tokens

| Alias | Model | Input/Output | `/model` command |
|-------|-------|-------------|-----------------|
| `opus46` | Claude Opus 4.6 | $15.00/$75.00 | `/model opus46` |

---

## Presets

| # | Name | Best for | Base | Work | Frontier |
|---|------|----------|------|------|----------|
| 1 | `balanced` | Most people | flashlite | minimax | kimi25 |
| 2 | `code-machine` | Developers | devfree ⚠️ | minimax | codex52 |
| 3 | `claude-diehards` | Claude fans | haiku | sonnet | opus46 |
| 4 | `big-context` | Huge files | flash | grokfast | gem3pro |
| 5 | `openai-focused` | OpenAI fans | mini | gpt51 | gpt52 |
| 6 | `tool-master` | MCP/tools | gem3flash | kimi25 | gpt52 |
| 7 | `ultra-budget` | Tight budget | mimo ⚠️ | deepseek | kimi25 |
| 8 | `free-tier` | $0 only | mimo ⚠️ | devfree ⚠️ | glm ⚠️ |

---

## Tips

- **Cheapest reliable model:** `/model deepseek` — $0.14/M input, rock solid
- **Best value coder:** `/model minimax` — $0.28/M input, top SWE-bench scores
- **Cheapest frontier:** `/model kimi25` — $0.50/M input, 1500 parallel tool calls
- **Biggest context:** `/model grokfast` — 2M tokens, or `/model gem3pro` — 1M tokens
- **Most powerful:** `/model opus46` — but $15/M input, use sparingly
