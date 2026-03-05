# shadcn/ui Skill

Complete shadcn/ui component library documentation as an OpenClaw AgentSkill.

## What's Included

- **201 MDX files** with full shadcn/ui documentation
- 50+ component guides (Button, Dialog, Form, Table, Charts, etc.)
- Installation guides for Next.js, Vite, Remix, Astro, Laravel, Gatsby
- Theming and dark mode implementation
- Form integration (React Hook Form, Tanstack Form, Zod)
- Chart components (Recharts integration)
- Data table patterns
- CLI reference and configuration
- Registry system documentation
- Accessibility best practices

## Installation

### From Local Directory

```bash
clawhub install /path/to/shadcn-ui-skill
```

### From Archive

```bash
clawhub install shadcn-ui.skill
```

## Usage

This skill is automatically loaded by OpenClaw when available in the workspace skills directory.

Agents with this skill can answer questions about:

- Installing and configuring shadcn/ui components
- Component API reference and usage examples
- Theming and customization
- Framework integration (Next.js, Vite, Remix, etc.)
- Form validation with React Hook Form and Zod
- Building data tables with sorting, filtering, pagination
- Chart implementation with Recharts
- Accessibility best practices
- Dark mode implementation

## shadcn/ui Philosophy

**Not a component library.** It's a collection of re-usable components that you copy and paste into your apps.

### Key Benefits

- **You own the code** - Components are copied to your project, not imported from npm
- **Fully customizable** - Modify components directly in your codebase
- **Built on Radix UI** - Accessible, unstyled primitives
- **Styled with Tailwind** - Utility-first CSS for easy customization
- **CSS Variables** - Theme with CSS variables for consistent design
- **Framework agnostic** - Works with Next.js, Vite, Remix, Astro, etc.

## Documentation Source

Official documentation from:
- Website: https://ui.shadcn.com
- Repository: https://github.com/shadcn-ui/ui
- Extracted: 2026-02-07

## File Structure

```
shadcn-ui/
├── SKILL.md              # Skill metadata and description
├── README.md             # This file
├── .gitignore            # Git ignore rules
└── docs/                 # Full shadcn/ui documentation (201 MDX files, 1.4MB)
    ├── installation/
    ├── components/
    ├── charts/
    ├── forms/
    ├── registry/
    └── ...
```

## Tags

`shadcn` `ui` `components` `tailwind` `radix` `react` `nextjs` `design-system` `accessibility` `theming` `documentation`

## License

Documentation content © shadcn.
Skill package © OpenClaw Community, MIT License.
