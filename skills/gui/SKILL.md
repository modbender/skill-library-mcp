---
name: pywayne-gui
description: Windows GUI automation toolkit for global hotkeys and window management. Use when users need to register global hotkeys, find/control windows, automate GUI operations, or perform Windows desktop automation. Requires Windows OS with pywin32, pyuserinput, and pyautogui dependencies.
---

# Pywayne Gui

Windows 图形用户界面自动化工具，提供全局热键监听和窗口操作功能。

## Quick Start

```python
from pywayne.gui import GlobalHotKeys, GuiOperation

# 全局热键
g = GlobalHotKeys()

@g.register(GlobalHotKeys.VK_F1, GlobalHotKeys.MOD_SHIFT)
def shift_f1():
    print('Shift+F1 被按下')

# 启动监听（按 Q 或 Ctrl+C 退出）
GlobalHotKeys.listen()
```

## Dependencies

| 包 | 用途 | 安装命令 |
|------|------|----------|
| pywin32 | Windows API 封装 | `pip install pywin32` |
| pyuserinput | 键盘鼠标输入 | `pip install pyuserinput` |
| pyautogui | GUI 自动化 | `pip install pyautogui` |

## GlobalHotKeys - 全局热键

注册全局热键，在全局范围内监听键盘事件。

### 注册热键

```python
from pywayne.gui import GlobalHotKeys

g = GlobalHotKeys()

# 装饰器方式注册
@g.register(GlobalHotKeys.VK_F1, GlobalHotKeys.MOD_SHIFT)
def shift_f1():
    print('Shift+F1')

# 组合键修饰符（支持组合使用）
g.register(GlobalHotKeys.VK_F1, GlobalHotKeys.MOD_CTRL | GlobalHotKeys.MOD_SHIFT)

# 直接调用 register 方法
def handler():
    print('Ctrl+A 被按下')
GlobalHotKeys.register(GlobalHotKeys.VK_A, GlobalHotKeys.MOD_CTRL, handler)
```

### 启动监听

```python
# 启动消息循环，开始监听热键
GlobalHotKeys.listen()
```

### 停止条件

按以下任意组合键会停止监听循环：
- `Q` 键
- `Ctrl + C`

### 虚拟键码

**常用虚拟键码**（`VK_*`）：

| 按键 | 键码 | 组合键 |
|------|------|--------|
| A-Z | `VK_A` 到 `VK_Z` | `ord('A')` 到 `ord('Z')` |
| 0-9 | `VK_0` 到 `VK_9` | `ord('0')` 到 `ord('9')` |
| F1-F12 | `VK_F1` 到 `VK_F12` | - |

**修饰键**（`MOD_*`）：

| 修饰键 | 常量 |
|------|------|
| Alt | `MOD_ALT` |
| Ctrl | `MOD_CTRL` |
| Shift | `MOD_SHIFT` |
| Win | `MOD_WIN` |

修饰键可使用 `|` 组合，如 `MOD_CTRL | MOD_SHIFT`。

## GuiOperation - 窗口操作

提供 Windows 窗口查找、控制和操作功能。

### 初始化

```python
from pywayne.gui import GuiOperation

gui = GuiOperation()
```

### find_window

查找包含指定关键字的窗口，返回窗口句柄列表。

```python
# 查找包含"记事本"的窗口
notepad_handles = gui.find_window('记事本')

# 查找包含"微信"的窗口
wechat_handles = gui.find_window('微信')

# 多关键字匹配
handles = gui.find_window('Visual', 'Studio')
```

**参数说明**：
- `*keys`: 按关键字匹配窗口标题

**返回值**：
- 匹配的窗口句柄列表（`hwnd`）
- 未找到时返回空列表

### get_windows_attr

获取指定窗口的属性信息。

```python
hwnd = gui.find_window('记事本')[0]
title, class_name = gui.get_windows_attr(hwnd)
print(f"窗口标题: {title}")
print(f"窗口类名: {class_name}")
```

**返回值**：
- 找到窗口：`(窗口标题, 窗口类名)`
- 窗口不存在：`('', '')`

### maximize_window

将指定窗口最大化。

```python
hwnd = gui.find_window('记事本')[0]
gui.maximize_window(hwnd)
```

### bring_to_top

将指定窗口置于顶层。

```python
hwnd = gui.find_window('记事本')[0]
gui.bring_to_top(hwnd)
```

### close_window

关闭指定窗口。

```python
hwnd = gui.find_window('记事本')[0]
gui.close_window(hwnd)
```

### change_window_name

修改指定窗口的标题。

```python
hwnd = gui.find_window('记事本')[0]
gui.change_window_name(hwnd, '新标题')
```

### get_window_rect

获取窗口的矩形坐标。

```python
hwnd = gui.find_window('记事本')[0]
rect = gui.get_window_rect(hwnd)
print(f"窗口位置: {rect}")
```

**返回值**：`(left, top, right, bottom)`

### get_child_windows

获取指定窗口的子窗口列表。

```python
hwnd = gui.find_window('记事本')[0]
children = gui.get_child_windows(hwnd)
print(f"子窗口数量: {len(children)}")
```

## 使用示例

### 示例 1：热键自动化

```python
from pywayne.gui import GlobalHotKeys

g = GlobalHotKeys()

@g.register(GlobalHotKeys.VK_F10, GlobalHotKeys.MOD_SHIFT)
def screenshot_hotkey():
    print('截图热键被触发')
    # 执行截图逻辑...

@g.register(GlobalHotKeys.VK_Q, GlobalHotKeys.MOD_CTRL)
def copy_hotkey():
    print('复制热键被触发')
    # 执行复制逻辑...

GlobalHotKeys.listen()
```

### 示例 2：窗口自动化

```python
from pywayne.gui import GuiOperation
import time

gui = GuiOperation()

# 查找记事本窗口
notepad = gui.find_window('记事本')
if notepad:
    print('未找到记事本')
    exit()

# 置顶并最大化
gui.bring_to_top(notepad[0])
time.sleep(0.5)
gui.maximize_window(notepad[0])

# 修改窗口标题
gui.change_window_name(notepad[0], '自动化控制中...')
```

### 示例 3：综合自动化

```python
from pywayne.gui import GuiOperation, GlobalHotKeys
from pywayne.gui import PyMouse, PyKeyboard

gui = GuiOperation()
g = GlobalHotKeys()

@g.register(GlobalHotKeys.VK_F1, GlobalHotKeys.MOD_SHIFT)
def auto_test():
    # 查找测试软件窗口
    st_window = gui.find_window('ST测试软件')
    if not st_window:
        return

    st_hwnd = st_window[0]
    gui.bring_to_top(st_hwnd)

    # 获取子窗口
    for child in gui.get_child_windows(st_hwnd):
        title, cls = gui.get_windows_attr(child)
        print(f'子窗口: {title}')

    # 操作完成后关闭
    gui.close_window(st_hwnd)

GlobalHotKeys.listen()
```

## 注意事项

1. **平台限制**: 本模块仅支持 Windows 系统
2. **依赖安装**: 使用前需确保已安装 pywin32、pyuserinput、pyautogui
3. **管理员权限**: 某些操作可能需要管理员权限
4. **窗口状态**: 查找和操作仅对可见且启用的窗口有效
5. **热键冲突**: 注册的热键可能与其他软件冲突
