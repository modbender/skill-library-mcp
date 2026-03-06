# Trigger Tests

## True Positives (should trigger)

| # | Input | Expected |
|---|-------|----------|
| 1 | "Ask deepwiki how session compaction works" | trigger |
| 2 | "How does the heartbeat system work in openclaw?" | trigger |
| 3 | "Look up the config schema in the codebase" | trigger |
| 4 | "Check the source code for tool policies" | trigger |
| 5 | "What's the repo architecture of facebook/react?" | trigger |
| 6 | "Use deepwiki to find out about compaction" | trigger |
| 7 | "openclaw source code question" | trigger |

## True Negatives (should NOT trigger)

| # | Input | Expected |
|---|-------|----------|
| 1 | "Search the web for React tutorials" | no trigger |
| 2 | "Read the file at src/main.ts" | no trigger |
| 3 | "Create a new GitHub repo" | no trigger |
| 4 | "What's the weather today?" | no trigger |
| 5 | "Help me write a Python script" | no trigger |
| 6 | "Clone this repository" | no trigger |
