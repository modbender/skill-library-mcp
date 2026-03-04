# 04 - 場景與節點

## 場景組合模式

```
Player (CharacterBody2D)
├── CollisionShape2D
├── Sprite2D
├── AnimationPlayer
├── StateMachine (Node)
│   ├── IdleState
│   ├── RunState
│   └── JumpState
├── Hitbox (Area2D)
└── Hurtbox (Area2D)
```

**原則：組合優先於繼承**

---

## 場景實例化

```gdscript
# 預載入頻繁使用的場景
const BulletScene := preload("res://scenes/projectiles/bullet.tscn")

func shoot() -> void:
    var bullet := BulletScene.instantiate() as Bullet
    bullet.global_position = $Muzzle.global_position
    bullet.direction = facing_direction
    get_tree().current_scene.add_child(bullet)
```

---

## 場景繼承

```gdscript
# enemy_base.gd - 基類
class_name EnemyBase
extends CharacterBody2D

@export var max_health: int = 100
@export var move_speed: float = 100.0

var health: int

func _ready() -> void:
    health = max_health

func take_damage(amount: int) -> void:
    health -= amount
    if health <= 0:
        die()

func die() -> void:
    queue_free()
```

```gdscript
# enemy_flying.gd - 繼承
class_name EnemyFlying
extends EnemyBase

@export var flight_height: float = 50.0

func _physics_process(delta: float) -> void:
    velocity.y = sin(Time.get_ticks_msec() * 0.001) * flight_height
    move_and_slide()
```

---

## 節點群組

```gdscript
# 添加到群組
add_to_group("enemies")
add_to_group("damageable")

# 查找群組中的所有節點
func damage_all_enemies(amount: int) -> void:
    for enemy in get_tree().get_nodes_in_group("enemies"):
        if enemy.has_method("take_damage"):
            enemy.take_damage(amount)

# 調用群組方法
get_tree().call_group("enemies", "alert", player_position)
```

---

## 常用節點層級

### 2D 角色

```
Character (CharacterBody2D)
├── Sprite2D
├── CollisionShape2D
├── AnimationPlayer
├── Camera2D (optional)
└── UI (CanvasLayer)
    └── HealthBar
```

### 3D 角色

```
Character (CharacterBody3D)
├── MeshInstance3D
├── CollisionShape3D
├── AnimationPlayer
├── Camera3D
│   └── SpringArm3D
└── RayCast3D
```

### 可收集物品

```
Collectible (Area2D)
├── Sprite2D
├── CollisionShape2D
├── AnimationPlayer
└── AudioStreamPlayer2D
```

---

## ⚠️ AI PITFALL：節點路徑錯誤

```gdscript
# ❌ WRONG - 硬編碼絕對路徑
var player = get_node("/root/Main/Level/Player")

# ✅ CORRECT - 使用相對路徑
var player = get_tree().get_first_node_in_group("player")

# ✅ CORRECT - 使用 unique name (%前綴)
@onready var health_bar: ProgressBar = %HealthBar
```

---

## ⚠️ AI PITFALL：get_node 在 _init 中

```gdscript
# ❌ WRONG - 節點樹還沒準備好
func _init() -> void:
    var sprite = $Sprite2D  # 錯誤！

# ✅ CORRECT - 使用 @onready 或 _ready
@onready var sprite: Sprite2D = $Sprite2D
```

---

## ⚠️ AI PITFALL：queue_free 後存取

```gdscript
# ❌ WRONG - queue_free 後節點還存在一幀
enemy.queue_free()
enemy.position = Vector2.ZERO  # 可能出問題

# ✅ CORRECT - 先處理再刪除
enemy.position = Vector2.ZERO
enemy.queue_free()

# ✅ 或者檢查
if is_instance_valid(enemy):
    enemy.position = Vector2.ZERO
```

---

## 場景管理器模式

```gdscript
# scene_manager.gd (Autoload)
extends Node

signal scene_loaded(scene: Node)
signal transition_finished

var _current_scene: Node

func _ready() -> void:
    _current_scene = get_tree().current_scene

func change_scene(scene_path: String) -> void:
    await _fade_out()
    _load_scene(scene_path)
    await _fade_in()

func _load_scene(path: String) -> void:
    if _current_scene:
        _current_scene.queue_free()
    
    var scene := load(path) as PackedScene
    _current_scene = scene.instantiate()
    get_tree().root.add_child(_current_scene)
    get_tree().current_scene = _current_scene
    scene_loaded.emit(_current_scene)

func _fade_out() -> void:
    var tween := create_tween()
    # 實現淡出效果
    await tween.finished

func _fade_in() -> void:
    var tween := create_tween()
    # 實現淡入效果
    await tween.finished
    transition_finished.emit()
```

---

## Unique Name (% 前綴)

在編輯器中設置節點為 Unique Name 後：

```gdscript
# 不管層級深度，直接存取
@onready var health_label: Label = %HealthLabel
@onready var score_display: Label = %ScoreDisplay
```

比硬編碼路徑更穩固，移動節點不會破壞引用。
