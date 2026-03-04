---
name: godot-dev-guide
description: "Godot 4.x 完整開發指南。涵蓋 GDScript 模式、文件格式（.gd/.tscn/.tres）、場景架構、物理/UI/音效、性能優化、多平台導出、測試。自動觸發於 Godot 相關開發。"
autoInvoke: true
priority: high
triggers:
  - "godot"
  - "gdscript"
  - ".gd"
  - ".tscn"
  - ".tres"
  - "scene"
  - "node"
  - "CharacterBody"
  - "RigidBody"
  - "Area2D"
  - "Area3D"
  - "project.godot"
---

# Godot Dev Guide Skill

Godot 4.x 遊戲開發完整指南，專為 AI 輔助開發設計。

## 核心原則

### 1. 文件格式差異（最重要！）

```
.gd  → GDScript 程式碼（完整語言）
.tscn → 場景序列化（嚴格格式，非 GDScript）
.tres → 資源序列化（嚴格格式，非 GDScript）
```

⚠️ **AI PITFALL：混淆 GDScript 與資源格式**
```gdscript
# ❌ WRONG in .tres/.tscn
script = preload("res://script.gd")
var items = [1, 2, 3]

# ✅ CORRECT in .tres/.tscn
[ext_resource type="Script" path="res://script.gd" id="1"]
script = ExtResource("1")
items = Array[int]([1, 2, 3])
```

### 2. 類型系統（永遠使用）

```gdscript
# 變數類型
var health: int = 100
var speed: float = 200.0
var items: Array[Item] = []
var stats: Dictionary = {}

# 函數簽名
func calculate_damage(base: int, multiplier: float) -> int:
    return int(base * multiplier)
```

### 3. 架構模式

```
組合優先於繼承
信號用於解耦通信
資源用於數據配置
自動載入用於全局系統
```

---

## 快速參考

### 項目結構

```
res://
├── project.godot
├── scenes/           # .tscn 場景
│   ├── player/
│   ├── enemies/
│   └── ui/
├── scripts/          # .gd 腳本
├── assets/           # 資源文件
├── autoload/         # 單例腳本
├── resources/        # .tres 資源
└── test/             # 測試
```

### 常用節點

| 2D | 3D | 用途 |
|----|----|----|
| CharacterBody2D | CharacterBody3D | 玩家/NPC 移動 |
| RigidBody2D | RigidBody3D | 物理模擬 |
| Area2D | Area3D | 碰撞檢測（無物理） |
| Sprite2D | MeshInstance3D | 視覺渲染 |

### Export 變數

```gdscript
@export var speed: float = 5.0
@export_range(0, 100, 1) var health: int = 100
@export_file("*.tscn") var next_level: String
@export_group("Combat")
@export var damage: int = 10
```

### 信號模式

```gdscript
signal health_changed(current: int, maximum: int)
signal died

func take_damage(amount: int) -> void:
    health -= amount
    health_changed.emit(health, max_health)
    if health <= 0:
        died.emit()
```

### 節點引用

```gdscript
@onready var sprite: Sprite2D = $Sprite2D
@onready var anim: AnimationPlayer = $AnimationPlayer
```

---

## 關鍵陷阱清單

| 陷阱 | 錯誤寫法 | 正確寫法 |
|-----|---------|---------|
| .tres 使用 preload | `preload("res://x.gd")` | `ExtResource("id")` |
| .tres 使用 var | `var x = 5` | `x = 5` |
| 未類型化陣列 | `[1, 2, 3]` in .tres | `Array[int]([1, 2, 3])` |
| 缺少 ext_resource | 直接使用 id | 先宣告 ext_resource |
| @onready 初始化 | 在宣告時存取其他節點 | 等到 _ready() |
| 直接修改資源 | `resource.value = x` | `resource.duplicate()` |
| 輸入處理 | UI 和遊戲混用 _input | UI 用 _gui_input |

---

## 參考文件

| 主題 | 路徑 |
|------|------|
| 項目結構 | `references/01-project-structure.md` |
| GDScript 模式 | `references/02-gdscript-patterns.md` |
| 文件格式 | `references/03-file-formats.md` |
| 場景與節點 | `references/04-scenes-nodes.md` |
| UI 與輸入 | `references/05-ui-input.md` |
| 物理系統 | `references/06-physics.md` |
| 音效與動畫 | `references/07-audio-animation.md` |
| 性能優化 | `references/08-performance.md` |
| 導出平台 | `references/09-export.md` |
| 測試指南 | `references/10-testing.md` |

---

## CLI 快速命令

```bash
# 運行遊戲
godot --path .

# 驗證腳本
godot --path . --check-only --script path/to/script.gd

# 無頭測試
godot --path . --headless --quit

# 導出
godot --path . --export-release "Preset Name" builds/game.exe
```

---

**Version:** 1.0.0 | **Last Updated:** 2026-02-17
