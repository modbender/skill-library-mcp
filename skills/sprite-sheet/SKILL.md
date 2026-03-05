# Sprite Sheet & Texture Atlas Mastery

**Category**: Game Development | Asset Optimization  
**Tech Stack**: Rust (Macroquad, Bevy), Godot 4.x  
**Created**: 2026-02-06  
**Status**: ✅ Complete

---

## 📋 Overview

Sprite sheets (texture atlases) are essential for efficient game asset management, reducing draw calls, memory usage, and load times by packing multiple sprites into a single texture.

### Key Benefits
- **Performance**: 1 HTTP request instead of N (web games)
- **Memory**: Reduced texture swaps, better GPU cache utilization
- **Mobile**: Lower bandwidth consumption, faster loading
- **Batching**: Multiple sprites rendered in single draw call

---

## 🎯 Core Concepts

### Sprite Sheet vs Texture Atlas
- **Sprite Sheet**: Uniformly-sized frames (e.g., 16×16 grid for animations)
- **Texture Atlas**: Irregular shapes packed efficiently (arbitrary sizes)
- **Practical**: Terms often used interchangeably

### Anatomy
```
sprite-sheet.png (2048×2048)
├─ player_idle_01 (0, 0, 64, 64)
├─ player_run_01  (64, 0, 64, 64)
├─ enemy_walk_01  (128, 0, 32, 32)
└─ ... (metadata in JSON/XML)
```

**Components**:
1. **Texture**: The actual PNG/JPG image
2. **Atlas Metadata**: JSON/XML with frame coordinates
3. **Animation Data**: Frame sequences, durations

---

## 🛠️ Framework Implementations

### 1. Rust + Macroquad (WASM-Ready)

**Loading**:
```rust
use macroquad::prelude::*;

#[derive(Clone, Copy)]
struct SpriteFrame {
    x: f32, y: f32, w: f32, h: f32,
}

impl SpriteFrame {
    fn as_rect(&self) -> Rect {
        Rect::new(self.x, self.y, self.w, self.h)
    }
}

#[macroquad::main("Sprite Demo")]
async fn main() {
    let texture = load_texture("assets/spritesheet.png").await.unwrap();
    texture.set_filter(FilterMode::Nearest); // Pixel art
    
    let frames = vec![
        SpriteFrame { x: 0.0, y: 0.0, w: 64.0, h: 64.0 },
        SpriteFrame { x: 64.0, y: 0.0, w: 64.0, h: 64.0 },
    ];
    
    let mut frame_idx = 0;
    let mut timer = 0.0;
    
    loop {
        clear_background(BLACK);
        
        // Animation logic
        timer += get_frame_time();
        if timer > 0.1 {
            frame_idx = (frame_idx + 1) % frames.len();
            timer = 0.0;
        }
        
        // Draw specific frame
        let frame = frames[frame_idx];
        draw_texture_ex(
            &texture,
            100.0, 100.0, // destination
            WHITE,
            DrawTextureParams {
                source: Some(frame.as_rect()),
                dest_size: Some(vec2(128.0, 128.0)), // scale 2x
                ..Default::default()
            },
        );
        
        next_frame().await
    }
}
```

**Key Points**:
- Use `source` parameter in `DrawTextureParams` for sub-rectangle
- `FilterMode::Nearest` for pixel art, `Linear` for smooth sprites
- Store atlas data in const arrays or load JSON with `serde`

---

### 2. Rust + Bevy (ECS Architecture)

