---
name: Active Learner
description: Implements the Active Learning Protocol (R3). Allows the agent to
  programmatically internalize lessons into MEMORY.md and generate structured
  "ask for help" requests.
---

# Active Learner

**Version:** 1.0.0
**Author:** OpenClaw Evolution (Cycle #2597)

## Description
Implements the Active Learning Protocol (R3). Allows the agent to programmatically internalize lessons into `MEMORY.md` and generate structured "ask for help" requests.

## Usage

### Internalize a Lesson
```bash
node skills/active-learner/index.js internalize --id "L1" --category "Protocol" --text "Lesson content here..."
```

### Ask for Help
```bash
node skills/active-learner/index.js ask --text "I don't understand X..."
```
