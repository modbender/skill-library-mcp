---
name: humanizer-enhanced
description: |
  Advanced AI text humanizer for blog content. Detects and removes 34 AI writing
  patterns, adds personality/soul, and handles crypto/Web3 specific tells.
  Use when user says /humanizer, "humanize this", "remove AI patterns",
  "make it sound human", or asks to clean up blog posts, articles, or drafts.
  Features: 28 base patterns from Wikipedia's "Signs of AI writing",
  6 crypto/Web3 specific patterns, severity scoring (HIGH/MEDIUM/LOW),
  stat attribution fixer, soul/personality injection, batch mode.
metadata:
  version: 1.2.0
  author: 0G Labs content team
---

# Humanizer enhanced: remove AI writing patterns

Identify and remove signs of AI-generated text. This enhanced version includes crypto/Web3 patterns and adds personality to make content sound genuinely human-written.

## Quick start

```text
/humanizer                    # Humanize current file or selection
/humanizer path/to/file.md    # Humanize specific file
/humanizer --scan             # Scan only, don't edit (show issues)
/humanizer --batch drafts/    # Process all .md files in directory
```

---

## Process

### Step 1: Scan for patterns

Identify all AI patterns in the text, categorize by severity:

- **HIGH** — Obvious AI tells, must fix (negative parallelism, chatbot artifacts, em dash overuse, vague attributions, copula avoidance)
- **MEDIUM** — Common AI patterns, should fix (rule of three, significance inflation, synonym cycling)
- **LOW** — Minor tells, fix if time permits (title case headings, excessive bold)

### Step 2: Report findings

Show user a summary:

```text
## Humanizer scan results

HIGH (3 issues)
- Line 45: Negative parallelism "isn't X. It's Y"
- Line 89: Em dash overuse (5 instances)
- Line 120: "Research shows" without attribution

MEDIUM (5 issues)
- Line 23: Rule of three pattern
- Line 67: Copula avoidance "serves as"
...

LOW (2 issues)
- Line 12: Title case heading
...

Total: 10 issues found
Estimated humanization: ~15 edits needed
```

### Step 3: Fix (with user approval)

Ask user: "Fix all issues? Or review one by one?"

### Step 4: Add soul

After fixing patterns, review for personality. Sterile writing is still obvious AI. See `references/communication-crypto-soul-patterns.md` for the full soul/personality guide.

### Step 5: Readability check

Check Flesch-Kincaid readability. Target grade 10-12 for developer content, grade 8-10 for general audience. If score is too high (too complex), simplify longest sentences and replace jargon.

### Step 6: Em dash regression scan

After all other fixes, run a final check for em dashes (—) across the text. Humanizer rewrites can reintroduce em dashes. Remove any that were added during the fix process.

---

## Pattern routing table

All 34 patterns are documented with before/after examples in the reference files below.

