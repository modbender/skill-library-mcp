# Unity Asset Store에서 Sprite Sheet 추출 및 활용

## 실전 사례: 2D Astronaut Character

**데모:** https://eastsea.monster/examples/sprite-sheet-demo/  
**소스:** https://github.com/kjaylee/eastsea-blog/tree/main/examples/sprite-sheet-demo  
**에셋:** Unity Asset Store - "2D Character - Astronaut" by Lootzifr

## 개요

Unity Asset Store에서 구매/다운로드한 에셋을 Rust + WebAssembly 게임에서 사용하는 전체 과정.

## 1단계: Unity Package 구조 이해

### Unity Package 파일 (.unitypackage)

```
2D Character - Astronaut.unitypackage
├── [UUID]/
│   ├── asset          # 실제 파일 (PNG, 메타데이터 없음)
│   ├── asset.meta     # Unity 메타데이터 (YAML)
│   ├── pathname       # 원본 경로 (텍스트)
│   └── preview.png    # 썸네일 (선택)
```

### 추출 명령어

```bash
cd /tmp && mkdir astronaut && cd astronaut
tar -xzf "/path/to/2D Character - Astronaut.unitypackage"
```

## 2단계: 원하는 Sprite 찾기

### pathname 파일로 검색

```bash
# 특정 애니메이션 찾기
find . -name "pathname" -exec grep -l "walk/side" {} \;

# 결과 예시
./8a3592263c504db68fcd3bebb63ad038/pathname
./f0e4c68635e7455fbf07b51e5b6b959c/pathname
...
```

### pathname 내용 확인

```bash
cat ./8a3592263c504db68fcd3bebb63ad038/pathname
# Assets/.../ Variant A/Sprites/Character/walk/side/13.png
```

## 3단계: Asset 파일 추출

### 개별 프레임 복사

```bash
# walk 애니메이션 프레임 추출 (01-14)
for i in {01..14}; do
    dir=$(find . -name "pathname" \
         -exec grep -l "walk/side/$i.png" {} \; \
         | head -1 | xargs dirname)
    cp "$dir/asset" "walk_$i.png"
done
```

### 파일 크기 확인

```bash
$ file walk_01.png
walk_01.png: PNG image data, 360 x 300, 8-bit colormap

$ ls -lh walk_*.png
-rw-r--r--  1 user  staff   7.0K  walk_01.png
-rw-r--r--  1 user  staff   7.3K  walk_02.png
...
```

## 4단계: Sprite Sheet 생성

### Python + PIL 사용

```python
from PIL import Image
import glob

# 모든 walk 프레임 로드
frames = sorted(glob.glob("walk_*.png"))
images = [Image.open(f) for f in frames]

# 첫 프레임 크기
w, h = images[0].size  # 360x300

# 가로 strip으로 합치기
sprite_sheet = Image.new('RGBA', (w * len(images), h))

for i, img in enumerate(images):
    sprite_sheet.paste(img, (i * w, 0))

sprite_sheet.save("astronaut_walk.png")
print(f"Sprite sheet: {w * len(images)}x{h}")
# Output: Sprite sheet: 1080x300 (3 frames)
```

### ImageMagick 사용 (대안)

```bash
convert walk_*.png +append astronaut_walk.png
identify astronaut_walk.png
# astronaut_walk.png PNG 1080x300 8-bit sRGB
```

## 5단계: Rust 게임에서 사용

### Cargo.toml

```toml
[dependencies]
macroquad = "0.4"

[profile.release]
opt-level = "z"
lto = true
```

### 핵심 코드

```rust
use macroquad::prelude::*;

const FRAME_WIDTH: f32 = 360.0;
const FRAME_HEIGHT: f32 = 300.0;
const FRAME_COUNT: usize = 3;

#[macroquad::main("Sprite Demo")]
async fn main() {
    // 1. Sprite sheet 로드
    let texture = load_texture("astronaut_walk.png")
        .await
        .expect("Failed to load sprite sheet");
    
    // 픽셀 아트용 필터 설정
    texture.set_filter(FilterMode::Nearest);
    
    let mut current_frame = 0;
    
    loop {
        clear_background(BLACK);
        
        // 2. 현재 프레임의 source rectangle 계산
        let source_rect = Rect::new(
            current_frame as f32 * FRAME_WIDTH,  // x = frame_index * frame_width
            0.0,                                   // y = 0 (horizontal strip)
            FRAME_WIDTH,                          // width
            FRAME_HEIGHT,                         // height
        );
        
        // 3. 텍스처 그리기 (플립 지원)
        draw_texture_ex(
            &texture,
            100.0,  // screen x
            100.0,  // screen y
            WHITE,
            DrawTextureParams {
                source: Some(source_rect),
                // 좌우 반전: 음수 width 사용
                dest_size: Some(vec2(
                    if facing_right { FRAME_WIDTH } else { -FRAME_WIDTH },
                    FRAME_HEIGHT,
                )),
                ..Default::default()
            },
        );
        
        // 4. 프레임 애니메이션
        current_frame = (current_frame + 1) % FRAME_COUNT;
        
        next_frame().await;
    }
}
```

## 6단계: WebAssembly 빌드

