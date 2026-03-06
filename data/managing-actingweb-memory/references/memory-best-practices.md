# Memory Best Practices

Detailed guidance on writing effective memories and understanding what to store.

## How to Write Good Memories

### Atomic, Not Narrative

Each memory should contain one idea. Break complex information into separate entries.

- Bad: "Had a long discussion about security priorities and decided to focus on production uptime"
- Good: "Security leadership prioritizes production uptime over compliance scope"

### Searchable Language

Write as if you'll later search for it using natural language:
- "Why did we choose..."
- "What do I think about..."
- "How do I usually..."

Natural language beats shorthand. Avoid abbreviations or internal jargon that you wouldn't use as a search term.

### Include Facts + Reasoning

Best format:
```
Decision or belief
Because / rationale
Optional constraint or context
```

Example: "Chose Postgres over DynamoDB because we need complex joins and the team already knows SQL. Cost is comparable at our scale."

## High-Value Use Cases

### 1. Decisions with Context (Highest ROI)

Store decisions with rationale, not just outcomes.

Examples:
- "Chose vendor X over Y due to SOC2 readiness and EU hosting"
- "Rejected feature A because it conflicted with latency budget"

Why: Prevents re-litigating old decisions and gives future-you instant context.

### 2. Personal Operating Manual

Store how you work best.

Examples:
- "I prefer weekly written updates over ad-hoc Slack pings"
- "I make better decisions with a one-pager + options table"

Why: Helps AI assistants adapt to your style across conversations.

### 3. Stakeholder Insights

Store durable signals about people and organizations, not full meeting notes.

Examples:
- "CTO strongly opposed to outsourcing IAM components"
- "Board is sensitive to downtime metrics over cost"

Why: These insights decay slowly but are often forgotten.

### 4. Strategy & Product Breadcrumbs

Capture evolving thinking over time.

Examples:
- "Our ICP prioritizes uptime guarantees over feature breadth"
- "Security buyers respond more to operational risk framing"

Why: Strategy is iterative — memory preserves the trajectory.

## Effective Retrieval Patterns

**Keyword and semantic search:**
- "coffee preferences" (short keywords work best)
- "why did we choose Postgres"
- "decisions about authentication"
- "dietary restrictions"

Combine with category filters for precision: `search(query="allergies", memory_type="health")`

**Browse by recency** (no query needed):
- `search(last_n=5)` — 5 most recent memories
- `search(recency_days=7)` — everything from the last week
- `search(last_n=10, recency_days=30)` — up to 10 memories from the last month

Useful for "what have I been working on?" or reviewing recent activity.

**Interpreting search results:**
Each result includes a `relevance_score` (0–100) and a `match_type` (semantic, keyword, or hybrid). Use these to judge quality:
- Scores >50 are strong, confident matches
- Scores 25–50 are plausible but may need user confirmation
- Scores <25 are tangential — skip unless nothing better is available

## What NOT to Store

- Full documents or raw meeting transcripts
- Short-lived to-dos or transient reminders
- Information that changes frequently without meaningful signal
- Anything you wouldn't search for in 3–12 months
