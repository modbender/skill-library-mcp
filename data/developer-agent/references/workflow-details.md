# Workflow Details

## Complete Decision Tree

```
Requirement Received
        ↓
    Understand? ──NO──→ Ask Questions ──┐
        ↓ YES                           │
    Git Setup                           │
        ↓                               │
    Simple Task? ──YES──→ Direct Code ─┤
        ↓ NO                            │
    Use Cursor Agent                    │
        ↓                               │
    Need Planning? ──NO──→ Implement ──┤
        ↓ YES                           │
    Select Planning Model               │
        ↓                               │
    Send Minimal Prompt to Cursor       │
    (Include links & attachments)       │
        ↓                               │
    Cursor Creates Plan                 │
        ↓                               │
    Present Cursor's Plan to User       │
        ↓                               │
    Wait for Approval ──REJECT────────→┘
        ↓ APPROVE
    Select Implementation Model
        ↓
    Send to Cursor with Plan
    (Include links & attachments)
        ↓
    Cursor Implements
        ↓
    Self Review ──FAIL──→ Re-implement
        ↓ PASS
    Run pnpm build ──FAIL──→ Fix & Rebuild
        ↓ SUCCESS
    Git Commit & Push
        ↓
    Merge to Staging
        ↓
    Wait Release Pipeline
        ↓
    Wait Build Pipeline
        ↓
    Wait Deploy Pipeline
        ↓
    Generate Final Report
        ↓
    ✅ COMPLETE
```

## Stage Details

### Cursor Prompt Template (Planning)

```
Create a detailed implementation plan for the following requirement:

[STATE THE REQUIREMENT CLEARLY AND CONCISELY]

Requirements Context:
[ONLY ESSENTIAL CONTEXT - 2-3 sentences max]

Attached Resources:
• [Link 1 provided by user]
• [Link 2 provided by user]
• [Attachment 1]
• [Attachment 2]

Please analyze the codebase and create a comprehensive plan with your best approach.
```

### Cursor Prompt Template (Implementation)

```
Implement the approved plan:

[INCLUDE THE APPROVED PLAN]

Attached Resources:
• [All links from user]
• [All attachments from user]

Requirements:
• Follow the approved plan
• Write clean, maintainable code
• Follow project coding standards
• Handle edge cases
• Ensure quality implementation
```
