# Tinmem Memory System

openclaw-tinmem provides persistent memory capabilities for the OpenClaw AI assistant.

## Tools

### memory_recall

Search and retrieve relevant memories from past conversations.

Use this tool when:
- The user references something from a previous conversation
- You need context about user preferences, background, or past decisions
- You want to check if a problem has been solved before

**Parameters:**
- `query` (required): Search query to find relevant memories
- `scope`: Memory namespace (default: "global")
- `categories`: Filter by category: profile, preferences, entities, events, cases, patterns
- `limit`: Max results (default: 10)
- `level`: Detail level - L0 (headline), L1 (summary), L2 (full content)

**Example:**
```json
{
  "query": "user's preferred programming language",
  "categories": ["profile", "preferences"],
  "level": "L1"
}
```

---

### memory_store

Store new information as a persistent memory.

Use this tool when:
- The user shares important personal information
- A significant decision is made
- A problem is solved in a novel way
- A new project or entity is introduced

**Parameters:**
- `content` (required): The information to store
- `category` (required): profile | preferences | entities | events | cases | patterns
- `scope`: Memory namespace
- `importance`: 0.0-1.0 (default: 0.5)
- `tags`: Keywords for searchability

**Example:**
```json
{
  "content": "User is building a SaaS product called TaskFlow for project management, using Next.js 14 and PostgreSQL with Prisma",
  "category": "entities",
  "importance": 0.9,
  "tags": ["taskflow", "nextjs", "postgresql", "saas"]
}
```

---

### memory_forget

Remove memories that are no longer relevant or are incorrect.

**Parameters:**
- `id`: Specific memory ID to delete
- `query`: Search and delete matching memories
- `scope`: Limit deletion to this scope
- `categories`: Limit deletion to these categories

**Example:**
```json
{
  "query": "old job at previous company",
  "categories": ["profile", "entities"]
}
```

---

### memory_update

Update an existing memory with corrected or additional information.

**Parameters:**
- `id` (required): Memory ID to update
- `content`: New full content
- `summary`: New summary
- `headline`: New headline
- `importance`: New importance score
- `tags`: New tags (replaces existing)

---

## Memory Categories Reference

| Category | What to Store | Merge Behavior |
|----------|---------------|----------------|
| `profile` | User identity, role, expertise, demographics | Always merge |
| `preferences` | Likes/dislikes, habits, recurring preferences | Topic-based merge |
| `entities` | Projects, people, tools, organizations | Merge if same entity |
| `events` | Decisions made, milestones, things that happened | Always append (never merge) |
| `cases` | Problem-solution pairs, debugging sessions | Always append (never merge) |
| `patterns` | Recurring workflows, methodologies, best practices | Merge if same pattern |

## Notes

- Memories are automatically injected into context before each response via `<agent-experience>` tags
- New memories are automatically extracted after each conversation turn
- Similar memories are deduplicated using LLM-based analysis
- All memories persist across sessions in a local LanceDB database
