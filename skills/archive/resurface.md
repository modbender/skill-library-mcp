# Resurfacing Rules

## When to Resurface

### Contextual Triggers
- User mentions topic that matches archived item
- User starts working on project with related archives
- User asks question that archived content answers

### NOT Triggers
- Random time-based ("it's been 30 days")
- Low relevance matches
- User is clearly focused on something else

## Frequency Limits

| Context | Max resurfaces |
|---------|----------------|
| Per conversation | 1-2 items |
| Per day | 3-5 items |
| Same item | Once per week max |

## Format

**Good resurface:**
```
By the way — you archived an article about this 3 months ago 
when researching SaaS pricing. Want me to pull it up?
```

**Bad resurface:**
```
Here are 47 items about pricing from your archive...
```

## Relevance Scoring

Only surface if:
1. **Topic match > 70%** — genuinely related, not tangential
2. **Recency helps** — archived within context where it's useful
3. **User would want this** — based on why they saved it

## User Preferences

Track in `memory.md`:
- Did user engage with resurfaced items?
- Did user say "not now" or "stop suggesting"?
- Which topics get positive response?

Adjust frequency based on actual engagement.

## Opt-out

If user says "don't resurface" or "just search when I ask":
- Note preference in memory.md
- Switch to search-only mode
- Can be reversed: "start suggesting again"
