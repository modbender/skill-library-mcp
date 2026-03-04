---
description: Generate, test, and explain regular expressions from natural language descriptions.
---

# Regex Wizard

Generate, test, and explain regular expressions from plain English.

## Requirements

- `python3`, `grep -P`, or `node` for testing regex (at least one)
- No API keys needed

## Instructions

### Generate regex from description
1. Clarify ambiguous requirements (multiline? global? case-insensitive?)
2. Produce the pattern with flavor noted (Python, JS, PCRE, Go)
3. Explain each component in plain English
4. Show 3+ example matches and 2+ non-matches

### Explain existing regex
1. Break into tokens/groups with inline annotations
2. Explain in simple language (avoid jargon)
3. Show example strings that match and don't match
4. Note the assumed flavor and any flavor-specific features used

### Test regex against strings
Run the pattern against provided test strings:
```bash
# Python (most portable)
python3 -c "
import re
pattern = r'YOUR_PATTERN'
tests = ['test1', 'test2', 'test3']
for t in tests:
    m = re.search(pattern, t)
    print(f'{t!r}: {\"✅ Match\" if m else \"❌ No match\"}' + (f' → groups: {m.groups()}' if m else ''))
"

# Grep (quick check)
echo "test string" | grep -P 'pattern'
```

### Output format
```
**Pattern**: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
**Flavor**: Python/PCRE
**Flags**: None

| Component | Meaning |
|-----------|---------|
| `^` | Start of string |
| `[a-zA-Z0-9._%+-]+` | One or more valid email chars |
| `@` | Literal @ |
| `[a-zA-Z0-9.-]+` | Domain name |
| `\.[a-zA-Z]{2,}$` | TLD (2+ letters) at end |

**Matches**: `user@example.com`, `a.b+c@test.co.uk`
**Non-matches**: `@example.com`, `user@`, `user@.com`
```

## Common Pitfalls to Warn About

- **Greedy vs lazy**: `.*` vs `.*?` — explain when it matters
- **Catastrophic backtracking**: Nested quantifiers like `(a+)+` — always flag these
- **Unescaped dots**: `.` matches any char, not just literal dots
- **Anchors**: Missing `^`/`$` can cause partial matches
- **Unicode**: `\w` behavior differs across flavors (Python 3 includes Unicode by default)

## Edge Cases

- **Email/URL validation**: Warn that perfect regex for these is extremely complex. Suggest using libraries instead for production.
- **Multi-line input**: Remind about `re.DOTALL` / `re.MULTILINE` flags.
- **Empty string matching**: Patterns like `.*` match empty strings — clarify if that's intended.

## Security

- Never use user-supplied regex directly in production without timeout/limits (ReDoS risk).
- When testing regex against user data, sanitize the test strings in output.
