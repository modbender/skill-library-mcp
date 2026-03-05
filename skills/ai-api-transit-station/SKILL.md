---
name: AIAPI-Doc
description: 伝富AI-API文档技能 - 快速查询和使用302+个AI接口，涵盖聊天、图像、视频、音频、Midjourney等多个类别
---

# 伝富AI-API 调用技能

本技能帮助你调用伝富AI-API平台的302+个API接口。当用户需要调用AI能力时，使用此技能。

## 🔐 关键地址配置

> [!IMPORTANT]
> 请注意区分以下三个关键地址：

| 类型              | 地址                              | 说明                              |
| ----------------- | --------------------------------- | --------------------------------- |
| **API请求地址**   | `https://api.winfull.cloud-ip.cc` | 以此开头调用所有接口 (Base URL)   |
| **API官网/Token** | https://api.winfull.cloud-ip.cc/  | 在此注册账户、充值、申请API Token |
| **API文档地址**   | https://winfull.apifox.cn/        | 查阅最新的接口文档、参数说明      |

**认证方式**: 所有请求必须在Header中携带Bearer Token

```
Authorization: Bearer sk-xxxxxxxx
```

---

## 📚 API分类速查

完整文档地址：https://winfull.apifox.cn/

| 类别       | 接口数 | 说明                                |
| ---------- | ------ | ----------------------------------- |
| 图像生成   | 82     | DALL·E、Flux、豆包、Ideogram、Imagen |
| 视频生成   | 54     | Sora、Veo、可灵、即梦、Minimax      |
| 聊天       | 43     | GPT、Claude、Gemini、DeepSeek       |
| 任务查询   | 33     | 异步任务查询                        |
| 其他       | 24     | 文件上传、模型列表、代码执行等      |
| 函数调用   | 12     | Function Calling、Web搜索           |
| Replicate  | 12     | Replicate平台模型                   |
| 音乐生成   | 9      | Suno音乐生成                        |
| Midjourney | 8      | Midjourney完整功能                  |
| 音频       | 7      | TTS、Whisper、音频理解              |
| 系统API    | 7      | Token管理、用户信息                 |
| 可灵Kling  | 6      | 可灵专属功能                        |
| 文档处理   | 3      | PDF理解、文档解析                   |
| 嵌入       | 2      | Embeddings向量化                    |

**总计**: 302+ 个API接口

---

## 🚀 核心API调用模式

### 1. 聊天补全 (Chat Completions)

**端点**: `POST /v1/chat/completions`

```python
import requests

response = requests.post(
    "https://api.winfull.cloud-ip.cc/v1/chat/completions",
    headers={
        "Authorization": "Bearer sk-xxx",
        "Content-Type": "application/json"
    },
    json={
        "model": "gpt-5.2",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "你好"}
        ]
    }
)

result = response.json()
print(result["choices"][0]["message"]["content"])
```

---

### 2. 图像生成 (Image Generations)

**端点**: `POST /v1/images/generations`

```python
response = requests.post(
    "https://api.winfull.cloud-ip.cc/v1/images/generations",
    headers={
        "Authorization": "Bearer sk-xxx",
        "Content-Type": "application/json"
    },
    json={
        "model": "gpt-image-1.5-all",
        "prompt": "一只可爱的猫咪在草地上",
        "size": "1024x1536"
    }
)

result = response.json()
image_url = result["data"][0]["url"]
```

---

### 3. 图片上传到图床

> [!IMPORTANT]
> **图生视频必读**: 如果需要使用本地图片生成视频，必须先将图片上传到图床获取公网URL，然后使用该URL传给视频生成接口。
> 
> **两种方式**:
> 1. 上传本地图片到图床（推荐）
> 2. 直接使用已有的公网图片地址

**端点**: `POST https://imageproxy.zhongzhuan.chat/api/upload`

```python
# 方式1: 上传本地图片到图床
with open("reference_image.jpg", "rb") as f:
    response = requests.post(
        "https://imageproxy.zhongzhuan.chat/api/upload",
        headers={"Authorization": "Bearer sk-xxx"},
        files={"file": f}
    )

result = response.json()
image_url = result["url"]  # 获取图床URL
print(f"图片已上传: {image_url}")

# 方式2: 直接使用公网图片地址
# image_url = "https://example.com/your-image.jpg"

# 现在可以使用这个URL进行图生视频
```

**curl示例**:
```bash
curl --location --request POST 'https://imageproxy.zhongzhuan.chat/api/upload' \
--header 'Authorization: Bearer <token>' \
--form 'file=@"/path/to/your/image.png"'
```

---

### 4. 视频生成 (异步任务)

**创建视频**: `POST /v1/video/create`

```python
import time

# 如果需要使用参考图，先上传图片到图床
image_url = None
if use_reference_image:
    with open("reference.jpg", "rb") as f:
        upload_response = requests.post(
            "https://imageproxy.zhongzhuan.chat/api/upload",
            headers={"Authorization": "Bearer sk-xxx"},
            files={"file": f}
        )
    image_url = upload_response.json()["url"]
    print(f"参考图已上传: {image_url}")

# 步骤1: 创建视频任务
response = requests.post(
    "https://api.winfull.cloud-ip.cc/v1/video/create",
    headers={
        "Authorization": "Bearer sk-xxx",
        "Content-Type": "application/json"
    },
    json={
        "model": "sora-2",
        "prompt": "一只小狗在草地上奔跑",
        "images": [image_url] if image_url else [],  # 使用图床URL
        "orientation": "portrait",
        "duration": 15
    }
)

result = response.json()
task_id = result["id"]
```

