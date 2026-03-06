# Shared Memories from Connections

Detailed guidance on accessing and working with memories shared by trusted connections.

## Overview

ActingWeb lets you access memories shared by trusted connections. Connections can be:
- **People** (family, colleagues) who have their own ActingWeb account
- **AI assistants** (e.g., ChatGPT, other Claude instances) connected to the same user account

Trust relationships and sharing preferences are configured via the web dashboard.

## Search Remote Memories

```
search(query="vacation plans", include_remote=true)
```

## Filter by Connection

```
search(query="allergies", include_remote=true, source_connection="Alice")
```

## Filter Remote Types

Search all local memories but restrict remote results to specific categories:

```
search(query="trip", include_remote=true, source_connection="spouse", remote_types="travel,food")
```

## Discover Connections

Use `list_connections()` to see who shares memories with you, what types they share, and whether they also offer remote actions.

## Best Practices

- Ask the user before searching remote memories for the first time in a conversation
- Attribute shared memories to their source naturally (e.g., "Alice mentioned she prefers...")
- Remote memories are read-only — you cannot modify another person's memories
- A connection may share memories, offer remote actions, or both
