---
name: ralstp-consultant
description: Analyze problems using RALSTP (Recursive Agents and Landmarks Strategic-Tactical Planning). Based on PhD thesis by Dorian Buksz (RALSTP). Identifies agents, calculates difficulty, and suggests decomposition.
---

# RALSTP Consultant

Based on **"Recursive Agents and Landmarks Strategic-Tactical Planning (RALSTP)"** by Dorian Buksz, King's College London, 2024.

## Core Concepts (from the thesis)

### 1. Agents Identification

**Definition:** Agents are objects with **dynamic types** that are active during goal state search.

**How to identify:**
- Dynamic type = appears as first argument of a predicate in any action's **effects**
- Static type = never appears in action effects
- Example: In Driverlog, `truck` and `driver` are dynamic (they're in `drive` action effects), but `location` is static

**Real PDDL Example (RTAM Domain):**
```pddl
(:types  
   ambulance police_car tow_truck fire_brigade - vehicle
   acc_victim vehicle car - subject
   ...
)
```
- **Agents:** ambulance, police_car, tow_truck, fire_brigade (appear in action effects like `at`, `available`, `busy`)
- **Passive:** acc_victim, car (acted upon but don't act)

### 2. Passive Objects

Objects that are NOT agents — things being acted upon but don't act themselves.
- Packages, cargo, data, files, victims in RTAM

### 3. Agent Dependencies

**Definition:** Relationships between agents based on what preconditions they satisfy for other agents.

**Types:**
- **Independent** — agents that don't depend on each other
- **Dependent** — agents that need other agents' preconditions satisfied
- **Conflicting** — agents that interfere with each other

### 4. Entanglement

**Definition:** When agents fight for shared resources (time, space, locations, etc.)

**Measurement:**
- Count of shared predicates
- Conflict frequency in goal states

**Real PDDL Example (RTAM - Road Traffic Accident):**
```pddl
(:durative-action confirm_accident
   :parameters (?V - police_car ?P - subject ?A - accident_location)
   :condition (and (at start (at ?V ?A)) (at start (at ?P ?A)) ...)
   :effect (and (at end (certified ?P)) ...)
)

(:durative-action untrap
   :parameters (?V - fire_brigade ?P - acc_victim ?A - accident_location)
   :condition (and (at start (certified ?P)) (at start (available ?V)) ...)
)
```
- **Entanglement:** `police_car` must certify BEFORE `fire_brigade` can untrap
- **Resource conflict:** Both need to be at same `accident_location`
- **Availability:** `fire_brigade` busy during untrap → others must wait

### 5. Landmarks

**Definition:** Facts that **must be true** in any valid plan (from goals back to initial state).

**Types:**
- **Fact landmarks** — propositions that must hold
- **Action landmarks** — actions that must be executed
- **Relaxed landmarks** — landmarks considering only positive effects (ignoring deletes)

**Real PDDL Example (RTAM - sequential dependencies):**
```
Goal: (delivered victim1) ∧ (delivered car1)

Required sequence of fact landmarks:
1. (certified victim1)     ← police must confirm
2. (untrapped victim1)     ← fire must free them
3. (aided victim1)         ← ambulance must treat
4. (loaded victim1 ambulance) ← ambulance must load
5. (at victim1 hospital)   ← deliver to hospital
6. (delivered victim1)     ← FINAL

Action landmarks:
- confirm_accident → untrap → first_aid → load_victim → unload_victim → deliver_victim
```

### 6. Strategic vs Tactical

- **Strategic:** Abstract planning level. Solve "what needs to happen first" ignoring details.
- **Tactical:** Detailed execution level. Solve "exactly how to do it".

### 7. Difficulty Metrics

From the thesis, difficulty increases with:
- More agents in goal state
- More entangled agents (conflicting dependencies)
- More inactive dynamic objects not in goal

**Buksz Complexity Score ≈ Agent Count × Entanglement Factor**

## Implementation Note (Natural Language vs PDDL)

This skill operates in two modes:

1.  **Conceptual Mode (Default):** Uses the LLM to apply RALSTP methodology to **natural language** problems (e.g., "Plan a marketing launch"). No PDDL files are required. The agent identifies Agents/Landmarks conceptually.
2.  **Formal Mode (Optional):** If you provide PDDL domain/problem files, the included `scripts/analyze.py` can be run to mathematically extract agents and landmarks.

*The instructions below apply to both modes, but "Real PDDL Examples" are provided for technical context.*

## Usage

For any complex problem, just describe it and I'll apply RALSTP:

```
RALSTP analyze: I need to migrate 1000 VMs from datacentre A to B with minimal downtime
```

## Output Format

```
## RALSTP Analysis

### Agents Identified
- [list agents and their types]

### Passive Objects  
- [list objects being acted upon]

### Dependency Graph
- [which agents depend on which]

### Difficulty Assessment
- Agent Count: X
- Entanglement: Low/Medium/High
- Estimated Complexity: [score]

### Strategic Phase
- [high-level plan ignoring details]

### Tactical Phase
- [detailed execution]

### Decomposition Suggestion
- Split by: [agent type / landmark / location]
- Parallelize: [what can run concurrently]
- Risks: [potential conflicts/entanglements]
```

## When to Use

**USE for:**
- Multi-step workflows with multiple actors
- Migration/tasks with dependencies
- Resource contention problems
- Complex orchestrations

**SKIP for:**
- Simple Q&A
- Single-task problems

## Reference

PhD Thesis: "Recursive Agents and Landmarks Strategic-Tactical Planning (RALSTP)" — Dorian Buksz, King's College London, 2024.

## Example: RTAM Domain (IPC-2014)

**Domain:** Road Traffic Accident Management

**Source:** https://github.com/potassco/pddl-instances/tree/master/ipc-2014/domains/road-traffic-accident-management-temporal-satisficing

### Full Analysis

**Agents (4):**
- `ambulance` — transports victims to hospital
- `police_car` — certifies accident/victims
- `tow_truck` — recovers vehicles
- `fire_brigade` — untraps victims, extinguishes fires

**Passive Objects:**
- `acc_victim` — people needing help
- `car` — vehicles involved in accident
- `accident_location`, `hospital`, `garage`

**Dependencies (Critical Path):**
```
police_car → fire_brigade → ambulance → hospital
     ↓            ↓           ↓
  certify      untrap       deliver
```

**Landmarks Chain (must execute in order):**
1. `confirm_accident` (police at scene)
2. `untrap` (fire frees victim)
3. `first_aid` (ambulance treats)
4. `load_victim` → `unload_victim` → `deliver_victim`
5. `load_car` → `unload_car` → `deliver_vehicle`

**Entanglement:**
- Multiple vehicles must be at same location (accident scene)
- Vehicles have limited availability (busy during actions)
- Sequence constraints: can't deliver before certify

**Difficulty:** High — 4 agents, tight dependencies, shared locations

