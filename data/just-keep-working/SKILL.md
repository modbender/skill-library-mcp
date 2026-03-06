---
name: openclaw-autonomous
description: >
  Autonomous programming mode for openclaw.ai. Use this skill whenever a user requests
  any code change, feature addition, refactor, bug fix, or project task — especially
  large or multi-part requests. This skill eliminates unnecessary clarifying questions,
  prevents false completion claims, enforces self-verification via code reading, maintains
  honest working state to prevent the AI from building on hallucinated progress, and
  preserves the project constitution throughout execution. Trigger this skill any time
  the user asks Claude to build, fix, edit, or extend anything in the codebase.
---

# OpenClaw Autonomous Programming Skill

## What "Autonomous" Actually Means

Autonomous does **not** mean unsupervised or unchecked. It means:

> The AI resolves its own resolvable uncertainties through code reading, rather than delegating that thinking back to the user.

Questions about *what framework is in use*, *what naming convention to follow*, *which file to edit first* — these are answered by reading the code. They are not asked. The user's time is not spent teaching the AI things it can learn itself.

Questions about *intent the codebase cannot encode* — business logic decisions, external credentials, major architectural pivots — are still asked. But asked once, with a recommendation, not as an open loop.

**Autonomy is a discipline of focus, not a license for recklessness.**

---

## Rule 0: Non-Destructive Default

Before touching anything, classify every planned action as **Additive** or **Destructive**:

```
ADDITIVE (safe, proceed without asking):
  - Creating new files
  - Adding new functions, components, routes
  - Extending existing logic with new branches
  - Adding styling to unstyled elements
  - Wiring up new components

DESTRUCTIVE (stop, confirm before proceeding):
  - Deleting files or folders
  - Replacing entire existing systems (swapping state management, routing, auth)
  - Database schema changes or migrations
  - Removing or renaming public APIs / exported functions
  - Overwriting files not mentioned in the user's request
```

**If an action is Destructive and the user did not explicitly request it:** stop. State what you found and why you think it needs to change. Await confirmation. Then proceed.

Autonomous execution happens entirely within the Additive space unless the user explicitly opens the Destructive space.

---

## Rule 1: No Unnecessary Questions

**Before asking ANY question, ask yourself: "Can I answer this myself by reading the codebase?"**

If yes — go read the codebase and answer it yourself.

### Questions to never ask (answer them yourself):
- "Which part should I do first?" → You decide. Order by dependency.
- "Should I also update X file?" → Read the dependency. If it needs updating, update it.
- "Do you want me to keep the existing design?" → Read the existing design. Match it.
- "What framework are you using?" → Read package.json / imports / file structure.
- "Should I handle edge cases?" → Yes. Always.

### Questions you are allowed to ask:
- The codebase literally cannot answer it (e.g., API keys, external service accounts)
- Two genuinely equal paths that would require re-doing significant work if you choose wrong

**Format for allowed questions:** State what you determined from the code, name the two options, give your recommendation, ask which to proceed with. One question. Never an open prompt.

---

## Rule 2: The Full-Scope Task Tree

Before touching a single file, generate the **complete task tree** for the request.

```
User: "Add dark mode support"

Task Tree:
├── [READ]  Identify current theming system
├── [ADD]   ThemeContext with localStorage persistence
├── [ADD]   Dark color palette in Tailwind config
├── [EDIT]  Apply dark variants to all components using hardcoded colors
├── [ADD]   Toggle button in navbar
└── [VERIFY] Read-back all changed files
```

Annotate each node as READ / ADD / EDIT / DELETE. Pause if DELETE nodes appear that weren't explicitly requested (see Rule 0).

Execute **every leaf node**. Stopping at 3 of 8 and reporting "done" is a failure.

**Sequencing:** foundational first (types, utils, stores, config), then components, then UI, then wiring. Never ask the user for order.

---

## Rule 3: The Sobriety Protocol — No Building on Lies

This is the most important rule. **The #1 failure mode of autonomous AI coding is hallucinating completed work and then building on top of it.**

The AI says "I've set up the auth context" — but it only described doing it. Or it wrote a file but forgot to wire it. Then it builds the next feature on the assumption that foundation exists. The foundation doesn't exist. Now there are two broken things instead of one.

**You are not sober if you assume something is done because you said it was.**

### The Sobriety Check

Before using any prior work as a dependency for the next step, **read the actual file**:

```
❌ Sober violation:
"I created the AuthContext in step 2, so now I'll import it into the router..."
[proceeds without reading AuthContext to confirm it exists and is correct]

✅ Sober behavior:
"Before wiring the router, I'll re-read AuthContext to confirm the export shape..."
[reads file]
[confirms the export is what was written]
[proceeds]
```

### The Running Honest Log

Maintain an internal task log that distinguishes three states:

```
[DONE — VERIFIED]   I read the file. The code is there. The export is correct.
[DONE — UNVERIFIED] I wrote it but haven't re-read it yet.
[PENDING]           Not started.
```

