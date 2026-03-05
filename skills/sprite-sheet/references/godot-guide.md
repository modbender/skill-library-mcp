# Godot 4.x Sprite Sheet Reference

## Method 1: AnimatedSprite2D (Recommended)

### Editor Workflow
1. **Import Sprite Sheet**
   - Drag PNG into FileSystem
   - Import tab → **Texture → 2D Pixels** (for pixel art)
   - Disable **Filter** for sharp pixels

2. **Create SpriteFrames Resource**
   - Right-click → New Resource → `SpriteFrames`
   - Save as `player_animations.tres`

3. **Add Frames from Atlas**
   - Open SpriteFrames editor (bottom panel)
   - Animation → **New** → Name: "idle"
   - **Add Frames from Sprite Sheet** button
   - Select your atlas PNG
   - Configure grid:
     - **Horizontal**: 8 (columns)
     - **Vertical**: 4 (rows)
     - Or use **Select Frames** for custom regions
   - Select frames to import

4. **Setup Node**
   ```gdscript
   # player.gd
   extends AnimatedSprite2D
   
   func _ready():
       sprite_frames = load("res://assets/player_animations.tres")
       animation = "idle"
       frame = 0
       play()
   
   func set_animation_state(state: String):
       if animation != state:
           animation = state
           play()
   ```

### Script-Only Workflow

```gdscript
extends AnimatedSprite2D

func _ready():
    var frames = SpriteFrames.new()
    
    # Create animation
    frames.add_animation("run")
    frames.set_animation_speed("run", 12.0)
    
    # Load atlas
    var atlas_texture = load("res://assets/character.png")
    
    # Add individual frames (manual cropping)
    for i in range(8):
        var atlas = AtlasTexture.new()
        atlas.atlas = atlas_texture
        atlas.region = Rect2(i * 64, 0, 64, 64)
        frames.add_frame("run", atlas)
    
    sprite_frames = frames
    play("run")
```

---

## Method 2: Sprite2D with Region

```gdscript
extends Sprite2D

@export var atlas_texture: Texture2D
@export var frame_width := 64
@export var frame_height := 64
@export var fps := 12.0

var frames: Array[Rect2] = []
var current_frame := 0
var time_accumulator := 0.0

func _ready():
    texture = atlas_texture
    region_enabled = true
    
    # Auto-generate grid frames
    var cols = texture.get_width() / frame_width
    var rows = texture.get_height() / frame_height
    
    for row in range(rows):
        for col in range(cols):
            frames.append(Rect2(
                col * frame_width,
                row * frame_height,
                frame_width,
                frame_height
            ))
    
    region_rect = frames[0]

func _process(delta):
    time_accumulator += delta
    var frame_duration = 1.0 / fps
    
    if time_accumulator >= frame_duration:
        time_accumulator -= frame_duration
        current_frame = (current_frame + 1) % frames.size()
        region_rect = frames[current_frame]
```

---

## Method 3: JSON Metadata Loading

```gdscript
# atlas_loader.gd
class_name AtlasLoader

static func load_from_json(texture_path: String, json_path: String) -> Dictionary:
    var atlas_texture = load(texture_path)
    var file = FileAccess.open(json_path, FileAccess.READ)
    var json = JSON.parse_string(file.get_as_text())
    
    var frames_dict = {}
    
    for frame_data in json.frames:
        var atlas = AtlasTexture.new()
        atlas.atlas = atlas_texture
        atlas.region = Rect2(
            frame_data.x,
            frame_data.y,
            frame_data.w,
            frame_data.h
        )
        frames_dict[frame_data.name] = atlas
    
    return frames_dict

# Usage:
var frames = AtlasLoader.load_from_json(
    "res://assets/sprites.png",
    "res://assets/sprites.json"
)
$Sprite2D.texture = frames["player_idle_01"]
```

---

## TexturePacker JSON Format (Compatible)

```json
{
  "frames": [
    {
      "name": "player_idle_01",
      "x": 0,
      "y": 0,
      "w": 64,
      "h": 64
    }
  ],
  "meta": {
    "size": { "w": 1024, "h": 1024 }
  }
}
```

---

## Performance Tips

1. **Texture Import Settings**
   - Pixel Art: `Texture → 2D Pixels`, **Filter OFF**
   - Smooth: `Texture → 2D`, **Filter ON**
   - Mobile: Enable **VRAM Compression → BPTC** (desktop) or **ETC2** (mobile)

2. **SpriteFrames Optimization**
   - Share `SpriteFrames` resources across multiple nodes
   - Use `duplicate()` for instances with different playback states

3. **Batching**
   - Keep sprites on same Z-index layer
   - Use CanvasGroup for batch rendering control
   - Avoid frequent texture swaps

4. **Memory**
   - Unload unused animations: `sprite_frames.remove_animation("boss")`
   - Use `ResourceLoader.load_threaded_request()` for async loading

---

## Export Settings (HTML5)

**Project → Export → Web**:
- **Texture Format**: `ETC2` or `S3TC`
- **Vram Texture Compression**: **For Desktop** (BPTC), **For Mobile** (ETC2)
- **Export Type**: **Regular** (not threads for iOS)

---

## See Also
- [Godot AnimatedSprite2D Docs](https://docs.godotengine.org/en/stable/classes/class_animatedsprite2d.html)
- [AtlasTexture API](https://docs.godotengine.org/en/stable/classes/class_atlastexture.html)
- [2D Sprite Animation Tutorial](https://docs.godotengine.org/en/stable/tutorials/2d/2d_sprite_animation.html)
