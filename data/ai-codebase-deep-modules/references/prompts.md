# Copy‑paste prompts for architecture work

These prompts are designed to be pasted into any agent chat.

## THE EXACT PROMPT — Build a module map

> Read this repository and produce a “Module Map” that matches how the product behaves.
> - Group code into 3–10 domains/features/services.
> - For each module: responsibilities, entrypoints, key data types, and current coupling risks.
> - Identify cross-import cycles and “junk drawer” directories (utils/shared/helpers).
> - Output a table and a short narrative summary.

## THE EXACT PROMPT — Specify a deep module interface

> For the module **{module-name}**, design a small public interface:
> - List the 3–12 exported functions/types.
> - Define inputs/outputs and error semantics.
> - Provide 2 examples (happy path + one edge case).
> - Define what is explicitly internal.
> Keep the interface boring and stable.

## THE EXACT PROMPT — Plan an incremental refactor (strangler)

> Create an incremental refactor plan to introduce deep modules without a rewrite:
> 1) Create module folders + public entrypoints.
> 2) Add contract tests at the boundaries.
> 3) Wrap existing code behind the new interfaces until tests pass.
> 4) Move internals behind `internal/` gradually.
> 5) Add boundary enforcement (lint/arch tests).
> Include checkpoints and rollback strategy.

## THE EXACT PROMPT — Boundary enforcement options

> Given this repo’s language/tooling, propose the lightest boundary enforcement that prevents:
> - imports from `**/internal/**`
> - cross-domain imports that bypass module entrypoints
> Include exact config snippets for lint rules and/or architecture tests.

## THE EXACT PROMPT — Review this plan for realism

> Review this architecture plan as a senior engineer.
> - What is risky or ambiguous?
> - What hidden dependencies might break?
> - Are the modules too shallow or too broad?
> - Where should we add contract tests first?
> Propose a revised plan that is safer and more incremental.
