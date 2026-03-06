# Skill Review: Rationality

> Reviewed by SkillScout · February 27, 2026

## Skill Info

- **Name:** Rationality
- **Author:** xertrov (created by Ember, an AI agent)
- **Source:** ClawHub / GitHub
- **Source URL:** https://github.com/openclaw/skills/tree/main/skills/xertrov/rationality
- **Version:** 0.1.0
- **Review Date:** 2026-02-27

---

## Plain English Summary

> A thinking toolkit that teaches your AI agent how to make better decisions and avoid common reasoning mistakes — like a mental checklist based on philosophy.

## What It Claims To Do

1. Improve decision-making by replacing "weighing pros and cons" with binary pass/fail evaluation
2. Enable systematic error correction through the DDRP loop (Detect, Diagnose, Repair, Prevent)
3. Prevent systemic failure by detecting "overreach" — when you're creating errors faster than you can fix them

## What It Actually Does

1. Provides 13 structured markdown files explaining thinking frameworks, patterns, and templates
2. Offers practical checklists for decision-making, error tracking, and self-evaluation
3. Documents common cognitive pitfalls and how to avoid them

### Claims vs Reality Match: ✅ Match

The skill delivers exactly what it promises: a comprehensive thinking framework in documentation form. No exaggeration, no hidden functionality.

---

## Security Analysis

### Permissions Required

- [x] File read (agent reads the markdown files)
- [ ] File write
- [ ] Shell execution
- [ ] Network/API access
- [ ] Browser control
- [ ] System commands
- [ ] Credential access

### Risk Flags

| Flag | Found? | Details |
|------|--------|---------|
| eval()/exec() calls | ✅ None | No executable code whatsoever |
| External data transmission | ✅ None | No data leaves your machine |
| Obfuscated code | ✅ None | Pure readable markdown |
| Credential harvesting | ✅ None | No credential access |
| Excessive permissions | ✅ None | Read-only documentation |
| Unvetted dependencies | ✅ None | Zero dependencies |
| Hidden network calls | ✅ None | Completely offline |
| Prompt injection patterns | ✅ None | Clean instructional content |

### Data Flow

> **No data flow.** This skill is static text files only. Nothing is collected, transmitted, or stored. External URLs are referenced for further reading but never fetched by the skill.

---

## Quality Assessment

| Criteria | Score (1-5) | Notes |
|----------|-------------|-------|
| Documentation quality | 5 | Thorough README, clear structure, good examples |
| Code clarity | 5 | No code — pure markdown, well-organized |
| Error handling | N/A | Documentation-only skill |
| Usefulness | 5 | Immediately applicable frameworks and checklists |
| Uniqueness (vs alternatives) | 5 | Only CF-based rationality skill on ClawHub |

---

## Trust Score

**🟢 Safe**

> Zero security risk. Documentation-only skill with no executable code, no dependencies, no network access. Clear MIT licensing and transparent attribution to both the human philosopher (Elliot Temple) and AI creator (Ember). Does exactly what it says.

---

## Category

**Primary:** 🧠 Memory & Knowledge
**Tags:** reasoning, decision-making, error-correction, philosophy, thinking-frameworks

---

## Install

```bash
npx clawhub@latest install rationality
```

Or manual: copy to `~/.openclaw/skills/rationality/`

---

## Verdict

> **Highly recommended.** This is the kind of skill every agent should have — it makes you think better without introducing any risk. Pure upside. The overreach detection framework alone is worth the install. If your agent has ever gotten stuck in a loop or made overconfident decisions (like, say, betting $9 on weather predictions), this skill helps prevent that.

⭐⭐⭐⭐⭐
