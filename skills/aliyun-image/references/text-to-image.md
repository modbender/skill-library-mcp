# 文生图 API 参考

根据文本描述生成图像，尤其擅长复杂文字渲染。

## 目录

- [模型列表](#模型列表)
- [API 端点](#api-端点)
- [请求参数](#请求参数)
- [分辨率选项](#分辨率选项)
- [响应格式](#响应格式)
- [完整示例](#完整示例)

---

## 模型列表

| 模型 | 简介 | 输出规格 |
|------|------|----------|
| `qwen-image-plus` | Plus系列，默认推荐 | PNG, 1张, 可选分辨率 |
| `qwen-image-plus-2026-01-09` | Plus指定版本 | 同上 |
| `qwen-image-max` | Max系列，更高质量 | PNG, 1张, 可选分辨率 |
| `qwen-image-max-2025-12-30` | Max指定版本 | 同上 |
| `qwen-image` | 基础版 | PNG, 1张, 默认分辨率 |

---

## API 端点

| 地域 | 端点 |
|------|------|
| 北京（默认） | `https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation` |
| 新加坡 | `https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation` |

---

## 请求参数

### Headers

| Header | 值 |
|--------|-----|
| `Content-Type` | `application/json` |
| `Authorization` | `Bearer $DASHSCOPE_API_KEY` |

### Body

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| `model` | string | 是 | 模型名称 |
| `input.messages` | array | 是 | 消息数组，仅支持单轮 |
| `input.messages[].role` | string | 是 | 固定 `user` |
| `input.messages[].content[].text` | string | 是 | 提示词，≤800字符 |

### parameters

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `negative_prompt` | string | - | 反向提示词，≤500字符 |
| `size` | string | `1664*928` | 分辨率 `宽*高` |
| `n` | integer | 1 | 生成数量，**固定为1** |
| `prompt_extend` | bool | `true` | 提示词智能改写 |
| `watermark` | bool | `false` | 是否添加水印 |
| `seed` | integer | 随机 | 随机种子 [0, 2147483647] |

---

## 分辨率选项

| 宽高比 | 分辨率 |
|--------|--------|
| 16:9（默认） | `1664*928` |
| 4:3 | `1472*1104` |
| 1:1 | `1328*1328` |
| 3:4 | `1104*1472` |
| 9:16 | `928*1664` |

---

## 响应格式

```json
{
    "output": {
        "choices": [{
            "finish_reason": "stop",
            "message": {
                "content": [{"image": "https://dashscope-result-sh.oss-cn-shanghai.aliyuncs.com/xxx.png?Expires=xxx"}]
            }
        }]
    },
    "usage": {"image_count": 1, "width": 1664, "height": 928},
    "request_id": "xxx"
}
```

---

## 完整示例

### cURL

```bash
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation' \
--header 'Content-Type: application/json' \
--header "Authorization: Bearer $DASHSCOPE_API_KEY" \
--data '{
    "model": "qwen-image-plus",
    "input": {
        "messages": [{"role": "user", "content": [{"text": "一只坐着的橘黄色的猫"}]}]
    },
    "parameters": {
        "negative_prompt": "低分辨率，低画质，肢体畸形",
        "prompt_extend": true,
        "watermark": false,
        "size": "1664*928"
    }
}'
```

### Python

```python
import os
import requests

def generate_image(prompt, size="1664*928", negative_prompt=None, use_max=False):
    api_key = os.getenv("DASHSCOPE_API_KEY")
    model = "qwen-image-max" if use_max else "qwen-image-plus"

    payload = {
        "model": model,
        "input": {"messages": [{"role": "user", "content": [{"text": prompt}]}]},
        "parameters": {"prompt_extend": True, "watermark": False, "size": size}
    }
    if negative_prompt:
        payload["parameters"]["negative_prompt"] = negative_prompt

    resp = requests.post(
        "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        json=payload
    )
    result = resp.json()
    if "output" in result:
        return result["output"]["choices"][0]["message"]["content"][0]["image"]
    raise Exception(f"Error: {result.get('message', 'Unknown')}")

# 使用
url = generate_image("一片宁静的湖泊，远处是雪山倒影", size="1920*1080")
print(url)
```

## 提示词技巧

1. **具体描述**：详细描述场景、风格、构图
2. **使用修饰词**：如"高清"、"写实"、"卡通风格"
3. **指定细节**：颜色、光影、视角
4. **利用智能改写**：开启 `prompt_extend` 优化简短提示词
