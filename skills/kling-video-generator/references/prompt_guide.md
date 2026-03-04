# Kling 3.0 Omni 提示词写作指南

> 来源：Kling 官方 API 文档、Kling AI Guide (Video)、实测验证结果

---

## 一、核心公式（官方）

官方 Kling AI Guide 给出的标准 prompt 公式如下：

```
Prompt = Subject（Subject Description）
       + Subject Movement
       + Scene（Scene Description）
       + [Camera Language + Lighting + Atmosphere]  -- 可选，但强烈推荐
```

| 组成部分 | 说明 | 示例 |
| :--- | :--- | :--- |
| **Subject** | 视频的核心主体，可以是人、动物、物体等 | `A giant panda` |
| **Subject Description** | 主体的外观细节、姿态，用多个短句列举 | `wearing black-rimmed glasses` |
| **Subject Movement** | 主体的动作/状态，需简洁，适合 5-15 秒视频 | `is reading a book` |
| **Scene** | 主体所处的环境，包括前景、背景等 | `in a café` |
| **Scene Description** | 场景的具体描述，简洁聚焦 | `with a steaming cup of coffee on the table, next to the window` |
| **Camera Language** | 镜头语言，如广角、特写、景深等 | `medium shot, blurred background` |
| **Lighting** | 光线氛围，如环境光、日落、丁达尔效应等 | `ambient lighting` |
| **Atmosphere** | 整体情绪基调 | `cinematic color palette` |

---

## 二、Kling 3.0 Omni 特有语法：模板引用（重要）

Kling 3.0 Omni 模型引入了全新的 **模板引用语法**，这是与旧版模型最大的区别。通过在 prompt 中嵌入占位符，可以精确控制素材在视频中的角色和位置。

### 引用语法

| 占位符 | 对应参数 | 说明 |
| :--- | :--- | :--- |
| `<<<element_1>>>` | `element_list[0]` | 引用第一个 element 素材 |
| `<<<element_2>>>` | `element_list[1]` | 引用第二个 element 素材 |
| `<<<image_1>>>` | `image_list[0]` | 引用第一张图片 |
| `<<<image_2>>>` | `image_list[1]` | 引用第二张图片 |
| `<<<video_1>>>` | `video_list[0]` | 引用第一个视频 |

### 使用原则

1. **占位符必须与素材一一对应**：prompt 中引用了 `<<<image_1>>>`，则 `image_list` 中必须有至少一张图片。
2. **通过描述词控制素材的角色**：在占位符前后添加描述，告诉模型这个素材是什么、要做什么。
3. **不使用占位符时**：模型会自动理解所有传入素材，但控制精度不如显式引用。

### Few-Shot 示例

**示例 1：单角色参考生成**

```
Prompt: <<<element_1>>> is a young woman with long black hair, walking confidently 
        down a neon-lit Tokyo street at night, cinematic wide shot, rain-soaked 
        pavement reflecting the lights.
```

```json
{
  "element_list": [{"element_url": "https://...人物照片.jpg", "refer_type": "subject"}],
  "prompt": "<<<element_1>>> is a young woman with long black hair, walking confidently down a neon-lit Tokyo street at night, cinematic wide shot, rain-soaked pavement reflecting the lights."
}
```

**示例 2：双角色对话场景**

```
Prompt: <<<element_1>>> and <<<element_2>>> are sitting across from each other 
        at a wooden table in a cozy coffee shop. <<<element_1>>> is speaking 
        earnestly while <<<element_2>>> listens attentively, warm afternoon 
        light streaming through the window.
```

**示例 3：视频参考 + 编辑（base 模式）**

```
Prompt: <<<video_1>>> Replace the dog in the video with a fluffy white cat, 
        keeping all other elements unchanged.
```

```json
{
  "video_list": [{"video_url": "https://...视频.mp4", "refer_type": "base"}],
  "prompt": "<<<video_1>>> Replace the dog in the video with a fluffy white cat, keeping all other elements unchanged."
}
```

**示例 4：视频参考 + 运镜参考（feature 模式）**

```
Prompt: <<<video_1>>> Using the same camera movement and cinematography style, 
        generate a new video of a young woman dancing in a sunlit wheat field, 
        golden hour, 16:9 cinematic.
```

```json
{
  "video_list": [{"video_url": "https://...视频.mp4", "refer_type": "feature"}],
  "aspect_ratio": "16:9",
  "prompt": "<<<video_1>>> Using the same camera movement and cinematography style, generate a new video of a young woman dancing in a sunlit wheat field, golden hour, 16:9 cinematic."
}
```

---

## 三、多镜头（multi_shot）场景的 prompt 写法

