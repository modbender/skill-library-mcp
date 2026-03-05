# Bevy Sprite Sheet Reference (0.15+)

## Basic Setup

```rust
use bevy::prelude::*;

fn setup(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
    mut layouts: ResMut<Assets<TextureAtlasLayout>>,
) {
    // Grid-based atlas (uniform frames)
    let layout = TextureAtlasLayout::from_grid(
        UVec2::new(64, 64), // frame size
        8, 4,               // columns, rows
        None,               // padding
        None,               // offset
    );
    let layout_handle = layouts.add(layout);
    
    commands.spawn((
        Sprite::from_atlas_image(
            asset_server.load("sprites/player.png"),
            TextureAtlas {
                layout: layout_handle,
                index: 0,
            },
        ),
        Transform::from_xyz(0.0, 0.0, 0.0),
    ));
}
```

## Custom Atlas (Irregular Frames)

```rust
use bevy::math::URect;

// Define custom rectangles
let layout = TextureAtlasLayout::from_textures(&[
    URect::new(0, 0, 64, 64),
    URect::new(64, 0, 48, 64),
    URect::new(112, 0, 32, 32),
]);
```

## Animation Component

```rust
#[derive(Component)]
struct AnimationIndices {
    first: usize,
    last: usize,
}

#[derive(Component, Deref, DerefMut)]
struct AnimationTimer(Timer);

fn animate_sprite(
    time: Res<Time>,
    mut query: Query<(&AnimationIndices, &mut AnimationTimer, &mut TextureAtlas)>,
) {
    for (indices, mut timer, mut atlas) in &mut query {
        timer.tick(time.delta());
        if timer.just_finished() {
            atlas.index = if atlas.index == indices.last {
                indices.first
            } else {
                atlas.index + 1
            };
        }
    }
}

// Spawn with animation
commands.spawn((
    Sprite::from_atlas_image(...),
    AnimationIndices { first: 0, last: 7 },
    AnimationTimer(Timer::from_seconds(0.1, TimerMode::Repeating)),
));
```

## State Machine Integration

```rust
#[derive(Component)]
struct AnimationState {
    animations: HashMap<PlayerState, (usize, usize)>, // state -> (first, last)
    current_state: PlayerState,
}

#[derive(Eq, PartialEq, Hash)]
enum PlayerState {
    Idle,
    Running,
    Jumping,
}

fn update_animation_state(
    mut query: Query<(&AnimationState, &mut AnimationIndices)>,
) {
    for (state, mut indices) in &mut query {
        if let Some(&(first, last)) = state.animations.get(&state.current_state) {
            if indices.first != first {
                indices.first = first;
                indices.last = last;
            }
        }
    }
}
```

## Cargo.toml

```toml
[dependencies]
bevy = "0.15"

[profile.wasm-release]
inherits = "release"
opt-level = "z"
lto = "fat"
codegen-units = 1
```

## WASM Build

```bash
cargo build --release --target wasm32-unknown-unknown
wasm-bindgen --out-dir ./out/ --target web \
  ./target/wasm32-unknown-unknown/release/game.wasm
```

## Performance Considerations

1. **Minimize Layouts**: Reuse `TextureAtlasLayout` handles across entities
2. **Change Detection**: Bevy only updates GPU when `TextureAtlas::index` changes
3. **Batching**: Entities with same texture + layout batch automatically
4. **Asset Loading**: Use `AssetServer::load_folder()` for bulk loads
