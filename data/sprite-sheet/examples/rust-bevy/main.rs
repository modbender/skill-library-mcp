// Bevy 0.15 Sprite Sheet Example
// Run: cargo run

use bevy::prelude::*;
use std::collections::HashMap;

fn main() {
    App::new()
        .add_plugins(DefaultPlugins.set(ImagePlugin::default_nearest()))
        .add_systems(Startup, setup)
        .add_systems(Update, (animate_sprite, handle_input))
        .run();
}

#[derive(Component)]
struct AnimationLibrary {
    animations: HashMap<AnimationState, AnimationClip>,
    current_state: AnimationState,
}

#[derive(Clone, Copy, PartialEq, Eq, Hash, Debug)]
enum AnimationState {
    Idle,
    Run,
    Jump,
}

#[derive(Clone)]
struct AnimationClip {
    first_frame: usize,
    last_frame: usize,
    fps: f32,
    looping: bool,
}

#[derive(Component)]
struct AnimationTimer {
    timer: Timer,
}

fn setup(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
    mut texture_atlas_layouts: ResMut<Assets<TextureAtlasLayout>>,
) {
    commands.spawn(Camera2d);
    
    // Create atlas layout (4x4 grid, 64x64 frames)
    let layout = TextureAtlasLayout::from_grid(
        UVec2::new(64, 64),
        4, 4,
        None, None,
    );
    let layout_handle = texture_atlas_layouts.add(layout);
    
    // Define animation clips
    let mut animations = HashMap::new();
    animations.insert(
        AnimationState::Idle,
        AnimationClip {
            first_frame: 0,
            last_frame: 3,
            fps: 8.0,
            looping: true,
        },
    );
    animations.insert(
        AnimationState::Run,
        AnimationClip {
            first_frame: 4,
            last_frame: 11,
            fps: 12.0,
            looping: true,
        },
    );
    animations.insert(
        AnimationState::Jump,
        AnimationClip {
            first_frame: 12,
            last_frame: 15,
            fps: 10.0,
            looping: false,
        },
    );
    
    let initial_state = AnimationState::Idle;
    let initial_clip = animations.get(&initial_state).unwrap();
    
    // Spawn character sprite
    commands.spawn((
        Sprite {
            image: asset_server.load("sprites/character.png"), // Replace with demo texture
            texture_atlas: Some(TextureAtlas {
                layout: layout_handle,
                index: initial_clip.first_frame,
            }),
            ..default()
        },
        Transform::from_xyz(0.0, 0.0, 0.0).with_scale(Vec3::splat(2.0)),
        AnimationLibrary {
            animations,
            current_state: initial_state,
        },
        AnimationTimer {
            timer: Timer::from_seconds(1.0 / initial_clip.fps, TimerMode::Repeating),
        },
    ));
    
    // UI Text
    commands.spawn((
        Text::new("Bevy Sprite Animation Demo\nPress 1: Idle | 2: Run | 3: Jump"),
        Node {
            position_type: PositionType::Absolute,
            top: Val::Px(20.0),
            left: Val::Px(20.0),
            ..default()
        },
    ));
}

fn animate_sprite(
    time: Res<Time>,
    mut query: Query<(
        &mut Sprite,
        &AnimationLibrary,
        &mut AnimationTimer,
    )>,
) {
    for (mut sprite, library, mut anim_timer) in &mut query {
        anim_timer.timer.tick(time.delta());
        
        if anim_timer.timer.just_finished() {
            if let Some(atlas) = &mut sprite.texture_atlas {
                let clip = library.animations.get(&library.current_state).unwrap();
                
                if atlas.index < clip.last_frame {
                    atlas.index += 1;
                } else if clip.looping {
                    atlas.index = clip.first_frame;
                }
            }
        }
    }
}

fn handle_input(
    keyboard: Res<ButtonInput<KeyCode>>,
    mut query: Query<(
        &mut Sprite,
        &mut AnimationLibrary,
        &mut AnimationTimer,
    )>,
) {
    for (mut sprite, mut library, mut anim_timer) in &mut query {
        let new_state = if keyboard.just_pressed(KeyCode::Digit1) {
            Some(AnimationState::Idle)
        } else if keyboard.just_pressed(KeyCode::Digit2) {
            Some(AnimationState::Run)
        } else if keyboard.just_pressed(KeyCode::Digit3) {
            Some(AnimationState::Jump)
        } else {
            None
        };
        
        if let Some(state) = new_state {
            if library.current_state != state {
                library.current_state = state;
                let clip = library.animations.get(&state).unwrap();
                
                // Reset animation
                if let Some(atlas) = &mut sprite.texture_atlas {
                    atlas.index = clip.first_frame;
                }
                anim_timer.timer = Timer::from_seconds(
                    1.0 / clip.fps,
                    TimerMode::Repeating,
                );
            }
        }
    }
}
