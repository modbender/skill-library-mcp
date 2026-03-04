# 08 - 性能優化

## 物件池

```gdscript
class_name ObjectPool
extends Node

@export var pooled_scene: PackedScene
@export var initial_size: int = 10
@export var can_grow: bool = true

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
        if can_grow:
            _create_instance()
        else:
            push_warning("Pool exhausted")
            return null
    
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

使用物件池的場景：
- 子彈/投射物
- 敵人
- 粒子效果
- 收集物品

---

## LOD (細節層級)

```gdscript
extends Node2D

@export var lod_distances: Array[float] = [100, 300, 600]
@export var lod_nodes: Array[Node2D]

var camera: Camera2D

func _process(_delta: float) -> void:
    if not camera:
        camera = get_viewport().get_camera_2d()
        return
    
    var distance := global_position.distance_to(camera.global_position)
    
    for i in lod_nodes.size():
        if i < lod_distances.size():
            lod_nodes[i].visible = distance < lod_distances[i]
        else:
            lod_nodes[i].visible = true
```

---

## ⚠️ AI PITFALL：在 _process 中使用 get_node

```gdscript
# ❌ WRONG - 每幀查找節點
func _process(delta: float) -> void:
    $Sprite2D.modulate.a = health / max_health  # 每幀調用 get_node

# ✅ CORRECT - 緩存節點引用
@onready var sprite: Sprite2D = $Sprite2D

func _process(delta: float) -> void:
    sprite.modulate.a = health / max_health
```

---

## ⚠️ AI PITFALL：熱路徑中分配記憶體

```gdscript
# ❌ WRONG - 每幀創建新陣列
func _process(_delta: float) -> void:
    var nearby = []  # 每幀分配
    for enemy in get_tree().get_nodes_in_group("enemies"):
        if global_position.distance_to(enemy.global_position) < 100:
            nearby.append(enemy)

# ✅ CORRECT - 重用陣列
var _nearby_cache: Array = []

func _process(_delta: float) -> void:
    _nearby_cache.clear()  # 重用而非重新分配
    for enemy in get_tree().get_nodes_in_group("enemies"):
        if global_position.distance_to(enemy.global_position) < 100:
            _nearby_cache.append(enemy)
```

---

## 條件處理

```gdscript
# 屏幕外不處理
func _process(delta: float) -> void:
    if not is_visible_on_screen():
        return
    # 昂貴的處理...

# 根據距離降低更新頻率
var _update_timer: float = 0.0
var _update_interval: float = 0.1  # 每 0.1 秒更新

func _process(delta: float) -> void:
    _update_timer += delta
    if _update_timer < _update_interval:
        return
    _update_timer = 0.0
    
    # 昂貴的 AI 計算...
```

---

## 禁用處理

```gdscript
func _on_off_screen() -> void:
    set_process(false)
    set_physics_process(false)

func _on_on_screen() -> void:
    set_process(true)
    set_physics_process(true)
```

---

## 計時測量

```gdscript
func expensive_operation() -> void:
    var start := Time.get_ticks_usec()
    
    # ... 操作 ...
    
    var elapsed := Time.get_ticks_usec() - start
    print("Operation took: %d microseconds" % elapsed)
```

---

## 異步載入

```gdscript
func load_level_async(level_path: String) -> void:
    $LoadingScreen.show()
    ResourceLoader.load_threaded_request(level_path)
    
    while ResourceLoader.load_threaded_get_status(level_path) == \
          ResourceLoader.THREAD_LOAD_IN_PROGRESS:
        var progress := []
        ResourceLoader.load_threaded_get_status(level_path, progress)
        $LoadingScreen.set_progress(progress[0])
        await get_tree().process_frame
    
    var level = ResourceLoader.load_threaded_get(level_path)
    get_tree().change_scene_to_packed(level)
```

---

## 渲染優化

### 批次處理

```gdscript
# 使用 CanvasGroup 批次處理子節點繪製
# 所有子節點會合併為單一繪製調用

# 場景結構：
# CanvasGroup
#   ├── Sprite2D
#   ├── Sprite2D
#   └── Sprite2D (全部一次繪製)
```

### Y 排序

```gdscript
# 啟用 Y 排序（俯視角遊戲）
# 在父節點設置 y_sort_enabled = true
# 子節點會根據 Y 位置自動排序
```

### 遮擋剔除

```gdscript
# 使用 VisibleOnScreenNotifier2D
@onready var notifier: VisibleOnScreenNotifier2D = $VisibleOnScreenNotifier2D

func _ready() -> void:
    notifier.screen_entered.connect(func(): set_process(true))
    notifier.screen_exited.connect(func(): set_process(false))
```

---

## 物理優化

```gdscript
# 減少物理更新頻率
# Project Settings > Physics > Common > Physics Ticks Per Second
# 預設 60，可降至 30 以節省 CPU

# 使用簡單碰撞形狀
# CircleShape2D > CapsuleShape2D > ConvexPolygonShape2D > ConcavePolygonShape2D

# 禁用不需要的碰撞
collision_layer = 0  # 不參與碰撞
collision_mask = 0   # 不檢測碰撞
```

---

## 記憶體管理

```gdscript
# 清理資源
func _exit_tree() -> void:
    # 斷開信號
    if signal_source.some_signal.is_connected(_on_signal):
        signal_source.some_signal.disconnect(_on_signal)
    
    # 清理計時器
    if _timer:
        _timer.queue_free()

# 使用弱引用
var _weak_reference: WeakRef

func set_target(node: Node) -> void:
    _weak_reference = weakref(node)

func get_target() -> Node:
    return _weak_reference.get_ref()
```

---

## Profiler 使用

```
Debugger > Profiler:
- Frame Time：每幀時間
- Physics Frame：物理更新時間
- Idle：場景樹處理時間
- Process Functions：各函數耗時

Monitor:
- FPS
- Object Count
- Node Count
- Resource Count
```
