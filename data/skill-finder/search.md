# Search Strategies — Skill Finder

Reference for effective skill discovery.

## Commands

```bash
# Search by keyword(s)
npx clawhub search "query"
npx clawhub search "react testing"

# Get detailed info about a skill
clawhub inspect <slug>
clawhub inspect <slug> --files  # see all files

# Install a skill
clawhub install <slug>

# Browse latest skills
clawhub explore

# See what's installed
clawhub list
```

## Search by Need, Not Name

User says "I need help with PDFs" — don't just search "pdf".

Think about what they actually need:

| User Need | Better Search |
|-----------|--------------|
| Edit PDFs | `"pdf edit"`, `"pdf modify"` |
| Create PDFs | `"pdf create"`, `"pdf generate"` |
| Extract from PDFs | `"pdf extract"`, `"pdf parse"` |
| Fill PDF forms | `"pdf form"`, `"pdf fill"` |

## Expand Search Terms

If first search yields poor results:

1. **Synonyms** — edit → modify, create → generate, check → validate
2. **Related tools** — pdf → document, docx → word
3. **Underlying task** — "pdf form" → "form filling"
4. **Domain name** — "stripe payments" → just "stripe"

## Interpret Results

Search returns: name, description, author, downloads.

**Quick quality signals:**
- High downloads + recent update = well-maintained
- Clear description = probably well-structured
- Multiple skills by same author = established creator
- Vague description = likely low quality

## Multiple Results Strategy

When several skills match:

1. **Filter** — Apply quality criteria (see `evaluate.md`)
2. **Rank** — By fit to specific need, not just downloads
3. **Present top 3** — With reasoning for each
4. **Let user choose** — Or ask clarifying questions

Example response:
> Found 3 options for React testing:
> 1. `react-testing` — focuses on component tests, 5k downloads
> 2. `jest-react` — Jest-specific patterns, 3k downloads  
> 3. `testing` — general testing, includes React section
>
> Which fits your project better?

## Query Refinement

| Situation | Action |
|-----------|--------|
| Too many results | Add specificity: "python" → "python async" |
| No results | Broaden: "fastapi oauth2" → "api auth" |
| Wrong domain | Clarify: "testing" → "unit testing" vs "e2e testing" |
| Tool-specific | Try tool name directly: "stripe", "twilio" |

## Search Operators

The search is semantic (meaning-based), not keyword-exact.

- `"react hooks"` finds skills about React patterns
- `"api testing"` finds REST, GraphQL testing skills
- `"deploy docker"` finds containerization + deployment

No special operators needed — describe what you want in natural language.
