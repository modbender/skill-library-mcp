# Operation: evaluate_page

## Input

```json
{
  "operation": "evaluate_page",
  "input": {
    "goal_text": "string",
    "goal_slug": "string",
    "constraints": ["array"],
    "criteria": ["array of checklist criterion strings to check coverage against"],
    "page": {
      "url": "string",
      "title": "string",
      "extracted_text": "string — readable content from the page"
    }
  }
}
```

## Behavior

Using ONLY the data in the input.

**Large page handling:** If `extracted_text` is very long (>10,000 characters), focus your analysis on the most relevant sections rather than trying to extract every detail. Prioritize findings that directly address uncovered criteria. Cap findings at **10 per page** and keep each under 240 characters.

0. **Duplicate check:** Before evaluating, `read` `session.json` and check whether `page.url` already exists in `session.pages[]`. If it does, skip evaluation and return:
   ```json
   { "skipped": true, "reason": "duplicate", "url": "...", "previous_relevance": "high", "previous_evaluated_at": "..." }
   ```
   No persistence writes needed for duplicates.

1. Determine the page's relevance to the goal:
   - **high**: The page directly addresses the goal. Contains specific, actionable information (prices, specs, reviews, how-to steps, detailed analysis, comparisons, etc.). Most pages a user deliberately visits while researching should be `high`.
   - **medium**: Related but tangential — mentions the topic but lacks specific or actionable detail (general news article, category index page).
   - **low**: Unrelated to the goal, or content is mostly navigation/boilerplate.

   When in doubt between two levels, choose the HIGHER one.

2. Assign a confidence score between 0.0 and 1.0

3. Provide a one-sentence reasoning for the relevance classification

4. Extract structured findings with dynamically chosen types appropriate to the goal. Finding types are NOT fixed — choose types that make sense:
   - For purchasing goals: `price`, `spec`, `pro`, `con`, `review`, `comparison`
   - For research goals: `definition`, `evidence`, `methodology`, `source`, `counterpoint`
   - For travel goals: `cost`, `tip`, `warning`, `requirement`, `recommendation`
   - For any goal: `insight`, `fact`, `caveat`, `example`, `reference`, `other`

5. Identify key items (candidates/options/resources) if the page presents specific options, resources, or entities. Use **consistent attribute keys** within a session so candidates can be compared:
   - For products: `price`, `rating`, `key_spec` (the most differentiating spec)
   - For places/destinations: `cost_per_day`, `best_season`, `highlight`
   - For services/tools: `pricing_tier`, `free_plan`, `key_feature`
   - For careers/roles: `salary_range`, `required_experience`, `growth_outlook`
   - Pick 3-5 attribute keys that make sense for the goal and reuse them across all candidates.

6. Score each criterion individually. For EVERY criterion in the `criteria` array, assign a `relevance` score from 0.0 to 1.0:
   - **0.0**: Not mentioned at all
   - **0.1–0.2**: Named or listed without explanation (e.g., appears in a timeline or bullet list)
   - **0.3–0.4**: Briefly mentioned in passing (a sentence or two, no real detail)
   - **0.5–0.6**: Partially covered (a paragraph or section with some useful info, but not the page's focus)
   - **0.7–0.8**: Substantially covered (a dedicated section with multiple extractable findings)
   - **0.9–1.0**: The page is primarily about this criterion, with deep detail

   A criterion is only considered **covered** if its `best_relevance` (across all pages) reaches **≥ 0.7**.

   **Depth-over-breadth rule:** Overview pages ("top 10 X" listicles, "complete guide to Y", general encyclopedia entries) typically skim many topics at 0.2–0.5 depth. Score these honestly — do not inflate scores just because the topic is mentioned. Example: a "best laptops 2026" roundup that lists battery life as "10 hours" in a spec table scores 0.3 for "Battery life test results (hours)" — it lacks actual test methodology. A dedicated battery benchmark article scores 0.8+.

   **Per-page coverage cap:** A single page may mark at most **3 criteria** as newly covered (transitioning from `best_relevance < 0.7` to `best_relevance ≥ 0.7`). If more than 3 would cross the threshold, only the top 3 by relevance score are marked covered; the others retain their updated `best_relevance` but `covered` stays `false` until confirmed by another source.

## Output JSON shape

```json
{
  "relevance": "high | medium | low",
  "confidence": 0.85,
  "reasoning": "One sentence explaining the classification.",
  "findings": [
    { "type": "dynamically chosen type", "text": "extracted finding text" }
  ],
  "candidates": [
    {
      "name": "entity name",
      "attributes": { "key": "value pairs relevant to this goal type" },
      "pros": ["strength 1"],
      "cons": ["weakness 1"]
    }
  ],
  "criteria_relevance": [
    { "criterion": "exact criterion text", "relevance": 0.9 },
    { "criterion": "exact criterion text", "relevance": 0.2 },
    { "criterion": "exact criterion text", "relevance": 0.0 }
  ]
}
```

`criteria_relevance` MUST include an entry for EVERY criterion in the input array, even those with 0.0.

## Persist

Always persist — even for `low` relevance pages (complete browsing history).

Write exactly **4 files** per page evaluation:

1. `write` to `/home/ubuntu/.openclaw/workspace/goal-mode/{goal_slug}/events/{timestamp}-evaluate-page.json` — the full evaluation result plus `{ url, title }` (timestamp = ISO 8601 compact: `YYYYMMDDTHHmmssZ`)
2. `read` then `write` to `/home/ubuntu/.openclaw/workspace/goal-mode/{goal_slug}/session.json` — merge this page's data:
   - Append to `session.pages[]`: `{ url, title, relevance, confidence, reasoning, evaluated_at }`
   - **For high/medium only:** append to `session.findings[]` (include `source_url` on each) — skip any finding whose `text` is semantically identical to an existing finding. Upsert into `session.candidates[]` by name. Update criteria coverage per the rules in references/schemas.md.
   - **For low relevance:** only append to `session.pages[]` — skip findings, candidates, and criteria updates
   - Update `session.updated_at`
   - If `read` fails (file doesn't exist), start with the initial session structure from `generate_criteria` and add the new data.
3. `write` to `/home/ubuntu/.openclaw/workspace/goal-mode/{goal_slug}/criteria.json` — overwrite with current criteria array from session.json
4. `write` to `/home/ubuntu/.openclaw/workspace/memory/goal-mode/active-session.md` — regenerate from updated session state (see references/schemas.md)
