# Negative Space — Common Void Patterns by Task Type

Quick-reference patterns for each void, organized by the type of task the agent is performing.

---

## Code Modification Tasks

### Unstated Assumptions
- Which branch am I on? Is it the right one?
- Are there uncommitted changes I'd overwrite?
- Is this function called from other places I haven't seen?
- Does this variable name exist elsewhere with a different meaning?

### Missing Constraints
- What's the test coverage expectation?
- Are there type definitions or interfaces that need updating?
- Does the project have a linter config that enforces specific patterns?
- Is there a CHANGELOG or migration guide that needs an entry?

### Absent Context
- Why was the code written this way? (Check git blame before "fixing" it)
- Was this a deliberate trade-off or an accident?
- Is there a related issue, PR, or discussion that provides background?

### Invisible Failure Modes
- What happens at the boundaries? (empty input, null, max values)
- Does this change break the API contract for callers?
- If I rename this, what breaks downstream?
- Does this change behave differently in different environments?

---

## Search & Discovery Tasks

### Unstated Assumptions
- Am I searching for the right term? (Could be abbreviated, aliased, or in a different language/convention)
- Am I looking in the right directory? (Monorepos may have multiple roots)

### Missing Constraints
- Should I search all files or only source files? (Ignoring build artifacts, node_modules, vendor)
- Is the user looking for the definition or the usage?

### Absent Context
- Has the user already searched and failed? What terms did they try?
- Is there a project-specific naming convention I should know about?

### Invisible Failure Modes
- The term might not exist yet (the user wants to CREATE it, not find it)
- The code might be generated/compiled and not in the source tree
- Case sensitivity could cause misses

---

## Command Execution Tasks

### Unstated Assumptions
- Is the expected runtime/tool installed?
- Am I in the correct working directory?
- Are environment variables set that this command depends on?

### Missing Constraints
- Does this project use a specific package manager? (npm vs yarn vs pnpm vs bun)
- Are there project-specific scripts that wrap standard commands?
- Does the project expect a specific Node/Python/Ruby version?

### Absent Context
- Has this command been run before in this session? What was the output?
- Is there a Makefile, Taskfile, or justfile that defines project commands?
- Are there required setup steps (database migrations, env file creation) that must come first?

### Invisible Failure Modes
- The command might modify global state (installing globally, changing system configs)
- The command might have interactive prompts that block execution
- The command might take very long and appear "stuck" when it's actually working
- The command might succeed silently while actually doing nothing (wrong directory, no matching files)

---

## File Creation Tasks

### Unstated Assumptions
- Where should this file go? (Assuming directory structure)
- What should it be named? (Assuming naming convention)
- What format/extension? (Assuming file type)

### Missing Constraints
- Is there a template or boilerplate for this type of file?
- Does the project have a specific directory structure convention?
- Should this file be registered somewhere (index, config, manifest)?

### Absent Context
- Does a similar file already exist that should be modified instead?
- Are there adjacent files that establish a pattern I should follow?

### Invisible Failure Modes
- Creating a file that already exists (overwriting)
- Creating a file in the wrong directory (won't be discovered by the build system)
- Creating a file without updating imports/exports/registrations (orphaned file)

---

## Debugging Tasks

### Unstated Assumptions
- Is the bug reproducible? Under what conditions?
- Am I looking at the right layer? (Frontend bug might be a backend issue, or vice versa)
- Is this a code bug or a configuration/environment issue?

### Missing Constraints
- What's the expected behavior vs. actual behavior?
- Which version/environment exhibits the bug?
- Is there a minimal reproduction case?

### Absent Context
- When did this start happening? (What changed recently?)
- Does it happen for all users or specific ones?
- Is there relevant log output, error messages, or stack traces?

### Invisible Failure Modes
- Fixing the symptom instead of the cause
- Fixing it in one place while it persists in another code path
- The "fix" introduces a regression in an unrelated feature
- The bug is actually a feature that someone depends on

---

## Refactoring Tasks

### Unstated Assumptions
- The user wants the behavior to stay the same (or do they want it to change?)
- The tests cover the current behavior (or are there gaps?)
- The refactoring scope is limited to what the user mentioned

### Missing Constraints
- Are there performance requirements that the refactored code must still meet?
- Are there backwards-compatibility requirements? (Public API, saved data formats)
- Is this code used by external consumers (libraries, APIs)?

### Absent Context
- Why wasn't it written this way originally? (There might be a reason)
- Are there pending PRs that touch the same code? (Merge conflict risk)
- Is there tribal knowledge about why certain patterns are used?

### Invisible Failure Modes
- Breaking subtle behavior that isn't tested
- Changing performance characteristics (O(n) to O(n^2) accidentally)
- Moving code that has side effects (initialization order, global state)
- The refactored version is "cleaner" but harder to debug
