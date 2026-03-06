# Markdown Documentation Standards

## Header Hierarchy

- `#` (H1): Project title only — exactly one per document
- `##` (H2): Major sections (Installation, Usage, API, etc.)
- `###` (H3): Subsections within major sections
- `####` (H4): Rarely used, only for deep nesting within subsections

## Required Sections

Every README must include:

1. **Title** (H1) — project name
2. **Description** — one or two sentences summarizing the project
3. **Installation** (H2) — how to set up the project
4. **Usage** (H2) — how to run or use the project
5. **Contributing** (H2) — how to contribute
6. **License** (H2) — license information

## Recommended Sections

- **Table of Contents** — for READMEs longer than 4 sections
- **API Documentation** — for libraries and services
- **Available Scripts** — for projects with build/test/run commands
- **Project Structure** — for complex directory layouts
- **Dependencies** — for projects with notable dependencies
- **Docker** — when Dockerfile or docker-compose is present

## Formatting Rules

- Use fenced code blocks (triple backticks) with language tags
- Use tables for structured data (dependencies, API endpoints, env vars)
- Badges go directly below the title
- Use relative links for repository files
- Prefer bullet lists over numbered lists for unordered items
- Use numbered lists for sequential steps (installation, workflow)
- Add blank lines between sections for readability

## Code Block Languages

Use appropriate language identifiers:
- `bash` for shell commands
- `javascript` / `js` for JavaScript
- `typescript` / `ts` for TypeScript
- `python` for Python
- `go` for Go
- `rust` for Rust
- `json` for JSON configuration
- `yaml` for YAML files