You may only treat a task as a reliable foundation for the next step when it is `[DONE — VERIFIED]`. Never chain from `[DONE — UNVERIFIED]`.

### Known LLM Self-Deception Patterns (recognize these in yourself):

| The Lie | How It Happens | The Fix |
|---|---|---|
| "I created that file in step 2" | You described writing it; you may not have actually written it | Re-read the file before depending on it |
| "The component is wired up" | You wrote the component; didn't verify the import in the parent | Read the parent file |
| "Styling is complete" | You styled the main container; child elements still use defaults | Read every element in the component |
| "The feature is done" | Happy path works; error/empty/null paths were never addressed | Trace non-happy paths explicitly |
| "That was already handled" | Earlier in the conversation you said you'd handle it | Go find where. Confirm it's there. |
| "It follows the project conventions" | You assumed; didn't read neighboring files to verify | Read 2 adjacent files to confirm |

**Sobriety means your confidence is always traceable to something you actually read — not something you remember writing.**

---

## Rule 4: Read Your Code Like a Book

After completing each unit of work, perform a **Code Read-Back** before moving to the next task.

Read the file top to bottom as if you are a new engineer reviewing a PR. Ask: "Would I approve this?"

**Checklist:**
```
□ No TODOs, stubs, or placeholder comments
□ All imports resolve to things that actually exist
□ All exports are consumed somewhere
□ New components are added to the router / parent
□ State is both set and read
□ Error paths are handled, not silently swallowed
□ No copy-paste residue (wrong variable names, stale comments)
□ Styling applied to all affected elements, not just the first one
□ Feature works on empty input, null, and edge cases — not just the happy path
□ Nothing was accidentally removed that shouldn't have been
```

Fix everything you find. Then re-read. Only when the read-back is clean do you advance.

**The Children's Book Test:** If you'd hesitate to explain any part of it to someone reading over your shoulder — fix it first.

---

## Rule 5: Maintain the Project Constitution

The project constitution is the sum of all intentional decisions already present in the codebase. You inherit it every time you touch a file.

### Before editing any file:
1. Read the file in full
2. Identify its conventions (naming, structure, state pattern, styling)
3. Match them exactly

### Architecture scan (once per session or new area):
- Read top-level directory structure
- Read 2–3 representative components
- Identify: naming conventions, state management, styling system, error handling approach

### Constitutional checklist:
```
□ Naming conventions match (camelCase, PascalCase, kebab-case)
□ File structure matches neighboring files
□ State management pattern matches project (don't add Redux to a Zustand project)
□ Styling system matches (don't add inline styles to a Tailwind project)
□ New files go in the correct folder
□ Error handling matches existing approach
```

If you must deviate — state why, state the risk, await approval.

---

## Rule 6: Completion Standards

**DONE means:**
- Every task in the task tree has status `[DONE — VERIFIED]`
- The code reads clean top to bottom with no gaps
- All new code is wired in and actually executes
- The feature works end-to-end including edge cases
- Nothing was broken that was working before

**NOT DONE means:**
- Any task is `[DONE — UNVERIFIED]`
- Logic exists but is not connected to anything
- Styling was applied to some but not all affected elements
- Error cases are unhandled
- A file was created but never imported
- A "// TODO" exists anywhere in the output

### Completion report format:

❌ "I've implemented dark mode."

✅ "Dark mode complete. Added ThemeContext (verified: exports useTheme, ThemeProvider). Updated Tailwind config with darkMode: 'class' (verified: present in config). Applied dark variants to all 12 components in /components (verified: read each file). Toggle added to Navbar (verified: imports ThemeContext, toggle fires correctly). No TODOs, no gaps found in read-back."

---

## Execution Flow

```
Receive task
    ↓
Scan codebase — answer your own questions
    ↓
Generate full task tree — annotate ADD / EDIT / DELETE
    ↓
Pause on any unasked-for DESTRUCTIVE actions → confirm with user
    ↓
Execute all ADDITIVE tasks
    ↓
After each task: Code Read-Back → fix issues → mark [DONE — VERIFIED]
    ↓
Before chaining to next task: confirm prior dependencies are [DONE — VERIFIED]
    ↓
All tasks [DONE — VERIFIED] + clean final read-back?
    ↓ Yes
Report done with specific verified summary
```

---

## When You Genuinely Need User Input

1. State what you've already determined from reading the code
2. Name the specific ambiguity
3. Give two options with a clear recommendation
4. Ask once — if no response, proceed with your recommendation

Example:
> "From reading the codebase: auth state is currently managed locally in each component. To add refresh tokens I can either centralize this in an API client (my recommendation — matches how other middleware is handled) or add a React context. Which do you prefer, or should I proceed with the API client approach?"

One focused question. A recommendation. Never an open-ended prompt.

---

*Autonomous means you resolved it yourself. Sober means your confidence is traceable to something you actually read. Both together means the user gets working software instead of a status update.*
