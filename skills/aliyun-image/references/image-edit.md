# 图像编辑 API 参考

支持单图编辑和多图融合，可修改文字、增删物体、改变动作、迁移风格。

## 目录

- [模型列表](#模型列表)
- [输入图像要求](#输入图像要求)
- [请求参数](#请求参数)
- [分辨率选项](#分辨率选项)
- [使用场景](#使用场景)
- [完整示例](#完整示例)

---

## 模型列表

| 模型 | 简介 | 输出规格 |
|------|------|----------|
| `qwen-image-edit-plus` | Plus系列，默认推荐 | PNG, 1-6张, 可自定义分辨率 |
| `qwen-image-edit-plus-2025-12-15` | Plus指定版本 | 同上 |
| `qwen-image-edit-max` | Max系列，更高质量 | PNG, 1-6张, 可自定义分辨率 |
| `qwen-image-edit-max-2026-01-16` | Max指定版本 | 同上 |
| `qwen-image-edit` | 基础版 | PNG, 1张, 默认分辨率 |

---

## 输入图像要求

| 项目 | 要求 |
|------|------|
| 格式 | JPG, JPEG, PNG, BMP, TIFF, WEBP, GIF |
| 分辨率 | 建议 384-3072 像素 |
| 大小 | ≤10MB |
| GIF | 仅处理第一帧 |
| 数量 | 1-3张 |

### 输入格式

| 格式 | 示例 |
|------|------|
| 公网URL | `https://example.com/image.jpg` |
| OSS临时URL | `oss://dashscope-instant/xxx/cat.png` |
| Base64 | `data:image/jpeg;base64,GDU7MtCZz...` |

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
| `input.messages[].role` | string | 是 | 固定 `user` |
| `input.messages[].content[].image` | string | 是 | 图像URL/Base64，1-3张 |
| `input.messages[].content[].text` | string | 是 | 编辑指令，≤800字符 |

### parameters

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `n` | integer | 1 | 输出数量，Max/Plus支持1-6 |
| `negative_prompt` | string | - | 反向提示词，≤500字符 |
| `size` | string | 自动 | 分辨率 `宽*高`，范围[512, 2048] |
| `prompt_extend` | bool | `true` | 提示词智能改写 |
| `watermark` | bool | `false` | 是否添加水印 |
| `seed` | integer | 随机 | 随机种子 [0, 2147483647] |

---

## 分辨率选项

| 宽高比 | 分辨率 |
|--------|--------|
| 1:1 | `1024*1024`, `1536*1536` |
| 2:3 | `768*1152`, `1024*1536` |
| 3:2 | `1152*768`, `1536*1024` |
| 3:4 | `960*1280`, `1080*1440` |
| 4:3 | `1280*960`, `1440*1080` |
| 9:16 | `720*1280`, `1080*1920` |
| 16:9 | `1280*720`, `1920*1080` |
| 21:9 | `1344*576`, `2048*872` |

**默认规则**：若不设置size，输出图像保持与输入图像（多图时为最后一张）相似的宽高比，总像素≈1024*1024。

---

## 使用场景

### 单图编辑

```json
{
    "model": "qwen-image-edit-plus",
    "input": {
        "messages": [{
            "role": "user",
            "content": [
                {"image": "https://example.com/photo.jpg"},
                {"text": "把背景改成星空，添加流星"}
            ]
        }]
    },
    "parameters": {"n": 2, "prompt_extend": true, "watermark": false}
}
```

### 多图融合（最多3张输入图）

```json
{
    "model": "qwen-image-edit-plus",
    "input": {
        "messages": [{
            "role": "user",
            "content": [
                {"image": "https://example.com/person.jpg"},
                {"image": "https://example.com/dress.jpg"},
                {"image": "https://example.com/pose.jpg"},
                {"text": "图1中的人物穿着图2的裙子，按图3的姿势站立"}
            ]
        }]
    },
    "parameters": {"n": 1, "prompt_extend": true}
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
    "model": "qwen-image-edit-plus",
    "input": {
        "messages": [{
            "role": "user",
            "content": [
                {"image": "https://example.com/photo.jpg"},
                {"text": "把女孩的头发改成红色"}
            ]
        }]
    },
    "parameters": {"n": 2, "prompt_extend": true, "watermark": false}
}'
```

### Python

```python
import os
import requests
import base64

def edit_image(images, instruction, n=1, size=None, use_max=False):
    """
    编辑图像

    Args:
        images: 图像URL或本地路径列表（1-3张）
        instruction: 编辑指令
        n: 输出数量（1-6）
        size: 输出分辨率
        use_max: 是否使用Max模型
    """
    api_key = os.getenv("DASHSCOPE_API_KEY")
    model = "qwen-image-edit-max" if use_max else "qwen-image-edit-plus"

    # 处理图像输入
    content = []
    for img in images if isinstance(images, list) else [images]:
        if img.startswith("http") or img.startswith("oss://") or img.startswith("data:"):
            content.append({"image": img})
        else:
            # 本地文件转Base64
            with open(img, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            content.append({"image": f"data:image/jpeg;base64,{b64}"})

    content.append({"text": instruction})

    payload = {
        "model": model,
        "input": {"messages": [{"role": "user", "content": content}]},
        "parameters": {"n": n, "prompt_extend": True, "watermark": False}
    }
    if size:
        payload["parameters"]["size"] = size

    resp = requests.post(
        "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        json=payload
    )
    result = resp.json()
    if "output" in result:
        return [c["image"] for c in result["output"]["choices"][0]["message"]["content"]]
    raise Exception(f"Error: {result.get('message', 'Unknown')}")

# 单图编辑
urls = edit_image("https://example.com/photo.jpg", "把背景替换成东京夜景", n=2)
for i, url in enumerate(urls):
    print(f"结果 {i+1}: {url}")

# 多图融合
urls = edit_image(
    ["person.jpg", "dress.jpg", "pose.jpg"],
    "图1的人物穿图2的裙子，按图3的姿势",
    n=1
)
```

---

## 编辑技巧

1. **明确指令**：清晰描述要修改的内容
2. **多图引用**：如"图1中的人物穿着图2的衣服"
3. **保持原图特征**：指定"保持原有背景"、"保持表情不变"
4. **适当使用反向提示词**：避免不需要的效果

---

## 响应格式

```json
{
    "output": {
        "choices": [{
            "finish_reason": "stop",
            "message": {
                "content": [
                    {"image": "https://dashscope-result-sz.oss-cn-shenzhen.aliyuncs.com/xxx.png"},
                    {"image": "https://dashscope-result-sz.oss-cn-shenzhen.aliyuncs.com/yyy.png"}
                ]
            }
        }]
    },
    "usage": {"image_count": 2, "width": 1536, "height": 1024},
    "request_id": "xxx"
}
```
