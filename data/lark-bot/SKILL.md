---
name: pywayne-lark-bot
description: Feishu/Lark Bot API wrapper for full-featured Feishu bot interactions. Use when users need to send messages (text, image, audio, file, post, interactive, share), especially Markdown delivery via send_markdown_to_chat with card_v2/post routing, table fallback, and auto chunking; manage files (upload/download); query user/group info; or listen for incoming messages with LarkBotListener.
---

# Pywayne Lark Bot

飞书机器人模块，提供完整飞书 API 交互功能，包括消息发送、文件管理、用户/群组查询和消息监听。

## Quick Start

```python
from pywayne.lark_bot import LarkBot, TextContent

# 初始化
bot = LarkBot(app_id="your_app_id", app_secret="your_app_secret")

# 发送文本消息到用户
bot.send_text_to_user(user_open_id="user_xxx", text="Hello!")

# 发送文本消息到群聊
bot.send_text_to_chat(chat_id="oc_xxx", text="Group message")
```

## TextContent - 文本格式化工具

创建各种文本格式，用于发送带格式的文本消息。

### Mentions

```python
# @所有人
at_all = TextContent.make_at_all_pattern()

# @指定用户
at_user = TextContent.make_at_someone_pattern(user_open_id="user_xxx", username="张三", id_type="open_id")
```

### Text Styles

```python
# 加粗、斜体、下划线、删除线
bold = TextContent.make_bold_pattern("粗体")
italic = TextContent.make_italian_pattern("斜体")
underline = TextContent.make_underline_pattern("下划线")
strikethrough = TextContent.make_delete_line_pattern("删除线")

# 超链接
link = TextContent.make_url_pattern("https://example.com", "点击访问")
```

## LarkBot - 消息发送与查询

### 推荐路径：发送 Markdown（优先使用）

优先使用 `send_markdown_to_chat`，它会自动处理大文本分包，并支持两种路由：

- `prefer="card_v2"`（默认）：发送 schema 2.0 interactive 卡片，适合绝大多数 Markdown 场景
- `prefer="post"`：发送 post 富文本；可设置 `table_fallback="code_block"` 将 Markdown 表格稳定降级

```python
md = """
# 发布说明

- 新增对账接口
- 修复支付重试逻辑

| 模块 | 状态 |
| --- | --- |
| API | 完成 |
| FE  | 测试中 |
"""

# 默认走 card_v2（推荐）
bot.send_markdown_to_chat(
    chat_id="oc_xxx",
    md_text=md,
    title="版本进度",
    prefer="card_v2"
)

# 需要 post 时切换路由
bot.send_markdown_to_chat(
    chat_id="oc_xxx",
    md_text=md,
    title="版本进度",
    prefer="post",
    table_fallback="code_block"
)
```

### 发送消息

#### Text Message

```python
bot.send_text_to_user(user_open_id, "私聊消息")
bot.send_text_to_chat(chat_id, "群聊消息")
```

#### Image Message

```python
# 上传图片
image_key = bot.upload_image("/path/to/image.jpg")

# 发送图片
bot.send_image_to_user(user_open_id, image_key)
bot.send_image_to_chat(chat_id, image_key)
```

#### Audio / Media / File Message

```python
# 上传文件
file_key = bot.upload_file("/path/to/file.pdf", file_type="pdf")

# 发送音频
bot.send_audio_to_user(user_open_id, file_key)

# 发送多媒体
bot.send_media_to_chat(chat_id, file_key)

# 发送文件
bot.send_file_to_user(user_open_id, file_key)
```

#### Post (Rich Text) Message

```python
from pywayne.lark_bot import PostContent

post = PostContent(title="富文本标题")

# 添加内容
line = post.make_text_content("这是粗体文本", styles=["bold"])
post.add_content_in_new_line(line)

# 发送
bot.send_post_to_user(user_open_id, post.get_content())
bot.send_post_to_chat(chat_id, post.get_content())
```

#### Interactive Card Message

```python
# 直接传原始 interactive 卡片
card = {
    "header": {"title": {"content": "卡片标题", "tag": "plain_text"}},
    "elements": [...]
}
bot.send_interactive_to_user(user_open_id, card)
bot.send_interactive_to_chat(chat_id, card)
```

#### CardContentV2（schema 2.0 卡片构造器）

```python
from pywayne.lark_bot import CardContentV2

card = CardContentV2(title="日报", template="blue")
card.add_markdown("# 今日进展\n\n- 完成接口联调\n- 修复2个问题")
card.add_hr()
card.add_image(img_key="img_xxx")

bot.send_interactive_to_chat(chat_id, card.get_card())
```

