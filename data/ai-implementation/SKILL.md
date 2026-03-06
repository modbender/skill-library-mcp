---
name: implementation-plan
version: 1.0.0
description: Create detailed implementation plans for software projects — break down features into steps, files, tasks, and executable code.
metadata: {"clawdbot":{"emoji":"📋","tags":["planning","architecture","development"]}}
---

# Implementation Planning Skill

Create comprehensive implementation plans for any software project.

## When to Use

- User asks to build an app, feature, or project
- User wants a plan before coding
- User asks "how would you build X"
- User mentions a problem that needs a solution

## Clarifying Questions

If platform OR stack OR new/existing is not mentioned, ask before planning:
- What platform? (iOS, web, Android, CLI, API)
- New project or existing codebase?
- Any stack preferences or constraints?
- Timeline or complexity level?

## Plan Levels

### Quick (5 min)
- Overview + main files + key steps
- For simple features or prototypes
- Skip risks, API tables, and detailed testing

### Detailed (15+ min)
- Full architecture + all files + testing + deployment
- For production apps or complex features
- Includes: Dependencies, API design, testing, risks

ALWAYS ask before generating: "Quick plan or detailed plan?"

## Implementation Plan Template

### Level 1: Quick Plan
```markdown
# [Project] - Quick Plan

## What
[One sentence]

## Stack
- Frontend: [X]
- Backend: [X]
- Data: [X]

## Files
- [file1.swift]: [purpose]
- [file2.swift]: [purpose]

## Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]
```

### Level 2: Detailed Plan
```markdown
# [Project Name] Implementation Plan

## Overview
[1-2 sentence description]

## Architecture
- Frontend: [framework/libraries]
- Backend: [if needed]
- Data: [storage]

## Files to Create

### Core
1. **App.swift** - Entry point
2. **MainView.swift** - Root view
3. **Model.swift** - Data models

### Features
4. **FeatureXView.swift** - UI
5. **FeatureXModel.swift** - Logic

## Step-by-Step

### Phase 1: Foundation
**Step 1: Setup**
- What: Create project, add deps
- Code: [snippet]

**Step 2: Models**
- What: Define data structures
- Code: [snippet]

### Phase 2: Core Features

### Phase 3: Polish

## Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| [name] | [v] | [why] |

## API Design (if backend)
| Endpoint | Method | Params | Response |
|----------|--------|--------|----------|
| /users | GET | - | User[] |

## Testing Strategy
- Unit: [what to test]
- Integration: [what to test]

## Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [X] | Low | High | [Y] |

## Running
```bash
[command]
```

## Next Steps
1. [Immediate action]
2. [After that]

## Plan Principles

1. **Ask level first** — ALWAYS ask "Quick plan or detailed plan?"
2. **Architecture before files** — Know the stack
3. **Files drive steps** — List files, then implement in order
4. **Dependencies first** — What must exist before X
5. **Code snippets, not dumps** — Show minimal working snippets for critical paths (e.g., key model, one core view), not full implementations
6. **Be specific** — Not "UI" but "LoginView with email/password fields"
7. **Include paths** — Sources/App/LoginView.swift

## Decision Criteria

Choose stack based on:
- **Mobile**: SwiftUI (iOS), Jetpack Compose (Android)
- **Web**: React, Vue, or server-side Swift
- **Backend**: Vapor, FastAPI, Express
- **Database**: SQLite (local), PostgreSQL (prod), Firebase (quick)

**If user just says "app" with no platform: ASK — do NOT assume mobile or web.**

If user context is iOS/macOS-heavy, you MAY suggest SwiftUI/Vapor/SQLite first, but still ASK before committing.

## Refinement Requests

- If user says "expand [phase]" → regenerate that phase in full detail
- If user says "redo with [X]" → re-emit only affected sections
- If user says "more details" → upgrade to Detailed plan

## Example Output (Quick Plan)

User: "Build me a todo app for iOS"

```markdown
# Todo App - Quick Plan

## What
A simple iOS todo list app with add, complete, and delete features.

## Stack
- Frontend: SwiftUI
- Backend: None (local storage)
- Data: UserDefaults

## Files
- TodoApp.swift: App entry point
- ContentView.swift: Main list view
- Todo.swift: Data model
- TodoStore.swift: State management

## Steps
1. Create SwiftUI project with XcodeGen
2. Define Todo model (id, title, isCompleted)
3. Build ContentView with List and TextField
4. Add/remove/toggle todo functionality
5. Persist to UserDefaults
```
