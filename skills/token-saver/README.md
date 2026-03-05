# ⚡ Token Saver v3

> **💡 Did you know?** Every API call sends your workspace files (SOUL.md, USER.md, MEMORY.md, AGENTS.md, etc.) along with your message. These files cost real money on every message.

**Token Saver v3 is model-aware** — it knows your model's context window and adapts recommendations accordingly.

![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-3.0.0-blue)

## Quick Start

```
/optimize
```

That's it. You'll see a dashboard with your savings options.

## What's New in v3

| Feature | v2 | v3 |
|---------|----|----|
| Compaction presets | Fixed (80K/120K/160K) | **Dynamic** (% of model's context) |
| Model detection | Fragile, env-only | **Robust fallback chain** |
| Context windows | Not tracked | **Full registry (9 models)** |
| Savings estimates | Static | **Model-aware pricing** |

## Dashboard Preview

```
╭─────────────────────────────────────────────────────────╮
│  ⚡ TOKEN SAVER v3                                       │
│  Reduce AI costs by optimizing what gets sent each call │
╰─────────────────────────────────────────────────────────╯

🤖 **Model:** Claude Opus 4.5 (200K context)
   Detected: openclaw.json

📊 **Context Usage:** [████████░░░░░░░░░░░░] 42% (84K/200K)

📁 **WORKSPACE FILES** (sent every API call)
┌──────────────────────┬───────┬────────────────┐
│ File                 │ Tokens│ Can Save       │
├──────────────────────┼───────┼────────────────┤
│ 🔴 AGENTS.md          │  1180 │     -825 (70%) │
│ 🟢 SOUL.md            │   235 │    ✓ optimized │
...
```

## Commands

| Command | What It Does |
|---|---|
| `/optimize` | Dashboard with files, models, context usage |
| `/optimize tokens` | Compress workspace files (auto-backup) |
| `/optimize compaction` | Chat compaction control (model-aware) |
| `/optimize compaction balanced` | Apply balanced preset (60% of context) |
| `/optimize models` | Detailed model audit with registry |
| `/optimize revert` | Restore backups, disable persistent mode |

## Dynamic Presets

Presets adapt to your model's context window:

| Preset | % | Claude 200K | GPT-4o 128K | Gemini 1M |
|--------|---|-------------|-------------|-----------|
| Aggressive | 40% | 80K | 51K | 400K |
| Balanced | 60% | 120K | 77K | 600K |
| Conservative | 80% | 160K | 102K | 800K |

## Model Registry

9 models with context windows and pricing:
- **Claude:** Opus 4.5, Sonnet 4, Haiku 3.5 (200K)
- **Gemini:** 2.0 Flash, 2.5 Pro (1M)
- **OpenAI:** GPT-4o, GPT-4o Mini (128K)
- **Others:** DeepSeek V3 (64K), Kimi K2.5 (128K)

## File Compression

**Before** (verbose):
> When Ruben greets me in the morning, I should proactively review our task list...

**After** (compressed):
```
MORNING: greeting → review(todos+pending+urgent)
```

Same meaning. 90% fewer tokens. Real savings.

## Safety

- ✅ **Auto-backup** before any changes
- ✅ **Smart bypass** — skips already-optimized files
- ✅ **One-command revert** — `/optimize revert`
- ✅ **No external calls** — all local

## Install

```bash
# From ClawHub
clawhub install token-saver --registry "https://www.clawhub.ai"

# Or clone directly
git clone https://github.com/RubenAQuispe/token-saver.git
```

## License

MIT — Use it, modify it, share it.
