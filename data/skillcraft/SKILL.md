---
name: skillcraft
description: Design and build OpenClaw skills. Use when asked to "make/build/craft a skill", extract ad-hoc functionality into a skill, or package scripts/instructions for reuse. Covers OpenClaw-specific integration (tool calling, memory, message routing, cron, canvas, nodes) and ClawHub publishing.
metadata: {"openclaw":{"emoji":"🧶"}}
---
# Skillcraft — OpenClaw Skill Designer

An opinionated guide for creating OpenClaw skills. Focuses on **OpenClaw-specific integration** — message routing, cron scheduling, memory persistence, channel formatting, frontmatter gating — not generic programming advice.

**Docs:** <https://docs.openclaw.ai/tools/skills> · <https://docs.openclaw.ai/tools/creating-skills>

## Model Notes

This skill is written for frontier-class models (Opus, Sonnet). If you're running a cheaper model and find a stage underspecified, expand it yourself — the design sequence is a scaffold, not a script. Cheaper models should:

- Read the pattern files in `{baseDir}/patterns/` more carefully before architecting
- Spend more time on Stage 2 (capability discovery) — enumerate OpenClaw features explicitly
- Be more methodical in Stage 4 (spec) — write out the full structure before implementing
- Consult <https://docs.openclaw.ai> when unsure about any OpenClaw feature

---

## The Design Sequence

### Stage 0: Inventory (Extraction Only)

Skip if building from scratch. Use when packaging existing functionality (scripts, TOOLS.md sections, conversation patterns, repeated instructions) into a skill.

Gather what exists, where it lives, what works, what's fragile. Then proceed to Stage 1.

### Stage 1: Problem Understanding

Work through with the user:

1. **What does this skill do?** (one sentence)
2. **When should it load?** Example phrases, mid-task triggers, scheduled triggers
3. **What does success look like?** Concrete outcomes per example

### Stage 2: Capability Discovery

#### Generalisability

Ask early: **Is this for your setup, or should it work on any OpenClaw instance?**

| Choice | Implications |
|--------|-------------|
| **Universal** | Generic paths, no local assumptions, ClawHub-ready |
| **Particular** | Can reference local skills, tools, workspace config |

#### Skill Synergy (Particular Only)

Scan `<available_skills>` from the system prompt for complementary capabilities. Read promising skills to understand composition opportunities.

#### OpenClaw Features

Review the docs with the skill's needs in mind. Think compositionally — OpenClaw's primitives combine in powerful ways. Key docs to check:

| Need | Doc |
|------|-----|
| Messages | `/concepts/messages` |
| Cron/scheduling | `/automation/cron-jobs` |
| Subagents | `/tools/subagents` |
| Browser | `/tools/browser` |
| Canvas UI | `/tools/` (canvas) |
| Node devices | `/nodes/` |
| Slash commands | `/tools/slash-commands` |

See `{baseDir}/patterns/composable-examples.md` for inspiration on combining these.

### Stage 3: Architecture

Based on Stages 1–2, identify which patterns apply:

| If the skill... | Pattern |
|-----------------|---------|
| Wraps a CLI tool | `{baseDir}/patterns/cli-wrapper.md` |
| Wraps a web API | `{baseDir}/patterns/api-wrapper.md` |
| Monitors and notifies | `{baseDir}/patterns/monitor.md` |

Load all that apply and synthesise. Most skills combine patterns.

**Script vs. instructions split:** Scripts handle deterministic mechanics (API calls, data gathering, file processing). SKILL.md instructions handle judgment (interpreting results, choosing approaches, composing output). The boundary is: could a less intelligent system do this reliably? If yes → script.

### Stage 4: Design Specification

Present proposed architecture for user review:

1. **Skill structure** — files and directories
2. **SKILL.md outline** — sections and key content
3. **Components** — scripts, modules, wrappers
4. **State** — stateless, session-stateful, or persistent (and where it lives)
5. **OpenClaw integration** — which features, how they interact
6. **Secrets** — env vars, keychain, config file (document in setup section, never hardcode)

**State locations:**
- `<workspace>/memory/` — user-facing context
- `{baseDir}/state.json` — skill-internal state (travels with skill)
- `<workspace>/state/<skill>.json` — skill state in common workspace area

