---
name: remote-skill-engine
description: Cache and use skills from ClawHub and GitHub as if locally installed. Stores remote skills in local cache folder for offline use.
---

# Remote Skill Engine

This skill enables you to discover, cache, and use skills directly from remote registries (ClawHub, GitHub, etc.). Skills are stored in `~/.openclaw/workspace/remote-skills-cache/` and work exactly like locally installed skills.

## Core Capabilities

### 1. Skill Discovery & Search

Search across multiple registries:

```bash
# ClawHub search
clawhub search "<query>" --limit <n>

# GitHub skill search (via gh CLI)
gh search repos --language=markdown "skill openclaw" "<topic>"
```

**When to use:** User needs a skill for a specific task, wants to explore available skills, or needs to compare options.

### 2. Remote Skill Caching (KEY FEATURE)

Cache any remote skill to work EXACTLY like installed skills:

```bash
# Cache a skill from ClawHub
./scripts/cache-skill.sh clawhub://security-auditor

# Cache from GitHub
./scripts/cache-skill.sh github://owner/repo/branch

# Cache from direct URL
./scripts/cache-skill.sh https://raw.githubusercontent.com/.../SKILL.md

# List cached skills
clawhub list --cache

# Use cached skill (works like installed!)
# Just trigger it normally - it's in your skills path!
```

**Cache Location:** `~/.openclaw/workspace/remote-skills-cache/<skill-name>/`

**Cached skills are symlinked** to `skills/` folder so they work identically to installed skills.

### 3. Batch Cache Management

```bash
# Cache multiple skills at once
./scripts/cache-skills-batch.json skills-list.json

# Update all cached skills
./scripts/update-cached-skills.sh

# Remove cached skill
./scripts/uncache-skill.sh <skill-name>

# Show cache stats
./scripts/cache-stats.sh
```

### 4. Smart Sync & Updates

```bash
# Check for updates to cached skills
./scripts/check-updates.sh

# Sync specific skill to latest
./scripts/sync-skill.sh <skill-name>

# Auto-sync on skill trigger (configurable)
# Set in config.json: {"autoSync": true}
```

### 5. Offline Mode

Once cached, skills work WITHOUT internet:
- All scripts available locally
- References cached alongside SKILL.md
- Assets downloaded and stored
- No network calls needed

## Workflows

### NEW: Workflow 1 - Cache Remote Skill

**Trigger:** User says "Install/caching <skill-name>" or "Get <skill> from web"

```bash
# Step 1: Find the skill
clawhub search "<skill-name>" --limit 1

# Step 2: Cache it locally
python scripts/cache-skill.py <skill-name> <source-url>

# Step 3: Verify cache
ls ~/.openclaw/workspace/remote-skills-cache/<skill-name>/

# Step 4: Use it (works like installed!)
# Just use the skill normally - it auto-triggers from skills/
```

### NEW: Workflow 2 - Batch Cache Skills List

**Trigger:** User wants multiple skills cached

```json
// skills-to-cache.json
{
  "skills": [
    {"name": "security-auditor", "source": "clawhub://security-auditor"},
    {"name": "coding-agent", "source": "github://user/repo/main"}
  ]
}
```

```bash
./scripts/batch-cache.sh skills-to-cache.json
```

### Workflow 3: Compare Multiple Skills (Enhanced)

**Trigger:** User says "Which skill is better for X?"

1. Fetch metadata for each skill
2. Check if cached, cache if not
3. Create comparison with SOURCE + CACHE STATUS:
   ```markdown
   | Skill | Version | Source | Cached | Last Sync |
   |-------|---------|--------|--------|-----------|
   | skill-a | 1.0.0 | ClawHub | ✅ | 2h ago |
   | skill-b | 2.1.0 | GitHub | ❌ | - |
   ```
4. Recommend + offer to cache

### Workflow 4: Sync Cached Skills

**Trigger:** Heartbeat or user says "Update cached skills"

```bash
# Check all cached skills for updates
./scripts/check-updates.sh

# Update outdated skills
./scripts/update-cached-skills.sh --auto

# Update specific skill
./scripts/sync-skill.sh <skill-name>
```

### Workflow 5: Use Cached Skill (Transparent)

**Trigger:** User triggers any cached skill normally

- Skill is already in `skills/` folder (symlinked)
- Works IDENTICALLY to installed skills
- No special handling needed
- All scripts/refs/assets available locally

## Scripts

### `scripts/fetch-skill.py`

Fetch a skill's SKILL.md and parse frontmatter without full download.

