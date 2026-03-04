# TUI Interaction Patterns — Real-World Examples

Complete walkthroughs of driving interactive CLI tools with `clrun`.

## Example: create-vue (Vue.js scaffolder)

```bash
# 1. Start the scaffolder
clrun "npx create-vue@latest"
# Response includes terminal_id, output shows "Project name:" prompt

# 2. Enter project name (text input)
clrun <id> "my-vue-app"
# → Advances to feature multi-select

# 3. Select features: TypeScript, Router, Pinia, Linter
#    Layout:
#    ◻ TypeScript     ← space (select)
#    ◻ JSX            ← down (skip)
#    ◻ Router         ← down, space (select)
#    ◻ Pinia          ← down, space (select)
#    ◻ Vitest         ← down (skip)
#    ◻ E2E Testing    ← down (skip)
#    ◻ Linter         ← down, space (select)
#    ◻ Prettier       ← down (skip)
#                     ← down, enter (confirm)
clrun key <id> space down down space down space down down down space down down enter

# 4. Skip experimental features (select none)
clrun key <id> enter

# 5. Keep example code (accept default "No")
clrun key <id> enter

# 6. Install dependencies and start dev server
clrun <id> "cd my-vue-app && npm install"
# Wait for install to finish...
clrun tail <id> --lines 10
clrun <id> "npm run dev"
# → Vite dev server running
```

## Example: create-vite (React + TypeScript)

```bash
# 1. Start scaffolder
clrun "npx create-vite@latest"

# 2. Project name (text input)
clrun <id> "my-react-app"

# 3. Framework select list:
#    ● Vanilla       ← 0 downs
#    ○ Vue           ← 1 down
#    ○ React         ← 2 downs
clrun key <id> down down enter

# 4. Variant (accept default: TypeScript)
clrun key <id> enter

# 5. Install confirm (accept default: Yes)
clrun key <id> enter
# → Project scaffolded, deps installed, dev server started
```

## Example: npm init (readline prompts)

```bash
clrun "npm init"

# package name:
clrun <id> "my-package"

# version: (1.0.0)
clrun <id> ""                    # Accept default

# description:
clrun <id> "A cool project"

# entry point: (index.js)
clrun <id> ""                    # Accept default

# test command:
clrun <id> "vitest run"

# git repository:
clrun <id> ""                    # Accept default

# keywords:
clrun <id> "cli,agent,terminal"

# author:
clrun <id> "myname"

# license: (ISC)
clrun <id> "MIT"

# Is this OK? (yes)
clrun <id> "yes"
```

## Example: Long-running dev server

```bash
# Start and monitor
clrun "npm run dev"
clrun tail <id> --lines 20
# → Look for "ready" or URL in output

# Session stays alive — dev server keeps running
# Check on it anytime:
clrun tail <id> --lines 5

# Stop when done:
clrun kill <id>
```

## Example: Interrupting a stuck process

```bash
# Process is hung or you need to cancel:
clrun key <id> ctrl-c

# Check if it stopped:
clrun tail <id> --lines 10

# If still running, force kill:
clrun kill <id>
```

## Example: Environment variable persistence

```bash
# Start a session
clrun "bash"

# Set variables
clrun <id> "export API_KEY=sk-12345"
clrun <id> "export NODE_ENV=development"

# Use them later in the same session
clrun <id> 'echo $API_KEY'
# → Output: sk-12345

# Variables survive suspension too:
# After 5 min idle, session suspends automatically
# Next input auto-restores with all env vars intact
clrun <id> 'echo $NODE_ENV'
# → Output: development
```

## Pattern: Priority queuing for multi-step input

When a command will ask multiple questions, pre-queue answers with priority:

```bash
clrun "npm init"

# Queue all answers at once — higher priority sent first
clrun input <id> "my-package" --priority 10
clrun input <id> "" --priority 9           # version default
clrun input <id> "Description" --priority 8
clrun input <id> "" --priority 7           # entry point default
clrun input <id> "" --priority 6           # test command
clrun input <id> "" --priority 5           # repo
clrun input <id> "" --priority 4           # keywords
clrun input <id> "" --priority 3           # author
clrun input <id> "MIT" --priority 2
clrun input <id> "yes" --priority 1
```

## Pattern: Override for recovery

When you sent the wrong input or need to change course:

```bash
# Cancel all pending inputs and send new one immediately
clrun input <id> "n" --override

# Or interrupt the process entirely
clrun key <id> ctrl-c
```
