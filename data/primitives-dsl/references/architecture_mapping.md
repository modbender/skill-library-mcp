# Architecture Mapping — 68K → Cell → CUDA → ECS

This is a translation table, not a judgment table.

## Translation Table

| Primitive | 68K-era / classic | Cell (PPU/SPU) | CUDA / GPU | Modern ECS |
|-----------|-------------------|----------------|------------|------------|
| **LOOP** | `main() while(running) { tick(); }` | PPU master loop orchestrates SPU jobs | CPU host loop launches kernels per step | "World tick" runs systems in order |
| **TILEGRID** | tilemap arrays; sector maps | SPU reads tile chunks via DMA | grids/chunks as buffers; texture-like access | spatial hash, grid components, zone graph |
| **CONTROLBLOCK** | structs; bitflags; state machines | control blocks describe DMA/jobs; state structs per actor | kernel params + per-entity structs in buffers | component data, archetype chunks, state blobs |
| **POOL** | fixed arrays for entities/bullets | job pools + preallocated SPU buffers | device buffers, arena allocators, compaction | entity pools, component pools, job pools |
| **EVENT** | message queues; ring buffers | mailbox + command lists + job completion signals | append buffers; prefix sums; event flags | event bus, command buffers, reactive systems |
| **DISPATCHER** | switch/case + function pointers | PPU dispatcher launches SPU tasks | kernel launch scheduler + stream policy | system scheduler + job system |

## Portability Notes

- **68K** teaches explicit loops and bounded memory (POOL discipline)
- **Cell** teaches dispatch + data movement (DISPATCHER + CONTROLBLOCK as contracts)
- **CUDA** teaches batching and locality (TILEGRID + POOL as buffers, EVENTS as streams)
- **ECS** teaches data-oriented CONTROLBLOCKS (components) and predictable scheduling

## "Same shape, different metal"

When porting, **keep**:
- CONTROLBLOCK field meanings stable
- EVENTS stable in name and route keys
- DISPATCHER policy explicit (determinism, budgets)

Only **change**:
- execution backend (thread/SPU/kernel/system)
- memory layout (arrays-of-structs vs structs-of-arrays)

---

# Deep Dive: Full Code Examples

The sections below show actual implementations across architectures. Read these when you need concrete syntax, not just concepts.

## LOOP

**Definition:** Execute the same operation N times in predictable sequence with known stride.

### 68K/Amiga (1995) — Alien Bash II

```asm
; Main game loop (from main/main.s:135-186)
; Runs at 50Hz, synchronized to VBlank
Main_Game_Routine:
    move.l  a6,d0                ; current schedule
    cmp.l   #GAME_LOOP,d0
    bne     .check_pause

    jsr     Sync_To_VBlank       ; Wait for frame boundary (20ms)
    jsr     Read_Input           ; INPUT
    jsr     Update_Player        ; UPDATE
    jsr     Update_Aliens        ; UPDATE (100-alien pool)
    jsr     Update_Projectiles   ; UPDATE (50-projectile pool)
    jsr     Collision_Check      ; COLLIDE
    jsr     Render_Screen        ; RENDER
    bra     Main_Game_Routine
```

**Key Property:** 50Hz hardware-enforced by VBlank interrupt.

### Cell SPE (2006)

```c
// PPE main loop dispatches to 6 SPEs
void ppe_main() {
    while (running) {
        sync_to_vsync();  // 60Hz frame boundary
        
        // INPUT: Read controller (PPE only)
        read_input();
        
        // UPDATE: Distribute to 6 SPEs (16 aliens each)
        for (int spu = 0; spu < 6; spu++) {
            spu_write_mailbox(spu, JOB_UPDATE_ALIENS);
        }
        wait_for_all_spes();
        
        // COLLIDE: PPE coordinates (SPEs can't sync)
        collision_check();
        
        // RENDER: GPU async
        queue_render_commands();
    }
}
```

**Key Property:** UPDATE parallelized across SPEs, but frame boundaries are sequential.

### CUDA GPU (2008+)

```cuda
// Host loop launches kernels
void cuda_main() {
    while (running) {
        // INPUT: CPU reads controller
        read_input();
        
        // UPDATE: Launch kernels
        update_aliens<<<blocks, threads>>>();
        update_projectiles<<<blocks, threads>>>();
        
        // COLLIDE: Separate kernel
        collision_check<<<blocks, threads>>>();
        
        cudaDeviceSynchronize();  // Frame boundary
        
        // RENDER: OpenGL/Vulkan
        render();
    }
}
```

**Key Property:** Kernels are parallel, but frame sync is explicit.

### Modern ECS (Unity/Unreal-ish)

