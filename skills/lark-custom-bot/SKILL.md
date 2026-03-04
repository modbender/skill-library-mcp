---
name: pywayne-lark-custom-bot
description: Feishu/Lark Custom Bot API wrapper for sending messages to Feishu channels via webhook. Use when users need to send text messages, images, rich text posts, interactive cards, or share chat content to Feishu/Lark. Supports image upload from files or OpenCV images, signature verification for security, and @mention functionality.
---

# Pywayne Lark Custom Bot

飞书自定义机器人模块，用于通过 webhook 向飞书渠道发送消息。

## Quick Start

```python
from pywayne.lark_custom_bot import LarkCustomBot

# 初始化
bot = LarkCustomBot(
    webhook="your_webhook_url",
    secret="your_secret",  # 可选，用于签名验证
    bot_app_id="your_app_id",  # 上传图片时需要
    bot_secret="your_app_secret"  # 上传图片时需要
)

# 发送文本
bot.send_text("Hello, 飞书!")

# 发送文本并 @所有人
bot.send_text("重要通知！", mention_all=True)
```

## Message Types

### Text Message

发送纯文本消息。

```python
bot.send_text("这是一条文本消息")
bot.send_text("@所有人请注意", mention_all=True)
```

### Image Message

发送图片消息，需要先上传获取 `image_key`。

```python
# 从文件上传
image_key = bot.upload_image("/path/to/image.jpg")
bot.send_image(image_key)

# 从 OpenCV 图像上传
import cv2
cv2_img = cv2.imread("/path/to/image.jpg")
image_key = bot.upload_image_from_cv2(cv2_img)
bot.send_image(image_key)
```

**注意**: 上传图片需要配置 `bot_app_id` 和 `bot_secret`。

### Rich Text Post

发送富文本消息，支持文本、链接、@用户、图片等元素。

```python
from pywayne.lark_custom_bot import (
    create_text_content,
    create_link_content,
    create_at_content,
    create_image_content
)

content = [
    [create_text_content("欢迎使用飞书机器人\n")],
    [create_link_content(href="https://www.feishu.cn", text="点击访问飞书")],
    [create_at_content(user_id="user_id", user_name="用户名")],
    [create_image_content(image_key="img_xxx", width=400, height=300)]
]

bot.send_post(content, title="富文本消息标题")
```

### Interactive Card

发送交互式卡片消息。

```python
card = {
    "header": {
        "title": {
            "content": "卡片标题",
            "tag": "plain_text"
        }
    },
    "elements": [
        {
            "tag": "div",
            "text": {
                "tag": "plain_text",
                "content": "卡片内容"
            }
        }
    ]
}
bot.send_interactive(card)
```

### Share Chat

分享会话。

```python
bot.send_share_chat(share_chat_id="oc_xxxxxxxxxxxxxxxx")
```

## Content Builders

### create_text_content

创建文本内容元素。

```python
create_text_content("文本内容", unescape=False)
```

### create_link_content

创建超链接内容元素。

```python
create_link_content(href="https://example.com", text="点击访问")
```

### create_at_content

创建 @用户内容元素。

```python
create_at_content(user_id="user_id", user_name="用户名")
```

### create_image_content

创建图片内容元素。

```python
create_image_content(image_key="img_xxx", width=400, height=300)
```

## Authentication

### Signature Verification

为增强安全性，可配置 `secret` 进行签名验证：

```python
bot = LarkCustomBot(
    webhook="your_webhook_url",
    secret="your_signing_secret"
)
```

### Image Upload Authentication

上传图片需要应用凭证：

```python
bot = LarkCustomBot(
    webhook="your_webhook_url",
    bot_app_id="cli_xxxxxxxxxxxxxxxx",
    bot_secret="xxxxxxxxxxxxxxx"
)
```

## Error Handling

所有方法内部已实现日志记录和异常处理。发送失败时会记录错误日志并抛出 `requests.RequestException`。