**查询任务**: `GET /v1/video/query?id={task_id}`

```python
# 步骤2: 轮询查询任务状态
while True:
    result = requests.get(
        f"https://api.winfull.cloud-ip.cc/v1/video/query?id={task_id}",
        headers={"Authorization": "Bearer sk-xxx"}
    ).json()
    
    if result["status"] == "completed":
        video_url = result["video_url"]
        print(f"视频生成成功: {video_url}")
        break
    elif result["status"] == "failed":
        raise Exception(f"视频生成失败: {result.get('error')}")
    
    time.sleep(5)
```

---

### 5. 语音合成 (TTS)

**端点**: `POST /v1/audio/speech`

```python
response = requests.post(
    "https://api.winfull.cloud-ip.cc/v1/audio/speech",
    headers={
        "Authorization": "Bearer sk-xxx",
        "Content-Type": "application/json"
    },
    json={
        "model": "tts-1",
        "input": "你好，世界！",
        "voice": "alloy"
    }
)

with open("output.mp3", "wb") as f:
    f.write(response.content)
```

---

### 6. 语音识别 (Whisper)

**端点**: `POST /v1/audio/transcriptions`

```python
response = requests.post(
    "https://api.winfull.cloud-ip.cc/v1/audio/transcriptions",
    headers={"Authorization": "Bearer sk-xxx"},
    files={"file": open("audio.mp3", "rb")},
    data={"model": "whisper-1"}
)

result = response.json()
transcribed_text = result["text"]
```

---

### 7. Midjourney

**提交Imagine任务**: `POST /mj/submit/imagine`

```python
response = requests.post(
    "https://api.winfull.cloud-ip.cc/mj/submit/imagine",
    headers={
        "Authorization": "Bearer sk-xxx",
        "Content-Type": "application/json"
    },
    json={
        "prompt": "a beautiful sunset over the ocean --ar 16:9 --v 6"
    }
)

result = response.json()
task_id = result["result"]
```

---

## 📋 异步任务通用流程

大多数生成类API（视频、音乐、部分图像）都是异步的：

1. 创建任务 → 获取task_id
2. 轮询查询状态 (pending/processing)
3. 状态变为completed → 获取结果URL
4. 状态变为failed → 处理错误

**轮询建议**: 间隔5-10秒查询一次任务状态

---

## ⚠️ 重要注意事项

1. **认证方式**: 所有请求必须在Header中携带 `Authorization: Bearer sk-xxxxxxxx`
2. **图生视频流程**: 
   - 本地图片必须先上传到图床: `https://imageproxy.zhongzhuan.chat/api/upload`
   - 或使用已有的公网图片URL
   - 然后将URL传给视频生成接口的 `images` 参数
3. **异步轮询**: 视频/音乐生成需要轮询，间隔建议5-10秒
4. **Base URL**: 所有接口都以 `https://api.winfull.cloud-ip.cc` 开头
5. **速率限制**: 合理控制请求频率，避免触发限流
6. **Token计费**: 不同模型计费标准不同，详见官网

---

## 📖 详细文档参考

- **在线API文档**: https://winfull.apifox.cn/
- **完整接口列表**: 查看 `api_list.md` 文件
- **官网/Token管理**: https://api.winfull.cloud-ip.cc/

---

## ❓ 常见问题

### Q1: 如何获取API Token?
访问 https://api.winfull.cloud-ip.cc/ 注册账户，在控制台中申请API Token。

### Q2: 如何使用本地图片生成视频?
必须先将本地图片上传到图床：
```python
# 1. 上传图片到图床
with open("image.jpg", "rb") as f:
    upload_resp = requests.post(
        "https://imageproxy.zhongzhuan.chat/api/upload",
        headers={"Authorization": "Bearer sk-xxx"},
        files={"file": f}
    )
image_url = upload_resp.json()["url"]

# 2. 使用图片URL创建视频
video_resp = requests.post(
    "https://api.winfull.cloud-ip.cc/v1/video/create",
    headers={"Authorization": "Bearer sk-xxx", "Content-Type": "application/json"},
    json={"model": "sora-2", "prompt": "描述", "images": [image_url]}
)
```

### Q3: 可以直接使用公网图片URL吗?
可以！如果图片已经在公网上，可以直接使用URL，无需上传：
```python
image_url = "https://example.com/your-image.jpg"
# 直接使用这个URL创建视频
```

### Q4: 异步任务一直处于pending状态怎么办?
- 检查任务ID是否正确
- 等待更长时间（某些模型生成较慢）
- 查看账户余额是否充足
- 联系技术支持

### Q5: 视频生成需要多长时间?
根据模型和视频长度不同，通常需要1-10分钟。建议每5-10秒轮询一次任务状态。