```typescript
// System update tick (from game.ts)
function gameLoop(timestamp: number) {
    if (!state.running) return;
    
    // Delta time with spike protection
    let dt = (timestamp - state.lastFrameTime) / 1000;
    dt = Math.min(dt, 0.05);  // Max 50ms
    state.lastFrameTime = timestamp;
    
    // INPUT: Sample adapter
    const intent = state.adapter.sample(dt);
    
    // UPDATE + COLLIDE: Brain function
    updateGame(state, intent);
    
    // RENDER: Observer function
    renderCallback(state, ctx);
    
    requestAnimationFrame(gameLoop);
}
```

**Key Property:** `requestAnimationFrame` provides vsync, delta time handles variable framerate.

---

## TILEGRID

**Definition:** Uniform spatial subdivision where each cell is a fixed work unit.

### 68K/Amiga (1995)

```asm
; Level data: 64×64 tiles, 16 pixels each
; RLE compressed in ROM, decompressed to RAM

TILE_SIZE       equ 16      ; pixels
MAP_WIDTH       equ 64      ; tiles
MAP_HEIGHT      equ 64      ; tiles

; Collision check: entity position → tile lookup
Check_Tile_Collision:
    move.w  entity_x,d0
    lsr.w   #4,d0           ; divide by 16 (>> 4)
    move.w  entity_y,d1
    lsr.w   #4,d1
    mulu    #MAP_WIDTH,d1   ; row offset
    add.w   d0,d1           ; + column
    lea     tile_map,a0
    move.b  (a0,d1.w),d0    ; fetch tile type
    rts
```

### Cell SPE (2006)

```c
// SPE processes 128-byte aligned tile sectors (8×8 tiles)
void spe_process_tile_sector(uint8_t* tiles, collision_t* out) {
    // DMA fetch 128 bytes (8×8 tiles)
    dma_get(local_tiles, main_memory_ptr, 128);
    dma_wait_all();
    
    // Process all 64 tiles in sector
    for (int i = 0; i < 64; i++) {
        uint8_t tile = local_tiles[i];
        out[i] = (tile & SOLID_FLAG) ? COLLISION : NONE;
    }
    
    dma_put(out, result_ptr, sizeof(collision_t) * 64);
}
```

**Key Property:** Each SPE processes one 128-byte sector, not individual tiles.

### CUDA GPU (2008+)

```cuda
__global__ void process_tiles(uint8_t* level_map, int stride,
                              collision_t* collisions) {
    int tile_idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (tile_idx >= total_tiles) return;
    
    int ty = tile_idx / stride;
    int tx = tile_idx % stride;
    
    uint8_t tile = level_map[ty * stride + tx];
    collisions[tile_idx] = (tile & SOLID_FLAG) ? COLLISION : NONE;
}
```

**Key Property:** Warp processes 32 consecutive tiles (perfect coalescing).

### Modern ECS (TypeScript)

```typescript
// From primitives.ts
export interface Tile {
    readonly size: 64;        // Fixed 64×64
    grid_x: number;
    grid_y: number;
    material: MaterialID;
    walkable: boolean;
    texture_id?: TextureID;
    height?: number;
    light_level?: number;
}

// Collision check: world → tile → lookup
function isBlocked(x: number, y: number, map: HybridMapJSON): boolean {
    const tileX = Math.floor(x);
    const tileY = Math.floor(y);
    if (tileX < 0 || tileX >= map.width) return true;
    if (tileY < 0 || tileY >= map.height) return true;
    return map.tiles[tileY][tileX] > 0;  // Non-zero = wall
}
```

---

## CONTROLBLOCK

**Definition:** Fixed-size entity state struct.

### 68K/Amiga (1995)

```asm
; Alien control block: 50 bytes (from alien_routines.s)
; Fixed layout for predictable access
ALIEN_CB_SIZE   equ 50

                rsreset
alien_active    rs.b 1      ; +0:  active flag
alien_type      rs.b 1      ; +1:  alien type
alien_x         rs.w 1      ; +2:  x position
alien_y         rs.w 1      ; +4:  y position
alien_vx        rs.w 1      ; +6:  x velocity
alien_vy        rs.w 1      ; +8:  y velocity
alien_health    rs.w 1      ; +10: health
alien_state     rs.b 1      ; +12: behavior state
alien_frame     rs.b 1      ; +13: animation frame
; ... more fields to 50 bytes
```

### Cell SPE (2006)

```c
// Fixed struct for DMA alignment
typedef struct __attribute__((aligned(16))) {
    uint8_t  active;
    uint8_t  type;
    int16_t  x, y;
    int16_t  vx, vy;
    int16_t  health;
    uint8_t  state;
    uint8_t  frame;
    uint8_t  padding[6];  // Pad to 16-byte boundary
} alien_cb_t;

_Static_assert(sizeof(alien_cb_t) == 16, "CB must be 16 bytes for DMA");
```

