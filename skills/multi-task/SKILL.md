---
name: multi-task
description: "Orchestrate parallel execution of batch tasks by splitting work into independent units and dispatching them to multiple subagents simultaneously. Use this skill whenever the user has multiple similar independent tasks — such as processing a batch of files (PDFs, DOCX, images, CSVs), developing multiple pages or components, generating multiple reports, or any scenario involving 'each', 'every', 'all', 'batch', or a list of similar items. Also trigger when the user provides a numbered list of tasks, references a folder of files to process, or describes repetitive work across multiple inputs. Even if the user doesn't explicitly say 'parallel' or 'batch', if the work naturally decomposes into 3+ independent units of similar type, use this skill to maximize throughput."
---

# Multi-Task: Parallel Batch Orchestration

## Overview

When users present tasks that decompose into multiple independent work units, serial execution wastes time. This skill guides you to identify batch opportunities, construct self-contained prompts for each unit, and dispatch them as parallel subagents via the Task tool — completing in minutes what would otherwise take much longer sequentially.

The core insight: a single message can contain multiple Task tool calls, and they all execute concurrently. Your job is to make each subagent's prompt fully self-contained (they cannot see this conversation) and to coordinate the results.

## When to Use This Skill

**Strong signals:**
- User says "process all files in X folder"
- User provides a list: "do A, B, C, D for each of these..."
- User mentions "batch", "bulk", "every", "each", "all N files"
- A folder contains multiple files needing the same operation
- User wants multiple pages/components/reports generated

**Also consider using when:**
- User describes repetitive work that you'd otherwise do in a loop
- The task involves 3+ independent units of similar type
- Processing time per unit is non-trivial (reading/transforming documents, generating code, etc.)

