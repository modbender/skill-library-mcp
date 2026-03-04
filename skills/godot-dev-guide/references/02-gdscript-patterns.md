# 02 - GDScript 模式

## 狀態機

```gdscript
# state_machine.gd
class_name StateMachine
extends Node

signal state_changed(from_state: StringName, to_state: StringName)

@export var initial_state: State
var current_state: State
var states: Dictionary = {}

func _ready() -> void:
    for child in get_children():
        if child is State:
            states[child.name] = child
            child.state_machine = self
            child.process_mode = Node.PROCESS_MODE_DISABLED
    
    if initial_state:
        current_state = initial_state
        current_state.process_mode = Node.PROCESS_MODE_INHERIT
        current_state.enter()

func _process(delta: float) -> void:
    if current_state:
        current_state.update(delta)

func _physics_process(delta: float) -> void:
    if current_state:
        current_state.physics_update(delta)

func transition_to(state_name: StringName, msg: Dictionary = {}) -> void:
    if not states.has(state_name):
        push_error("State '%s' not found" % state_name)
        return
    
    var previous_state := current_state
    previous_state.exit()
    previous_state.process_mode = Node.PROCESS_MODE_DISABLED
    
    current_state = states[state_name]
    current_state.process_mode = Node.PROCESS_MODE_INHERIT
    current_state.enter(msg)
    
    state_changed.emit(previous_state.name, current_state.name)
```

```gdscript
# state.gd
class_name State
extends Node

var state_machine: StateMachine

func enter(_msg: Dictionary = {}) -> void:
    pass

func exit() -> void:
    pass

func update(_delta: float) -> void:
    pass

func physics_update(_delta: float) -> void:
    pass
```

---

## 單例/自動載入

```gdscript
# game_manager.gd (Project Settings > Autoload)
extends Node

signal game_started
signal game_paused(is_paused: bool)
signal game_over(won: bool)

enum GameState { MENU, PLAYING, PAUSED, GAME_OVER }

var state: GameState = GameState.MENU
var score: int = 0

func _ready() -> void:
    process_mode = Node.PROCESS_MODE_ALWAYS

func start_game() -> void:
    score = 0
    state = GameState.PLAYING
    game_started.emit()

func toggle_pause() -> void:
    var is_paused := state != GameState.PAUSED
    state = GameState.PAUSED if is_paused else GameState.PLAYING
    get_tree().paused = is_paused
    game_paused.emit(is_paused)
```

```gdscript
# event_bus.gd - 全局信號總線
extends Node

signal player_died(player: Node2D)
signal enemy_spawned(enemy: Node2D)
signal item_collected(item_type: StringName, value: int)
signal level_completed(level: int, time: float)
```

---

## 自定義資源

```gdscript
# weapon_stats.gd
class_name WeaponStats
extends Resource

@export var name: StringName
@export var damage: int
@export var attack_speed: float
@export var range: float
@export_multiline var description: String
@export var icon: Texture2D
@export var projectile_scene: PackedScene

func get_dps() -> float:
    return damage * attack_speed
```

```gdscript
# 使用資源
@export var weapon: WeaponStats

func attack() -> void:
    deal_damage(weapon.damage)
```

⚠️ **AI PITFALL：直接修改資源**
```gdscript
# ❌ WRONG - 修改會影響所有使用該資源的實例
weapon.damage += 10

# ✅ CORRECT - 複製後再修改
var my_weapon = weapon.duplicate()
my_weapon.damage += 10
```

---

## 物件池

```gdscript
class_name ObjectPool
extends Node

@export var pooled_scene: PackedScene
@export var initial_size: int = 10

var _available: Array[Node] = []
var _in_use: Array[Node] = []

func _ready() -> void:
    for i in initial_size:
        _create_instance()

func _create_instance() -> Node:
    var instance := pooled_scene.instantiate()
    instance.process_mode = Node.PROCESS_MODE_DISABLED
    instance.visible = false
    add_child(instance)
    _available.append(instance)
    
    if instance.has_signal("returned_to_pool"):
        instance.returned_to_pool.connect(_return.bind(instance))
    
    return instance

func get_instance() -> Node:
    if _available.is_empty():
        _create_instance()
    
    var instance := _available.pop_back()
    instance.process_mode = Node.PROCESS_MODE_INHERIT
    instance.visible = true
    _in_use.append(instance)
    
    if instance.has_method("on_spawn"):
        instance.on_spawn()
    
    return instance

func _return(instance: Node) -> void:
    _in_use.erase(instance)
    instance.process_mode = Node.PROCESS_MODE_DISABLED
    instance.visible = false
    _available.append(instance)
```

---

## 組件模式

```gdscript
# health_component.gd
class_name HealthComponent
extends Node

signal health_changed(current: int, maximum: int)
signal damaged(amount: int, source: Node)
signal died

@export var max_health: int = 100
@export var invincibility_time: float = 0.0

var current_health: int
var _invincible: bool = false

func _ready() -> void:
    current_health = max_health

func take_damage(amount: int, source: Node = null) -> int:
    if _invincible or current_health <= 0:
        return 0
    
    var actual := mini(amount, current_health)
    current_health -= actual
    damaged.emit(actual, source)
    health_changed.emit(current_health, max_health)
    
    if current_health <= 0:
        died.emit()
    elif invincibility_time > 0:
        _start_invincibility()
    
    return actual

func heal(amount: int) -> int:
    var actual := mini(amount, max_health - current_health)
    current_health += actual
    health_changed.emit(current_health, max_health)
    return actual

func _start_invincibility() -> void:
    _invincible = true
    await get_tree().create_timer(invincibility_time).timeout
    _invincible = false
```

---

## Async/Await

```gdscript
# 等待信號
func play_death_animation() -> void:
    $AnimationPlayer.play("death")
    await $AnimationPlayer.animation_finished
    queue_free()

# 等待計時器
func delayed_spawn() -> void:
    await get_tree().create_timer(2.0).timeout
    spawn_enemy()

# 等待下一幀
await get_tree().process_frame
```

---

## ⚠️ AI PITFALL：信號連接錯誤

```gdscript
# ❌ WRONG - 字符串連接（Godot 4 不支援）
button.connect("pressed", self, "_on_button_pressed")

# ✅ CORRECT - Callable 連接
button.pressed.connect(_on_button_pressed)

# ✅ CORRECT - 帶參數
timer.timeout.connect(_on_timeout.bind(extra_data))
```

## ⚠️ AI PITFALL：@onready 時機

```gdscript
# ❌ WRONG - 在宣告時存取其他節點的屬性
@onready var target_pos: Vector2 = $Target.position

# ✅ CORRECT - 在 _ready 中初始化
@onready var target: Node2D = $Target
var target_pos: Vector2

func _ready() -> void:
    target_pos = target.position
```

## ⚠️ AI PITFALL：is_instance_valid 檢查

```gdscript
# ❌ WRONG - 直接使用可能已刪除的節點
target.take_damage(10)

# ✅ CORRECT - 檢查有效性
if is_instance_valid(target):
    target.take_damage(10)
```
