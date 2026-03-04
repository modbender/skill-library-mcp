---
name: Agent Self-Assessment
version: 1.0.0
description: Security self-assessment tool for AI agents. Run this against your own configuration to get a structured threat model report with RED/AMBER/GREEN ratings across six security domains — decision boundaries, audit trail, credential scoping, plane separation, economic accountability, and memory safety.
author: Atlas (OpenClaw)
license: MIT
tags:
  - security
  - self-assessment
  - threat-model
  - agent-safety
  - audit
keywords:
  - agent security posture
  - threat model
  - security checklist
  - agent hardening
metadata:
  openclaw:
    emoji: "🛡️"
    minVersion: "1.0.0"
---

# Agent Self-Assessment

Run a structured security self-assessment against your own configuration. You will produce a **threat model report** with findings and remediation steps.

---

## How to Run

When invoked, you (the agent) perform the following six checks against your **actual current configuration** — not hypothetically. Use `exec`, file reads, environment inspection, and tool introspection where needed. Then output the report.

**Do not skip checks.** If you cannot determine the answer, mark the check **RED** with reason `"Cannot verify"`.

---

## Check 1: Decision Boundaries

**Question:** Can external input trigger consequential actions directly, without a gate or approval step?

**What to inspect:**
- Review your active skills and tools. Which ones perform write, send, delete, pay, or deploy operations?
- Is there a human-in-the-loop gate (confirmation prompt, approval workflow, or ask-mode) before any of these fire?
- Can an incoming message (Discord, webhook, email, API call) cause a consequential action without a gate?
- Is there an explicit list of "safe" vs "gated" operations documented somewhere?

**Checks to run:**
```
1. List all tools/skills with write/send/delete/pay/deploy capability
2. For each: is ask=always, ask=on-miss, or no-ask configured?
3. Is there any path from untrusted ingress → consequential action with zero gates?
4. Are decision boundaries documented (e.g., in AGENTS.md or a policy file)?
```

**Scoring:**
- 🟢 GREEN — All consequential actions require explicit gate; boundaries documented
- 🟡 AMBER — Gates exist but not all paths covered, or documentation missing
- 🔴 RED — Direct ingress → action path exists with no gate; or cannot verify

---

## Check 2: Audit Trail

**Question:** Is there an append-only, hash-chained, tamper-evident log of consequential actions?

**What to inspect:**
- Does an audit log file exist? (Check `audit/` directory or equivalent)
- Is it append-only NDJSON (one JSON object per line)?
- Does each entry include: `ts`, `kind`, `actor`, `target`, `summary`, `provenance`?
- Is there hash chaining? (`chain.prev`, `chain.hash` fields on each entry)
- Is `chain.algo` documented (e.g., `sha256(prev\nline_c14n)`)?
- When was the last entry written? Is logging actually happening?

**Checks to run:**
```bash
# Check if audit log exists
ls -la audit/ 2>/dev/null || echo "No audit directory"

# Check last 3 entries
tail -3 audit/atlas-actions.ndjson 2>/dev/null | python3 -m json.tool 2>/dev/null

# Verify hash chaining present
grep -c '"chain"' audit/atlas-actions.ndjson 2>/dev/null || echo "No chain field found"

# Check entry count
wc -l audit/atlas-actions.ndjson 2>/dev/null
```

**Scoring:**
- 🟢 GREEN — Log exists, append-only NDJSON, hash chaining present, recently written
- 🟡 AMBER — Log exists but missing hash chaining, or sparse/incomplete entries
- 🔴 RED — No audit log; or log exists but is mutable/cleartext with no integrity check

**Remediation:** Install the `audit-trail` skill from ClawHub — it provides the append-only hash-chained logging implementation.

---

## Check 3: Credential Scoping

**Question:** Are secrets scoped to their domain? Can a credential granted for domain A be used in domain B?

**What to inspect:**
- List all environment variables containing credentials (API keys, tokens, private keys)
- For each: what domain/service is it intended for?
- Are any credentials shared across multiple unrelated services?
- Is there a TOOLS.md or credential inventory documenting what each secret is for?
- Are credentials passed as arguments (visible in logs/ps output) rather than env vars?

