# Language and style patterns (7-17)

## 7. AI vocabulary words — MEDIUM

**High-frequency AI words:** Additionally, crucial, delve, emphasizing, enhance, fostering, garner, highlight (verb), interplay, intricate, landscape (abstract), pivotal, showcase, tapestry (abstract), testament, underscore, valuable, vibrant

**Before:**
> Additionally, the intricate interplay between validators showcases the protocol's pivotal role in the evolving DeFi landscape.

**After:**
> Validators coordinate through a gossip protocol. This adds latency but prevents single points of failure.

---

## 8. Copula avoidance — HIGH

**Pattern:** "serves as", "stands as", "functions as", "acts as" instead of simple "is"

**Before:**
> The token serves as a governance mechanism and functions as a fee payment method.

**After:**
> The token is used for governance and fee payments.

---

## 9. Negative parallelism — HIGH (always fix)

**Pattern:** "It's not X, it's Y", "Not just X, but Y", "isn't about X. It's about Y"

**Before:**
> The shift to decentralized AI isn't philosophy. It's economics. It's not just about cost. It's about access.

**After:**
> Decentralized AI costs less and removes single points of failure. That's the pitch, anyway.

---

## 10. Rule of three — MEDIUM

**Pattern:** Forcing ideas into groups of three

**Before:**
> The platform provides security, scalability, and decentralization. Users get speed, reliability, and transparency.

**After:**
> The platform prioritizes security over raw speed. Most users don't notice the extra 200ms latency.

---

## 11. Synonym cycling — MEDIUM

**Pattern:** Using different words for the same thing to avoid repetition

**Before:**
> The protocol handles transactions. The system processes transfers. The platform manages exchanges.

**After:**
> The protocol handles transactions, processing about 10,000 per second at peak.

---

## 12. False ranges — LOW

**Pattern:** "from X to Y" where X and Y aren't on a meaningful scale

**Before:**
> From individual developers to enterprise teams, from startups to Fortune 500 companies...

**After:**
> Both solo developers and large teams use it, though the enterprise features cost extra.

---

## 13. Em dash overuse — HIGH

**Problem:** AI uses em dashes (—) 2-5x more than humans

**Before:**
> The solution—while not perfect—offers several advantages—including cost reduction—that make it worth considering.

**After:**
> The solution offers several advantages, including cost reduction. It's not perfect, but it works.

**Rule:** Default: ZERO em dashes in published content. Use commas, periods, colons, or parentheses instead.

**Common em dash locations to check (v1.2):**

| Location | Wrong | Right |
|----------|-------|-------|
| Quote attribution | `"Quote." — **Name**` | `"Quote." **Name**` or `"Quote." - Name` |
| List item separator | `Feature — Description` | `Feature: Description` |
| Inline break (body) | `text — more text` | `text. More text` or `text, more text` |
| Inline break (FAQ) | `data — fully owned` | `data, fully owned` |

**Pre-publish scan:**
```bash
grep -n "—" file.md
```

If this returns ANY results, fix them before publishing.

---

## 14. Excessive boldface — LOW

**Before:**
> The platform offers **security**, **scalability**, and **decentralization** through its **innovative architecture**.

**After:**
> The platform offers security, scalability, and decentralization through its modular architecture.

**Rule:** Bold only for stats or truly critical points. Max 2-3 bold phrases per section.

---

## 15. Inline-header lists — MEDIUM

**Before:**
> - **Security:** End-to-end encryption protects all data.
> - **Speed:** Transactions confirm in under 2 seconds.
> - **Cost:** Fees average $0.001 per transaction.

**After:**
> Transactions confirm in under 2 seconds and cost about $0.001. All data is encrypted end-to-end.

---

## 16. Title case headings — LOW

**Before:**
> ## How Decentralized Infrastructure Addresses These Challenges

**After:**
> ## How decentralized infrastructure addresses these challenges

---

## 17. Curly quotes — LOW

**Before:** "smart quotes"
**After:** "straight quotes"

---

## Quote attribution format

When attributing quotes in content, do NOT use em dashes before the name.

**Wrong:**
> "The protocol changes everything." — **John Smith, CEO**

**Right:**
> "The protocol changes everything."
>
> **John Smith, CEO, Project Name**

The em dash attribution style is an AI writing tell. Human editors typically use line breaks or simpler formatting.

---

## AI vocabulary banned list

Never use these words in published content:

> additionally, crucial, delve, emphasizing, enhance, fostering, garner, groundbreaking, highlight (as verb), interplay, intricate, landscape (abstract), pivotal, revolutionizing, seamless, showcase, tapestry, testament, underscore, unprecedented, valuable, vibrant, game-changing, frictionless, empowers, nestled, notably, furthermore, moreover
