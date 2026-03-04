---
name: workspace-analyzer
description: "Analyzes OpenClaw workspace structure and content to identify maintenance needs, bloat, duplicates, and organization issues. Outputs a JSON report for the agent to review and act upon."
version: "1.1.0"
metadata:
  {"openclaw":{"emoji":"📊","requires":{"bins":["python3"]}, "tags":["workspace", "maintenance", "analysis", "health"]}}
---

# Workspace Analyzer

> "Scans, analyzes, and reports. The agent decides."

---

## Overview

A self-improving agent needs a clean workspace. This skill analyzes any OpenClaw workspace to:
1. **Detect** core files dynamically (adapts to workspace changes)
2. **Analyze** content for issues (bloat, duplicates, broken links)
3. **Validate** single source of truth (content in multiple places)
4. **Report** actionable insights for the agent to act upon

**Key Principle:** The script analyzes → the agent decides → the agent acts.

---

## Installation

```bash
# Clone or copy to your skills folder
cp -r workspace-analyzer/ ~/.openclaw/workspace/skills/
```

---

## Usage

### Run Analysis

```bash
# Full analysis (default)
python3 skills/workspace-analyzer/scripts/analyzer.py

# Quick scan (structure only, no content analysis)
python3 skills/workspace-analyzer/scripts/analyzer.py --quick

# Specific workspace
python3 skills/workspace-analyzer/scripts/analyzer.py --root /path/to/workspace

# Output to file
python3 skills/workspace-analyzer/scripts/analyzer.py --output report.json
```

---

## Output Format

```json
{
  "scan_info": {
    "root": "/home/user/.openclaw/workspace",
    "timestamp": "2026-02-21T18:00:00Z",
    "files_scanned": 291
  },
  "core_files_detected": {
    "kai_core": {
      "files": ["SOUL.md", "OPERATING.md", ...],
      "count": 11
    },
    "mission_control": {...},
    "agent_cores": {...},
    "skills": {...}
  },
  "analysis": {
    "SOUL.md": {
      "category": "kai_core",
      "line_count": 450,
      "sections": [...],
      "wiki_links": [...],
      "issues": [...]
    }
  },
  "single_source_validation": {
    "skill_graph": {
      "status": "PASS/FAIL",
      "locations": ["AGENTS.md", "OPERATING.md", "SOUL.md"],
      "recommendation": "Reference all to SUB_CONSCIOUS.md"
    },
    "memory_architecture": {...},
    "image_handling": {...}
  },
  "recommendations": [
    {"action": "FIX_DUPLICATE_CONTENT", "topic": "skill_graph", "files": ["AGENTS.md", "OPERATING.md"], "severity": "CRITICAL"},
    {"action": "REVIEW_BLOAT", "file": "OPERATING.md", "severity": "WARN"},
    {"action": "CHECK_DUPLICATE", "severity": "WARN"},
    {"action": "CHECK_BROKEN_LINK", "severity": "INFO"}
  ],
  "summary": {
    "total_files": 291,
    "total_issues": 17,
    "total_recommendations": 25
  }
}
```

---

## Single Source of Truth Validation

### What It Checks

The analyzer validates that each topic exists in exactly ONE place:

| Topic | Expected Single Source |
|-------|----------------------|
| Skill Graph | SUB_CONSCIOUS.md |
| Memory Architecture | OPERATING.md or SUB_CONSCIOUS.md |
| Message Reactions | SUB_CONSCIOUS.md |
| Image Handling | OPERATING.md |
| Session Bootstrap | AGENTS.md |

### Detection Logic

1. **Scan all core files** for key section headings
2. **Build content map** of where each topic appears
3. **Flag violations** where topic appears in 2+ places
4. **Recommend fix** by pointing to single source

### Example Output

