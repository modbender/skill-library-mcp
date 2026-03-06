# 10 - 測試指南

## GDUnit4 設置

### 安裝

1. AssetLib > 搜索 "GDUnit4" > 下載 > 安裝
2. Project > Project Settings > Plugins > 啟用 "GDUnit4"

### 項目結構

```
project/
├── addons/
│   └── gdunit4/
└── test/              # 所有測試在這裡
    ├── player/
    │   └── test_player.gd
    └── enemies/
        └── test_enemy.gd
```

---

## 基本測試結構

```gdscript
# test/player/test_player.gd
extends GdUnitTestSuite

# 每個測試前調用
func before_test() -> void:
    pass

# 每個測試後調用
func after_test() -> void:
    pass

# 所有測試前調用一次
func before() -> void:
    pass

# 所有測試後調用一次
func after() -> void:
    pass

# 測試方法必須以 "test_" 開頭
func test_example() -> void:
    assert_bool(true).is_true()
```

---

## 斷言

### 布林

```gdscript
assert_bool(true).is_true()
assert_bool(false).is_false()
```

### 數值

```gdscript
assert_int(42).is_equal(42)
assert_int(10).is_greater(5)
assert_int(5).is_less(10)
assert_int(7).is_between(5, 10)

assert_float(3.14).is_equal_approx(3.14159, 0.01)
```

### 字串

```gdscript
assert_str("hello").is_equal("hello")
assert_str("hello world").contains("world")
assert_str("hello").starts_with("he")
assert_str("hello").ends_with("lo")
assert_str("hello").has_length(5)
assert_str("").is_empty()
```

### 陣列

```gdscript
var arr := [1, 2, 3]

assert_array(arr).has_size(3)
assert_array(arr).contains([1, 2])
assert_array(arr).contains_exactly([1, 2, 3])
assert_array(arr).not_contains([4, 5])
assert_array([]).is_empty()
```

### 物件

```gdscript
var player := Player.new()

assert_object(player).is_not_null()
assert_object(player).is_instanceof(Player)
assert_object(null).is_null()
```

### 向量

```gdscript
var v := Vector2(3, 4)

assert_vector(v).is_equal(Vector2(3, 4))
assert_vector(v).is_equal_approx(Vector2(3.01, 4.01), 0.1)
```

---

## 場景測試

```gdscript
extends GdUnitTestSuite

var player: Player

func before_test() -> void:
    # auto_free 確保測試後清理
    player = auto_free(preload("res://scenes/player/player.tscn").instantiate())
    add_child(player)

func test_player_initial_state() -> void:
    assert_int(player.health).is_equal(100)
    assert_bool(player.is_alive).is_true()

func test_player_take_damage() -> void:
    player.take_damage(25)
    assert_int(player.health).is_equal(75)
```

---

## 信號測試

```gdscript
func test_signal_emitted() -> void:
    var player := auto_free(Player.new())
    
    # 創建信號收集器
    var collector := signal_collector(player, "died")
    
    # 觸發信號
    player.health = 0
    player.check_death()
    
    # 斷言信號被發射
    await assert_signal(collector).is_emitted("died")

func test_signal_with_args() -> void:
    var player := auto_free(Player.new())
    var collector := signal_collector(player, "health_changed")
    
    player.take_damage(25)
    
    # 斷言信號帶特定參數
    await assert_signal(collector).is_emitted("health_changed", [75, 100])

func test_signal_not_emitted() -> void:
    var player := auto_free(Player.new())
    var collector := signal_collector(player, "died")
    
    player.take_damage(10)  # 不足以死亡
    
    await assert_signal(collector).is_not_emitted("died")
```

---

## Mock 和 Spy

```gdscript
# Mock 物件
func test_with_mock() -> void:
    var enemy_mock := mock(Enemy) as Enemy
    
    # 定義 mock 行為
    do_return(50).on(enemy_mock).get_damage()
    
    # 使用 mock
    var damage := enemy_mock.get_damage()
    assert_int(damage).is_equal(50)
    
    # 驗證方法被調用
    verify(enemy_mock).get_damage()

# Spy 物件
func test_with_spy() -> void:
    var player := auto_free(Player.new())
    var player_spy := spy(player)
    
    player_spy.take_damage(25)
    
    # 驗證方法被調用
    verify(player_spy).take_damage(25)
    verify(player_spy, 1).take_damage(any_int())
```

---

## 異步測試

