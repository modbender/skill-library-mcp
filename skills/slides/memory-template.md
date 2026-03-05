# Memory Setup — Slides

## Initial Setup

Create directory on first use:
```bash
mkdir -p ~/slides/{styles,projects,templates}
touch ~/slides/memory.md
```

## memory.md Template

Copy to `~/slides/memory.md`:

```markdown
# Slides Memory

## Active Projects
<!-- Current presentations being worked on -->
| Project | Type | Tool | Style | Last Updated |
|---------|------|------|-------|--------------|

## Preferred Tools
<!-- Default tools by context -->
- Corporate decks: 
- Tech talks: 
- Quick presentations: 

## Recent Learnings
<!-- Style corrections, preferences discovered -->

---
*Last: YYYY-MM-DD*
```

## styles/{name}.md Template

For each brand/client style:

```markdown
# Style: {Name}

## Colors
- Primary: #HEXCODE
- Secondary: #HEXCODE
- Accent: #HEXCODE
- Text: #HEXCODE
- Background: #HEXCODE

## Typography
- Headings: {Font Name}, {Weight}
- Body: {Font Name}, {Weight}
- Code: {Monospace Font}

## Size Scale
- Title: 44pt
- H1: 36pt
- H2: 28pt
- Body: 24pt
- Caption: 18pt

## Logo
- Path: 
- Placement: top-right | bottom-left
- Min size: 

## Additional Rules
<!-- Company-specific guidelines -->
```

## projects/{name}/context.md Template

```markdown
# Project: {Name}

## Purpose
<!-- Why this presentation exists -->

## Audience
<!-- Who will see it, what they care about -->

## Constraints
- Duration: X minutes
- Slide count: ~X
- Format: .pptx | Google Slides | web
- Must include: 
- Avoid: 

## Key Messages
1. 
2. 
3. 

## Assets Available
- Data sources: 
- Images: 
- Previous versions: 
```

## projects/{name}/versions.md Template

```markdown
# Versions: {Project Name}

## v1.0 — YYYY-MM-DD
- Initial version
- Audience: 
- Slides: X

## v1.1 — YYYY-MM-DD
- Changes: 
- Reason: 

<!-- Add new versions at top -->
```

## templates/{type}.md Template

For reusable deck structures:

```markdown
# Template: {Type} Deck

## When to Use
<!-- Context where this template applies -->

## Structure

### Slide 1: {Title}
- Content: 
- Layout: title-only | title-content | two-column

### Slide 2: {Title}
- Content: 
- Layout: 

<!-- Continue for all slides -->

## Variations
- Short version (X slides): skip slides #
- Extended version: add # between X and Y

## Notes
<!-- Tips for using this template -->
```
