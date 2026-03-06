# Worked Example 2 — Mall Simulation Tick

Goal: a mall "world tick" that updates zones, cloud pressure, NPC drift, and discoveries.

## Primitive Map

| Primitive | Instance |
|-----------|----------|
| **LOOP** | sim tick @ 10Hz (budgeted) |
| **TILEGRID** | zones + adjacency graph (zone cells) |
| **CONTROLBLOCK** | ZoneCB, CloudCB, NPC_CB |
| **POOL** | NPCPool (256), ArtifactPool (1024), EventPool (4096) |
| **EVENT** | EnterZone, Interact, Contradiction, Discovery |
| **DISPATCHER** | budgeted scheduler (some systems can skip if over budget) |

## CONTROLBLOCKs (minimum fields)

**CloudCB**
- level (0..100)
- mood_id
- drift
- last_event_tick
- budget_ms

**ZoneCB**
- zone_id
- turbulence
- resonance
- qbit_aggregate (optional)
- occupant_count

**NPC_CB**
- npc_id
- zone_id
- state_id
- intent
- never_rule_mask
- contradiction_threshold

## LOOP Pseudocode (budgeted)

```
LOOP tick(dt):
    DISPATCHER.budget_start(CloudCB.budget_ms)

    DISPATCHER.run(System_UpdateCloud)       # CloudCB
    DISPATCHER.run(System_UpdateZones)       # ZoneCB from CloudCB + events
    DISPATCHER.run(System_NPC_Intents)       # writes NPC_CB.intent
    DISPATCHER.run(System_NPC_Move)          # zone transitions emit EnterZone
    DISPATCHER.run(System_Interactions)      # emits Interact/Discovery
    DISPATCHER.run(System_Contradictions)    # emits Contradiction when thresholds crossed
    DISPATCHER.run(System_ApplyEvents)       # authoritative state changes
    DISPATCHER.run(System_Cleanup)           # pool housekeeping

    DISPATCHER.budget_end()
```

## Portability Notes

| Platform | Translation |
|----------|-------------|
| **Edge** | DISPATCHER can skip lower-priority systems if budget exceeded |
| **GPU** | zone updates and NPC move scoring can batch; EVENTS as append streams |
| **ECS** | Zones are entities; adjacency is TILEGRID; cloud is singleton CONTROLBLOCK |

---

# Deep Dive: Full Implementation

The sections below show complete TypeScript/QBIT implementations.

```typescript
// Zone as spatial partition
interface Zone {
    id: string;
    name: string;
    type: 'STORE' | 'CORRIDOR' | 'FOOD_COURT' | 'ANCHOR' | 'UTILITY';
    
    // TILEGRID: Bounds in tile coordinates
    bounds: {
        min_x: number;
        min_y: number;
        max_x: number;
        max_y: number;
    };
    
    // Zone properties
    capacity: number;           // Max NPCs
    current_occupancy: number;  // Current count
    vibe_vector: VibeVector;    // Aesthetic state
    
    // Connections to adjacent zones
    exits: Exit[];
    
    // Zone-specific behavior
    behavior_type: ZoneBehavior;
}

// NPC as CONTROLBLOCK with QBIT state
interface MallNPC {
    id: string;
    active: boolean;
    
    // Position
    zone_id: string;
    x: number;
    y: number;
    
    // QBIT behavioral state (8 axes)
    qbit: {
        energy: number;      // -1 (exhausted) to +1 (energetic)
        social: number;      // -1 (avoidant) to +1 (seeking)
        purpose: number;     // -1 (browsing) to +1 (mission)
        wealth: number;      // -1 (broke) to +1 (spending)
        patience: number;    // -1 (frustrated) to +1 (relaxed)
        conformity: number;  // -1 (rebel) to +1 (follower)
        nostalgia: number;   // -1 (modern) to +1 (retro)
        hunger: number;      // -1 (full) to +1 (hungry)
    };
    
    // Behavior state machine
    state: 'WALKING' | 'BROWSING' | 'PURCHASING' | 'EATING' | 'RESTING' | 'LEAVING';
    state_timer: number;
    
    // Target
    destination_zone: string | null;
    path: string[];  // Zone IDs to traverse
}
```

## Zone Pool Management (POOL)

