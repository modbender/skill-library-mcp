# Rust + Macroquad 상세 가이드

Macroquad는 Rust로 간단한 2D 게임을 만들기 위한 경량 프레임워크. 빠른 빌드(16초), 작은 WASM(567KB), 직관적인 API가 장점.

## 프로젝트 구조

```
game-name/
├── Cargo.toml
├── src/
│   └── main.rs
├── assets/          # 에셋 폴더
│   ├── images/
│   ├── sounds/
│   └── fonts/
├── index.html       # 빌드 후 생성
├── game-name.wasm   # 빌드 결과물
└── mq_js_bundle.js  # Macroquad JS 바인딩
```

## Cargo.toml 설정

```toml
[package]
name = "game-name"
version = "0.1.0"
edition = "2021"

[dependencies]
macroquad = "0.4"

# 추가 기능 (필요 시)
macroquad-audio = "0.2"  # 사운드
quad-rand = "0.2"        # 랜덤

[profile.release]
opt-level = "z"          # 최소 크기
lto = true               # Link Time Optimization
codegen-units = 1        # 단일 코드젠 유닛
strip = true             # 디버그 정보 제거
```

## 기본 게임 루프

```rust
use macroquad::prelude::*;

#[macroquad::main("Game Title")]
async fn main() {
    loop {
        // 1. 입력 처리
        if is_key_down(KeyCode::Right) {
            // 오른쪽 이동
        }
        
        // 2. 게임 로직 업데이트
        update_game_state();
        
        // 3. 화면 그리기
        clear_background(BLACK);
        draw_rectangle(100.0, 100.0, 50.0, 50.0, RED);
        
        // 4. 다음 프레임 대기
        next_frame().await
    }
}

fn update_game_state() {
    // 게임 상태 업데이트
}
```

## 에셋 로딩

### 이미지

```rust
use macroquad::prelude::*;

// 전역 또는 구조체에 저장
struct Assets {
    player_texture: Texture2D,
    enemy_texture: Texture2D,
}

async fn load_assets() -> Assets {
    Assets {
        player_texture: load_texture("assets/images/player.png").await.unwrap(),
        enemy_texture: load_texture("assets/images/enemy.png").await.unwrap(),
    }
}

#[macroquad::main("My Game")]
async fn main() {
    let assets = load_assets().await;
    
    loop {
        clear_background(BLACK);
        
        // 텍스처 그리기
        draw_texture(&assets.player_texture, 100.0, 100.0, WHITE);
        
        next_frame().await
    }
}
```

### 사운드 (macroquad-audio)

```rust
use macroquad::prelude::*;
use macroquad::audio::{load_sound, play_sound, PlaySoundParams};

async fn load_sounds() -> (Sound, Sound) {
    let bgm = load_sound("assets/sounds/bgm.ogg").await.unwrap();
    let sfx_jump = load_sound("assets/sounds/jump.wav").await.unwrap();
    (bgm, sfx_jump)
}

#[macroquad::main("My Game")]
async fn main() {
    let (bgm, sfx_jump) = load_sounds().await;
    
    // BGM 반복 재생
    play_sound(
        &bgm,
        PlaySoundParams {
            looped: true,
            volume: 0.5,
        },
    );
    
    loop {
        // 점프 시 SFX 재생
        if is_key_pressed(KeyCode::Space) {
            play_sound(&sfx_jump, PlaySoundParams::default());
        }
        
        next_frame().await
    }
}
```

## 입력 처리

### 키보드

```rust
// 키 누름 (한 번만 반응)
if is_key_pressed(KeyCode::Space) {
    jump();
}

// 키 누르는 중 (연속 반응)
if is_key_down(KeyCode::Right) {
    move_right();
}

// 키 뗌
if is_key_released(KeyCode::Escape) {
    pause_game();
}
```

### 마우스/터치

```rust
// 마우스 위치
let (mouse_x, mouse_y) = mouse_position();

// 마우스 클릭
if is_mouse_button_pressed(MouseButton::Left) {
    shoot(mouse_x, mouse_y);
}

// 터치 (모바일)
for touch in touches() {
    println!("Touch at: {} {}", touch.position.x, touch.position.y);
}
```

