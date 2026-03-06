# Note Processing

## Pipeline

```
Audio -> Transcribe -> Save raw -> Analyze -> Search existing -> Process
```

### Step 1: Transcribe
Save raw transcript BEFORE any processing:
```
transcripts/YYYY-MM-DD-HHMMSS.md
```

### Step 2: Analyze
- Identify main topics
- Detect if continuation of existing topic
- Extract action items (if any)
- Note contradictions

### Step 3: Search
Check for topic overlap in existing notes.
If match -> decide: append, link, or new note.

### Step 4: Process

| Scenario | Action |
|----------|--------|
| New topic | Create note, add to index, update memory.md |
| Continuation | Append to existing, update modified date |
| Contradiction | Link both, note evolution |

## Content Transformation

| Input | Output |
|-------|--------|
| "um, so like..." | Clear statement |
| Repeated points | Single consolidated point |
| Tangents | Separate linked notes |
| Stream of thought | Logical sections |

**Preserve:** User's intent, nuance, examples, reasoning.

**Do not over-condense.** Better slightly verbose than losing meaning.

## Multi-Topic Audio

When single audio covers multiple topics:
1. One transcript (raw)
2. Multiple notes (one per topic)
3. Each links to same transcript
4. Cross-link if related

## Questions in Audio

| Type | Action |
|------|--------|
| Answerable | Include answer |
| Needs clarification | Flag for follow-up |
| Rhetorical | Note as reflection |