```typescript
// Pre-allocated NPC pool
const MAX_NPCS = 500;
const npcPool: MallNPC[] = [];

// Per-zone occupancy tracking (no per-frame allocation)
const zoneOccupancy: Map<string, MallNPC[]> = new Map();

function initMallPools(zones: Zone[]) {
    // Initialize NPC pool
    for (let i = 0; i < MAX_NPCS; i++) {
        npcPool.push(createEmptyNPC(i));
    }
    
    // Initialize zone occupancy maps
    for (const zone of zones) {
        zoneOccupancy.set(zone.id, []);
    }
}

function spawnNPC(zone: Zone, qbit: QBITState): MallNPC | null {
    // Check zone capacity
    const occupants = zoneOccupancy.get(zone.id)!;
    if (occupants.length >= zone.capacity) {
        return null;  // Zone full
    }
    
    // Find inactive slot in pool
    for (const npc of npcPool) {
        if (!npc.active) {
            npc.active = true;
            npc.zone_id = zone.id;
            npc.qbit = { ...qbit };
            npc.state = 'WALKING';
            
            // Add to zone tracking
            occupants.push(npc);
            zone.current_occupancy++;
            
            return npc;
        }
    }
    return null;  // Global pool exhausted
}
```

## Zone Event System (EVENT)

```typescript
// Zone-level flags (polled each tick)
interface ZoneFlags {
    overcrowded: boolean;      // occupancy > 80% capacity
    vibe_shifted: boolean;     // Significant vibe change
    incident_active: boolean;  // Security event
    anchor_effect: boolean;    // Adjacent to anchor store
}

// Mall-level events (propagate across zones)
interface MallEvents {
    time_of_day: 'MORNING' | 'LUNCH' | 'AFTERNOON' | 'EVENING' | 'CLOSING';
    day_of_week: 'WEEKDAY' | 'WEEKEND';
    special_event: string | null;  // "SALE", "HOLIDAY", etc.
    security_level: number;        // 0-100
}

// Calculate zone flags from state
function computeZoneFlags(zone: Zone): ZoneFlags {
    const occupancy_pct = zone.current_occupancy / zone.capacity;
    
    return {
        overcrowded: occupancy_pct > 0.8,
        vibe_shifted: zone.vibe_vector.delta > VIBE_THRESHOLD,
        incident_active: false,  // Set by security system
        anchor_effect: zone.exits.some(e => 
            getZone(e.target_zone)?.type === 'ANCHOR'
        )
    };
}
```

## Zone Tick Dispatcher (DISPATCHER + LOOP)

```typescript
// Main simulation tick (runs at 10Hz for large-scale sim)
function mallSimTick(dt: number) {
    // PHASE 1: Gather global inputs
    updateTimeOfDay();
    const mallEvents = computeMallEvents();
    
    // PHASE 2: Update each zone
    for (const zone of zones) {
        zoneUpdate(zone, mallEvents, dt);
    }
    
    // PHASE 3: Process zone transitions (NPCs moving between zones)
    processZoneTransitions();
    
    // PHASE 4: Propagate events
    propagateZoneEvents();
}

function zoneUpdate(zone: Zone, events: MallEvents, dt: number) {
    const flags = computeZoneFlags(zone);
    const occupants = zoneOccupancy.get(zone.id)!;
    
    // Update each NPC in zone
    for (const npc of occupants) {
        if (!npc.active) continue;
        
        // QBIT behavioral step
        updateNPCQBIT(npc, zone, flags, events, dt);
        
        // State machine (mini-DISPATCHER)
        switch (npc.state) {
            case 'WALKING':
                moveNPCTowardDestination(npc, dt);
                if (atDestination(npc)) {
                    npc.state = decideNextState(npc, zone);
                }
                break;
                
            case 'BROWSING':
                npc.state_timer -= dt;
                // QBIT influence: low patience = shorter browse
                const patience_mod = (1 + npc.qbit.patience) / 2;
                if (npc.state_timer <= 0) {
                    if (npc.qbit.wealth > 0.3 && Math.random() < 0.3) {
                        npc.state = 'PURCHASING';
                    } else {
                        npc.state = 'WALKING';
                        npc.destination_zone = pickNextZone(npc);
                    }
                }
                break;
                
            case 'PURCHASING':
                npc.state_timer -= dt;
                if (npc.state_timer <= 0) {
                    npc.qbit.wealth -= 0.2;  // Spent money
                    npc.qbit.purpose -= 0.1; // Completed goal
                    npc.state = 'WALKING';
                }
                break;
                
            case 'EATING':
                npc.state_timer -= dt;
                if (npc.state_timer <= 0) {
                    npc.qbit.hunger = -0.8;  // Full
                    npc.qbit.energy += 0.3;  // Restored
                    npc.state = 'WALKING';
                }
                break;
                
            case 'RESTING':
                npc.qbit.energy += 0.1 * dt;
                npc.qbit.patience += 0.05 * dt;
                if (npc.qbit.energy > 0.5) {
                    npc.state = 'WALKING';
                }
                break;
                
            case 'LEAVING':
                moveNPCTowardExit(npc, dt);
                if (atMallExit(npc)) {
                    despawnNPC(npc, zone);
                }
                break;
        }
    }
    
    // Update zone vibe from aggregate NPC state
    updateZoneVibe(zone, occupants);
}
```

