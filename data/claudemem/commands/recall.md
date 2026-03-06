---
description: Search persistent memory for relevant context about a topic
argument-hint: Topic or keyword to search for
---

Search claudemem for anything related to the given topic.

## Instructions

1. If the user provided a topic/keyword, search for it:
```bash
claudemem search "<topic>" --format json
```

2. If no topic provided, show recent activity:
```bash
claudemem session list --last 5
claudemem stats
```

3. Present the results in a clear, organized format:
   - Group by type (notes vs sessions)
   - Show the most relevant content inline (not just titles)
   - If a note is highly relevant, read the full content with `claudemem note get <id>`

4. Offer to dive deeper into any specific result if the user wants more detail.
