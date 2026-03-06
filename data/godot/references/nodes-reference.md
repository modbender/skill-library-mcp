# Godot Nodes Reference

자주 사용하는 Godot 4.x 노드 목록과 사용법

## 2D Nodes

### Node2D
**용도**: 모든 2D 노드의 베이스. 위치, 회전, 스케일 보유  
**주요 속성**:
- `position: Vector2` - 위치
- `rotation: float` - 회전 (라디안)
- `scale: Vector2` - 스케일

```gdscript
$Node2D.position = Vector2(100, 200)
$Node2D.rotation_degrees = 45
$Node2D.scale = Vector2(2.0, 2.0)
```

---

### Sprite2D
**용도**: 2D 이미지 표시  
**주요 속성**:
- `texture: Texture2D` - 표시할 이미지
- `flip_h: bool` - 수평 반전
- `flip_v: bool` - 수직 반전

```gdscript
$Sprite2D.texture = load("res://assets/player.png")
$Sprite2D.flip_h = true
```

---

### AnimatedSprite2D
**용도**: 프레임 애니메이션  
**주요 속성**:
- `sprite_frames: SpriteFrames` - 애니메이션 리소스

```gdscript
$AnimatedSprite2D.play("walk")
$AnimatedSprite2D.stop()
```

---

### CharacterBody2D
**용도**: 플레이어/NPC 물리 컨트롤러  
**주요 속성**:
- `velocity: Vector2` - 이동 속도
- `motion_mode: int` - MOTION_MODE_GROUNDED / MOTION_MODE_FLOATING

```gdscript
extends CharacterBody2D

func _physics_process(delta):
    velocity = Vector2(100, 0)
    move_and_slide()
```

---

### RigidBody2D
**용도**: 물리 시뮬레이션 (중력, 충돌 반응)  
**주요 속성**:
- `gravity_scale: float` - 중력 영향도
- `mass: float` - 질량
- `linear_velocity: Vector2` - 선형 속도

```gdscript
$RigidBody2D.apply_central_impulse(Vector2(0, -500))
```

---

### Area2D
**용도**: 충돌 감지 영역 (트리거)  
**신호**:
- `body_entered(body: Node2D)` - 물체 진입
- `body_exited(body: Node2D)` - 물체 퇴장

```gdscript
extends Area2D

func _ready():
    body_entered.connect(_on_body_entered)

func _on_body_entered(body):
    if body.is_in_group("player"):
        print("Player touched!")
```

---

### Camera2D
**용도**: 2D 카메라  
**주요 속성**:
- `zoom: Vector2` - 줌 배율 (1.0 = 기본)
- `position_smoothing_enabled: bool` - 부드러운 이동

```gdscript
$Camera2D.zoom = Vector2(2.0, 2.0)
$Camera2D.position_smoothing_speed = 5.0
```

---

### TileMap
**용도**: 타일맵 렌더링  
**주요 함수**:
- `set_cell(layer, coords, tile_id)` - 타일 배치
- `get_cell_source_id(layer, coords)` - 타일 ID 가져오기

```gdscript
$TileMap.set_cell(0, Vector2i(0, 0), 1)
```

---

### CollisionShape2D
**용도**: 충돌 형태 정의 (CharacterBody2D/Area2D 자식)  
**주요 속성**:
- `shape: Shape2D` - 충돌 형태 (RectangleShape2D, CircleShape2D 등)

```gdscript
var shape = CircleShape2D.new()
shape.radius = 32
$CollisionShape2D.shape = shape
```

---

## 3D Nodes

### Node3D
**용도**: 모든 3D 노드의 베이스  
**주요 속성**:
- `position: Vector3`
- `rotation: Vector3` (라디안)
- `scale: Vector3`

```gdscript
$Node3D.position = Vector3(0, 10, 0)
$Node3D.rotation_degrees = Vector3(0, 45, 0)
```

---

### MeshInstance3D
**용도**: 3D 메시 표시  
**주요 속성**:
- `mesh: Mesh` - 표시할 메시

```gdscript
var sphere = SphereMesh.new()
$MeshInstance3D.mesh = sphere
```

---

### CharacterBody3D
**용도**: 3D 캐릭터 컨트롤러  
**주요 함수**:
- `move_and_slide()` - 충돌 고려한 이동
- `is_on_floor()` - 바닥 접촉 여부

```gdscript
extends CharacterBody3D

func _physics_process(delta):
    if not is_on_floor():
        velocity.y -= 9.8 * delta
    move_and_slide()
```

---

### RigidBody3D
**용도**: 3D 물리 시뮬레이션  
**주요 함수**:
- `apply_central_impulse(impulse: Vector3)` - 충격력
- `apply_torque_impulse(impulse: Vector3)` - 회전력

```gdscript
$RigidBody3D.apply_central_impulse(Vector3(0, 500, 0))
```

---

### Area3D
**용도**: 3D 충돌 감지 영역  
**신호**: `body_entered`, `body_exited` (2D와 동일)

