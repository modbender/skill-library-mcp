# 图像翻译 API 参考

千问-图像翻译模型（Qwen-MT-Image）可精准翻译图像中的文字，并保留原始排版。

## 目录

- [模型概览](#模型概览)
- [支持的语言](#支持的语言)
- [API 调用流程](#api-调用流程)
- [创建任务](#创建任务)
- [查询结果](#查询结果)
- [高级功能](#高级功能)
- [完整示例](#完整示例)

---

## 模型概览

| 模型 | 简介 | 计费 |
|------|------|------|
| `qwen-mt-image` | 图像翻译，保留排版 | 0.003元/张 |

**特点**：
- 精准翻译图像中的文字
- 保留原始排版与内容信息
- 支持术语定义、敏感词过滤、图像主体检测

---

## 支持的语言

### 源语种（11种）

| 中文名 | 英文全称 | 编码 |
|--------|----------|------|
| 简体中文 | Chinese | zh |
| 英文 | English | en |
| 韩语 | Korean | ko |
| 日语 | Japanese | ja |
| 俄语 | Russian | ru |
| 西语 | Spanish | es |
| 法语 | French | fr |
| 葡萄牙语 | Portuguese | pt |
| 意大利语 | Italian | it |
| 德语 | Germany | de |
| 越南语 | Vietnamese | vi |

### 目标语种（14种）

| 中文名 | 英文全称 | 编码 |
|--------|----------|------|
| 简体中文 | Chinese | zh |
| 英文 | English | en |
| 韩语 | Korean | ko |
| 日语 | Japanese | ja |
| 俄语 | Russian | ru |
| 西语 | Spanish | es |
| 法语 | French | fr |
| 葡萄牙语 | Portuguese | pt |
| 意大利语 | Italian | it |
| 越南语 | Vietnamese | vi |
| 马来语 | Malay | ms |
| 泰语 | Thai | th |
| 印尼语 | Indonesian | id |
| 阿拉伯语 | Arabian | ar |

**注意**：翻译方向必须以中文或英文作为源语种或目标语种。不支持在其他语种之间互译（如：日文译为韩文）。若不确定源语种，可设置为 `auto` 自动检测。

---

## API 调用流程

图像翻译采用异步模式，调用流程分两步：

1. **创建任务获取任务ID**：发送请求创建任务，返回 `task_id`
2. **根据任务ID查询结果**：使用 `task_id` 轮询任务状态，直到任务完成

---

## 创建任务

### 端点

```
POST https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis
```

### Headers

| Header | 值 |
|--------|-----|
| `Content-Type` | `application/json` |
| `Authorization` | `Bearer $DASHSCOPE_API_KEY` |
| `X-DashScope-Async` | `enable`（必须） |

### Body

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| `model` | string | 是 | 固定 `qwen-mt-image` |
| `input.image_url` | string | 是 | 输入图像URL |
| `input.source_lang` | string | 是 | 源语种，支持语种全称或编码，不确定时设为 `auto` |
| `input.target_lang` | string | 是 | 目标语种 |
| `input.ext.domainHint` | string | 否 | 领域提示，英文描述使用场景、译文风格（≤200词） |
| `input.ext.sensitives` | array | 否 | 敏感词列表，屏蔽部分内容（≤50个） |
| `input.ext.terminologies` | array | 否 | 术语定义，`[{src, tgt}]` 格式 |
| `input.ext.config.skipImgSegment` | bool | 否 | 是否翻译主体文字，默认 `false` 不翻译 |

### 输入图像要求

| 项目 | 要求 |
|------|------|
| 格式 | JPG, JPEG, PNG, BMP, PNM, PPM, TIFF, WEBP |
| 分辨率 | 15-8192 像素，宽高比 1:10 至 10:1 |
| 大小 | ≤10MB |

### 响应

```json
{
    "output": {
        "task_status": "PENDING",
        "task_id": "0385dc79-5ff8-4d82-bcb6-xxxxxx"
    },
    "request_id": "4909100c-7b5a-9f92-bfe5-xxxxxx"
}
```

---

## 查询结果

### 端点

```
GET https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}
```

### Headers

| Header | 值 |
|--------|-----|
| `Authorization` | `Bearer $DASHSCOPE_API_KEY` |

### 任务状态

| 状态 | 说明 |
|------|------|
| `PENDING` | 任务排队中 |
| `RUNNING` | 任务处理中 |
| `SUCCEEDED` | 任务执行成功 |
| `FAILED` | 任务执行失败 |
| `CANCELED` | 任务取消成功 |
| `UNKNOWN` | 任务不存在或状态未知 |

### 成功响应

```json
{
    "request_id": "5fec62eb-bf94-91f8-b9f4-f7f758e4e27e",
    "output": {
        "task_id": "72c52225-8444-4cab-ad0c-xxxxxx",
        "task_status": "SUCCEEDED",
        "submit_time": "2025-08-13 18:11:16.954",
        "scheduled_time": "2025-08-13 18:11:17.003",
        "end_time": "2025-08-13 18:11:23.860",
        "image_url": "http://dashscope-result-bj.oss-cn-beijing.aliyuncs.com/xxx?Expires=xxx"
    },
    "usage": {"image_count": 1}
}
```

---

## 高级功能

### 领域提示（domainHint）

用英文描述使用场景和译文风格，获得更符合特定领域的翻译：

```json
{
    "input": {
        "ext": {
            "domainHint": "These sentences are from seller-buyer conversations on a B2C ecommerce platform. Translate them into clear, engaging customer service language."
        }
    }
}
```

### 敏感词过滤（sensitives）

屏蔽指定内容，翻译后图片中不显示：

```json
{
    "input": {
        "ext": {
            "sensitives": ["满200-20", "七天无理由退换"]
        }
    }
}
```

### 术语定义（terminologies）

为特定术语设定固定译文：

```json
{
    "input": {
        "ext": {
            "terminologies": [
                {"src": "应用程序接口", "tgt": "API"},
                {"src": "机器学习", "tgt": "ML"}
            ]
        }
    }
}
```

### 翻译主体文字（skipImgSegment）

控制是否翻译图像中关键主体（如人物、商品、Logo）上的文字：

- `false`（默认）：智能识别主体，不翻译主体上的文字
- `true`：将图像主体上的文字一并翻译

```json
{
    "input": {
        "ext": {
            "config": {"skipImgSegment": true}
        }
    }
}
```

---

## 完整示例

### cURL

```bash
# 1. 创建任务
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis' \
--header 'X-DashScope-Async: enable' \
--header "Authorization: Bearer $DASHSCOPE_API_KEY" \
--header 'Content-Type: application/json' \
--data '{
    "model": "qwen-mt-image",
    "input": {
        "image_url": "https://example.com/image.jpg",
        "source_lang": "en",
        "target_lang": "zh"
    }
}'

# 2. 查询结果（将task_id替换为实际值）
curl -X GET "https://dashscope.aliyuncs.com/api/v1/tasks/YOUR_TASK_ID" \
--header "Authorization: Bearer $DASHSCOPE_API_KEY"
```

### Python

```python
import os
import time
import requests

def translate_image(
    image_url: str,
    source_lang: str = "auto",
    target_lang: str = "zh",
    domain_hint: str = None,
    sensitives: list = None,
    terminologies: list = None,
    skip_img_segment: bool = False,
    poll_interval: int = 3
) -> str:
    """
    图像翻译

    Args:
        image_url: 输入图像URL
        source_lang: 源语种，默认自动检测
        target_lang: 目标语种，默认中文
        domain_hint: 领域提示
        sensitives: 敏感词列表
        terminologies: 术语定义列表
        skip_img_segment: 是否翻译主体文字
        poll_interval: 轮询间隔（秒）

    Returns:
        翻译后图像的URL
    """
    api_key = os.getenv("DASHSCOPE_API_KEY")

    # 构建请求体
    payload = {
        "model": "qwen-mt-image",
        "input": {
            "image_url": image_url,
            "source_lang": source_lang,
            "target_lang": target_lang
        }
    }

    # 添加可选参数
    ext = {}
    if domain_hint:
        ext["domainHint"] = domain_hint
    if sensitives:
        ext["sensitives"] = sensitives
    if terminologies:
        ext["terminologies"] = terminologies
    if skip_img_segment:
        ext["config"] = {"skipImgSegment": True}

    if ext:
        payload["input"]["ext"] = ext

    # 创建任务
    resp = requests.post(
        "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "X-DashScope-Async": "enable"
        },
        json=payload
    )
    result = resp.json()

    if "code" in result:
        raise Exception(f"[{result['code']}] {result.get('message', 'Unknown error')}")

    task_id = result["output"]["task_id"]
    print(f"任务已创建: {task_id}")

    # 轮询查询结果
    while True:
        time.sleep(poll_interval)
        resp = requests.get(
            f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        result = resp.json()
        status = result["output"]["task_status"]

        if status == "SUCCEEDED":
            return result["output"]["image_url"]
        elif status == "FAILED":
            raise Exception(f"任务失败: {result['output'].get('message', 'Unknown error')}")
        elif status in ("PENDING", "RUNNING"):
            print(f"任务状态: {status}, 等待中...")
        else:
            raise Exception(f"未知状态: {status}")

# 使用示例
url = translate_image(
    image_url="https://example.com/english-poster.jpg",
    source_lang="en",
    target_lang="zh"
)
print(f"翻译结果: {url}")
```

---

## 注意事项

1. **有效期**：
   - `task_id` 查询有效期为 **24小时**
   - 翻译后图像URL有效期为 **24小时**
2. **耗时**：模型处理约15秒，建议轮询间隔3秒
3. **限流**：RPS限制为1，同时处理任务数为2
4. **域名白名单**：如需访问图像链接，请配置OSS域名白名单
