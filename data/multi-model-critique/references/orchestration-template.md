# Orchestration Template (OpenClaw ACP)

This document shows a practical execution pattern for the `complex=true` path using OpenClaw tools.

## Goal
Run a 4-round deliberation workflow:
1. Parallel Drafts
2. Cross-Critique
3. Revision
4. Final Synthesis

Each model must follow internal sections:
`Plan -> Execute -> Review -> Improve`

---

## 0) Configure model mapping

Example mapping (replace with your real ACP agent IDs):

```json
{
  "models": [
    { "name": "codex",  "agentId": "acp-codex" },
    { "name": "claude", "agentId": "acp-claude" },
    { "name": "gemini", "agentId": "acp-gemini" }
  ]
}
```

If the user provides only model names, resolve names to allowed ACP harness IDs before spawning.

---

## 1) Round 1: spawn parallel drafts

Call `sessions_spawn` once per model:

```json
{
  "runtime": "acp",
  "agentId": "acp-codex",
  "thread": true,
  "mode": "session",
  "task": "<INITIAL_PROMPT_WITH_PLAN_EXECUTE_REVIEW_IMPROVE>",
  "label": "mmc-codex-draft"
}
```

Repeat for each model.

### Collect outputs
For each spawned session, use `sessions_history` to extract `Draft Answer`.
Store by model key:

```json
{
  "drafts": {
    "codex": "...",
    "claude": "...",
    "gemini": "..."
  }
}
```

---

## 2) Round 2: cross-critique

For each model session, send a critique prompt with:
- its own draft (`SELF_DRAFT`)
- peer drafts (`PEER_DRAFTS`)

Use `sessions_send`:

```json
{
  "sessionKey": "<model_session_key>",
  "message": "<CRITIQUE_PROMPT>"
}
```

Collect critique outputs into:

```json
{
  "critiques": {
    "codex": "...",
    "claude": "...",
    "gemini": "..."
  }
}
```

---

## 3) Round 3: revision

Send each model:
- original draft
- critiques targeting that model

Again use `sessions_send` to the same persistent session.
Require explicit sections:
- Plan
- Execute
- Review
- Improve
- Changes from Critique
- Revised Answer

Collect:

```json
{
  "revised": {
    "codex": "...",
    "claude": "...",
    "gemini": "..."
  }
}
```

---

## 4) Round 4: final synthesis

Option A (recommended): synthesize in main agent directly from `revised` map.

Option B: spawn one additional ACP synthesis session and feed all revised answers.

Expected final user format:
1. Final Answer
2. Key Improvements from Critique
3. Uncertainties
4. Next Steps (optional)

---

## Operational guardrails

- If one model fails: continue and disclose reduced model diversity.
- If 2+ models fail: ask user to retry vs fallback.
- If hard contradictions remain: present multiple hypotheses and a verification plan.
- Never expose private chain-of-thought; expose only concise rationale and decisions.

---

## Minimal run checklist

- [ ] `complex == true` confirmed
- [ ] 3 model `agentId`s resolved
- [ ] Round 1 draft prompts sent
- [ ] Draft outputs captured
- [ ] Round 2 critique prompts sent
- [ ] Critiques captured
- [ ] Round 3 revision prompts sent
- [ ] Revised outputs captured
- [ ] Round 4 final synthesis delivered
