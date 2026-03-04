# API 格式参考

本技能支持两种 API 格式调用 Gemini 图片生成模型（如 `gemini-3-pro-image-preview`）。通过 `--api-format` / `-F` / `GEMINI_API_FORMAT` 切换。

## OpenAI 兼容格式（默认）

适用于提供 OpenAI 兼容接口的第三方代理（如 cliproxy、one-api 等）。脚本通过 `httpx` 直接发送 HTTP 请求。

### 请求格式

**文生图（纯文本提示）：**

```http
POST {baseUrl}/chat/completions
Authorization: Bearer {apiKey}
Content-Type: application/json

{
  "model": "gemini-3-pro-image-preview",
  "messages": [
    {"role": "user", "content": "一只戴着礼帽的橘猫，水彩风格"}
  ],
  "max_tokens": 4096,
  "temperature": 1.0
}
```

> 纯文本提示时，`content` 为字符串；带图片时，`content` 为数组。

**图片编辑（单图 + 文本指令）：**

输入图片以 base64 编码的 data URL 传入，文本指令放在最后：

```json
{
  "model": "gemini-3-pro-image-preview",
  "messages": [{
    "role": "user",
    "content": [
      {
        "type": "image_url",
        "image_url": {"url": "data:image/png;base64,iVBORw0KGgo..."}
      },
      {"type": "text", "text": "把背景改成星空"}
    ]
  }],
  "max_tokens": 4096,
  "temperature": 1.0
}
```

**多图合成（最多 14 张图 + 文本指令）：**

```json
{
  "model": "gemini-3-pro-image-preview",
  "messages": [{
    "role": "user",
    "content": [
      {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}},
      {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}},
      {"type": "text", "text": "将这两张图片合成为一张全景图"}
    ]
  }],
  "max_tokens": 4096,
  "temperature": 1.0
}
```

**分辨率与风格控制：**

OpenAI 兼容格式没有原生的分辨率参数，脚本通过在提示词末尾追加标记实现：

```
用户提示词原文
[Resolution: 2K]
[Quality: high detail]
[Style: vivid, vibrant colors]
```

这些标记由 `--resolution`、`--quality`、`--style` 参数自动生成，无需手动添加。

### 响应格式

不同代理服务返回的响应结构可能不同。脚本按以下顺序依次尝试解析（匹配到第一个即返回）：

**格式 A：`message.images` 数组**

部分代理（如 cliproxy）将图片放在独立的 `images` 字段中：

```json
{
  "choices": [{
    "message": {
      "content": "这是一只戴着礼帽的橘猫",
      "images": [
        {
          "type": "image_url",
          "image_url": {"url": "data:image/png;base64,iVBORw0KGgo..."}
        }
      ]
    }
  }]
}
```

脚本提取逻辑（按优先级）：
1. `images[].image_url.url` → 解码 base64 data URL
2. `images[].base64` → 直接解码 base64 字符串
3. `images[].url` → 作为图片下载链接返回

**格式 B：`content` 数组含 `image_url`**

图片和文本混合在 `content` 数组中：

```json
{
  "choices": [{
    "message": {
      "content": [
        {"type": "text", "text": "这是生成的图片"},
        {
          "type": "image_url",
          "image_url": {"url": "data:image/png;base64,iVBORw0KGgo..."}
        }
      ]
    }
  }]
}
```

脚本提取逻辑：遍历 `content` 数组，找到 `type: "image_url"` 的项，解码其 data URL。

> 注意：脚本仅处理 `data:image/...;base64,...` 格式的 URL，不支持普通 HTTP 图片链接。

**格式 C：`content` 数组含 `image` 对象**

图片以独立的 `image` 对象返回：

```json
{
  "choices": [{
    "message": {
      "content": [
        {"type": "text", "text": "这是生成的图片"},
        {
          "type": "image",
          "image": {"base64": "iVBORw0KGgo...", "mime_type": "image/png"}
        }
      ]
    }
  }]
}
```

脚本提取逻辑（按优先级）：
1. `image.base64` → 直接解码
2. `image.url` → 作为图片下载链接返回

**格式 E：`content` 为 data URL 字符串**

部分代理直接将 base64 图片作为 `content` 字符串返回：

```json
{
  "choices": [{
    "message": {
      "content": "data:image/png;base64,iVBORw0KGgo..."
    }
  }]
}
```

脚本提取逻辑：检测 `content` 字符串以 `data:image` 开头，直接解码。

**格式 D：DALL-E 风格（`data[].b64_json`）**

