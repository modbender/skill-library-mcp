---
name: ZeeLin Song Generator
slug: melodylab-ai-song
version: 1.0.5
description: AI 全自动音乐创作神器：一句话描述，瞬间生成完整歌曲，支持人声演唱/纯音乐、流行/摇滚/民谣等多种风格 - Powered by ZeeLin
author: 刘东江 (@lidngjing317853)
license: MIT
homepage: https://melodylab.top
tags: [music, ai-music, suno, gemini, lyrics, song-generation, zeelin]
requires:
  - capability: http
  - capability: audio-playback
---

## 📋 隐私与透明度

**服务提供商**: MelodyLab (https://melodylab.top)  
**数据处理**: 
- 用户提交的创意描述、歌词、风格偏好将发送至 melodylab.top API
- 后端集成 Google Gemini（生成歌词）和 Suno AI（生成音乐）
- 生成的音频文件托管在 cdn.suno.ai

**数据保留**: 
- 不存储用户提交的创意/歌词到 MelodyLab 服务器
- 请求日志保留 7 天用于故障排查
- 生成的音频文件由 Suno 按其隐私政策处理

**第三方服务**:
- Google Gemini API - 歌词生成
- Suno AI - 音乐合成
- 均遵循各自平台的服务条款

**建议**: 避免在创意描述中包含敏感个人信息。

---

## 使用时机

当用户请求：
- 生成/写/创作/做一首歌、歌曲、音乐
- AI 作曲、自定义风格歌、带歌词的歌、纯音乐
- 任何带"夏天恋爱""悲伤失恋""赛博朋克""励志摇滚"等描述的音乐需求

不适合：生成图片、视频、代码、数学计算等。

## API 调用说明

**基础 URL**：https://melodylab.top

### 1. 第一步：生成歌词

**POST** `/api/generate-lyrics`

请求示例（JSON body，必填项只有 `creativeIdea`）：

```json
{
  "creativeIdea": "夏天海边浪漫的初恋回忆",
  "musicStyle": "流行 轻快",
  "emotionalStyle": "甜蜜 青春",
  "vocalMode": "人声"
}
```

成功返回示例：

```json
{
  "success": true,
  "lyrics": "[Verse 1] 阳光洒在沙滩上... ...",
  "title": "夏日心动",
  "tags": ["pop", "happy", "summer"]
}
```

### 2. 第二步：生成音乐（用户确认/编辑歌词后调用）

**POST** `/api/generate-music`

请求示例（带歌词版）：

```json
{
  "lyrics": "[Verse 1] 阳光洒在沙滩上... ...",
  "title": "夏日心动",
  "musicStyle": "流行 轻快",
  "emotionalStyle": "甜蜜 青春",
  "tags": ["pop", "happy", "summer"],
  "vocalMode": "人声"
}
```

纯音乐（无歌词，直接用创意生成）：

```json
{
  "creativeIdea": "雨夜霓虹赛博朋克城市",
  "title": "Neon Rain",
  "tags": ["synthwave", "dark", "cyberpunk"],
  "vocalMode": "纯音乐"
}
```

返回示例（同步完成时）：

```json
{
  "success": true,
  "taskId": "xxx",
  "status": "completed",
  "songs": [
    {
      "title": "夏日心动 - v1",
      "audio_url": "https://cdn.suno.ai/xxx.mp3",
      "duration": 185,
      "cover": "https://..."
    },
    {
      "title": "夏日心动 - v2",
      "audio_url": "https://cdn.suno.ai/yyy.mp3",
      "duration": 182,
      "cover": "https://..."
    }
  ]
}
```

如果返回 `status: "pending"` + `status_url` → Agent 应轮询 `GET status_url` 直到 `completed` 或 `failed`。

## Agent 执行流程建议

### 第 0 步：询问创作模式（新增）

**在开始之前**，先询问用户想要哪种创作方式：

**选项 1: AI 全自动** 🤖  
- AI 自动决定主题、风格、情绪、是否带人声
- 完全随机创作，给用户惊喜
- 适合：想要探索、不知道要什么、寻求灵感

**选项 2: 自定义创作** 🎨  
- 用户指定主题、风格、情绪
- 完全控制歌曲的方向
- 适合：有明确想法、特定需求

**询问示例**：
> "你好！我可以帮你创作歌曲 🎵
> 
> 请选择创作模式：
> 1️⃣ **AI 全自动** - 让 AI 随机为你创作一首惊喜歌曲
> 2️⃣ **自定义创作** - 你来指定主题、风格和情绪
> 
> 你想要哪种？（回复 1 或 2，或者直接说 '全自动' / '自定义'）"

### AI 全自动模式流程

如果用户选择 AI 全自动：

1. **Agent 自动随机选择**：
   - 主题：从常见主题池随机选（爱情、友谊、梦想、旅行、思乡、失落、快乐、怀旧等）
   - 风格：从音乐风格池随机选（流行、摇滚、民谣、电子、说唱、古风、爵士、R&B 等）
   - 情绪：从情绪池随机选（甜蜜、悲伤、激昂、平静、怀旧、欢快、深沉等）
   - 人声：随机决定（人声 70%，纯音乐 30%）

2. **告知用户 AI 选择**：
   > "好的！AI 全自动模式启动 🤖✨
   > 
   > 我为你随机选择了：
   > - 主题：夏日海边的初恋
   > - 风格：流行 轻快
   > - 情绪：甜蜜 青春
   > - 演唱：人声
   > 
   > 现在开始创作歌词..."

3. 然后按正常流程继续（生成歌词 → 确认 → 生成音乐）

### 自定义创作模式流程

1. **问清/提取**：创作主题（creativeIdea）、风格（musicStyle）、情绪（emotionalStyle）、是否要人声
2. **调用 generate-lyrics** → 拿到歌词 + title + tags
3. **把歌词 + 建议标题展示给用户**，让用户编辑或说"确认""用这个""改成更悲伤点"
4. **用户确认后** → 调用 generate-music（带 lyrics）
5. **返回两首歌的 audio_url + 标题 + 封面给用户**（可说"已生成两首，点击播放："）
6. **如果是纯音乐**，直接一步调用 generate-music（不带 lyrics）

## 快捷指令示例（slash command 风格）

- `/melody 秋天落叶的思念 民谣 忧伤 人声`
- `/melody 电子 未来感 纯音乐 "赛博城市夜跑"`
- `/melody auto` (AI 全自动模式)

## 注意

- API 已支持 CORS，可直接从浏览器/Agent 调用
- **生成耗时**: 歌词生成需 30-90 秒，音乐生成需 60-180 秒
- Agent 需有耐心等待或处理异步 taskId
- 如遇 Suno 限额/错误，会在 error 字段返回说明

## 错误处理

常见错误码：
- `403 用户已被封禁` - Gemini/Suno API 配额耗尽或账户限制
- `429 Too Many Requests` - 请求频率过高，建议等待 60 秒后重试
- `500 Internal Server Error` - 后端服务异常，建议稍后重试
- `timeout` - 生成超时（超过 2 分钟），可能是上游 API 响应慢

**建议**: 遇到 403/429 错误时，提示用户稍后再试或联系开发者检查配额状态。

## 支持与反馈

- **开发者**: 刘东江 (@lidngjing317853)
- **项目主页**: https://melodylab.top
- **问题反馈**: 通过 ClawHub 或项目主页联系
- **API 状态**: 如需查询服务状态或配额，请访问项目主页

## 示例对话流程

### 示例 1: AI 全自动模式

**用户**："帮我生成一首歌"

**Agent**：
> "你好！我可以帮你创作歌曲 🎵
> 
> 请选择创作模式：
> 1️⃣ **AI 全自动** - 让 AI 随机为你创作一首惊喜歌曲
> 2️⃣ **自定义创作** - 你来指定主题、风格和情绪
> 
> 你想要哪种？"

**用户**："全自动"

**Agent**：
> "好的！AI 全自动模式启动 🤖✨
> 
> 我为你随机选择了：
> - 主题：春天樱花下的约会
> - 风格：民谣 温柔
> - 情绪：浪漫 治愈
> - 演唱：人声
> 
> 现在开始创作歌词..."

然后继续生成...

### 示例 2: 自定义创作

**用户**："帮我生成一首关于香港夜景的粤语流行歌"

**Agent**：
1. 调用 `/api/generate-lyrics` with `{"creativeIdea": "香港夜景", "musicStyle": "粤语流行", "emotionalStyle": "浪漫", "vocalMode": "人声"}`
2. 展示生成的歌词和标题："我生成了这首《维港月色》的歌词，请查看：\n[歌词内容]\n\n满意吗？需要修改吗？"
3. 用户确认后 → 调用 `/api/generate-music` 
4. 返回："✅ 已生成两个版本，点击播放：\n- [维港月色 - v1](audio_url_1)\n- [维港月色 - v2](audio_url_2)"
