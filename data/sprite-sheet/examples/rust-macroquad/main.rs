// Macroquad Sprite Sheet Example
// Build: cargo build --target wasm32-unknown-unknown --release

use macroquad::prelude::*;

struct SpriteSheet {
    texture: Texture2D,
    frame_width: f32,
    frame_height: f32,
    columns: usize,
    rows: usize,
}

impl SpriteSheet {
    fn new(texture: Texture2D, frame_width: f32, frame_height: f32) -> Self {
        let columns = (texture.width() / frame_width) as usize;
        let rows = (texture.height() / frame_height) as usize;
        
        Self {
            texture,
            frame_width,
            frame_height,
            columns,
            rows,
        }
    }
    
    fn get_frame(&self, index: usize) -> Rect {
        let col = index % self.columns;
        let row = index / self.columns;
        
        Rect::new(
            col as f32 * self.frame_width,
            row as f32 * self.frame_height,
            self.frame_width,
            self.frame_height,
        )
    }
    
    fn draw(&self, frame: usize, x: f32, y: f32, scale: f32) {
        draw_texture_ex(
            &self.texture,
            x, y,
            WHITE,
            DrawTextureParams {
                source: Some(self.get_frame(frame)),
                dest_size: Some(vec2(
                    self.frame_width * scale,
                    self.frame_height * scale,
                )),
                ..Default::default()
            },
        );
    }
}

struct Animation {
    start_frame: usize,
    end_frame: usize,
    current_frame: usize,
    timer: f32,
    frame_duration: f32,
    looping: bool,
    playing: bool,
}

impl Animation {
    fn new(start: usize, end: usize, fps: f32, looping: bool) -> Self {
        Self {
            start_frame: start,
            end_frame: end,
            current_frame: start,
            timer: 0.0,
            frame_duration: 1.0 / fps,
            looping,
            playing: true,
        }
    }
    
    fn update(&mut self, dt: f32) {
        if !self.playing {
            return;
        }
        
        self.timer += dt;
        
        while self.timer >= self.frame_duration {
            self.timer -= self.frame_duration;
            
            if self.current_frame < self.end_frame {
                self.current_frame += 1;
            } else if self.looping {
                self.current_frame = self.start_frame;
            } else {
                self.playing = false;
            }
        }
    }
    
    fn reset(&mut self) {
        self.current_frame = self.start_frame;
        self.timer = 0.0;
        self.playing = true;
    }
}

#[macroquad::main("Sprite Animation Demo")]
async fn main() {
    // For this demo, we'll create a simple colored grid as placeholder
    // Replace with: load_texture("assets/character.png").await.unwrap()
    let texture = create_demo_texture();
    texture.set_filter(FilterMode::Nearest);
    
    let sprite_sheet = SpriteSheet::new(texture, 64.0, 64.0);
    
    // Define animations (frame ranges)
    let mut animations = vec![
        ("idle", Animation::new(0, 3, 8.0, true)),
        ("run", Animation::new(4, 11, 12.0, true)),
        ("jump", Animation::new(12, 15, 10.0, false)),
    ];
    
    let mut current_anim = 0;
    
    loop {
        clear_background(Color::from_rgba(40, 44, 52, 255));
        
        // Input switching
        if is_key_pressed(KeyCode::Key1) { current_anim = 0; animations[0].1.reset(); }
        if is_key_pressed(KeyCode::Key2) { current_anim = 1; animations[1].1.reset(); }
        if is_key_pressed(KeyCode::Key3) { current_anim = 2; animations[2].1.reset(); }
        
        // Update current animation
        let (_, anim) = &mut animations[current_anim];
        anim.update(get_frame_time());
        
        // Draw sprite
        let screen_center_x = screen_width() / 2.0 - 32.0 * 2.0;
        let screen_center_y = screen_height() / 2.0 - 32.0 * 2.0;
        
        sprite_sheet.draw(
            anim.current_frame,
            screen_center_x,
            screen_center_y,
            2.0, // 2x scale
        );
        
        // UI
        draw_text("Sprite Sheet Animation Demo", 20.0, 30.0, 30.0, WHITE);
        draw_text(&format!("Animation: {} (Frame {})", 
            animations[current_anim].0, anim.current_frame), 
            20.0, 60.0, 20.0, LIGHTGRAY);
        draw_text("Press 1: Idle | 2: Run | 3: Jump", 20.0, 90.0, 20.0, LIGHTGRAY);
        draw_text(&format!("FPS: {:.0}", get_fps()), 20.0, screen_height() - 20.0, 20.0, GRAY);
        
        next_frame().await
    }
}

// Helper: Create demo texture (4x4 grid of colored squares)
fn create_demo_texture() -> Texture2D {
    let size = 256;
    let mut pixels = vec![0u8; size * size * 4];
    
    let colors = [
        [255, 100, 100, 255], // Red
        [100, 255, 100, 255], // Green
        [100, 100, 255, 255], // Blue
        [255, 255, 100, 255], // Yellow
    ];
    
    for frame_idx in 0..16 {
        let frame_x = (frame_idx % 4) * 64;
        let frame_y = (frame_idx / 4) * 64;
        let color = &colors[frame_idx % 4];
        
        for y in 0..64 {
            for x in 0..64 {
                let px = frame_x + x;
                let py = frame_y + y;
                let idx = (py * size + px) * 4;
                
                if idx + 3 < pixels.len() {
                    pixels[idx..idx + 4].copy_from_slice(color);
                }
            }
        }
    }
    
    Texture2D::from_rgba8(size as u16, size as u16, &pixels)
}
