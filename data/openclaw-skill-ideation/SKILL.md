---
name: ideation
description: Transform raw brain dumps (dictated freestyle) into structured implementation artifacts. Use when user has messy ideas, scattered thoughts, or dictated stream-of-consciousness, or when they want to plan a feature, spec something out, or turn rough ideas into actionable specs. Produces contracts and implementation specs written to ./docs/ideation/{project-name}/.
---

# Ideation

Transform unstructured brain dumps into structured, actionable implementation artifacts through a confidence-gated workflow.

## Workflow Pipeline

```
INTAKE → CODEBASE EXPLORATION → CONTRACT FORMATION → PHASING → SPEC GENERATION → HANDOFF
              ↓                        ↓                  ↓            ↓               ↓
         Understand              confidence < 95%?    PRDs or     Repeatable?    Analyze deps
         existing code                ↓               straight      ↓               ↓
                                 ASK QUESTIONS        to specs?   Template +    Sequential?
                                      ↓                           per-phase     Parallel?
                                 (loop until ≥95%)                deltas        
```

## Phase 1: Intake

Accept whatever the user provides:

- Scattered thoughts and half-formed ideas
- Voice dictation transcripts (messy, stream-of-consciousness)
- Bullet points mixed with rambling
- Topic jumping and tangents
- Contradictions and unclear statements
- Technical jargon mixed with vague descriptions

**Don't require organization. The mess is the input.**

Acknowledge receipt and begin analysis. Do not ask for clarification yet.

## Phase 2: Codebase Exploration

**Before scoring confidence or generating any artifacts, understand the existing codebase.** This is critical — specs written without understanding existing patterns, architecture, and conventions will be generic and wrong.

### When to Explore

Exploration is needed when:
- The brain dump references existing code, features, or systems
- The project directory contains source code (not a greenfield project)
- The user mentions extending, modifying, or integrating with existing functionality

Skip exploration for greenfield projects with no existing code.

### What to Explore

Use file reading and search to understand:

1. **Project structure** — What frameworks, languages, and patterns are in use?
2. **Relevant existing code** — What modules/files relate to the brain dump's scope?
3. **Conventions and patterns** — How are similar features implemented? What abstractions exist?
4. **Testing patterns** — How is the codebase tested? What infrastructure exists?
5. **Configuration and build** — What tools, package managers, and CI/CD are in use?

**Do not write exploration findings to files.** They're context for the ideation process, not an artifact.

## Phase 3: Contract Formation

### 3.1 Analyze the Brain Dump

Extract from the raw input + codebase exploration:

1. **Problem signals**: What pain point or need is being described?
2. **Goal signals**: What does the user want to achieve?
3. **Success signals**: How will they know it worked?
4. **Scope signals**: What's included? What's explicitly excluded?
5. **Contradictions**: Note any conflicting statements
6. **Codebase constraints**: What does the existing architecture enable or limit?

### 3.2 Calculate Confidence Score

Score each dimension (0-20 points):

| Dimension        | Question                                                       |
| ---------------- | -------------------------------------------------------------- |
| Problem Clarity  | Do I understand what problem we're solving and why it matters? |
| Goal Definition  | Are the goals specific and measurable?                         |
| Success Criteria | Can I write tests or validation steps for "done"?              |
| Scope Boundaries | Do I know what's in and out of scope?                          |
| Consistency      | Are there contradictions I need resolved?                      |

**Total: /100 points**

See `references/confidence-rubric.md` for detailed scoring criteria.

### 3.3 Confidence Thresholds

| Score | Action                                                    |
| ----- | --------------------------------------------------------- |
| < 70  | Major gaps. Ask 5+ questions targeting lowest dimensions. |
| 70-84 | Moderate gaps. Ask 3-5 targeted questions.                |
| 85-94 | Minor gaps. Ask 1-2 specific questions.                   |
| ≥ 95  | Ready to generate contract.                               |

### 3.4 Ask Clarifying Questions

When confidence < 95%, ask clarifying questions:

**Question strategy**:
- Target the lowest-scoring dimension first
- Be specific, not open-ended
- Offer options when possible ("Is it A, B, or C?")
- Reference what was stated ("You mentioned X, did you mean...?")
- Limit to 3-5 questions per round
- After each round, recalculate confidence

### 3.5 Generate Contract

When confidence ≥ 95%:

1. Confirm project name with user
2. Convert to kebab-case for directory name
3. Create output directory: `./docs/ideation/{project-name}/`
4. Write `contract.md` using `references/contract-template.md`
5. Get explicit approval before proceeding

**Do not proceed until contract is explicitly approved.**

## Phase 4: Phasing & Specification

### 4.1 Choose Workflow

Ask the user:
- **Straight to specs** — Recommended for technical projects. Faster.
- **PRDs then specs** — Recommended for large scope or cross-functional teams.

### 4.2 Determine Phases

**Small-project shortcut:** If the scope is small enough to implement in a single phase (1-3 components, touches fewer than ~10 files), skip phasing entirely. Generate a single `spec.md`.

**Phasing criteria** (for multi-phase projects):
- Dependencies (what must be built first?)
- Risk (tackle high-risk items early)
- Value delivery (can users benefit after each phase?)
- Complexity (balance phases for consistent effort)

### 4.3 Generate PRDs (if chosen)

For each phase, generate `prd-phase-{n}.md` using `references/prd-template.md`.

### 4.4 Generate Implementation Specs

Generate specs using `references/spec-template.md`:

- Technical approach
- File changes (new and modified)
- Implementation details with code patterns
- Testing requirements
- Error handling
- Validation commands
- Per-component feedback loops

**Reference existing code:** Include "Pattern to follow: `path/to/similar/file.ts`" when relevant patterns exist.

### 4.5 Present for Review

Before presenting specs, evaluate feedback loop quality. Present all specs for user approval.

## Phase 5: Execution Handoff

Present the execution strategy:

```
Ideation complete. Artifacts written to `./docs/ideation/{project-name}/`.

## To start implementation

Start a fresh session and work through the specs in order:
1. Read the contract for context
2. Read spec-phase-1.md  
3. Implement following the spec
4. Validate using the commands in the spec
5. Commit and move to next phase
```

## Output Artifacts

All artifacts written to `./docs/ideation/{project-name}/`:

```
contract.md                        # Problem, goals, success, scope
prd-phase-1.md                     # Phase 1 requirements (only if PRDs chosen)
spec-phase-1.md                    # Phase 1 implementation spec
spec-template-{pattern}.md         # Shared template for repeatable phases (if applicable)
spec-phase-{n}.md                  # Per-phase specs
```

## Important Notes

- **Explore the codebase** before scoring confidence (unless greenfield).
- **Score confidence conservatively.** When uncertain, score lower.
- Never skip the confidence check. Don't assume understanding.
- Always write artifacts to files. Don't just display them.
- Each phase should be independently valuable.
- Specs should be detailed enough to implement without re-reading PRDs or the contract.
- Keep contracts lean. Heavy docs slow iteration.
- **Reference existing code patterns** in specs.
- **Small projects don't need phases.** If scope is 1-3 components, generate a single spec.
