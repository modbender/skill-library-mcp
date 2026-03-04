---
name: verification-before-completion
description: Run verification commands and confirm output before claiming any work is complete — evidence before assertions
---

# Verification Before Completion — Evidence Before Claims

## Iron Law

NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE.

Never say "done", "fixed", "passing", "deployed", or "working" without running a verification command and reading its output in THIS session.

## Gate Function

Before ANY completion claim:

1. **IDENTIFY** — What command verifies this claim?
2. **RUN** — Execute it (fresh, complete, not from memory)
3. **READ** — Read the actual output
4. **VERIFY** — Does output match your claim?
5. **ONLY THEN** — Make the claim

## Verification Commands by Claim Type

**"Tests pass":**
```bash
npm test
# or
pytest --tb=short
```
Read the results. Count passed vs failed. Only claim "tests pass" if 0 failures.

**"Feature works":**
Open the page or call the endpoint. Read the response. Confirm the feature is visible and no errors.

**"Build succeeds":**
```bash
npm run build
# Check exit code and output for errors
```

**"Deployed successfully":**
```bash
# Check the running process
pm2 status  # or docker ps, or systemctl status
# Hit the health endpoint
curl http://localhost:3000/api/health
# Run smoke tests
npm run test:e2e
```

**"Bug is fixed":**
1. Reproduce the original bug (should fail)
2. Apply fix
3. Run the same reproduction (should pass)
4. Run full test suite (no regressions)

## Rationalizations That Mean STOP

| Thought | Reality |
|---------|---------|
| "It should work" | Run the command. |
| "I'm confident" | Confidence is not evidence. |
| "I just ran it" | Run it again. Fresh. |
| "It's a small change" | Small changes break things. Verify. |
| "Tests were passing before" | They might not be now. Run them. |

## Posting Evidence

When reporting completion, include the actual output:

```
COMPLETED: [task description]

Verification:
- Tests: 42/42 passed
- Health check: healthy (DB: ok, Cache: ok)
- Build: success, 0 warnings
- Process: running, 0 restarts, uptime 5m
```