### 스와이프 감지 (모바일)

```rust
struct SwipeDetector {
    start_pos: Option<Vec2>,
    threshold: f32,
}

impl SwipeDetector {
    fn new() -> Self {
        Self {
            start_pos: None,
            threshold: 30.0,
        }
    }
    
    fn update(&mut self) -> Option<Direction> {
        let touches_list = touches();
        
        if touches_list.is_empty() {
            self.start_pos = None;
            return None;
        }
        
        let current_pos = touches_list[0].position;
        
        if self.start_pos.is_none() {
            self.start_pos = Some(current_pos);
            return None;
        }
        
        let delta = current_pos - self.start_pos.unwrap();
        
        if delta.length() > self.threshold {
            let direction = if delta.x.abs() > delta.y.abs() {
                if delta.x > 0.0 { Direction::Right } else { Direction::Left }
            } else {
                if delta.y > 0.0 { Direction::Down } else { Direction::Up }
            };
            self.start_pos = Some(current_pos);
            return Some(direction);
        }
        
        None
    }
}

enum Direction {
    Up, Down, Left, Right,
}
```

## 그리기

### 기본 도형

```rust
// 사각형
draw_rectangle(x, y, width, height, color);

// 원
draw_circle(x, y, radius, color);

// 선
draw_line(x1, y1, x2, y2, thickness, color);

// 텍스트
draw_text("Score: 100", x, y, font_size, color);
```

### 텍스처

```rust
// 기본 텍스처 그리기
draw_texture(&texture, x, y, WHITE);

// 회전/크기 조절
draw_texture_ex(
    &texture,
    x, y,
    WHITE,
    DrawTextureParams {
        rotation: angle,
        dest_size: Some(vec2(width, height)),
        ..Default::default()
    },
);

// 텍스처 일부만 그리기 (스프라이트시트)
let source_rect = Rect::new(src_x, src_y, src_w, src_h);
draw_texture_ex(
    &spritesheet,
    x, y,
    WHITE,
    DrawTextureParams {
        source: Some(source_rect),
        ..Default::default()
    },
);
```

## 충돌 감지

```rust
struct Entity {
    x: f32,
    y: f32,
    width: f32,
    height: f32,
}

impl Entity {
    fn rect(&self) -> Rect {
        Rect::new(self.x, self.y, self.width, self.height)
    }
    
    fn collides_with(&self, other: &Entity) -> bool {
        self.rect().overlaps(&other.rect())
    }
}

// 사용 예시
if player.collides_with(&enemy) {
    game_over();
}
```

## 게임 상태 관리

```rust
enum GameState {
    Menu,
    Playing,
    Paused,
    GameOver,
}

struct Game {
    state: GameState,
    score: i32,
    // ...
}

#[macroquad::main("My Game")]
async fn main() {
    let mut game = Game {
        state: GameState::Menu,
        score: 0,
    };
    
    loop {
        match game.state {
            GameState::Menu => {
                draw_menu();
                if is_key_pressed(KeyCode::Enter) {
                    game.state = GameState::Playing;
                }
            },
            GameState::Playing => {
                update_game(&mut game);
                draw_game(&game);
            },
            GameState::Paused => {
                draw_pause_menu();
            },
            GameState::GameOver => {
                draw_game_over(&game);
            },
        }
        
        next_frame().await
    }
}
```

## 빌드 & 배포

### WASM 빌드 (MiniPC)

```bash
cd $HOME/spritz/dynamic/games/<game-name>

# 릴리즈 빌드
cargo build --release --target wasm32-unknown-unknown

# WASM 파일 복사
cp target/wasm32-unknown-unknown/release/<game-name>.wasm .

# Macroquad가 자동으로 index.html, mq_js_bundle.js 제공
```

### index.html (자동 생성)

Macroquad는 빌드 시 자동으로 `index.html`을 생성하지 않으므로 직접 작성:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Game Title</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <style>
        body {
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: #0f172a;
        }
        #glcanvas {
            width: 90vw;
            height: 90vh;
            max-width: 800px;
            max-height: 800px;
            display: block;
        }
    </style>
