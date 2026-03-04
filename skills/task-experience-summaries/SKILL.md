---
name: task-experience-summaries
description: Experience summaries for OpenClaw tasks, including common installation problems, troubleshooting steps, and best practices for packages, configurations, and tools. Use when experiencing installation issues, facing unknown error messages, or needing guidance on package names and configuration methods. Also use when documenting new experiences for future reference.
---

# Task Experience Summaries

## Overview

This skill provides curated experience summaries from real OpenClaw tasks, including:

- Installation/packaging problems and solutions
- Common error messages and root causes
- Package search and discovery methods
- Configuration patterns and environment setups
- Tool-specific troubleshooting steps
- Best practices for documenting new experiences

Each entry includes: Problem → Solutions → Key Lessons → Prevention Steps.

## Common Installation Packages

### ClawHub CLI

**Purpose:** Search, install, update, and publish OpenClaw skills from clawhub.com.

**Installation:**
```bash
npm install -g clawhub
```

**Usage:**
```bash
# Search for skills
clawhub search "keyword"

# Install a skill
clawhub install "skill-name"

# List installed skills
clawhub list

# Publish a new skill (when ready)
clawhub publish "skill-directory"
```

**Authentication:**
- Token: `clh_<token>`
- Username: `@<username>`
- Available at: https://clawhub.ai

### Tavily Search

**Purpose:** AI-optimized web search via Tavily API.

**Configuration:**
```bash
# Set environment variable
set TAVILY_API_KEY=your-api-key-here
```

**Usage:**
- Search query: `web_search` tool
- API key location: `<skill-dir>/README_CONFIG.md`
- Quality: High relevance for AI agents

---

## Troubleshooting Categories

### 1. Package Installation Issues

#### Problem: npm 404 Not Found

**Scenario:** Install command fails with "404 Not Found"

**Solutions:**
1. Check package name spelling
2. Search ClawHub: `clawhub search "keyword"`
3. Try npm search: `npm search "keyword"`
4. Verify the package exists in npm registry

**Typical Fixes:**
- Wrong package name (e.g., `tavily-search` → correct: `tavily-mcp`)
- Package removed or renamed
- Typo in command

**Key Lesson:** Always verify package existence before installation. Use search tools.

#### Problem: Windows Permission EEXIST Error

**Scenario:** Installation fails with "EEXIST: file already exists"

**Solution:**
```bash
npm i -g clawhub --force
```

**Root Cause:** Old version files remain, blocking installation

**Prevention:** Use `--force` for global installations on Windows if issues occur

#### Problem: Unknown Package Name

**Scenario Package not found in npm registry**

