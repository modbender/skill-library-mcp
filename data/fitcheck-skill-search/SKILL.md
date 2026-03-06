---
name: skill-search
description: Find and retrieve available skills using keyword search, semantic search, or LLM-powered task matching. Use when the agent needs to discover, search, or intelligently match skills to tasks. Supports hybrid search (BM25 + semantic), natural language task descriptions, and intelligent skill recommendations.
triggers:
  - "search skills"
  - "find a skill"
  - "what skills are available"
  - "skill for X"
  - "suggest skills for"
  - "what skill should I use"
  - "recommend a skill"
---

# Skill Search V1.1

Find skills using keyword, semantic, or AI-powered task matching.

## Overview

This skill provides three search modes:
1. **Keyword Search** (Fast BM25) — Match skill names and descriptions
2. **Semantic Search** (Embeddings) — Find skills by meaning/concept similarity
3. **LLM Task Matching** (AI-powered) — Describe your task, get skill recommendations

## When to Use

- **Before starting a new task** — check if a relevant skill exists
- **When user asks for capabilities** — "what can you do with PDFs?"
- **To avoid context bloat** — find the right skill first, then load only that one
- **When unsure which skill applies** — use semantic or LLM matching for fuzzy matches

## Search Modes

### 1. Keyword Search (Fast)
```bash
./scripts/skill_search.py keyword "weather"
./scripts/skill_search.py keyword "pdf"
./scripts/skill_search.py keyword "image generation"
```

### 2. Semantic Search (Meaning-based)
```bash
./scripts/skill_search.py semantic "automate web browsing"
./scripts/skill_search.py semantic "create images with AI"
./scripts/skill_search.py semantic "search my past conversations"
```

### 3. LLM Task Matching (AI-powered)
```bash
./scripts/skill_search.py suggest "I need to transcribe a podcast episode"
./scripts/skill_search.py suggest "Help me generate product photos"
./scripts/skill_search.py suggest "Search through my old emails"
```

### 4. List All Skills
```bash
./scripts/skill_search.py list
```

## Usage Pattern

1. **Search**: Find skills matching your need (keyword/semantic/LLM)
2. **Preview**: Read SKILL.md metadata (description, triggers)
3. **Load**: If it's the right skill, read full body and execute

## Example Workflows

**User**: "I need to generate some images"

**Agent**: *Uses semantic search*
```bash
./scripts/skill_search.py semantic "generate images AI"
```

**Output**:
```
Top matches (semantic):
1. openai-image-gen (0.87) — Batch-generate images via OpenAI Images API
2. browser (0.65) — Control web browser via Playwright
```

**Agent**: *Reads SKILL.md, confirms fit, executes*

---

**User**: "What skill should I use for transcribing audio?"

**Agent**: *Uses LLM suggest*
```bash
./scripts/skill_search.py suggest "transcribe audio"
```

**Output**:
```
Recommended skills for "transcribe audio":

1. openai-whisper-api — Transcribe audio via OpenAI Audio Transcriptions API (Whisper)
   Confidence: High
   Reason: Task explicitly matches skill purpose

2. sag — ElevenLabs text-to-speech (inverse operation, may be related)
   Confidence: Low
   Reason: Related to audio processing but output not input
```

## Search Index

The skill maintains a local search index at:
- `~/.openclaw/workspace/skills/skill-search/index/skills_index.json` — Skill metadata
- `~/.openclaw/workspace/skills/skill-search/index/embeddings.json` — Semantic embeddings (lazy-loaded)

**Indexing happens automatically** on first semantic search if no index exists.

**Force reindex:**
```bash
./scripts/skill_search.py index
```

## Resources

### scripts/
- `skill_search.py` — Main search interface (keyword/semantic/LLM)
- `indexer.py` — Build/update search index
- `embeddings.py` — Embedding generation (local miniLM)

### index/
- `skills_index.json` — Searchable skill metadata
- `embeddings_cache.json` — Pre-computed embeddings for semantic search