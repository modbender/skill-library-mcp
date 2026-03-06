# 03 - 文件格式

## 核心差異

| 文件類型 | 用途 | 語法 |
|----------|------|------|
| .gd | 程式碼 | 完整 GDScript |
| .tscn | 場景 | 嚴格序列化格式 |
| .tres | 資源 | 嚴格序列化格式 |

---

## GDScript (.gd)

```gdscript
extends Node
class_name MyClass

var speed: float = 5.0
const MAX_HEALTH = 100

@export var damage: int = 10
@onready var sprite: Sprite2D = $Sprite2D

func _ready() -> void:
    var scene = preload("res://scenes/bullet.tscn")
    print("Ready")
```

---

## 場景文件 (.tscn)

```
[gd_scene load_steps=3 format=3 uid="uid://abc123"]

[ext_resource type="Script" path="res://scripts/player.gd" id="1_script"]
[ext_resource type="Texture2D" path="res://assets/player.png" id="2_texture"]

[sub_resource type="RectangleShape2D" id="RectangleShape2D_1"]
size = Vector2(32, 64)

[node name="Player" type="CharacterBody2D"]
script = ExtResource("1_script")
speed = 200.0

[node name="Sprite2D" type="Sprite2D" parent="."]
texture = ExtResource("2_texture")

[node name="CollisionShape2D" type="CollisionShape2D" parent="."]
shape = SubResource("RectangleShape2D_1")
```

### 關鍵規則

1. **ext_resource** - 外部文件引用
2. **sub_resource** - 內嵌資源
3. **node** - 節點定義
4. **parent="."** - 父節點路徑

---

## 資源文件 (.tres)

```
[gd_resource type="Resource" script_class="WeaponStats" load_steps=2 format=3]

[ext_resource type="Script" path="res://scripts/weapon_stats.gd" id="1"]

[resource]
script = ExtResource("1")
name = "Sword"
damage = 25
attack_speed = 1.5
```

### 關鍵規則

1. **不能使用 GDScript 關鍵字**（var, const, func）
2. **不能使用 preload()**
3. **陣列必須類型化**

---

## ⚠️ AI PITFALL：.tres 中使用 GDScript 語法

```
# ❌ WRONG - .tres 中
script = preload("res://script.gd")
var items = [1, 2, 3]
const DAMAGE = 10

# ✅ CORRECT - .tres 中
[ext_resource type="Script" path="res://script.gd" id="1"]

[resource]
script = ExtResource("1")
items = Array[int]([1, 2, 3])
damage = 10
```

---

## ⚠️ AI PITFALL：未宣告 ExtResource

```
# ❌ WRONG - 直接使用未宣告的 ID
[resource]
script = ExtResource("1_script")  # 錯誤！未宣告

# ✅ CORRECT - 先宣告再使用
[ext_resource type="Script" path="res://script.gd" id="1_script"]

[resource]
script = ExtResource("1_script")
```

---

## ⚠️ AI PITFALL：未類型化陣列

```
# ❌ WRONG - .tres 中
effects = [SubResource("Effect_1")]

# ✅ CORRECT - .tres 中
effects = Array[Resource]([SubResource("Effect_1")])
```

---

## ⚠️ AI PITFALL：實例屬性覆蓋

當實例化場景時，需要覆蓋子節點屬性：

```
# ❌ WRONG - 忘記設置實例的子節點屬性
[node name="KeyPickup" parent="." instance=ExtResource("6_pickup")]
# 子節點的 item_resource 是 null！

# ✅ CORRECT - 使用 index 語法覆蓋
[node name="KeyPickup" parent="." instance=ExtResource("6_pickup")]

[node name="PickupInteraction" parent="KeyPickup" index="0"]
item_resource = ExtResource("7_key")
```

---

## 常見資料類型格式

### .tres/.tscn 中的類型

```
# 向量
position = Vector2(100, 200)
position = Vector3(1, 2, 3)

# 顏色
modulate = Color(1, 0, 0, 1)
modulate = Color("#ff0000")

# 陣列
items = Array[int]([1, 2, 3])
positions = Array[Vector2]([Vector2(0, 0), Vector2(1, 1)])

# 字典（避免在 .tres 中使用複雜字典）
data = {"key": "value"}

# 資源引用
texture = ExtResource("1")
shape = SubResource("Shape_1")

# 布林
visible = true
disabled = false

# 枚舉（使用整數）
collision_layer = 1
collision_mask = 6
```

---

## 安全編輯建議

### 適合文字編輯

- 修改數值屬性
- 添加/修改 @export 預設值
- 添加簡單節點

### 使用編輯器

- 複雜節點層級
- 動畫
- 粒子系統
- UI 佈局

---

## 驗證腳本

編輯 .tres/.tscn 後驗證：

```bash
# 語法檢查
godot --path . --check-only --headless

# 測試載入
godot --path . --headless --quit
```
