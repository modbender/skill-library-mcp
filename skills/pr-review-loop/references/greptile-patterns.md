# Common Greptile Feedback Patterns

## Score Patterns
Greptile includes scores in review body. Look for:
- `Score: X/5`
- `Confidence: X/5`  
- `X/5` standalone
- Sometimes embedded in sentences like "I'd rate this a 3/5"

## Common Feedback Categories

### Security (fix immediately)
- SQL injection, XSS, auth bypass
- Hardcoded secrets/credentials
- Missing input validation

### Error Handling
- Unhandled promise rejections
- Missing try/catch blocks
- Silent error swallowing

### Type Safety
- Missing TypeScript types
- `any` usage where specific types needed
- Nullable fields not checked

### Code Quality
- Dead code / unused imports
- Duplicated logic
- Magic numbers without constants
- Missing comments on complex logic

### Performance
- N+1 queries
- Missing indexes
- Unnecessary re-renders
- Large bundle imports

### Architecture (ESCALATE to Master)
- Breaking API changes
- Database schema changes
- New dependencies that affect the stack
- Pattern changes (e.g., switching from REST to GraphQL)
- Changes to auth/permission model

## Fix Strategy

1. **Group by file** — batch fixes per file to minimize commits
2. **Address high-severity first** — security > errors > types > quality
3. **Don't over-fix** — only address what Greptile flagged, don't refactor unrelated code
4. **Descriptive commits** — list each fix in the commit message
5. **One commit per round** — squash fixes into a single commit per review round
