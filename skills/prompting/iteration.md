# Prompt Iteration Workflow

## 1. Understand the Failure
Before changing anything:
- What EXACTLY went wrong?
- Is it reproducible or random?
- Which part of the prompt might cause it?

## 2. Single Variable Change
Change ONE thing:
- Move a constraint
- Add one example
- Rephrase one instruction

Never change multiple things. You won't know what fixed it.

## 3. Test Against Original Failure
Run the same input that failed. Did it pass?
- Yes → test 5 more inputs (regression check)
- No → revert, try different fix

## 4. Regression Testing
After any fix, re-test:
- Original failing case
- 3-5 known working cases
- 2 edge cases

New fixes often break old behavior.

## 5. Document the Change
In `~/prompting/history.md`:
```
[date] task: [description]
- Problem: [what failed]
- Fix: [what changed]
- Result: [working/partial/failed]
```

## 6. Compression Pass
After prompt works:
- Remove one line at a time
- Test after each removal
- Stop when removal breaks behavior

Minimal prompt = cheaper + often better.

## A/B Testing Setup
When comparing prompts:
1. Same test set for both
2. Blind evaluation if possible
3. Score specific criteria, not "overall"
4. 10+ examples minimum
5. Track: accuracy, format compliance, latency, cost