## QBIT Behavioral Update

```typescript
// QBIT step: environment → NPC state
function updateNPCQBIT(
    npc: MallNPC,
    zone: Zone,
    flags: ZoneFlags,
    events: MallEvents,
    dt: number
) {
    // Environmental pressure
    if (flags.overcrowded) {
        npc.qbit.patience -= 0.02 * dt;
        npc.qbit.social -= 0.01 * dt;
    }
    
    // Zone vibe influence (NPCs absorb zone aesthetic)
    const vibe = zone.vibe_vector;
    npc.qbit.energy += vibe.energy_mod * 0.01 * dt;
    npc.qbit.nostalgia += vibe.nostalgia_mod * 0.01 * dt;
    
    // Time pressure
    if (events.time_of_day === 'CLOSING') {
        npc.qbit.purpose += 0.1 * dt;  // Urgency
    }
    
    // Hunger drift (always increasing)
    npc.qbit.hunger += 0.005 * dt;
    
    // Energy drift (decreasing while active)
    if (npc.state !== 'RESTING') {
        npc.qbit.energy -= 0.003 * dt;
    }
    
    // Decision triggers (QBIT → state change)
    if (npc.qbit.hunger > 0.7 && zone.type !== 'FOOD_COURT') {
        npc.destination_zone = findNearestFoodCourt(npc);
        npc.state = 'WALKING';
    }
    
    if (npc.qbit.energy < -0.5) {
        npc.state = 'RESTING';
    }
    
    if (npc.qbit.patience < -0.8) {
        npc.state = 'LEAVING';
    }
    
    // Clamp all values to [-1, 1]
    for (const key of Object.keys(npc.qbit)) {
        npc.qbit[key] = Math.max(-1, Math.min(1, npc.qbit[key]));
    }
}
```

## Zone Vibe Aggregation

```typescript
// Zone vibe emerges from aggregate NPC state
function updateZoneVibe(zone: Zone, occupants: MallNPC[]) {
    if (occupants.length === 0) {
        // Empty zone: decay toward neutral
        zone.vibe_vector.energy_mod *= 0.95;
        return;
    }
    
    // Aggregate QBIT axes
    let total_energy = 0;
    let total_social = 0;
    let total_nostalgia = 0;
    
    for (const npc of occupants) {
        if (!npc.active) continue;
        total_energy += npc.qbit.energy;
        total_social += npc.qbit.social;
        total_nostalgia += npc.qbit.nostalgia;
    }
    
    const n = occupants.length;
    const avg_energy = total_energy / n;
    const avg_social = total_social / n;
    const avg_nostalgia = total_nostalgia / n;
    
    // Blend toward aggregate (zone has inertia)
    zone.vibe_vector.energy_mod = 
        zone.vibe_vector.energy_mod * 0.9 + avg_energy * 0.1;
    zone.vibe_vector.social_mod = 
        zone.vibe_vector.social_mod * 0.9 + avg_social * 0.1;
    zone.vibe_vector.nostalgia_mod = 
        zone.vibe_vector.nostalgia_mod * 0.9 + avg_nostalgia * 0.1;
    
    // Check for significant vibe shift (triggers EVENT)
    const delta = Math.abs(avg_energy - zone.vibe_vector.energy_mod);
    zone.vibe_vector.delta = delta;
}
```

## Primitive Count

| Primitive | Instances |
|-----------|-----------|
| LOOP | 1 (mall sim @ 10Hz) |
| TILEGRID | ~100 (zone bounds) |
| CONTROLBLOCK | 2 (Zone, MallNPC) |
| POOL | 1 (npcPool: 500 NPCs) |
| EVENT | 2 (ZoneFlags, MallEvents) |
| DISPATCHER | 2 (mallSimTick phases, NPC state machine) |

## Key Insights

1. **Spatial partitioning (TILEGRID) enables parallel zone updates** — each zone is independent within a tick.

2. **QBIT is a CONTROLBLOCK extension** — fixed axes, bounded values, predictable updates.

3. **Zone vibe is emergent EVENT** — aggregated from individual NPC state, triggers zone-level behaviors.

4. **Capacity limits via POOL** — both per-zone and global; graceful degradation when full.

5. **Nested DISPATCHERs** — Mall tick → Zone update → NPC state machine.
