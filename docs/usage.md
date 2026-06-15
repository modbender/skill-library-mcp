---
title: Usage
description: The three Skill Library MCP tools in depth — list_categories, search_skill, and load_skill — plus the recommended browse, search, load workflow.
sidebar:
  order: 3
---

Skill Library MCP exposes exactly three tools. Two help your assistant *find* a skill, and one *loads* it. The whole library is driven through these three:

| Tool | Purpose |
| --- | --- |
| `list_categories` | Browse all 13 categories with counts and examples — discover what's available. |
| `search_skill` | Find skills matching a keyword or natural-language query. |
| `load_skill` | Load the full content of a specific skill (optionally with its resource files). |

:::tip
You usually don't invoke these tools by hand. Describe what you want in plain language — *"find me a skill for writing Playwright tests and apply it"* — and your assistant decides when to call `list_categories`, `search_skill`, and `load_skill` for you. The examples below show the underlying calls so you understand what's happening.
:::

## The recommended workflow

The three tools are designed to be used in order, narrowing from "what exists" to "the exact skill I want":

1. **`list_categories`** — get the lay of the land. Useful when you don't yet know what's available or want to point search at the right area.
2. **`search_skill`** — find candidate skills for your task.
3. **`load_skill`** — pull in the one you picked.

For a fully worked walkthrough of this loop, see [Search and load a skill](/skill-library-mcp/examples/search-and-load/).

## `list_categories`

Lists every category with its skill count and a few example skills. It takes **no parameters**. Use it to discover what's in the library before you search.

```text
list_categories()
```

The response counts the full library and names each category:

```text
15223 skills in 13 categories:

- **Frontend** (…) — react-patterns, tailwind-layouts, accessibility-audit, +… more
- **Backend** (…) — fastapi-service, graphql-schema, rest-api-design, +… more
- **AI & LLM** (…) — rag-implementation, agent-patterns, prompt-engineering, +… more
…
```

The 13 categories are: **Frontend**, **Backend**, **AI & LLM**, **DevOps & Infra**, **Data & Databases**, **Security**, **Testing**, **Mobile**, **Automation**, **Python**, **TypeScript & JS**, **Architecture**, and **Other** (skills that don't match a keyword category).

## `search_skill`

Searches the library and returns a ranked list of matching skills. Search is IDF-weighted, so it surfaces the most distinctive matches — and it handles natural-language queries, not just bare keywords.

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `query` | `string` | **Yes** | Keywords or a natural-language description of what you need. |

```text
search_skill({ query: "react patterns" })
```

```text
search_skill({ query: "help me debug a memory leak" })
```

Each result line shows the skill's **name**, its **directory name** in parentheses, an optional **`[+resources]`** marker, and the description:

```text
Found 12 skills matching "react patterns":

- **react-patterns** (react-patterns) [+resources] — Composition, hooks, and render patterns for React apps.
- **react-performance** (react-performance) — Profiling and reducing unnecessary re-renders.
- **state-management** (state-management) — Choosing and structuring client state.
…
```

:::tip
The **`[+resources]`** marker means the skill ships extra `resources/*.md` files beyond its main document. You can pull those in too with `include_resources: true` when you load it — see below.
:::

If nothing clears the relevance threshold, you get back a plain `No skills found matching "<query>".` — try broadening the query or running `list_categories` to find the right area first.

## `load_skill`

Loads the full content of a single skill. This is what actually brings the skill's instructions into your assistant's context.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `name` | `string` | **Yes** | — | The skill's frontmatter `name` *or* its directory name. Case-insensitive. |
| `include_resources` | `boolean` | No | `false` | When `true`, appends the skill's `resources/*.md` files to the returned content. |

Load just the main skill document:

```text
load_skill({ name: "react-patterns" })
```

Load it together with its resource files:

```text
load_skill({ name: "react-patterns", include_resources: true })
```

The `name` accepts either form shown by `search_skill` — the human-readable frontmatter name or the directory name — and matching is case-insensitive, so `React-Patterns` and `react-patterns` both work.

:::caution
`include_resources` defaults to `false`. Leave it off for a quick read of the core skill; turn it on only when you want the full deep-dive, since resource files add to what's loaded into context.
:::

### When a name doesn't match

If `load_skill` can't find an exact match, it doesn't fail silently — it runs a fuzzy search and suggests the closest skills:

```text
load_skill({ name: "react pattern" })
→ Skill "react pattern" not found. Did you mean: react-patterns, react-performance, state-management?
```

Pick one of the suggestions and call `load_skill` again with that exact name.

## Next steps

- [Configuration](/skill-library-mcp/configuration/) — install scopes, the plugin-vs-server distinction, and the `include_resources` toggle.
- [Search and load a skill](/skill-library-mcp/examples/search-and-load/) — the full workflow end to end.
