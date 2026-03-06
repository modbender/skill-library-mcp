# ~/prompting/ Setup

Create on first use:

```bash
mkdir -p ~/prompting/patterns
```

## memory.md Template

```markdown
# Prompting Memory

## User Preferences
- Default tone: [terse/detailed/casual/formal]
- Preferred models: [claude-sonnet, gpt-4, etc.]
- Token sensitivity: [high/medium/low]

## Voice Patterns
(Extract from user samples when provided)

## Corrections Log
- [date] User said: "..." → Apply: ...

## Frequently Used Prompts
- [task type]: [link to patterns/]
```

## patterns/ Organization

```
patterns/
├── extraction.md      # Entity extraction, parsing
├── generation.md      # Content creation
├── transformation.md  # Format conversion, translation
└── analysis.md        # Summarization, evaluation
```
