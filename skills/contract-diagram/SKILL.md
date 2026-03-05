---
name: contract-diagram
description: "Diagram as contract for agreed-upon AI development"
type: public
version: 1.0.0
status: stable
dependencies: []
author: nonlinear

license: MIT
---

| Legend | Description |
|--------|-------------|
| ![default](https://img.shields.io/badge/default-lightgray) | Not discussed yet |
| ![approved](https://img.shields.io/badge/approved-yellow) | Agreed by stakeholders |
| ![blocker](https://img.shields.io/badge/blocker-red) | Needs discussion/failed implementation (always has notes) |
| ![developed](https://img.shields.io/badge/developed-lightgreen) | Agreed and implemented |
| ![notes](https://img.shields.io/badge/notes-blue) | Implemented but developer made decisions (in notes) |
| ![outside](https://img.shields.io/badge/outside-lightgreen) | (dashed border) To be performed outside system |

---














## SKILL contract diagram ![Ready%20to%20check](https://img.shields.io/badge/Ready%20to%20check-lightgray) [ℹ️](https://github.com/nonlinear/skills/tree/main/contract-diagram/SKILL.md)

```mermaid
%%{init: {'theme':'base','themeVariables':{"primaryColor":"#4A90E2","primaryTextColor":"#fff","primaryBorderColor":"#2E5C8A","lineColor":"#666","secondaryColor":"#50E3C2","tertiaryColor":"#FFD700","edgeLabelBackground":"#666"},'flowchart':{"nodeSpacing":50,"rankSpacing":50,"padding":15,"curve":"basis"}}}%%
flowchart TD
    TRIGGER["Trigger + contract"]
    CHECK_CONTRACT{"Has contract?"}
    OPEN["Open contract"]
    CLARIFY["Clarify"]
    CHECK_DIAGRAM{"Has diagram?"}
    CREATE["New 1️⃣"]
    CLAIM["Claimed 1️⃣"]
    ERROR["Error 2️⃣"]
    
    DESIGN["Design phase"]
    SIGNOFF["Ready to approve"]
    DEVELOPMENT["Developing..."]
    BLOCKERS{"Has blockers?"}
    TESTS{"Pass checks? 3️⃣"}
    PUBLISH["Publish 3️⃣"]
    
    TRIGGER --> CHECK_CONTRACT
    CHECK_CONTRACT -->|Yes| OPEN
    CHECK_CONTRACT -->|Yes but<br/>not editable| ERROR
    CHECK_CONTRACT -->|No| CLARIFY
    CLARIFY --> TRIGGER
    
    OPEN --> CHECK_DIAGRAM
    CHECK_DIAGRAM -->|Yes, more<br/>than one| ERROR
    CHECK_DIAGRAM -->|Yes, one| CLAIM
    CHECK_DIAGRAM -->|No| CREATE
    
    CREATE --> DESIGN
    CLAIM --> DESIGN
    DESIGN --> SIGNOFF
    SIGNOFF -->|Approved| DEVELOPMENT
    DEVELOPMENT --> BLOCKERS
    BLOCKERS -->|Yes| DESIGN
    BLOCKERS -->|No| TESTS
    TESTS -->|Yes| PUBLISH
    TESTS -->|No| DESIGN
    
    classDef default fill:#e0e0e0,stroke:#666,color:#000
    classDef approved fill:#FFF9C4,stroke:#F9A825,color:#000
    classDef developed fill:#D5F5D5,stroke:#388E3C,color:#000
    classDef blocker fill:#FFCDD2,stroke:#D32F2F,color:#000
    classDef notes fill:#E3F2FD,stroke:#1976D2,color:#000
    classDef outside fill:#D5F5D5,stroke:#388E3C,stroke-dasharray:5 5,color:#000
    
    class CHECK_DIAGRAM,CREATE,CLAIM,ERROR,SIGNOFF,DESIGN,DEVELOPMENT,BLOCKERS,CHECK_CONTRACT,OPEN,CLARIFY,TRIGGER developed
    class PUBLISH,TESTS outside
```

**1️⃣** Wrapper auto-injects title + phase badge + CSS on first load and watches for change of phase on badge.

**2️⃣** More than one diagram confuses system. For now, only one per md in order to run.

**3️⃣** Checks and publication depend on what and where final product goes, so it's user discretion.

---





## Numbered Notes (1️⃣ 2️⃣ 3️⃣)

**When to use:**

**Pre-execution (design phase):**
- Questions that need discussion
- Trade-offs that need decisions
- Unclear requirements

**During execution:**
- Errors AI can't resolve alone
- Permission needed (destructive action, cost implications)
- Ambiguity in implementation

**Format:**

```markdown
### 1️⃣ [Component Name] - [Issue Title]
**Question/Error:** ...
**Context:** ...
**Options:** A, B, C
**Needed:** Decision / Permission / Help
```

**Notes without numbers = just explanations, turn yellow when approved.**

---

## Localhost Trigger

**Trigger:** "lets diagram [PATH]"

**Assumes:** File at PATH already has mermaid diagram.

**Action:**
1. Start localhost server (port 8080)
2. Open browser with diagram

**Example:**
```
User: "lets diagram epic-notes/webhook-contract.md"

AI executes:
  cd ~/Documents/skills/contract-diagram/engine
  ./serve.sh &
  open "http://localhost:8080/?md=../../epic-notes/webhook-contract.md"
```

**Hot reload enabled by default** (2s interval).

---