</head>
<body>
    <canvas id="glcanvas" tabindex='1'></canvas>
    <script src="mq_js_bundle.js"></script>
    <script>
        load("game-name.wasm");
    </script>
</body>
</html>
```

**mq_js_bundle.js 다운로드**:
```bash
wget https://github.com/not-fl3/macroquad/releases/download/v0.4.0/mq_js_bundle.js
```

### 모바일 최적화

```rust
// 화면 크기에 맞춘 렌더링
let (screen_w, screen_h) = (screen_width(), screen_height());
let scale = (screen_w / 800.0).min(screen_h / 600.0);

// DPI 고려
set_camera(&Camera2D {
    zoom: vec2(2.0 / screen_width(), -2.0 / screen_height()),
    ..Default::default()
});
```

## 성능 팁

1. **텍스처 미리 로딩**: `async fn main()` 시작 시 모든 텍스처 로딩
2. **객체 풀링**: `Vec<Enemy>`를 미리 할당, 재사용
3. **불필요한 그리기 방지**: 화면 밖 객체는 그리지 않기
4. **릴리즈 빌드**: `cargo build --release`로 최적화
5. **프로파일링**: `opt-level = "z"`, `lto = true` 설정

## 디버깅

### 콘솔 출력

```rust
println!("Player position: {} {}", player.x, player.y);  // Rust 콘솔
macroquad::logging::info!("Score: {}", score);           // 브라우저 콘솔
```

### 브라우저 개발자 도구

1. Chrome/Firefox 개발자 도구 열기 (F12)
2. Console 탭에서 에러 확인
3. Network 탭에서 에셋 로딩 확인

## 예시 프로젝트

### Snake 게임 (최소 구조)

```rust
use macroquad::prelude::*;

struct Snake {
    body: Vec<Vec2>,
    direction: Vec2,
}

struct Food {
    pos: Vec2,
}

#[macroquad::main("Snake")]
async fn main() {
    let mut snake = Snake {
        body: vec![vec2(5.0, 5.0)],
        direction: vec2(1.0, 0.0),
    };
    let mut food = Food { pos: vec2(10.0, 10.0) };
    let mut timer = 0.0;
    
    loop {
        // 입력
        if is_key_pressed(KeyCode::Right) { snake.direction = vec2(1.0, 0.0); }
        if is_key_pressed(KeyCode::Left) { snake.direction = vec2(-1.0, 0.0); }
        if is_key_pressed(KeyCode::Up) { snake.direction = vec2(0.0, -1.0); }
        if is_key_pressed(KeyCode::Down) { snake.direction = vec2(0.0, 1.0); }
        
        // 업데이트 (0.2초마다)
        timer += get_frame_time();
        if timer > 0.2 {
            timer = 0.0;
            let head = snake.body[0] + snake.direction;
            snake.body.insert(0, head);
            
            // 먹이 충돌 체크
            if head != food.pos {
                snake.body.pop();
            } else {
                food.pos = vec2(rand::gen_range(0, 20) as f32, rand::gen_range(0, 20) as f32);
            }
        }
        
        // 그리기
        clear_background(BLACK);
        let cell_size = 20.0;
        for &seg in &snake.body {
            draw_rectangle(seg.x * cell_size, seg.y * cell_size, cell_size, cell_size, GREEN);
        }
        draw_rectangle(food.pos.x * cell_size, food.pos.y * cell_size, cell_size, cell_size, RED);
        
        next_frame().await
    }
}
```

빌드 시간: 약 16초  
WASM 크기: 약 567KB  
실행 성능: 60fps 안정적

## 트러블슈팅

### "wasm32-unknown-unknown target not installed"
```bash
rustup target add wasm32-unknown-unknown
```

### "Cannot find mq_js_bundle.js"
```bash
wget https://github.com/not-fl3/macroquad/releases/download/v0.4.0/mq_js_bundle.js
```

### "Canvas has zero size"
`index.html`에서 `#glcanvas`에 명시적인 `width`, `height` CSS 추가

### "Sound not playing"
`Cargo.toml`에 `macroquad-audio` 추가 확인