兼容 OpenAI Images API 的响应格式（无 `choices` 包装）：

```json
{
  "data": [
    {
      "b64_json": "iVBORw0KGgo...",
      "revised_prompt": "A ginger cat wearing a top hat, watercolor style"
    }
  ]
}
```

脚本提取逻辑（按优先级）：
1. `data[].b64_json` → 直接解码
2. `data[].url` → 作为图片下载链接，通过 `httpx.get` 下载并保存

### 解析优先级总结

```
格式 A（message.images）
  ↓ 未匹配
格式 B/C/E（message.content 数组或字符串）
  ↓ 未匹配
格式 D（data[].b64_json / data[].url）
  ↓ 未匹配
输出文本响应，返回空结果
```

### 错误处理与重试

| 场景 | 处理方式 |
|------|---------|
| HTTP 200 | 正常解析响应 |
| HTTP 429（限流） | 自动重试，间隔 10s → 20s → 40s，最多 3 次 |
| 请求超时（`ReadTimeout`） | 同上重试策略，失败后建议增加 `--timeout` |
| 连接失败（`ConnectError`） | 直接报错退出，请检查网络或端点地址 |
| 其他 HTTP 错误 | 输出状态码和响应体，直接退出 |
| 响应中无图片数据 | 输出模型文本响应（如有），提示使用 `--verbose` 排查 |

## Google 原生格式

适用于直接调用 Google Gemini API 或兼容 Google API 结构的第三方服务。脚本通过 `google-genai` SDK 调用。

### 请求方式

```python
from google import genai
from google.genai import types

client = genai.Client(
    api_key="your-api-key",
    http_options={"base_url": "https://your-provider.com"}  # 可选，自定义端点
)
```

**文生图：**

```python
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="一只戴着礼帽的橘猫，水彩风格",
    config=types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(image_size="1K"),  # 可选：1K / 2K / 4K
    ),
)
```

**图片编辑（传入 PIL Image 对象）：**

```python
from PIL import Image
input_img = Image.open("input.png")

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[input_img, "把背景改成星空"],
    config=types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(image_size="2K"),
    ),
)
```

**多图合成：**

```python
img1 = Image.open("photo1.png")
img2 = Image.open("photo2.png")

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[img1, img2, "将这两张照片合成为一张全景图"],
    config=types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
    ),
)
```

> `contents` 中 PIL Image 对象和文本可以任意混合，文本建议放在最后。

### 响应结构

响应为多模态内容，`response.parts` 中包含 `text` 和 `inline_data` 两种类型：

```python
for part in response.parts:
    if part.text is not None:
        print(part.text)           # 模型的文本描述（可能为空）
    elif part.inline_data is not None:
        image_bytes = part.inline_data.data       # bytes 或 base64 字符串
        mime_type = part.inline_data.mime_type     # 通常为 "image/png"
```

> 脚本会自动处理 `inline_data.data` 为 `bytes` 或 base64 `str` 两种情况。如果是字符串，先 base64 解码再保存。

### 与 OpenAI 格式的区别

| 特性 | OpenAI 兼容格式 | Google 原生格式 |
|------|---------------|---------------|
| 网络库 | `httpx`（直接 HTTP 请求） | `google-genai` SDK |
| 认证方式 | `Authorization: Bearer` 请求头 | SDK 内置 API Key 管理 |
| 图片输入 | base64 data URL 字符串 | PIL Image 对象（自动序列化） |
| 图片输出 | 四种格式自动识别（A/B/C/D/E） | `inline_data.data` 统一格式 |
| 自定义端点 | `--base-url` 拼接 `/chat/completions` | `http_options.base_url` |
| 分辨率控制 | 提示词末尾追加 `[Resolution: 2K]` | `ImageConfig(image_size="2K")` 原生参数 |
| 重试机制 | 脚本内置（429 + 超时，最多 3 次） | 依赖 SDK 默认行为 |
| 适用场景 | 第三方代理、自建中转 | Google 官方 API、兼容代理 |

## 支持的模型

| 模型 | 说明 |
|------|------|
| `gemini-3-pro-image-preview` | 默认模型，最新一代图片生成能力 |
| `gemini-2.5-flash-image` | 上一代（Nano Banana），速度快、质量好 |
| `gemini-2.0-flash-exp` | 早期实验版本 |
| `gemini-3.1-flash-image-preview` | Flash 系列最新图片生成模型，速度快 |

模型名称通过 `--model` / `-m` / `GEMINI_MODEL` 配置，具体可用模型取决于 API 提供商。
