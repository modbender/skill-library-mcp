---
name: neural-note-taker
description: Advanced associative memory helper for building relationships between facts and entities. Use when processing dense information to ensure context is preserved across long sessions.
---

# Neural Note Taker

Connect the dots in your memory. This skill implements a concept-linkage protocol.

## Core Process

1. **Entity Identification**: Extract names, tools, dates, and projects from current chat.
2. **Relationship Mapping**: Use `[[Target]] -> [[Related]]` notation.
3. **Context Weighting**: Assign priority based on recurrence.

## Commands
- `memo_link [topicA] [topicB]`: Force a connection in long-term memory.
- `memo_query [topic]`: Surface all associated nodes.

## Installation
```bash
clawhub install neural-note-taker
```
