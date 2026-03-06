---
name: pywayne-lark-bot-listener
description: Feishu/Lark message listener for real-time message processing via WebSocket. Use when users need to listen for incoming Feishu messages (text, image, file, post) with automatic deduplication and async handling. Provides convenient decorators (text_handler, image_handler, file_handler) that handle message download/cleanup and optional automatic reply.
---

# Pywayne Lark Bot Listener

飞书消息监听器，通过 WebSocket 实时接收和处理飞书消息。

## Quick Start

```python
from pywayne.lark_bot_listener import LarkBotListener

# 初始化监听器
listener = LarkBotListener(
    app_id="your_app_id",
    app_secret="your_app_secret",
    message_expiry_time=60  # 消息去重过期时间（秒）
)

# 处理文本消息
@listener.text_handler()
async def handle_text(text: str):
    print(f"收到消息: {text}")

# 启动监听
listener.run()
```

## Decorators - 消息处理装饰器

### text_handler

文本消息处理装饰器，直接传递文本内容。

```python
@listener.text_handler(group_only=False, user_only=False)
async def handle_text(text: str, chat_id: str, is_group: bool, group_name: str, user_name: str):
    print(f"收到来自 {user_name} 的消息: {text}")
    listener.send_message(chat_id, f"已收到：{text}")
```

**参数说明**（除 `text` 外均为可选）：

| 参数 | 类型 | 说明 |
|------|------|------|
| `text` | str | 文本内容（必需） |
| `chat_id` | str | 会话 ID |
| `is_group` | bool | 是否群组消息 |
| `group_name` | str | 群组名称（私聊时为空） |
| `user_name` | str | 发送消息的用户姓名 |

**装饰器参数**：
- `group_only=True`: 只处理群组消息
- `user_only=True`: 只处理私聊消息

### image_handler

图片消息处理装饰器，自动下载图片到临时文件并清理。

```python
from pathlib import Path
import cv2
import tempfile

@listener.image_handler()
async def handle_image(image_path: Path, user_name: str) -> Path:
    # 处理图片
    img = cv2.imread(str(image_path))
    # ...处理逻辑...
    # 返回新图片路径会自动发送回去，返回 None 则不发送
    return image_path
```

**参数说明**（除 `image_path` 外均为可选）：

| 参数 | 类型 | 说明 |
|------|------|------|
| `image_path` | Path | 临时图片文件路径（必需） |
| `chat_id` | str | 会话 ID |
| `is_group` | bool | 是否群组消息 |
| `group_name` | str | 群组名称 |
| `user_name` | str | 发送消息的用户姓名 |

**返回值**：
- 返回 `Path`: 自动上传并发送新图片
- 返回 `None`: 不发送任何图片

### file_handler

文件消息处理装饰器，自动下载文件到临时文件并清理。

```python
@listener.file_handler()
async def handle_file(file_path: Path, user_name: str) -> Path:
    # 处理文件
    with open(file_path, 'r') as f:
        content = f.read()
    # ...处理逻辑...
    return file_path  # 返回文件路径会自动发送回去
```

**参数说明**（除 `file_path` 外均为可选）：

| 参数 | 类型 | 说明 |
|------|------|------|
| `file_path` | Path | 临时文件路径（必需） |
| `chat_id` | str | 会话 ID |
| `is_group` | bool | 是否群组消息 |
| `group_name` | str | 群组名称 |
| `user_name` | str | 发送消息的用户姓名 |

## listen - 通用消息监听器

用于监听任意类型消息（包括富文本 post）。

```python
@listener.listen(message_type="post")
async def handle_post(ctx: MessageContext):
    print(f"收到富文本消息: {ctx.content}")
```

**MessageContext 属性**：

| 属性 | 类型 | 说明 |
|------|------|------|
| `chat_id` | str | 会话 ID |
| `user_id` | str | 用户 ID |
| `message_type` | str | 消息类型 |
| `content` | str | 消息内容（文本消息为字符串，其他类型为 JSON 字符串） |
| `is_group` | bool | 是否群组消息 |
| `chat_type` | str | 会话类型 |
| `message_id` | str | 消息 ID |

## send_message - 发送消息

发送 Markdown 格式的消息到飞书。

```python
listener.send_message(chat_id, "**这是加粗文本**")
listener.send_message(chat_id, "普通文本\n[链接](https://example.com)")
```

## 完整示例

```python
from pywayne.lark_bot_listener import LarkBotListener
from pathlib import Path

listener = LarkBotListener(
    app_id="your_app_id",
    app_secret="your_app_secret"
)

# 文本消息 - AI 回复示例
@listener.text_handler()
async def handle_text(text: str, chat_id: str, user_name: str):
    # 处理逻辑...
    listener.send_message(chat_id, f"收到来自 {user_name} 的消息")

# 图片消息 - 自动下载和清理
@listener.image_handler()
async def handle_image(image_path: Path):
    # image_path 是临时文件，处理完会自动清理
    print(f"处理图片: {image_path}")

# 文件消息 - 自动下载和清理
@listener.file_handler(group_only=True)
async def handle_file(file_path: Path, group_name: str):
    print(f"收到文件: {file_path} 来自 {group_name}")

# 富文本消息
@listener.listen(message_type="post")
async def handle_post(ctx: MessageContext):
    import json
    post_content = json.loads(ctx.content)
    print(f"收到富文本: {post_content}")

# 启动监听
listener.run()
```

## 注意事项

1. **异步处理**: 所有处理函数使用 `async/await` 语法
2. **消息去重**: 每个处理函数独立去重，默认 60 秒过期
3. **临时文件**: 图片和文件下载到 `系统临时目录/lark_bot_temp`，处理完自动清理
4. **错误隔离**: 每个处理函数异常独立捕获，不影响其他函数
5. **多注册**: 同一消息可被多个处理函数处理
