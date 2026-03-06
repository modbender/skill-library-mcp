# /extract-patterns

Extract patterns, design systems, and methodology from the current codebase.

## Usage

```
/extract-patterns [focus]
```

**Focus options:**
- `all` (default) — Full extraction across all categories
- `design` — Design system and visual patterns only
- `architecture` — Code organization and patterns only
- `workflow` — Build, dev, deploy patterns only

## Examples

```
/extract-patterns
/extract-patterns design
/extract-patterns architecture
```

## What It Does

1. **Discovers** what exists in the codebase (tech stack, structure, design)
2. **Categorizes** findings by type (design > architecture > workflow)
3. **Extracts** valuable patterns into skills and documentation
4. **Outputs** to `ai/skills/` and `docs/extracted/`

## Quick Start

Just run `/extract-patterns` and the extraction process will:

1. Scan the project structure
2. Identify the tech stack
3. Look for design system signals (Tailwind config, CSS variables, themes)
4. Find architecture patterns (folder structure, components, data flow)
5. Capture workflow patterns (Makefile, scripts, CI/CD)
6. Generate methodology documentation
7. Create skills for reusable patterns

## Output Locations

```
docs/extracted/
├── [project]-summary.md       # Methodology overview
├── [project]-design-system.md # Design tokens and aesthetic
└── [project]-architecture.md  # Architecture patterns

ai/skills/
└── [project]-[pattern]/
    └── SKILL.md               # Extracted skill
```

## Priority Order

Extraction prioritizes in this order:

1. **Design Systems** — Highest priority (colors, typography, motion, aesthetic)
2. **UI Patterns** — Components, layouts, interactions
3. **Architecture** — Folder structure, data flow, APIs
4. **Workflows** — Build, dev, deploy, CI/CD
5. **Domain-Specific** — Application-specific patterns

## After Extraction

To consolidate patterns from multiple projects:

```bash
# Copy extracted content to the skills repo staging area
cp -r ai/skills/[project]-* /path/to/skills-repo/ai/staging/skills/
cp -r docs/extracted/* /path/to/skills-repo/ai/staging/docs/
```

Then in the skills repo, say "refine staged content" to consolidate.

## Related

- Full skill: [`SKILL.md`](SKILL.md)
- Values reference: [`references/methodology-values.md`](references/methodology-values.md)
- Categories: [`references/extraction-categories.md`](references/extraction-categories.md)
- Staging: [`../../staging/README.md`](../../staging/README.md)
- Refinement: [`../refinement/SKILL.md`](../refinement/SKILL.md)
