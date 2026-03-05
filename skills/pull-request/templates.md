# Pull Request Templates

## Standard PR Description

```markdown
## Summary

[One paragraph: what this PR does and why]

## Related Issue

Fixes #[number] (or: No issue - small fix per CONTRIBUTING.md)

## Changes

- [Specific change 1]
- [Specific change 2]

## Testing

- [ ] Tests pass locally
- [ ] Manual testing done

How verified: [describe]

## AI Disclosure (if applicable)

This PR was created with AI assistance.
- Testing level: [untested / lightly tested / fully tested]
- Human owner: @[username]

## Checklist

- [ ] Read CONTRIBUTING.md
- [ ] Tests pass
- [ ] Linting passes
```

---

## Bug Fix PR

```markdown
## Bug Fix: [Brief description]

Fixes #[number]

### Problem
[What was happening]

### Root Cause
[Why it happened]

### Solution
[What this PR changes]

### Testing
- Reproduced bug
- Applied fix
- Added regression test
```

---

## AI-Assisted PR

```markdown
## [AI-assisted] [Title]

### Summary
[What and why]

### AI Disclosure
- **Assisted by:** [tool name]
- **Testing level:** untested / lightly tested / fully tested
- **Human owner:** @[username]
- **I confirm:** I have reviewed this code and understand what it does

### Changes
[List]

### Notes for Reviewer
[Anything the AI couldn't verify]
```

---

## Commit Message Formats

### Conventional Commits
```
type(scope): description

[body]

[footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### With DCO Sign-Off
```
feat: add feature

Description.

Signed-off-by: Name <email>
```

Use `git commit -s` to auto-add.
