---
name: godot
description: "Godot Engine 게임 개발. 프로젝트 생성, GDScript 코딩, 2D/3D 게임 제작, 노드 시스템, Scene 구조, 물리/애니메이션/UI 구현 지원. Godot 프로젝트 작업 시 사용."
keywords: [godot, game-engine, gdscript, 2d-game, 3d-game, game-development]
version: 1.0.0
---

# Godot Engine Skill

Godot 4.x 게임 엔진 개발을 위한 종합 가이드. 프로젝트 생성부터 빌드, GDScript 코딩, Scene/Node 시스템, 2D/3D 게임 제작까지 전 과정을 지원합니다.

## 🚀 Quick Start

### 신규 프로젝트 생성 (CLI)
```bash
# MiniPC에서 실행 (Godot 4.6 설치됨)
cd $HOME/
godot4 --headless --path . --create-project "MyGame"

# 또는 맥 스튜디오에서 원격 실행
# (nodes.run 또는 ssh 사용)
```

### 프로젝트 구조
```
MyGame/
├── project.godot       # 프로젝트 설정
├── scenes/             # 씬 파일 (.tscn)
│   ├── main.tscn
│   ├── player.tscn
│   └── enemy.tscn
├── scripts/            # GDScript 파일
│   ├── player.gd
│   └── enemy.gd
├── assets/             # 에셋 (텍스처, 사운드 등)
│   ├── sprites/
│   ├── sounds/
│   └── fonts/
└── export_presets.cfg  # 빌드 설정
```

### 첫 씬 생성
1. **Node2D** (2D 게임) 또는 **Node3D** (3D 게임) 루트 노드 생성
2. 자식 노드 추가 (Sprite2D, CharacterBody2D, Camera2D 등)
3. 스크립트 첨부 (Attach Script)
4. `_ready()`, `_process(delta)` 함수 작성

## 📚 GDScript Basics

### 핵심 라이프사이클 함수
```gdscript
extends Node2D

# 씬 트리 진입 시 1회 호출
func _ready():
    print("Ready!")

# 매 프레임 호출 (delta = 프레임 시간)
func _process(delta):
    position.x += 100 * delta  # 초당 100픽셀 이동

# 물리 프레임마다 호출 (고정 간격)
func _physics_process(delta):
    move_and_slide()
```

### 변수 & 타입
```gdscript
# 타입 추론
var speed := 200.0           # float
var health := 100            # int
var player_name := "Hero"    # String

# 명시적 타입
var velocity: Vector2 = Vector2.ZERO
var sprite: Sprite2D

# @export로 에디터 노출
@export var max_speed: float = 300.0
@export_range(0, 100) var hp: int = 100
```

### Signal (신호)
```gdscript
# 신호 정의
signal health_changed(new_health)
signal player_died

# 신호 발생
func take_damage(amount):
    health -= amount
    health_changed.emit(health)
    if health <= 0:
        player_died.emit()

# 다른 스크립트에서 연결
func _ready():
    $Player.health_changed.connect(_on_player_health_changed)

func _on_player_health_changed(new_health):
    print("Health: ", new_health)
```

### Node 접근
```gdscript
# 자식 노드 가져오기
var sprite = $Sprite2D
var label = get_node("Label")

# 부모/형제 접근
var parent = get_parent()
var sibling = get_parent().get_node("OtherNode")

# 씬 전역 접근 (Autoload)
GlobalScript.some_function()
```

## 🎮 2D Game Workflows

### 플레이어 이동 (8방향)
```gdscript
extends CharacterBody2D

@export var speed = 300.0

func _physics_process(delta):
    var input_dir = Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
    velocity = input_dir * speed
    move_and_slide()
```

### 애니메이션 (AnimatedSprite2D)
```gdscript
@onready var anim = $AnimatedSprite2D

func _process(delta):
    if velocity.length() > 0:
        anim.play("walk")
    else:
        anim.play("idle")
```

### 충돌 감지 (Area2D)
```gdscript
extends Area2D

func _ready():
    body_entered.connect(_on_body_entered)

func _on_body_entered(body):
    if body.is_in_group("player"):
        print("Player entered!")
        queue_free()  # 자신 제거
```

