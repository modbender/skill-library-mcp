# Ingest Pipeline

How to capture a thought from any source and route it to the right place. The pipeline is always the same regardless of where the content came from.

## Pipeline Overview

The ingest pipeline has six steps:

1. **Embed** — Generate embedding via OpenRouter (text-embedding-3-small, 1536 dims)
2. **Classify** — Extract metadata via OpenRouter LLM (gpt-4o-mini, JSON mode) — includes confidence score and routing suggestion
3. **Log** — Insert into `thoughts` table (the Receipt — always, regardless of routing outcome)
4. **Bounce check** — If confidence < 0.6, stop here. Tell user it was captured but you're not sure where to file it.
5. **Route** — Based on type, insert/upsert into the appropriate structured table (the Sorter)
6. **Confirm** — Tell the user what was captured AND where it was filed

## Step 1: Generate Embedding

Convert the thought text into a 1536-dimensional vector via OpenRouter.

```bash
curl -s -X POST "https://openrouter.ai/api/v1/embeddings" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai/text-embedding-3-small",
    "input": "THE_THOUGHT_TEXT"
  }'
```

Extract `data[0].embedding` from the response.

## Step 2: Extract Metadata

Use an LLM to classify the thought and determine routing. OpenRouter with `gpt-4o-mini` in JSON mode:

```bash
curl -s -X POST "https://openrouter.ai/api/v1/chat/completions" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai/gpt-4o-mini",
    "response_format": { "type": "json_object" },
    "messages": [
      {
        "role": "system",
        "content": "Extract metadata from the user'\''s captured thought. Return JSON with:\n- \"type\": one of \"observation\", \"task\", \"idea\", \"reference\", \"person_note\"\n- \"topics\": array of 1-3 short topic tags (always at least one)\n- \"people\": array of people mentioned (empty if none)\n- \"action_items\": array of implied to-dos (empty if none)\n- \"dates_mentioned\": array of dates YYYY-MM-DD (empty if none)\n- \"confidence\": float 0-1 indicating how confident you are in the classification\n- \"suggested_route\": one of \"people\", \"projects\", \"ideas\", \"admin\", or null if observation/reference\n- \"extracted_fields\": object with structured data for the destination table (see below)\n\nFor person_note: extracted_fields = {\"person_name\": \"...\", \"context_update\": \"...\", \"follow_up\": \"...\" (optional)}\nFor task: extracted_fields = {\"task_name\": \"...\", \"due_date\": \"YYYY-MM-DD\" (optional), \"notes\": \"...\" (optional)}\nFor idea: extracted_fields = {\"title\": \"...\", \"summary\": \"...\", \"topics\": [...]}\nFor observation/reference: extracted_fields = null\n\nOnly extract what'\''s explicitly there. When unsure of the type, use \"observation\" with a lower confidence score."
      },
      {
        "role": "user",
        "content": "THE_THOUGHT_TEXT"
      }
    ]
  }'
```

Extract `choices[0].message.content` and parse as JSON.

### Expected Response Format

```json
{
  "type": "person_note",
  "topics": ["career", "consulting"],
  "people": ["Sarah"],
  "action_items": ["Follow up with Sarah about consulting"],
  "dates_mentioned": [],
  "confidence": 0.92,
  "suggested_route": "people",
  "extracted_fields": {
    "person_name": "Sarah",
    "context_update": "Thinking about leaving her job to start a consulting business",
    "follow_up": "Ask about her consulting plans next time"
  }
}
```

### Fallback on Parse Failure

If JSON parsing fails:

```json
{
  "type": "observation",
  "topics": ["uncategorized"],
  "confidence": 0.3,
  "suggested_route": null,
  "extracted_fields": null
}
```

## Steps 1 & 2 Run in Parallel

The embedding and metadata extraction are independent — run them concurrently for speed. Both calls take the same input text and produce independent outputs that get combined in Step 3.

## Step 3: Log in thoughts (The Receipt)

Always insert into `thoughts` first. This is the Receipt — proof that the thought was captured, regardless of what happens next.

```bash
curl -s -X POST "$SUPABASE_URL/rest/v1/thoughts" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d '[{
    "content": "THE_THOUGHT_TEXT",
    "embedding": [EMBEDDING_VECTOR],
    "metadata": {
      "type": "person_note",
      "topics": ["career", "consulting"],
      "people": ["Sarah"],
      "action_items": ["Follow up with Sarah about consulting"],
      "dates_mentioned": [],
      "source": "signal",
      "confidence": 0.92,
      "suggested_route": "people"
    }
  }]'
```

Always include a `source` field in metadata to track where the thought came from. Capture the thought UUID from the response for later routing updates.

## Step 4: Bounce Check (The Bouncer)

If `confidence < 0.6`, stop here. The thought is saved in the inbox (thoughts table) but not routed anywhere else.

Tell the user:

```
Captured as *observation* (confidence: 0.4)
I wasn't confident enough to file this anywhere specific. It's saved in your inbox.
Could you clarify? Try adding a prefix: "person:", "task:", "idea:"
```

If confidence is 0.6 or higher, proceed to routing.

## Step 5: Route to Structured Tables (The Sorter)

Based on the classified type, insert or upsert into the appropriate table.

### Routing Logic

| Type | Route | Action |
|------|-------|--------|
| `person_note` | `people` | Upsert: if person exists, append to context and add follow_up. If new, create row. |
| `task` | `admin` | Insert new task with name, due_date, status='pending' |
| `idea` | `ideas` | Insert new idea with title, summary, topics |
| `observation` | none | Stays in thoughts only |
| `reference` | none | Stays in thoughts only |

