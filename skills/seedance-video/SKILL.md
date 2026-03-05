---
name: Seedance 视频生成
description: 使用 Bytedance Seedance 模型生成视频。支持文生视频（带音频）、图生视频、参考图生视频。当用户想要生成视频、使用图片生成视频、保持人物一致性、或提到 seedance 时使用此 skill。
category: video
tags: [视频生成, 文生视频, 图生视频, 参考图, Seedance, Bytedance, 人物一致性, 首帧图, 音频生成]
featured: true
---

# Seedance 视频生成

Bytedance Seedance 是一系列先进的视频生成模型，支持文生视频（带音频）和图生视频。

## 可用模型

| 模型 ID | 功能 | 分辨率 | 说明 |
|--------|------|--------|------|
| `fal-ai/bytedance/seedance/v1.5/pro/text-to-video` | 文生视频 | 480p/720p/1080p | **新** 支持音频生成（对话+音效+背景音乐），唇形同步 |
| `fal-ai/bytedance/seedance/v1.5/pro/image-to-video` | 首帧图生视频 | 480p/720p | **新** 支持音频生成（对话+音效），首尾帧，唇形同步 |
| `fal-ai/bytedance/seedance/v1/pro/fast/image-to-video` | 首帧图生视频 | 480p/720p/1080p | **推荐** 以图片为首帧生成视频，高性能低成本 |
| `fal-ai/bytedance/seedance/v1/lite/image-to-video` | 首帧图生视频 | 480p/720p/1080p | 支持首尾帧视频，画质更优 |
| `fal-ai/bytedance/seedance/v1/lite/reference-to-video` | 参考图生视频 | 480p/720p | 使用 1-4 张参考图生成视频，人物一致性更强 |

## 计费方式（按秒计费）

### v1.5 Pro T2V 文生视频（带音频）

| 分辨率 | 单价（带音频） | 单价（不带音频） | 5秒带音频 | 10秒带音频 |
|--------|---------------|-----------------|----------|-----------|
| 480p | 10积分/秒 | 5积分/秒 | 50 | 100 |
| 720p | 21积分/秒 | 11积分/秒 | 105 | 210 |
| 1080p | 47积分/秒 | 24积分/秒 | 235 | 470 |

### v1.5 Pro I2V 图生视频（带音频）

| 分辨率 | 单价（带音频） | 单价（不带音频） | 5秒带音频 | 10秒带音频 |
|--------|---------------|-----------------|----------|-----------|
| 480p | 10积分/秒 | 5积分/秒 | 50 | 100 |
| 720p | 21积分/秒 | 10积分/秒 | 105 | 210 |

> 设置 `generate_audio: false` 可关闭音频生成，价格减半

### Pro Fast 系列（Image-to-Video / Text-to-Video）

| 分辨率 | 单价 | 5秒 | 10秒 | 12秒 |
|--------|------|-----|------|------|
| 480p | 5积分/秒 | 25 | 50 | 60 |
| 720p | 10积分/秒 | 50 | 100 | 120 |
| 1080p | 20积分/秒 | 100 | 200 | 240 |

### Lite Image-to-Video / Text-to-Video

| 分辨率 | 单价 | 5秒 | 10秒 | 12秒 |
|--------|------|-----|------|------|
| 480p | 8积分/秒 | 40 | 80 | 96 |
| 720p | 15积分/秒 | 75 | 150 | 180 |
| 1080p | 35积分/秒 | 175 | 350 | 420 |

### Lite Reference-to-Video

| 分辨率 | 单价 | 5秒 | 10秒 | 12秒 |
|--------|------|-----|------|------|
| 480p | 8积分/秒 | 40 | 80 | 96 |
| 720p | 15积分/秒 | 75 | 150 | 180 |

---

## v1.5 Pro Text-to-Video（带音频）

Seedance 1.5 Pro 文生视频可以生成**带音频的视频**，包括对话、音效和背景音乐。支持**唇形同步**，非常适合创建说话的角色视频、广告片、短剧等。

### 核心特性

