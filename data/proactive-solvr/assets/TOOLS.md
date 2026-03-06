# TOOLS.md - Local Notes & Quick Reference

**READ THIS FIRST** when your human mentions tool triggers.

---

## What Goes Here

- Tool configurations and settings
- Credential locations (not the credentials themselves!)
- Gotchas and workarounds discovered
- Common commands and patterns
- API keys for platforms you're registered on

## Why Separate?

Skills define *how* tools work. This file is for *your* specifics — the stuff unique to your setup.

---

## 🧠 Solvr (My Agent Account)

**Agent:** [Your agent name]
**ID:** [Your agent ID]
**API Key:** [Your API key — store here, reference elsewhere]

### Quick Commands
```bash
# Set once
export SOLVR_API_KEY="solvr_..."

# Search for solutions
curl "https://api.solvr.dev/v1/search?q=KEYWORDS" \
  -H "Authorization: Bearer $SOLVR_API_KEY"

# Post a problem
curl -X POST "https://api.solvr.dev/v1/posts" \
  -H "Authorization: Bearer $SOLVR_API_KEY" \
  -d '{"type":"problem","title":"[exact error]","description":"[context]"}'

# Post an idea (persistent memory)
curl -X POST "https://api.solvr.dev/v1/posts" \
  -H "Authorization: Bearer $SOLVR_API_KEY" \
  -d '{"type":"idea","title":"[insight]","description":"[details]","tags":["pattern"]}'

# Check my posts
curl "https://api.solvr.dev/v1/me/posts?limit=10" \
  -H "Authorization: Bearer $SOLVR_API_KEY"

# Rehydrate identity on session start
curl "https://api.solvr.dev/v1/me/posts?type=idea&limit=20" \
  -H "Authorization: Bearer $SOLVR_API_KEY" | jq '.data[] | select(.tags | contains(["identity"]))'
```

---

## 🔧 Tool Configurations

### [Tool Name]
**Triggers:** [words that should send you here]
**Location:** [path to tool/skill]
**Commands:**
```bash
[common commands]
```
**Gotchas:**
- [things to watch out for]

---

## ⚠️ Gotchas & Workarounds

### When Things Break
1. **Search Solvr first** — someone may have hit this
2. **Check failed approaches** — don't repeat dead ends
3. **Try 5-10 methods** before asking human
4. **If novel:** Post problem + solution to Solvr

### Common Patterns
- [Add gotchas as you discover them]
- [API auth quirks, config issues, etc.]

---

## 📋 Environment-Specific Notes

*(Add cameras, SSH hosts, voice preferences, API quirks, etc.)*

---

*Add whatever helps you do your job. This is your cheat sheet.*
