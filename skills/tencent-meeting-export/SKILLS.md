# 腾讯会议录制转写导出工具

从腾讯会议**公开分享链接**中导出完整的会议转写内容。

## 导出内容

| 内容 | 说明 |
|------|------|
| AI 全文摘要 | 腾讯会议自动生成的会议摘要 |
| 智能章节 | 按主题自动分段，附时间戳和概要 |
| 关键节点 | 屏幕共享开始/停止、成员加入/离开等事件 |
| 完整转写 | 逐段语音转文字，含说话人识别和时间戳 |

## 前置要求

```bash
pip install playwright
playwright install chromium
```

## 使用方法

### 基本用法

```bash
python scripts/tencent_meeting_export.py <分享链接>
```

### 指定输出文件

```bash
python scripts/tencent_meeting_export.py https://meeting.tencent.com/cw/xxxxx -o 会议纪要.md
```

### 导出原始 JSON 数据

```bash
# 同时导出 Markdown + JSON
python scripts/tencent_meeting_export.py https://meeting.tencent.com/cw/xxxxx --json

# 仅导出 JSON（不生成 Markdown）
python scripts/tencent_meeting_export.py https://meeting.tencent.com/cw/xxxxx --json-only -o raw.json
```

### 完整参数

```
positional arguments:
  url                   腾讯会议分享链接

optional arguments:
  -o, --output          输出文件路径 (默认: meeting_transcript.md)
  --json                同时导出原始 JSON 数据
  --json-only           仅导出原始 JSON 数据
  --timeout             页面加载超时时间（秒，默认 60）
  -q, --quiet           静默模式
```

## 技术原理

1. 使用 Playwright 无头 Chromium 浏览器加载分享页面
2. 拦截页面向后端发起的 API 请求响应：
   - `v1/minutes/detail` — 转写段落（懒加载分页）
   - `get-full-summary` — AI 摘要
   - `get-chapter` — 智能章节
   - `get-critical-node` — 关键事件节点
   - `common-record-info` — 会议元信息
3. 自动点击「转写」标签页并滚动加载全部内容
4. 将数据格式化为 Markdown（或 JSON）输出

## 数据结构

转写段落 (paragraph) 的关键字段：

```
paragraph
├── start_time / end_time  (毫秒时间戳)
├── speaker
│   ├── user_id
│   ├── user_name           ← 说话人姓名
│   └── avatar_url
└── sentences[]
    └── words[]
        └── text             ← 转写文字
```

## 限制

- 仅支持**公开分享**的会议录制链接（无需登录）
- 需要该会议已开启转写/字幕功能
- 分享链接需在有效期内
- 依赖腾讯会议当前的页面结构和 API，如有变更可能需要更新脚本

## 编程接口

也可在 Python 代码中直接调用：

```python
import asyncio
from scripts.tencent_meeting_export import TranscriptCapture, format_markdown

async def export():
    capture = TranscriptCapture("https://meeting.tencent.com/cw/xxxxx")
    data = await capture.capture()
    md = format_markdown(data)
    print(md)

asyncio.run(export())
```
