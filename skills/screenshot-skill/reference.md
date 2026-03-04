# Screenshot Capture — 完整 API 参考

## 类: `ScreenCapture`

### 构造函数

```python
ScreenCapture(save_dir: str | None = None)
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `save_dir` | `str \| None` | `None` | 自动保存截图的目录路径。设置后 `capture_to_base64` 会同时保存文件。目录不存在会自动创建。 |

支持上下文管理器：

```python
with ScreenCapture(save_dir="shots") as sc:
    ...
# 退出时自动调用 sc.close()
```

---

### 属性

#### `screen_size -> tuple[int, int]`

返回**主显示器**的 `(宽, 高)` 像素值。

```python
w, h = sc.screen_size  # e.g. (1920, 1080)
```

#### `all_screen_size -> tuple[int, int]`

返回**虚拟全屏**的 `(宽, 高)`。多显示器时是所有屏幕合并后的尺寸。

```python
w, h = sc.all_screen_size  # e.g. (3840, 1080) 双屏
```

#### `monitors -> list[dict]`

返回所有显示器的详细信息列表。

- 索引 `0`: 虚拟全屏 (所有屏幕合并)
- 索引 `1`: 主显示器
- 索引 `2+`: 其他显示器

每个 dict 包含: `left`, `top`, `width`, `height`

---

### 方法

#### `capture(...) -> Image.Image`

截取屏幕内容，返回 PIL Image 对象。

```python
capture(
    monitor: int = 1,
    region: dict | None = None,
    delay: float = 0.0,
) -> Image.Image
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `monitor` | `int` | `1` | 显示器编号。`0`=所有屏幕合并, `1`=主显示器 |
| `region` | `dict \| None` | `None` | 自定义截取区域，格式: `{"left": x, "top": y, "width": w, "height": h}`。设置后 `monitor` 被忽略 |
| `delay` | `float` | `0.0` | 截图前等待的秒数 |

---

#### `capture_to_file(...) -> Path`

截图并保存为图片文件。

```python
capture_to_file(
    filepath: str | Path = "screenshot.png",
    monitor: int = 1,
    region: dict | None = None,
    delay: float = 0.0,
) -> Path
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `filepath` | `str \| Path` | `"screenshot.png"` | 输出文件路径，格式由扩展名决定 (`.png`, `.jpg` 等) |
| 其他参数 | — | — | 同 `capture()` |

返回实际保存的 `Path` 对象。

---

#### `capture_to_base64(...) -> str`

截图并返回 base64 编码的字符串，适合直接嵌入 API 请求。

```python
capture_to_base64(
    monitor: int = 1,
    region: dict | None = None,
    delay: float = 0.0,
    quality: int = 85,
    fmt: str = "JPEG",
    step: int = 0,
) -> str
```

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `quality` | `int` | `85` | JPEG 压缩质量 (1-100)，仅 `fmt="JPEG"` 时生效 |
| `fmt` | `str` | `"JPEG"` | 编码格式: `"JPEG"` 或 `"PNG"` |
| `step` | `int` | `0` | 步骤编号，用于 `save_dir` 自动保存时的文件命名 (`step_000.jpg`) |
| 其他参数 | — | — | 同 `capture()` |

**Tips**: JPEG 体积小速度快，适合发送给 API；PNG 无损但体积大。

---

#### `close()`

释放 mss 资源。使用 `with` 语句时自动调用。

---

## CLI 命令

脚本可直接作为命令行工具运行:

```bash
python scripts/screenshot.py <command> [options]
```

### `info`

输出所有显示器信息（JSON 格式）。

```bash
python scripts/screenshot.py info
```

输出示例:

```json
{
  "monitors": [
    {"left": 0, "top": 0, "width": 3840, "height": 1080},
    {"left": 0, "top": 0, "width": 1920, "height": 1080},
    {"left": 1920, "top": 0, "width": 1920, "height": 1080}
  ],
  "primary_size": [1920, 1080],
  "virtual_size": [3840, 1080]
}
```

### `capture`

截图并保存到文件。

```bash
python scripts/screenshot.py capture [options]
```

| 选项 | 默认 | 说明 |
|------|------|------|
| `-o, --output` | `screenshot.png` | 输出文件路径 |
| `-m, --monitor` | `1` | 显示器编号 |
| `-d, --delay` | `0.0` | 截图前延迟(秒) |
| `--region` | — | JSON 格式的区域: `'{"left":0,"top":0,"width":800,"height":600}'` |

### `base64`

截图并输出 base64 字符串到 stdout。

```bash
python scripts/screenshot.py base64 [options]
```

| 选项 | 默认 | 说明 |
|------|------|------|
| `-m, --monitor` | `1` | 显示器编号 |
| `-d, --delay` | `0.0` | 截图前延迟(秒) |
| `-q, --quality` | `85` | JPEG 质量 |
| `-f, --format` | `JPEG` | 输出格式: `JPEG` 或 `PNG` |

---

## 性能说明

- mss 使用操作系统原生 API 截图，比 Pillow 的 `ImageGrab` 快 **2-5 倍**
- 典型截图耗时: 1920×1080 约 **15-30ms**
- JPEG base64 输出大小: 约 **100-300KB** (quality=85)
- PNG base64 输出大小: 约 **1-3MB**
