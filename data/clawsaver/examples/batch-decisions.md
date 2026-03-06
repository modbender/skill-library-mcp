# ClawSaver — Batch Decision Examples

## ✅ Batch These (Same Topic)

### Example 1: Code Review in Parts
User sends:
> "Can you review this function for bugs? Also check if it's performant. And are there any missing test cases?"

ClawSaver: **Batch → 1 structured response**
- Three asks, one function, shared context
- All answers benefit from the same code read

### Example 2: Research + Action
User sends:
> "What are the main causes of this error? What should I do to fix it? And should I update my deps?"

ClawSaver: **Batch → 1 structured response**
- Research informs the fix informs the dep decision
- Shared knowledge base = no repeated context

### Example 3: Config Questions
User sends:
> "What's the right timeout setting? What about max retries? And what does the `backoff` option do?"

ClawSaver: **Batch → 1 structured response**
- All about the same config file/system

---

## ❌ Don't Batch These

### Example 4: Sequential Dependency
User: "Write the function." → "Now write tests for it."

ClawSaver: **Keep separate**
- Test content depends on the function output
- Can't write tests without knowing the implementation

### Example 5: Unrelated Topics
User sends:
> "What's the weather in NYC? Also, can you refactor my Python script?"

ClawSaver: **Keep separate**
- No shared context
- Different tools, different outputs

### Example 6: User Preference
User says:
> "Answer each question one at a time please."

ClawSaver: **Defer to user**
- Never override explicit instructions

---

## 💡 Offer to Batch (Within-Session Pattern)

Turn 1: "What's the current status of my build?"
Turn 2: "What should I do next?"
Turn 3: "Are there any blockers?"

ClawSaver detects pattern at turn 2 or 3:
> "Looks like these are all about the same build — want me to address all three in one go?"

If yes: Batch. If no: Answer normally.

---

## Savings Footer Examples

Short:
```
💸 Batched 3 → 1
```

Detailed:
```
💸 Batched 3 asks → 1 response. Est. savings: ~2 API calls, ~800 tokens.
```

Silent (omit footer when):
- User is in flow and doesn't need reminders
- Only 2 items batched (minor, not worth calling out)
- Response is already long (footer would clutter)
