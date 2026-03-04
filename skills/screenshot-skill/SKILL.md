---
name: screenshot-capture
description: Capture screenshots on Windows using mss and Pillow. Provides full-screen, region, and multi-monitor capture with output as PIL Image, PNG file, or base64 string. Use when the user asks to take screenshots, capture screen content, get screen info, or needs screen images for AI vision APIs.
---

# Screenshot Capture

基于 mss + Pillow 的高性能屏幕截图工具，适用于 Windows 桌面自动化、AI 视觉分析等场景。

## 依赖

```bash
uv add mss pillow
# 或
pip install mss pillow
```

## 快速开始

### 作为 Python 模块使用

```python
from scripts.screenshot import ScreenCapture

with ScreenCapture() as sc:
    # 获取屏幕分辨率
    width, height = sc.screen_size

    # 全屏截图 → PIL Image
    img = sc.capture()

    # 截图保存为文件
    sc.capture_to_file("output.png")

    # 截图转 base64 (用于发送给视觉 API)
    b64 = sc.capture_to_base64(quality=85, fmt="JPEG")
```

### 作为 CLI 工具使用

```bash
# 查看显示器信息
python scripts/screenshot.py info

# 截图保存到文件
python scripts/screenshot.py capture -o my_screenshot.png

# 截图输出 base64
python scripts/screenshot.py base64 --format JPEG --quality 85
```

## 核心 API

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `screen_size` | 主显示器 (宽, 高) | `tuple[int, int]` |
| `all_screen_size` | 虚拟全屏 (宽, 高)，多屏合并 | `tuple[int, int]` |
| `monitors` | 所有显示器详细信息 | `list[dict]` |
| `capture(monitor, region, delay)` | 截图 → PIL Image | `Image.Image` |
| `capture_to_file(filepath, ...)` | 截图 → PNG/JPG 文件 | `Path` |
| `capture_to_base64(quality, fmt, ...)` | 截图 → base64 字符串 | `str` |

## 常见场景

### 发送截图给 OpenAI 视觉 API

```python
from openai import OpenAI
from scripts.screenshot import ScreenCapture

client = OpenAI()
with ScreenCapture() as sc:
    b64 = sc.capture_to_base64(fmt="JPEG", quality=85)

resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "描述截图内容"},
            {"type": "image_url", "image_url": {
                "url": f"data:image/jpeg;base64,{b64}",
                "detail": "high",
            }},
        ],
    }],
)
```

### 截取指定区域

```python
with ScreenCapture() as sc:
    region = {"left": 100, "top": 200, "width": 800, "height": 600}
    img = sc.capture(region=region)
    img.save("region.png")
```

### 自动保存每步截图

```python
with ScreenCapture(save_dir="screenshots") as sc:
    for i in range(5):
        sc.capture_to_base64(step=i)  # 自动保存为 screenshots/step_000.jpg 等
```

## 详细参考

完整 API 参数说明见 [reference.md](reference.md)。