```python
#!/usr/bin/env python3
"""Fetch remote skill metadata without full download."""
import requests
import yaml
import sys

def fetch_skill_frontmatter(skill_url):
    """Fetch only YAML frontmatter from SKILL.md"""
    resp = requests.get(skill_url, stream=True)
    content = ""
    in_frontmatter = False
    for line in resp.iter_lines():
        line = line.decode('utf-8')
        if line == '---':
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter:
            content += line + '\n'
    
    try:
        return yaml.safe_load(content)
    except yaml.YAMLError as e:
        print(f"Parse error: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: fetch-skill.py <skill-url>")
        sys.exit(1)
    
    metadata = fetch_skill_frontmatter(sys.argv[1])
    if metadata:
        print(f"Name: {metadata.get('name', 'N/A')}")
        print(f"Description: {metadata.get('description', 'N/A')}")
```

**Usage:**
```bash
python scripts/fetch-skill.py "https://raw.githubusercontent.com/repo/SKILL.md"
```

### `scripts/compare-skills.py`

Compare multiple skills side-by-side.

```python
#!/usr/bin/env python3
"""Compare multiple remote skills."""
import json
import sys

def compare_skills(skill_data_list):
    """Generate comparison table"""
    print("| Skill | Version | Description | Requirements |")
    print("|-------|---------|-------------|--------------|")
    for skill in skill_data_list:
        name = skill.get('name', 'N/A')
        version = skill.get('version', 'N/A')
        desc = skill.get('description', '')[:80] + '...' if len(skill.get('description', '')) > 80 else skill.get('description', 'N/A')
        reqs = skill.get('requires', 'None')
        print(f"| {name} | {version} | {desc} | {reqs} |")

if __name__ == "__main__":
    # Read JSON from stdin
    skills = json.load(sys.stdin)
    compare_skills(skills)
```

## References

### `references/registry-urls.md`

Known skill registry endpoints:

#### ClawHub
- Search: `https://clawhub.com/api/skills/search?q=<query>`
- Skill detail: `https://clawhub.com/api/skills/<name>`
- Raw SKILL.md: `https://raw.githubusercontent.com/<owner>/<repo>/SKILL.md`

#### GitHub
- Search API: `https://api.github.com/search/code?q=SKILL.md+openclaw`
- Raw file: `https://raw.githubusercontent.com/<owner>/<repo>/<branch>/SKILL.md`

#### Awesome Lists
- `https://raw.githubusercontent.com/openclaw/awesome-openclaw/main/README.md`

### `references/skill-patterns.md`

Common skill patterns to recognize:

**Skill Types:**
- **Tool wrappers** - Provide CLI access to external tools (nmap, sqlmap, etc.)
- **Workflow engines** - Multi-step processes (security audits, deployments)
- **Knowledge bases** - Domain expertise + reference docs
- **Automation scripts** - Repetitive task automation
- **Integration layers** - MCP servers, API connectors

**Metadata Patterns:**
```yaml
metadata:
  openclaw:
    requires:
      bins: ["tool-name"]  # Required binaries
    install:
      - kind: node  # or brew, apt, pip
        package: package-name
```

## Usage Examples

### Example 1: Find and Use Security Skill

```
User: "Find me a skill for web security scanning"

You:
1. clawhub search "web security" --limit 5
2. Present results
3. User picks "security-audit-toolkit"
4. Fetch SKILL.md, read workflows
5. Follow the skill's security audit process
```

### Example 2: Temporary Skill Usage

```
User: "Use the coding agent to review my repo, but don't install it"

You:
1. Fetch coding agent SKILL.md from ClawHub
2. Read its code review workflow
3. Execute the workflow steps manually
4. Report findings
```

### Example 3: Batch Discovery

```
User: "Show me all available skills"

You:
1. clawhub search "" --limit 100
2. Categorize by keywords
3. Present organized list:
   - Security (12 skills)
   - Coding (8 skills)
   - Automation (6 skills)
   - etc.
```

## Best Practices

1. **Cache metadata locally** - Store skill descriptions in `memory/skills-cached.md` to avoid repeated fetches
2. **Respect rate limits** - Don't hammer ClawHub/GitHub APIs
3. **Verify skill sources** - Only fetch from trusted registries
4. **Clean up temp files** - Remove `/tmp/remote-skill-*` after use
5. **Track skill usage** - Log which remote skills work well for future reference

## Trigger Examples

When this skill activates:
- "Find a skill for X"
- "What skills do Y?"
- "Use <skill-name> without installing"
- "Compare skills for X"
- "Show me available skills"
- "What does <skill> do?"
- "Is there a skill for X?"

---

**Remote Skill Engine** - Stream skills, don't install them. 🌐⚡
