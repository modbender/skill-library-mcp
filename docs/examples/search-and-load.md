---
title: Search and load a skill
description: An end-to-end walkthrough — browse categories, search for a skill, load it, and load it with its resource files.
sidebar:
  order: 1
---

This is the core loop of Skill Library MCP, start to finish: discover what's available, narrow to the skill you want, and load it. We'll show the underlying tool calls and the shape of what comes back so you can recognize each step.

In practice you describe the goal in plain language and your assistant runs these calls for you — but seeing the raw inputs and outputs makes the workflow click.

## 1. Discover what's available

Start with `list_categories` when you're not sure what the library covers. It takes no parameters:

```text
list_categories()
```

It returns the total skill count and every category with examples:

```text
15223 skills in 13 categories:

- **Frontend** (…) — react-patterns, tailwind-layouts, accessibility-audit, +… more
- **Backend** (…) — fastapi-service, graphql-schema, rest-api-design, +… more
- **AI & LLM** (…) — rag-implementation, agent-patterns, prompt-engineering, +… more
- **DevOps & Infra** (…) — terraform-modules, k8s-deploy, ci-pipeline, +… more
- **Testing** (…) — tdd-workflow, playwright-e2e, vitest-setup, +… more
…
```

Now you know roughly where your task lives — say, **Testing** — and you can search with confidence.

## 2. Search for a skill

Pass a keyword or a natural-language description to `search_skill`:

```text
search_skill({ query: "end to end browser tests with playwright" })
```

You get back a ranked list. Each line shows the skill's **name**, its **directory name** in parentheses, an optional **`[+resources]`** marker, and a description:

```text
Found 8 skills matching "end to end browser tests with playwright":

- **playwright-e2e** (playwright-e2e) [+resources] — Writing reliable end-to-end browser tests with Playwright.
- **tdd-workflow** (tdd-workflow) — Red-green-refactor discipline for new features.
- **vitest-setup** (vitest-setup) — Configuring Vitest for unit and component tests.
…
```

The top hit, `playwright-e2e`, is what we want — and the `[+resources]` marker tells us it ships extra material we can optionally pull in.

:::tip
Search is IDF-weighted, so distinctive terms rank higher. A natural-language query like *"help me debug a memory leak"* works just as well as bare keywords — you don't need to guess the exact skill name.
:::

## 3. Load the skill

Load the skill by the name (or directory name) from the search results. Matching is case-insensitive:

```text
load_skill({ name: "playwright-e2e" })
```

This returns the full `SKILL.md` content — the complete instruction document, ready for your assistant to apply:

```text
---
name: playwright-e2e
description: Writing reliable end-to-end browser tests with Playwright.
---

# Playwright End-to-End Testing

## When to use this
…full skill instructions follow…
```

That's the loop. For most tasks, the main skill document is all you need.

## 4. Load with resources

When a skill is marked `[+resources]` and you want the deep-dive, set `include_resources: true`. The server appends the skill's `resources/*.md` files to the returned content:

```text
load_skill({ name: "playwright-e2e", include_resources: true })
```

```text
---
name: playwright-e2e
description: Writing reliable end-to-end browser tests with Playwright.
---

# Playwright End-to-End Testing
…main skill content…

# Resource: selectors-cheatsheet
…appended resource file…

# Resource: ci-integration
…appended resource file…
```

:::caution
`include_resources` defaults to `false`. Turn it on only when you actually want the extra material — resource files add to what's loaded into your context window, which is the very thing this server exists to keep lean.
:::

## When the name doesn't match

If you load a skill by a slightly wrong name, `load_skill` runs a fuzzy search and suggests the closest matches instead of erroring out:

```text
load_skill({ name: "playwright tests" })
→ Skill "playwright tests" not found. Did you mean: playwright-e2e, tdd-workflow, vitest-setup?
```

Re-run `load_skill` with one of the suggested exact names and you're back on track.

## Next steps

- [MCP client setup](/skill-library-mcp/examples/mcp-client-setup/) — wire the server into Claude Code and verify the tools.
- [Usage](/skill-library-mcp/usage/) — the full parameter reference for all three tools.