**Do NOT use when:**
- Tasks have strict sequential dependencies (output of task N feeds into task N+1)
- There are fewer than 3 work units (overhead isn't worth it)
- The task is a single complex operation that can't be decomposed
- User explicitly asks for serial processing

## The 6-Step Workflow

### Step 1: ANALYZE — Understand the Work

Before dispatching anything, enumerate what needs to be done:

1. **List all work units** — files to process, pages to build, items to transform
2. **Identify the operation** — what happens to each unit (extract, convert, summarize, generate, etc.)
3. **Check for shared context** — do all units need the same template, config, or reference data? If so, read it once now and include it in every subagent prompt.
4. **Detect dependencies** — are any units dependent on others? If yes, read `references/advanced-patterns.md` for dependency handling strategies. If all units are independent (the common case), proceed directly.
5. **Count the units** — this determines your dispatch strategy:
   - 3-10 units: single wave, all parallel
   - 11-50 units: dispatch in waves of 8-10
   - 50+ units: run 2-3 pilot tasks first to validate your prompt, then dispatch the rest in waves

Present your analysis to the user:
```
Found N work units: [brief list]
Operation: [what will happen to each]
Shared context: [any common dependencies]
Dependencies: [none / description]
Strategy: [single wave / M waves of ~K / pilot + waves]
```

Wait for user confirmation before dispatching, especially for large batches.

### Step 2: PLAN — Decompose into Task Units

For each work unit, define:

- **task-ID**: Sequential identifier (task-001, task-002, ...)
- **input**: Absolute path(s) to input file(s) or data
- **operation**: What the subagent should do
- **output**: Absolute path for results (ensure no path conflicts between tasks)
- **recommended skill**: If the task matches an installed skill (see Skill Matching below)

**Output path strategy:** Create a dedicated output directory to keep results organized:
```
<project-dir>/multi-task-output/
├── task-001/
├── task-002/
└── ...
```

Use `mkdir -p` to create the output directory structure before dispatching.

### Step 3: PROMPT — Construct Subagent Prompts

Each subagent starts with a blank context — it cannot see this conversation. Every prompt must be **completely self-contained**. Use this template:

```
## Task [task-ID]: [Brief description]

### Skill Recommendation
[If a matching skill is available]:
You have access to the `/[skill-name]` skill which is ideal for this task.
Invoke it using the Skill tool with skill="[skill-name]" to get specialized
instructions before proceeding.

### Context
[Any shared context the subagent needs — project background, conventions,
templates, reference data. Include the actual content, not references to
"the conversation above".]

### Input
- File: [absolute path]
- [Any other inputs, with absolute paths]

### Instructions
[Clear, step-by-step instructions for what to do]
1. [Step 1]
2. [Step 2]
...

### Output
- Save results to: [absolute path to task-specific output directory]
- Expected deliverables: [list of output files]
- [Any format requirements]

### Important Notes
- Use absolute paths for all file operations
- Do not modify the input file(s)
- If you encounter an error, save error details to [output-dir]/error.log
```

**Prompt quality checklist:**
- [ ] All paths are absolute
- [ ] No references to "the conversation" or "as discussed"
- [ ] Shared context is included verbatim, not by reference
- [ ] Output paths are unique per task (no conflicts)
- [ ] Instructions are specific enough for an agent with no prior context
- [ ] Skill recommendation is included if applicable

### Step 4: DISPATCH — Send Tasks in Parallel

**The critical mechanism:** Include multiple Task tool calls in a **single message**. This is what makes them parallel. If you send them in separate messages, they run serially.

**For 3-10 tasks:** Send all in one message:
```
[Single message containing:]
Task(subagent_type="general-purpose", prompt="## Task task-001: ...", description="Process file-001")
Task(subagent_type="general-purpose", prompt="## Task task-002: ...", description="Process file-002")
Task(subagent_type="general-purpose", prompt="## Task task-003: ...", description="Process file-003")
...
```

**For 11-50 tasks:** Dispatch in waves of 8-10. Wait for each wave to complete before starting the next:
```
Wave 1: task-001 through task-010 (single message, all parallel)
[Wait for completion, report progress]
Wave 2: task-011 through task-020 (single message, all parallel)
[Wait for completion, report progress]
...
```

**For 50+ tasks:** Run a pilot first:
1. Pick 2-3 representative tasks (include edge cases if possible)
2. Dispatch them as a pilot wave
3. Verify results are correct
4. If issues found, fix the prompt template and re-pilot
5. Once validated, dispatch the remaining tasks in waves of 8-10

**Subagent type selection:**
- Default: `general-purpose` (has access to all tools including Skill)
- For pure shell/git tasks: `Bash`
- For code exploration only: `Explore`

**Run tasks in background when appropriate:** For large batches, use `run_in_background: true` so you can monitor progress and report to the user incrementally.

### Step 5: MONITOR — Track Progress

As results come back:

1. **Track completion** — maintain a mental tally: "Wave 1: 8/10 complete"
2. **Check for failures** — if a task fails:
   - Analyze the error
   - Fix the prompt if needed
   - **Retry up to 2 times** automatically
   - If still failing after 2 retries, mark as failed and continue with others
3. **Report progress** to user after each wave:
   ```
   Wave 1 complete: 9/10 succeeded, 1 failed (task-007: [reason])
   Starting wave 2...
   ```
4. **Failure isolation** — one task's failure must never block or affect other tasks

### Step 6: MERGE — Collect and Present Results

After all waves complete:

1. **Sort results by task-ID** — present in order regardless of completion time
2. **Summarize outcomes:**
   ```
   Batch complete: N/M tasks succeeded

   Successful:
   - task-001: [output path] — [brief description]
   - task-002: [output path] — [brief description]
   ...

   Failed (if any):
   - task-007: [error reason] — [suggested fix]
   ```
3. **Handle failed tasks** — offer to retry failed tasks or let user fix input and rerun
4. **Merge outputs if requested** — some batch operations need a final merge step (e.g., combining extracted text into one document). Do this after all tasks complete.

## Skill Matching

When planning tasks, match each work unit against installed skills. This dramatically improves subagent performance because skills provide specialized, tested instructions.

**Matching rules:**

| Task involves... | Recommend skill |
|---|---|
| PDF files (read, create, merge, extract) | `/pdf` |
| Word documents (.docx read, create, edit) | `/docx` |
| PowerPoint files (.pptx) | `/pptx` |
| Spreadsheets (.xlsx, .csv, .tsv) | `/xlsx` |
| Web pages, components, HTML/CSS | `/frontend-design` |
| Visual design, posters, art | `/canvas-design` |
| Styling artifacts with themes | `/theme-factory` |

**How to include skill recommendations in prompts:**

In each subagent's prompt, add the skill invocation instruction:
```
### Skill Recommendation
You have access to the `/pdf` skill. Before starting work, invoke it using
the Skill tool: Skill(skill="pdf"). This will load specialized instructions
for PDF processing that will help you complete this task more effectively.
```

If no installed skill matches, omit the skill recommendation section — the subagent will use its general capabilities.

## Examples

### Example 1: Batch PDF Text Extraction

**User:** "Extract text from all PDFs in /Users/me/reports/ and save as markdown files"

**Analysis:**
```
Found 12 PDF files in /Users/me/reports/
Operation: Extract text from each PDF, save as .md
Shared context: None
Dependencies: None
Strategy: 2 waves of 6
```

**Subagent prompt (each task):**
```
## Task task-001: Extract text from Q1-report.pdf

### Skill Recommendation
You have access to the `/pdf` skill. Invoke it using the Skill tool with
skill="pdf" to get specialized PDF processing instructions.

### Input
- File: /Users/me/reports/Q1-report.pdf

### Instructions
1. Read the PDF file and extract all text content
2. Preserve heading structure where possible
3. Format the output as clean Markdown
4. Include page breaks as horizontal rules (---)

### Output
- Save to: /Users/me/reports/multi-task-output/task-001/Q1-report.md
- Create the output directory if it doesn't exist
```

### Example 2: Multi-Page Frontend Development

**User:** "Build 5 pages for our marketing site: Home, About, Pricing, Blog, Contact"

**Analysis:**
```
Found 5 work units: Home, About, Pricing, Blog, Contact pages
Operation: Generate frontend code for each page
Shared context: Brand guidelines, shared layout components, color scheme
Dependencies: None (each page is independent)
Strategy: Single wave, all 5 parallel
```

**Key considerations:**
- Read any existing shared components/styles first
- Include the full shared context (brand colors, fonts, layout patterns) in each prompt
- Each subagent gets `/frontend-design` skill recommendation
- Output to separate directories: `pages/home/`, `pages/about/`, etc.

### Example 3: Batch Data Conversion

**User:** "Convert all CSV files in /data/raw/ to JSON format with proper types"

**Analysis:**
```
Found 25 CSV files in /data/raw/
Operation: Parse CSV, infer types, convert to JSON
Shared context: Type inference rules (dates, numbers, booleans)
Dependencies: None
Strategy: 3 waves of ~8-9
```

**Key considerations:**
- Each subagent gets `/xlsx` skill recommendation (handles CSV)
- Include type inference rules in every prompt
- Standardize output format in the prompt template

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| Tasks run serially, not parallel | Task calls sent in separate messages | Put ALL Task calls in a single message |
| Subagent says "I don't have context" | Prompt references conversation history | Make prompt fully self-contained |
| File not found errors | Relative paths used | Use absolute paths everywhere |
| Output files overwrite each other | Same output path for multiple tasks | Use task-ID in output directory path |
| Subagent doesn't use recommended skill | Skill instruction unclear | Add explicit `Skill(skill="name")` call instruction |
| Too many tasks overwhelm the system | Dispatching 50+ at once | Use waves of 8-10 |
| Results arrive in wrong order | Relying on completion order | Sort by task-ID, not completion time |
| One failure cascades to others | Shared state between tasks | Ensure full isolation — separate dirs, no shared files |

## Advanced Patterns

For handling tasks with dependencies (linear chains, fan-in/fan-out, partial dependencies), dynamic batch sizing, and conditional dispatch, read `references/advanced-patterns.md`.
