# Unity .meta File Parsing Examples

## Overview

Unity stores sprite sheet metadata in `.meta` files (YAML format). This directory contains a Python parser that extracts sprite coordinates **without requiring Unity Editor**.

## Quick Start

```bash
# JSON output (default)
python3 unity_meta_parser.py path/to/sprite.png.meta

# Rust code output
python3 unity_meta_parser.py path/to/sprite.png.meta --rust

# Save to file
python3 unity_meta_parser.py sprite.png.meta --json > output.json
```

## Examples Included

### 1. wizard_walk_example.json
**Source**: Unity Asset Store - "Monster Survivors - Full Game"  
**Type**: Horizontal sprite strip  
**Specs**:
- 5 frames
- 512×512 pixels per frame
- Total: 2560×512 px
- Alignment: Bottom (pivot_y: 0)
- pixels_per_unit: 500

**Layout**:
```
[Frame0][Frame1][Frame2][Frame3][Frame4]
0       512    1024    1536    2048
```

### 2. wizard_walk_example.rs
**Purpose**: Rust struct initialization code  
**Usage**: Copy into your Rust game project  

```rust
// Define the struct first
#[derive(Debug, Clone)]
pub struct SpriteFrame {
    pub name: &'static str,
    pub x: i32,
    pub y: i32,
    pub width: i32,
    pub height: i32,
    pub pivot_x: f32,
    pub pivot_y: f32,
}

// Then use the generated constant
pub const SPRITE_FRAMES: &[SpriteFrame] = &[
    SpriteFrame { name: "wizard_walk_new_0", x: 0, y: 0, ... },
    // ...
];

// In your game loop
let frame = SPRITE_FRAMES[current_frame];
draw_texture_ex(
    &texture,
    x, y,
    WHITE,
    DrawTextureParams {
        source: Some(Rect::new(
            frame.x as f32,
            frame.y as f32,
            frame.width as f32,
            frame.height as f32,
        )),
        ..Default::default()
    },
);
```

## Unity .meta File Structure

### Basic Structure
```yaml
fileFormatVersion: 2
guid: 73c913de14d5d46419b410b591dfea42
TextureImporter:
  spriteMode: 2  # 1=Single, 2=Multiple, 3=Polygon
  spritePixelsToUnits: 500
  spriteSheet:
    serializedVersion: 2
    sprites:
    - serializedVersion: 2
      name: sprite_name_0
      rect:
        x: 0
        y: 0
        width: 512
        height: 512
      alignment: 7
      pivot: {x: 0.5, y: 0}
      border: {x: 0, y: 0, z: 0, w: 0}
      spriteID: ...
      internalID: -388209903
```

### Key Fields

| Field | Description | Values |
|-------|-------------|--------|
| `spriteMode` | Texture type | 1=Single, 2=Multiple (sprite sheet), 3=Polygon |
| `spritePixelsToUnits` | Unity units per pixel | Typically 100 or 500 |
| `rect` | Sprite position/size | {x, y, width, height} in pixels |
| `alignment` | Pivot preset | 0=Center, 1=TopLeft, 7=Bottom, etc. |
| `pivot` | Custom pivot point | {x: 0-1, y: 0-1}, (0,0)=bottom-left |
| `border` | 9-slice borders | {x=left, y=bottom, z=right, w=top} |

### Alignment Codes
```
0 = Center
1 = Top Left
2 = Top
3 = Top Right
4 = Left
5 = Right
6 = Bottom Left
7 = Bottom
8 = Bottom Right
9 = Custom (uses pivot)
```

### Grid Slicing Metadata
Some .meta files include grid slicing information:

```yaml
spriteCustomMetadata:
  entries:
  - key: SpriteEditor.SliceSettings
    value: '{"gridCellCount":{"x":8,"y":4},"gridSpriteSize":{"x":256,"y":256},...}'
```

The parser extracts this into `slice_settings`:
```json
{
  "slice_settings": {
    "grid_cell_count": {"x": 8, "y": 4},
    "grid_sprite_size": {"x": 256, "y": 256},
    "grid_sprite_offset": {"x": 0, "y": 0},
    "grid_sprite_padding": {"x": 2, "y": 2},
    "slicing_type": 1
  }
}
```

## Common Sprite Sheet Patterns

### Pattern 1: Horizontal Strip
```
[Frame0][Frame1][Frame2][Frame3]
```
- Simplest to calculate: `x = frame_index * frame_width`
- Common for walk cycles (4-8 frames)
- Example: `wizard_walk_example.json`

### Pattern 2: Grid Layout
```
[0][1][2][3]
[4][5][6][7]
[8][9][A][B]
```
- Better for many frames (16+)
- Calculate: 
  ```rust
  let row = frame_index / columns;
  let col = frame_index % columns;
  let x = col * frame_width;
  let y = row * frame_height;
  ```

