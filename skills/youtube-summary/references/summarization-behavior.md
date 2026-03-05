# youtube-summary behavior

This file defines how summaries are produced across modes.

## Modes and summary source

- **Full mode** (`run_youtube2md.sh <url> full ...`)
  - `youtube2md` generates Markdown summary output.
  - Use generated `.md` as the canonical summary source.
  - Do not re-summarize from raw transcript unless the user asks for a rewritten style.

- **Extract mode** (`run_youtube2md.sh <url> extract ...`)
  - `youtube2md` generates transcript JSON.
  - Runner then executes `prepare.py` to generate transcript text (`.txt`) from `segments[].text`.
  - Summarize using the prepared `.txt` as the primary source.

## Extract-mode summarization workflow

1. Load metadata (title, duration, publish date, URL/video id) from JSON when available.
2. Load transcript text from `.txt`.
3. Build a structured summary in this order:
   - `## Summary` (single dense paragraph)
   - `## Chapters` (chronological thematic sections)
   - `## Key Takeaways` (practical bullets)
4. Preserve factual values exactly when mentioned (prices, throughput, ping, wattage, dates).

## Chaptering heuristics

- Prefer **3-7 chapters** for ~10-30 minute videos.
- Use concise section titles (topic/action based).
- Keep each chapter bullet list factual (2-4 bullets).
- Avoid duplicate bullets across chapters.

## Key takeaways heuristics

- Prefer **6-10 takeaways**.
- Prioritize user-facing decisions:
  - when to use / when not to use
  - performance expectations and variability
  - cost and operational tradeoffs
- Include caveats and constraints (installation conditions, environment assumptions).

## Quality guardrails

- Do not hallucinate specs, pricing, benchmarks, or policy claims.
- If transcript quality is noisy, still extract stable facts and explicitly mark uncertain details.
- Keep summary language aligned with transcript/user language (Korean transcript → Korean summary unless requested otherwise).