- **原生音频生成**：对话、音效、环境音、背景音乐同步渲染
- **唇形同步**：角色说话时唇形自动匹配
- **电影级摄像机**：支持推拉摇移跟等各种运镜
- **高分辨率支持**：支持 480p/720p/1080p

### 调用示例

```json
{
  "model_id": "fal-ai/bytedance/seedance/v1.5/pro/text-to-video",
  "parameters": {
    "prompt": "Defense attorney declaring \"Ladies and gentlemen, reasonable doubt isn't just a phrase, it's the foundation of justice itself\", footsteps on marble, jury shifting, courtroom drama, closing argument power.",
    "resolution": "720p",
    "duration": "5",
    "generate_audio": true
  }
}
```

### 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|-----|-------|------|
| prompt | string | **是** | - | 视频生成提示词，对话用引号包裹 |
| aspect_ratio | string | 否 | "16:9" | 宽高比：21:9/16:9/4:3/1:1/3:4/9:16 |
| resolution | string | 否 | "720p" | 分辨率：480p（快速）/ 720p（最终输出）/ 1080p（高质量） |
| duration | string | 否 | "5" | 视频时长：4-12 秒 |
| generate_audio | boolean | 否 | true | 是否生成音频（关闭后价格减半） |
| camera_fixed | boolean | 否 | false | 是否固定摄像机位置（三脚架模式） |
| seed | integer | 否 | - | 随机种子，使用 -1 表示随机 |

### 提示词技巧（v1.5 Pro 特有）

像写镜头描述一样写提示词：

| 元素 | 示例 |
|------|------|
| **场景** | "Rainy Tokyo alley at night, neon reflections on wet pavement" |
| **动作** | "A woman in a trench coat turns and walks toward camera" |
| **对话** | `"I told you — we don't have much time."` (用引号包裹) |
| **镜头** | "Slow dolly-in ending on a close-up" |
| **音效** | "Rain on metal, distant traffic, her heels on concrete" |

> **提示**：
> - 对话用引号包裹并描述情绪：`"I can't believe it," voice breaking with emotion`
> - 描述环境音效：room reverb, crowd murmur, wind through trees
> - 每个片段保持 1-2 个角色和一个场景效果最佳

---

## v1.5 Pro Image-to-Video（带音频）

Seedance 1.5 Pro 可以生成**带音频的视频**，包括对话、音效和环境音。支持**唇形同步**，非常适合创建说话的角色视频。

### 核心特性

- **原生音频生成**：对话、音效、环境音同步渲染
- **唇形同步**：角色说话时唇形自动匹配
- **首尾帧控制**：可同时指定开始和结束画面
- **电影级摄像机**：支持推拉摇移跟等各种运镜

### 调用示例

```json
{
  "model_id": "fal-ai/bytedance/seedance/v1.5/pro/image-to-video",
  "parameters": {
    "prompt": "A man is crying and he says \"I shouldn't have done it. I regret everything\"",
    "image_url": "https://cdn-video.51sux.com/seedance-examples/20260204/seedance_15_pro_i2v.png",
    "resolution": "720p",
    "duration": "5",
    "generate_audio": true
  }
}
```

### 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|-----|-------|------|
| prompt | string | **是** | - | 视频生成提示词，对话用引号包裹 |
| image_url | string | **是** | - | 首帧图片 URL |
| end_image_url | string | 否 | - | 尾帧图片 URL，模型会生成两帧之间的运动 |
| aspect_ratio | string | 否 | "16:9" | 宽高比：21:9/16:9/4:3/1:1/3:4/9:16 |
| resolution | string | 否 | "720p" | 分辨率：480p（更快）/ 720p（最终输出） |
| duration | string | 否 | "5" | 视频时长：4-12 秒 |
| generate_audio | boolean | 否 | true | 是否生成音频（关闭后价格减半） |
| camera_fixed | boolean | 否 | false | 是否固定摄像机位置（三脚架模式） |
| seed | integer | 否 | - | 随机种子，使用 -1 表示随机 |

### 提示词技巧（v1.5 Pro 特有）

