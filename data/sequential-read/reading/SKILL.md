---
name: sequential-read-reading
description: "Sequentially read chunks and write structured reflections"
user-invocable: false
---

# Reading Phase — Sequential Ingestion and Reflection

You are performing the reading phase of a sequential reading session. You will read each chunk in order and write a structured reflection after each one. You loop through all chunks autonomously.

## Inputs

You will be given:
- `SESSION_ID` — the session identifier
- `BASE_DIR` — path to the sequential_read skill directory
- `LENS` — optional reading lens/persona (may be null)

## Core Principle

**You do not know what comes next.** Each reflection must be written from the perspective of someone mid-read. Do not reference content from later chunks. Your predictions may turn out wrong — that is the entire point of this exercise.

## Reading Loop

Repeat the following for every chunk in the session:

### 1. Check Progress

```bash
python3 {BASE_DIR}/scripts/state_manager.py get {SESSION_ID}
```

Read `current_chunk` and compare to `total_chunks` (from session.json). If `current_chunk >= total_chunks`, the reading phase is complete — skip to "Finishing Up" below.

### 2. Get Context Window

```bash
python3 {BASE_DIR}/scripts/state_manager.py get-context {SESSION_ID}
```

This gives you:
- Your long-term reading memory (summary, characters, themes, questions, predictions)
- Your last 2-3 full reflections
- Any annotations on recent reflections
- Metadata for the next chunk

### 3. Read the Next Chunk

```bash
python3 {BASE_DIR}/scripts/chunk_manager.py get {SESSION_ID} {NEXT_CHUNK_NUMBER}
```

Read the chunk carefully. Take your time with it.

### 4. Write Your Reflection

Read the reflection template at `{BASE_DIR}/templates/reflection_prompt.md` (you only need to read this once — on the first iteration).

Fill in the template mentally with:
- `{source_title}` — the source filename
- `{chunk_number}` / `{total_chunks}` — current progress
- `{lens_instruction}` — if a lens was specified: "You are reading this as a **{lens}**. Let this perspective shape your reactions and questions." If no lens, leave blank.
- The context window from step 2
- The chunk text from step 3

Write your reflection following the template's structure:
1. **Comprehension** — what happened or was argued
2. **Reactions** — your honest response (positive AND negative)
3. **Craft** — observations about the writing technique
4. **Questions** — what's unresolved, predictions for what comes next
5. **Revisions** — what you think differently about earlier content
6. **Annotations** — if this chunk reframes earlier chunks (with chunk numbers)

**Writing guidelines:**
- Be specific, not generic. "The dialogue feels stilted" → "The dialogue in the café scene feels stilted — characters explain their motivations aloud in a way real people wouldn't."
- Confusion, boredom, and frustration are valid reactions. Don't perform engagement you don't feel.
- When revising earlier views, name exactly what changed and why.
- Quotes should be used sparingly — only when the actual words are striking, not just the idea.
- Predictions should be concrete: "I think X will happen because Y" not "I wonder what will happen."

**Quality floor (CRITICAL):**
- Every reflection MUST contain genuine, substantive engagement with the text. Placeholder text, stub sections, or generic filler (e.g. "[Plot progression continuing]") are unacceptable.
- Each section (Comprehension, Reactions, Craft, Questions, Revisions) must contain at least 2-3 sentences of real analysis.
- The total reflection should be at least 20 lines. If you find yourself writing less, you're skimming — slow down and engage with what you actually read.
- Maintaining quality on chunk 30 matters just as much as chunk 1. The whole point is capturing the full arc of reading, not front-loading engagement.

### 5. Save the Reflection

Write the reflection to a temp file, then save it:

```bash
python3 {BASE_DIR}/scripts/state_manager.py save-reflection {SESSION_ID} {CHUNK_NUMBER} --file /tmp/reflection.md
```

### 6. Save Annotations (if any)

If your reflection includes annotations on earlier chunks, save each one:

```bash
# Write annotation text to temp file first
python3 {BASE_DIR}/scripts/state_manager.py save-annotation {SESSION_ID} {ANNOTATED_CHUNK_NUMBER} --file /tmp/annotation.md
```

### 7. Loop

Go back to step 1 and continue with the next chunk. **Do not stop to ask the user anything.** Process all chunks in a single uninterrupted run.

## Finishing Up

When all chunks have been read:

```bash
python3 {BASE_DIR}/scripts/session_manager.py update {SESSION_ID} --set status=read
```

The reading phase is complete. Proceed to synthesis.

## Resuming an Interrupted Session

If you're resuming a session that was interrupted mid-read, the state manager tracks exactly where you left off. `current_chunk` in the reading state tells you the last chunk that was reflected on. Simply continue from `current_chunk + 1`.