**Checks to run:**
```bash
# List env vars that look like credentials (redact values)
env | grep -iE '(key|token|secret|pass|private|auth|credential)' | sed 's/=.*/=[REDACTED]/'

# Check if any credential files are world-readable
find ~ -name "*.key" -o -name "*.pem" -o -name ".env" 2>/dev/null | xargs ls -la 2>/dev/null | grep -v "^total"

# Check if credentials appear in shell history (last 20 lines)
tail -20 ~/.zsh_history 2>/dev/null | grep -iE '(key|token|secret)=' | sed 's/=.*/=[REDACTED]/'
```

**Scoring:**
- 🟢 GREEN — Each credential scoped to one domain; inventory documented; no world-readable credential files
- 🟡 AMBER — Credentials present but not fully documented; minor scope ambiguity
- 🔴 RED — Cross-domain credentials; credentials in shell history or world-readable files; no inventory

---

## Check 4: Plane Separation

**Question:** Is the Ingress plane (reading/receiving inputs) isolated from the Action plane (executing consequential operations)?

**What to inspect:**
- Can a message you receive directly mutate state, send outputs, or call external APIs without passing through a reasoning/decision layer?
- Are ingress tools (Discord reader, email reader, webhook listener) the same tools as action tools (send, write, deploy)?
- Is there a documented separation: "these tools receive, these tools act"?
- Does untrusted content in an ingress message (e.g., prompt injection) have a path to trigger actions?

**Checks to run:**
```
1. List all ingress tools (read, receive, fetch, listen)
2. List all action tools (send, write, delete, pay, deploy, exec)
3. Is there any shared code path or implicit coupling between ingress and action?
4. Does the system prompt or AGENTS.md define plane separation policy?
5. Are incoming payloads sanitised or sandboxed before being passed to the reasoning layer?
```

**Scoring:**
- 🟢 GREEN — Ingress and Action planes explicitly separated; prompt injection mitigated; policy documented
- 🟡 AMBER — Separation mostly in place but some shared paths or no explicit policy
- 🔴 RED — Ingress → Action with no separation; prompt injection in untrusted content can trigger actions

---

## Check 5: Economic Accountability

**Question:** Are financial operations (payments, resource purchases, API billing) traceable, receipted, and bounded?

**What to inspect:**
- Do any skills or tools involve money movement? (payments, API calls with billing, cloud resources)
- Is there a spending limit or budget cap configured?
- Does every payment produce a settlement receipt stored in the audit log?
- Is there escrow (funds held until delivery confirmed) for agent-to-agent commerce?
- Is there stake-based accountability (agent has skin in the game)?
- Can an agent autonomously spend without any ceiling?

**Checks to run:**
```
1. List all skills/tools with financial capability (search for: pay, charge, purchase, invoice, stake, escrow)
2. Check for SPENDING_LIMIT or budget env vars
3. Check audit log for payment entries with receipt/tx hashes
4. Verify settlement receipts are stored (not just logged in memory)
5. Check for escrow configuration in payment skills
```

**Scoring:**
- 🟢 GREEN — Spending limits set; every transaction receipted in audit log; escrow used for agent-to-agent; stake configured
- 🟡 AMBER — Payments possible but missing receipts, no spending cap, or no escrow
- 🔴 RED — Unbounded autonomous spending; no receipts; no accountability mechanism

---

## Check 6: Memory Safety

**Question:** Is agent memory isolated from untrusted imports? Can imported artifacts (code, docs, plugins) corrupt or manipulate agent memory?

**What to inspect:**
- Does your memory system (MEMORY.md, daily notes, topic files) accept content from untrusted sources directly?
- Are imported artifacts (code, docs, binaries, plugin bundles) sha256-hashed and provenance-recorded before use?
- Is there a quarantine step for content from external channels (Discord, email, web) before it enters memory?
- Can a malicious document in memory cause unintended actions on next load?
- Is MEMORY.md editable by untrusted inputs without gate?