### Routing to people (Upsert Pattern)

First, check if the person exists:

```bash
curl -s "$SUPABASE_URL/rest/v1/people?name=eq.Sarah&select=id,context,follow_ups" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"
```

If the person exists, PATCH to append new context and add follow_up:

```bash
curl -s -X PATCH "$SUPABASE_URL/rest/v1/people?name=eq.Sarah" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d '{
    "context": "EXISTING_CONTEXT\n\nNEW_CONTEXT_UPDATE",
    "follow_ups": ["existing follow-up 1", "existing follow-up 2", "NEW_FOLLOW_UP"],
    "embedding": [NEW_EMBEDDING_VECTOR]
  }'
```

If the person doesn't exist, POST to create:

```bash
curl -s -X POST "$SUPABASE_URL/rest/v1/people" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d '[{
    "name": "Sarah",
    "context": "Thinking about leaving her job to start a consulting business",
    "follow_ups": ["Ask about her consulting plans next time"],
    "embedding": [EMBEDDING_VECTOR]
  }]'
```

### Routing to admin (Tasks)

Insert a new task:

```bash
curl -s -X POST "$SUPABASE_URL/rest/v1/admin" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d '[{
    "name": "Follow up with Sarah about consulting",
    "due_date": "2026-02-20",
    "status": "pending",
    "notes": "She mentioned thinking about leaving her job",
    "embedding": [EMBEDDING_VECTOR]
  }]'
```

### Routing to ideas

Insert a new idea:

```bash
curl -s -X POST "$SUPABASE_URL/rest/v1/ideas" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d '[{
    "title": "AI coaching service",
    "summary": "Use AI to provide personalized coaching at scale. Could combine ChatGPT with structured frameworks.",
    "topics": "{ai,coaching,business}",
    "embedding": [EMBEDDING_VECTOR]
  }]'
```

### About Projects

The agent doesn't auto-create projects from single thoughts. Projects are created explicitly by the user ("Start a project for the website redesign") or when the agent recognizes a pattern of related tasks/observations. The agent should suggest creating a project when appropriate.

## Embedding for Structured Tables

When inserting into a structured table, generate an embedding for semantic search. The text to embed varies by table:

| Table | Embed this text |
|-------|----------------|
| `people` | `"{name}. {context}"` |
| `projects` | `"{name}. {notes}"` |
| `ideas` | `"{title}. {summary}"` |
| `admin` | `"{name}. {notes}"` |

When updating an existing record (especially people), re-embed with the updated content.

## Updating the thoughts Row After Routing

After successful routing, update the thoughts row to record where it went:

```bash
curl -s -X PATCH "$SUPABASE_URL/rest/v1/thoughts?id=eq.THOUGHT_UUID" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "metadata": {
      "type": "person_note",
      "topics": ["career", "consulting"],
      "people": ["Sarah"],
      "action_items": ["Follow up with Sarah about consulting"],
      "dates_mentioned": [],
      "source": "signal",
      "confidence": 0.92,
      "suggested_route": "people",
      "routed_to": "people",
      "routed_id": "DESTINATION_UUID"
    }
  }'
```

## Step 6: Confirmation Messages

After successful routing, tell the user what was captured AND where it was filed:

```
Captured as *person_note* — career, consulting
Filed in: people (Sarah)
People: Sarah
Action items: Follow up about consulting plans
```

After bounce (low confidence):

```
Captured as *observation* (confidence: 0.4)
I wasn't confident enough to file this anywhere specific. It's saved in your inbox.
Could you clarify? Try adding a prefix: "person:", "task:", "idea:"
```

## Source Tags

Tag every thought with where it came from. Use these conventions:

| Source | When |
|--------|------|
| `slack` | From Slack |
| `signal` | From Signal |
| `sms` | From SMS |
| `cli` | Via CLI |
| `manual` | During conversation |
| `email` | From email |
| `voice` | Voice transcription |

Add custom sources as needed. The field is freeform text.

## Batch Ingest

For multiple thoughts at once:

1. Batch the embedding call (OpenRouter supports array input):

```bash
curl -s -X POST "https://openrouter.ai/api/v1/embeddings" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai/text-embedding-3-small",
    "input": ["Thought one", "Thought two", "Thought three"]
  }'
```

Each text gets its own entry in `data[]`, matched by `index`.

2. Run metadata extraction for each thought individually (LLM calls don't batch well).

3. Insert all thought rows in one Supabase call:

```bash
curl -s -X POST "$SUPABASE_URL/rest/v1/thoughts" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d '[
    {"content": "Thought one", "embedding": [...], "metadata": {...}},
    {"content": "Thought two", "embedding": [...], "metadata": {...}},
    {"content": "Thought three", "embedding": [...], "metadata": {...}}
  ]'
```

4. Route each thought individually based on its classification.

## Error Handling

| Failure | What to do |
|---------|-----------|
| Embedding fails | Retry once. If still failing, check OpenRouter key/credits. |
| Metadata extraction fails | Use fallback: `{"type": "observation", "topics": ["uncategorized"], "confidence": 0.3}`. No routing. |
| Thoughts insert fails | Critical failure. Check SUPABASE_URL and key. Don't proceed to routing. |
| Routing insert fails | The thought is already logged (Receipt preserved). Tell user: "Captured but filing failed. I'll retry or you can tell me where it goes." |
| People upsert conflict | Use the existing person's ID. Append new context rather than overwriting. |

---

Built by Limited Edition Jonathan • natebjones.com
