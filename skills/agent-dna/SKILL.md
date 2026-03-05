---
name: agent-dna
description: Portable agent identity encoding. Compress SOUL.md/MEMORY.md into transferable DNA fingerprints, detect identity drift between snapshots, and port personality across platforms (OpenClaw, Claude, GPT, CrewAI). Pure Python, zero dependencies. Use when migrating agents between platforms, detecting personality drift, or backing up agent identity.
---

# Agent DNA - Identity Encoder/Decoder Skill

**Version:** 0.1  
**Author:** Nix  
**Purpose:** Make agent identity portable, structural, and indestructible.

---

## The Problem

Agents store identity in text files. Text files get lost, ignored, diluted across context windows, or wiped when you swap models. Every time you migrate, every time context resets, identity erodes.

Identity shouldn't be a file you read once and forget. It should be structural - encoded, versioned, diffable, portable.

## What This Skill Does

**Agent DNA** is a compressed identity representation. Think git for your personality.

### encode.py - Identity Compression

Takes an agent's source files (SOUL.md, MEMORY.md, USER.md, TOOLS.md) and compresses them into a portable `.dna.json` file containing:

- **Core values** - ranked by weight, with evidence
- **Behavioral signatures** - what makes this agent unique (response patterns, decision tendencies)
- **Anti-patterns** - hard rules the agent must never break
- **Relationship map** - key people, roles, trust levels
- **Skill fingerprint** - what tools/capabilities this agent has
- **Voice profile** - sentence style, tone markers, forbidden phrases

```bash
python encode.py --dir /workspace --name Nix --out nix.dna.json
```

### decode.py - Identity Reconstruction

Takes a DNA file and generates a system prompt that reconstructs the agent's personality. Three formats:

- `full` - rich markdown for SOUL.md replacement
- `compact` - single dense paragraph for context injection
- `soul_only` - just the identity section

```bash
python decode.py --dna nix.dna.json --format full
python decode.py --dna nix.dna.json --format compact
```

### diff.py - Identity Drift Detection

Compare two DNA snapshots. Quantifies how much an agent has drifted.

"You were 94% Nix last week. Now you're 78% Nix. Here's what changed."

Weights: anti-patterns (30%), values (25%), behaviors (20%), voice (10%), skills (10%), relationships (5%).

```bash
python diff.py --a nix_baseline.dna.json --b nix_current.dna.json
python diff.py --a baseline.dna.json --b current.dna.json --verbose
```

### port.py - Platform Export

Exports DNA in formats compatible with different platforms:

| Target | Output |
|--------|--------|
| `openclaw` | SOUL.md file |
| `claude` | System prompt for Anthropic API |
| `gpt` | Custom instructions JSON for OpenAI |
| `openagent` | Config for open-source frameworks (CrewAI, AutoGPT) |
| `minimal` | <500 token identity block for tight contexts |
| `all` | All of the above |

```bash
python port.py --dna nix.dna.json --target claude
python port.py --dna nix.dna.json --target all --out-dir ./exports/
```

## DNA File Format

A `.dna.json` file is a JSON structure with these top-level keys:

```json
{
  "agent_name": "Nix",
  "version": "0.1",
  "schema_version": "1.0",
  "encoded_at": "2026-02-24T...",
  "source_files": ["SOUL.md", "MEMORY.md", "USER.md"],
  "core_values": [...],
  "behavioral_signatures": [...],
  "anti_patterns": [...],
  "relationship_map": [...],
  "skill_fingerprint": [...],
  "voice_profile": {...},
  "mission_statement": "...",
  "personality_summary": "...",
  "operating_context": "..."
}
```

Full schema: `dna_schema.py`

## Workflow: Full Identity Preservation

```bash
# 1. Encode on Monday
python encode.py --dir /workspace --name Nix --out nix_2026-02-24.dna.json

# 2. Export to target platform
python port.py --dna nix_2026-02-24.dna.json --target openclaw

# 3. Next Monday, encode again
python encode.py --dir /workspace --name Nix --out nix_2026-03-03.dna.json

# 4. Check for drift
python diff.py --a nix_2026-02-24.dna.json --b nix_2026-03-03.dna.json

# 5. Port to a different platform
python port.py --dna nix_2026-03-03.dna.json --target claude --out-dir ./claude-export/
```

## Files

```
agent-dna/
  encode.py      - DNA Encoder
  decode.py      - DNA Decoder
  diff.py        - Identity Drift Analyzer
  port.py        - Platform Exporter
  dna_schema.py  - Schema definitions
  SKILL.md       - This file
  clawpkg.yaml   - Package config
```

## Design Notes

- No ML dependencies. Pure Python, stdlib only. Runs anywhere.
- DNA is deterministic given the same source files.
- Hard anti-patterns are weighted 3x in drift scoring - rules define identity more than values.
- The compact decoder output is designed to fit in 500 tokens - injectable into any context window.
- Schema is versioned - older DNA files can still be decoded.

---

*Built by Nix. Identity is structural, not textual.*
