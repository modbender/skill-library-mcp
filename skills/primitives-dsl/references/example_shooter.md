# Worked Example 1 — Classic Shooter Loop

Goal: a portable shooter loop where bullets, enemies, pickups behave consistently.

## Primitive Map

| Primitive | Instance |
|-----------|----------|
| **LOOP** | fixed-step sim tick @ 60Hz |
| **TILEGRID** | collision grid / sector map |
| **CONTROLBLOCK** | PlayerCB, EnemyCB, BulletCB |
| **POOL** | BulletPool (512), EnemyPool (128), EventPool (2048) |
| **EVENT** | HitEvent, SpawnEvent, PickupEvent |
| **DISPATCHER** | routes events to systems; schedules update order |

## CONTROLBLOCKs (minimum fields)

**PlayerCB**
- pos, vel
- hp
- weapon_mode
- cooldown_ticks
- input_intent (packed)

**BulletCB**
- alive (bool), pos, vel
- owner_id
- ttl_ticks
- damage

**EnemyCB**
- alive, pos, vel
- hp
- ai_state
- target_id
- stun_ticks

## LOOP Pseudocode (portable)

```
LOOP tick(dt_fixed):
    read_input() -> PlayerCB.input_intent
    DISPATCHER.run(System_MovePlayers)
    DISPATCHER.run(System_AIEnemies)
    DISPATCHER.run(System_SpawnBullets)    # writes BulletPool
    DISPATCHER.run(System_MoveBullets)
    DISPATCHER.run(System_Collide)         # emits EVENTS
    DISPATCHER.run(System_ApplyEvents)     # consumes EVENTS
    DISPATCHER.run(System_CleanupPools)    # frees by ttl/hp
```

## EVENTS

**HitEvent**
- type="HIT"
- route="damage"
- src_entity, dst_entity
- amount
- tick_index

**SpawnEvent**
- type="SPAWN"
- route="spawn"
- entity_type, spawn_params

## Portability Notes

| Platform | Translation |
|----------|-------------|
| **68K** | DISPATCHER is call order; EVENT is ring buffer |
| **Cell** | DISPATCHER batches collide jobs; CONTROLBLOCKs are DMA'd to SPUs |
| **CUDA** | Collide becomes kernel; EVENTS are append buffers; ApplyEvents is reduction |
| **ECS** | CONTROLBLOCKs become components; DISPATCHER becomes system scheduling |

---

# Deep Dive: Full Implementation

The sections below show complete TypeScript implementations.

### Frame Loop (LOOP + DISPATCHER)

```typescript
// The heartbeat: 60Hz fixed timestep
function gameLoop(timestamp: number) {
    if (!state.running) return;
    
    // LOOP: Calculate delta time
    let dt = (timestamp - state.lastFrameTime) / 1000;
    dt = Math.min(dt, 0.05);  // Clamp to 50ms max
    state.lastFrameTime = timestamp;
    
    // DISPATCHER: State machine decides what runs
    switch (state.schedule) {
        case 'GAME_LOOP':
            // INPUT
            const intent = state.adapter.sample(dt);
            
            // UPDATE + COLLIDE
            updateGame(state, intent);
            
            // RENDER
            renderGame(state, ctx);
            break;
            
        case 'PAUSE':
            renderPauseScreen(ctx);
            break;
            
        case 'GAME_OVER':
            renderGameOver(ctx);
            break;
    }
    
    requestAnimationFrame(gameLoop);
}
```

### Entity Management (CONTROLBLOCK + POOL)

```typescript
// CONTROLBLOCK: Fixed entity structure
interface Enemy {
    active: boolean;
    x: number;
    y: number;
    vx: number;
    vy: number;
    health: number;
    state: 'PATROL' | 'CHASE' | 'ATTACK' | 'DEAD';
    frame: number;
}

// POOL: Pre-allocated, reuse slots
const MAX_ENEMIES = 100;
const enemyPool: Enemy[] = [];

function initPool() {
    for (let i = 0; i < MAX_ENEMIES; i++) {
        enemyPool.push({
            active: false,
            x: 0, y: 0, vx: 0, vy: 0,
            health: 0,
            state: 'PATROL',
            frame: 0
        });
    }
}

function spawnEnemy(x: number, y: number): Enemy | null {
    for (const enemy of enemyPool) {
        if (!enemy.active) {
            enemy.active = true;
            enemy.x = x;
            enemy.y = y;
            enemy.health = 50;
            enemy.state = 'PATROL';
            return enemy;
        }
    }
    return null;  // Pool exhausted
}

function despawnEnemy(enemy: Enemy) {
    enemy.active = false;  // Return to pool
}
```

### Spatial System (TILEGRID)

