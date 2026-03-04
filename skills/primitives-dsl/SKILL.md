---
name: primitives-dsl
description: "Universal game architecture DSL with six primitives (LOOP, TILEGRID, CONTROLBLOCK, POOL, EVENT, DISPATCHER). Use when: (1) designing portable game/sim loops, (2) translating between architectures (68K ↔ Cell ↔ CUDA ↔ ECS), (3) explaining engine structure to AI agents, (4) refactoring chaos into explicit state + flow. Invocation produces: Primitive Map, Dataflow Sketch, Worked Example, Portability Notes."
---

# primitives-dsl — Universal Game Architecture Patterns

## What this skill does

Provides a small, portable DSL of **six universal primitives** that appear across 68K-era loops, Cell/PPU+SPU orchestration, CUDA/GPU kernels, and modern ECS engines.

Primitives: **LOOP** · **TILEGRID** · **CONTROLBLOCK** · **POOL** · **EVENT** · **DISPATCHER**

Use this skill to:
- Design a game/sim loop that ports cleanly across platforms
- Translate between architectures (68K ↔ Cell ↔ CUDA ↔ ECS)
- Explain engine structure to AI agents with minimal ambiguity
- Produce "worked examples" using the same primitive vocabulary every time

## When to use it

- Starting a new subsystem and want a portable mental model
- Refactoring chaos into explicit state + flow
- Mapping legacy code to modern patterns
- Designing constrained-device / edge / "shareware for the future" loops

## When NOT to use it

- Don't invent new primitives (keep the vocabulary stable)
- Don't debate engine religion (Unity vs Unreal vs custom). Translate, don't preach.
- Don't skip the concrete artifact: **every use must end in a diagram, table, or pseudocode**

## The DSL (definitions)

**LOOP**
A repeated update cycle with explicit phases. Owns time slicing and ordering.

**TILEGRID**
A spatial index with stable adjacency rules (2D/3D grids, nav tiles, zone cells, chunk maps).

**CONTROLBLOCK**
A compact, authoritative state record (flags, counters, handles, timers) used to coordinate behavior and enforce constraints.

**POOL**
A bounded allocator for frequently-created things (entities, bullets, particles, jobs). No unbounded `new` in hot paths.

**EVENT**
A structured message representing "something happened" with minimal payload and explicit routing metadata.

**DISPATCHER**
Routes work and events to handlers (CPU threads, SPUs, GPU kernels, ECS systems). Also where scheduling policy lives.

## Output contract (what you must produce)

When invoked, produce:

1. **Primitive Map** — Identify which parts of the system correspond to each primitive
2. **Dataflow Sketch** — Text diagram or table describing movement of state/events
3. **One Worked Example** — Or cite an existing example file
4. **Portability Notes** — How this maps to 68K / Cell / CUDA / ECS

## Invocation patterns (copy/paste prompts)

```
"Apply primitives-dsl to design a loop for ___ . Provide a Primitive Map + Dataflow + Portability."

"Translate this architecture into LOOP/TILEGRID/CONTROLBLOCK/POOL/EVENT/DISPATCHER."

"Given these constraints (___), propose a primitives-dsl design and a worked example."
```

## Guardrails / style rules

- Use primitive names in **ALL CAPS**
- Prefer **tables** over paragraphs for mappings
- Use **tight pseudocode** (no full implementations)
- Always name the CONTROLBLOCK fields explicitly
- Always specify POOL bounds (even if guessed)
- EVENTS must have a routing key or channel
- DISPATCHER must declare policy: FIFO, priority, fixed-step, budgeted, etc.

## References

- **Quick Card**: [`assets/quick_card.md`](assets/quick_card.md) — One-page reference
- **Architecture Mapping**: [`references/architecture_mapping.md`](references/architecture_mapping.md) — Platform translation table + full code examples
- **Worked Examples**:
  - [`references/example_shooter.md`](references/example_shooter.md) — Classic shooter loop
  - [`references/example_mall_tick.md`](references/example_mall_tick.md) — GLITCHDEXMALL zone sim
  - [`references/example_npc_step.md`](references/example_npc_step.md) — NPC state machine step

## External Resources

- [Anthropic Skills Repository](https://github.com/anthropics/skills) — Skill creation patterns
- [Alien Bash II](https://github.com/) — 68K source extraction (Glenn Cumming, open domain)
- NVIDIA CUDA Programming Guide — Modern GPU primitive patterns
- Cell Broadband Engine Programming Handbook — SPE work distribution
