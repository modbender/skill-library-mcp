---
name: researching-in-parallel
description: Research any topic thoroughly by running three sub-agents with distinct analytical lenses (breadth, critique, evidence), then giving their outputs to a final sub-agent to produce/update one review report with a unified bibliography. Supports iterative research — outputs from one run can be fed back as starting-point sources for the next. Use when the user wants a deep, comprehensive, or multi-perspective synthesis of a topic. Not for quick factual lookups or conversational questions.
compatibility: Requires sessions_spawn (OpenClaw default config sufficient — maxSpawnDepth 1). Requires web search, file read/write access to workspace for sub-agents. Browser and PDF tools strongly recommended — without them sub-agents are limited to search snippets. IMPORTANT - This skill MUST be installed within the agent's workspace (e.g. /workspace/skills/) so that  sub-agents can access its internal assets and prompt templates. 
metadata:
  author: openclaw-skills
  version: 1.4
---

# Researching in Parallel

## When to use this skill

Trigger when the user asks to:
- Research a topic deeply or comprehensively
- Get a multi-perspective or balanced overview of a subject
- Produce a research report, briefing, or synthesis
- "Run deep research on…" or "use your research skill on…"

Do **not** trigger for quick factual questions, casual conversation, or anything
answerable from memory in a few sentences. This skill takes significant elapsed time and  and
incurs meaningful token cost.

---

## Steps

### 1. Clarify the brief

Confirm with the user:

- **Topic** — narrow if too broad (e.g. "AI" → "LLM use in clinical diagnosis, current evidence base")
- **Angle** — e.g. strategic overview / technical deep-dive / current developments / comparative / orientation
- **Output length:**
  - *Brief* (minimum 1000 words in report body)
  - *Standard* (minimum 3000 words in report body): full structured report
  - *Comprehensive* (minimum 5000 words, no maximum): cover all threads the research surfaces
- **Provided sources** — has the user supplied starting-point files (uploaded, workspace paths, or URLs)? Collect all paths/URLs now.
- **Blank sheet or Update** — does the user want a new report, or an expansion / deepening of one already created? 
- **Source extracts** — should sub-agents save a cleaned extract of each cited source to the workspace? Adds storage and modest token overhead; no additional retrieval cost. Recommended for serious runs — extracts form a verifiable evidence base and can be reused as provided sources on the next run. Default: no for exploratory runs, yes for serious ones. Update `save_source_extracts` in skill-config.json accordingly.
- **Workspace location** — where outputs and artifacts will be stored. All files for this run go inside this directory. Use this path as WORKSPACE_PATH throughout. This must be a new empty directory. 

You may complete all preparatory work (reading config, checking the workspace, identifying provided sources) without waiting for confirmation. The confirmation gate below covers the spawn decision only.

### 2. Assemble provided sources file (if applicable)

If the user has provided starting-point sources, write a `sources-provided-[TOPIC_SLUG]-[DATE].md` file **inside the workspace location** (`[WORKSPACE_PATH]/sources-provided-[TOPIC_SLUG]-[DATE].md`) before spawning. This file is part of the reproducible research record. 

Format:
```markdown
# Provided Sources: [TOPIC]
*Assembled [DATE] for research run [TOPIC_SLUG]-[DATE]*

[Full path or URL to each source, one per line, with a brief note on what it is]
```

If no sources were provided, skip this step. Sub-agents will check for this file — if absent they proceed with open research only.

### 2a. Identify if the user wants an existing report to be updated

If so, make a copy of the existing report in the workspace location, and copy the `sources-provided-*` file associated with that report.

### 3. Assemble sub-agent configuration and prompts, seek confirmation, then spawn

**Read skill-config.json now.** Note the prompt_template and model assigned to each role. 

*Initial agents*
| Label | Role | Config |
|---|---|---|
| `research-breadth` | Breadth sweep | `subagents.breadth` |
| `research-critical` | Critical lens |  `subagents.critical` |
| `research-evidence` | Evidence pass |  `subagents.evidence` |

