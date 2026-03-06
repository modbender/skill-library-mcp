# Pull Request Red Flags

## Instant Rejection Signals

These patterns cause maintainers to close PRs within 30 seconds:

### No Context
- PR appears out of nowhere for unsolicited feature
- No discussion, no approval, just code dump
- "I thought this would be cool" without checking if wanted

### Breaks CI Immediately
- Tests fail on first push
- Shows contributor never ran checks locally

### Scope Creep
- Title says "fix typo" but touches 47 files
- Refactors half the codebase "while fixing a bug"
- Multiple unrelated changes in one PR

### Wrong Target
- PRs to `main` when project uses `develop`
- Ignores branch naming conventions
- Didn't read CONTRIBUTING.md

### Already Addressed
- Issue was closed months ago
- Another PR already open doing same thing
- Duplicate of recently rejected PR

---

## AI-Generated PR Red Flags

Patterns that signal "an AI wrote this poorly":

### Hallucinated Code
- Uses functions that don't exist in the codebase
- References APIs from different libraries
- Invents patterns not used elsewhere in project

### Generic Everything
- Commit message: "Update file.js"
- PR description: "This PR fixes the bug"
- No specific references to actual changes

### Inconsistent Style
- Project uses snake_case, PR uses camelCase
- Different indentation or quote styles
- Ignores existing patterns for "better" ones

### Over-Documentation
- Comments that explain the obvious
- Verbose commit messages that sound robotic

### Drive-By Refactoring
- "Improved code quality" with no specifics
- Renamed variables "for clarity" without asking
- Reformatted unrelated code

### No AI Disclosure
- Clearly AI-generated but not marked
- Makes maintainers feel deceived when they realize

---

## Security Red Flags

### Accidental Vulnerabilities
- `verify=False`, `debug=True`, `allow_all_origins`
- SQL string concatenation instead of parameterized queries
- `eval()`, `exec()`, `pickle.loads()` without safeguards

### Suspicious Additions
- New external network calls
- Encoded/obfuscated content
- Changes to CI/CD configuration
- New dependencies from unknown sources

---

## Behavioral Red Flags

### Spam-Like
- Multiple PRs to same repo in short time
- Not responding to feedback
- Force-pushing without explanation

### Entitled
- @-mentioning maintainers for reviews after 1 day
- Arguing with rejection
- "Why hasn't this been merged yet?"

### Abandonment
- Opens PR, disappears
- Never responds to review comments
- WIP PR that stays WIP forever