---

### Camera3D
**용도**: 3D 카메라  
**주요 속성**:
- `fov: float` - 시야각 (FOV)
- `near: float` - Near plane
- `far: float` - Far plane

```gdscript
$Camera3D.fov = 90
$Camera3D.position = Vector3(0, 5, -10)
$Camera3D.look_at(Vector3.ZERO)
```

---

### DirectionalLight3D
**용도**: 태양광 같은 방향성 조명  
**주요 속성**:
- `light_energy: float` - 밝기
- `shadow_enabled: bool` - 그림자 활성화

```gdscript
$DirectionalLight3D.light_energy = 1.5
$DirectionalLight3D.shadow_enabled = true
```

---

## UI Nodes

### Control
**용도**: 모든 UI 노드의 베이스  
**주요 속성**:
- `anchor_left/right/top/bottom: float` - 앵커 (0.0~1.0)
- `position: Vector2`
- `size: Vector2`

```gdscript
$Control.position = Vector2(100, 100)
$Control.size = Vector2(200, 50)
```

---

### Label
**용도**: 텍스트 표시  
**주요 속성**:
- `text: String` - 표시할 텍스트

```gdscript
$Label.text = "Score: 100"
```

---

### Button
**용도**: 클릭 가능한 버튼  
**신호**:
- `pressed()` - 클릭 시

```gdscript
$Button.pressed.connect(_on_button_pressed)

func _on_button_pressed():
    print("Button clicked!")
```

---

### Panel
**용도**: 배경 패널 (UI 컨테이너)

---

### HBoxContainer / VBoxContainer
**용도**: 자식을 가로/세로로 자동 정렬  
**주요 속성**:
- `alignment: int` - 정렬 방식

```gdscript
# 자식 노드들이 자동으로 가로 정렬됨
$HBoxContainer.add_child(button1)
$HBoxContainer.add_child(button2)
```

---

### TextureRect
**용도**: UI에 이미지 표시  
**주요 속성**:
- `texture: Texture2D`

```gdscript
$TextureRect.texture = load("res://assets/icon.png")
```

---

### ProgressBar
**용도**: 진행률 표시 (HP 바 등)  
**주요 속성**:
- `value: float` - 현재 값
- `max_value: float` - 최대값

```gdscript
$ProgressBar.max_value = 100
$ProgressBar.value = 75  # 75%
```

---

## Audio Nodes

### AudioStreamPlayer
**용도**: 2D/3D 관계없는 글로벌 사운드  
**주요 속성**:
- `stream: AudioStream` - 오디오 파일
- `volume_db: float` - 볼륨 (dB)

```gdscript
$AudioStreamPlayer.stream = load("res://sounds/music.mp3")
$AudioStreamPlayer.play()
```

---

### AudioStreamPlayer2D
**용도**: 2D 공간 사운드 (거리감)

---

### AudioStreamPlayer3D
**용도**: 3D 공간 사운드 (거리감 + 방향성)

---

## Utility Nodes

### Timer
**용도**: 타이머  
**주요 속성**:
- `wait_time: float` - 대기 시간
- `one_shot: bool` - 1회만 실행

**신호**:
- `timeout()` - 시간 경과 시

```gdscript
$Timer.wait_time = 2.0
$Timer.timeout.connect(_on_timer_timeout)
$Timer.start()

func _on_timer_timeout():
    print("Timer done!")
```

---

### AnimationPlayer
**용도**: 노드 속성 애니메이션  
**주요 함수**:
- `play(name: String)` - 애니메이션 재생
- `stop()` - 중지

```gdscript
$AnimationPlayer.play("fade_in")
```

---

### CollisionShape2D / CollisionShape3D
**용도**: 물리 충돌 형태 정의  
**주요 속성**:
- `shape: Shape2D/Shape3D`

```gdscript
var rect = RectangleShape2D.new()
rect.size = Vector2(64, 64)
$CollisionShape2D.shape = rect
```

---

### PathFollow2D / PathFollow3D
**용도**: 경로를 따라 이동하는 노드  
**주요 속성**:
- `progress: float` - 경로상 위치 (0.0~1.0)

```gdscript
$PathFollow2D.progress_ratio += 0.01  # 경로를 따라 이동
```

---

## 노드 선택 가이드

### 캐릭터 컨트롤러
- **플레이어/NPC**: CharacterBody2D/3D
- **물리 기반 오브젝트**: RigidBody2D/3D
- **정적 배경**: StaticBody2D/3D

### UI
- **텍스트**: Label
- **버튼**: Button
- **HP 바**: ProgressBar
- **컨테이너**: HBoxContainer, VBoxContainer
- **배경**: Panel

### 충돌 감지
- **트리거 (아이템, 영역)**: Area2D/3D
- **물리 충돌**: CharacterBody2D/3D + CollisionShape2D/3D

---

**참고**: [Godot Class Reference](https://docs.godotengine.org/en/stable/classes/index.html)