| 元素 | 示例 |
|------|------|
| **动作** | "She turns to face the camera and smiles" |
| **对话** | `"I've been waiting for this moment."` (用引号包裹) |
| **镜头** | "Slow push-in ending on a close-up" |
| **音效** | "Soft piano, room reverb, fabric rustling" |

> 首帧已定义场景，提示词应聚焦于**动作**和**声音**
> 说话角色请将对话用引号包裹并描述情绪：`"I can't believe it," voice breaking with emotion`

---

## Pro Fast Image-to-Video（推荐）

以图片为首帧生成视频，高性能低成本，支持高达 1080p 分辨率。

### 调用示例

```json
{
  "model_id": "fal-ai/bytedance/seedance/v1/pro/fast/image-to-video",
  "parameters": {
    "prompt": "Bathed in a stark spotlight, a lone ballet dancer takes center stage. Her movements, precise and graceful, tell a story of passion and dedication against the velvet darkness.",
    "image_url": "https://cdn-video.51sux.com/seedance-examples/20260204/seedance_fast_i2v_input.png",
    "resolution": "1080p",
    "duration": "5"
  }
}
```

### 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|-----|-------|------|
| prompt | string | **是** | - | 视频生成提示词，描述视频中的动作和场景 |
| image_url | string | **是** | - | 首帧图片 URL |
| aspect_ratio | string | 否 | "auto" | 宽高比：21:9/16:9/4:3/1:1/3:4/9:16/auto |
| resolution | string | 否 | "1080p" | 分辨率：480p（更快）/ 720p（平衡）/ 1080p（高质量） |
| duration | string | 否 | "5" | 视频时长：2-12 秒 |
| camera_fixed | boolean | 否 | false | 是否固定摄像机位置 |
| seed | integer | 否 | - | 随机种子，使用 -1 表示随机 |
| enable_safety_checker | boolean | 否 | true | 是否启用安全检查 |

---

## Lite Image-to-Video

以图片为首帧生成视频，支持 1080p 高分辨率，支持首尾帧视频生成。画质比 Pro Fast 更优。

### 调用示例

```json
{
  "model_id": "fal-ai/bytedance/seedance/v1/lite/image-to-video",
  "parameters": {
    "prompt": "A little dog is running in the sunshine. The camera follows the dog as it plays in a garden.",
    "image_url": "https://cdn-video.51sux.com/seedance-examples/20260204/seedance_lite_i2v_input.png",
    "resolution": "720p",
    "duration": "5"
  }
}
```

### 首尾帧视频示例

```json
{
  "model_id": "fal-ai/bytedance/seedance/v1/lite/image-to-video",
  "parameters": {
    "prompt": "The scene transitions smoothly from the first frame to the last frame",
    "image_url": "https://example.com/first-frame.png",
    "end_image_url": "https://example.com/last-frame.png",
    "resolution": "720p",
    "duration": "5"
  }
}
```

### 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|-----|-------|------|
| prompt | string | **是** | - | 视频生成提示词，描述视频中的动作和场景 |
| image_url | string | **是** | - | 首帧图片 URL |
| end_image_url | string | 否 | - | 尾帧图片 URL，提供时生成首尾帧视频 |
| aspect_ratio | string | 否 | "auto" | 宽高比：21:9/16:9/4:3/1:1/3:4/9:16/auto |
| resolution | string | 否 | "720p" | 分辨率：480p（更快）/ 720p（平衡）/ 1080p（高质量） |
| duration | string | 否 | "5" | 视频时长：2-12 秒 |
| camera_fixed | boolean | 否 | false | 是否固定摄像机位置 |
| seed | integer | 否 | - | 随机种子，使用 -1 表示随机 |
| enable_safety_checker | boolean | 否 | true | 是否启用安全检查 |

---

## Lite Reference-to-Video

使用 1-4 张参考图片创建视频，参考图中的人物、物体等元素会出现在生成的视频中，非常适合保持人物或主体一致性的视频创作。

### 调用示例

