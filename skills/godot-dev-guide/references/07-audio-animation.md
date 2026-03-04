# 07 - 音效與動畫

## AnimationPlayer

```gdscript
@onready var anim: AnimationPlayer = $AnimationPlayer

func _ready() -> void:
    anim.animation_finished.connect(_on_animation_finished)

func play_attack() -> void:
    anim.play("attack")
    await anim.animation_finished
    return_to_idle()

func _on_animation_finished(anim_name: StringName) -> void:
    match anim_name:
        "death":
            queue_free()
        "attack":
            can_attack = true
```

---

## AnimationTree (狀態機)

```gdscript
@onready var anim_tree: AnimationTree = $AnimationTree
@onready var state_machine: AnimationNodeStateMachinePlayback = \
    anim_tree.get("parameters/playback")

func _physics_process(_delta: float) -> void:
    # 設置混合參數
    anim_tree.set("parameters/blend_position", velocity.x)
    
    # 狀態轉換
    if is_on_floor():
        if velocity.x != 0:
            state_machine.travel("run")
        else:
            state_machine.travel("idle")
    else:
        state_machine.travel("jump")
```

---

## Tween 動畫

```gdscript
# 一次性動畫
func flash_white() -> void:
    var tween := create_tween()
    tween.tween_property($Sprite2D, "modulate", Color.WHITE, 0.1)
    tween.tween_property($Sprite2D, "modulate", Color(1, 1, 1, 1), 0.1)

# 彈性動畫
func bounce_in() -> void:
    var tween := create_tween()
    tween.set_ease(Tween.EASE_OUT)
    tween.set_trans(Tween.TRANS_ELASTIC)
    tween.tween_property(self, "scale", Vector2.ONE, 0.5).from(Vector2.ZERO)

# 並行動畫
func fade_and_move() -> void:
    var tween := create_tween()
    tween.set_parallel(true)
    tween.tween_property(self, "modulate:a", 0.0, 1.0)
    tween.tween_property(self, "position:y", position.y - 50, 1.0)
    tween.chain().tween_callback(queue_free)

# 循環動畫
func pulse() -> void:
    var tween := create_tween()
    tween.set_loops()  # 無限循環
    tween.tween_property(self, "scale", Vector2(1.1, 1.1), 0.5)
    tween.tween_property(self, "scale", Vector2.ONE, 0.5)
```

---

## ⚠️ AI PITFALL：Tween 生命週期

```gdscript
# ❌ WRONG - 儲存 tween 引用但不處理
var tween: Tween

func animate() -> void:
    tween = create_tween()  # 舊的 tween 可能還在運行
    tween.tween_property(...)

# ✅ CORRECT - 停止舊的 tween
var tween: Tween

func animate() -> void:
    if tween and tween.is_running():
        tween.kill()
    tween = create_tween()
    tween.tween_property(...)
```

---

## ⚠️ AI PITFALL：animation_finished 信號

```gdscript
# ❌ WRONG - 忘記檢查是哪個動畫結束
func _on_animation_finished(anim_name: StringName) -> void:
    queue_free()  # 任何動畫結束都會觸發！

# ✅ CORRECT - 檢查動畫名稱
func _on_animation_finished(anim_name: StringName) -> void:
    if anim_name == "death":
        queue_free()
```

---

## 音效管理器

```gdscript
# audio_manager.gd (Autoload)
extends Node

var music_player: AudioStreamPlayer
var sfx_players: Array[AudioStreamPlayer] = []
const SFX_POOL_SIZE := 8

func _ready() -> void:
    music_player = AudioStreamPlayer.new()
    music_player.bus = "Music"
    add_child(music_player)
    
    for i in SFX_POOL_SIZE:
        var player := AudioStreamPlayer.new()
        player.bus = "SFX"
        add_child(player)
        sfx_players.append(player)

func play_music(stream: AudioStream, fade_in: float = 1.0) -> void:
    music_player.stream = stream
    music_player.volume_db = -80
    music_player.play()
    
    var tween := create_tween()
    tween.tween_property(music_player, "volume_db", 0, fade_in)

func play_sfx(stream: AudioStream) -> void:
    for player in sfx_players:
        if not player.playing:
            player.stream = stream
            player.play()
            return
    # 所有 player 都在用，使用第一個
    sfx_players[0].stream = stream
    sfx_players[0].play()

func stop_music(fade_out: float = 1.0) -> void:
    var tween := create_tween()
    tween.tween_property(music_player, "volume_db", -80, fade_out)
    tween.tween_callback(music_player.stop)
```

---

## 音效總線設置

```
Project Settings > Audio > Buses:

Master
├── Music (適合循環背景音樂)
├── SFX (適合短音效)
└── UI (適合 UI 音效)
```

```gdscript
# 調整音量
AudioServer.set_bus_volume_db(AudioServer.get_bus_index("Music"), -6)

# 靜音
AudioServer.set_bus_mute(AudioServer.get_bus_index("SFX"), true)
```

---

## 2D/3D 音效

```gdscript
# 2D 位置音效
var audio := AudioStreamPlayer2D.new()
audio.stream = preload("res://audio/explosion.wav")
audio.position = explosion_position
add_child(audio)
audio.play()
audio.finished.connect(audio.queue_free)

# 3D 位置音效
var audio := AudioStreamPlayer3D.new()
audio.stream = preload("res://audio/footstep.wav")
audio.global_position = foot_position
audio.unit_size = 10.0  # 聽到滿音量的距離
audio.max_distance = 50.0  # 聽不到的距離
add_child(audio)
audio.play()
```

---

## 動畫軌道

### 常用軌道類型

```
Property Track    - 任意屬性動畫
Bezier Track      - 平滑數值曲線
Call Method Track - 在特定幀調用方法
Audio Track       - 播放音效
Animation Track   - 觸發其他動畫
```

### 方法調用軌道

在動畫特定幀調用腳本方法：

```gdscript
# 在動畫編輯器中添加 Call Method Track
# 選擇時間點，添加 spawn_particles() 調用

func spawn_particles() -> void:
    var particles = preload("res://effects/hit_particles.tscn").instantiate()
    add_child(particles)
```

---

## 過渡效果

```gdscript
extends CanvasLayer
class_name TransitionManager

@onready var color_rect: ColorRect = $ColorRect

func fade_to_black(duration: float = 0.5) -> void:
    color_rect.show()
    color_rect.modulate.a = 0.0
    var tween := create_tween()
    tween.tween_property(color_rect, "modulate:a", 1.0, duration)
    await tween.finished

func fade_from_black(duration: float = 0.5) -> void:
    var tween := create_tween()
    tween.tween_property(color_rect, "modulate:a", 0.0, duration)
    await tween.finished
    color_rect.hide()

func transition_to_scene(scene_path: String) -> void:
    await fade_to_black()
    get_tree().change_scene_to_file(scene_path)
    await fade_from_black()
```
