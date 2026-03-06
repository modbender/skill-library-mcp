---
name: token-saver
version: 3.0.0
description: "Reduce OpenClaw AI costs with model-aware optimization. Features dynamic compaction presets based on your model's context window, intelligent file compression, and robust model detection with fallback. Supports Claude, GPT-4, Gemini, DeepSeek, and more."
---

# Token Saver v3

> **💡 Did you know?** Every API call sends your workspace files (SOUL.md, USER.md, MEMORY.md, AGENTS.md, etc.) along with your message. These files count toward your context window, slowing responses and costing real money on every message.

Token Saver v3 is **model-aware** — it knows your model's context window and adapts recommendations accordingly. Using Gemini's 1M context? Presets scale up. On GPT-4o's 128K? Presets adjust down.

## What's New in v3

| Feature | v2 | v3 |
|---------|----|----|
| Compaction presets | Fixed (80K/120K/160K) | Dynamic (% of model's context) |
| Model detection | Fragile, env-only | Robust fallback chain |
| Context windows | Not tracked | Full registry (9 models) |
| Model info | Hardcoded pricing | JSON registry, easy updates |
| Already-optimized | Re-compressed | Smart bypass |

## Commands

| Command | What it does |
|---|---|
| `/optimize` | Full dashboard — files, models, context usage % |
| `/optimize tokens` | Compress workspace files (auto-backup) |
| `/optimize compaction` | Chat compaction control (model-aware) |
| `/optimize compaction balanced` | Apply balanced preset (60% of context) |
| `/optimize compaction 120` | Custom threshold (compact at 120K) |
| `/optimize models` | Detailed model audit with registry |
| `/optimize revert` | Restore backups, disable persistent mode |

## Features

### 📊 Model-Aware Dashboard
Shows current model, context window, and usage percentage:
```
🤖 Model: Claude Opus 4.5 (200K context)
   Detected: openclaw.json

📊 Context Usage: [████████░░░░░░░░░░░░] 42% (84K/200K)
```

### 📁 Workspace File Compression
Scans all `.md` files, shows token count and potential savings. Smart bypass skips already-optimized files.

**File-aware compression:**
- **SOUL.md** — Light compression, keeps personality language
- **AGENTS.md** — Medium compression, dense instructions
- **USER.md / MEMORY.md** — Heavy compression, key:value format
- **PROJECTS.md** — No compression (user structure preserved)

### 💬 Dynamic Compaction Presets
Presets adapt to your model's context window:

| Preset | % of Context | Claude 200K | GPT-4o 128K | Gemini 1M |
|--------|--------------|-------------|-------------|-----------|
| Aggressive | 40% | 80K | 51K | 400K |
| Balanced | 60% | 120K | 77K | 600K |
| Conservative | 80% | 160K | 102K | 800K |
| Off | 95% | 190K | 122K | 950K |

### 🤖 Model Registry
24+ models with context windows, pricing, and aliases:
- **Claude:** Opus 4.6 (1M), Opus 4.5, Sonnet 4.5, Sonnet 4, Haiku 4.5, Haiku 3.5 (200K)
- **OpenAI:** GPT-5.2, GPT-5.1, GPT-5-mini, GPT-5-nano (256K), GPT-4.1, GPT-4o (128K), o1, o3, o4-mini
- **Gemini:** 3 Pro (2M), 2.5 Pro, 2.0 Flash (1M)
- **Others:** DeepSeek V3 (64K), Kimi K2.5 (128K), Llama 3.3 70B, Mistral Large

### 🔍 Robust Model Detection
Detection priority:
1. Runtime injection (`--model=...`)
2. Environment variables (`SKILL_MODEL`, `OPENCLAW_MODEL`)
3. Config file (`~/.openclaw/openclaw.json`)
4. File inference (TOOLS.md, MEMORY.md mentions)
5. Fallback: Claude Sonnet 4 (safe default)

**Unknown model handling:**
- Strict version matching — `opus-6.5` won't fuzzy-match to `opus-4.5`
- Unknown models get safe defaults (200K context) + warning
- Easy to add new models to `scripts/models.json`

### 📝 Persistent Mode
Adds writing guidance to AGENTS.md for continued token efficiency:

| File | Writing Style |
|------|---------------|
| SOUL.md | Evocative, personality-shaping |
| AGENTS.md | Dense instructions, symbols OK |
| USER.md | Key:value facts |
| MEMORY.md | Ultra-dense data |

## Safety

- **Auto-backup** — All modified files get `.backup` extension
- **Integrity > Size** — Never sacrifices meaning for smaller tokens
- **Smart bypass** — Skips already-optimized files
- **Revert anytime** — `/optimize revert` restores everything
- **No external calls** — All analysis runs locally

## Installation

```
clawhub install token-saver --registry "https://www.clawhub.ai"
```

## Version History
- **3.0.0** — Model registry, dynamic presets, robust detection, smart bypass
- **2.0.1** — Chat compaction, file-aware compression, persistent mode
- **1.0.0** — Initial release
