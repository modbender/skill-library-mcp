# Mediator Prompts Reference

These prompts are used by `summarize.py` to process messages.

## facts-only (default)

Extracts only actionable content. Best for high-conflict situations where you don't want any emotional content.

**Removes:** Anger, guilt, accusations, passive aggression, manipulation, blame, criticism, unnecessary history

**Extracts:** Specific requests, dates/times/deadlines, names/places/amounts, questions needing answers

## neutral

Rewrites the full message in professional tone. Preserves all information but removes emotional charge. Good for situations where you need the full context but can't deal with the tone.

## full

Shows everything but flags concerning patterns. Identifies manipulation tactics, distinguishes reasonable vs unreasonable asks, notes hidden implications. Best when you need to understand the full picture including the manipulation.

---

## Customizing Prompts

To customize prompts, edit `scripts/summarize.py` and modify the `PROMPTS` dictionary.

### Adding a new mode

```python
PROMPTS["custom-mode"] = """Your custom prompt here..."""
```

Then use with:
```bash
mediator.sh add "Contact" --summarize custom-mode
```

## Response Generation

All modes generate `suggested_response` fields. These are designed to be:
- Neutral and non-escalating
- Factual and direct
- Brief (no unnecessary words)
- Focused only on actionable items

Example transformations:

| Original | Response |
|----------|----------|
| "I can't BELIEVE you forgot AGAIN!!!" | (No response needed - no ask) |
| "Pick up kids at 3pm Saturday OR ELSE" | "Confirmed. I'll pick up the kids at 3pm Saturday." |
| "Why do you always do this to me? Can you at least send me the documents?" | "Sending the documents now." |
