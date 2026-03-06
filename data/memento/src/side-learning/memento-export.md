# /memento-export — Export session knowledge to Memento

Review this entire session and extract the most important knowledge worth remembering long-term. Focus on:

1. **Decisions** — What was decided and why (architectural choices, trade-offs, rejected alternatives)
2. **Patterns** — Coding patterns, conventions, or idioms established in this project
3. **Gotchas** — Bugs found, surprising behaviors, things that "don't work as expected"
4. **Preferences** — User preferences discovered (coding style, naming conventions, tool choices)
5. **Architecture** — How the system is structured, key abstractions, data flow
6. **People** — Names, roles, or contacts mentioned in context
7. **Tools** — Tool configurations, API quirks, version-specific behaviors

For each fact, provide:
- **content**: Full, specific description (be detailed enough that someone without context can understand)
- **summary**: One-line summary (max 100 chars)
- **category**: One of: `preference`, `decision`, `person`, `tool`, `pattern`, `gotcha`, `architecture`, `convention`
- **visibility**: `shared` (safe for all agents), `private` (this agent only), or `secret` (credentials, sensitive)
- **confidence**: 0.0-1.0 (how certain/important this fact is — use 0.7 for "probably worth remembering", 0.9+ for "definitely important")

Skip trivial facts (e.g., "user asked to create a file"). Focus on knowledge that would help ANY future session working on this or similar projects.

Write the output as a JSON file to `~/.engram/staging/` using this exact format:

```json
{
  "version": 1,
  "source": {
    "type": "claude-code",
    "project": "<current working directory>",
    "sessionId": "<session id if available>",
    "gitBranch": "<current git branch>",
    "exportedAt": "<ISO 8601 timestamp>"
  },
  "agentId": "main",
  "facts": [
    {
      "content": "The Memento plugin uses schema versioning (v1-v5) with automatic migrations on DB open. Each version adds tables without breaking previous ones. Migration runs synchronously in the ConversationDB constructor.",
      "summary": "Memento uses auto-migrating schema versions (v1-v5) in SQLite",
      "category": "architecture",
      "visibility": "shared",
      "confidence": 0.85
    }
  ]
}
```

File naming: `~/.engram/staging/<project-slug>-<timestamp>.json`
Where project-slug is the last directory component of the project path, lowercased and hyphenated.

Create the `~/.engram/staging/` directory if it doesn't exist.

After writing, report how many facts were exported and the file path.
