# Memory Setup — Business Idea Generator

## Initial Setup

Create directory on first use:
```bash
mkdir -p ~/business-ideas/archive
touch ~/business-ideas/ideas.md
touch ~/business-ideas/favorites.md
touch ~/business-ideas/filters.md
```

## ideas.md Template

Copy to `~/business-ideas/ideas.md`:

```markdown
# Generated Ideas

## 2024-XX-XX

### [Idea Name]
- **Category:** [Industry] / [Model]
- **One-liner:** [Single sentence pitch]
- **Target:** [Specific customer]
- **Scores:** Market: X | Timing: X | Moat: X | Fit: X | Simple: X | **Avg: X.X**
- **Status:** New | Exploring | Rejected | Archived

---
```

## favorites.md Template

Copy to `~/business-ideas/favorites.md`:

```markdown
# Favorite Ideas

Ideas marked for deeper exploration.

## [Idea Name]
- **Added:** YYYY-MM-DD
- **Why:** [What excited user about this]
- **Next step:** [Validation experiment or research]
- **Notes:**

---
```

## filters.md Template

Copy to `~/business-ideas/filters.md`:

```markdown
# My Filters

## Default Constraints
- **Industries:** [Tech, Health, etc.]
- **Models:** [SaaS, Marketplace, etc.]
- **Investment:** [Bootstrap, Seed, Funded]
- **Time:** [Side project, Part-time, Full-time]
- **Skills:** [Technical, Non-technical, Hybrid]

## Preferences
- **Risk tolerance:** [Conservative, Moderate, Aggressive]
- **Focus:** [B2B, B2C, Both]
- **Geography:** [Local, National, Global]

## Avoid
- [Industries or models to skip]

---
*Last updated: YYYY-MM-DD*
```
