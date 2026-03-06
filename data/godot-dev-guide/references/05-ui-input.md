# 05 - UI 與輸入

## UI 節點層級

### 主選單

```
MainMenu (Control) [PRESET_FULL_RECT]
├── Background (TextureRect)
├── VBoxContainer [centered]
│   ├── Logo (TextureRect)
│   ├── PlayButton (Button)
│   ├── OptionsButton (Button)
│   └── QuitButton (Button)
└── OptionsPanel (PanelContainer) [hidden]
```

### HUD

```
HUD (CanvasLayer)
├── MarginContainer [PRESET_FULL_RECT]
│   ├── TopBar (HBoxContainer)
│   │   ├── HealthBar (TextureProgressBar)
│   │   └── ScoreLabel (Label)
│   └── BottomBar (HBoxContainer)
│       └── AmmoLabel (Label)
└── DamageOverlay (ColorRect) [hidden]
```

---

## 輸入處理

### Input Actions

```gdscript
func _process(_delta: float) -> void:
    if Input.is_action_pressed("move_right"):
        move_right()
    
    if Input.is_action_just_pressed("jump"):
        jump()
    
    # 軸輸入 (-1 到 1)
    var direction := Input.get_vector("move_left", "move_right", "move_up", "move_down")
```

### Input Events

```gdscript
func _input(event: InputEvent) -> void:
    if event is InputEventKey:
        if event.pressed and event.keycode == KEY_ESCAPE:
            toggle_pause()
    
    if event is InputEventMouseButton:
        if event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
            shoot()
    
    if event is InputEventMouseMotion:
        look_at_mouse(event.position)

func _unhandled_input(event: InputEvent) -> void:
    # 只接收 UI 未處理的輸入
    if event.is_action_pressed("pause"):
        toggle_pause()
        get_viewport().set_input_as_handled()
```

---

## ⚠️ AI PITFALL：mouse_filter 設置

```gdscript
# ❌ WRONG - Control 節點阻擋點擊
# 預設 mouse_filter = MOUSE_FILTER_STOP

# ✅ CORRECT - 讓點擊穿透
control_node.mouse_filter = Control.MOUSE_FILTER_IGNORE

# 選項：
# MOUSE_FILTER_STOP - 攔截並停止傳播
# MOUSE_FILTER_PASS - 處理但繼續傳播
# MOUSE_FILTER_IGNORE - 完全忽略
```

---

## ⚠️ AI PITFALL：_input vs _gui_input

```gdscript
# ❌ WRONG - UI 元素使用 _input
extends Button
func _input(event: InputEvent) -> void:
    # 這會接收所有輸入，不只是按鈕上的

# ✅ CORRECT - UI 元素使用 _gui_input
extends Button  
func _gui_input(event: InputEvent) -> void:
    # 只接收該 UI 元素上的輸入
    if event is InputEventMouseButton and event.pressed:
        custom_click_handling()
```

---

## ⚠️ AI PITFALL：輸入處理順序

```
輸入事件傳播順序：
1. _input() - 全局，最先
2. _gui_input() - UI 節點
3. _unhandled_input() - 未被 UI 處理的
4. _unhandled_key_input() - 未處理的鍵盤

停止傳播：
get_viewport().set_input_as_handled()
```

---

## 暫停選單

```gdscript
extends CanvasLayer

var is_paused: bool = false

func _ready() -> void:
    $PausePanel.hide()
    process_mode = Node.PROCESS_MODE_ALWAYS  # 暫停時仍處理

func _input(event: InputEvent) -> void:
    if event.is_action_pressed("pause"):
        toggle_pause()

func toggle_pause() -> void:
    is_paused = !is_paused
    get_tree().paused = is_paused
    $PausePanel.visible = is_paused
    
    if is_paused:
        Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
    else:
        Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
```

---

## 對話系統

```gdscript
extends CanvasLayer
class_name DialogBox

signal dialog_finished

@onready var text_label: RichTextLabel = $Panel/TextLabel

var dialog_lines: Array[Dictionary] = []
var current_line: int = 0
var is_typing: bool = false

func show_dialog(lines: Array[Dictionary]) -> void:
    dialog_lines = lines
    current_line = 0
    show()
    display_line()

func display_line() -> void:
    if current_line >= dialog_lines.size():
        hide()
        dialog_finished.emit()
        return
    
    var line := dialog_lines[current_line]
    text_label.text = line.get("text", "")
    text_label.visible_ratio = 0.0
    is_typing = true
    
    var tween := create_tween()
    tween.tween_property(text_label, "visible_ratio", 1.0, 1.0)
    tween.tween_callback(func(): is_typing = false)

func _input(event: InputEvent) -> void:
    if not visible:
        return
    
    if event.is_action_pressed("ui_accept"):
        if is_typing:
            text_label.visible_ratio = 1.0
            is_typing = false
        else:
            current_line += 1
            display_line()
```

---

## 觸控控制

### 虛擬搖桿

```gdscript
extends Control
class_name VirtualJoystick

signal joystick_input(direction: Vector2)

@export var deadzone: float = 0.2
@export var clamp_zone: float = 75.0

@onready var base: TextureRect = $Base
@onready var stick: TextureRect = $Stick

var touch_index: int = -1

func _input(event: InputEvent) -> void:
    if event is InputEventScreenTouch:
        if event.pressed and is_point_inside(event.position):
            touch_index = event.index
            update_stick(event.position)
        elif not event.pressed and event.index == touch_index:
            reset()
    
    if event is InputEventScreenDrag:
        if event.index == touch_index:
            update_stick(event.position)

func update_stick(touch_pos: Vector2) -> void:
    var center := base.global_position + base.size / 2
    var direction := (touch_pos - center).limit_length(clamp_zone)
    stick.global_position = center + direction - stick.size / 2
    
    var normalized := direction / clamp_zone
    if normalized.length() < deadzone:
        normalized = Vector2.ZERO
    joystick_input.emit(normalized)

func reset() -> void:
    touch_index = -1
    stick.position = base.size / 2 - stick.size / 2
    joystick_input.emit(Vector2.ZERO)
```

---

## 響應式佈局

```gdscript
extends Control

func _ready() -> void:
    get_tree().root.size_changed.connect(_on_viewport_resized)
    _on_viewport_resized()

func _on_viewport_resized() -> void:
    var viewport_size := get_viewport_rect().size
    var aspect := viewport_size.x / viewport_size.y
    
    if aspect < 1.0:
        apply_portrait_layout()
    else:
        apply_landscape_layout()
```

---

## UI 動畫

```gdscript
# 彈入
func bounce_in(node: Control) -> void:
    node.scale = Vector2.ZERO
    node.show()
    var tween := create_tween()
    tween.set_ease(Tween.EASE_OUT)
    tween.set_trans(Tween.TRANS_ELASTIC)
    tween.tween_property(node, "scale", Vector2.ONE, 0.5)

# 抖動（錯誤提示）
func shake(node: Control, intensity: float = 10.0) -> void:
    var original_pos := node.position
    var tween := create_tween()
    for i in 5:
        tween.tween_property(node, "position", 
            original_pos + Vector2(randf_range(-intensity, intensity), 0), 0.05)
    tween.tween_property(node, "position", original_pos, 0.05)
```
