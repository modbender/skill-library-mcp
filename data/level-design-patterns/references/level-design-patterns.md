# Level Design Best Practices

## Scene Organization

### Hierarchy Structure
```
SceneRoot/
├── Lighting/
│   ├── Directional Light (Sun)
│   ├── Global Volume
│   └── Reflection Probes/
├── Environment/
│   ├── Terrain/
│   ├── Water/
│   └── Sky/
├── Props/
│   ├── Vegetation/
│   ├── Structures/
│   └── Clutter/
├── Gameplay/
│   ├── Player/
│   ├── SpawnPoints/
│   ├── Triggers/
│   └── Interactables/
└── Audio/
    ├── Ambient/
    └── Music/
```

### Naming Conventions
- **PascalCase** for GameObjects: `MainTerrain`, `PlayerSpawn`
- **Descriptive names**: `OakTree_Large_01` not `Tree1`
- **No spaces** (use underscores): `Stone_Wall_Corner`
- **Prefixes for types**:
  - `pfx_` - Particle effects
  - `snd_` - Audio sources
  - `trg_` - Triggers/colliders
  - `lgt_` - Lights

## Terrain Guidelines

### Heightmap Resolution
| World Size | Heightmap Res | Use Case |
|-----------|---------------|----------|
| 128x128 | 129 | Small arena/test |
| 512x512 | 513 | Medium level |
| 1024x1024 | 1025 | Large open world |
| 2048x2048 | 2049 | Very large (performance heavy) |

### Terrain Height Scale
- **0-50m**: Flat/subtle rolling hills
- **50-150m**: Moderate terrain, small mountains
- **150-500m**: Large mountains, dramatic landscapes
- **500m+**: Extreme terrain (careful with scale)

### Performance Tips
- Use **Terrain Layers** instead of multiple materials
- Keep **detail density** reasonable (max 1-2 per meter)
- Use **GPU instancing** for vegetation
- **Bake lighting** for static terrain
- Consider **terrain streaming** for large worlds

## Lighting Guidelines

### Light Types by Use
- **Directional**: Sun, moon, ambient light source
- **Point**: Torches, lamps, glowing objects
- **Spot**: Flashlights, street lamps, area lights
- **Area** (Baked only): Soft interior lighting

### Shadow Settings
| Quality Level | Shadow Distance | Shadow Resolution |
|--------------|-----------------|-------------------|
| Low | 50m | 1024 |
| Medium | 100m | 2048 |
| High | 200m | 4096 |
| Ultra | 400m | 8192 |

### Realtime vs Baked
**Use Realtime:**
- Sun/moon (day/night cycle)
- Player flashlight
- Dynamic environments
- Moving platforms with lights

**Use Baked:**
- Static interior lighting
- Architectural lighting
- Ambient occlusion
- Large scenes with many lights

**Use Mixed:**
- Important static lights that affect dynamic objects
- Performance-critical areas

## Level Design Principles

### Flow & Navigation
1. **Lead the eye** - Use lighting, contrast, landmarks
2. **Clear paths** - Players should always know where to go
3. **Affordances** - Make interactive objects obvious
4. **Verticality** - Use height for interest and strategy
5. **Cover** - Provide cover every 10-15 meters in combat areas

### Player Metrics (First-Person)
- **Eye height**: 1.6-1.8m
- **Crouch height**: 1.0-1.2m
- **Door width**: 1.2-1.5m
- **Door height**: 2.2-2.4m
- **Hallway width**: 2-3m (minimum 1.5m)
- **Ceiling height**: 2.5-4m (3m standard)
- **Jump height**: 1.5-2m (varies by game)
- **Jump distance**: 3-5m

### Environment Storytelling
- **Environmental details** tell stories without text
- **Wear and tear** shows history
- **Props placement** suggests what happened
- **Lighting mood** reinforces narrative

## Optimization Checklist

### Models & Meshes
- [ ] Combine static meshes where possible
- [ ] Use LODs (Level of Detail) for complex objects
- [ ] Keep mesh colliders simple (convex only)
- [ ] Remove unnecessary vertices

### Textures & Materials
- [ ] Use texture atlases for small objects
- [ ] Keep texture sizes appropriate (don't overuse 4K)
- [ ] Use GPU instancing for repeated objects
- [ ] Share materials between objects

### Lighting
- [ ] Bake lighting for static geometry
- [ ] Use light probes for dynamic objects
- [ ] Limit realtime lights (max 4-8 per area)
- [ ] Use shadow cascades appropriately

### Terrain
- [ ] Use terrain holes for caves/tunnels
- [ ] Paint terrain layers efficiently
- [ ] Limit tree/detail distance
- [ ] Use billboards for distant trees

### General
- [ ] Occlusion culling for indoor areas
- [ ] Lightmap static for non-moving objects
- [ ] Reflection probes for shiny materials
- [ ] Frustum culling (automatic, but awareness helps)

## Scene Types

### Open World
- **Chunked loading**: Load/unload terrain sections
- **Distant LODs**: Very low poly for far objects
- **Varying density**: Detailed near player, simple far away
- **Landmarks**: Use tall visible landmarks for navigation

### Linear Levels
- **Gating**: Control player flow with doors/chokepoints
- **Backtracking**: Consider if players return to areas
- **Shortcuts**: Unlock shortcuts after clearing areas
- **Set pieces**: Script memorable moments

### Arena/Combat
- **Cover placement**: Every 10-15 meters
- **Flanking routes**: Multiple paths through area
- **Verticality**: High ground advantages
- **Spawn points**: Enemy spawn locations (hidden from player)
- **Extraction**: Clear end point after combat

### Puzzle/Exploration
- **Clues**: Environmental hints for solutions
- **Progressive complexity**: Teach mechanics gradually
- **Multiple solutions**: Allow creativity
- **Reward placement**: Place rewards for exploration

## Common Mistakes

### Technical
- **Scale issues**: Inconsistent object sizes
- **Light leaks**: Gaps in geometry let light through
- **Z-fighting**: Overlapping faces flicker
- **Collision gaps**: Holes in collision mesh

### Design
- **Empty spaces**: Large areas with nothing to do
- **Dead ends**: Areas with no purpose or reward
- **Visual clutter**: Too much detail, can't see important elements
- **Poor lighting**: Too dark or flat, no depth
- **Scale confusion**: Doors too big/small, unrealistic proportions

### Performance
- **Too many draw calls**: Thousands of individual objects
- **Unnecessary realtime lights**: Baking would be better
- **Oversized textures**: Using 4K for small objects
- **No LODs**: Complex models visible at all distances
- **Overdraw**: Many transparent objects overlapping

## Testing Checklist

Before considering a level complete:
- [ ] Can players always tell where to go?
- [ ] Are there any soft locks (stuck without reset)?
- [ ] Does lighting support the mood?
- [ ] Can players see enemies/obstacles in time?
- [ ] Is performance acceptable on target hardware?
- [ ] Are all interactive elements clear?
- [ ] Does the level tell its story visually?
- [ ] Are there rewards for exploration?
- [ ] Is scale consistent and believable?
- [ ] Can players navigate without getting lost?