# API 调用方式

本 skill 支持两种 API 调用方式，根据模型类型自动选择。

---

## 方式一：MCP 调用（Fal.ai 模型）

适用于 `fal-ai/*` 开头的模型，通过 `user-速推AI` MCP 服务调用。

### 文生图

使用 `submit_task` 工具：

```json
{
  "model_id": "fal-ai/flux-2/flash",
  "parameters": {
    "prompt": "A young woman standing in a garden, full body shot, clear face, simple background",
    "image_size": "portrait_16_9",
    "num_images": 1
  }
}
```

### 图像编辑（人物一致性测试）

```json
{
  "model_id": "fal-ai/flux-2/flash",
  "parameters": {
    "prompt": "Transform this person to be running on a sunny beach, waves splashing, joyful expression, same person same face",
    "image_urls": ["https://example.com/base_portrait.png"]
  }
}
```

### 查询结果

使用 `get_task` 工具：

```json
{
  "task_id": "返回的任务ID"
}
```

### image_size 可选值

| 值 | 尺寸 | 用途 |
|----|------|------|
| `portrait_16_9` | 576x1024 | 竖版人像（推荐基准图） |
| `portrait_4_3` | 768x1024 | 竖版标准 |
| `landscape_16_9` | 1024x576 | 横版风景 |
| `landscape_4_3` | 1024x768 | 横版标准 |
| `square_hd` | 1024x1024 | 高清正方形 |
| `square` | 512x512 | 标准正方形 |

---

## 方式二：HTTP API（小北 API 模型）

适用于 `jimeng-*`、`nano-banana*`、`grok-*` 等模型。

### 接口地址

- **Base URL**: `https://api.xbyjs.top`
- **端点**: `/v1/chat/completions`

## 文生图调用

### 请求格式

```json
{
  "model": "模型名称",
  "messages": [{
    "role": "user",
    "content": "提示词，比例如16:9"
  }]
}
```

### cURL 示例

```bash
curl -s https://api.xbyjs.top/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "model": "jimeng-4.5",
    "messages": [{
      "role": "user",
      "content": "一只可爱的金毛犬在草地上奔跑，阳光明媚，16:9"
    }]
  }'
```

### 响应格式

```json
{
  "id": "chatcmpl-xxx",
  "model": "jimeng-4.5",
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "![image](https://xxx.png)\n![image](https://xxx.png)"
    }
  }],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 100,
    "total_tokens": 120
  }
}
```

## 图生图调用

### 请求格式

```json
{
  "model": "模型名称",
  "messages": [{
    "role": "user",
    "content": [
      {"type": "text", "text": "编辑指令"},
      {"type": "image_url", "image_url": {"url": "原图URL"}}
    ]
  }]
}
```

### cURL 示例

```bash
curl -s https://api.xbyjs.top/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "model": "jimeng-4.5",
    "messages": [{
      "role": "user",
      "content": [
        {"type": "text", "text": "把背景改成海边日落"},
        {"type": "image_url", "image_url": {"url": "https://example.com/photo.jpg"}}
      ]
    }]
  }'
```

## 比例参数说明

在提示词末尾添加比例参数来控制输出尺寸：

| 比例 | 用途 | 示例 |
|------|------|------|
| 16:9 | 横版风景、封面 | `xxx，16:9` |
| 9:16 | 竖版人像、手机壁纸 | `xxx，9:16` |
| 1:1 | 方形、头像、产品图 | `xxx，1:1` |
| 4:3 | 标准比例 | `xxx，4:3` |
| 3:4 | 竖版标准 | `xxx，3:4` |

## 错误处理

### 常见错误码

| 状态码 | 错误 | 处理方式 |
|--------|------|---------|
| 400 | 请求参数错误 | 检查请求格式 |
| 401 | 认证失败 | 检查 API Key |
| 429 | 请求过于频繁 | 降低请求频率 |
| 500 | 服务器错误 | 重试或更换模型 |
| 503 | 服务不可用 | 当前模型无可用渠道 |

### 超时处理

- 默认超时：120 秒
- 建议：对于高清模型（4K），适当增加超时时间

## Python 调用示例

```python
import requests
import json

def generate_image(model: str, prompt: str, api_key: str) -> dict:
    """文生图"""
    response = requests.post(
        "https://api.xbyjs.top/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        },
        timeout=120
    )
    return response.json()

def edit_image(model: str, instruction: str, image_url: str, api_key: str) -> dict:
    """图生图"""
    response = requests.post(
        "https://api.xbyjs.top/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        json={
            "model": model,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": instruction},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }]
        },
        timeout=120
    )
    return response.json()
```

## 解析图片 URL

响应中的图片以 Markdown 格式返回，需要解析提取：

```python
import re

def extract_image_urls(content: str) -> list:
    """从响应内容中提取图片 URL"""
    pattern = r'!\[.*?\]\((https?://[^\)]+)\)'
    return re.findall(pattern, content)

# 使用示例
content = response['choices'][0]['message']['content']
urls = extract_image_urls(content)
print(f"生成了 {len(urls)} 张图片")
```
