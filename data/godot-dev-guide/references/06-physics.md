# 06 - 物理系統

## CharacterBody2D 移動

```gdscript
extends CharacterBody2D

const SPEED := 300.0
const JUMP_VELOCITY := -400.0
const GRAVITY := 980.0

func _physics_process(delta: float) -> void:
    # 重力
    if not is_on_floor():
        velocity.y += GRAVITY * delta
    
    # 跳躍
    if Input.is_action_just_pressed("jump") and is_on_floor():
        velocity.y = JUMP_VELOCITY
    
    # 水平移動
    var direction := Input.get_axis("move_left", "move_right")
    if direction:
        velocity.x = direction * SPEED
    else:
        velocity.x = move_toward(velocity.x, 0, SPEED)
    
    move_and_slide()
```

---

## CharacterBody3D 移動

```gdscript
extends CharacterBody3D

@export var speed := 5.0
@export var jump_velocity := 4.5
@export var mouse_sensitivity := 0.002

var gravity: float = ProjectSettings.get_setting("physics/3d/default_gravity")

func _physics_process(delta: float) -> void:
    if not is_on_floor():
        velocity.y -= gravity * delta
    
    if Input.is_action_just_pressed("jump") and is_on_floor():
        velocity.y = jump_velocity
    
    var input_dir := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
    var direction := (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()
    
    if direction:
        velocity.x = direction.x * speed
        velocity.z = direction.z * speed
    else:
        velocity.x = move_toward(velocity.x, 0, speed)
        velocity.z = move_toward(velocity.z, 0, speed)
    
    move_and_slide()

func _input(event: InputEvent) -> void:
    if event is InputEventMouseMotion:
        rotate_y(-event.relative.x * mouse_sensitivity)
        $Camera3D.rotate_x(-event.relative.y * mouse_sensitivity)
        $Camera3D.rotation.x = clamp($Camera3D.rotation.x, -PI/2, PI/2)
```

---

## 碰撞層級

```
Layer 設置 (Project Settings > Layer Names):
Layer 1: Player
Layer 2: Enemies  
Layer 3: Projectiles
Layer 4: Environment
Layer 5: Pickups
Layer 6: Triggers
```

```gdscript
# 設置碰撞
collision_layer = 1   # 我是什麼
collision_mask = 6    # 我和什麼碰撞

# 程式碼設置位元
func set_layer_bit(layer: int, enabled: bool) -> void:
    if enabled:
        collision_layer |= (1 << layer)
    else:
        collision_layer &= ~(1 << layer)
```

---

## Area2D 檢測

### Hitbox/Hurtbox 模式

```gdscript
# hitbox.gd
class_name Hitbox
extends Area2D

@export var damage: int = 10

func _ready() -> void:
    area_entered.connect(_on_area_entered)

func _on_area_entered(area: Area2D) -> void:
    if area is Hurtbox:
        area.take_hit(self)
```

```gdscript
# hurtbox.gd
class_name Hurtbox
extends Area2D

signal hit_received(hitbox: Hitbox)

func take_hit(hitbox: Hitbox) -> void:
    hit_received.emit(hitbox)
```

---

## RayCast 檢測

```gdscript
@onready var raycast: RayCast2D = $RayCast2D

func _physics_process(_delta: float) -> void:
    if raycast.is_colliding():
        var collider = raycast.get_collider()
        var point = raycast.get_collision_point()
        var normal = raycast.get_collision_normal()
        
        if collider.is_in_group("enemies"):
            target_enemy(collider)
```

---

## ⚠️ AI PITFALL：PhysicsServer 查詢 API

```gdscript
# ❌ WRONG - Godot 3 語法
var space_state = get_world_2d().direct_space_state
var result = space_state.intersect_ray(from, to)

# ✅ CORRECT - Godot 4 語法
var space_state = get_world_2d().direct_space_state
var query = PhysicsRayQueryParameters2D.create(from, to)
query.collision_mask = collision_mask
query.exclude = [self]
var result = space_state.intersect_ray(query)

if result:
    var collider = result.collider
    var position = result.position
    var normal = result.normal
```

---

## ⚠️ AI PITFALL：move_and_slide 返回值

```gdscript
# ❌ WRONG - Godot 3 語法
velocity = move_and_slide(velocity, Vector2.UP)

# ✅ CORRECT - Godot 4 語法
# velocity 是屬性，不是參數
velocity = some_velocity
move_and_slide()  # 返回 bool，不是 velocity
# velocity 會被自動修改
```

---

## ⚠️ AI PITFALL：碰撞層設置錯誤

```gdscript
# ❌ WRONG - Layer 和 Mask 混淆
# Layer = 我是什麼
# Mask = 我檢測什麼

# 子彈應該：
# Layer = 3 (Projectiles)
# Mask = 1 | 2 (Player | Enemies)

# ✅ CORRECT 設置
bullet.collision_layer = 4  # 二進制 100 = Layer 3
bullet.collision_mask = 3   # 二進制 011 = Layer 1 和 2
```

---

## Shape Query

```gdscript
# 圓形範圍檢測
func get_entities_in_range(center: Vector2, radius: float) -> Array:
    var space_state = get_world_2d().direct_space_state
    var shape = CircleShape2D.new()
    shape.radius = radius
    
    var query = PhysicsShapeQueryParameters2D.new()
    query.shape = shape
    query.transform = Transform2D(0, center)
    query.collision_mask = collision_mask
    
    var results = space_state.intersect_shape(query)
    return results.map(func(r): return r.collider)
```

---

## 物理材質

```gdscript
# 設置彈性和摩擦
var material := PhysicsMaterial.new()
material.bounce = 0.5
material.friction = 0.2
$CollisionShape2D.physics_material_override = material
```

---

## 常見物理配置

### 平台遊戲角色

```gdscript
# CharacterBody2D 設置
motion_mode = MOTION_MODE_GROUNDED
floor_max_angle = deg_to_rad(45)
floor_snap_length = 8.0
platform_floor_layers = 1
```

### 俯視角角色

```gdscript
# CharacterBody2D 設置
motion_mode = MOTION_MODE_FLOATING
```
