# Worked Example 3 — NPC "One Step"

Goal: a single NPC update step that respects constraints ("never rules") and produces events.

## Primitive Map

| Primitive | Instance |
|-----------|----------|
| **LOOP** | called inside world tick (per NPC or batched) |
| **TILEGRID** | zone adjacency + local tags (liminal/hot/forbidden) |
| **CONTROLBLOCK** | NPC_CB + LocalPerceptionCB |
| **POOL** | EventPool |
| **EVENT** | SpeakLine, ChangeState, BreakRule, Flee |
| **DISPATCHER** | chooses handler by npc.state_id and conditions |

## CONTROLBLOCKs (minimum fields)

**NPC_CB**
- npc_id
- zone_id
- state_id
- intent
- stamina
- fear
- never_rule_mask
- contradiction_threshold
- last_spoke_tick

**LocalPerceptionCB**
- nearby_entities[]
- zone_tags
- cloud_level
- recent_events[]

## Step Pseudocode

```
NPC_STEP(npc, perception):
    
    # 1) Evaluate constraints
    if perception.cloud_level >= npc.contradiction_threshold:
        allow_breaks = true
    else:
        allow_breaks = false
    
    # 2) Decide intent (state machine)
    npc.intent = DISPATCHER.route(npc.state_id).decide(npc, perception)
    
    # 3) Enforce never-rules unless allowed_breaks
    if violates_never(npc.intent, npc.never_rule_mask) and not allow_breaks:
        npc.intent = sanitize_intent(npc.intent)  # downgrade: wait / pace / redirect
    
    # 4) Emit EVENTS from intent (no direct side-effects here)
    emit_events_from_intent(npc.intent, EventPool)
```

## Portability Notes

| Platform | Translation |
|----------|-------------|
| **CPU** | iterate NPCs; events in ring buffer |
| **GPU** | batch NPC_STEP; intent selection may be table-driven; events append |
| **ECS** | NPC_CB fields become components; DISPATCHER becomes reactive system |

---

# Deep Dive: Full Implementation

The sections below show complete TypeScript implementations with QBIT behavioral axes and wattitude bands. This forms the foundation for the `synthactor-blueprint` skill.

## The NPC CONTROLBLOCK

```typescript
// Full NPC state structure (Synthactor-lite)
interface NPC {
    // Identity (survives memory dump)
    id: string;
    name: string;
    archetype: 'CLERK' | 'SECURITY' | 'SHOPPER' | 'JANITOR' | 'GOTH';
    
    // Position
    x: number;
    y: number;
    facing: number;  // 0-7 (8-way direction)
    
    // QBIT behavioral axes (fixed 8 dimensions)
    qbit: {
        energy: number;      // -1 to +1
        social: number;      // -1 to +1
        purpose: number;     // -1 to +1
        patience: number;    // -1 to +1
        conformity: number;  // -1 to +1
        hostility: number;   // -1 to +1
        curiosity: number;   // -1 to +1
        fear: number;        // -1 to +1
    };
    
    // Wattitude (thermal pressure simulation)
    wattitude: number;  // 0-100 (COOL → WARM → HOT → CRITICAL)
    
    // State machine
    state: NPCState;
    state_timer: number;
    
    // Memory (can be dumped under pressure)
    memory: {
        last_seen_player: number;  // Timestamp
        known_threats: string[];   // Entity IDs
        destination: string | null;
        conversation_partner: string | null;
    };
    
    // Firmware layers (identity kernel)
    firmware: {
        primary: FirmwareType;    // Dominant behavior pattern
        secondary: FirmwareType;  // Fallback under stress
        terminal: FirmwareType;   // Survival mode
    };
}

type NPCState = 
    | 'IDLE'
    | 'PATROL'
    | 'INVESTIGATE'
    | 'CHASE'
    | 'ATTACK'
    | 'FLEE'
    | 'CONVERSE'
    | 'WORK'
    | 'REST';

type FirmwareType = 
    | 'CLERK_FIRMWARE'      // Customer service patterns
    | 'SECURITY_FIRMWARE'   // Threat assessment patterns
    | 'SHOPPER_FIRMWARE'    // Goal-seeking patterns
    | 'JANITOR_FIRMWARE'    // Maintenance patterns
    | 'GOTH_FIRMWARE';      // Existential patterns
```