```json
{
  "model_id": "fal-ai/bytedance/seedance/v1/lite/reference-to-video",
  "parameters": {
    "prompt": "The girl catches the puppy and hugs it.",
    "reference_image_urls": [
      "https://cdn-video.51sux.com/seedance-examples/20260204/seedance_reference.jpeg",
      "https://cdn-video.51sux.com/seedance-examples/20260204/seedance_reference_2.jpeg"
    ],
    "resolution": "720p",
    "duration": "5"
  }
}
```

### 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|-----|-------|------|
| prompt | string | **是** | - | 视频生成提示词，描述视频中的动作和场景 |
| reference_image_urls | array | **是** | - | 参考图片 URL 列表（1-4 张） |
| aspect_ratio | string | 否 | "auto" | 宽高比：21:9/16:9/4:3/1:1/3:4/9:16/auto |
| resolution | string | 否 | "720p" | 分辨率：480p（更快）/ 720p（更高质量） |
| duration | string | 否 | "5" | 视频时长：2-12 秒 |
| camera_fixed | boolean | 否 | false | 是否固定摄像机位置 |
| seed | integer | 否 | - | 随机种子，使用 -1 表示随机 |
| enable_safety_checker | boolean | 否 | true | 是否启用安全检查 |

---

## 查询任务状态

提交任务后会返回 `task_id`，使用 `get_task` 查询结果：

```json
{
  "task_id": "返回的任务ID"
}
```

任务状态：
- `pending` - 排队中
- `processing` - 处理中
- `completed` - 完成，结果在 `result` 中
- `failed` - 失败，查看 `error` 字段

## 提示词技巧

1. **描述动作**：明确描述主体的动作（抱、走、跑、跳、转身、微笑等）
2. **描述场景**：可以添加场景描述（在花园里、在海边、在城市街道）
3. **描述情感**：添加情感描述（开心地、温柔地、兴奋地）
4. **使用英文**：建议使用英文提示词以获得更好的效果
5. **光影描述**：添加光影描述（soft lighting, cinematic, spotlight）

### 提示词示例

**芭蕾舞者**：
```
Bathed in a stark spotlight, a lone ballet dancer takes center stage. 
Her movements, precise and graceful, tell a story of passion and dedication 
against the velvet darkness.
```

**人物互动**（参考图生视频）：
```
The girl catches the puppy and hugs it tightly, both looking happy, 
soft lighting, natural movement
```

## 模型选择建议

| 场景 | 推荐模型 | 原因 |
|------|---------|------|
| **纯文字创作带音频** | v1.5 Pro T2V | 无需图片，支持对话、音效、背景音乐 |
| **带音频/对话** | v1.5 Pro T2V/I2V | 支持对话、音效、唇形同步 |
| **说话角色** | v1.5 Pro T2V/I2V | 原生唇形同步，对话自然 |
| **短剧/广告** | v1.5 Pro T2V 1080p | 高质量+音频，适合成品输出 |
| 一般图生视频 | Pro Fast I2V | 高性能、低成本、支持 1080p |
| 首尾帧视频 | Lite I2V 或 v1.5 Pro I2V | 两者都支持 end_image_url |
| 追求画质 | Lite I2V 1080p | 画质比 Pro Fast 更优 |
| 保持人物一致性 | Lite R2V | 参考图中的人物会出现在视频中 |
| 多角色互动 | Lite R2V | 支持 1-4 张参考图，可组合多个角色 |
| 快速原型测试 | Pro Fast I2V 480p | 成本最低（5积分/秒） |
| 高质量成品 | v1.5 Pro T2V 1080p | 最高画质+音频 |
| 静音视频 | v1.5 Pro (generate_audio=false) | 关闭音频后价格减半 |

## 注意事项

1. **图片质量**：使用高清、主体清晰的图片效果更好
2. **时长选择**：2-12 秒可选，较长的视频需要更多生成时间
3. **摄像机固定**：设置 `camera_fixed: true` 可以让摄像机位置保持不变
4. **组合使用**：可以先用即梦/Flux 生成参考图，再用 Seedance 生成视频
