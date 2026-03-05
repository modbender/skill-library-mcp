---
name: glm-4.6v-api
description: "调用智谱 GLM-4.6V 多模态视觉模型。支持图像理解、文档解析、视频理解、工具调用。触发词：GLM-4.6V、视觉模型、多模态、看图、识图"
---

# GLM-4.6V API 调用指南

GLM-4.6V 是智谱 AI 发布的多模态大模型，支持 128K 上下文，原生支持 Function Call（工具调用）。

## 模型版本

| 模型 | 参数量 | 用途 |
|------|--------|------|
| `glm-4.6v` | 106B-A12B | 云端高性能版 |
| `glm-4.6v-flash` | 9B | 轻量版，免费使用 |

## API 价格

- **输入**: 1 元 / 百万 tokens
- **输出**: 3 元 / 百万 tokens
- **GLM-4.6V-Flash**: 免费

## 基础调用

### Python SDK

```python
from zhipuai import ZhipuAI

client = ZhipuAI(api_key="YOUR_API_KEY")

# 文本对话
response = client.chat.completions.create(
    model="glm-4.6v",  # 或 "glm-4.6v-flash"
    messages=[
        {"role": "user", "content": "你好"}
    ]
)
print(response.choices[0].message.content)
```

### cURL

```bash
curl -s -X POST https://open.bigmodel.cn/api/paas/v4/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-4.6v",
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

## 图像输入

GLM-4.6V 支持多种图像输入方式：

### 方式 1: URL 图像

```python
response = client.chat.completions.create(
    model="glm-4.6v",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": "https://example.com/image.jpg"}
                },
                {
                    "type": "text",
                    "text": "请描述这张图片"
                }
            ]
        }
    ]
)
```

### 方式 2: Base64 编码

```python
import base64

# 读取图片并编码
with open("image.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode()

response = client.chat.completions.create(
    model="glm-4.6v",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                },
                {
                    "type": "text",
                    "text": "请描述这张图片"
                }
            ]
        }
    ]
)
```

### cURL 图像调用

```bash
curl -s -X POST https://open.bigmodel.cn/api/paas/v4/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-4.6v",
    "messages": [{
      "role": "user",
      "content": [
        {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}},
        {"type": "text", "text": "请描述这张图片"}
      ]
    }]
  }'
```

## Function Call (工具调用)

GLM-4.6V 原生支持多模态工具调用，图像可以直接作为工具参数。

### 定义工具

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_image",
            "description": "搜索相似图片",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_url": {
                        "type": "string",
                        "description": "要搜索的图片URL"
                    },
                    "query": {
                        "type": "string",
                        "description": "搜索关键词"
                    }
                },
                "required": ["image_url"]
            }
        }
    }
]
```

### 调用工具

```python
response = client.chat.completions.create(
    model="glm-4.6v",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": "https://example.com/product.jpg"}},
                {"type": "text", "text": "帮我搜同款"}
            ]
        }
    ],
    tools=tools,
    tool_choice="auto"
)

# 处理工具调用
if response.choices[0].finish_reason == "tool_calls":
    tool_call = response.choices[0].message.tool_calls[0]
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)
    print(f"调用函数: {function_name}")
    print(f"参数: {arguments}")
```

## 长上下文 (128K)

GLM-4.6V 支持 128K 上下文，可以处理：
- 约 150 页复杂文档
- 约 200 页 PPT
- 约 1 小时视频

```python
# 多文档对比
response = client.chat.completions.create(
    model="glm-4.6v",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": "https://example.com/report1.pdf"}},
                {"type": "image_url", "image_url": {"url": "https://example.com/report2.pdf"}},
                {"type": "text", "text": "对比这两份财报的核心指标"}
            ]
        }
    ]
)
```

## 典型应用场景

### 1. 前端复刻

上传网页截图，生成 HTML/CSS/JS 代码：

```python
response = client.chat.completions.create(
    model="glm-4.6v",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": "screenshot.png"}},
                {"type": "text", "text": "根据这个截图生成 HTML 代码"}
            ]
        }
    ]
)
```

### 2. 文档解读 + 图文输出

```python
response = client.chat.completions.create(
    model="glm-4.6v",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": "paper.pdf"}},
                {"type": "text", "text": "写一篇图文并茂的科普文章介绍这篇论文"}
            ]
        }
    ]
)
```

### 3. 商品比价

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_product",
            "description": "搜索商品价格",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_url": {"type": "string"},
                    "platforms": {"type": "array", "items": {"type": "string"}}
                }
            }
        }
    }
]

response = client.chat.completions.create(
    model="glm-4.6v",
    messages=[...],
    tools=tools
)
```

### 4. OCR 识别

```python
response = client.chat.completions.create(
    model="glm-4.6v-flash",  # 简单 OCR 用 flash 即可
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": "handwriting.jpg"}},
                {"type": "text", "text": "识别图片中的文字"}
            ]
        }
    ]
)
```

## 流式输出

```python
response = client.chat.completions.create(
    model="glm-4.6v",
    messages=[...],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## MCP 调用入口

GLM-4.6V 已融入 GLM Coding Plan，支持 MCP 协议：

- 文档: https://docs.bigmodel.cn/cn/coding-plan/mcp/vision-mcp-server

## 开源资源

| 平台 | 链接 |
|------|------|
| GitHub | https://github.com/zai-org/GLM-V |
| Hugging Face | https://huggingface.co/collections/zai-org/glm-46v |
| 魔搭社区 | https://modelscope.cn/collections/GLM-46V-37fabc27818446 |

## 在线体验

- z.ai (选择 GLM-4.6V 模型)
- 智谱清言 APP
- bigmodel.cn 控制台

## 注意事项

1. 建议复杂任务开启「深度思考」模式
2. 根据任务选择合适的工具，不要全部勾选
3. 简单任务（如 OCR）使用 `glm-4.6v-flash` 即可
4. 图像 URL 需要可公开访问，或使用 Base64 编码
