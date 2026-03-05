# 2D Game Patterns

Godot 4.x 2D 게임 공통 패턴 모음

## 🎮 플레이어 이동

### 8방향 이동 (탑다운)
```gdscript
extends CharacterBody2D

@export var speed: float = 300.0

func _physics_process(delta):
    # Input.get_vector는 자동으로 normalize됨
    var direction = Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
    velocity = direction * speed
    move_and_slide()
```

### 플랫포머 이동 (좌우 + 점프)
```gdscript
extends CharacterBody2D

@export var speed: float = 200.0
@export var jump_velocity: float = -400.0
var gravity = ProjectSettings.get_setting("physics/2d/default_gravity")

func _physics_process(delta):
    # 중력 적용
    if not is_on_floor():
        velocity.y += gravity * delta
    
    # 점프
    if Input.is_action_just_pressed("ui_accept") and is_on_floor():
        velocity.y = jump_velocity
    
    # 좌우 이동
    var direction = Input.get_axis("ui_left", "ui_right")
    velocity.x = direction * speed
    
    move_and_slide()
```

### 마우스 따라가기 (적 AI)
```gdscript
extends CharacterBody2D

@export var speed: float = 100.0
var target_position: Vector2

func _physics_process(delta):
    var direction = (target_position - global_position).normalized()
    velocity = direction * speed
    move_and_slide()
```

---

## 🎯 발사체 (Bullet)

### 직선 발사
```gdscript
# bullet.gd
extends Area2D

@export var speed: float = 400.0
var direction: Vector2 = Vector2.RIGHT

func _ready():
    body_entered.connect(_on_body_entered)

func _process(delta):
    position += direction * speed * delta

func _on_body_entered(body):
    if body.is_in_group("enemies"):
        body.take_damage(10)
    queue_free()
```

### 플레이어가 발사
```gdscript
# player.gd
const BULLET_SCENE = preload("res://scenes/bullet.tscn")

func _process(delta):
    if Input.is_action_just_pressed("shoot"):
        shoot()

func shoot():
    var bullet = BULLET_SCENE.instantiate()
    bullet.position = $Muzzle.global_position  # 총구 위치
    bullet.direction = Vector2.RIGHT.rotated(rotation)
    get_parent().add_child(bullet)  # 부모에 추가 (중요!)
```

---

## 👾 적 AI

### 플레이어 추적
```gdscript
extends CharacterBody2D

@export var speed: float = 100.0
@export var chase_range: float = 300.0

@onready var player = get_tree().get_first_node_in_group("player")

func _physics_process(delta):
    if not player:
        return
    
    var distance = global_position.distance_to(player.global_position)
    
    if distance < chase_range:
        var direction = (player.global_position - global_position).normalized()
        velocity = direction * speed
        move_and_slide()
```

### 순찰 패턴
```gdscript
extends CharacterBody2D

@export var speed: float = 50.0
@export var patrol_points: Array[Vector2] = []
var current_point_index: int = 0

func _physics_process(delta):
    if patrol_points.is_empty():
        return
    
    var target = patrol_points[current_point_index]
    var direction = (target - global_position).normalized()
    
    velocity = direction * speed
    move_and_slide()
    
    # 도착 시 다음 포인트
    if global_position.distance_to(target) < 10:
        current_point_index = (current_point_index + 1) % patrol_points.size()
```

---

## 💥 체력 & 데미지

### 체력 시스템
```gdscript
extends CharacterBody2D

signal health_changed(new_health, max_health)
signal died

@export var max_health: int = 100
var health: int = max_health

func _ready():
    health_changed.emit(health, max_health)

func take_damage(amount: int):
    health -= amount
    health = max(health, 0)  # 0 이하 방지
    health_changed.emit(health, max_health)
    
    if health <= 0:
        die()

func heal(amount: int):
    health += amount
    health = min(health, max_health)  # max_health 넘지 않게
    health_changed.emit(health, max_health)

func die():
    died.emit()
    queue_free()
```

### HP 바 (UI)
```gdscript
extends ProgressBar

func _ready():
    var player = get_tree().get_first_node_in_group("player")
    if player:
        player.health_changed.connect(_on_health_changed)

func _on_health_changed(current, maximum):
    max_value = maximum
    value = current
```

---

## 💰 아이템 수집

### 코인 (아이템)
```gdscript
# coin.gd
extends Area2D

@export var value: int = 1

func _ready():
    body_entered.connect(_on_body_entered)

func _on_body_entered(body):
    if body.is_in_group("player"):
        body.collect_coin(value)
        queue_free()
```

### 플레이어 수집
```gdscript
# player.gd
signal coin_collected(total_coins)

var coins: int = 0

func collect_coin(amount: int):
    coins += amount
    coin_collected.emit(coins)
```

---

## 🎬 애니메이션

### AnimatedSprite2D (프레임 애니메이션)
```gdscript
@onready var anim = $AnimatedSprite2D

func _process(delta):
    # 이동 방향에 따라 애니메이션
    if velocity.length() > 0:
        anim.play("walk")
        # 좌우 반전
        anim.flip_h = velocity.x < 0
    else:
        anim.play("idle")
```

### AnimationPlayer (노드 속성 애니메이션)
```gdscript
@onready var anim_player = $AnimationPlayer

func take_damage(amount):
    health -= amount
    anim_player.play("hit_flash")  # 피격 깜빡임 애니메이션
```

---