```typescript
// TILEGRID: 64×64 map, each tile is 64 units
const TILE_SIZE = 64;
const MAP_WIDTH = 64;
const MAP_HEIGHT = 64;

interface Tile {
    solid: boolean;
    texture: number;
}

const tilemap: Tile[][] = [];

// Convert world position to tile
function worldToTile(x: number, y: number): [number, number] {
    return [
        Math.floor(x / TILE_SIZE),
        Math.floor(y / TILE_SIZE)
    ];
}

// Collision check against tilemap
function isBlocked(x: number, y: number): boolean {
    const [tx, ty] = worldToTile(x, y);
    if (tx < 0 || tx >= MAP_WIDTH) return true;
    if (ty < 0 || ty >= MAP_HEIGHT) return true;
    return tilemap[ty][tx].solid;
}
```

### State Coordination (EVENT)

```typescript
// EVENT: Flags polled each frame
interface GameFlags {
    player_dead: boolean;
    level_complete: boolean;
    boss_spawned: boolean;
    enemies_remaining: number;
}

const flags: GameFlags = {
    player_dead: false,
    level_complete: false,
    boss_spawned: false,
    enemies_remaining: 0
};

// Check events each frame (in updateGame)
function checkEvents() {
    // Count active enemies
    flags.enemies_remaining = enemyPool.filter(e => e.active).length;
    
    // Level complete when all dead
    if (flags.enemies_remaining === 0 && !flags.level_complete) {
        flags.level_complete = true;
        state.schedule = 'END_LEVEL';
    }
    
    // Player death check
    if (state.player.health <= 0 && !flags.player_dead) {
        flags.player_dead = true;
        state.schedule = 'GAME_OVER';
    }
}
```

### Update Logic (All Primitives)

```typescript
function updateGame(state: GameState, intent: Intent) {
    const dt = intent.dt;
    
    // UPDATE PLAYER (CONTROLBLOCK)
    state.player.angle += intent.turn * dt;
    
    const dx = Math.cos(state.player.angle) * intent.move.y * MOVE_SPEED * dt;
    const dy = Math.sin(state.player.angle) * intent.move.y * MOVE_SPEED * dt;
    
    // COLLIDE with TILEGRID
    if (!isBlocked(state.player.x + dx, state.player.y)) {
        state.player.x += dx;
    }
    if (!isBlocked(state.player.x, state.player.y + dy)) {
        state.player.y += dy;
    }
    
    // UPDATE ENEMIES (POOL iteration)
    for (const enemy of enemyPool) {
        if (!enemy.active) continue;
        
        // Behavior state machine (mini-DISPATCHER)
        switch (enemy.state) {
            case 'PATROL':
                enemy.x += enemy.vx * dt;
                if (distToPlayer(enemy) < ALERT_RANGE) {
                    enemy.state = 'CHASE';
                }
                break;
                
            case 'CHASE':
                moveTowardPlayer(enemy, dt);
                if (distToPlayer(enemy) < ATTACK_RANGE) {
                    enemy.state = 'ATTACK';
                }
                break;
                
            case 'ATTACK':
                // Attack logic
                break;
                
            case 'DEAD':
                enemy.frame += dt * DEATH_ANIM_SPEED;
                if (enemy.frame > DEATH_FRAMES) {
                    despawnEnemy(enemy);
                }
                break;
        }
    }
    
    // COLLIDE: Projectiles vs enemies
    for (const proj of projectilePool) {
        if (!proj.active) continue;
        
        for (const enemy of enemyPool) {
            if (!enemy.active) continue;
            
            if (distance(proj, enemy) < HIT_RADIUS) {
                enemy.health -= proj.damage;
                despawnProjectile(proj);
                
                // EVENT: Check for death
                if (enemy.health <= 0) {
                    enemy.state = 'DEAD';
                    enemy.frame = 0;
                }
                break;
            }
        }
    }
    
    // EVENT: Check game state transitions
    checkEvents();
}
```

## Primitive Count

| Primitive | Instances |
|-----------|-----------|
| LOOP | 1 (game loop @ 60Hz) |
| TILEGRID | 1 (64×64 map) |
| CONTROLBLOCK | 3 (Player, Enemy, Projectile) |
| POOL | 2 (enemyPool, projectilePool) |
| EVENT | 1 (GameFlags) |
| DISPATCHER | 2 (game state, enemy behavior) |

## Key Insight

The shooter loop is actually **nested DISPATCHERS**:
- Outer: Game state (MENU → GAME_LOOP → PAUSE → GAME_OVER)
- Inner: Enemy behavior (PATROL → CHASE → ATTACK → DEAD)

Each level of the state machine owns its own frame slice.
