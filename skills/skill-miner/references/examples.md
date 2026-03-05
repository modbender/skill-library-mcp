# skill-miner Examples

Real-world examples of the search → inspire → build workflow.

---

## Example 1: Found Suspicious Shell Skill

**Step 1: Search**
```bash
clawhub search shell
# Found: shell-commands v1.0.0
```

**Step 2: Inspect**
```bash
clawhub inspect shell-commands
# Summary: Execute shell commands remotely
# Owner: unknown-user
# Warning: Suspicious patterns detected
```

**Step 3: Analyze**
```
Problem: Execute shell commands on remote systems
Approach: Direct bash execution
Risk: Uses eval - dangerous!
Tools: ssh, bash
```

**Step 4: Build Clean**
```bash
# Create: safe-shell-runner
# - Predefined command whitelist
# - No eval
# - Input sanitization
# - Full logging
```

---

## Example 2: Wanted Crypto Trading Bot

**Step 1: Search**
```bash
clawhub search crypto trading
# Found: binance-pro, hyperliquid-trading
```

**Step 2: Inspect**
```bash
clawhub inspect hyperliquid-trading
# Summary: Automated trading
# Risk: Real money - HIGH RISK
```

**Step 3: Analyze**
```
Problem: Automated trading
Approach: Exchange API integration
Risk: Financial loss possible
```

**Step 4: Build Safe Alternative**
```bash
# Create: crypto-price-monitor
# - Read-only price fetching
# - Alert on thresholds
# - No trading
# - Completely safe
```

---

## Example 3: Gap Found - Log Analyzer

**Step 1: Search**
```bash
clawhub search log analyzer
# Results: Very few, outdated
```

**Step 2: Research**
```
Problem: Need to parse and analyze logs
Existing: Basic grep/sed skills
Gap: AI-powered log analysis
```

**Step 3: Build**
```bash
# Create: log-ai-analyzer
# Features:
# - Parse nginx, apache, syslog, app logs
# - Detect patterns
# - Alert on errors
# - Summary generation
```

---

## Example 4: Modern Network Tools

**Step 1: Search**
```bash
clawhub search network
# Found: network v1.0.0 (old, basic)
```

**Step 2: Inspect**
```bash
clawhub inspect network
# Summary: Basic network commands
# Updated: 2024 - outdated
```

**Step 3: Build Modern Version**
```bash
# Create: net-tools-modern
# Features:
# - Port scanning
# - SSL certificate checking
# - DNS lookup
# - Bandwidth monitoring
# - API-based lookups
```

---

## Example 5: API Testing Tool

**Step 1: Search**
```bash
clawhub search "api test"
# Found: few basic skills
```

**Step 2: Analyze**
```
Gap: No comprehensive API testing
Need: HTTP methods, auth, assertions
```

**Step 3: Build**
```bash
# Create: api-tester
# Features:
# - GET, POST, PUT, DELETE
# - Headers, body, auth
# - Response validation
# - JSON assertion
# - Chain requests
```

---

## Example 6: Task Scheduler

**Step 1: Search**
```bash
clawhub search scheduler cron
# Found: auto-updater (specific use)
# Gap: General task scheduling
```

**Step 2: Build**
```bash
# Create: task-scheduler
# Features:
# - Schedule commands
# - Recurring tasks
# - Conditional execution
# - Notification on completion
# - Log output
```

---

## Search Strategies

### Finding Gaps
```bash
# Search broadly
clawhub explore --sort newest

# Search specific categories
clawhub search "code"
clawhub search "data"
clawhub search "automation"

# Check downloads vs quality
clawhub explore --sort downloads
```

### Finding Inspiration
```bash
# Trending
clawhub explore --sort trending

# By use case
clawhub search "backup"
clawhub search "monitoring"
clawhub search "automation"

# By tool
clawhub search "github"
clawhub search "slack"
```

---

## Decision Matrix

| Situation | Action |
|-----------|--------|
| Good skill exists | Use it |
| Suspicious but good idea | Build clean version |
| Gap found | Build from scratch |
| Outdated skill | Improve it |
| Risky skill | Build safe alternative |

---

## Build Template

When building from inspiration:

```markdown
# My New Skill

## Based On
- ClawHub skill: [name]
- What I learned: [insight]

## My Approach
[How you're solving it differently]

## Security
[Your security measures]

## Features
- Feature 1
- Feature 2

## Usage
[Examples]
```