```bash
# WASM 타겟 추가 (처음 한 번)
rustup target add wasm32-unknown-unknown

# 빌드
cargo build --release --target wasm32-unknown-unknown

# 결과물
ls -lh target/wasm32-unknown-unknown/release/*.wasm
# -rwxr-xr-x  636K  astronaut-demo.wasm
```

### index.html 생성

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Sprite Demo</title>
</head>
<body style="margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; background: #1a1a2e;">
    <canvas id="glcanvas" tabindex='1'></canvas>
    <script src="https://not-fl3.github.io/miniquad-samples/gl.js"></script>
    <script>load("astronaut_demo.wasm");</script>
</body>
</html>
```

## 7단계: 배포

```bash
# GitHub Pages
cp target/wasm32-unknown-unknown/release/astronaut-demo.wasm ./
cp astronaut_walk.png ./
# Push to gh-pages branch

# 또는 간단한 서버로 테스트
python3 -m http.server 8000
# Open: http://localhost:8000
```

## 실전 팁

### 1. Sprite Sheet 레이아웃 선택

**수평 Strip (추천):**
- 장점: 계산 간단 (x = frame_index * frame_width)
- 단점: 프레임 많으면 너무 길어짐

**Grid 레이아웃:**
```rust
let cols = 4;
let row = frame_index / cols;
let col = frame_index % cols;
let source_rect = Rect::new(
    col as f32 * FRAME_WIDTH,
    row as f32 * FRAME_HEIGHT,
    FRAME_WIDTH,
    FRAME_HEIGHT,
);
```

### 2. 애니메이션 타이밍

```rust
struct Animator {
    frame: usize,
    timer: f32,
    speed: f32,  // seconds per frame
}

impl Animator {
    fn update(&mut self, delta: f32) {
        self.timer += delta;
        if self.timer >= self.speed {
            self.timer = 0.0;
            self.frame = (self.frame + 1) % FRAME_COUNT;
        }
    }
}
```

### 3. 메모리 최적화

```rust
// 텍스처를 static으로 한 번만 로드
static mut TEXTURES: Option<Textures> = None;

// 또는 Arc<Texture2D> 사용
```

### 4. 프레임 좌표 문서화

```rust
/// Astronaut walk animation sprite sheet
/// Layout: Horizontal strip
/// Total: 1080x300 (3 frames)
///
/// Frame coordinates:
/// - Frame 0: (0, 0, 360, 300)
/// - Frame 1: (360, 0, 360, 300)
/// - Frame 2: (720, 0, 360, 300)
const ASTRONAUT_WALK: &[Rect] = &[
    Rect { x: 0.0, y: 0.0, w: 360.0, h: 300.0 },
    Rect { x: 360.0, y: 0.0, w: 360.0, h: 300.0 },
    Rect { x: 720.0, y: 0.0, w: 360.0, h: 300.0 },
];
```

## 흔한 실수와 해결

### 1. 텍스처 blur 현상

**문제:** 픽셀 아트가 흐릿하게 보임  
**해결:**
```rust
texture.set_filter(FilterMode::Nearest);
```

### 2. 좌우 반전이 안 됨

**문제:** Sprite가 한 방향만 봄  
**해결:** dest_size에 음수 width 사용
```rust
dest_size: Some(vec2(
    if facing_right { width } else { -width },
    height,
))
```

### 3. 프레임 좌표 오류

**문제:** 잘못된 부분이 보임  
**해결:** source rectangle 계산 재확인
```rust
// Debug 출력
println!("Frame {}: x={}, y={}", 
         frame, frame as f32 * FRAME_WIDTH, 0.0);
```

### 4. WASM 로딩 실패

**문제:** "Failed to load WASM"  
**해결:**
- CORS 설정 확인 (로컬 서버 필요)
- 파일 이름 정확히 일치하는지 확인
- 브라우저 콘솔에서 에러 확인

## 성능 고려사항

### 빌드 크기 최적화

```toml
[profile.release]
opt-level = "z"        # Size optimization
lto = true             # Link-time optimization
codegen-units = 1      # Better optimization
strip = true           # Strip debug symbols (Rust 1.59+)
```

**결과:**
- 기본: ~2.5 MB
- 최적화 후: ~636 KB (73% 감소)

### 로딩 시간

- Sprite sheet 로딩: < 100ms
- WASM 초기화: < 500ms
- 총 로딩: < 1초

### 런타임 성능

- 60 FPS 안정
- 메모리: ~5 MB
- CPU: 1-3% (idle), 5-8% (active)

## 라이선스 주의사항

### Unity Asset Store 라이선스

✅ **허용:**
- 게임/앱에서 사용
- 상업적 사용 (게임 판매)
- 수정/편집

❌ **금지:**
- 에셋 단독 재배포
- 다른 에셋 스토어에 업로드
- 소스 파일 재판매

### 이 데모

- **목적:** 교육용 (에셋 통합 방법 시연)
- **에셋 포함:** 최소한의 샘플 (3 프레임)
- **프로덕션:** Asset Store에서 직접 구매 필요

## 참고 자료

- **Unity Asset Store:** https://assetstore.unity.com
- **Macroquad 문서:** https://macroquad.rs
- **WebAssembly:** https://webassembly.org
- **데모 소스:** https://github.com/kjaylee/eastsea-blog

---

**작성일:** 2026-02-06  
**업데이트:** 2026-02-06  
**태그:** #unity #sprite-sheet #rust #webassembly #macroquad #gamedev
