# Extraction Categories

What kinds of things to extract from a codebase, organized by category with specific patterns to look for.

---

## Category 1: Design Systems (Highest Priority)

Visual and aesthetic patterns that define how the application looks and feels.

### What to Extract

| Pattern | Where to Look | Output |
|---------|---------------|--------|
| Color tokens | `tailwind.config.*`, CSS variables, theme files | design-system skill |
| Typography | Font configs, text scale, font imports | design-system skill |
| Spacing | Spacing scale, layout rhythm | design-system skill |
| Motion | Animation configs, transitions, easing | motion-patterns skill |
| Component styles | Styled components, Tailwind classes | ui-patterns skill |

### Files to Scan

```
tailwind.config.js / tailwind.config.ts
postcss.config.js
app.css / globals.css / index.css
styles/ directory
theme.ts / theme.js
components.json (shadcn)
```

### Questions to Answer

- What's the color palette? Primary, secondary, accent, semantic?
- What fonts are used? What's the type scale?
- What's the spacing rhythm? 4px, 8px base?
- How are animations handled? Timing, easing?
- Is there a documented aesthetic (retro-futuristic, minimal, etc.)?

---

## Category 2: UI Patterns

Component patterns, layouts, and interaction designs.

### What to Extract

| Pattern | Where to Look | Output |
|---------|---------------|--------|
| Component organization | `components/` structure | component-patterns skill |
| Layout patterns | Page layouts, grid systems | layout-patterns skill |
| Form handling | Form components, validation | form-patterns skill |
| Loading states | Skeletons, spinners, optimistic UI | loading-patterns skill |
| Navigation | Routing patterns, menus | navigation-patterns skill |

### Files to Scan

```
components/ directory
layouts/ directory
pages/ or app/ directory (for Next.js/Nuxt)
hooks/ (for custom React hooks)
composables/ (for Vue)
```

### Questions to Answer

- How are components organized? Atomic design? Feature-based?
- What reusable layout patterns exist?
- How are forms validated and submitted?
- What loading states are implemented?
- How is navigation structured?

---

## Category 3: Architecture Patterns

Code organization, separation of concerns, data flow.

### What to Extract

| Pattern | Where to Look | Output |
|---------|---------------|--------|
| Folder structure | Root directory layout | architecture skill |
| API patterns | API routes, services | api-patterns skill |
| State management | Stores, context, hooks | state-patterns skill |
| Data fetching | API clients, React Query, SWR | data-fetching skill |
| Error handling | Error boundaries, handlers | error-patterns skill |

### Files to Scan

```
src/ structure
lib/ or utils/
services/ or api/
stores/ or state/
middleware/
```

### Questions to Answer

- What's the high-level folder organization?
- How is business logic separated from UI?
- What's the data fetching strategy?
- How is state managed? Local, global, server?
- How are errors handled throughout?

---

## Category 4: Workflow Patterns

Build processes, development workflows, CI/CD.

### What to Extract

| Pattern | Where to Look | Output |
|---------|---------------|--------|
| Build config | Vite, webpack, esbuild configs | build-patterns skill |
| Task automation | Makefile, package.json scripts | dev-workflow skill |
| Testing setup | Test configs, patterns | testing-patterns skill |
| CI/CD | GitHub Actions, deployment | cicd-patterns skill |
| Docker | Dockerfiles, compose files | docker-patterns skill |

### Files to Scan

```
Makefile
package.json (scripts section)
vite.config.* / webpack.config.*
vitest.config.* / jest.config.*
.github/workflows/
Dockerfile / docker-compose.yml
```

### Questions to Answer

- What's the dev command? (`make dev`, `npm run dev`)
- How are tests run and organized?
- What's the deployment process?
- How is the Docker setup structured?
- What automation exists?

---

## Category 5: Domain-Specific Patterns

Application-specific patterns based on what the app does.

### Detection by App Type

| App Type | Indicators | Domain Patterns to Look For |
|----------|------------|----------------------------|
| E-commerce | Cart, checkout, products | pricing, inventory, order flows |
| Dashboard | Charts, metrics, admin | data viz, filters, table patterns |
| SaaS | Auth, billing, multi-tenant | subscription, team, permission patterns |
| Real-time | WebSockets, live updates | presence, sync, conflict resolution |
| Content | CMS, blog, pages | content models, SEO, publishing |

### Files to Scan

Look for domain-specific directories:
```
features/ (feature-based organization)
modules/
domains/
Any directory named after business concepts
```

### Questions to Answer

- What domain is this application in?
- What are the core business entities?
- What unique workflows exist?
- What domain-specific patterns were developed?

---

## Category 6: Infrastructure Patterns

Kubernetes, monitoring, configuration.

### What to Extract

| Pattern | Where to Look | Output |
|---------|---------------|--------|
| K8s manifests | `k8s/` directory | k8s-patterns skill |
| Monitoring | Prometheus configs, Grafana dashboards | monitoring-patterns skill |
| Logging | Log format, aggregation | logging-patterns skill |
| Config management | env files, config loaders | config-patterns skill |

### Files to Scan

```
k8s/ or kubernetes/
monitoring/ or observability/
prometheus.yml
grafana/ (dashboard JSONs)
.env.example
config/ directory
```

---

## Output Structure

For each extraction category, create:

```
ai/skills/[project-name]-[category]/
├── SKILL.md          # Main skill with patterns
└── references/       # (optional) detailed docs
    └── [pattern].md
```

Or for methodology documentation:

```
docs/extracted/
├── [project-name]-summary.md       # Overall methodology
├── [project-name]-design-system.md # Design patterns
└── [project-name]-architecture.md  # Code patterns
```
