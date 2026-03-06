---
name: skill-creator
description: "Create or update AgentSkills based on lessons from building workspace-analyzer. Use when designing, structuring, packaging skills, testing, and publishing. Includes our learned best practices, dos/don'ts, and publishing workflow."
version: "1.0.0"
metadata:
  {"openclaw":{"emoji":"🛠️","requires":{"bins":["python3"]}, "tags":["skill", "creation", "development", "pipeline"]}}
---

# Skill Creator (Enhanced)

> "From idea to published skill - our learnings captured."

This skill guides you through creating skills based on our experience building workspace-analyzer.

---

## Our Skill Creation Pipeline

**How it works:**
1. Use skill-creator → Get guidance on building a skill
2. Build the skill → workspace-analyzer is an example result
3. Learn lessons → From building that specific skill
4. Improve skill-creator → With those learnings
5. Future skills are even better!

### Example: workspace-analyzer

This skill was built using the guidance in skill-creator. The lessons learned from building it have been incorporated back into this skill-creator to make it better.

---

### Phase 1: Define Problem & Success Criteria

**Before writing code, answer:**

| Question | Why It Matters |
|----------|---------------|
| What problem does it solve? | Clear purpose |
| Who is it for? | Agent or human? |
| What makes it dynamic? | How does it adapt? |
| What should it NEVER do? | Security/safety boundaries |

**Success Criteria Template:**
```
1. [Dynamic] Works for any OpenClaw workspace
2. [Safe] No sensitive info exposed
3. [Documented] Clear purpose and usage
4. [Agent-focused] Outputs JSON, agent decides
```

---

### Phase 2: Build Skill Structure

```
skill-name/
├── SKILL.md              ← Documentation (required)
├── scripts/
│   └── main.py          ← Main logic
├── references/          ← Detailed docs (optional)
│   └── guide.md
└── tests/               ← Test cases (optional)
    └── test_main.py
```

---

### Phase 3: Implement Core Logic

**Our Approach (from workspace-analyzer):**

1. **File Discovery** - Walk directory, collect files
2. **Pattern Detection** - Find core files dynamically
3. **Content Analysis** - Line counts, sections, links
4. **Issue Detection** - Bloat, orphans, duplicates
5. **Recommendation Generation** - Actionable JSON output

**Key Lesson:** Script analyzes → Agent decides → Agent acts

---

### Phase 4: Testing Protocol

**Test 1: Accuracy**
```bash
python3 skills/workspace-analyzer/scripts/analyzer.py --output test.json
# Verify counts manually
ls *.md | wc -l
wc -l OPERATING.md
```

**Test 2: False Positives**
- Run on real workspace
- Check: Are broken links real?
- Check: Are duplicates problematic?
- Check: Is bloat legitimate?

**Test 3: Actionability**
- Can agent act on recommendations?
- Is output clear enough?
- Does agent need more context?

---

### Phase 5: Document

**Required Sections:**
1. **Overview** - What it does
2. **Usage** - How to run
3. **Output** - JSON format explained
4. **Features** - What it detects
5. **Integration** - How to use with heartbeat
6. **Security** - What it does NOT do
7. **Skill Graph** - Related skills

---

## Dos and Don'ts

### ✅ DO

| Do | Why |
|----|-----|
| Start with success criteria | Keeps you focused |
| Make it dynamic | Works for any workspace |
| Test on real data | Catches issues early |
| Document as you go | Future you thanks you |
| Keep SKILL.md under 500 lines | Context efficiency |
| Use progressive disclosure | Load details as needed |
| Add skill graph links | Helps discovery |

### ❌ DON'T

| Don't | Why |
|-------|-----|
| Hardcode paths | Breaks on other workspaces |
| Expose secrets/API keys | Security risk |
| Auto-fix without review | Can break things |
| Skip testing | Bugs happen |
| Write monolithic code | Hard to maintain |
| Skip false positive checks | Agent loses trust |

---

## What Works (from experience)

### 1. Category-Specific Thresholds
Different file types need different thresholds:
```python
THRESHOLDS = {
    "kai_core": {"bloat_warning": 400, "bloat_critical": 600},
    "skills": {"bloat_warning": 600, "bloat_critical": 1000},
    "memory": {"bloat_warning": 500, "bloat_critical": 800}
}
```

### 2. Dynamic Pattern Detection
Find files by location, not hardcoded names:
```python
# Instead of: if filename == "SOUL.md"
# Use: if "/" not in filename and filename.endswith(".md")
```

### 3. False Positive Handling
Document what may look like issues but aren't:
- Links to skills like [[blogwatcher]] - valid!
- Large reference docs - legitimate
- Agent template files - expected

### 4. Actionable Output
Each recommendation should have:
```json
{
  "action": "REVIEW_BLOAT",
  "file": "OPERATING.md",
  "reason": "503 lines - consider splitting",
  "severity": "WARN",
  "category": "kai_core"
}
```

---

## Publishing Guide

### Checklist Before Publish

- [ ] SKILL.md complete with all sections
- [ ] Script runs without errors
- [ ] Tests pass on real workspace
- [ ] False positives documented
- [ ] No secrets in output
- [ ] Related skills in skill graph
- [ ] README.md cleaned up (if any)
- [ ] Version in frontmatter

### Publishing Steps

```bash
# 1. Verify skill structure
ls -la skills/[skill-name]/

# 2. Test the script
python3 skills/[skill-name]/scripts/main.py

# 3. Check for sensitive data
grep -r "sk-\|ghp_\|eyJ" skills/[skill-name]/

# 4. Publish (if using ClawHub)
npx clawhub publish skills/[skill-name]/
```

---

## Common Pitfalls

### 1. Hardcoded Workspace Path
**Bad:** `root = "/home/zendenho/.openclaw/workspace"`
**Good:** `root = os.path.expanduser("~/.openclaw/workspace")`

### 2. Missing Error Handling
**Bad:** `with open(file) as f: return f.read()`
**Good:** 
```python
try:
    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()
except Exception as e:
    return {"error": str(e)}
```

### 3. No False Positive Handling
**Bad:** Flag all large files as bloat
**Good:** Category-specific thresholds + documentation

### 4. Monolithic Output
**Bad:** One big JSON blob
**Good:** Structured sections + summary + recommendations

---

## Integration with Heartbeat

Add skill execution to maintenance:

```markdown
## X. Run Analysis Skills

### Workspace Analyzer
python3 skills/workspace-analyzer/scripts/analyzer.py --output /tmp/analysis.json
# Review recommendations

### [Your New Skill]
python3 skills/[your-skill]/scripts/main.py --output /tmp/your-analysis.json
# Review recommendations
```

---

## Related Skills

- [[workspace-analyzer]] - The skill we built (reference implementation)
- [[qmd]] - For memory organization
- [[mcporter]] - For MCP server integration

---

## References

For detailed guidance, see:
- `skills/workspace-analyzer/SKILL_CREATION_GUIDE.md` - How we built workspace-analyzer using this guide
- Official OpenClaw skill-creator in npm modules

---

## Example Output

The workspace-analyzer skill was built using this guide. It's an example of what skill-creator helps you create!

---

## Changelog

### v1.1 (2026-02-21)
- Added our learnings from building workspace-analyzer
- Added dos/don'ts from experience
- Added publishing checklist
- Added common pitfalls section

### v1.0 (2026-02-21)
- Initial based on official skill-creator

---

*Enhanced: 2026-02-21*