### Pattern 3: Atlas (Irregular)
```
[Small][Big    ]
[    ][Sprite  ]
[Mid ][        ]
```
- Non-uniform frame sizes
- Requires metadata for each frame
- Most efficient packing

## Workflow: Unity Asset → Rust Game

### Step 1: Locate the .meta file
```bash
# In Unity project
find . -name "*.png.meta" | grep character
# → Assets/Sprites/character_walk.png.meta
```

### Step 2: Extract sprite data
```bash
python3 unity_meta_parser.py Assets/Sprites/character_walk.png.meta --rust > src/sprites.rs
```

### Step 3: Copy the source PNG
```bash
cp Assets/Sprites/character_walk.png rust_game/assets/
```

### Step 4: Use in Rust
```rust
// src/sprites.rs (generated)
include!("sprites.rs");

// src/main.rs
#[macroquad::main("Game")]
async fn main() {
    let texture = load_texture("assets/character_walk.png").await.unwrap();
    
    for frame in SPRITE_FRAMES.iter() {
        draw_texture_ex(&texture, 100.0, 100.0, WHITE, DrawTextureParams {
            source: Some(Rect::new(frame.x as f32, frame.y as f32, 
                                   frame.width as f32, frame.height as f32)),
            ..Default::default()
        });
    }
}
```

## Batch Processing

### Extract all sprite sheets in a project
```bash
#!/bin/bash
find /path/to/unity/Assets -name "*.png.meta" | while read meta; do
    png="${meta%.meta}"
    name=$(basename "$png" .png)
    
    # Parse metadata
    python3 unity_meta_parser.py "$meta" > "output/${name}.json"
    
    # Copy texture
    cp "$png" "output/${name}.png"
done
```

### Generate Rust module for entire project
```bash
#!/bin/bash
echo "// Auto-generated sprite data" > sprites.rs
echo "" >> sprites.rs

find Assets -name "*.png.meta" | while read meta; do
    python3 unity_meta_parser.py "$meta" --rust >> sprites.rs
    echo "" >> sprites.rs
done
```

## Troubleshooting

### "No TextureImporter section found"
- File is not a texture .meta file
- Solution: Check that you're parsing a PNG/JPG .meta, not a script or prefab

### "spriteMode is 1 (not Multiple/2)"
- Texture is set to "Single" sprite mode in Unity
- Solution: In Unity, change Texture Type to "Sprite (2D and UI)" and Sprite Mode to "Multiple"

### "No sprites found in spriteSheet section"
- Sprite sheet hasn't been sliced yet in Unity
- Solution: Use Unity's Sprite Editor to define sprite rectangles, or manually add to .meta file

### Coordinates seem wrong (off by a few pixels)
- Check `spritePixelsToUnits` ratio
- Unity's coordinate system: bottom-left origin (0,0)
- Game engine coordinate system: may be top-left
- Solution: You may need to flip Y coordinate: `y = texture_height - rect.y - rect.height`

## Advanced: Manual .meta Creation

You can create .meta files manually for non-Unity sprite sheets:

```yaml
fileFormatVersion: 2
guid: YOUR_GUID_HERE
TextureImporter:
  spriteMode: 2
  spritePixelsToUnits: 100
  spriteSheet:
    sprites:
    - name: frame_0
      rect: {x: 0, y: 0, width: 64, height: 64}
      pivot: {x: 0.5, y: 0.5}
      alignment: 0
      border: {x: 0, y: 0, z: 0, w: 0}
    - name: frame_1
      rect: {x: 64, y: 0, width: 64, height: 64}
      pivot: {x: 0.5, y: 0.5}
      alignment: 0
      border: {x: 0, y: 0, z: 0, w: 0}
```

Generate GUID:
```python
import uuid
print(str(uuid.uuid4()).replace('-', ''))
```

## Dependencies

The parser requires:
```bash
pip install pyyaml
```

Or use the project's requirements:
```bash
pip install -r requirements.txt
```

## License & Legal

**Parser Script**: MIT License (free to use)

**Unity .meta Files**: Metadata generated by Unity Editor
- Safe to parse for private projects
- Do not redistribute Unity Asset Store assets (check individual licenses)

**Best Practice for Public Projects**:
- Use Kenney.nl (CC0) or self-created assets
- Unity Asset Store assets → private projects only
- Always verify asset license before redistribution

## See Also

- [SKILL.md](../SKILL.md) - Full sprite sheet guide
- [unity-asset-extraction.md](../unity-asset-extraction.md) - Detailed Unity workflow
- [Macroquad Texture Docs](https://docs.rs/macroquad/latest/macroquad/texture/)
- [Unity TextureImporter](https://docs.unity3d.com/ScriptReference/TextureImporter.html)

---

**Last Updated**: 2026-02-06  
**Maintainer**: Agent (kjaylee workspace)
