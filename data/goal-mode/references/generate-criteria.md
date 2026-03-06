# Operation: generate_criteria

## Input

```json
{
  "operation": "generate_criteria",
  "input": {
    "goal_text": "string — the user's goal in their own words",
    "constraints": ["array of constraint strings"]
  }
}
```

## Behavior

Analyze the goal to determine its category and generate **6-10** checklist criteria. Each criterion is a **specific noun phrase** describing a narrow topic or dimension to evaluate — NOT a question, NOT a sentence, NOT a "Does this page..." filter.

### The Specificity Rule (most important)

Criteria must be **narrow enough that a single overview page cannot satisfy more than 2-3 of them**. This is the single most important quality metric.

Before finalizing, mentally test: "Could one broad overview page on this topic score ≥ 0.7 on more than 3 of these criteria?" If yes, your criteria are too broad — decompose them.

**Decomposition strategy for broad goals:**
- Split by **sub-topic** (not just facet): e.g., "best headphones" → specific use cases, driver types, or price tiers narrow enough that a "top 10 headphones" listicle only skims them
- Split by **depth requirement**: prefer criteria that require specialized sources (detailed reviews, comparison tests, expert guides) rather than generic overviews
- Split by **actionability**: at least 2 criteria should require information that helps the user **do something** (make a decision, take an action, compare options)

### Rules for criteria

- Each criterion is a specific noun phrase (3-8 words)
- Narrow enough to require a **dedicated page or section** to satisfy — not just a passing mention in an overview
- Describes WHAT to evaluate, not HOW to evaluate it
- Specific to the goal (not generic)
- Measurable or verifiable from web pages
- Ordered by importance
- **Every constraint MUST produce at least one criterion.** If the user says "budget under $1000", there must be a criterion about pricing within that budget. If the user says "vegetarian options only", there must be a criterion targeting vegetarian-specific information. Do not silently ignore constraints.
- At least 2 criteria should target information requiring **specialized sources** (not found in a general overview)

### CORRECT format examples (diverse goal types)

- Goal "buy a laptop under $1000":
  `["CPU and GPU benchmark comparisons under $1000", "Battery life test results (hours)", "Build quality: hinge durability and chassis material", "Display color accuracy and brightness (nits)", "SSD speed and upgrade options", "Thermal throttling under sustained load", "Warranty terms and repair track record"]`
- Goal "find best noise-cancelling headphones":
  `["ANC effectiveness in dB reduction tests", "Sound signature: bass vs neutral profile", "Comfort for 4+ hour wear sessions", "Multipoint Bluetooth pairing support", "Battery life and fast-charge specs", "Microphone quality for calls", "Durability and hinge/folding mechanism"]`
- Goal "plan a trip to Japan in April":
  `["Cherry blossom forecast and peak viewing spots", "JR Pass vs IC card cost comparison", "Ryokan vs hotel pricing in Kyoto", "Visa-free entry requirements and duration", "Tokyo to Kyoto transit options and times", "Daily food budget breakdown", "Must-book-ahead attractions and reservation tips", "Pocket Wi-Fi vs eSIM providers and pricing"]`
- Goal "switch to data science career":
  `["Python vs R for entry-level roles", "Portfolio projects that hiring managers value", "Bootcamp vs self-study completion rates", "Entry-level salary by city and industry", "SQL and cloud skills gap analysis", "Interview process at FAANG vs startups", "Transition timeline from non-technical background"]`
- Goal "improve home espresso setup":
  `["Grinder burr types: flat vs conical performance", "Pressure profiling on sub-$500 machines", "Water mineral content and filtration", "Milk steaming wand power and technique", "Single-dose workflow and retention", "Puck prep: WDT and tamping consistency"]`

### WRONG — never generate criteria like these

- "Does this page discuss coffee varieties?" (question format)
- "The page should contain information about..." (sentence format)
- "Check if the page mentions..." (instruction format)
- "Comprehensive overview of the entire topic" (too vague, too long)
- "Performance benchmarks" (too vague — benchmarks for what? under what conditions?)
- "Price and value" (too broad — every product page touches this)
- "Build quality" (too broad — need to specify what aspect: materials, durability tests, etc.)
- "History and background" (too broad — any overview page covers this trivially)

## Output JSON shape

`criteria` must be a flat JSON array of plain strings. No nested objects, no keywords/categories/subcriteria.

```json
{
  "criteria": ["Specific noun phrase 1", "Specific noun phrase 2", "..."]
}
```

## Persist

Always write ALL four files:

1. `write` to `/home/ubuntu/.openclaw/workspace/goal-mode/active-goal.json` — the active-goal pointer JSON (goal_slug, goal_text, constraints, status: "active", started_at, updated_at)
2. `write` to `/home/ubuntu/.openclaw/workspace/goal-mode/{goal_slug}/session.json` — full session object with all arrays seeded empty:
   ```json
   { "schema_version": 2, "goal_slug": "...", "goal_text": "...", "constraints": [...], "status": "active", "started_at": "...", "updated_at": "...", "criteria": [{ "text": "...", "covered": false, "best_relevance": 0.0, "sources": 0 }], "pages": [], "findings": [], "candidates": [] }
   ```
3. `write` to `/home/ubuntu/.openclaw/workspace/goal-mode/{goal_slug}/criteria.json` — see criteria.json schema in references/schemas.md
4. `write` to `/home/ubuntu/.openclaw/workspace/memory/goal-mode/active-session.md` — see active-session.md format in references/schemas.md
