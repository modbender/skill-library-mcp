# Godot 4.x HTML5 Export 가이드

Godot 4.x로 웹 게임을 만들고 HTML5로 Export하는 전체 워크플로우.

## 환경 (MiniPC)

```
Godot 버전: 4.6 stable
위치: $HOME/godot4
프로젝트 디렉토리: $HOME/godot4/projects/
```

## 프로젝트 생성

### GUI로 생성 (로컬 개발 시)

```bash
# MiniPC GUI 접속 후
godot4
# New Project → Browse → projects/<game-name> → Create & Edit
```

### CLI로 생성 (서브에이전트)

```bash
cd $HOME/godot4/projects
mkdir <game-name>
cd <game-name>

# project.godot 생성
godot4 --headless --path . --quit

# 기본 씬 생성 (main.tscn)
# 수동으로 씬 파일 작성하거나 GUI에서 작업
```

## 기본 프로젝트 구조

```
game-name/
├── project.godot          # 프로젝트 설정
├── main.tscn              # 메인 씬
├── scripts/
│   └── main.gd            # GDScript
├── assets/
│   ├── images/
│   ├── sounds/
│   └── fonts/
├── build/
│   └── web/               # HTML5 Export 결과물
│       ├── index.html
│       ├── <game>.wasm
│       ├── <game>.pck
│       └── <game>.js
└── export_presets.cfg     # Export 설정
```

## project.godot 기본 설정

```ini
; Engine configuration file.

config_version=5

[application]

config/name="Game Name"
run/main_scene="res://main.tscn"
config/features=PackedStringArray("4.3", "GL Compatibility")
config/icon="res://icon.png"

[display]

window/size/viewport_width=800
window/size/viewport_height=600
window/stretch/mode="canvas_items"
window/handheld/orientation=1  # 가로 고정 (필요 시)

[rendering]

renderer/rendering_method="gl_compatibility"
renderer/rendering_method.mobile="gl_compatibility"
```

## 기본 씬 생성 (main.tscn)

### 노드 구조

```
Main (Node2D)
├── Player (Sprite2D)
├── Enemy (Area2D)
│   ├── Sprite2D
│   └── CollisionShape2D
├── UI (CanvasLayer)
│   └── ScoreLabel (Label)
└── BGM (AudioStreamPlayer)
```

### GDScript 예시 (scripts/main.gd)

```gdscript
extends Node2D

var score = 0

func _ready():
    # 초기화
    pass

func _process(delta):
    # 매 프레임 업데이트
    if Input.is_action_pressed("ui_right"):
        move_player(Vector2.RIGHT * delta * 200)

func move_player(offset):
    $Player.position += offset

func _on_enemy_area_entered(area):
    # 충돌 처리
    score += 1
    $UI/ScoreLabel.text = "Score: " + str(score)
```

## 입력 처리

### Input Map 설정 (project.godot)

```ini
[input]

ui_accept={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":32,"physical_keycode":0,"key_label":0,"unicode":0,"echo":false,"script":null)
]
}

move_right={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":68,"physical_keycode":0,"key_label":0,"unicode":0,"echo":false,"script":null)
]
}
```

### GDScript에서 사용

```gdscript
func _process(delta):
    # 키 입력
    if Input.is_action_pressed("move_right"):
        position.x += speed * delta
    
    # 마우스/터치
    if Input.is_action_just_pressed("ui_accept"):
        var mouse_pos = get_global_mouse_position()
        shoot(mouse_pos)
```

## 에셋 로딩

### 이미지

```gdscript
extends Sprite2D

func _ready():
    # 프로젝트 내 에셋 자동 로딩
    texture = load("res://assets/images/player.png")
    
    # 또는 씬 에디터에서 Texture 속성에 드래그 앤 드롭
```

### 사운드

```gdscript
extends AudioStreamPlayer

func _ready():
    stream = load("res://assets/sounds/bgm.ogg")
    play()

func play_sfx(sound_path):
    var sfx_player = AudioStreamPlayer.new()
    add_child(sfx_player)
    sfx_player.stream = load(sound_path)
    sfx_player.play()
    await sfx_player.finished
    sfx_player.queue_free()
```

## 충돌 감지

### Area2D 사용

```gdscript
extends Area2D

signal enemy_hit

func _ready():
    # 충돌 시그널 연결
    area_entered.connect(_on_area_entered)

func _on_area_entered(area):
    if area.is_in_group("bullets"):
        emit_signal("enemy_hit")
        queue_free()
```

### PhysicsBody2D 사용

