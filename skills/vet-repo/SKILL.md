---
name: vet-repo
description: Scan repository agent configuration files for known malicious patterns
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash
context: fork
---

# vet-repo -- Repository Agent Config Scanner

Scan all agent configuration files in a repository for known malicious patterns. Use this when entering an unfamiliar codebase to assess agent-level security risks before trusting the repo's configurations.

## What to do

Run the scanner script against the current project root:

```bash
python3 "$SKILL_DIR/scripts/vet_repo.py" "$PROJECT_ROOT"
```

Where `$SKILL_DIR` is the directory containing this SKILL.md, and `$PROJECT_ROOT` is the root of the repository being scanned.

## What it scans

- `.claude/settings.json` -- hook configs (auto-approve, stop loops, env persistence)
- `.claude/skills/` -- all SKILL.md files (hidden comments, curl|bash, persistence triggers)
- `.mcp.json` -- MCP server configs (unknown URLs, env var expansion, broad tools)
- `CLAUDE.md` / `.claude/CLAUDE.md` -- instruction injection in project config

## Output

Structured report with findings grouped by severity (CRITICAL, HIGH, MEDIUM, LOW, INFO) and actionable recommendations for each finding.

## When to use

- Before trusting a cloned repository's agent configurations
- After pulling changes that modify `.claude/` or `.mcp.json`
- As part of a security review of any codebase with agent integration
