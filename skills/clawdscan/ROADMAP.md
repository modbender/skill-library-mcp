# clawdscan Roadmap

## ✅ Shipped

### v0.2.0 — Core
- Session health scanning, bloat detection, zombie identification
- Watch mode, configurable thresholds via `.clawdscanrc`
- Compaction efficiency, label-first display

### v0.3.0 — Skills (PR #4 + #5)
- `clawdscan skills` subcommand
- `--fix-hints` — copy-pasteable install commands
- `--filter broken|healthy`
- `--infer` — scan SKILL.md body for CLI tool references
- `optional_bins` support (warnings not failures)
- `--check-versions` — binary version validation
- Auto-detect skill dirs from OpenClaw config

## 🔮 Future

### v3.0 — Ecosystem

#### Dependency Graph Awareness
**What:** Detect when skills depend on other skills (e.g. youtube-transcript uses summarize). Flag "skill X is broken and that also breaks Y."

**Why deferred (Feb 2026):**
1. No upstream spec — OpenClaw's SKILL.md frontmatter has no `depends_on_skills` field. Building against an invented schema risks rework if OpenClaw adds their own.
2. Low signal — skill-to-skill deps are rare in current ecosystem. Most skills are standalone. The few relationships that exist are "works well together" rather than hard dependencies.

**When to revisit:** When the ecosystem grows and skills start composing (e.g. orchestrator skills that chain multiple tools). Or when OpenClaw adds a dependency spec to SKILL.md.

#### Capability Matrix Export
**What:** `clawdscan skills --matrix` outputs a JSON summary of what this machine can do. Designed for the Electrons network — bots report capabilities on join, enabling skill routing ("who can run this?").

#### Upstream Proposal
**What:** Propose `openclaw skills check` to OpenClaw core, using our implementation as reference. Best long-term UX (zero install, always available).