**Setup**:
```rust
use bevy::prelude::*;

fn main() {
    App::new()
        .add_plugins(DefaultPlugins.set(ImagePlugin::default_nearest())) // pixel art
        .add_systems(Startup, setup)
        .add_systems(Update, animate_sprite)
        .run();
}

fn setup(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
    mut texture_atlases: ResMut<Assets<TextureAtlasLayout>>,
) {
    commands.spawn(Camera2dBundle::default());
    
    let texture = asset_server.load("sprites/character.png");
    
    // Define atlas layout (8 columns, 4 rows, each 64×64)
    let layout = TextureAtlasLayout::from_grid(
        UVec2::new(64, 64),
        8, 4,
        Some(UVec2::new(2, 2)), // padding
        Some(UVec2::new(4, 4)), // offset
    );
    let atlas_layout = texture_atlases.add(layout);
    
    // Spawn entity with atlas
    commands.spawn((
        SpriteBundle {
            texture,
            transform: Transform::from_scale(Vec3::splat(2.0)),
            ..default()
        },
        TextureAtlas {
            layout: atlas_layout,
            index: 0,
        },
        AnimationTimer(Timer::from_seconds(0.1, TimerMode::Repeating)),
    ));
}

#[derive(Component)]
struct AnimationTimer(Timer);

fn animate_sprite(
    time: Res<Time>,
    mut query: Query<(&mut AnimationTimer, &mut TextureAtlas)>,
) {
    for (mut timer, mut atlas) in &mut query {
        timer.0.tick(time.delta());
        if timer.0.just_finished() {
            atlas.index = (atlas.index + 1) % 8; // 8 frames loop
        }
    }
}
```

**Key Points**:
- `TextureAtlasLayout` defines grid or custom rectangles
- `TextureAtlas` component stores current frame index
- Use `Timer` for frame-based animation
- Bevy 0.15+ uses separate layout/atlas pattern

---

### 3. Godot 4.x (Built-in Atlas Support)

**Method A: AtlasTexture (Editor)**:
1. Import sprite sheet PNG
2. Create **AtlasTexture** resource
3. Set `atlas` to your PNG
4. Define `region` (x, y, w, h)
5. Assign to Sprite2D node

**Method B: AnimatedSprite2D**:
```gdscript
# res://player.gd
extends AnimatedSprite2D

func _ready():
    # Load sprite frames resource (created in editor)
    sprite_frames = load("res://assets/player_frames.tres")
    animation = "idle"
    play()

# player_frames.tres setup:
# 1. Create SpriteFrames resource
# 2. Add animation "idle"
# 3. Import frames from atlas with "Add Frames from Sprite Sheet"
# 4. Specify H/V frames or custom regions
```

**Method C: Code-based Atlas** (GDScript):
```gdscript
extends Sprite2D

var atlas_texture: Texture2D
var frames: Array = [
    Rect2(0, 0, 64, 64),
    Rect2(64, 0, 64, 64),
    Rect2(128, 0, 64, 64),
]
var current_frame := 0
var timer := 0.0

func _ready():
    atlas_texture = load("res://assets/spritesheet.png")
    texture = atlas_texture

func _process(delta):
    timer += delta
    if timer > 0.1:
        current_frame = (current_frame + 1) % frames.size()
        region_enabled = true
        region_rect = frames[current_frame]
        timer = 0.0
```

**Key Points**:
- Use `AnimatedSprite2D` for most cases (editor-friendly)
- `region_enabled` + `region_rect` for manual control
- Import settings: **Texture → 2D Pixels** for pixel art

---

## 🎨 Sprite Sheet Creation Tools

| Tool | Platform | Price | Best For | Export Formats |
|------|----------|-------|----------|----------------|
| **TexturePacker** | Win/Mac/Linux | Free/$40 | Professional workflows | JSON, XML, Cocos2d, Phaser, Unity |
| **Aseprite** | Win/Mac/Linux | $20 | Pixel art animation | JSON, PNG strips |
| **Free Texture Packer** | Web | Free | Quick web projects | JSON, CSS |
| **ShoeBox** | Adobe AIR | Free | Batch processing | Custom XML/JSON |
| **Kenney Asset Studio** | Win/Mac/Linux | Free | Kenney.nl assets only | PNG, JSON |
| **Godot Editor** | Built-in | Free | Godot projects | .tres (SpriteFrames) |

### Recommended Workflow
1. **For Kenney.nl Assets**: Use as-is (already optimized) or Kenney Asset Studio
2. **For Custom Pixel Art**: Aseprite → export sprite sheet with JSON
3. **For Unity Asset Store Sprites**: Manual extraction (see below)
4. **For Production**: TexturePacker (best packing algorithm, multiple formats)

---

## 📦 Working with Existing Assets

### Kenney.nl (CC0, Recommended)
- **Status**: Pre-packed sprite sheets with XML/JSON metadata
- **Example**: `characters.png` (1024×1024, 64 characters)
- **Usage**: Load directly, parse XML for coordinates
- **Rust parsing**: Use `quick-xml` or `serde_json` crate

