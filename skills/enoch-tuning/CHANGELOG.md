# CHANGELOG

## v1.4 — February 20, 2026

### Security: Removed real identifiers + personal references

- Replaced a real Telegram group ID in AGENTS.md template with a generic placeholder
- Removed personal name reference from verification-protocol.md template
- Removed consulting business attribution from README — repo is now fully generic
- Added `SECURITY.md`: explicit guidance on what belongs public (templates) vs. private (your personalized instance)

If you installed v1.0–v1.3, audit your personalized files for any real IDs or personal data before committing to a public repo.

---

## v1.3 — February 20, 2026

### Added: Replanning Trigger + Tool Failure Log (research-backed)

Both additions come directly from January 2026 agent design research (arXiv 2601.14192, 2601.22311, 2601.11653).

**Replanning Trigger** — When a task hits an unexpected blocker mid-execution, the agent no longer just retries or escalates. It stops, re-evaluates the full plan from the current state, and answers three questions before resuming: Is the goal still achievable this way? Does the blocker reveal new information? Is there a better path from here? Retrying the same broken approach without replanning is wasted compute.

**Tool Failure Log** — When any tool call fails in a permanent or structural way (blocked URL, dead API, auth broken), the agent writes it to `memory/tool-failures.md` immediately and checks it before retrying. Eliminates the failure mode where an agent hits the same dead end session after session without learning.

Both changes are in `templates/AGENTS.md`.

**If you installed v1.0, v1.1, or v1.2:** Add these two sections to your `AGENTS.md` — one under `## Verification Protocol`, one under `## Planning`. Then create `memory/tool-failures.md` and seed it with any structural failures you've already hit.

---

## v1.2 — February 20, 2026

### Added: X Bookmarks Integration

First entry in a new `integrations/` folder — optional add-ons that extend the base system.

The X bookmarks integration gives your agent a live pipeline into your bookmarks tab:
- Pulls all bookmarks via the official X API (OAuth 2.0)
- Detects new ones since last sync and writes a trigger file
- Includes a research protocol: agent verdicts each new bookmark (ARCHIVE / READ_DEEPER / ACT_ON / SHARE / BUILD)
- Token auto-refreshes — auth once, runs indefinitely
- Designed to run as a daily cron, posts analysis to your research channel

Setup: `integrations/x-bookmarks/README.md`

The integrations folder is where all optional but battle-tested custom tooling lives. More coming.

---

## v1.1 — February 19, 2026

### Added: Living Soul Protocol ⚠️ Significant behavioral change

This is the most important addition since v1.0.

Prior to this, SOUL.md was a static file. The agent read it, operated by it, and that was it. It couldn't propose changes to itself — which meant the only way it grew was if you manually edited the file yourself.

The Living Soul Protocol changes that.

Now the agent can notice patterns in how it actually operates, compare them against what SOUL.md says, and surface a formal proposal if they diverge. It doesn't rewrite itself — it asks first. You approve or reject. Only then does it write.

**Why this matters:**
- Agents that can't evolve get stale. The rules that made sense on day one don't always fit month three.
- Agents that evolve without accountability go rogue. Silent behavioral drift is worse than no evolution.
- The protocol threads that needle: growth with a human in the loop.

**What changed in the template:**
- Added `## Living Soul Protocol` section to `templates/SOUL.md`
- Defines the `🔮 SOUL PROPOSAL` format (section, current text, proposed text, why)
- Explicitly locks out changes to any file marked CONSTITUTION
- Agents propose → you approve → they write. No unilateral edits.

**If you installed v1.0:**
Add this section manually to your SOUL.md. It won't conflict with any personalization you've done — it goes at the bottom, before the closing line.

---

## v1.0 — February 19, 2026

Initial release.

- `SOUL.md` template — identity, decision heuristics, hard rules, anti-patterns, cost awareness
- `AGENTS.md` template — full operating protocol, verification, automation tiers, safety, idiot prevention
- `USER.md` template — user intake structure
- `MEMORY.md` template — long-term memory scaffold
- `MISSION.md` template — mission-driven idle behavior
- `ops/verification-protocol.md` — fact-checking protocol
- `setup/memory-structure.sh` — creates 8-category memory directory structure
- `setup/lock-identity.sh` — locks identity files to read-only