#### Share Message

```python
# 分享群聊
bot.send_shared_chat_to_user(user_open_id, shared_chat_id)
bot.send_shared_chat_to_chat(chat_id, shared_chat_id)

# 分享用户
bot.send_shared_user_to_user(user_open_id, shared_user_id)
bot.send_shared_user_to_chat(chat_id, shared_user_id)
```

### PostContent - 富文本构建器

```python
post = PostContent(title="标题")

# 可用内容类型
text = post.make_text_content("文本", styles=["bold", "underline"])
link = post.make_link_content("链接文字", "https://example.com")
at = post.make_at_content(user_open_id)
img = post.make_image_content(image_key="img_xxx")
media = post.make_media_content(file_key="file_xxx", image_key="thumb_xxx")
emoji = post.make_emoji_content(emoji_type="OK")
hr = post.make_hr_content()
code_block = post.make_code_block_content(language="python", text="print('hello')")
markdown = post.make_markdown_content("**Markdown**")

# 添加内容
post.add_content_in_new_line(text)
post.add_contents_in_line([link, at])  # 同一行添加多个元素
```

```python
# 推荐：直接添加 markdown，支持分块与表格降级
md = """
## 迭代计划
| 任务 | 状态 |
| --- | --- |
| A   | done |
| B   | doing |
"""
post.add_markdown(md, table_as="code_block", max_chunk_bytes=8000)
```

### 文件操作

```python
# 上传
image_key = bot.upload_image("/path/to/image.jpg")
file_key = bot.upload_file("/path/to/file.pdf", file_type="pdf")

# 下载
bot.download_image(image_key, "/save/path/image.jpg")
bot.download_file(file_key, "/save/path/file.pdf")

# 下载消息中的所有资源
resources = bot.download_message_resources(
    message_id="msg_xxx",
    message_content='{"image_key":"img_xxx"}',
    save_dir="/save/dir"
)
```

### 用户与群组查询

```python
# 获取用户信息
users = bot.get_user_info(emails=["test@example.com"], mobiles=["13800138000"])

# 获取群组列表
groups = bot.get_group_list()

# 通过群名获取群ID
chat_ids = bot.get_group_chat_id_by_name("项目讨论组")

# 获取群成员
members = bot.get_members_in_group_by_group_chat_id(chat_id)

# 通过群成员名获取 open_id
member_ids = bot.get_member_open_id_by_name(chat_id, "张三")

# 获取群名和用户名
chat_name, user_name = bot.get_chat_and_user_name(chat_id, user_id)
```

## LarkBotListener - 消息监听

飞书消息监听器，用于实时接收和处理消息。

```python
from pywayne.lark_bot_listener import LarkBotListener
from pathlib import Path

listener = LarkBotListener(
    app_id="your_app_id",
    app_secret="your_app_secret"
)
```

### 文本消息处理

```python
@listener.text_handler(group_only=False, user_only=False)
async def handle_text(text: str, chat_id: str, is_group: bool, group_name: str, user_name: str):
    print(f"收到来自 {user_name} 的消息: {text}")
    # 回复
    listener.send_message(chat_id, f"已收到：{text}")
```

### 图片消息处理

```python
@listener.image_handler(group_only=True)
async def handle_image(image_path: Path, chat_id: str, user_name: str):
    print(f"收到图片: {image_path}")
    # 处理图片...
```

### 文件消息处理

```python
@listener.file_handler()
async def handle_file(file_path: Path, chat_id: str, user_name: str):
    print(f"收到文件: {file_path}")
    # 处理文件...
```

### 通用消息监听

```python
@listener.listen(message_type="post")
async def handle_post(ctx):
    print(f"收到富文本消息: {ctx.content}")
```

### 启动监听

```python
listener.run()
```

### 监听器参数说明

**Handler 参数**（除必需参数外均为可选）：

| Handler | 必需参数 | 可选参数 |
|---------|-----------|----------|
| `text_handler` | `text` | `chat_id`, `is_group`, `group_name`, `user_name` |
| `image_handler` | `image_path` | `chat_id`, `is_group`, `group_name`, `user_name` |
| `file_handler` | `file_path` | `chat_id`, `is_group`, `group_name`, `user_name` |

**装饰器参数**：

- `message_type`: 消息类型（"text", "image", "file", "post"）
- `group_only=True`: 只监听群组消息
- `user_only=True`: 只监听私聊消息

### 注意事项

1. 所有处理函数使用 `async/await` 语法
2. 消息会去重（默认 60 秒）
3. 图片和文件下载到临时目录，处理完及时清理
4. 每个处理函数异常独立捕获，不影响其他函数
