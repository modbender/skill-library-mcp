## Session Start — Mandatory Context Load (add to your AGENTS.md)

On EVERY new session (including /new, /reset, greeting messages), BEFORE answering:
1. **Session Recovery Check** — Run `bash ~/your-workspace/skills/total-recall/scripts/session-recovery.sh` to capture any observations missed by the reactive watcher (5th layer of redundancy — catches gaps between `/new` and Observer runs)
2. `memory/observations.md` — always load (auto-generated cross-session memory from Observer agent)
3. `memory/favorites.md` — always load (critical facts, urgent items)
4. `memory/YYYY-MM-DD.md` for TODAY — always read directly (not via search)
5. `memory/YYYY-MM-DD.md` for YESTERDAY — always read directly
6. THEN run `memory_search` for additional context

**Do not rely solely on semantic search** — it may rank today's updates low if the query is broad.
**Do not trust favorites.md alone** — daily memory files have the latest status updates.

**Why session recovery:** The reactive watcher (40-line trigger) has a 5-min cooldown. If `/new` happens during that cooldown, observations are lost. Session recovery checks the last session file's hash against what was observed.

Together these provide **5-layer redundancy**: 15-min cron → reactive watcher → pre-compaction hook → session recovery → manual file loading.
