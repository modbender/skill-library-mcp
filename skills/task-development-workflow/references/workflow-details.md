# Workflow Details

## Clarification Questions Examples

### Business Understanding
- What problem does this solve?
- Who are the target users?
- What are the success criteria?

### UI/UX Flow
- What screens/views are needed?
- What is the user journey?
- Are there mockups or wireframes?

### Architecture
- What tech stack?
- What databases/services?
- How does it integrate with existing systems?

### Technical Decisions
- Authentication method?
- API design (REST/GraphQL)?
- Deployment target?

## Task Breakdown Guidelines

**Good tasks:**
- Single responsibility
- Completable in 1-4 hours
- Has clear acceptance criteria
- Independently testable

**Bad tasks:**
- "Build the frontend" (too big)
- "Fix bugs" (too vague)
- "Refactor everything" (no clear end)

## TDD Cycle

```
Red → Green → Refactor
```

1. **Red**: Write a failing test
2. **Green**: Write minimal code to pass
3. **Refactor**: Clean up while tests pass

## PR Description Template

```markdown
## Summary
Brief description of changes

## Trello Task
[Task Name](trello-link)

## Changes
- Change 1
- Change 2

## Testing
- [ ] All tests pass
- [ ] Manual testing done

## Screenshots (if UI)
```

## Handling CR Feedback

1. Read all comments before responding
2. Address each comment explicitly
3. If disagreeing, explain reasoning
4. Push all fixes in one commit if possible
5. Re-request review when ready

## Edge Cases

### Blocked by another task?
- Note blocker in Trello card
- Move to "Backlog" or create dependency
- Pick different task

### PR has conflicts?
- Rebase on latest main
- Resolve conflicts
- Re-run tests
- Push force with lease

### Scope creep during implementation?
- Complete current task as scoped
- Create new card for additional work
- Discuss with stakeholder