### TileMap 사용
```gdscript
@onready var tilemap = $TileMap

func _ready():
    # 타일 좌표 (0, 0)에 타일 ID 1 배치
    tilemap.set_cell(0, Vector2i(0, 0), 1)
```

## 🌍 3D Game Workflows

### FPS 플레이어 컨트롤러
```gdscript
extends CharacterBody3D

@export var speed = 5.0
@export var jump_velocity = 4.5
var gravity = ProjectSettings.get_setting("physics/3d/default_gravity")

func _physics_process(delta):
    # 중력
    if not is_on_floor():
        velocity.y -= gravity * delta
    
    # 점프
    if Input.is_action_just_pressed("ui_accept") and is_on_floor():
        velocity.y = jump_velocity
    
    # 이동
    var input_dir = Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
    var direction = (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()
    velocity.x = direction.x * speed
    velocity.z = direction.z * speed
    
    move_and_slide()
```

### 카메라 회전 (마우스)
```gdscript
extends Camera3D

@export var sensitivity = 0.003

func _ready():
    Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _input(event):
    if event is InputEventMouseMotion:
        rotation.y -= event.relative.x * sensitivity
        rotation.x -= event.relative.y * sensitivity
        rotation.x = clamp(rotation.x, -PI/2, PI/2)
```

## 🛠️ Common Patterns

### 씬 전환
```gdscript
# 다음 씬으로 이동
get_tree().change_scene_to_file("res://scenes/level2.tscn")

# 씬 인스턴스 생성
var enemy_scene = preload("res://scenes/enemy.tscn")
var enemy = enemy_scene.instantiate()
add_child(enemy)
```

### 타이머
```gdscript
# 타이머 노드 사용
@onready var timer = $Timer

func _ready():
    timer.timeout.connect(_on_timer_timeout)
    timer.start(2.0)  # 2초 후 신호 발생

func _on_timer_timeout():
    print("Timer finished!")
```

### 트윈 (Tween) 애니메이션
```gdscript
func fade_out():
    var tween = create_tween()
    tween.tween_property($Sprite2D, "modulate:a", 0.0, 1.0)  # 1초간 투명화
```

### UI 업데이트
```gdscript
extends Control

@onready var label = $Label

func update_score(score):
    label.text = "Score: %d" % score
```

## 🏗️ 빌드 & Export (MiniPC)

### Web (HTML5) 빌드
```bash
cd $HOME/
godot4 --headless --path MyGame --export-release "Web" output/index.html
```

### Export Preset 설정 (project.godot)
```ini
[export]
name="Web"
platform="Web"
runnable=true
export_path="export/web/index.html"
```

### 커스텀 부트 스플래시
```bash
# East Sea Games 로고 사용
cp $HOME/godot-demo/boot_splash.png MyGame/
```

## 📖 References

### 자주 쓰는 노드
- **2D**: Node2D, Sprite2D, CharacterBody2D, RigidBody2D, Area2D, Camera2D, TileMap, AnimatedSprite2D
- **3D**: Node3D, MeshInstance3D, CharacterBody3D, RigidBody3D, Area3D, Camera3D
- **UI**: Control, Label, Button, Panel, HBoxContainer, VBoxContainer
- **오디오**: AudioStreamPlayer, AudioStreamPlayer2D, AudioStreamPlayer3D
- **기타**: Timer, AnimationPlayer, CollisionShape2D/3D

### 유용한 링크
- [Godot 공식 문서](https://docs.godotengine.org/en/stable/)
- [GDQuest 튜토리얼](https://www.gdquest.com/tutorial/godot/)
- [First 2D Game 튜토리얼](https://docs.godotengine.org/en/stable/getting_started/first_2d_game/index.html)

### References 디렉토리
- `references/gdscript-cheatsheet.md`: GDScript 문법 치트시트
- `references/nodes-reference.md`: 자주 쓰는 노드 목록
- `references/best-practices.md`: Godot 베스트 프랙티스
- `references/2d-patterns.md`: 2D 게임 공통 패턴
- `references/3d-patterns.md`: 3D 게임 공통 패턴

---

**Version**: 1.0.0  
**Author**: Miss Kim  
**Date**: 2026-02-05
