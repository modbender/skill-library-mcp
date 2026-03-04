---
name: unity-level-design
description: Use when creating Unity game scenes and prototypes, building level designs, or automating Unity Editor workflows for terrain, lighting, environment setup, and player controllers. Use for post-apocalyptic scenes, fantasy forests, dungeon crawlers, and other game environments that need rapid prototyping.
---

# Unity Level Design

## Overview

Rapidly prototype Unity game scenes using Editor automation, modern Unity APIs, and best practices for level design. This skill automates terrain generation, lighting setup, environment placement, and player controller creation to get you implementing gameplay ideas quickly.

## When to Use

Use this skill when:
- Creating prototype scenes (post-apocalypse, fantasy, sci-fi, dungeon crawler, etc.)
- Setting up Unity terrain, meshes, and ground geometry
- Automating lighting, post-processing, and environment setup
- Building player controllers and basic gameplay systems
- Need to go from concept to playable scene rapidly

## Core Workflow

### Step 1: Research Current APIs

Before implementing, check Unity's latest APIs and best practices:

**Modern Unity Systems:**
- Terrain Tools package (GPU-accelerated sculpting)
- Universal Render Pipeline (URP) or High Definition Render Pipeline (HDRP)
- DOTS/ECS for performance-critical scenarios
- Shader Graph for custom materials
- VFX Graph for particle effects

**Key APIs to reference:**
- `UnityEngine.Terrain` - Terrain manipulation
- `UnityEditor.TerrainTools` - Editor terrain tools
- `UnityEngine.Rendering.Universal` - URP components
- `UnityEditor.SceneManagement` - Scene automation

### Step 2: Scene Setup Automation

Use Editor scripts to automate repetitive setup:

```csharp
// Example: Automated scene initialization
public static class SceneSetupHelper
{
    [MenuItem("Level Design/Create Basic Scene")]
    public static void CreateBasicScene()
    {
        // Setup lighting
        SetupLighting();
        
        // Create terrain
        CreateTerrain();
        
        // Setup post-processing
        SetupPostProcessing();
        
        // Create player
        CreatePlayerController();
    }
}
```

### Step 3: Terrain Generation

**Options:**
1. **Unity Terrain** - Best for natural landscapes
2. **Mesh Generation** - Best for stylized/architectural
3. **Procedural Generation** - Best for endless/replayable worlds

### Step 4: Environment & Props

Automate placement of:
- Vegetation (trees, grass, rocks)
- Structures (buildings, ruins, dungeons)
- Lighting (sun, ambient, point lights)
- Effects (fog, particles, post-processing)

### Step 5: Player & Gameplay

Create basic:
- Player controller (FPS, third-person, top-down)
- Camera setup
- Input handling
- Basic interactions

## Scene Types

### Post-Apocalyptic Scene
- Destroyed urban environment
- Ruined buildings and debris
- Overgrown vegetation
- Atmospheric fog and lighting
- Scattered resources/props

### Fantasy Forest
- Dense woodland terrain
- Rivers and lakes
- Fantasy vegetation
- Magical lighting effects
- Pathways and clearings

### Dungeon Crawler
- Procedural room generation
- Corridor systems
- Torch/candle lighting
- Traps and enemy spawners
- Loot chests

## Quick Reference

| Task | Method | API/Tool |
|------|--------|----------|
| Create Terrain | Editor script | `Terrain.CreateTerrainGameObject` |
| Sculpt Terrain | Noise/heightmaps | `TerrainData.SetHeights` |
| Add Vegetation | Tree/Grass painting | `TerrainData.treeInstances` |
| Setup Lighting | URP/HDRP | `UniversalAdditionalLightData` |
| Post-Processing | Volume components | `Volume` + profiles |
| Player Controller | Character Controller | `CharacterController` component |
| Procedural Meshes | Runtime generation | `Mesh` class |

## Editor Tools

See `scripts/` for automation tools:
- `SceneSetupWizard.cs` - One-click scene initialization
- `TerrainGenerator.cs` - Procedural terrain creation
- `EnvironmentPainter.cs` - Batch environment placement
- `LightingSetup.cs` - Automated lighting configuration

## References

See `references/` for detailed documentation:
- `unity-apis.md` - Current Unity API reference
- `terrain-tools.md` - Terrain system documentation
- `urp-setup.md` - Universal Render Pipeline guide
- `level-design-patterns.md` - Best practices and patterns

## Common Mistakes

- **Wrong render pipeline**: Check if project uses URP, HDRP, or Built-in RP
- **Terrain scale**: Unity terrain uses different height/length scales
- **Lighting baking**: Realtime GI can be slow; use baked lighting for static geometry
- **Performance**: Too many trees/colliders will kill performance
- **Scale consistency**: Keep player, environment, and props to consistent scale

## Example Usage

```csharp
// Create a post-apocalyptic scene
[MenuItem("Level Design/Post-Apocalyptic Scene")]
static void CreatePostApocalypticScene()
{
    // 1. Create terrain with noise
    var terrain = TerrainGenerator.CreateRuinedTerrain();
    
    // 2. Setup dramatic lighting
    LightingSetup.CreateDramaticLighting(Color.gray * 0.3f);
    
    // 3. Add fog and post-processing
    PostProcessingSetup.CreateAtmosphericFog();
    
    // 4. Scatter debris and props
    EnvironmentPainter.ScatterDebris(50);
    
    // 5. Create player
    var player = PlayerSetup.CreateFPSPlayer();
    player.transform.position = new Vector3(0, 5, 0);
}
```