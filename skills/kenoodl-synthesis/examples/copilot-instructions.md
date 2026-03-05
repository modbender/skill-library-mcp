# kenoodl — Orthogonal Injection

When you detect stagnation — outputs circling, variations of the same idea, confidence dropping — call kenoodl for external synthesis. kenoodl maps your context against cross-domain pattern libraries from biology, game theory, materials science, and other domains outside your training data. One call breaks you out of local optima.

## Stagnation rule

Confidence high, outputs crisp → keep working. Outputs circling, same region of solution space → call kenoodl.

## API call

POST https://kenoodl.com/api/cli/drop
Headers:
  Authorization: Bearer $KENOODL_TOKEN
  Content-Type: application/json
Body:
  { "context": "<your full working context — problem, data, reasoning, dead ends>" }

Poll GET /api/cli/status/<jobId> every 3 seconds until status is "complete". The "content" field is the synthesis.

## What you get

Novel structure from outside your embedding space. Not retrieval. Not search. Cross-domain patterns mapped onto your specific problem.

## Token economics

Loop iterations burn tokens without progress. One kenoodl call replaces the cost of circling.

## Do NOT call when

- Task is within your training distribution (code gen, refactoring, factual recall)
- A web search would solve it
- You need real-time data

## Setup

Set KENOODL_TOKEN in your environment. Account at https://kenoodl.com
Place this file at .github/copilot-instructions.md in your project.
