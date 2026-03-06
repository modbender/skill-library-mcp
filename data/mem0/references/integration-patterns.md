# Mem0 Integration Patterns for Clawdbot

## Best Practice: Pre-Search, Post-Store Pattern

The optimal workflow for using mem0 in Clawdbot conversations:

### 1. Before Responding (Retrieve)
Search relevant memories to inject context:

```javascript
const memories = await memory.search(userQuery, {
  userId: "abhay",
  limit: 3
});

// Extract and format memories for context
const context = memories.results
  .map(m => `- ${m.memory}`)
  .join("\n");
```

### 2. During Response (Use)
Inject memory context into your reasoning:
- Consider user preferences from memories
- Reference past interactions
- Adapt tone and depth based on learned patterns

### 3. After Responding (Store)
Extract and store new memories from the conversation:

```javascript
// For explicit "remember this" requests
await memory.add(factText, { userId: "abhay" });

// For conversation context
const messages = [
  { role: "user", content: userMessage },
  { role: "assistant", content: assistantResponse }
];
await memory.add(messages, { userId: "abhay" });
```

## Memory Types to Store

### ✅ Store These:
- **Explicit requests**: "Remember that I prefer..."
- **Preferences**: Communication style, format preferences
- **Facts**: Personal details, work info, family
- **Patterns**: Usage times, frequent requests
- **Context**: Project names, important dates
- **Corrections**: When user corrects mistakes

### ❌ Don't Store:
- Secrets, passwords, API keys
- Temporary context (unless explicitly requested)
- System messages or errors
- Redundant information already in MEMORY.md

## Complementing Clawdbot Memory

### Clawdbot MEMORY.md (Manual)
- Permanent facts: Name, location, family
- Reference data: URLs, email, identities
- Structured knowledge: Project info, credentials

### Mem0 (Automatic)
- Dynamic preferences: "Abhay likes brief updates"
- Learned patterns: "Usually asks for bus info at 8:30am"
- Conversational context: Recent interests, topics
- Adaptive facts: "Currently interested in AI news"

## Performance Optimization

### Token Efficiency
- Mem0 reduces prompt size by 90% vs full context
- Search retrieves only relevant memories (not all history)
- LLM extracts and deduplicates automatically

### Speed
- Sub-50ms retrieval (91% faster than full-context)
- Async operations don't block responses
- Local vector store for fast access

### Accuracy
- +26% accuracy improvement over OpenAI Memory
- Semantic search finds context beyond keywords
- Automatic deduplication and updates

## Error Handling

Always wrap mem0 operations in try-catch:

```javascript
try {
  const results = await memory.search(query, { userId });
  // Use results
} catch (error) {
  console.error("Mem0 search failed:", error.message);
  // Fall back to response without memory context
}
```

Never let memory failures block user responses.

## Configuration Notes

- Uses OpenAI embeddings (text-embedding-3-small)
- Uses OpenAI LLM (gpt-4o-mini) for extraction
- Stores in local vector DB (~/.mem0/)
- History tracked in SQLite DB
- All operations tied to userId: "abhay"