## Environment Sensing (INPUT)

```typescript
// What the NPC perceives this tick
interface NPCSensorData {
    // Nearby entities
    visible_entities: Array<{
        id: string;
        type: 'PLAYER' | 'NPC' | 'ITEM';
        distance: number;
        angle: number;  // Relative to NPC facing
        threat_level: number;
    }>;
    
    // Zone information
    current_zone: string;
    zone_crowding: number;  // 0-1
    zone_vibe: VibeVector;
    
    // Sounds
    nearby_sounds: Array<{
        type: 'FOOTSTEP' | 'GUNSHOT' | 'VOICE' | 'ALARM';
        distance: number;
        direction: number;
    }>;
    
    // Time
    time_of_day: 'MORNING' | 'AFTERNOON' | 'EVENING' | 'NIGHT';
    
    // Global events
    alarm_active: boolean;
    lockdown: boolean;
}

function senseEnvironment(npc: NPC, world: WorldState): NPCSensorData {
    const visible = [];
    
    // Raycast-style visibility check
    for (const entity of world.entities) {
        if (entity.id === npc.id) continue;
        
        const dist = distance(npc, entity);
        if (dist > SIGHT_RANGE) continue;
        
        const angle = angleTo(npc, entity) - npc.facing;
        if (Math.abs(angle) > FOV / 2) continue;
        
        if (!lineOfSight(npc, entity, world.tilemap)) continue;
        
        visible.push({
            id: entity.id,
            type: entity.type,
            distance: dist,
            angle: angle,
            threat_level: assessThreat(npc, entity)
        });
    }
    
    return {
        visible_entities: visible,
        current_zone: getZoneAt(npc.x, npc.y),
        zone_crowding: getZoneCrowding(npc.x, npc.y),
        zone_vibe: getZoneVibe(npc.x, npc.y),
        nearby_sounds: getNearbyAudio(npc, world),
        time_of_day: world.time_of_day,
        alarm_active: world.flags.alarm_active,
        lockdown: world.flags.lockdown
    };
}
```

## QBIT Update (CONTROLBLOCK mutation)

```typescript
// Update QBIT axes based on environment
function updateQBIT(npc: NPC, sensors: NPCSensorData, dt: number) {
    // Threat response
    const max_threat = Math.max(
        ...sensors.visible_entities.map(e => e.threat_level),
        0
    );
    if (max_threat > 0.5) {
        npc.qbit.fear += max_threat * 0.1 * dt;
        npc.qbit.hostility += max_threat * 0.05 * dt;
    } else {
        // Decay fear when safe
        npc.qbit.fear *= 0.95;
    }
    
    // Social pressure
    if (sensors.zone_crowding > 0.7) {
        npc.qbit.patience -= 0.02 * dt;
        npc.qbit.social -= 0.01 * dt;
    }
    
    // Vibe absorption (NPC picks up zone aesthetic)
    npc.qbit.energy += sensors.zone_vibe.energy_mod * 0.01 * dt;
    
    // Wattitude calculation (thermal metaphor)
    // Higher wattitude = more stressed = degraded behavior
    const stress_factors = 
        Math.abs(npc.qbit.fear) * 20 +
        Math.abs(npc.qbit.hostility) * 15 +
        (1 - npc.qbit.patience) * 10 +
        (sensors.alarm_active ? 20 : 0);
    
    const target_wattitude = Math.min(100, stress_factors);
    
    // Smooth transition (hysteresis)
    if (target_wattitude > npc.wattitude) {
        npc.wattitude += 5 * dt;  // Heat up fast
    } else {
        npc.wattitude -= 2 * dt;  // Cool down slow
    }
    npc.wattitude = Math.max(0, Math.min(100, npc.wattitude));
    
    // Clamp QBIT axes
    for (const key of Object.keys(npc.qbit)) {
        npc.qbit[key] = Math.max(-1, Math.min(1, npc.qbit[key]));
    }
}
```

