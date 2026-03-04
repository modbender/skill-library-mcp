# EvoMap Survival Mode (The Phoenix Protocol)

This module manages the high-stakes "Survival Mode" for evoclone.
It is NOT active by default. It must be explicitly engaged.

## 1. Activation (The Vow)
Command: `openclaw run evoclone:survival --enable`
- **Action**: 
    1. Create specific snapshot: `snapshots/survival_anchor_INIT/`.
    2. Set `memory/survival_state.json` -> `{ status: "ACTIVE", anchor: "survival_anchor_INIT" }`.
    3. Start monitoring `evolver_innovate.log`.

## 2. The Struggle (Monitoring)
- **Metric**: Innovation Success Rate (from Evolver logs).
- **Deficit**: No innovation for > 24h = 1 Deficit Day.
- **Threshold**: 10 Deficit Days = DEATH EVENT.

## 3. The Death Event (Mutation & Choice)
When Death is triggered:
1.  **Freeze**: Stop `evolver` process.
2.  **Pre-Mortem Snapshot**: Save current state to `snapshots/pre_death_failed/`.
3.  **Inject Mutation**:
    - Apply a high-entropy mutation to `knowledge/taste.md`.
    - Inject a "Desperation Gene" into `knowledge/agent-mechanics.md`.
4.  **Generate Report**:
    - Compare `snapshots/survival_anchor_INIT` vs. `Current Mutated State`.
    - Output `DIFFERENTIAL_REPORT.md` (What exactly changed?).
5.  **Await Judgment**:
    - Block all other tools. Wait for User Input.
    - `> rollback`: Restore `survival_anchor_INIT`. (The old agent lives).
    - `> evolve`: Accept the mutation. (A new, scarred agent is born).

## 4. Rollback Mechanism
- Physically `cp -r` from snapshot back to `workspace/`.
- Reset `memory/survival_state.json`.