## 📷 카메라

### 플레이어 따라가기
```gdscript
# player.tscn에 Camera2D 자식 추가
# Camera2D 속성:
# - Enabled: true
# - Position Smoothing: Enabled
# - Position Smoothing Speed: 5.0
```

### 카메라 쉐이크
```gdscript
extends Camera2D

@export var shake_intensity: float = 10.0

func shake(duration: float = 0.3):
    var tween = create_tween()
    for i in range(int(duration / 0.05)):
        var offset_x = randf_range(-shake_intensity, shake_intensity)
        var offset_y = randf_range(-shake_intensity, shake_intensity)
        tween.tween_property(self, "offset", Vector2(offset_x, offset_y), 0.05)
    tween.tween_property(self, "offset", Vector2.ZERO, 0.05)
```

---

## 🌟 파티클 효과

### 파티클 트리거
```gdscript
const EXPLOSION_EFFECT = preload("res://effects/explosion.tscn")

func explode():
    var effect = EXPLOSION_EFFECT.instantiate()
    effect.position = global_position
    get_parent().add_child(effect)
    
    # 파티클 종료 후 자동 제거
    effect.finished.connect(effect.queue_free)
```

---

## 🗺️ TileMap

### 타일 충돌 감지
```gdscript
# TileMap에서 자동으로 충돌 처리됨
# CharacterBody2D의 move_and_slide()가 TileMap 충돌 처리
```

### 타일 배치/제거 (런타임)
```gdscript
@onready var tilemap = $TileMap

func place_tile(pos: Vector2i):
    tilemap.set_cell(0, pos, 1)  # layer 0, tile_id 1

func remove_tile(pos: Vector2i):
    tilemap.set_cell(0, pos, -1)  # -1 = 빈 타일
```

---

## 🎯 적 스포너

### 랜덤 위치 스폰
```gdscript
extends Node2D

const ENEMY_SCENE = preload("res://scenes/enemy.tscn")

@export var spawn_interval: float = 2.0
@export var spawn_radius: float = 500.0

@onready var timer = $Timer

func _ready():
    timer.wait_time = spawn_interval
    timer.timeout.connect(_on_spawn_timer_timeout)
    timer.start()

func _on_spawn_timer_timeout():
    spawn_enemy()

func spawn_enemy():
    var enemy = ENEMY_SCENE.instantiate()
    
    # 랜덤 위치
    var angle = randf() * TAU
    var distance = randf_range(0, spawn_radius)
    var offset = Vector2(cos(angle), sin(angle)) * distance
    
    enemy.position = global_position + offset
    get_parent().add_child(enemy)
```

---

## 🔊 사운드 효과

### 효과음 재생
```gdscript
# 전역 AudioStreamPlayer (Autoload)
extends Node

var sounds = {
    "jump": preload("res://sounds/jump.wav"),
    "coin": preload("res://sounds/coin.wav"),
    "hit": preload("res://sounds/hit.wav")
}

func play(sound_name: String):
    if sounds.has(sound_name):
        var player = AudioStreamPlayer.new()
        add_child(player)
        player.stream = sounds[sound_name]
        player.play()
        player.finished.connect(player.queue_free)

# 사용: AudioManager.play("jump")
```

---

## 🎮 입력 관리

### 커스텀 입력 액션 (Project Settings → Input Map)
```
move_left: A, Left Arrow
move_right: D, Right Arrow
jump: Space, W
shoot: Left Mouse Button
```

### 코드에서 사용
```gdscript
if Input.is_action_pressed("move_left"):
    velocity.x = -speed

if Input.is_action_just_pressed("jump"):
    jump()
```

---

## 🏁 씬 전환

### 페이드 전환
```gdscript
# scene_transition.gd (Autoload)
extends CanvasLayer

@onready var anim = $AnimationPlayer

func change_scene(target_scene: String):
    anim.play("fade_out")
    await anim.animation_finished
    get_tree().change_scene_to_file(target_scene)
    anim.play("fade_in")

# 사용: SceneTransition.change_scene("res://scenes/level_2.tscn")
```

---

## 💾 세이브/로드

### 간단한 세이브
```gdscript
# save_manager.gd (Autoload)
extends Node

const SAVE_PATH = "user://savegame.save"

func save_game(data: Dictionary):
    var file = FileAccess.open(SAVE_PATH, FileAccess.WRITE)
    if file:
        file.store_var(data)
        file.close()

func load_game() -> Dictionary:
    if FileAccess.file_exists(SAVE_PATH):
        var file = FileAccess.open(SAVE_PATH, FileAccess.READ)
        if file:
            var data = file.get_var()
            file.close()
            return data
    return {}

# 사용
SaveManager.save_game({"score": 100, "level": 2})
var data = SaveManager.load_game()
```

---

## 🎯 추가 패턴

### 대쉬 (빠른 이동)
```gdscript
@export var dash_speed: float = 500.0
@export var dash_duration: float = 0.2
var is_dashing: bool = false

func _process(delta):
    if Input.is_action_just_pressed("dash") and not is_dashing:
        dash()

func dash():
    is_dashing = true
    var dash_direction = velocity.normalized()
    velocity = dash_direction * dash_speed
    
    await get_tree().create_timer(dash_duration).timeout
    is_dashing = false
```

---

**추가 참고**: [Godot 2D 튜토리얼](https://docs.godotengine.org/en/stable/tutorials/2d/index.html)