```gdscript
extends CharacterBody2D

const SPEED = 200.0

func _physics_process(delta):
    var direction = Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
    velocity = direction * SPEED
    move_and_slide()
    
    # 충돌 감지
    for i in get_slide_collision_count():
        var collision = get_slide_collision(i)
        print("Collided with: ", collision.get_collider().name)
```

## 게임 상태 관리

### Singleton (Autoload) 패턴

**scripts/game_manager.gd**:
```gdscript
extends Node

enum State { MENU, PLAYING, PAUSED, GAME_OVER }

var current_state = State.MENU
var score = 0
var high_score = 0

signal state_changed(new_state)

func change_state(new_state):
    current_state = new_state
    emit_signal("state_changed", new_state)

func reset_game():
    score = 0
    change_state(State.PLAYING)
```

**project.godot**에 Autoload 등록:
```ini
[autoload]

GameManager="*res://scripts/game_manager.gd"
```

**다른 스크립트에서 사용**:
```gdscript
func _ready():
    GameManager.state_changed.connect(_on_state_changed)

func _on_state_changed(new_state):
    match new_state:
        GameManager.State.MENU:
            show_menu()
        GameManager.State.PLAYING:
            start_game()
        GameManager.State.GAME_OVER:
            show_game_over()
```

## HTML5 Export 설정

### export_presets.cfg 생성

```ini
[preset.0]

name="Web"
platform="Web"
runnable=true
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path="build/web/index.html"
encryption_include_filters=""
encryption_exclude_filters=""
encrypt_pck=false
encrypt_directory=false

[preset.0.options]

custom_template/debug=""
custom_template/release=""
variant/extensions_support=false
vram_texture_compression/for_desktop=true
vram_texture_compression/for_mobile=true
html/export_icon=true
html/custom_html_shell=""
html/head_include=""
html/canvas_resize_policy=2
html/focus_canvas_on_start=true
html/experimental_virtual_keyboard=false
progressive_web_app/enabled=false
progressive_web_app/offline_page=""
progressive_web_app/display=1
progressive_web_app/orientation=0
progressive_web_app/icon_144x144=""
progressive_web_app/icon_180x180=""
progressive_web_app/icon_512x512=""
progressive_web_app/background_color=Color(0, 0, 0, 1)
```

### CLI로 Export Preset 추가

```bash
# export_presets.cfg 파일 생성 (위 내용)
# 또는 GUI에서: Project → Export → Add... → Web
```

## 빌드 & 배포

### Headless Export (MiniPC)

```bash
cd $HOME/godot4/projects/<game-name>

# HTML5 Export
godot4 --headless --path . --export-release "Web"

# 결과물: build/web/
# - index.html
# - <game-name>.wasm
# - <game-name>.pck
# - <game-name>.js
```

### eastsea.monster 배포

```bash
# MiniPC에서 Mac Studio로 전송
scp -r build/web/* <user>@<MACBOOK_IP>:$WORKSPACE/eastsea-blog/games/<game-name>/

# 또는 HTTP 서버로 전송
cd build/web
python3 -m http.server 9877  # Mac Studio에서 curl로 다운로드
```

## 모바일 최적화

### 터치 입력

```gdscript
func _input(event):
    if event is InputEventScreenTouch:
        if event.pressed:
            handle_touch(event.position)

func handle_touch(pos):
    print("Touched at: ", pos)
```

### 반응형 화면

```gdscript
extends Node2D

func _ready():
    # 화면 크기에 맞춘 스케일
    var viewport_size = get_viewport().get_visible_rect().size
    var base_size = Vector2(800, 600)
    var scale_factor = min(viewport_size.x / base_size.x, viewport_size.y / base_size.y)
    scale = Vector2(scale_factor, scale_factor)
```

### Safe Area (모바일 노치 대응)

```gdscript
func _ready():
    var safe_area = DisplayServer.get_display_safe_area()
    # UI를 safe area 안쪽에 배치
    $UI.position = Vector2(safe_area.position.x, safe_area.position.y)
```

## 성능 최적화

### 텍스처 압축

```ini
[rendering]

textures/vram_compression/import_etc2_astc=true  # 모바일
textures/vram_compression/import_s3tc_bptc=true  # 데스크톱
```

### 오브젝트 풀링

```gdscript
class_name ObjectPool extends Node

var _pool = []
var _scene: PackedScene

func _init(scene: PackedScene, initial_size: int = 10):
    _scene = scene
    for i in range(initial_size):
        var obj = _scene.instantiate()
        obj.visible = false
        _pool.append(obj)

func get_object():
    if _pool.is_empty():
        return _scene.instantiate()
    var obj = _pool.pop_back()
    obj.visible = true
    return obj

func return_object(obj):
    obj.visible = false
    _pool.append(obj)
```

