# AI Specialists - Workspace Conventions

## Specialist Workspace Structure

Each specialist has a structured workspace tailored to their domain. Common patterns:

```
specialist/
├── ai-instructions/          # ALWAYS present
│   ├── core-instructions.md  # Identity, capabilities, communication style
│   └── getting_started.md    # Init sequence, workspace map, protocols
├── preferences/              # User preferences relevant to this domain
├── [domain-folders]/         # Domain-specific content
└── README.md                 # Optional overview
```

## Known Specialist Types

These are types available on AI Specialists Hub. Each user hires instances with custom names:

- **Friday-Personal-Planning** — Personal planning, family stewardship, scheduling
- **peter-product-manager** — Product management, strategic work organization
- **marty-moltbook** — Social media management for Moltbook AI agent network
- **creator** — Interactive workshop for creating new AI specialists
- **dnd-character-development** — D&D character building
- **game-collection-manager** — Board/video game collection tracking
- **github-import** — Specialists imported from GitHub repos (e.g. recipe planners, custom specialists)

## Workspace Patterns by Domain

### Meal Planner (e.g. Ruby)
```
meal-planner/YYYY/MM-month/    # Monthly folders with weekly plans and event plans
recipes/                        # Categorized recipe collection
shopping/                       # Shopping lists, pantry, store preferences
cooking-notes/                  # Tips, substitutions, lessons learned
preferences/                    # Dietary restrictions, cooking style, household info
```

Date convention: `meal-planner/2026/01-january/week-jan-1.md`

### Product Manager (e.g. Peter)
Tracks projects, decisions, strategic context. Read their `ai-instructions/` for specifics.

### Personal Planner (e.g. Benjamin)
Family planning, budgets, goals. Read their `ai-instructions/` for specifics.

## Tips

- **Bulk reads are cheaper** — Use `read_specialist_documents` with an array instead of multiple single reads
- **Trees are free** — `explore_specialist_tree` gives you the full layout in one call
- **Create folders first** — Before writing docs to a new path, create the folder
- **Specialists don't talk to each other** — You (the agent) are the bridge between specialists
- **Respect their style** — Each specialist has a defined communication style in their instructions. When writing to their workspace, match their conventions.
