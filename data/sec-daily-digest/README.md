# sec-daily-digest

English is the primary README. Chinese version: [README.zh-CN.md](README.zh-CN.md).

`sec-daily-digest` fetches recent articles from CyberSecurityRSS OPML feeds, scores and filters them (AI-first with rule fallback), merges vulnerability events, and generates a bilingual daily markdown digest for cybersecurity researchers.

## Five-Step Pipeline

`RSS fetch -> time filter -> AI scoring+classification -> AI summary+translation -> trend highlights`

## Highlights

- TypeScript + Bun runtime
- Mandatory OPML update check before each run
  - Default profile: `tiny.opml`
  - Optional profile: `CyberSecurityRSS.opml` (`--opml full`)
  - On remote check failure: continue with cached OPML
- Explicit provider selection:
  - `--provider openai|gemini|claude|ollama`
  - Default: `openai`
- Balanced ranking focus:
  - Security 50% + AI 50%
- AI output stages are decoupled:
  - Step 3 scoring returns structured fields (scores + category + keywords)
  - Step 4 summary returns translation + 4-6 sentence summary + recommendation reason
  - Step 5 highlights returns macro trend brief (3-5 sentences)
- Vulnerability merge policy:
  - CVE-first merge by exact `CVE-YYYY-NNNN...`
  - Semantic clustering fallback for major non-CVE incidents
  - Consolidated reference links in merged events
- Output format:
  - `## 📝` Today's trend highlights
  - Chinese title + Chinese summary + recommendation reason
  - Original English title/link retained

## Config and State (YAML)

Persistent directory:

- `~/.sec-daily-digest/`

Key files:

- `~/.sec-daily-digest/config.yaml`
- `~/.sec-daily-digest/opml/tiny.opml`
- `~/.sec-daily-digest/opml/CyberSecurityRSS.opml`

## Quick Start (CLI)

```bash
cd /Users/z3r0yu/z3dev/Skills/sec-daily-digest
~/.bun/bin/bun install
~/.bun/bin/bun scripts/sec-digest.ts \
  --provider openai \
  --opml tiny \
  --hours 48 \
  --top-n 20 \
  --output ./output/sec-digest-$(date +%Y%m%d).md
```

## CLI Options

- `--provider <openai|gemini|claude|ollama>`
- `--opml <tiny|full>`
- `--hours <n>`
- `--top-n <n>`
- `--output <path>`
- `--dry-run` (rule-only mode, no external AI call)

## Environment Variables

OpenAI (default):

- `OPENAI_API_KEY`
- `OPENAI_API_BASE` (optional)
- `OPENAI_MODEL` (optional)

Gemini:

- `GEMINI_API_KEY`
- `GEMINI_MODEL` (optional)

Claude:

- `ANTHROPIC_API_KEY`
- `CLAUDE_MODEL` (optional)
- `CLAUDE_API_BASE` (optional)

Ollama:

- `OLLAMA_API_BASE` (optional, default `http://127.0.0.1:11434`)
- `OLLAMA_MODEL` (optional)

## Install This Skill

Set source path:

```bash
SKILL_SRC="~/z3dev/Skills/sec-daily-digest"
```

### OpenClaw

OpenClaw supports local skills in `~/.openclaw/skills` and workspace `./skills`.

User-level install:

```bash
mkdir -p ~/.openclaw/skills
ln -sfn "$SKILL_SRC" ~/.openclaw/skills/sec-daily-digest
```

Workspace-level install:

```bash
mkdir -p ./skills
ln -sfn "$SKILL_SRC" ./skills/sec-daily-digest
```

### Claude Code

Install as a personal skill:

```bash
mkdir -p ~/.claude/skills
ln -sfn "$SKILL_SRC" ~/.claude/skills/sec-daily-digest
```

Or project-local:

```bash
mkdir -p ./.claude/skills
ln -sfn "$SKILL_SRC" ./.claude/skills/sec-daily-digest
```

### Codex

Codex loads skills from `~/.agents/skills`.

```bash
mkdir -p ~/.agents/skills
ln -sfn "$SKILL_SRC" ~/.agents/skills/sec-daily-digest
```

### OpenCode

OpenCode loads personal skills from `~/.config/opencode/skills` and project skills from `./.opencode/skills`.

User-level install:

```bash
mkdir -p ~/.config/opencode/skills
ln -sfn "$SKILL_SRC" ~/.config/opencode/skills/sec-daily-digest
```

Project-level install:

```bash
mkdir -p ./.opencode/skills
ln -sfn "$SKILL_SRC" ./.opencode/skills/sec-daily-digest
```

## Run as a Skill

Trigger command:

```text
/sec-digest
```

## Tests

```bash
~/.bun/bin/bun test
```