**Solutions:**
1. Use ClawHub search: `clawhub search "keyword"`
2. Try broader search terms
3. Check if the skill is hosted on ClawHub (OpenClaw's official registry)

**Example:**
```
Initial attempt: npm install "find-skills" → 404
Solution: clawhub search "find-skills" → Found "find-skills v0.1.0"
Result: clawhub install "find-skills" → Success
```

**Key Lesson:** ClawHub is the first place to check for OpenClaw skills

### 2. Configuration Issues

#### Environment Variables

**Standard Pattern:**
```bash
# SET in current session
set ENV_VAR=value

# For persistent settings, add to shell config
# (e.g., .bashrc, .zshrc, PowerShell profile)
```

**Common Variables:**
- `TAVILY_API_KEY` - For web search tools
- `OPENAI_API_KEY` - If needed for OpenAI-based skills
- Custom credentials for specific tools

**Verification:**
```bash
echo $TAVILY_API_KEY  # Unix-like
echo %TAVILY_API_KEY% # PowerShell/CMD
```

### 3. Tool-Specific Issues

#### OpenClaw Browser Extension

**Symptom:** "tab not found" errors after browser operations

**Solutions:**
1. Restart OpenClaw Gateway (OpenClaw.app → Restart)
2. Keep Chrome extension badge ON (not OFF)
3. Do not close browser tab between operations
4. Reseat connection: Open Extension → Attach Tab → Badge ON

**Best Practice:**
- Browser tool is for one-time operations or screenshots
- Not suitable for long-lived automated sessions
- Direct browser interaction is more reliable for persistent needs

#### Browser Profile Issues

**Symptom:** Multiple profiles causing conflicts

**Solutions:**
- Use `--profile=chrome` for managed Chrome browser
- Use `--profile=openclaw` for isolated browser
- Test with clean profile if issues persist

**Status Check:**
```bash
openclaw gateway status
```

---

## Problem-Solving Workflow

### Step 1: Identify the Category

Determine if the issue belongs to:
- Installation problems
- Configuration issues
- Tool-specific malfunctions
- Package discovery
- Platform-specific behavior (Windows/Linux/macOS)

### Step 2: Search the Summary

Use the tables and categorized entries above:
- Match symptoms to category
- Review associated solutions
- Try recommended fixes

### Step 3: Test Solutions

Apply suggested fixes in order:
1. Most common/simplest solution first
2. Platform-specific fixes second
3. Advanced configurations third

### Step 4: Document New Experiences

**When to Document:**
- Successfully resolved an unknown problem
- Discovered a pattern or workaround
- Learned a configuration trick
- Found that a documented solution works differently

**How to Document:**
1. Record the problem clearly
2. Note the solution steps
3. Include platform-specific details
4. Add prevention/prevention steps
5. Update relevant section in this SKILL.md

**Template for New Entry:**
```markdown
### Problem: [Clear description]

**Scenario:** [Context where problem occurs]

**Solution:** [Step-by-step resolution]

**Root Cause:** [Why this happens]

**Prevention:** [How to avoid]

**Platform Notes:** [If platform-specific]
```

### Step 5: Iterate and Refine

Review after using the skill:
- Are entries clear and actionable?
- Are symptoms and solutions well-matched?
- Is formatting consistent?
- Any missing common issues?

---

## Quick Reference Table

| Issue Type | Symptoms | Primary Tool | Key Command |
|-----------|----------|--------------|-------------|
| Package not found | 404, npm errors | npm, ClawHub | `clawhub search "keyword"` |
| Permission errors | EEXIST, access denied | npm install | `--force` flag |
| Configuration missing | Tool fails | Environment variables | `set VAR=value` |
| Browser connection | Tab not found | Browser tools | Restart Gateway + Badge ON |
| Unknown package | Cannot install | clawhub list | `clawhub install "name"` |

---

## Best Practices

1. **Search Before Guessing:** Always use search tools first
2. **Document Solutions:** Write down everything you learn
3. **Categorize Issues:** Group by type for easy lookup
4. **Platform Notes:** Track Windows/macOS/Linux differences
5. **Prevention Over Cure:** Add prevention steps to avoid recurrence
6. **Keep It Practical:** Focus on actionable steps, not theory

---

## Example Use Cases

### Example 1: Installing a New Skill

```bash
# User asks: "I need a weather skill for checking forecasts"

# Step 1: Search
clawhub search "weather"

# Step 2: Identify candidate
Found: "weather v1.0" - Get current weather and forecasts (no API key required)

# Step 3: Install
clawhub install "weather"

# Step 4: Configure (if needed)
# Check README_CONFIG.md for required environment variables

# Step 5: Use
# Use web_search tool with query: "weather today"
```

### Example 2: Troubleshooting Browser Issues

```bash
# Symptom: Browser tool reports "tab not found"

# Step 1: Restart Gateway (first fix)
OpenClaw.app → Restart

# Step 2: Check extension
✓ Badge indicator should be ON
✓ Running state
✓ CDP Ready (Chrome DevTools Protocol)

# Step 3: Reattach if needed
Click OpenClaw extension icon → Attach tab → Badge ON

# Step 4: Verify
Try browser open → snapshot
```

### Example 3: Finding Unknown Package

```bash
# Symptom: "I need an RSS feed parser" - package unknown

# Step 1: ClawHub search
clawhub search "rss"

# Step 2: Identify
Found: "rss-parser skill v0.5.0" with description "Parse RSS feeds"

# Step 3: Install
clawhub install "rss-parser"

# Result: Success
```

---

## Notes

- All entries are based on actual resolved issues
- Platform-specific behaviors are noted when applicable
- Configuration details refer to current workspace setup
- For newer issues, always consult official documentation before relying on summaries