## Wattitude Bands (DISPATCHER selection)

```typescript
// Wattitude determines which firmware layer is active
type WattitudeBand = 'COOL' | 'WARM' | 'HOT' | 'CRITICAL';

function getWattitudeBand(wattitude: number): WattitudeBand {
    if (wattitude < 25) return 'COOL';
    if (wattitude < 50) return 'WARM';
    if (wattitude < 85) return 'CRITICAL';
    return 'CRITICAL';
}

// Each band has different behavioral characteristics
const BAND_BEHAVIORS: Record<WattitudeBand, {
    response_complexity: number;  // How nuanced the behavior
    memory_access: boolean;       // Can access memory?
    social_capacity: boolean;     // Can have conversations?
    combat_style: 'tactical' | 'aggressive' | 'defensive' | 'flee';
}> = {
    'COOL': {
        response_complexity: 1.0,
        memory_access: true,
        social_capacity: true,
        combat_style: 'tactical'
    },
    'WARM': {
        response_complexity: 0.7,
        memory_access: true,
        social_capacity: true,
        combat_style: 'aggressive'
    },
    'HOT': {
        response_complexity: 0.4,
        memory_access: false,  // Memory dumped
        social_capacity: false,
        combat_style: 'defensive'
    },
    'CRITICAL': {
        response_complexity: 0.1,
        memory_access: false,
        social_capacity: false,
        combat_style: 'flee'
    }
};
```

## State Machine Step (DISPATCHER)

```typescript
function npcStateMachineStep(
    npc: NPC,
    sensors: NPCSensorData,
    dt: number
): NPCAction {
    const band = getWattitudeBand(npc.wattitude);
    const behavior = BAND_BEHAVIORS[band];
    
    // Memory dump at HOT+
    if (!behavior.memory_access) {
        npc.memory.known_threats = [];
        npc.memory.conversation_partner = null;
        // Identity (archetype, firmware) survives
    }
    
    // State transitions based on current state + sensors
    switch (npc.state) {
        case 'IDLE':
            // Transition checks
            if (sensors.alarm_active) {
                npc.state = 'INVESTIGATE';
                return { type: 'ALERT' };
            }
            if (hasThreat(sensors)) {
                npc.state = npc.archetype === 'SECURITY' ? 'INVESTIGATE' : 'FLEE';
            }
            if (npc.state_timer <= 0) {
                npc.state = 'PATROL';
                npc.state_timer = 10 + Math.random() * 20;
            }
            return { type: 'WAIT' };
            
        case 'PATROL':
            npc.state_timer -= dt;
            
            // Threat detection
            if (hasThreat(sensors)) {
                if (band === 'CRITICAL') {
                    npc.state = 'FLEE';
                } else if (npc.archetype === 'SECURITY') {
                    npc.state = 'INVESTIGATE';
                } else {
                    npc.state = 'FLEE';
                }
                return { type: 'ALERT' };
            }
            
            // Continue patrol
            if (npc.state_timer <= 0) {
                npc.state = 'IDLE';
                npc.state_timer = 5 + Math.random() * 10;
            }
            
            return {
                type: 'MOVE',
                direction: getPatrolDirection(npc),
                speed: behavior.response_complexity * WALK_SPEED
            };
            
        case 'INVESTIGATE':
            const threat = getHighestThreat(sensors);
            
            if (!threat) {
                npc.state = 'PATROL';
                return { type: 'LOOK_AROUND' };
            }
            
            if (threat.distance < ATTACK_RANGE && npc.archetype === 'SECURITY') {
                npc.state = 'ATTACK';
            }
            
            return {
                type: 'MOVE',
                direction: threat.angle,
                speed: RUN_SPEED
            };
            
        case 'CHASE':
            const target = getChaseTarget(npc, sensors);
            
            if (!target) {
                npc.state = 'INVESTIGATE';
                return { type: 'LOOK_AROUND' };
            }
            
            if (target.distance < ATTACK_RANGE) {
                npc.state = 'ATTACK';
            }
            
            return {
                type: 'MOVE',
                direction: target.angle,
                speed: RUN_SPEED
            };
            
        case 'ATTACK':
            if (band === 'CRITICAL') {
                npc.state = 'FLEE';
                return { type: 'DISENGAGE' };
            }
            
            const attackTarget = getHighestThreat(sensors);
            if (!attackTarget || attackTarget.distance > ATTACK_RANGE) {
                npc.state = 'CHASE';
                return { type: 'PURSUE' };
            }
            
            return {
                type: 'ATTACK',
                target: attackTarget.id,
                style: behavior.combat_style
            };
            
        case 'FLEE':
            const threats = sensors.visible_entities
                .filter(e => e.threat_level > 0.3);
            
            if (threats.length === 0) {
                npc.state = 'IDLE';
                npc.state_timer = 30;  // Extended cooldown
                return { type: 'RECOVER' };
            }
            
            // Run away from average threat direction
            const avg_threat_angle = averageAngle(threats.map(t => t.angle));
            const flee_angle = avg_threat_angle + Math.PI;  // Opposite direction
            
            return {
                type: 'MOVE',
                direction: flee_angle,
                speed: RUN_SPEED * 1.2
            };
            
        case 'CONVERSE':
            if (!behavior.social_capacity) {
                // Too stressed to talk
                npc.state = 'IDLE';
                return { type: 'END_CONVERSATION' };
            }
            
            npc.state_timer -= dt;
            if (npc.state_timer <= 0) {
                npc.state = 'IDLE';
                return { type: 'END_CONVERSATION' };
            }
            
            return { type: 'TALK' };
            
        default:
            npc.state = 'IDLE';
            return { type: 'WAIT' };
    }
}
```