### CUDA GPU (2008+)

```cuda
// Structure-of-Arrays for coalesced access
struct AlienSOA {
    float* x;       // All x positions contiguous
    float* y;       // All y positions contiguous
    float* vx;
    float* vy;
    int* health;
    int* state;
};

__global__ void update_aliens(AlienSOA aliens, int count) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= count) return;
    
    // Coalesced reads (all threads read adjacent memory)
    float x = aliens.x[i];
    float vx = aliens.vx[i];
    
    // Update
    aliens.x[i] = x + vx;
}
```

**Key Property:** GPU prefers Structure-of-Arrays over Array-of-Structures.

### Modern ECS (TypeScript)

```typescript
// From primitives.ts
export interface Entity {
    sprite_id: SpriteID;
    position: TilePosition;
    velocity?: [number, number];
    facing?: number;
    current_frame?: number;
    behavior_type?: BehaviorType;
    behavior_loop: () => void;
    state?: string;
    health?: number;
    max_health?: number;
    attack_range?: number;
    attack_damage?: number;
}
```

---

## POOL

**Definition:** Pre-allocated collection with slot reuse.

### 68K/Amiga (1995)

```asm
; Pre-allocated pool (NO malloc during gameplay)
; From alien_routines.s
.align 4
alien_pool:     .fill 50 * 100   ; 5000 bytes (100 aliens × 50 bytes)

Spawn_Alien:
    lea     alien_pool,a0
    move.w  #99,d0
.search:
    tst.b   (a0)                 ; Check active flag
    beq     .found
    adda.l  #50,a0               ; Next CB
    dbra    d0,.search
    rts                          ; Pool exhausted

.found:
    move.b  #1,(a0)              ; Mark active (reuse slot)
    move.w  spawn_x,2(a0)        ; Set x
    move.w  spawn_y,4(a0)        ; Set y
    rts
```

### Cell SPE (2006)

```c
#define MAX_ALIENS 100
alien_cb_t alien_pool[MAX_ALIENS];  // Static allocation

void spawn_alien(float x, float y) {
    // SPE cannot allocate; must reuse pool
    for (int i = 0; i < MAX_ALIENS; i++) {
        if (!alien_pool[i].active) {
            alien_pool[i].active = 1;
            alien_pool[i].x = x;
            alien_pool[i].y = y;
            return;
        }
    }
    // Pool exhausted (drops spawn, no error)
}
```

### CUDA GPU (2008+)

```cuda
__device__ AlienCB d_aliens[MAX_ALIENS];  // Pre-allocated
__device__ int free_slot_counter = 0;

__global__ void spawn_aliens(float* spawn_x, float* spawn_y, int count) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= count) return;
    
    // Atomically find free slot
    int slot = atomicAdd(&free_slot_counter, 1);
    if (slot < MAX_ALIENS) {
        d_aliens[slot].active = true;
        d_aliens[slot].x = spawn_x[i];
        d_aliens[slot].y = spawn_y[i];
    }
}
```

### Modern ECS (TypeScript)

```typescript
// Pool pattern from entity management
const MAX_ENTITIES = 100;
const entityPool: Entity[] = [];

// Initialize pool at startup
function initPool() {
    for (let i = 0; i < MAX_ENTITIES; i++) {
        entityPool.push(createEntity(SpriteID.NONE, 0, 0, () => {}));
    }
}

// Spawn: find inactive slot
function spawn(sprite: SpriteID, x: number, y: number): Entity | null {
    for (const entity of entityPool) {
        if (!entity.active) {
            entity.active = true;
            entity.sprite_id = sprite;
            entity.position.tile_x = x;
            entity.position.tile_y = y;
            return entity;
        }
    }
    return null;  // Pool exhausted
}

// Despawn: mark inactive (don't delete)
function despawn(entity: Entity) {
    entity.active = false;
}
```

---

## EVENT

**Definition:** Small shared state that changes processing flow.

### 68K/Amiga (1995)

```asm
; Global flags (from panel_routines.s:750-776)
Number_Of_Keys:         ds.w 1      ; Key count
Gate_Opened:            ds.b 1      ; Gate state
Generator_Destroyed:    ds.b 1      ; Level complete flag
Schedule_Entry:         ds.w 1      ; Current game state

; Usage: poll flag each frame
Check_Level_Complete:
    tst.b   Generator_Destroyed
    beq     .not_complete
    move.w  #END_LEVEL,Schedule_Entry
.not_complete:
    rts
```

### Cell SPE (2006)

```c
// Flags via mailbox (PPE ↔ SPE communication)
void spe_check_flags() {
    LevelFlags flags = fetch_flags();  // DMA get
    
    if (flags.generator_destroyed) {
        spu_write_mailbox(PPE, EVENT_LEVEL_COMPLETE);
    }
}
```

