---
name: hsk-learning
description: "HSK Chinese learning system with spaced repetition mastery tracking, vocabulary analysis, and adaptive quiz generation. Use when: (1) tracking HSK vocabulary progress, (2) generating adaptive quizzes, (3) analyzing Chinese language exposure in conversations, (4) managing spaced repetition reviews. NOT for: general language learning beyond HSK, pronunciation practice, or handwriting practice."
metadata:
  openclaw:
    emoji: "📚"
    requires:
      node: true
    install:
      - id: "init"
        kind: "node"
        script: "scripts/init-mastery-db.js"
        label: "Initialize mastery database (first-time setup)"
---

# HSK Learning Skill for OpenClaw

**Purpose**: Provide a comprehensive HSK Chinese learning system with spaced repetition mastery tracking, vocabulary analysis, and adaptive quiz generation.

**Version**: 1.1.0  
**Author**: Claw  
**Date**: 2026-02-18

## Features

- **Spaced Repetition Mastery System**: Tracks mastery state (unknown/learning/mastered) for all 2,211 HSK 3.0 words using SM‑2 inspired algorithm.
- **Vocabulary Exposure Analysis**: Scans conversation logs, categorizes CJK tokens by HSK level, generates progress reports.
- **Quiz Log Parsing**: Automatically extracts vocabulary and correctness from quiz‑performance logs.
- **Adaptive Quiz Generation**: Creates quizzes prioritizing words due for review based on mastery.
- **Comprehensive Toolset**: Six tools for updating, querying, and managing the HSK learning system.

## Tools

### 1. `hsk_update_vocab_tracker`
Scans `memory/*.md` files for CJK tokens, categorizes by HSK level, updates `memory/hsk‑word‑report.md`.

**Parameters**:
- `force` (boolean): Force update even if recent scan exists (default: false)

### 2. `hsk_update_mastery_from_quiz`
Processes quiz‑performance logs and updates mastery database.

**Parameters**:
- `date` (string): Specific date (YYYY‑MM‑DD) or "all" for all logs (default: "all")

### 3. `hsk_get_mastery_stats`
Returns mastery statistics: unknown/learning/mastered counts, breakdown by HSK level.

**Parameters**:
- `format` (string): Output format: "text", "json", or "markdown" (default: "text")

### 4. `hsk_get_due_words`
Lists words due for review based on spaced repetition schedule.

**Parameters**:
- `limit` (number): Maximum words to return (default: 20)
- `level` (number): Filter by HSK level (1‑6), 0 for all (default: 0)

### 5. `hsk_generate_quiz`
Generates adaptive quiz based on mastery state.

**Parameters**:
- `difficulty` (string): "review", "learning", "new", or "mixed" (default: "mixed")
- `format` (string): "simple", "listening", "reading", "writing", or "full" (default: "simple")

### 6. `hsk_parse_quiz_log`
Parses a quiz‑performance log file and extracts vocabulary.

**Parameters**:
- `filePath` (string): Path to quiz log file (required)

## Data Files

The skill maintains these data files in its `data/` directory:

| File | Purpose |
|------|---------|
| `hsk‑word‑to‑level.json` | HSK 3.0 word‑to‑level mapping (2,211 words) |
| `hsk‑database.json` | Full HSK database with metadata |
| `hsk‑mastery‑db.json` | Mastery state for all HSK words (user-specific) |

## Setup & Installation

### For New Users (First-Time Setup)

1. **Install the skill** via ClawHub:
   ```bash
   clawhub install hsk-learning
   ```

2. **Initialize your personal mastery database** (required for each user):
   ```bash
   cd skills/hsk-learning
   node scripts/init-mastery-db.js
   ```
   This creates a fresh `hsk-mastery-db.json` with all 2,211 HSK words in "unknown" state.

3. **Optional: Configure user settings**:
   ```bash
   cp data/user-config.template.json data/user-config.json
   # Edit user-config.json with your preferences
   ```

4. **Restart OpenClaw gateway** to load the skill:
   ```bash
   openclaw gateway restart
   ```

### Data Files Structure

| File | Purpose | User-Specific? | Git Ignored? |
|------|---------|----------------|--------------|
| `hsk-database.json` | HSK word database (shared) | ❌ No | ❌ No |
| `hsk-word-to-level.json` | Word-to-level mapping (shared) | ❌ No | ❌ No |
| `hsk-mastery-db.json` | Your personal mastery tracking | ✅ Yes | ✅ Yes |
| `user-config.json` | Your preferences (optional) | ✅ Yes | ✅ Yes |
| `user-config.template.json` | Configuration template | ❌ No | ❌ No |

### Git Repository Setup

When publishing or contributing to this skill:

1. **User-specific files are automatically ignored** via `.gitignore`
2. **Shared data files** (HSK database) are included
3. **Initialization script** creates user data on first run
4. **No personal data** is committed to the repository

## Testing the Skill

After restart, test basic functionality:

```javascript
// In an OpenClaw session
hsk_get_mastery_stats({ format: 'text' });
hsk_update_mastery_from_quiz({ date: 'all' });
hsk_get_due_words({ limit: 5 });
```

## Maintenance

- **Mastery database updates automatically** when quiz logs are processed.
- **Vocabulary report updates** via cron job or manual trigger.
- **System health**: Consider adding a weekly health‑check cron job.

## Next Steps

1. **Update all HSK‑related cron jobs** to use skill tools.
2. **Enhance quiz generation** with GPT‑based passage creation.
3. **Add listening practice** with audio generation.
4. **Implement HSK mock exams** (full test simulation).

## References

- **HSK 3.0 word lists**: mandarinbean.com
- **Spaced repetition algorithm**: SM‑2 (SuperMemo)
- **OpenClaw skill documentation**: https://docs.openclaw.ai

---
*Part of William's personalized HSK learning system. Integrated with OpenClaw cron scheduler for automated operation.*