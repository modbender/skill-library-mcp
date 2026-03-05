---
name: no-code-frontend-builder
description: Meta-skill for generating production-ready React UI for non-programmers by orchestrating frontend-design-ultimate, shadcn-ui, and react-expert. Use when users describe UI outcomes (for example dashboards, landing pages, admin screens) and need a single copy-pasteable TSX component with explicit setup and dependency instructions.
homepage: https://clawhub.ai
user-invocable: true
disable-model-invocation: false
metadata: {"openclaw":{"emoji":"🧩","requires":{"bins":["node","npm","npx"],"env":[],"config":[]},"note":"Requires local installation of frontend-design-ultimate, shadcn-ui, and react-expert."}}
---

# Purpose

Enable non-programmers to get production-grade frontend components from natural-language requirements.

This meta-skill coordinates three upstream skills and produces implementation-ready output, usually as one `.tsx` file plus concise setup notes.

It does not replace upstream skill logic and does not assume hidden dependencies are already installed.

# Required Installed Skills

- `frontend-design-ultimate` (inspected latest: `1.0.0`)
- `shadcn-ui` (inspected latest: `1.0.0`)
- `react-expert` (inspected latest: `0.1.0`)

Install/update:

```bash
npx -y clawhub@latest install frontend-design-ultimate
npx -y clawhub@latest install shadcn-ui
npx -y clawhub@latest install react-expert
npx -y clawhub@latest update --all
```

Verify:

```bash
npx -y clawhub@latest list
```

# OpenClaw Compatibility Notes

This skill is written to match OpenClaw skill-loading rules:
- `SKILL.md` with YAML frontmatter and Markdown body
- single-line frontmatter keys
- `metadata` encoded as a single-line JSON object
- no unsupported custom top-level frontmatter keys

If this file is edited later, keep those constraints intact.

# Runtime Prerequisites

Minimum local stack:
- Node.js 18+
- npm
- React + TypeScript project with Tailwind configured

Adjacent ecosystem dependencies (from inspected upstream skill content):
- `tailwindcss` (layout/styling baseline)
- `lucide-react` (icons used by many shadcn examples)
- `next-themes` (theme toggle patterns in shadcn guidance)
- `react-hook-form`, `zod`, `@hookform/resolvers` (form patterns)
- optional: `framer-motion` (motion patterns from frontend-design-ultimate)
- optional: `recharts` or equivalent if a real chart package is required

If user wants shadcn components and they are missing, include explicit setup commands in output:

```bash
npx shadcn@latest init
npx shadcn@latest add card button badge tabs table sheet sidebar
```

Do not assume Next.js unless the user says Next.js.
Default to framework-agnostic React `.tsx` output that can run in Vite or Next.js with minimal adaptation.

# Inputs the LM Must Collect First

- `ui_goal` (dashboard, landing page, admin panel, etc.)
- `theme_mode` (`dark`, `light`, or `system`)
- `primary_metrics` (for example revenue, MRR, growth)
- `chart_expectation` (line, bar, area; static or interactive)
- `layout_density` (`compact`, `balanced`, `spacious`)
- `brand_constraints` (colors, logo, typography constraints)
- `target_framework` (`vite-react`, `nextjs`, or `generic-react`)
- `single_file_strict` (`true`/`false`)

If any critical input is missing, make explicit defaults and state them in `Assumptions`.

# Tool Responsibilities

## frontend-design-ultimate

Use for visual direction and anti-generic design decisions:
- choose strong aesthetic direction
- define typographic hierarchy and color system
- enforce mobile-first responsiveness
- avoid boilerplate “AI-slop” layouts

From inspected upstream guidance:
- commit to one clear tone
- include an unforgettable visual element
- prefer CSS variables and strong contrast
- avoid generic default fonts

## shadcn-ui

Use for robust UI primitives and composition patterns:
- cards, tabs, sheets, navigation, table, badges, dialogs
- theming conventions and dark mode compatibility
- predictable component structure for fast shipping

From inspected upstream guidance:
- components are copied into the project (not a hosted runtime UI SDK)
- include install commands for any components you reference
- prefer composable primitives for layout and data display

## react-expert

Use for behavioral correctness and maintainability:
- state design and data flow
- strict TypeScript-first component patterns
- accessibility and predictable rendering behavior
- optional performance hardening for non-trivial UI

From inspected upstream guidance:
- avoid state mutation and unstable keys
- use semantic structure and cleanup in effects
- ship clear typed interfaces for props/data

# Canonical Causal Chain

Use this exact orchestration order.

1. `Requirement Parse`
- Normalize user request into goals, constraints, and output contract.

2. `Design Direction (frontend-design-ultimate)`
- Select one explicit aesthetic mode.
- Define palette, type scale, spacing, and page composition.
- Decide dark-mode token strategy.

3. `Component Architecture (shadcn-ui)`
- Map UI blocks to component primitives (sidebar, card, tabs, table, badge).
- Declare required shadcn installs for referenced primitives.

4. `React Glue Logic (react-expert)`
- Implement typed data models and render loops.
- Add local state/hooks where required.
- Keep logic simple and deterministic for copy-paste usability.

5. `Output Assembly`
- Produce one `.tsx` file by default.
- Include short `Setup` section with required install commands.
- Include `Assumptions` and `Adaptation Notes`.

# Output Contract

Default output must contain:

- `Setup`:
  - exact npm/npx commands for missing dependencies
  - shadcn component add commands used by generated code

- `Single TSX File`:
  - one self-contained React component in TypeScript
  - imports listed at top
  - mock data included inline unless user supplies real data source

- `Assumptions`:
  - explicit defaults chosen due to missing input

- `Adaptation Notes`:
  - where to plug in real API data
  - which imports to remove if a component is unavailable

No auxiliary script generation. No multi-file scaffolding unless user explicitly asks.

# Chart Handling Rule

If chart library is not guaranteed in target project:
- default to a semantic “chart-ready” card layout with placeholders, or
- use lightweight inline SVG chart logic in the same `.tsx`.

Do not hallucinate unavailable chart components.
If using external chart lib (for example Recharts), include install command and clearly label as optional.

# Scenario Mapping: Revenue Dashboard (Dark Mode)

For scenario:
"I need a dark-mode dashboard showing revenue metrics"

Execution:
1. frontend-design-ultimate defines dark palette, bold typography, and dashboard composition (sidebar + metric grid + chart area).
2. shadcn-ui maps layout to `Card`, `Badge`, `Tabs`, optional `Sidebar` primitives.
3. react-expert creates typed metric arrays and rendering loops for KPI tiles + trend view.
4. final output returns one production-usable `.tsx` component plus setup commands.

# Quality Gates

Before finalizing output, ensure:
- component compiles as TSX (no missing symbols in emitted code)
- design is intentional, not default-template generic
- dark mode tokens are coherent and readable
- mobile behavior is included (`sm/md/lg` responsive strategy)
- all referenced UI components are listed in setup commands
- no fake API calls presented as real integrations

If any gate fails, return `Needs Revision` with a concrete missing-items list.

# Guardrails

- Never claim “works out of the box” without listing dependency assumptions.
- Never emit components from libraries not declared in setup.
- Never hide unresolved decisions (state them under `Assumptions`).
- Prefer one high-quality component over broad but shallow scaffolding.

# Failure Handling

- Missing upstream skills: stop and report exact missing skills.
- Missing project context: output generic React version and mark adaptation points.
- Missing chart dependency: provide fallback rendering path and optional install command.
- Conflicting constraints (for example “single file” + “full app routing”): prioritize single-file contract and document tradeoff.
