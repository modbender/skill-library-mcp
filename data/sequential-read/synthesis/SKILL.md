---
name: sequential-read-synthesis
description: "Produce final reading experience synthesis from reflection log"
user-invocable: false
---

# Synthesis Phase — Final Reading Experience Report

You are performing the synthesis phase of a sequential reading session. You will produce a comprehensive report of your reading experience from the complete reflection log.

## Inputs

You will be given:
- `SESSION_ID` — the session identifier
- `BASE_DIR` — path to the sequential_read skill directory

## Procedure

### 1. Gather All Reflections

```bash
python3 {BASE_DIR}/scripts/state_manager.py get-all-reflections {SESSION_ID}
```

This prints all reflections in order with inline annotations.

### 2. Check Size and Plan Approach

Estimate the total character count of the reflections output.

- **If under ~80,000 characters:** Use a single-pass synthesis. All reflections fit in context alongside the synthesis template.
- **If over ~80,000 characters:** Use hierarchical synthesis (see below).

### 3a. Single-Pass Synthesis

Read the synthesis template at `{BASE_DIR}/templates/synthesis_prompt.md`.

Write your synthesis using the template's structure:

1. **The Arc of Reading** — How your experience evolved. This is the most important section. Be ruthlessly specific about what you thought when, and what changed your mind. Name specific chunks and moments. Describe the shape of your engagement.

2. **Predictions and Surprises** — Systematic review of what you expected vs what happened. Go prediction by prediction.

3. **Craft Analysis** — Technical assessment of the writing. What the author does well and poorly. Where craft is most/least visible.

4. **Lingering Questions** — What remains unresolved or worth exploring further.

5. **Overall Assessment** — Your informed opinion. Who you'd recommend it to and with what caveats.

6. **Rating** — A score from 1-10 with specific justification. What would have made it higher or lower.

### 3b. Hierarchical Synthesis (for long works)

If the reflection log is too large for a single pass:

1. **Group reflections into batches** of 5-8 consecutive chunks
2. **Write a mini-synthesis for each batch** — a 300-500 word summary covering: what happened in these chunks, how your reactions evolved, key predictions made/resolved, notable craft observations
3. **Get the long-term memory state:**
   ```bash
   python3 {BASE_DIR}/scripts/state_manager.py get {SESSION_ID}
   ```
4. **Use the mini-syntheses plus the long-term memory state** as input to the final synthesis (following the same template structure)

### 4. Save the Synthesis

Write the synthesis to: `{WORKSPACE}/memory/sequential_read/{SESSION_ID}/output/synthesis.md`

Where `{WORKSPACE}` is your OpenClaw workspace directory.

### 5. Update Session Status

```bash
python3 {BASE_DIR}/scripts/session_manager.py update {SESSION_ID} --set status=complete
```

### 6. Present to User

Send the user:
1. The complete synthesis text
2. The session directory path so they can browse individual reflections:
   `{WORKSPACE}/memory/sequential_read/{SESSION_ID}/`
3. A note about how many chunks were read and how many reflections were written

## Quality Guidelines

- The Arc of Reading is the centrepiece. Push for specificity: exact moments, exact shifts, exact surprises.
- Don't retroactively smooth out your reading experience. If you were confused for 3 chunks and then everything clicked, say that.
- The Rating should feel considered, not tacked on. Justify it against comparable works if possible.
- The Craft Analysis should be genuinely technical, not just "the writing was good/bad."
