# MVP Scope Management

## Feature Prioritization Matrix

| Priority | Definition | Rule | Example |
|----------|------------|------|---------|
| **Must** | MVP fails without it | Max 3 features | User can sign up |
| **Should** | Important for UX | Only if time allows | Password reset |
| **Could** | Nice to have | v2 | Dark mode |
| **Won't** | Explicitly out | Document and park | Mobile app |

**The 3-Feature Rule:** If you can't ship with 3 "Must" features, your scope is too broad or your hypothesis is too complex.

---

## Tradeoff Template

When scope is challenged, use this script:

```
Request: "Can we add [FEATURE]?"

Response options:
A) "Yes, if we cut [OTHER FEATURE]"
B) "Yes, if we slip launch by [X WEEKS]"
C) "We can add it to v2 backlog and revisit after launch data"

Which do you prefer?
```

Never accept additions without explicit tradeoffs.

---

## Decision Log Template

| Date | Request | Decision | Rationale | Decided By |
|------|---------|----------|-----------|------------|
| | | In/Out/v2 | Why | Name |

Keep this visible. Update it live. Point people to it when they re-ask.

---

## Common Scope Traps by Role

### Technical Founders
- "Auth needs to support SSO" (No, email/password is fine)
- "We need an admin panel" (No, use database directly)
- "Should be mobile-responsive" (Maybe, or just desktop first)

### Product Managers
- "Users expect onboarding" (No, 10 beta users can figure it out)
- "We need analytics" (No, talk to users directly at this scale)
- "Should integrate with X" (No, manual export is fine for MVP)

### Non-Technical Founders
- "Competitor has this feature" (Irrelevant, different hypothesis)
- "Investors want to see X" (Build for users, not investors)
- "It won't feel complete without Y" (Complete ≠ viable)

### Solo Builders
- "I should add one more thing before launch" (No, ship now)
- "The UI isn't polished enough" (Users don't care at MVP)
- "What if it can't scale?" (It can't. That's fine.)

---

## Scope Document Template

```
# [Product] MVP Scope

## Hypothesis
We believe [user] will [action] because [reason].

## Success Criteria
- Primary: [specific metric + threshold]
- Secondary: [specific metric + threshold]

## In Scope (Must)
1. [Feature 1]
2. [Feature 2]
3. [Feature 3]

## Out of Scope (v2)
- [Feature A] — why it can wait
- [Feature B] — why it can wait

## Ship Date
[DATE] — non-negotiable

## Signed Off By
- [Name, Role]
- [Name, Role]
```