| Patterns | Severity | Reference file |
|----------|----------|----------------|
| 1. Significance inflation | MEDIUM | `references/content-patterns.md` |
| 2. Promotional language | MEDIUM | `references/content-patterns.md` |
| 3. Superficial -ing analyses | MEDIUM | `references/content-patterns.md` |
| 4. Vague attributions | HIGH | `references/content-patterns.md` |
| 5. Formulaic challenges sections | MEDIUM | `references/content-patterns.md` |
| 6. Generic positive conclusions | MEDIUM | `references/content-patterns.md` |
| 7. AI vocabulary words | MEDIUM | `references/language-style-patterns.md` |
| 8. Copula avoidance | HIGH | `references/language-style-patterns.md` |
| 9. Negative parallelism | HIGH | `references/language-style-patterns.md` |
| 10. Rule of three | MEDIUM | `references/language-style-patterns.md` |
| 11. Synonym cycling | MEDIUM | `references/language-style-patterns.md` |
| 12. False ranges | LOW | `references/language-style-patterns.md` |
| 13. Em dash overuse | HIGH | `references/language-style-patterns.md` |
| 14. Excessive boldface | LOW | `references/language-style-patterns.md` |
| 15. Inline-header lists | MEDIUM | `references/language-style-patterns.md` |
| 16. Title case headings | LOW | `references/language-style-patterns.md` |
| 17. Curly quotes | LOW | `references/language-style-patterns.md` |
| 18. Chatbot artifacts | HIGH | `references/communication-crypto-soul-patterns.md` |
| 19. Knowledge cutoff disclaimers | HIGH | `references/communication-crypto-soul-patterns.md` |
| 20. Sycophantic tone | MEDIUM | `references/communication-crypto-soul-patterns.md` |
| 21. Excessive hedging | MEDIUM | `references/communication-crypto-soul-patterns.md` |
| 22. Filler phrases | MEDIUM | `references/communication-crypto-soul-patterns.md` |
| 23. Crypto hype language | HIGH | `references/communication-crypto-soul-patterns.md` |
| 24. Vague "ecosystem" claims | MEDIUM | `references/communication-crypto-soul-patterns.md` |
| 25. Unsubstantiated stats | HIGH | `references/communication-crypto-soul-patterns.md` |
| 26. "Seamless" and "frictionless" | MEDIUM | `references/communication-crypto-soul-patterns.md` |
| 27. Abstract "empowerment" language | MEDIUM | `references/communication-crypto-soul-patterns.md` |
| 28. Fake decentralization claims | HIGH | `references/communication-crypto-soul-patterns.md` |
| 29. Meta-narration | HIGH | `references/communication-crypto-soul-patterns.md` |
| 30. False audience range | MEDIUM | `references/communication-crypto-soul-patterns.md` |
| 31. Parenthetical definitions | MEDIUM | `references/communication-crypto-soul-patterns.md` |
| 32. Sequential numbering | MEDIUM | `references/communication-crypto-soul-patterns.md` |
| 33. "It's worth noting" filler | MEDIUM | `references/communication-crypto-soul-patterns.md` |
| 34. Identical paragraph structure | HIGH | `references/communication-crypto-soul-patterns.md` |
| Soul and personality guide | — | `references/communication-crypto-soul-patterns.md` |

---

## Severity reference

| Severity | Patterns | Action |
|----------|----------|--------|
| HIGH | Negative parallelism, em dash overuse, chatbot artifacts, vague attributions, copula avoidance, crypto hype, unsubstantiated stats, meta-narration, identical paragraph structure, fake decentralization, knowledge cutoff disclaimers | Must fix |
| MEDIUM | Rule of three, significance inflation, promotional language, -ing analyses, AI vocabulary, sycophantic tone, hedging, filler phrases, ecosystem claims, false audience range, parenthetical definitions, sequential numbering, "it's worth noting" filler, inline-header lists, "seamless"/"frictionless", abstract empowerment | Should fix |
| LOW | Title case, curly quotes, excessive bold, false ranges | Fix if time permits |

---

## Quick reference: find and replace

| Find | Replace |
|------|---------|
| `—` (em dash, multiple) | `, ` or `. ` |
| `serves as` / `stands as` | `is` |
| `isn't X. It's Y` | Rewrite as single statement |
| `crucial` / `vital` / `pivotal` | `important` or `key` or delete |
| `Furthermore,` / `Moreover,` | `Also,` or delete |
| `It is important to note` | Delete |
| `Research shows` | Add specific source |
| `landscape` (abstract) | Be specific |
| `revolutionizing` / `game-changing` | Describe what it actually does |
| `seamless` / `frictionless` | Describe the actual UX |
| `In this article, we'll explore` | Delete |
| `Let's dive in` / `Let's take a look` | Delete |
| `First,... Second,... Third,...` | Vary transitions |
| `It's worth noting` / `Notably,` | Delete |
| `delve` | "look at" / "examine" |
| `Additionally` | Delete |

---

## Batch mode

To humanize multiple files:

```bash
# Scan all markdown files in drafts/
/humanizer --scan drafts/*.md

# Fix all files (with confirmation)
/humanizer --batch drafts/
```

Output format for batch:

```text
## Batch humanization report

drafts/post-1.md
   HIGH 3 | MEDIUM 5 | LOW 2

drafts/post-2.md
   HIGH 1 | MEDIUM 3 | LOW 4

drafts/post-3.md
   Clean! No issues found.

Total: 3 files, 18 issues
```

---

## Sources

Based on:
- [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
- [GitHub: blader/humanizer](https://github.com/blader/humanizer)
- Original research on crypto/Web3 AI patterns

Key insight: "LLMs use statistical algorithms to guess what should come next. The result tends toward the most statistically likely result that applies to the widest variety of cases."

---

*Version 1.2.0 | Created for 0G Labs content team*
