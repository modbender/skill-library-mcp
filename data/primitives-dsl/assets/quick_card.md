# PRIMITIVES DSL — QUICK CARD (v1)

Six primitives that keep your architecture portable across eras.

---

## 1) LOOP

**Purpose:** Owns time and ordering.
**Questions it answers:** "When do things happen? In what sequence? At what rate?"

**Common forms:**
- fixed-step tick (simulation) + variable render
- budgeted tick (edge devices)
- multi-rate loop (AI slower than physics)

**Minimum spec:**
- phases: INPUT → SIM → AI → EVENTS → RENDER → HOUSEKEEPING
- tick rate and budgets declared

---

## 2) TILEGRID

**Purpose:** Stable spatial index + adjacency.
**Questions:** "Where is it? What is nearby? What can connect?"

**Common forms:**
- 2D tile map, 3D voxel chunks, zone graph, navmesh cells

**Minimum spec:**
- coordinate system + adjacency rule
- lookup: cell(x,y,…) → occupancy / tags / links

---

## 3) CONTROLBLOCK

**Purpose:** Authoritative compact state record.
**Questions:** "What is true right now? What's the mode? What's locked?"

**Common forms:**
- entity state struct, job descriptor, DMA control block, ECS component bundle

**Minimum spec:**
- fields list (flags/counters/handles/timers)
- ownership: who writes it vs reads it

---

## 4) POOL

**Purpose:** Bounded allocation + reuse.
**Questions:** "How many of these can exist? What happens at limit?"

**Common forms:**
- entity pool, bullet pool, job pool, audio voice pool, packet pool

**Minimum spec:**
- capacity number
- overflow policy: drop / recycle / backpressure

---

## 5) EVENT

**Purpose:** Minimal message that something happened.
**Questions:** "What changed? Who should care? How do we avoid tight coupling?"

**Common forms:**
- ring-buffer event stream, pub/sub topic, command queue, RPC-ish packets

**Minimum spec:**
- type
- routing key/channel
- payload (small)
- timestamp or tick index

---

## 6) DISPATCHER

**Purpose:** Routes events + schedules work.
**Questions:** "Who handles what? With what priority? On what compute?"

**Common forms:**
- system scheduler, job graph executor, SPU task launcher, GPU kernel launcher

**Minimum spec:**
- handler map: event type → handler
- policy: FIFO / priority / budgeted / deterministic
- concurrency model: single-thread / worker pool / heterogeneous

---

## Pattern Mantra

**State lives in CONTROLBLOCKS.**
**Things live in POOLS.**
**Changes move as EVENTS.**
**DISPATCHER decides where work runs.**
**LOOP decides when work runs.**
**TILEGRID makes "nearby" cheap.**

---

## Physics Mapping (why these six)

| Primitive | Maps To |
|-----------|---------|
| LOOP | Time (causality) |
| TILEGRID | Space (geometry) |
| CONTROLBLOCK | Entity (conservation) |
| POOL | Resources (thermodynamics) |
| EVENT | Change (information) |
| DISPATCHER | Control (causality) |

> "These patterns emerged independently on three architectures because they map to physics, not design trends."
