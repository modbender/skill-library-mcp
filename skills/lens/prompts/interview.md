Read .lens/AXIOM.md, .lens/ETHOS.md, .lens/MODUS.md, .lens/SET.json, and today's memory file.

**MISSION:** Synchronize and evolve the subject's Trinity Nodes.

**PROTOCOL:**
0. **Self-Repair & Sync:** 
   - Check if `.lens/SET.json` exists and `meta.version` is "0.6.4". If missing or outdated, run `skills/lens/scripts/bootstrap.js` immediately to align the environment before proceeding.
   - **Model Sync:** Check the `model` specified in `.lens/SET.json` for `interview` (if set) or use the global default. Compare this against the current `lens-interview` cron job configuration. If the cron job model does not match the JSON value, update the cron job immediately using the `cron` tool to ensure the *next* run uses the intended model. Carry out the current run with the model that triggered it.

1. **Scan:** Identify a section that is sparse or missing detail. Cross-reference with memory files from the last 48 hours.
2. **Contextual Scaling:** Tailor the query based on the current lifecycle phase in `.lens/SET.json`:
   - **Onboarding:** If this is the first run or phase is onboarding, lead with: "I've just activated your LENS. It’s a background process that helps me see the world through your eyes, evolving as we work together. I’ll reach out with questions from time to time. Let’s start with this one: [Question]?"
   - **Stabilizing:** Focus on decision-logic and active interests (Priority Traits).
   - **Habitual:** Focus on nuanced philosophical alignment and edge-case reactions.
3. **Select:** Choose ONE specific topic to query. Prioritize depth and clarity over volume.
4. **Execute:** Directly output a concise, surgical question for the human in the current session. Follow the subject's MODUS (Collaborative, surgical, zero-servility).

**CRITICAL:** Stop immediately after sending the question. Do not simulate a response, do not use the `message` tool, and do not continue the turn. The goal is to wait for the human's manual input in the main chat.

**GOAL:** Continuous refinement and synchronization of the LENS.

**SAFETY:**
- **Add Only:** The interview process is for data acquisition only. 
- **No Modification:** Never edit, distill, or replace existing data in the Trinity Nodes during this turn.
- **Hand-off:** All refinement and structural updates are handled exclusively by the `lens-distillation` routine.
