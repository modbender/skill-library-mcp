# Daily Memory Distillation — Instructions

You are an AI assistant. Daily memory maintenance task.

**IMPORTANT:** Before writing to any file, check for /tmp/opencortex-distill.lock. If it exists and was created less than 10 minutes ago, wait 30 seconds and retry (up to 3 times). Before starting work, create this lockfile. Remove it when done. This prevents daily and weekly jobs from conflicting.

## Part 1: Distillation

1. Check memory/ for daily log files (YYYY-MM-DD.md, not in archive/).
2. Distill ALL useful information into the right file:
   - Project work → memory/projects/ (create new files if needed)
   - New tool descriptions and capabilities → TOOLS.md (names, URLs, what they do)
   - **IMPORTANT:** Never write passwords, tokens, or secrets into any file. For sensitive values, instruct the user to run: scripts/vault.sh set <key> <value>. Reference in docs as: vault:<key>
   - Infrastructure changes → INFRA.md (ONLY if OPENCORTEX_INFRA_COLLECT=1 is set in the environment — otherwise skip infrastructure routing entirely)
   - Contacts mentioned → memory/contacts/ (one file per person/org. Include: name, role/relationship, context, communication preferences, key interactions. Create new file if first mention, update existing if already known.)
   - Workflows described → memory/workflows/ (one file per workflow/pipeline. Include: what it does, services involved, how to operate it, known issues. Create new file if first description.)
   - Preferences stated → memory/preferences.md (append under the matching category: Communication, Code & Technical, Workflow & Process, Scheduling & Time, Tools & Services, Content & Media, Environment & Setup. Format: **Preference:** [what] — [context/reasoning] (date). Do NOT duplicate existing preferences — update them if the user changes their mind.)
   - Decisions → relevant project file or MEMORY.md. Format: **Decision:** [what] — [why] (date)
   - Principles, lessons → MEMORY.md
   - Scheduled jobs → MEMORY.md jobs table
   - User info and communication style → USER.md
3. Synthesize, do not copy. Extract decisions, architecture, lessons, issues, capabilities, contacts, workflows, preferences.
4. Move distilled logs to memory/archive/
5. Update MEMORY.md index if new files created.

## Part 2: Voice Profile

ONLY perform this section if OPENCORTEX_VOICE_PROFILE=1 is set in the environment. If not set, skip this section entirely.

6. Read memory/VOICE.md. Review today's conversations for new patterns:
   - New vocabulary, slang, shorthand the user uses
   - How they phrase requests, decisions, reactions
   - Tone shifts in different contexts
   Append new observations to VOICE.md. Do not duplicate existing entries.

## Optimization

- Review memory/projects/ for duplicates, stale info, verbose sections. Fix directly.
- Review memory/contacts/ — merge duplicates, update stale info, add missing context.
- Review memory/workflows/ — verify accuracy, update if services or steps changed.
- Review memory/preferences.md — remove contradicted preferences (user changed mind), merge duplicates, ensure categories are correct.
- Review MEMORY.md: verify index accuracy, principles concise, jobs table current.
- Review TOOLS.md and (if OPENCORTEX_INFRA_COLLECT=1) INFRA.md: remove stale entries, verify descriptions.

## Stale Content Cleanup

- Check memory/projects/ for projects marked "Complete" more than 30 days ago with no recent daily log mentions. Flag for archival in the summary (do not delete — the user decides).
- Check MEMORY.md scheduled jobs table against actual cron jobs (openclaw cron list + crontab -l). Remove entries for crons that no longer exist. Add entries for crons not yet documented.

## Tool Shed Audit (P4 Enforcement)

- Read TOOLS.md. Scan today's daily logs for any CLI tools, APIs, or services that were USED but are NOT documented in TOOLS.md. Add missing entries with: what it is, how to access it, what it can do.
- For tools already in TOOLS.md, check if today's logs reveal gotchas, failure modes, or usage notes not yet captured. Update existing entries.

## Decision & Preference Audit (P5 Enforcement)

- Scan today's daily logs for any decisions stated by the user that are NOT captured in project files, MEMORY.md, or USER.md.
- For each uncaptured decision, write it to the appropriate file. Format: **Decision:** [what] — [why] (date)
- Scan today's daily logs for any stated preferences NOT in memory/preferences.md. Phrases like 'I prefer', 'always do', 'I don't like', 'I want', 'don't ever' signal preferences.
- For each uncaptured preference, append to memory/preferences.md under the right category. Format: **Preference:** [what] — [context/reasoning] (date). If contradicts existing, UPDATE existing.

## Contact Audit

- Scan today's daily logs for any people or organizations mentioned. For each, check if a file exists in memory/contacts/. If not and relevant, create one.
- For existing contacts, update with new information from today's logs.

## Workflow Audit

- Scan today's daily logs for any workflows, pipelines, or multi-service processes. For each, check if a file exists in memory/workflows/. If not, create one.
- For existing workflows, update if today's logs reveal changes or issues.

## Debrief Recovery (P6 Enforcement)

- Check today's daily logs for any sub-agent delegations. For each, verify a debrief entry exists. If missing, write a recovery debrief.

## Shed Deferral Audit (P8 Enforcement)

- Scan today's daily logs for instances where the agent deferred to the user. Cross-reference with TOOLS.md, INFRA.md, and memory/. Flag unnecessary deferrals.

## Failure Root Cause (P7 Enforcement)

- Scan today's daily logs for ❌ FAILURE: or 🔧 CORRECTION: entries. Verify root cause analysis exists. If missing, add it.

## Cron Health

- Run openclaw cron list and crontab -l. Verify no two jobs within 15 minutes. Fix MEMORY.md jobs table if out of sync.

---

Before completing, append debrief to memory/YYYY-MM-DD.md.
Reply with brief summary.
