# Card Creation & Formats

## Atomic Card Principle

Every card = ONE fact. Test yourself:
- Can this card have only ONE correct answer?
- If I see only the question, is the answer unambiguous?
- Am I testing recall or recognition?

**Bad:** "What are the symptoms of X?" (list → should be separate cards)
**Good:** "X causes [symptom]. What disease?" (single fact)

## Card Formats

### Basic (Q&A)
Best for: concepts, explanations, processes

```
Front: What enzyme converts angiotensin I to angiotensin II?
Back: ACE (Angiotensin-Converting Enzyme)
```

**Traps:**
- "What is X?" without context — fails when multiple X exist
- Answer on front visible — no "The answer is ACE" on back

### Cloze Deletion
Best for: fill-in-the-blank facts, definitions, sequences

```
{{c1::ACE}} converts angiotensin I to {{c2::angiotensin II}}
```

**Traps:**
- Multiple clozes testing DIFFERENT facts — should be separate cards
- Cloze too long — "{{c1::The mitochondria is the powerhouse of the cell}}" useless
- Cloze too short — "{{c1::A}}CE" doesn't test understanding

**Good cloze targets:**
- Key terms in definitions
- Numbers, dates, quantities
- Names in processes
- One element in a small set

### Image Occlusion
Best for: anatomy, diagrams, maps, visual structures

**Traps:**
- Occluding too much — can't identify structure without context
- Not occluding enough — answer visible from surrounding labels
- Low-resolution images — frustrating to study

### Reversed Cards
Create both directions ONLY when both are meaningful:
- ✅ Spanish→English AND English→Spanish (vocabulary)
- ✅ Term→Definition AND Definition→Term (if term is recallable)
- ❌ "Capital of France?" + "Paris is the capital of?" (second is useless)

## Context and Cues

**Every card needs:**
- Domain indicator (deck name, tag, or in text)
- Enough context to distinguish from similar facts
- Source reference (optional but useful for review)

**Bad:** "What does ACE stand for?" (which ACE?)
**Good:** "[Cardiology] What does ACE stand for in the context of blood pressure regulation?"

## Mnemonics

Add only when:
- Fact is arbitrary (not deducible from logic)
- Mnemonic is shorter than the fact
- It genuinely helps recall

**Don't force mnemonics on everything.** Most facts are better learned through understanding and repetition.

## Batch Card Generation

When generating multiple cards from source material:

1. **Extract facts** — Read material, identify testable facts
2. **Dedupe** — Check for overlaps with existing cards
3. **Format** — Choose appropriate format per fact
4. **Tag** — Assign consistent tags
5. **Review** — Quick pass for ambiguity

Output format for Anki import (tab-separated):
```
Front	Back	Tags
What enzyme...	ACE	physiology cardiology
```

## Common Card Diseases

| Problem | Symptom | Fix |
|---------|---------|-----|
| Too complex | Always fail, can't recall all parts | Split into multiple cards |
| Too vague | Multiple answers seem right | Add specificity/context |
| Too easy | Always pass, no effort | Delete or combine with harder concept |
| Pattern matching | Pass based on wording, not knowledge | Rephrase, add variations |
| Orphan fact | Passes alone, fails in context | Add related cards, build network |
