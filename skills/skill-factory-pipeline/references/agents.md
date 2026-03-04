# Agents Reference

Each stage of the skill-factory pipeline runs as a dedicated agent. All agents are called as isolated top-level CLI calls — never from within a nested session.

## Invocation pattern

```bash
openclaw agent --agent <id> -m "<prompt>"
```

The prompt is constructed by `pipeline.sh` and injected at invocation time. No interactive input. No session state carried between agents. All communication goes through the filesystem (workspace files).

---

## Stage 1 — market

**Agent ID:** `market`
**Model guidance:** High-reasoning model preferred (needs judgment on market signals)
**Input:** `idea.md`
**Output:** `market.md`

**Task:** Validate the skill idea against real market demand. Research the competitive landscape, identify the target audience, and deliver a GO / NO-GO verdict.

**Key behaviors:**
- Searches for existing tools, skills, or libraries that solve the same problem
- Identifies primary and secondary user personas
- Estimates demand based on tool usage, forum activity, search patterns
- Produces a structured market.md with a clear verdict at the end

**Failure modes:**
- market.md not written → gate fails, pipeline stops
- Verdict omitted → docs stage will lack context for positioning
- Overly optimistic analysis → pricer overestimates value

---

## Stage 2 — planner

**Agent ID:** `planner`
**Model guidance:** High-reasoning model preferred (product decisions require judgment)
**Input:** `idea.md`, `market.md`
**Output:** `plan.md`

**Task:** Translate the idea and market research into a concrete product plan. Defines scope, capabilities, trigger scenarios, and the exact list of files to build.

**Key behaviors:**
- Names the skill in hyphen-case (max 32 chars)
- Writes the one-sentence description that will go into SKILL.md frontmatter
- Lists trigger scenarios precisely (what user messages activate this skill)
- Specifies which resource directories are needed (scripts/, references/, assets/)
- Lists every file the skill will contain

**Failure modes:**
- plan.md not written → gate fails, pipeline stops
- Vague trigger scenarios → skill fires incorrectly or not at all
- Missing file list → builder makes arbitrary decisions

---

## Stage 3 — arch

**Agent ID:** `arch`
**Model guidance:** High-reasoning model preferred (architecture decisions have downstream impact)
**Input:** `plan.md`
**Output:** `arch.md`

**Task:** Design the internal architecture of the skill. Produces a detailed blueprint that the builder follows exactly.

**Key behaviors:**
- Draws the full directory tree
- Outlines the SKILL.md sections
- Describes each script: name, language, inputs, outputs, core logic
- Describes each reference file: content summary and when an agent would load it
- Documents the data flow and integration pattern

**Failure modes:**
- arch.md not written → gate fails, pipeline stops
- Directory tree missing → builder creates arbitrary structure
- Script descriptions too vague → builder produces generic stubs

---

## Stage 4 — builder

**Agent ID:** `builder`
**Model guidance:** Any capable coding model; cost-effective models work for mechanical file creation
**Input:** `arch.md`, `plan.md`
**Output:** `skill/` directory with all files

**Task:** Implement the skill. Creates every file listed in the architecture. No placeholders, no TODOs — production-ready content.

**Key behaviors:**
- Creates `skill/SKILL.md` with valid frontmatter (name, description)
- Creates all scripts with correct shebangs, usage docs, real logic
- Creates all reference files with comprehensive content
- Follows the directory structure exactly as specified in arch.md

**Gate check:** `skill/SKILL.md` must exist and be non-empty

**Failure modes:**
- skill/SKILL.md missing → gate fails, pipeline stops
- Placeholder content in scripts → auditor will flag as FAIL
- Divergence from arch.md → inconsistency with plan

---

## Stage 5 — auditor

**Agent ID:** `auditor`
**Model guidance:** High-reasoning model preferred (quality judgment requires thoroughness)
**Input:** `skill/` (all files)
**Output:** `audit.md`

**Task:** Perform a structured quality audit of the built skill. Each audit item gets PASS / WARN / FAIL status. Concludes with OVERALL: PASS or FAIL.

**Audit checklist:**
1. SKILL.md completeness and frontmatter validity
2. Trigger accuracy (correct activation conditions)
3. Script quality (shebang, error handling, real logic)
4. Reference quality (comprehensive, no placeholder content)
5. Internal consistency across all files
6. Security review (no injection risks, no hardcoded secrets)
7. Gap analysis (missing capabilities)

**Failure modes:**
- audit.md not written → gate fails, pipeline stops
- OVERALL: FAIL → docs stage is blocked (by design)
- Missing security review → undetected vulnerabilities in scripts

---

## Stage 6 — docs

**Agent ID:** `docs`
**Model guidance:** Any capable writing model
**Input:** `skill/`, `audit.md`
**Output:** `docs_review.md`

**Task:** Review documentation quality and provide specific rewrites for unclear passages. Blocked by a failed audit.

**Key behaviors:**
- Checks if audit OVERALL is FAIL → writes blocking message to docs_review.md
- Evaluates clarity, examples, decision guidance, edge cases, cross-references
- Quotes original text and provides improved rewrites (not just "this is unclear")

**Failure modes:**
- docs_review.md not written → gate fails, pipeline stops
- Vague feedback without rewrites → developer has nothing actionable

---

## Stage 7 — pricer

**Agent ID:** `pricer`
**Model guidance:** Any capable model; benefits from business reasoning
**Input:** `market.md`, `plan.md`, `audit.md`, `skill/SKILL.md`
**Output:** `pricing.md`

**Task:** Determine the pricing, positioning, and marketplace strategy for the skill.

**Key behaviors:**
- Assigns a quality tier (Starter / Standard / Pro) based on audit results and complexity
- Recommends a specific USD price with written rationale
- Writes a one-paragraph positioning statement for the marketplace listing
- Lists 3-5 key selling points as bullet points
- Suggests tags and categories for discovery
- Recommends launch strategy (free trial / bundle / direct)

**Failure modes:**
- pricing.md not written → gate fails, pipeline stops
- Price without rationale → owner cannot adjust or negotiate
- Missing positioning statement → listing lacks copy
