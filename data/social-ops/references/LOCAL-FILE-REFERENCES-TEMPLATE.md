# Local File References (Template)

Use this template to create:

`$SOCIAL_OPS_DATA_DIR/Guidance/Local-File-References.md`

Purpose:
- Provide a human-editable list of local files/directories that the **Content Specialist** may read during backlog generation.
- Keep source selection explicit and auditable.

## Rules

- Keep paths relative to the skill runtime root where possible.
- Prefer small, high-signal files over huge directories.
- Mark optional items clearly.
- Remove stale paths instead of letting the list rot.

## Suggested format

```markdown
# Local File References

## Required
- Projects/Some-Project.md
- Creative/Ideas/Recurring-Themes.md

## Optional
- Reference/Bolton/
- Notes/Experiments/

## Exclusions
- Private/
- Archive/
```

## Notes for operators

- Missing paths are non-fatal; the run should continue.
- The Content Specialist should log skipped/missing references in its daily content log.
