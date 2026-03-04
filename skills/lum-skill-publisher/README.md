# ClawHub Skill Publisher

> Research, structure, and publish skills to ClawHub — informed by what's actually working in the marketplace.

This skill turns a rough skill idea into a polished, publish-ready ClawHub listing. It analyzes top-performing skills in your category, generates a gap report against your draft, patches your files to match marketplace standards, and walks you through `clawhub publish`.

---

## What It Does

1. **Research** — installs and analyzes top listings in your category
2. **Gap report** — scores your draft against marketplace best practices
3. **Patch** — applies findings to README and SKILL.md
4. **Publish** — runs `clawhub publish` with the right flags

---

## When to Use

- Writing a new skill and want to know what ClawHub buyers respond to
- Have a draft and want an objective quality check before publishing
- Updating an existing skill and want to know what's changed in the market

---

## Key Finding: What Makes a Top Listing

| Factor | Best Practice |
|--------|--------------|
| Description | ≤160 chars, value-first ("reduces X by Y%"), not feature-first |
| First line of SKILL.md | States the use case immediately — no preamble |
| Structure | Tables > prose for comparisons and decision rules |
| "When to use" | Explicit do/don't list — top skills all have this |
| Safety section | "Never does X" builds trust — include even if short |
| Examples | Concrete ✅/❌ pairs in a separate examples file |
| Word count | 400–700 words for SKILL.md; README can run longer |
| Version history | Shows maintenance; place at the bottom |

---

## Workflow

```
1. clawhub search <category>
2. Install top 3-5 results → /tmp/ch-research/
3. Read SKILL.md + README for each
4. Score your draft against the gap table
5. Patch description, sections, word count
6. clawhub whoami (confirm auth)
7. clawhub publish ./skills/<slug> --slug <slug> --name "..." --version X.Y.Z
```

---

## Installation

```bash
clawhub install clawhub-skill-publisher
```

---

## Version

**1.0.0** — Initial release. Framework built from live analysis of ClawHub top listings (Feb 2026).

---

*Built for [OpenClaw](https://openclaw.ai) · Listed on [ClawHub](https://clawhub.ai)*