```gdscript
# 等待幀
func test_async_behavior() -> void:
    var player := auto_free(Player.new())
    add_child(player)
    
    player.start_jump()
    
    await await_idle_frame()
    await await_idle_frame()
    
    assert_bool(player.is_jumping).is_true()

# 等待時間
func test_timed_behavior() -> void:
    var bomb := auto_free(Bomb.new())
    add_child(bomb)
    
    bomb.start_countdown()
    
    await await_millis(2100)
    
    assert_bool(bomb.has_exploded).is_true()

# 帶超時的信號等待
func test_signal_with_timeout() -> void:
    var player := auto_free(Player.new())
    var collector := signal_collector(player, "animation_finished")
    
    player.play_attack()
    
    await assert_signal(collector).wait_until(5000).is_emitted("animation_finished")
```

---

## 參數化測試

```gdscript
func test_damage_calculation(
    base_damage: int,
    multiplier: float,
    expected: int,
    test_parameters := [
        [10, 1.0, 10],
        [10, 1.5, 15],
        [10, 2.0, 20],
        [25, 1.0, 25],
        [25, 2.0, 50],
    ]
) -> void:
    var result := calculate_damage(base_damage, multiplier)
    assert_int(result).is_equal(expected)
```

---

## 跳過測試

```gdscript
func test_mobile_only() -> void:
    if not OS.has_feature("mobile"):
        skip("This test requires mobile platform")
        return
    # ... 測試代碼
```

---

## 運行測試

### 從編輯器

1. GDUnit 面板：底部面板 > GDUnit
2. 運行全部：點擊 "Run All Tests"
3. 運行單個：右鍵測試方法 > Run

### 從命令行

```bash
# 運行所有測試
godot --headless -s addons/gdunit4/bin/GdUnitCmdTool.gd --add test/

# 運行特定文件
godot --headless -s addons/gdunit4/bin/GdUnitCmdTool.gd --add test/player/test_player.gd

# 詳細輸出
godot --headless -s addons/gdunit4/bin/GdUnitCmdTool.gd --add test/ -v
```

### CI/CD 整合

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    container:
      image: barichello/godot-ci:4.2

    steps:
      - uses: actions/checkout@v4

      - name: Run tests
        run: |
          godot --headless -s addons/gdunit4/bin/GdUnitCmdTool.gd \
            --add test/ \
            --report-directory reports/

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: reports/
```

---

## 最佳實踐

### 命名

```gdscript
# ✅ Good - 描述性名稱
func test_player_dies_when_health_reaches_zero() -> void:
func test_enemy_attacks_when_player_in_range() -> void:

# ❌ Bad - 模糊名稱
func test_player() -> void:
func test_1() -> void:
```

### AAA 模式

```gdscript
func test_player_takes_damage() -> void:
    # Arrange
    var player := auto_free(Player.new())
    player.health = 100
    
    # Act
    player.take_damage(25)
    
    # Assert
    assert_int(player.health).is_equal(75)
```

### 測試隔離

```gdscript
# 每個測試應該獨立
func before_test() -> void:
    player = auto_free(Player.new())
    player.reset()  # 每個測試都是新的狀態
```

---

## ⚠️ AI PITFALL：忘記 auto_free() 造成記憶體洩漏

```gdscript
# ❌ WRONG - 節點沒有自動清理
func test_player_health() -> void:
    var player := Player.new()  # 測試結束後不會被清理！
    add_child(player)
    assert_int(player.health).is_equal(100)

# ✅ CORRECT - 使用 auto_free 確保清理
func test_player_health() -> void:
    var player := auto_free(Player.new())
    add_child(player)
    assert_int(player.health).is_equal(100)
```

---

## ⚠️ AI PITFALL：異步斷言忘記 await

```gdscript
# ❌ WRONG - 沒有 await，信號斷言不會等待
func test_signal_emitted() -> void:
    var player := auto_free(Player.new())
    var collector := signal_collector(player, "died")
    player.take_damage(100)
    
    assert_signal(collector).is_emitted("died")  # 不等待！永遠失敗

# ✅ CORRECT - 使用 await 等待信號
func test_signal_emitted() -> void:
    var player := auto_free(Player.new())
    var collector := signal_collector(player, "died")
    player.take_damage(100)
    
    await assert_signal(collector).is_emitted("died")  # 正確等待
```

---

## ⚠️ AI PITFALL：測試 GDScript 內部實作細節

```gdscript
# ❌ WRONG - 測試私有實作細節
func test_internal_timer() -> void:
    var player := auto_free(Player.new())
    # 依賴內部計時器實作，重構後就會壞
    assert_float(player._attack_cooldown_timer).is_equal(0.5)

# ✅ CORRECT - 測試可觀察的行為
func test_cannot_attack_during_cooldown() -> void:
    var player := auto_free(Player.new())
    add_child(player)
    player.attack()
    # 測試外部行為而非內部狀態
    assert_bool(player.can_attack()).is_false()
```
