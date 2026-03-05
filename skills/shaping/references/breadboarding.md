# Breadboarding Reference

Transform workflow descriptions into affordance tables showing UI and Code affordances with their wiring.

## Table of Contents

1. Core Concepts (Places, Affordances, Wiring)
2. Affordance Tables Format
3. Procedure: Mapping Existing System
4. Procedure: Designing from Shaped Parts
5. Places Deep Dive
6. Verification Checks
7. Mermaid Visualization
8. Chunking
9. Slicing

## Core Concepts

### Places

A Place is a bounded context of interaction. While in a Place, you have specific affordances and cannot interact outside that boundary.

**Blocking Test**: Can you interact with what's behind? No → different Place. Yes → same Place.

| UI Element | Place? | Why |
|------------|--------|-----|
| Modal | Yes | Can't interact with page behind |
| Edit mode (whole screen) | Yes | All affordances changed |
| Dropdown menu | No | Can click away |
| Checkbox reveals fields | No | Surroundings unchanged |

### Place IDs

| # | Place | Description |
|---|-------|-------------|
| P1 | Page Name | Standard page |
| P2 | Page (Edit Mode) | Mode variant |
| P2.1 | widget-name | Subplace within P2 |
| P3 | Modal Name | Modal dialog |

### Affordances

- **UI (U)**: inputs, buttons, displays, scroll regions
- **Code (N)**: methods, subscriptions, stores, framework mechanisms
- **Data Store (S)**: state that persists and is read/written

### Wiring

- **Wires Out** (solid →): Control flow — calls, triggers, writes, navigation
- **Returns To** (dashed -.->): Data flow — return values, reads

Navigate to Places, not affordances inside: `N1 → P2` not `N1 → U3`.

## Affordance Tables

### UI Affordances

| # | Place | Component | Affordance | Control | Wires Out | Returns To |
|---|-------|-----------|------------|---------|-----------|------------|
| U1 | P1 | search | search input | type | → N1 | — |
| U2 | P1 | search | loading spinner | render | — | — |

### Code Affordances

| # | Place | Component | Affordance | Control | Wires Out | Returns To |
|---|-------|-----------|------------|---------|-----------|------------|
| N1 | P1 | search | activeQuery.next() | call | → N2 | — |
| N2 | P1 | search | performSearch() | call | → N3, → S1 | — |

### Data Stores

| # | Place | Store | Description |
|---|-------|-------|-------------|
| S1 | P1 | results | Array of search results |

### Controls

click, type, call, observe, write, render, config, conditional, signal

## Procedure: Mapping Existing System

1. Identify the flow to analyze (specific user journey)
2. List all places involved
3. Trace through code to find components
4. For each component, list affordances
5. Name the actual thing (never abstractions)
6. Fill Control, Wires Out, Returns To
7. Add data stores and framework mechanisms
8. Verify against code

## Procedure: Designing from Shaped Parts

1. List each part from shape
2. Translate parts into affordances (UI + Code)
3. Verify every U has a supporting N
4. Classify places as existing or new
5. Wire affordances (Wires Out + Returns To)
6. Connect to existing system if applicable
7. Check completeness

## Key Principles

- **Tables are truth** — Mermaid diagrams are optional visualizations
- **Never use memory** — scan Wires Out column systematically
- **Every affordance name must exist** (when mapping) — point to real code
- **Mechanisms aren't affordances** — skip wrappers, transforms, navigation utilities
- **Every U displaying data needs a source** (S or N returning to it)
- **Every N must connect** — handlers need Wires Out, queries need Returns To
- **Side effects need stores** — Browser URL, localStorage, Clipboard as external stores
- **Place stores where consumed**, not where written

### Not Affordances

| Type | Example | Why |
|------|---------|-----|
| Visual containers | modal-frame | Can't act on a wrapper |
| Internal transforms | dataTransform() | Implementation detail |
| Navigation mechanisms | modalService.open() | Just "how" of getting somewhere |

Wire directly to destination instead.

## Place References

When nested place is complex, detach it:
1. Put reference node in parent: `_letter-browser`
2. Define full place separately
3. Wire: `_letter-browser --> letter-browser`

Style with dashed border: `stroke-dasharray:5 5`

## Modes as Places

Edit mode transforms entire screen → separate Places. Use place reference to show composition:
```
P3: component (Read) — base state
P4: component (Edit) — contains _component (Read) + new affordances
```

## Subplaces

Hierarchical IDs: P2.1, P2.2 for subsets within P2. Use placeholder for out-of-scope content:
```
otherContent[["... other page content ..."]]
```

## Verification Checks

| Check | Question |
|-------|----------|
| Every U displaying data | Has incoming wire? |
| Every N | Has Wires Out or Returns To? |
| Every S | Something reads from it? |
| Navigation mechanisms | Wire to Place directly? |
| N with side effects | External store modeled? |

## Chunking

Collapse subsystem with one wire in, one wire out, many internals into single node.

Stadium-shaped node: `dynamicForm[["CHUNK: dynamic-form"]]`
Separate detail diagram with boundary markers: `input([formDefinition])`, `output(["valid$"])`

## Mermaid Conventions

### Line Styles

| Style | Syntax | Use |
|-------|--------|-----|
| Solid | `-->` | Wires Out |
| Dashed | `-.->` | Returns To |
| Labeled | `-.->|...|` | Abbreviated flow |

### Colors

| Type | Color | Hex |
|------|-------|-----|
| UI (U) | Pink | `#ffb6c1` |
| Code (N) | Grey | `#d3d3d3` |
| Store (S) | Lavender | `#e6e6fa` |
| Chunk | Light blue | `#b3e5fc` |

```
classDef ui fill:#ffb6c1,stroke:#d87093,color:#000
classDef nonui fill:#d3d3d3,stroke:#808080,color:#000
classDef store fill:#e6e6fa,stroke:#9370db,color:#000
```

### Subgraph IDs

Use Place ID as subgraph ID: `subgraph P1["P1: Page Name"]`

## Slicing

Break breadboard into vertical implementation increments.

### Rules

- Every slice must have **demo-able UI** (no horizontal layers)
- Max 9 slices
- Each demonstrates a mechanism working

### Procedure

1. Identify minimal demo-able increment → V1
2. Layer capabilities as slices (each demonstrates a mechanism)
3. Assign affordances to slices
4. Create per-slice affordance tables
5. Write demo statement for each slice

### Slice Summary Format

| # | Slice | Mechanism | Affordances | Demo |
|---|-------|-----------|-------------|------|
| V1 | Widget with data | F1, F4 | U2-U5, N3-N8 | "Shows real data" |
| V2 | Search works | F3 | U1, N1, N2 | "Type to filter" |

### Visualizing Slices

| Category | Style |
|----------|-------|
| This slice | Bright color |
| Already built | Solid grey |
| Future | Transparent, dashed |

Slice colors: V1 `#e8f5e9` green, V2 `#e3f2fd` blue, V3 `#fff3e0` orange, V4 `#f3e5f5` purple, V5 `#fff8e1` yellow, V6 `#fce4ec` pink

### Sliced Breadboard

Wrap affordances in colored slice subgraphs. Use invisible links for ordering: `slice1 ~~~ slice2`. Make nested subgraphs transparent.
