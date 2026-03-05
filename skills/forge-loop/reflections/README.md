# Universal Patterns

Cross-project repair experience. Auto-populated by Forge after each repair cycle.

## Format (JSONL)

```json
{"pattern_name": "descriptive_name", "error_type": "category", "solution_template": "abstract fix approach", "prevention": "how to avoid in future"}
```

Patterns are auto-extracted from project-specific reflections, stripped of file paths and project context.
Deduped by `pattern_name`.