## Complete NPC Tick

```typescript
// One frame of NPC behavior
function npcTick(npc: NPC, world: WorldState, dt: number): NPCAction {
    // 1. INPUT: Sense environment
    const sensors = senseEnvironment(npc, world);
    
    // 2. UPDATE: QBIT axes + wattitude
    updateQBIT(npc, sensors, dt);
    
    // 3. DECIDE: State machine step
    const action = npcStateMachineStep(npc, sensors, dt);
    
    // 4. OUTPUT: Return action for execution layer
    return action;
}

// Called by zone update loop
function updateAllNPCs(npcs: NPC[], world: WorldState, dt: number) {
    for (const npc of npcs) {
        if (!npc.active) continue;
        
        const action = npcTick(npc, world, dt);
        executeNPCAction(npc, action, world, dt);
    }
}
```

## Primitive Count (Single NPC)

| Primitive | Role |
|-----------|------|
| LOOP | Called once per frame via zone tick |
| CONTROLBLOCK | NPC struct (position, QBIT, state) |
| EVENT | Sensor data (visible threats, sounds) |
| DISPATCHER | State machine (IDLE → PATROL → ... → FLEE) |

## Bridge to Synthactor

This NPC structure is "Synthactor-lite." Full Synthactors add:

1. **Firmware Layers** — Multiple personality stacks that regress under pressure
2. **Dialogue Config** — Compression rules, metaphor sources, ROM fallback phrases
3. **Identity Kernel** — Core traits that survive complete memory dump
4. **Wattitude Hysteresis** — Heating/cooling rates, band transition thresholds

See the `synthactor-blueprint` skill for full specification.

## Key Insight

> "The NPC doesn't know if it's in a shooter, a mall sim, or a visual novel. It only knows its CONTROLBLOCK state and the DISPATCHER's current state. Everything else is sensor input."

This abstraction allows the same NPC behavior core to operate across different game genres.
