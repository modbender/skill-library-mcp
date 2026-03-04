# Project Summary Template

Use this template when generating a methodology summary document for an extracted project.

---

## Template

```markdown
# [Project Name] - Methodology Summary

Brief one-line description of what this project is.

---

## How This Was Built

High-level approach and key decisions that shaped this project.

### Development Approach
- [Docs-first? Iterative? Feature-driven?]
- [Key methodologies used]

### Key Decisions
| Decision | Choice | Why |
|----------|--------|-----|
| [e.g., Framework] | [e.g., Next.js] | [Reasoning] |
| [e.g., Styling] | [e.g., Tailwind + custom tokens] | [Reasoning] |
| [e.g., State] | [e.g., React Query + Zustand] | [Reasoning] |

---

## Design Philosophy

The intentional aesthetic and emotional direction.

### Aesthetic Direction
- **Vibe**: [e.g., Retro-futuristic, minimal, video game UI]
- **Inspirations**: [Reference sites, mood boards, influences]
- **Emotions to evoke**: [e.g., Satisfying, nostalgic, powerful]

### Design System Highlights
- **Colors**: [Key palette decisions]
- **Typography**: [Font choices and why]
- **Motion**: [Animation philosophy]

---

## Architecture Patterns

How the code is organized and why.

### Folder Structure
```
[Key directory structure]
```

### Core Patterns
- **Components**: [Organization approach]
- **Data Flow**: [State management, fetching]
- **API Design**: [REST, GraphQL, tRPC, etc.]

---

## Workflow

Build process, dev setup, deployment.

### Development
- **Start command**: `[e.g., make dev]`
- **Hot reload**: [What reloads automatically]
- **Test command**: `[e.g., make test]`

### Deployment
- **Platform**: [e.g., Vercel, GKE]
- **CI/CD**: [e.g., GitHub Actions]
- **Process**: [How deploys happen]

---

## Patterns to Reuse

What's worth extracting for future projects.

### High Value
- [Pattern 1 - why it's valuable]
- [Pattern 2 - why it's valuable]

### Design System Elements
- [Specific tokens, themes, or components worth extracting]

### Infrastructure
- [Docker patterns, CI/CD configs, etc.]

---

## Lessons Learned

What would be done differently next time.

- [Lesson 1]
- [Lesson 2]
```

---

## Usage Notes

When filling this template:

1. **Be specific** — Don't say "good architecture", say what the architecture is
2. **Capture reasoning** — The "why" is more valuable than the "what"
3. **Focus on reusable** — Emphasize what can be extracted for future projects
4. **Include examples** — Concrete code snippets, file paths, command examples
5. **Note aesthetics** — Design philosophy is high priority, capture it thoroughly
