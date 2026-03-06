# GDScript Cheatsheet

GDScript 4.x 문법 빠른 참조 가이드

## 기본 문법

### 변수 선언
```gdscript
# 타입 추론
var speed := 100.0      # float
var name := "Player"    # String
var hp := 100           # int

# 명시적 타입
var position: Vector2 = Vector2.ZERO
var sprite: Sprite2D

# 상수
const MAX_SPEED = 500
const PI_DOUBLED = PI * 2
```

### 함수
```gdscript
# 기본 함수
func greet(name: String):
    print("Hello, " + name)

# 반환값 있는 함수
func add(a: int, b: int) -> int:
    return a + b

# 기본값 파라미터
func shoot(damage: int = 10, speed: float = 200.0):
    pass

# 람다 함수
var multiply = func(x, y): return x * y
print(multiply.call(3, 4))  # 12
```

### 조건문
```gdscript
# if/elif/else
if hp > 80:
    print("Healthy")
elif hp > 30:
    print("Wounded")
else:
    print("Critical")

# 삼항 연산자
var status = "alive" if hp > 0 else "dead"

# match (switch)
match state:
    "idle":
        play_idle_animation()
    "walk", "run":
        play_move_animation()
    _:
        print("Unknown state")
```

### 반복문
```gdscript
# for (range)
for i in range(10):
    print(i)  # 0~9

for i in range(5, 10):
    print(i)  # 5~9

# for (배열)
var fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# while
var count = 0
while count < 10:
    count += 1
```

## 클래스 & 상속

### 클래스 정의
```gdscript
# 스크립트 = 클래스
extends Node2D

# 전역 클래스 등록
class_name Player

# 내부 클래스
class Weapon:
    var damage: int = 10
    func attack():
        print("Attack!")
```

### 생성자
```gdscript
func _init():
    print("Instance created")

func _ready():
    print("Node entered the tree")
```

## Signal (신호)

```gdscript
# 신호 정의
signal health_changed(new_hp)
signal player_died

# 신호 발생
func take_damage(amount):
    hp -= amount
    health_changed.emit(hp)
    if hp <= 0:
        player_died.emit()

# 신호 연결
func _ready():
    $Player.health_changed.connect(_on_health_changed)
    $Player.player_died.connect(_on_player_died)

func _on_health_changed(new_hp):
    print("HP: ", new_hp)

func _on_player_died():
    print("Game Over")
```

## Export (에디터 노출)

```gdscript
# 기본 export
@export var speed: float = 100.0
@export var max_hp: int = 100

# 범위 제한
@export_range(0, 100) var volume: int = 50
@export_range(0.0, 1.0, 0.1) var opacity: float = 1.0

# 파일/폴더
@export_file var config_path: String
@export_dir var data_folder: String

# 컬러
@export var player_color: Color = Color.WHITE

# 노드 참조
@export var target_node: Node
```

## 노드 접근

```gdscript
# $ 단축 문법
var sprite = $Sprite2D
var label = $UI/Label

# get_node()
var sprite = get_node("Sprite2D")
var label = get_node("UI/Label")

# @onready (씬 로드 후 초기화)
@onready var sprite = $Sprite2D
@onready var anim = $AnimationPlayer

# 부모/자식
var parent = get_parent()
var first_child = get_child(0)

# 그룹 검색
var enemies = get_tree().get_nodes_in_group("enemies")
```

## 입력 처리

```gdscript
# 단일 키 체크
func _process(delta):
    if Input.is_action_pressed("ui_right"):
        position.x += 100 * delta

# 벡터 입력 (8방향)
func _physics_process(delta):
    var dir = Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
    velocity = dir * speed
    move_and_slide()

# 마우스/터치
func _input(event):
    if event is InputEventMouseButton:
        if event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
            print("Left click at ", event.position)
```

## Vector 연산

```gdscript
# Vector2
var pos = Vector2(100, 200)
var dir = Vector2.RIGHT  # (1, 0)

# 연산
var sum = pos + dir * 50
var length = pos.length()
var normalized = pos.normalized()
var distance = pos.distance_to(target_pos)

# Vector3
var pos3d = Vector3(1, 2, 3)
var up = Vector3.UP  # (0, 1, 0)
```

## 타이머

```gdscript
# 타이머 노드
@onready var timer = $Timer

func _ready():
    timer.timeout.connect(_on_timer_timeout)
    timer.start(2.0)  # 2초

func _on_timer_timeout():
    print("Timer done!")

# 코드로 타이머 생성
func _ready():
    get_tree().create_timer(3.0).timeout.connect(_on_delayed_action)

func _on_delayed_action():
    print("3 seconds passed")
```

## 트윈 (Tween)

```gdscript
# 위치 이동
var tween = create_tween()
tween.tween_property($Sprite, "position", Vector2(500, 300), 1.0)

# 체인
tween.tween_property($Sprite, "position", Vector2(100, 100), 1.0)
tween.tween_property($Sprite, "modulate:a", 0.0, 0.5)

# Easing
tween.set_ease(Tween.EASE_IN_OUT)
tween.set_trans(Tween.TRANS_CUBIC)
```

## 씬 관리

```gdscript
# 씬 전환
get_tree().change_scene_to_file("res://scenes/level2.tscn")

# 씬 인스턴스 생성
var enemy_scene = preload("res://scenes/enemy.tscn")
var enemy = enemy_scene.instantiate()
add_child(enemy)

# 노드 제거
queue_free()  # 프레임 끝에 제거
$Enemy.queue_free()
```

## 충돌 감지

```gdscript
# Area2D 신호
extends Area2D

func _ready():
    body_entered.connect(_on_body_entered)
    body_exited.connect(_on_body_exited)

func _on_body_entered(body):
    if body.is_in_group("player"):
        print("Player entered!")

# CharacterBody2D
func _physics_process(delta):
    var collision = move_and_collide(velocity * delta)
    if collision:
        print("Hit ", collision.get_collider().name)
```

## 랜덤

```gdscript
# 랜덤 정수
var roll = randi() % 6 + 1  # 1~6

# 랜덤 float
var random_value = randf()  # 0.0~1.0

# 랜덤 범위
var damage = randi_range(10, 20)
var speed = randf_range(100.0, 200.0)

# 배열에서 랜덤 선택
var colors = ["red", "green", "blue"]
var random_color = colors[randi() % colors.size()]
```

## 유용한 함수

```gdscript
# 수학
var clamped = clamp(value, 0, 100)
var lerped = lerp(start, end, 0.5)  # 중간값
var mapped = remap(value, 0, 100, 0, 1)  # 범위 변환

# 문자열
var formatted = "HP: %d/%d" % [hp, max_hp]
var joined = "/".join(["home", "user", "file.txt"])

# 배열
var arr = [1, 2, 3]
arr.append(4)
arr.pop_back()  # 마지막 제거
arr.has(2)  # true

# 딕셔너리
var dict = {"name": "Player", "hp": 100}
dict["level"] = 5
dict.erase("hp")
```

---

**참고**: [GDScript 공식 레퍼런스](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_basics.html)
