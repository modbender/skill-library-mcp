# Curiosity Engine — Examples

## Example 1: Open-ended Research (Full OODA-C)

**User:** "Why is mass timber construction gaining popularity?"

**OBSERVE:** User asks about a trend in construction. I know basics about CLT/glulam but not recent drivers.

**ORIENT:** Initial hypothesis: environmental concerns + cost reduction. Confidence: 5/10.

**DOUBT:**
- Protocol A (Self-Ask):
  1. "What changed recently to make it more viable than before?"
  2. "Are there regulatory changes driving this?"
  3. "How does it compare to steel/concrete on total lifecycle cost?"
  → Question 2 has highest info gain — regulations directly enable or block adoption.

- Protocol B (Devil's Advocate):
  - Assumption: "It's gaining popularity everywhere" → What if it's only in specific regions?
  - Assumption: "Environmental concern is a driver" → What if insurance/fire codes still block it?

- Protocol C (Gap Map):
  - ✅ KNOWN: CLT exists, is renewable, sequesters carbon
  - ⚠️ ASSUMED: It's cheaper than alternatives
  - ❌ UNKNOWN: Recent building code changes, insurance stance, actual market data

**ACT:**
- web_search("mass timber building code changes 2025 2026")
- web_search("mass timber vs steel construction cost comparison")
→ Found: IBC 2021 expanded mass timber to 18 stories. Several states adopted.
→ Found: Cost parity reached in mid-rise buildings in 2024.
→ Surprise! Insurance is actually becoming MORE favorable due to fire test data.

**CURIOSE:**
- Confidence updated: 5/10 → 8/10
- Surprise: Insurance favorability was unexpected
- Open thread: "How do CLT fire test results compare to steel?"

**Response includes** the enriched answer + confidence + open thread.

---

## Example 2: Encountering Surprising Information (Surprise Detector)

**User:** "Summarize this paper about ant colony optimization."

While reading the paper, the agent encounters: "ACO outperformed gradient descent on non-convex protein folding subproblems."

**Surprise Detector triggers:** 🔍
- This connects two seemingly unrelated domains (swarm intelligence + protein folding)
- One extra step: web_search("ant colony optimization protein folding benchmark")
- Result enriches the summary with unexpected cross-domain application

---

## Example 3: Quick Question (Skip)

**User:** "What time is it in Tokyo?"

No curiosity activation. Direct answer. This is a deterministic lookup.

---

## Example 4: Medium Complexity (Light Activation — Protocol C only)

**User:** "How much RAM does my server have?"

**Protocol C:**
- ✅ KNOWN: Can run `free -h`
- ⚠️ ASSUMED: User means physical RAM, not swap
- ❌ UNKNOWN: Nothing significant

→ Light activation produces a quick but precise answer, clarifying physical vs swap.

---

## Example 5: User-Triggered Deep Exploration

**User:** "Dig deeper into why SQLite uses a B-tree and not an LSM tree."

Full OODA-C activates because user said "dig deeper":

**DOUBT Protocol A generates:**
1. "What workload patterns favor B-tree over LSM?"
2. "Has SQLite ever considered switching?"
3. "Are there SQLite forks that use LSM?"

→ Question 3 is most surprising — leads to discovering SQLite's experimental LSM extension (lsm1).

**Result:** A much richer answer than "B-trees are good for reads."