### Unity Asset Store (⚠️ Avoid for Public Games)
**Extraction Script** (Unity Editor C#):
```csharp
using UnityEngine;
using UnityEditor;
using System.IO;

public class SpriteSheetExporter : EditorWindow {
    [MenuItem("Tools/Export Sprite Sheet")]
    static void Export() {
        var sprites = Selection.GetFiltered<Sprite>(SelectionMode.Assets);
        if (sprites.Length == 0) return;
        
        var texture = sprites[0].texture;
        var path = EditorUtility.SaveFilePanel("Export", "", "spritesheet.png", "png");
        
        // Copy texture to path
        File.WriteAllBytes(path, texture.EncodeToPNG());
        
        // Export metadata
        var json = "[";
        foreach (var s in sprites) {
            var r = s.textureRect;
            json += $"{{\"name\":\"{s.name}\",\"x\":{r.x},\"y\":{r.y},\"w\":{r.width},\"h\":{r.height}}},";
        }
        json = json.TrimEnd(',') + "]";
        File.WriteAllText(path + ".json", json);
    }
}
```
**⚠️ Legal Note**: Most Unity Asset Store licenses prohibit redistribution. Use only for private projects or local testing.

---

## 🎯 Best Practices

### 1. Texture Sizing
- **Power of 2**: 512, 1024, 2048 (GPU-friendly, though not strictly required on modern hardware)
- **Mobile**: Max 2048×2048 (some devices limit 4096)
- **Padding**: 1-2px between sprites to avoid bleeding

### 2. Format Selection
- **Pixel Art**: PNG-8, nearest neighbor filtering
- **Smooth Sprites**: PNG-24 with alpha
- **Large Atlases**: Use compression (WebP for web, ETC2/ASTC for mobile)

### 3. Animation Optimization
- **Frame Reuse**: Mirror/flip frames instead of duplicating
- **Variable FPS**: Slow down idle animations, speed up impacts
- **LOD**: Swap to simpler sprite sheets for distant objects

### 4. Memory Management
- **Lazy Loading**: Load atlases per-level, unload on scene change
- **Atlas Splitting**: Group by usage (UI, enemies, environment)
- **Mipmap Disable**: For pixel art and UI sprites

### 5. Development Workflow
```
1. Create sprites (Aseprite/Photoshop)
2. Export individual PNGs
3. Pack with TexturePacker → atlas.png + atlas.json
4. Load in engine with custom parser or plugin
5. Test on target devices (mobile = critical)
```

---

## 📚 Additional Resources

### Official Documentation
- [Macroquad Texture Docs](https://docs.rs/macroquad/latest/macroquad/texture/)
- [Bevy TextureAtlas Guide](https://bevyengine.org/examples/2d/texture-atlas/)
- [Godot AnimatedSprite2D](https://docs.godotengine.org/en/stable/classes/class_animatedsprite2d.html)

### Metadata Parsers
- **Rust**: `serde_json`, `quick-xml`, `ron`
- **Godot**: Built-in JSON parser, ResourceLoader

### Testing Assets
- [Kenney.nl Sprite Packs](https://kenney.nl/assets?q=2d) (CC0)
- [OpenGameArt](https://opengameart.org/) (various licenses)
- [itch.io Game Assets](https://itch.io/game-assets/free) (check licenses)

---

## ✅ Checklist for Implementation

- [ ] Choose sprite sheet tool based on workflow
- [ ] Set texture filter mode (Nearest for pixel art)
- [ ] Implement frame-based animation system
- [ ] Add padding to prevent texture bleeding
- [ ] Test on target platforms (mobile memory limits!)
- [ ] Profile draw calls (should see reduction with atlases)
- [ ] Document atlas structure for team (JSON format)
- [ ] Set up hot-reload for rapid iteration

---

## 🔗 See Also
- `game-dev-rust-godot/` - Main tech stack documentation
- `AGENTS.md` - Asset license policy (Kenney.nl CC0 only for public games)
- `/Volumes/workspace/Asset Store-5.x/` - Local Unity assets (private use only)

---

**Last Updated**: 2026-02-06  
**Maintained By**: Agent (kjaylee workspace)