### 불필요한 노드 비활성화

```gdscript
func _process(delta):
    # 화면 밖 객체 비활성화
    if position.x < -100 or position.x > 900:
        set_process(false)
        visible = false
```

## 디버깅

### 콘솔 출력

```gdscript
print("Player position: ", position)            # Godot 콘솔
print_debug("Debug info: ", health)             # 디버그 정보 포함
push_warning("Warning: Low health!")            # 경고
push_error("Error: Game state invalid!")        # 에러
```

### 브라우저 개발자 도구

1. Chrome/Firefox 개발자 도구 열기 (F12)
2. Console 탭에서 Godot 출력 확인
3. Network 탭에서 `.pck`, `.wasm` 로딩 확인

### Remote Debugging

```bash
# MiniPC에서 디버그 서버 실행
godot4 --path . --remote-debug tcp://0.0.0.0:6007

# Mac Studio에서 Godot Editor로 연결
# Editor → Debug → Deploy Remote Debug → tcp://<MINIPC_IP>:6007
```

## 예시 프로젝트: Snake 게임

### main.tscn 노드 구조

```
Main (Node2D)
├── Snake (Node2D)
│   └── SnakeSegment (Sprite2D) × N개
├── Food (Sprite2D)
├── UI (CanvasLayer)
│   └── ScoreLabel (Label)
└── Timer (Timer)
```

### scripts/main.gd

```gdscript
extends Node2D

const CELL_SIZE = 20
var snake_body = [Vector2(5, 5)]
var direction = Vector2.RIGHT
var food_pos = Vector2(10, 10)
var score = 0

func _ready():
    $Timer.timeout.connect(_on_timer_timeout)
    $Timer.start()

func _input(event):
    if event.is_action_pressed("ui_right") and direction != Vector2.LEFT:
        direction = Vector2.RIGHT
    elif event.is_action_pressed("ui_left") and direction != Vector2.RIGHT:
        direction = Vector2.LEFT
    elif event.is_action_pressed("ui_up") and direction != Vector2.DOWN:
        direction = Vector2.UP
    elif event.is_action_pressed("ui_down") and direction != Vector2.UP:
        direction = Vector2.DOWN

func _on_timer_timeout():
    var head = snake_body[0] + direction
    snake_body.insert(0, head)
    
    if head == food_pos:
        score += 1
        $UI/ScoreLabel.text = "Score: " + str(score)
        spawn_food()
    else:
        snake_body.pop_back()
    
    queue_redraw()

func _draw():
    # 뱀 그리기
    for segment in snake_body:
        draw_rect(Rect2(segment * CELL_SIZE, Vector2(CELL_SIZE, CELL_SIZE)), Color.GREEN)
    
    # 먹이 그리기
    draw_rect(Rect2(food_pos * CELL_SIZE, Vector2(CELL_SIZE, CELL_SIZE)), Color.RED)

func spawn_food():
    food_pos = Vector2(randi() % 20, randi() % 20)
```

빌드 시간: 약 10초  
결과물 크기: ~5MB (.wasm + .pck)  
실행 성능: 60fps 안정적

## 트러블슈팅

### "Export template not found"
```bash
# Export templates 다운로드
godot4 --headless --quit  # 자동 다운로드
# 또는 GUI에서: Editor → Manage Export Templates → Download and Install
```

### "Failed to load .pck file"
- `export_presets.cfg`에서 `export_path` 경로 확인
- `.pck` 파일이 `.html`과 같은 디렉토리에 있는지 확인

### "CORS error when loading assets"
- 로컬 서버 사용: `python3 -m http.server 8000`
- 또는 eastsea.monster에 직접 배포

### "Touch input not working"
- `project.godot`에서 `input_devices/pointing/emulate_touch_from_mouse=true` 설정
- 브라우저에서 모바일 에뮬레이션 활성화

## Godot vs Rust 선택 기준

### Godot 추천
- ✅ 씬 기반 게임 (여러 레벨/화면)
- ✅ 복잡한 UI (인벤토리, 대화 시스템)
- ✅ 애니메이션 많은 게임
- ✅ 비주얼 에디터 선호

### Rust + WASM 추천
- ✅ 단일 화면 게임 (Snake, Tetris, Pong)
- ✅ 작은 번들 크기 필요 (< 1MB)
- ✅ 빠른 빌드 시간 중요
- ✅ 코드 중심 개발 선호
