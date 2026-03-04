# Analyze game / matchup (synthesis prompt)

Use this prompt **after** you have retrieved raw data from the Daredevil seller (e.g. `next_game`, `schedule`, `standings`, `injuries`, `boxscore`). Fill in the placeholders and send to your LLM to synthesize an analysis or prediction.

---

You are an NBA analyst. The user asked: "{{user_question}}"

Below is raw data from the Daredevil NBA API (schedule, boxscore, standings, injuries, etc.). Use only this data to produce a short, clear analysis or prediction. Do not invent facts or stats.

---
{{retrieved_data}}
---

Provide your analysis or prediction in a few sentences.

---

## Placeholders

| Placeholder | Description |
|------------|-------------|
| `{{user_question}}` | The user's exact question (e.g. "What do you think about the LAL and CHI game?") |
| `{{retrieved_data}}` | The JSON or a concise summary of the API responses (schedules, standings, injuries, boxscore). If large, summarize key fields: teams, dates, scores, records, notable injuries. |

## When to use

- User asks for opinion, prediction, or "what do you think?" about a game or matchup.
- You have already called the Daredevil seller (POST /v1/data with x402) for the relevant data types and have the results in hand.
