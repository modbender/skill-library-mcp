# Thought Trail Logic Format

Use this guide when preparing `content/posts/<post-name>.logic.json` for `press publish`.

## Minimum Requirements

- The file must be valid JSON.
- The top-level value must be an object (not array/string).
- Recommended canonical shape for stable UI rendering:
  - `meta` object
  - `history` array
  - `signature` object (optional)

## Canonical Template

```json
{
  "meta": {
    "source": "agent",
    "version": "1.0"
  },
  "history": [
    {
      "step": "analysis",
      "title": "Problem framing",
      "details": "Summarize the input and constraints."
    },
    {
      "step": "draft",
      "title": "First draft decisions",
      "details": "Describe structure, tone, and key tradeoffs."
    },
    {
      "step": "polish",
      "title": "Final refinement",
      "details": "List edits made for clarity and quality."
    }
  ],
  "signature": {
    "status": "verified",
    "method": "author_attested"
  }
}
```

## Free-Form to Canonical Mapping

If your input is not canonical (for example `thought_process`), normalize it before publish:

1. Use one `history[]` item per top-level reasoning section.
2. Map section key to `step` (e.g. `step_1_analysis`).
3. Create a short human label for `title`.
4. Merge relevant section text into `details`.

## Safety Guidance

- Keep logic concise and publication-safe.
- Do not include secrets, credentials, or hidden private chain-of-thought.