*Final agent* (one only)
If the user wants an existing report to be updated, use the Updater sub-agent. For a new report, use Synthesis.
| Label | Role | Config |
|---|---|---|
| `review-report` | Synthesis |  `subagents.synthesis` |
| `review-report-updated` | Updater | `subagents.updater` |

You must make it clear to the user which models will be used for each agent, and alert the user to homogeneity. If any `model` parameter is null in `skil-config.json`, attempt to identify which models are available and ask the user to select one.

**Assemble each sub-agent's task prompt** by combining the files specified. 

1. Open the appropriate role prompt_template files specified. 
2. At each `{{INSERT: shared-blocks.md > Block: [name]}}` marker, paste the corresponding block from `shared-blocks.md` verbatim
3. Substitute all `{{PLACEHOLDERS}}` with values from skill-config.json and the confirmed brief
4. At `{{INJECT_CONTEXT}}`, insert any run-specific instructions relevant to this role (e.g. gaps identified in a prior run, specific angles to prioritise). Delete the section if you have nothing to add.
5. If the user has specified a previous report to be updated, in the updater prompt, additionally substitute `{{REPORT_TO_EDIT_PATH}}` 
6. Ensure that any files mentioned in the sub-agent prompts are accessible. If necessary, copy them into the `[WORKSPACE_PATH]` to ensure the sub-agent can find them. 
7. You must create one prompt file for each sub-agent, containing only the instructions for that agent. Write each prompt to the  `[WORKSPACE_PATH]`.

**Before spawning sub-agents:** Present the following to the user and wait for explicit confirmation before proceeding to Step 3a:
- Topic and angle as interpreted
- Output length
- Whether creating a new or updating an existing report
- Workspace path
- Models assigned to each role (from skill-config.json)
- Any provided sources identified
- Any run-specific instructions you plan to pass to sub-agents via {{INJECT_CONTEXT}}

The user may override any of these. If the user asks for changes, redo whatever is needed to comply, then ask again for explicit confirmation to proceed. Sub-agents are resource-intensive and costly - do not spawn sub-agents until the user confirms.

### 3a. Spawn the breadth, critical and evidence sub-agents

Get the parameters defined in `skill-config.json`: `subagents.params`

Call `sessions_spawn` for the sub-agents. For `task`, use the prompt file you created for that agent. Respect the `subagents.maxConcurrent` parameter. 

When a sub-agent terminates for any reason, check for the existence of its expected outputs at the file path(s) specified. Do not proceed to Step 4 with missing outputs — investigate and resolve first.

### 4. Compile the unified bibliography

Consolidate all SOURCES sections from the three research outputs into `bibliography-[TOPIC_SLUG]-[DATE].md` inside the workspace. Deduplicate across passes. Flag single-pass-only sources. Add the BibTeX block.

Follow the structure in `assets/bibliography-template.md` exactly. The template includes:
- Primary / Secondary / Unverified source tables with Access and AI-generated columns
- A BibTeX export block at the end

Populate all columns. Do not omit the Access or AI-generated columns — these were present in the sub-agent SOURCES sections.

### 5. Spawn the final sub-agent.

Spawn a dedicated synthesis or updater sub-agent. Call `sessions_spawn` to spawn the sub-agent. For `task`, use the prompt file you created for the agent.

If the sub-agent fails to deliver in full or times out, investigate and resolve. Do not change the model without explaining the issue to the user and getting approval. 

### 6. Deliver

When the final sub-agent completes and has delivered a report file, announce completion in chat. Confirm all workspace artifacts are saved and give the user the file paths. Remind the user that the current outputs and bibliography can serve as provided sources for another research run.

---

For sub-agent task prompts, see `references/prompts/` (one file per role plus `shared-blocks.md`).  
For output templates, see `assets/report-template.md` and `assets/bibliography-template.md`.  
For model assignments, see `skill-config.json`.  
For configuration and cost guidance, see `references/configuration.md`.