```json
{
  "single_source_validation": {
    "skill_graph": {
      "status": "FAIL",
      "locations": ["AGENTS.md:285", "OPERATING.md:56", "SOUL.md:52"],
      "severity": "CRITICAL",
      "recommendation": "Consolidate to SUB_CONSCIOUS.md, reference from others"
    },
    "memory_architecture": {
      "status": "FAIL", 
      "locations": ["AGENTS.md:157", "OPERATING.md:74", "OPERATING.md:193"],
      "severity": "CRITICAL",
      "recommendation": "Remove duplicate section at OPERATING.md:193"
    }
  }
}
```

---

## Features

### Dynamic Core File Detection

Automatically detects core files based on location patterns:

| Category | Pattern | Example |
|----------|---------|---------|
| KAI Core | Root *.md | SOUL.md, OPERATING.md |
| Mission Control | mission_control/*GUIDELINES.md | MISSION_CONTROL_GUIDELINES.md |
| Agent Cores | mission_control/agents/*/*.md | designer/SOUL.md |
| Skills | skills/*/SKILL.md | react-expert/SKILL.md |
| SUB_CONSCIOUS | Root SUB_CONSCIOUS.md | SUB_CONSCIOUS.md |

### Category-Specific Thresholds

Bloat thresholds vary by category:

| Category | Warning | Critical |
|----------|---------|----------|
| kai_core | 400 | 600 |
| mission_control | 500 | 800 |
| agent_cores | 300 | 500 |
| skills | 600 | 1000 |
| memory | 500 | 800 |
| docs | 400 | 600 |
| SUB_CONSCIOUS | 100 | 200 |

### Issue Detection

- **BLOAT_WARNING**: File exceeds warning threshold
- **BLOAT_CRITICAL**: File exceeds critical threshold
- **ORPHAN_WARNING**: File not modified in 30+ days
- **DUPLICATE_CONTENT**: Same topic in multiple files
- **BROKEN_WIKI_LINK**: Wiki-link may not match any file

---

## Recommendations

The analyzer generates actionable recommendations:

| Action | Severity | Description | What To Do |
|--------|----------|-------------|------------|
| FIX_DUPLICATE_CONTENT | CRITICAL | Same content in 2+ files | Consolidate to single source |
| REVIEW_BLOAT | WARN/CRITICAL | File is too large | Review if legitimate or split |
| REVIEW_ORPHAN | INFO | File hasn't been modified | Archive if no longer needed |
| CHECK_DUPLICATE | WARN | Potential duplicate files | Verify if intentional or merge |
| CHECK_BROKEN_LINK | INFO | Wiki-link may be broken | Verify if skill exists |
| CHECK_MISSING | WARN | Expected core files not found | Create if needed |

---

## Fix Instructions for Agents

When duplicate content is detected, follow these steps:

### Step 1: Identify the True Source

Determine which file should be the single source:

| Topic | Should Be In |
|-------|-------------|
| Reflex behaviors | SUB_CONSCIOUS.md |
| Session bootstrap | AGENTS.md |
| Procedures | OPERATING.md |
| Identity principles | SOUL.md |
| Knowledge index | KNOWLEDGE_GRAPH.md |

### Step 2: Update Non-Source Files

Replace duplicate content with references:

```markdown
**Topic:** See [[SUB_CONSCIOUS.md]] for procedures.
```

### Step 3: Verify Bootstrap Injection

Ensure new files are injected at session start:

Check `~/.openclaw/openclaw.json`:
```json
{
  "hooks": {
    "internal": {
      "entries": {
        "bootstrap-extra-files": {
          "enabled": true,
          "paths": ["SUB_CONSCIOUS.md", "self-improving/memory.md"]
        }
      }
    }
  }
}
```

### Step 4: Commit Changes

```bash
git add -A
git commit -m "Fix duplicate content - consolidate to single source"
```

---

## Interpretation Guide

### How to Use Results

**Step 1: Prioritize by Severity**
```
CRITICAL → Review immediately
WARN → Review during next maintenance
INFO → Review during weekly cleanup
```

**Step 2: Check Single Source Validation**
```
FAIL → Fix duplicate content first (most important)
PASS → Move to other issues
```

**Step 3: Understand Context**
- **BLOAT** = Informational, not all need fixing
  - Reference docs (skills/*/references/*.md) can be legitimately large
  - Research logs are consolidations - consider splitting by date
  - Session logs - archive old ones
  
- **DUPLICATES** = Check if intentional
  - IDENTITY files = Expected (agent templates)
  - REVIEW files = May need consolidation
  - LESSONS files = OK (different skills)
  
- **BROKEN LINKS** = Usually false positives
  - Links to skills like [[blogwatcher]] ARE valid
  - Skills have SKILL.md suffix - analyzer doesn't detect this
  - Only flag if link to core file is truly broken

**Step 4: Take Action**
1. Don't auto-fix - review first
2. Archive old session logs monthly
3. Split large research logs by topic
4. Keep reference docs as-is (legitimate)
5. **Fix duplicate content** by consolidating to single source

---

## Integration

### With Heartbeat

Add to your HEARTBEAT.md maintenance section:

```markdown
## 7. Memory + Workspace Maintenance

### Run Workspace Analyzer
python3 skills/workspace-analyzer/scripts/analyzer.py --output /tmp/analysis.json

### Review Single Source Validation
- Check for DUPLICATE_CONTENT issues
- Fix by consolidating to single source

### Review Recommendations
- Check recommendations in output
- Prioritize by severity
- Fix issues manually
```

### Output to Memory

Save analysis results for later review:

```bash
python3 skills/workspace-analyzer/scripts/analyzer.py \
  --output memory/$(date +%Y-%m-%d)-workspace-analysis.json
```

---

## Safety & Security

### Read-Only
- Never modifies files
- Only reads and analyzes

### No Secrets
- Never reads API keys
- Never accesses credentials
- Only analyzes file metadata and content structure

### Safe Output
- Only contains: file paths, sizes, line counts, recommendations
- No sensitive data exposed

---

## Limitations

- **No auto-fix:** Script reports, agent must decide and act
- **Wiki-link false positives:** Links to external skills may appear broken
- **Date-based duplicate detection:** May miss non-date-based duplicates

---

## Examples

### Sample Output - Single Source Validation

```json
{
  "single_source_validation": {
    "skill_graph": {
      "status": "FAIL",
      "files": ["AGENTS.md", "OPERATING.md", "SOUL.md"],
      "severity": "CRITICAL",
      "recommendation": "Reference all to SUB_CONSCIOUS.md"
    },
    "memory_architecture": {
      "status": "FAIL",
      "files": ["AGENTS.md", "OPERATING.md"],
      "severity": "CRITICAL", 
      "recommendation": "Remove duplicate in OPERATING.md"
    },
    "message_reactions": {
      "status": "PASS",
      "files": ["SUB_CONSCIOUS.md"],
      "severity": "OK"
    }
  }
}
```

### Sample Output - Recommendations

```json
[
  {
    "action": "FIX_DUPLICATE_CONTENT",
    "topic": "skill_graph",
    "files": ["AGENTS.md:285", "OPERATING.md:56", "SOUL.md:52"],
    "severity": "CRITICAL",
    "recommendation": "Replace with reference to SUB_CONSCIOUS.md"
  },
  {
    "action": "REVIEW_BLOAT",
    "file": "OPERATING.md",
    "category": "kai_core",
    "reason": "503 lines - consider splitting (threshold: 400)",
    "severity": "WARN"
  }
]
```

---

## Skill Graph

This skill is related to:

- [[mcporter]] - For MCP server analysis
- [[clean-workspace]] - For actual cleanup tasks
- [[qmd]] - For memory organization

---

## Changelog

### v1.1.0 (2026-02-24)
- Added single source of truth validation
- Added duplicate content detection (same topics in multiple files)
- Added FIX_DUPLICATE_CONTENT recommendation type
- Added SUB_CONSCIOUS category
- Added fix instructions for agents

### v1.0 (2026-02-21)
- Initial release
- Basic file analysis
- Core file detection
- Bloat detection

---

*Last updated: 2026-02-24*