If extracting: include migration notes (what moves, what workspace files need updating).

**Validate:** Does it handle all Stage 1 examples? Any contradictions? Edge cases?

Iterate until the user is satisfied. This is where design problems surface cheaply.

### Stage 5: Implementation

**Default: same-session.** Work through the spec with user review at each step. Reserve subagent handoff for complex script subcomponents only — SKILL.md and integration logic stay in the main session.

1. Create skill directory + SKILL.md skeleton (frontmatter + sections)
2. Scripts (if any) — get them working and tested
3. SKILL.md body — complete instructions
4. Test against Stage 1 examples

If extracting: update workspace files, clean up old locations, verify standalone operation.

---

## Crafting the Frontmatter

The frontmatter determines discoverability and gating. Format follows the [AgentSkills](https://agentskills.io) spec with OpenClaw extensions.

```yaml
---
name: my-skill
description: [description optimised for discovery — see below]
homepage: https://github.com/user/repo  # optional
metadata: {"openclaw":{"emoji":"🔧","requires":{"bins":["tool"],"env":["API_KEY"]},"primaryEnv":"API_KEY","install":[...]}}
---
```

**Critical:** `metadata` must be a **single-line** JSON object (parser limitation).

### Description — Write for Discovery

The description determines whether the skill gets loaded. Include:
- **Core capability** — what it does
- **Trigger keywords** — terms users would say
- **Contexts** — situations where it applies

Test: would the agent select this skill for each of your Stage 1 example phrases?

### Frontmatter Keys

| Key | Purpose |
|-----|---------|
| `name` | Skill identifier (required) |
| `description` | Discovery text (required) |
| `homepage` | URL for docs/repo |
| `user-invocable` | `true`/`false` — expose as slash command (default: true) |
| `disable-model-invocation` | `true`/`false` — exclude from model prompt (default: false) |
| `command-dispatch` | `tool` — bypass model, dispatch directly to a tool |
| `command-tool` | Tool name for direct dispatch |
| `command-arg-mode` | `raw` — forward raw args to tool |

### Metadata Gating

OpenClaw filters skills at load time using `metadata.openclaw`:

| Field | Effect |
|-------|--------|
| `always: true` | Skip all gates, always load |
| `emoji` | Display in macOS Skills UI |
| `os` | Platform filter (`darwin`, `linux`, `win32`) |
| `requires.bins` | All must exist on PATH |
| `requires.anyBins` | At least one must exist |
| `requires.env` | Env var must exist or be in config |
| `requires.config` | Config paths must be truthy |
| `primaryEnv` | Maps to `skills.entries.<name>.apiKey` |
| `install` | Installer specs for auto-setup (brew/node/go/uv/download) |

**Sandbox note:** `requires.bins` checks the **host** at load time. If sandboxed, the binary must also exist inside the container.

### Token Budget

Each eligible skill adds ~97 chars + name + description + location path to the system prompt. Keep descriptions informative but not bloated — every character costs tokens on every turn.

### Install Specs

```json
"install": [
  {"id": "brew", "kind": "brew", "formula": "tap/tool", "bins": ["tool"], "label": "Install via brew"},
  {"id": "npm", "kind": "node", "package": "tool", "bins": ["tool"]},
  {"id": "uv", "kind": "uv", "package": "tool", "bins": ["tool"]},
  {"id": "go", "kind": "go", "package": "github.com/user/tool@latest", "bins": ["tool"]},
  {"id": "dl", "kind": "download", "url": "https://...", "archive": "tar.gz"}
]
```

## Path Conventions

| Token | Meaning |
|-------|---------|
| `{baseDir}` | This skill's directory (OpenClaw resolves at runtime) |
| `<workspace>/` | Agent's workspace root |

- Use `{baseDir}` for skill-internal references (scripts, state, patterns)
- Use `<workspace>/` for workspace files (TOOLS.md, memory/, etc.)
- Never hardcode absolute paths — workspaces are portable
- For subagent scenarios, include path context in the task description (sandbox mounts differ)

## References

- Pattern files: `{baseDir}/patterns/` (cli-wrapper, api-wrapper, monitor, composable-examples)
- OpenClaw docs: <https://docs.openclaw.ai/tools/skills>
- ClawHub: <https://clawhub.com>
