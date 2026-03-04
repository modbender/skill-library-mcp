# 09 - 導出平台

## 平台總覽

| 平台 | 輸出格式 | 要求 |
|------|----------|------|
| HTML5 | .html + .wasm | WebGL 2.0 瀏覽器 |
| Android | .apk / .aab | Android SDK + JDK |
| iOS | .ipa | Xcode + Apple Developer |
| Windows | .exe | 無（可選 Windows SDK） |
| macOS | .app / .dmg | Xcode CLI 工具 |
| Linux | 二進制 | 無 |

---

## HTML5 導出

### 配置

```ini
# export_presets.cfg
[preset.0]
name="HTML5"
platform="Web"

[preset.0.options]
html/export_icon=true
html/canvas_resize_policy=2
vram_texture_compression/for_mobile=true
```

### HTML5 特定代碼

```gdscript
func _ready() -> void:
    if OS.has_feature("web"):
        configure_for_web()

func configure_for_web() -> void:
    # 禁用不支援的功能
    $FullscreenButton.disabled = true
    
    # 處理瀏覽器焦點
    get_tree().root.focus_exited.connect(func(): get_tree().paused = true)
    get_tree().root.focus_entered.connect(func(): get_tree().paused = false)
```

### 伺服器 Headers

```apache
# Apache .htaccess
Header set Cross-Origin-Opener-Policy "same-origin"
Header set Cross-Origin-Embedder-Policy "require-corp"
AddType application/wasm .wasm
```

---

## Android 導出

### 設置

1. 安裝 Android SDK（透過 Android Studio）
2. 安裝 JDK 17
3. 配置 Editor Settings:
   - `export/android/android_sdk_path`
   - `export/android/java_sdk_path`

### Android 特定代碼

```gdscript
func _ready() -> void:
    if OS.has_feature("android"):
        configure_for_android()

func configure_for_android() -> void:
    get_tree().set_auto_accept_quit(false)  # 處理返回鍵
    
    # 安全區域（瀏海）
    var safe_area := DisplayServer.get_display_safe_area()
    $UI.offset_top = safe_area.position.y

func _notification(what: int) -> void:
    if what == NOTIFICATION_WM_GO_BACK_REQUEST:
        if can_go_back():
            go_back()
        else:
            show_quit_dialog()

func vibrate() -> void:
    if OS.has_feature("android"):
        Input.vibrate_handheld(50)
```

### Google Play 要求

- Target API 34+ (Android 14)
- 64-bit (arm64-v8a)
- App Bundle (.aab) 格式
- Release 簽名

---

## iOS 導出

### 設置

1. macOS + Xcode
2. Apple Developer Account ($99/年)
3. 配置 Provisioning Profiles

### iOS 特定代碼

```gdscript
func _ready() -> void:
    if OS.has_feature("ios"):
        configure_for_ios()

func configure_for_ios() -> void:
    apply_safe_area()

func apply_safe_area() -> void:
    var safe_area := DisplayServer.get_display_safe_area()
    var screen_size := DisplayServer.screen_get_size()
    
    $UI.offset_top = safe_area.position.y
    $UI.offset_bottom = -(screen_size.y - safe_area.size.y - safe_area.position.y)
    $UI.offset_left = safe_area.position.x
    $UI.offset_right = -(screen_size.x - safe_area.size.x - safe_area.position.x)

func haptic_feedback() -> void:
    if OS.has_feature("ios"):
        Input.vibrate_handheld(10)
```

---

## 跨平台模式

### 平台檢測

```gdscript
func get_platform() -> String:
    if OS.has_feature("web"):
        return "web"
    elif OS.has_feature("android"):
        return "android"
    elif OS.has_feature("ios"):
        return "ios"
    elif OS.has_feature("windows"):
        return "windows"
    elif OS.has_feature("macos"):
        return "macos"
    elif OS.has_feature("linux"):
        return "linux"
    return "unknown"

func is_mobile() -> bool:
    return OS.has_feature("mobile")

func is_desktop() -> bool:
    return OS.has_feature("pc")

func is_touch_screen() -> bool:
    return DisplayServer.is_touchscreen_available()
```

### 響應式控制

```gdscript
@onready var virtual_joystick: Control = $VirtualJoystick
@onready var touch_buttons: Control = $TouchButtons

func _ready() -> void:
    if is_mobile() or is_touch_screen():
        virtual_joystick.show()
        touch_buttons.show()
    else:
        virtual_joystick.hide()
        touch_buttons.hide()
```

### 存檔路徑

```gdscript
func get_save_path() -> String:
    # 自動選擇正確路徑：
    # Windows: %APPDATA%/godot/app_userdata/GameName/
    # macOS: ~/Library/Application Support/Godot/app_userdata/GameName/
    # Linux: ~/.local/share/godot/app_userdata/GameName/
    # Android: /data/data/com.company.game/files/
    # iOS: Documents 文件夾
    # Web: IndexedDB
    return "user://save_data.json"
```

---

## ⚠️ AI PITFALL：平台特定 API

```gdscript
# ❌ WRONG - 未檢查平台就調用特定 API
Input.vibrate_handheld(50)  # 桌面會失敗

# ✅ CORRECT - 先檢查平台
if OS.has_feature("mobile"):
    Input.vibrate_handheld(50)
```

---

## ⚠️ AI PITFALL：路徑分隔符

```gdscript
# ❌ WRONG - 硬編碼路徑分隔符
var path = "saves\\game.sav"  # Windows 特定

# ✅ CORRECT - 使用 res:// 或 user://
var path = "user://saves/game.sav"  # Godot 會自動處理
```

---

## 導出檢查清單

- [ ] 設置唯一 Bundle ID
- [ ] 配置應用圖標
- [ ] 啟用 VRAM 壓縮（Mobile + Web）
- [ ] 測試觸控控制（Mobile）
- [ ] 處理安全區域（Mobile）
- [ ] 配置權限（Mobile）
- [ ] 設置簽名（Mobile + macOS）
- [ ] 在設備上測試

---

## CLI 導出

```bash
# 導出 Release 版本
godot --path . --export-release "Preset Name" builds/game.exe

# 導出 Debug 版本
godot --path . --export-debug "Preset Name" builds/game_debug.exe

# 無頭模式（CI/CD）
godot --path . --headless --export-release "HTML5" builds/index.html
```
