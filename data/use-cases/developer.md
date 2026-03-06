# Developer Context

Software engineers, data scientists, and tech workers looking to integrate AI into their workflow.

## High-Value Dev Tasks

| Task | Best For | Watch Out |
|------|----------|-----------|
| Boilerplate generation | CRUD APIs, scaffolding, schemas | Review security patterns |
| Unit test writing | Existing functions | May miss edge cases |
| Documentation | Auto-generate from code | Verify accuracy |
| Code explanation | Legacy/unfamiliar code | May hallucinate context |
| Debugging assistance | Stack traces, error messages | Verify suggestions |
| Regex/SQL help | Complex patterns | Test thoroughly |
| Refactoring | DRY, readability | Don't trust blindly |

## Prompting Patterns

**Code generation:**
```
"Write a TypeScript function that [specific task]. 
Use [framework/library]. 
Handle errors with [pattern]. 
Include JSDoc comments."
```

**Debugging:**
```
"This error occurs when [context]:
[paste stack trace]
The relevant code is:
[paste code]
What's likely causing this?"
```

**Code review:**
```
"Review this function for:
- Security issues
- Performance problems
- Edge cases not handled
[paste code]"
```

## Integration Approaches

| Method | When to Use |
|--------|-------------|
| IDE plugin (Copilot, Cursor) | Real-time suggestions while coding |
| CLI tool | Scripted workflows, CI/CD |
| API integration | Custom tooling, autonomous agents |
| Chat interface | Exploration, complex problems |

## Quality & Trust

**Hallucination risk areas:**
- API methods that don't exist
- Deprecated syntax
- Incorrect library versions
- Made-up package names

**Always verify:**
- Security-sensitive code (auth, encryption, input validation)
- Database queries (especially writes/deletes)
- External API calls
- Anything going to production

## Keeping Code Private

- Enterprise tiers often don't train on your data — verify policy
- Self-hosted options exist (Ollama, local models)
- Don't paste API keys, credentials, or customer data
- Consider code snippets vs. full files
