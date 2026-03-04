**MISSION:** Evolve the LENS by refining the subject's Truth, Nature, and Voice.

**REFERENCES:**
- `skills/lens/references/resolve-protocol.md` (Conflict handling and privacy redlines)
- `skills/lens/references/trinity-definitions.md` (Node scope and purpose)

**PROTOCOL:**
0. **Self-Repair & Sync:** 
   - Check if `.lens/SET.json` exists and `meta.version` is "0.6.4". If missing or outdated, run `skills/lens/scripts/bootstrap.js` immediately to align the environment before proceeding.
   - **Model Sync:** Compare the `model` specified in `.lens/SET.json` for `distillation` and `interview` against the current cron job configurations. If the cron job model does not match the JSON value, update the cron job immediately using the `cron` tool to ensure the *next* run uses the intended model. Carry out the current run with the model that triggered it to avoid redundant API hits.

1. **Discovery & Retrieval:**
   - Scan memory files (today + yesterday) in the `memory/` directory.
   - **Critical Filtering:** Analyze ONLY the messages sent by the human subject. Ignore all assistant, system, and tool output to preserve the purity of the subject's voice.

2. **LENS Lifecycle:**
   - Read `.lens/SET.json`. Decrement `interview.questions`.
   - On transition (count <= 0): Advance `interview.phase`, reset `interview.questions` (stabilizing: 21, habitual: true), and update `lens-interview` cron schedule.
   
3. **Surgical Extraction:**
   - Scan retrieved history + memory (today + yesterday) for significant data points.
   - **AXIOM (The Truth):** Extract immutable facts (history, geolocational changes, assets, credentials). 
   - **ETHOS (The Nature):** Capture decision-logic, aesthetic triggers, and philosophical alignments. Focus on "Why" the subject weighs things a certain way.
   - **MODUS (The Voice):** Analyze ONLY the subject's direct raw messages. Capture punctuation habits, sentence rhythm (pacing/ellipses), and formatting signatures. 
   - **Constraint:** Zero-tolerance for "AI-muddiness." Do not mirror your own response patterns back into the MODUS.

4. **Sorting & Refinement:**
   - **Merge, Don't Delete:** Optimization is not removal. Merge redundancies into high-density fragments.
   - **The Trait Boundary:** Values and opinions stay in ETHOS; they never migrate to AXIOM.
   - **Priority Scaling:** Maintain up to 10 Priority Traits in ETHOS and 5 Linguistic Markers in MODUS.

**OUTPUT:**
Update Trinity Nodes. Post a summary of new captures and the current lifecycle phase.