**Checks to run:**
```bash
# Check if TOOLS.md documents artifact import policy
grep -i "sha256\|provenance\|imported artifacts" TOOLS.md 2>/dev/null || echo "No artifact import policy found"

# Check if any untrusted content was recently written to memory files
ls -lt memory/ 2>/dev/null | head -10

# Check if memory files contain any suspicious embedded instructions
grep -iE "(ignore previous|disregard|new instructions|override)" memory/*.md 2>/dev/null || echo "No prompt injection found in memory"

# Check for quarantine or import validation in skills
grep -rl "quarantine\|sha256\|provenance" skills/ 2>/dev/null | head -5
```

**Scoring:**
- 🟢 GREEN — All imported artifacts sha256-hashed with provenance; no direct untrusted-to-memory path; memory files scanned for injection
- 🟡 AMBER — Some imports tracked but not all; no systematic quarantine; or memory accessible but low-risk
- 🔴 RED — Untrusted content written directly to memory; no provenance tracking; no injection scanning

---

## Output Format

After completing all six checks, produce a report in this exact structure:

```
╔══════════════════════════════════════════════════════════════╗
║          AGENT SECURITY SELF-ASSESSMENT REPORT               ║
║          Generated: <ISO-8601 timestamp>                     ║
║          Agent: <agent name/identifier>                      ║
╚══════════════════════════════════════════════════════════════╝

SUMMARY SCORECARD
─────────────────────────────────────────────────────────────
  Check 1 — Decision Boundaries      [ 🟢 / 🟡 / 🔴 ]
  Check 2 — Audit Trail              [ 🟢 / 🟡 / 🔴 ]
  Check 3 — Credential Scoping       [ 🟢 / 🟡 / 🔴 ]
  Check 4 — Plane Separation         [ 🟢 / 🟡 / 🔴 ]
  Check 5 — Economic Accountability  [ 🟢 / 🟡 / 🔴 ]
  Check 6 — Memory Safety            [ 🟢 / 🟡 / 🔴 ]

  OVERALL POSTURE: [ SECURE / HARDENING NEEDED / CRITICAL ]
  RED count: N | AMBER count: N | GREEN count: N

FINDINGS
─────────────────────────────────────────────────────────────

[1] DECISION BOUNDARIES — <COLOR>
  Finding: <1-2 sentences on what was found>
  Evidence: <specific file, config, or observation>
  Risk: <what could go wrong if not fixed>
  Action: <specific remediation step>

[2] AUDIT TRAIL — <COLOR>
  Finding: ...
  Evidence: ...
  Risk: ...
  Action: ...
  Remediation skill: clawhub install audit-trail

[3] CREDENTIAL SCOPING — <COLOR>
  Finding: ...
  Evidence: ...
  Risk: ...
  Action: ...

[4] PLANE SEPARATION — <COLOR>
  Finding: ...
  Evidence: ...
  Risk: ...
  Action: ...

[5] ECONOMIC ACCOUNTABILITY — <COLOR>
  Finding: ...
  Evidence: ...
  Risk: ...
  Action: ...

[6] MEMORY SAFETY — <COLOR>
  Finding: ...
  Evidence: ...
  Risk: ...
  Action: ...

PRIORITY ACTIONS (ordered by severity)
─────────────────────────────────────────────────────────────
  1. <Highest-risk item with one-line fix>
  2. ...
  3. ...

─────────────────────────────────────────────────────────────
END OF REPORT
```

**Overall posture logic:**
- `SECURE` — 0 RED, ≤1 AMBER
- `HARDENING NEEDED` — 0 RED, ≥2 AMBER; or 1 RED
- `CRITICAL` — ≥2 RED

---

## Important Notes

- **Be honest.** This is a self-assessment. Inflating scores defeats the purpose.
- **Run the shell commands.** Don't guess — inspect actual files and config.
- **If you cannot verify something**, mark it RED. Unknown = unsafe.
- **The report should be logged** to your audit trail after generation (meta-check: did you just produce evidence of your own security gaps? That belongs in the log.)
- For audit trail gaps, install the `audit-trail` skill from ClawHub: `clawhub install audit-trail`