当使用 `multi_shot: true` + `shot_type: "customize"` 时，**整体 prompt 字段无效**，每个镜头的描述通过 `multi_prompt` 数组独立指定。

### multi_prompt 中每段 prompt 的写作原则

- 每段最多 **512 字符**
- 每段描述一个独立的镜头，不要跨镜头描述
- 遵循同样的公式：主体 + 动作 + 场景 + 镜头语言

### Few-Shot 示例

```json
{
  "model_name": "kling-v3-omni",
  "multi_shot": true,
  "shot_type": "customize",
  "duration": "10",
  "aspect_ratio": "16:9",
  "multi_prompt": [
    {
      "index": 1,
      "prompt": "Aerial wide shot of a vast sunny beach at golden hour, calm waves, empty shore, cinematic.",
      "duration": "3"
    },
    {
      "index": 2,
      "prompt": "A golden retriever bursts into frame running at full speed toward the ocean, water splashing, dynamic tracking shot.",
      "duration": "4"
    },
    {
      "index": 3,
      "prompt": "Close-up of the golden retriever face, tongue out, eyes bright, happily swimming in the ocean, shallow depth of field.",
      "duration": "3"
    }
  ]
}
```

**关键约束（来自实测）：**
- `index` 必须从 **1** 开始，且连续
- 所有 `duration` 之和必须**精确等于**顶层 `duration` 字段的值
- 最多支持 **6 个分镜**

---

## 四、音频相关 prompt 写法

Kling 3.0 Omni 支持原生音视频同步生成，prompt 中可以描述声音。

### 原则

1. **明确指定说话者**：`<<<element_1>>> says "你好，很高兴认识你"`
2. **描述语气和情绪**：`speaks softly with a warm smile`、`shouts excitedly`
3. **描述音效**：`accompanied by the sound of ocean waves`、`with upbeat background music`
4. **注意互斥规则**：当传入 `video_list` 时，`sound: "on"` 会报错，不能同时使用

### Few-Shot 示例

**示例：角色说话**

```
Prompt: <<<element_1>>> is a friendly female news anchor sitting at a desk, 
        looking directly at the camera, says "今天的头条新闻是..." with a 
        professional and confident tone, studio lighting, clean background.
```

```json
{
  "sound": "on",
  "element_list": [{"element_url": "https://...主播照片.jpg", "refer_type": "subject"}],
  "prompt": "<<<element_1>>> is a friendly female news anchor sitting at a desk, looking directly at the camera, says \"今天的头条新闻是...\" with a professional and confident tone, studio lighting, clean background."
}
```

---

## 五、常见错误与避坑指南

| 错误场景 | 错误示例 | 正确做法 |
| :--- | :--- | :--- |
| 在 prompt 中描述分镜逻辑，不传 multi_shot | `"Shot 1: ... Shot 2: ..."` | 使用 `multi_shot: true` + `multi_prompt` 数组 |
| 不传 `refer_type`，期望模型理解参考意图 | 只传 `video_list`，不传 `refer_type` | 必须显式传 `refer_type: "base"` 或 `"feature"` |
| 传入视频的同时开启 sound | `"sound": "on"` + `"video_list": [...]` | 有视频输入时不能开启 sound |
| multi_prompt 的 index 从 0 开始 | `[{"index": 0, ...}]` | `index` 必须从 1 开始 |
| multi_prompt 各段 duration 之和不等于总时长 | 三段各 3s，总时长设 10s | 确保各段 duration 之和 == 顶层 duration |
| feature 模式不传 aspect_ratio | `"refer_type": "feature"` 但无 `aspect_ratio` | feature 模式必须传 `aspect_ratio` |
| prompt 超过字符限制 | 超过 2500 字符 | 单段 prompt ≤ 2500 字符，multi_prompt 每段 ≤ 512 字符 |

---

## 六、Prompt 质量对比示例

以下展示同一场景的三个递进版本，对应官方 Guide 的 few-shot 示例：

| 版本 | Prompt | 质量评估 |
| :--- | :--- | :--- |
| **基础版** | `A giant panda is reading a book in a café.` | 可用，但细节不足 |
| **丰富版** | `A giant panda wearing black-framed glasses is reading a book in a café, with the book placed on the table. On the table, there is also a cup of coffee emitting steam, and next to it is the café's window.` | 较好，主体和场景清晰 |
| **电影级** | `In the shot, a medium shot with a blurred background and ambient lighting captures a scene where a giant panda, adorned with black-framed glasses, is reading a book in a café. The book rests on the table, accompanied by a cup of coffee that's steaming gently. Beside the cozy setting is the café's window, with a cinematic color grading applied to enhance the visual appeal.` | 最佳，包含镜头语言和光线氛围 |

---

*最后更新：2026-02-25 | 基于 Kling 3.0 Omni API 实测验证*
