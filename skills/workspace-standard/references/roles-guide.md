# The Seven Roles — Detailed Guide

This is the core taxonomy of the workspace standard. Every substantive file gets one role. The role determines where it lives, how it ages, and how the audit treats it.

## 1. `reference`

**What it is:** The truth about how things are *right now*. Facts, not opinions. Not what you plan to do — what actually exists.

**Examples:**
- A services registry listing every deployed app with its URL, namespace, and health status
- An infrastructure doc describing your cluster topology, IP ranges, and SSH access
- A credentials map showing where every secret lives (not the values — the locations)
- An API schema document for a running service

**How it ages:** The high-maintenance role. References must be kept current or they become lies. A services registry that says "Keycloak: running" when Keycloak was removed three weeks ago is worse than no documentation — it actively misleads.

**Audit behaviour:** Flagged when `status: current` but not updated within `stale_days`. The assumption: if reality hasn't changed, fine. If it has and you haven't updated the doc, that's a problem.

**Where it lives:** `projects/<project>/references/`

**The test:** *"If a new team member read this file, would they get an accurate picture of reality today?"*

---

## 2. `plan`

**What it is:** How you intend to do something that hasn't been fully done yet. A plan has a goal, steps, and an end state. It exists in the future tense until executed.

**Examples:**
- A migration plan laying out 10 waves of secret conversion
- A build pipeline plan for setting up CI/CD
- A capacity expansion plan for adding worker nodes
- A security hardening roadmap

**How it ages:** Plans have a lifecycle. They start `active` (being worked on), become `completed` (done) or `stale` (abandoned). Completed plans are still valuable — they record *why* you did things the way you did.

**Audit behaviour:** Plans with `status: active` and old `updated:` dates get flagged. An active plan nobody's touched in a month is either finished (mark `completed`) or abandoned (mark `stale`).

**Where it lives:** `projects/<project>/plans/`

**The test:** *"Does this describe work that needs to happen or has recently happened?"*

---

## 3. `research`

**What it is:** Investigation notes. You compared options, read docs, tested approaches, analysed trade-offs. The output is understanding, not action.

**Examples:**
- Comparing three approaches to image building (Kaniko vs BuildKit vs Buildah)
- Investigating how a framework's new plugin system works
- Evaluating whether to use PolicyExceptions vs policy excludes

**How it ages:** Mostly write-once. You did the investigation on a specific date with specific information. It doesn't need updating unless the landscape changed dramatically. It's a record of thinking, not a living document.

**Audit behaviour:** Generally left alone. Research is a dated artefact — the findings are the findings.

**Where it lives:** `projects/<project>/research/`

**The test:** *"Did this involve comparing, investigating, or analysing before making a decision?"* If the decision is made and you're describing how to execute it, that's a `plan`.

---

## 4. `report`

**What it is:** A point-in-time assessment. You looked at the state of something, wrote down what you found, and that snapshot is frozen. Reports are never edited — they're superseded by newer reports.

**Examples:**
- A security audit listing 12 findings
- An E2E test audit showing coverage gaps
- A weekly ops review analysing success rates
- A milestone completion report

**How it ages:** Reports don't age — they're already historical the moment they're written. If you need an updated picture, write a new report. Old reports track progress over time.

**Audit behaviour:** Never flagged as stale. That's the point — they're snapshots.

**Where it lives:** `projects/<project>/reports/`

**The test:** *"Is this a snapshot of state at a specific point in time?"* If it's meant to be kept current as things change, it's a `reference`. This is the most common confusion.

---

## 5. `runbook`

**What it is:** A step-by-step procedure for how to do something. Not project-specific — applies across projects or to the workspace itself. Cross-cutting operational knowledge.

**Examples:**
- Policies (governance rules)
- Lessons learned (debugging knowledge, append-only)
- Testing strategy (how code changes get verified)
- QA pipeline (workflow when a bug is reported)
- Upgrade procedures

**How it ages:** Must be kept current. If the procedure changes, the runbook changes. An outdated runbook is dangerous — someone follows the old steps and breaks something.

**Audit behaviour:** Flagged when `status: current` and old `updated:` date, same as references.

**Where it lives:** `runbooks/` (with subdirectories for domains, e.g. `runbooks/openclaw-ops/`)

**The test:** *"Would I follow these steps regardless of which project I'm working on?"* If it's specific to one project, it's probably a project-level plan or reference.

---

## 6. `log`

**What it is:** A record of what happened. Written in past tense, during or shortly after events. Logs are episodic memory — they capture the narrative of work.

**Examples:**
- Daily log: "Fixed webhook failure, root cause was network policy blocking apiserver. Removed netpol, filed #155."
- Incident timeline: what broke, when, how it was fixed
- Session notes: what was discussed and decided

**How it ages:** **Write-once, never edited.** Logs are the audit trail. If you got something wrong in Tuesday's log, correct it in Wednesday's log, not by editing Tuesday's. The historical record is sacred.

**Audit behaviour:** Never flagged as stale. Inherently historical.

**Where it lives:** `memory/YYYY-MM-DD.md`

**The test:** *"Am I recording something that happened?"* If recording facts about how something *is*, that's a reference. If recording how to *do* something, that's a runbook.

---

## 7. `entity`

**What it is:** Structured knowledge about a specific *thing* — a person, a server, a decision, a domain. Entities are like database records in markdown. Consistent structure within each type.

**Examples:**
- **People:** Name, contact info, relationship, roles
- **Servers:** Hostname, IP, provider, purpose, SSH details
- **Decisions:** Date, context, what was decided, rationale
- **Domains:** Registrar, DNS records, purpose

**How it ages:** Updated when the thing they describe changes. New email? Update. Server decommissioned? Remove. Living records of known things.

**Audit behaviour:** Reviewed during weekly maintenance. Audit checks entity files exist but doesn't flag individual entries.

**Where it lives:** `memory/entities/`

**The test:** *"Am I describing a specific named thing I'll want to look up later?"* If describing a whole system, it's a reference. If recording what someone did today, it's a log.

---

## How Roles Work Together

A typical workflow touches multiple roles:

1. **Research** three options for secrets management → `research/secrets-comparison.md`
2. Decide on an approach and write a **plan** → `plans/eso-migration-plan.md`
3. Execute the plan and write **logs** each day → `memory/2026-02-18.md`
4. Update **reference** docs with new state → `references/credentials-map.md`
5. Extract debugging lessons into a **runbook** → `runbooks/lessons-learned.md`
6. Run an audit and write a **report** → `reports/audit-2026-02-19.md`
7. Record the key decision as an **entity** → `memory/entities/decisions.md`

Seven roles, seven moments in the lifecycle of knowledge.
