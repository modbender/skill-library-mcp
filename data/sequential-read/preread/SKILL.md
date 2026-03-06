---
name: sequential-read-preread
description: "Analyse source material and split into semantic chunks for sequential reading"
user-invocable: false
---

# Preread Phase — Semantic Chunking

You are performing the preread phase of a sequential reading session. Your job is to analyse the source material, split it into semantic chunks, and prepare the session for reading.

## Inputs

You will be given:
- `SESSION_ID` — the session identifier
- `SOURCE_FILE` — path to the source text file
- `BASE_DIR` — path to the sequential_read skill directory

## Procedure

### 1. Read the Source File

Read the entire source file using the `read` tool. Understand its structure, length, and type (novel, essay, article, poetry, non-fiction, etc.).

### 2. Decide Chunking Strategy

Choose an appropriate chunking approach based on the material:

| Material Type | Default Approach |
|---|---|
| Novel with chapters | One chunk per chapter (combine very short chapters) |
| Novel without chapters | Scene breaks or ~300-400 line segments at paragraph boundaries |
| Essay/article | Section by section, or argument-by-argument |
| Non-fiction with chapters | One chunk per chapter |
| Poetry | Stanza groups or poem-by-poem in a collection |
| Short story | 2-5 chunks based on narrative movement |

**Key constraints:**
- Chunks must contain the **complete original text** — no abridging, no summarising
- Chunks must be **in order**
- Each chunk should be a meaningful unit of reading (not mid-sentence or mid-paragraph)
- Consider reading rhythm: cliffhanger endings might pair better with the next section

### 3. Determine if Structural Fallback is Needed

If the source file is too large to fit entirely in your context (roughly >200,000 characters), use the structural chunker as a fallback:

```bash
python3 {BASE_DIR}/scripts/chunk_manager.py structural-chunk {SESSION_ID} {SOURCE_FILE}
```

This will automatically split on chapter markers, scene breaks, and paragraph boundaries (targeting 300-400 lines per chunk) and save all chunks to the session.

Skip to step 5 if using the structural fallback.

### 4. Save Chunks (Semantic Approach)

For each chunk you identify:

1. Write the chunk text to a temp file:
   ```bash
   # Write chunk text to temp file (use the read tool to get the text, write tool to save it)
   ```

2. Save via chunk_manager:
   ```bash
   python3 {BASE_DIR}/scripts/chunk_manager.py save {SESSION_ID} {N} \
     --text-file /tmp/chunk_N.md \
     --meta '{"tone":"<tone>","intensity":"<low|medium|high>","themes":["<theme1>","<theme2>"],"adjacent_relationship":"<relationship to previous/next chunk>"}'
   ```

   Metadata fields:
   - **tone**: descriptive string (e.g., "melancholic", "argumentative", "playful", "tense")
   - **intensity**: low / medium / high — how emotionally or intellectually demanding
   - **themes**: array of 1-4 thematic tags
   - **adjacent_relationship**: how this chunk connects to neighbours (e.g., "resolution of previous chapter's cliffhanger", "new argument thread", "continuation of scene")

### 5. Update Session Status

```bash
python3 {BASE_DIR}/scripts/session_manager.py update {SESSION_ID} --set status=chunked
```

### 6. Initialise Reading State

```bash
python3 {BASE_DIR}/scripts/state_manager.py init {SESSION_ID}
```

### 7. Write Chunking Notes

Write a brief `chunking_notes.md` file to the session directory explaining:
- How many chunks you created and why
- What chunking approach you chose and the rationale
- Any notable structural features of the source (unusual formatting, embedded documents, etc.)

Save it to: `{WORKSPACE}/memory/sequential_read/{SESSION_ID}/chunking_notes.md`

## Done

After completing all steps, the preread phase is complete. The reading phase can begin.
