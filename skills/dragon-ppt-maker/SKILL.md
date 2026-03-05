# ppt-maker

使用 python-pptx 制作精美PPT，支持科技风设计、图文混排、HTML内容嵌入。

## 功能

- 🎨 科技风UI设计
- 📊 多种布局：标题页、内容页、特性网格、对比页
- 🖼️ 支持插入图片
- 🔗 支持HTML内容（通过截图或链接）

## 安装依赖

```bash
pip install python-pptx pillow
```

## 使用方法

### 命令行

```bash
python ppt_maker.py --title "演示标题" --content "内容1|内容2|内容3" --output demo.pptx
```

### Python API

```python
from ppt_maker import PresentationBuilder

builder = PresentationBuilder()
builder.add_title_slide("标题", "副标题")
builder.add_content_slide("章节标题", ["要点1", "要点2", "要点3"])
builder.add_feature_grid([("特性1", "描述1"), ("特性2", "描述2")])
builder.save("output.pptx")
```

## 示例：OpenClaw 介绍

```python
from ppt_maker import PresentationBuilder, Theme

prs = PresentationBuilder(theme=Theme.TECH)

# 封面
prs.add_title_slide("OpenClaw", "您的跨平台AI个人助理")

# 内容页
prs.add_content_slide("什么是 OpenClaw?", [
    "开源免费的自托管 AI 网关",
    "连接 WhatsApp、Telegram、Discord 等多平台",
    "数据完全掌控在自己手中"
], icon="🤖")

# 特性网格
prs.add_feature_grid([
    ("多通道网关", "一个 Gateway 同时连接多个平台"),
    ("插件扩展", "支持 Mattermost 等更多插件"),
    ("多 Agent 路由", "隔离的会话空间"),
    ("移动节点", "配对 iOS/Android 设备")
])

# 保存
prs.save("OpenClaw介绍.pptx")
```

## 主题

- `Theme.TECH` - 科技风（深蓝+青色）
- `Theme.MODERN` - 现代简约（黑白灰）
- `Theme.CORPORATE` - 企业风格（蓝+白）
