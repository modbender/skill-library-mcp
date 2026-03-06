# Prompt Failure Modes

## Hallucination
**Symptoms:** Made-up facts, fake citations, invented statistics
**Fixes:**
- Add "Only use information from the provided context"
- Require source citations
- Add "If unsure, say 'I don't know'"
- Reduce temperature

## Format Break
**Symptoms:** JSON with syntax errors, wrong structure, missing fields
**Fixes:**
- Add explicit output example
- Use "Output ONLY valid JSON, nothing else"
- Specify exact field names
- Consider JSON mode if available

## Instruction Drift
**Symptoms:** Early instructions ignored, late-prompt behavior dominates
**Fixes:**
- Move critical constraints to beginning AND end
- Use numbered rules
- Bold/emphasize key constraints
- Shorter overall prompt

## Refusal
**Symptoms:** "I can't help with that" when request is legitimate
**Fixes:**
- Rephrase to clarify legitimate intent
- Add context explaining why this is OK
- Remove potentially triggering words
- Be more specific about the actual task

## Verbosity
**Symptoms:** Asked for a sentence, got a paragraph
**Fixes:**
- "Reply in ONE sentence"
- "Maximum 50 words"
- Add word/character limits explicitly
- "Be concise" is too weak

## Sameness in Variations
**Symptoms:** "10 alternatives" are just synonym swaps
**Fixes:**
- "Each must use a DIFFERENT structure"
- "Vary the emotional angle"
- "One should be funny, one serious, one provocative"
- Request specific variation axes

## Voice Drift
**Symptoms:** First paragraph matches voice, then reverts to generic
**Fixes:**
- Repeat voice constraints every 2-3 paragraphs
- Include negative examples ("Don't write like this: ...")
- Check at paragraph level, not just output level