### CUDA GPU (2008+)

```cuda
__shared__ uint32_t level_flags;  // Fast shared memory

__global__ void game_kernel(uint32_t* global_flags) {
    // One thread loads to shared
    if (threadIdx.x == 0) {
        level_flags = *global_flags;
    }
    __syncthreads();
    
    // All threads check flag
    if (level_flags & GENERATOR_DESTROYED) {
        return;  // Early exit
    }
    
    update_enemy(threadIdx.x);
}
```

### Modern ECS (TypeScript)

```typescript
// Event flags pattern
interface LevelFlags {
    generator_destroyed: boolean;
    wall_removed: boolean;
    zone_entered: string | null;
}

// In game state
const flags: LevelFlags = {
    generator_destroyed: false,
    wall_removed: false,
    zone_entered: null
};

// Polled each frame in updateGame()
function checkEvents(state: GameState) {
    if (state.flags.generator_destroyed && 
        state.schedule === 'GAME_LOOP') {
        state.schedule = 'END_LEVEL';
        // Could also emit to event queue for observers
    }
}
```

---

## DISPATCHER

**Definition:** State machine that orchestrates which work runs when.

### 68K/Amiga (1995)

```asm
; Branch table dispatcher (from main.s)
Main_Dispatcher:
    move.w  Schedule_Entry,d0
    cmp.w   #GAME_LOOP,d0
    beq     Do_Game_Loop
    cmp.w   #PAUSE,d0
    beq     Do_Pause
    cmp.w   #END_LEVEL,d0
    beq     Do_End_Level
    bra     Main_Dispatcher

Do_Game_Loop:
    jsr     Update_All
    jsr     Collision_Check
    jsr     Render
    bra     Main_Dispatcher

Do_Pause:
    ; No updates, just wait for input
    jsr     Check_Resume_Input
    bra     Main_Dispatcher

Do_End_Level:
    jsr     Load_Next_Level
    move.w  #GAME_LOOP,Schedule_Entry
    bra     Main_Dispatcher
```

### Cell SPE (2006)

```c
void ppe_dispatcher() {
    ScheduleState state = GAME_LOOP;
    
    while (state != QUIT) {
        switch (state) {
        case GAME_LOOP:
            // Queue parallel work
            dispatch_to_spes(JOB_UPDATE);
            wait_for_spes();
            
            if (check_level_complete()) {
                state = END_LEVEL;
            }
            break;
            
        case PAUSE:
            // SPEs idle
            if (check_resume_input()) {
                state = GAME_LOOP;
            }
            break;
            
        case END_LEVEL:
            load_next_level();
            state = GAME_LOOP;
            break;
        }
    }
}
```

### CUDA GPU (2008+)

```cuda
// Host-side state machine (GPU workers don't decide)
void cuda_dispatcher() {
    ScheduleState state = GAME_LOOP;
    
    while (state != QUIT) {
        switch (state) {
        case GAME_LOOP:
            update_aliens<<<blocks, threads>>>();
            update_projectiles<<<blocks, threads>>>();
            collision_check<<<blocks, threads>>>();
            cudaDeviceSynchronize();
            
            if (is_level_complete()) {
                state = END_LEVEL;
            }
            break;
            
        case PAUSE:
            // GPU idle
            if (is_resume_input()) {
                state = GAME_LOOP;
            }
            break;
        }
    }
}
```

### Modern ECS (TypeScript)

```typescript
// From game loop pattern
type ScheduleState = 'GAME_LOOP' | 'PAUSE' | 'END_LEVEL' | 'MENU';

function updateGame(state: GameState, intent: Intent): void {
    switch (state.schedule) {
        case 'GAME_LOOP':
            updatePlayerFromIntent(state.player, state.hybridMap, intent);
            updateEntities(state.entities, intent.dt);
            checkCollisions(state);
            
            if (state.flags.level_complete) {
                state.schedule = 'END_LEVEL';
            }
            break;
            
        case 'PAUSE':
            // Only check for unpause
            if (intent.actions.pause) {
                state.schedule = 'GAME_LOOP';
            }
            break;
            
        case 'END_LEVEL':
            loadNextLevel(state);
            state.schedule = 'GAME_LOOP';
            break;
    }
}
```

---

## The Universal Truth

All four architectures implement the same algorithm:

1. **LOOP** at frame boundaries (causality)
2. **TILEGRID** for spatial work distribution (geometry)
3. **CONTROLBLOCK** for predictable entity state (conservation)
4. **POOL** for bounded resource usage (thermodynamics)
5. **EVENT** for state change coordination (information)
6. **DISPATCHER** for control flow (causality)

The language, syntax, and parallelism differ. The architecture does not.
