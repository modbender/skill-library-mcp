# Macroquad Sprite Sheet Reference

## Quick Start

```rust
use macroquad::prelude::*;
use serde::Deserialize;

#[derive(Deserialize)]
struct AtlasFrame {
    name: String,
    x: f32,
    y: f32,
    w: f32,
    h: f32,
}

#[derive(Deserialize)]
struct Atlas {
    frames: Vec<AtlasFrame>,
}

async fn load_atlas(png_path: &str, json_path: &str) -> (Texture2D, Atlas) {
    let texture = load_texture(png_path).await.unwrap();
    let json = load_string(json_path).await.unwrap();
    let atlas: Atlas = serde_json::from_str(&json).unwrap();
    (texture, atlas)
}
```

## Animation System

```rust
struct Animation {
    frames: Vec<Rect>,
    current: usize,
    timer: f32,
    fps: f32,
}

impl Animation {
    fn new(atlas: &Atlas, prefix: &str, fps: f32) -> Self {
        let frames: Vec<Rect> = atlas.frames.iter()
            .filter(|f| f.name.starts_with(prefix))
            .map(|f| Rect::new(f.x, f.y, f.w, f.h))
            .collect();
        
        Self {
            frames,
            current: 0,
            timer: 0.0,
            fps,
        }
    }
    
    fn update(&mut self, dt: f32) {
        self.timer += dt;
        let frame_duration = 1.0 / self.fps;
        
        while self.timer >= frame_duration {
            self.timer -= frame_duration;
            self.current = (self.current + 1) % self.frames.len();
        }
    }
    
    fn current_frame(&self) -> Rect {
        self.frames[self.current]
    }
}

// Usage:
let mut anim = Animation::new(&atlas, "player_run_", 12.0);

loop {
    anim.update(get_frame_time());
    draw_texture_ex(
        &texture,
        x, y,
        WHITE,
        DrawTextureParams {
            source: Some(anim.current_frame()),
            ..Default::default()
        },
    );
    next_frame().await
}
```

## Cargo.toml Dependencies

```toml
[dependencies]
macroquad = "0.4"
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
```

## WASM Build

```bash
cargo build --target wasm32-unknown-unknown --release
cp target/wasm32-unknown-unknown/release/game.wasm web/
```

## Performance Tips

1. **Texture Filtering**: Use `set_filter(FilterMode::Nearest)` for pixel art
2. **Batch Drawing**: Group sprites by texture to minimize state changes
3. **Preload**: Load all textures during init, not during gameplay
4. **Asset Size**: Keep total WASM + assets under 5MB for web games
