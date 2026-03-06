---
name: MiniMax 多人对话语音合成
description: 根据用户需求生成多人对话，为每个角色匹配音色进行语音合成，输出完整长音频和分段音频，并生成 HTML 展示页面。
category: audio
tags: [语音合成, TTS, 多人对话, MiniMax, 海螺]
featured: true
---

# MiniMax 多人对话语音合成

根据用户需求生成多人对话剧本，智能匹配角色音色，合成完整音频和分段音频，最终生成精美的 HTML 展示页面。

## 工作流

### 1. 分析用户需求

获取用户想要生成的对话主题或场景：
- 对话场景（商务会议/日常聊天/故事情节/采访/辩论等）
- 参与角色数量和特点
- 对话风格（正式/轻松/幽默/严肃等）
- 对话长度（简短/中等/详细）

### 2. 生成对话剧本

根据用户需求，创作一段自然流畅的多人对话。格式要求：

```json
{
  "title": "对话标题",
  "scene": "场景描述",
  "characters": [
    {
      "id": "A",
      "name": "角色名称",
      "gender": "male/female",
      "age": "child/young/middle/elder",
      "personality": "性格特点描述"
    }
  ],
  "dialogues": [
    {
      "speaker_id": "A",
      "speaker_name": "角色名",
      "text": "对话内容",
      "emotion": "情绪标签"
    }
  ]
}
```

#### 对话生成规则

1. **角色塑造**：每个角色应有鲜明的个性和说话方式
2. **自然流畅**：对话要符合真实交流习惯，有互动和回应
3. **情感丰富**：根据内容添加适当的情绪表达
4. **长度适中**：每段对话控制在 20-100 字为宜

### 3. 智能匹配音色

调用 MCP 工具获取可用音色，然后根据角色特点匹配：

```json
{
  "server": "user-速推AI",
  "toolName": "list_voices",
  "arguments": {}
}
```

> **参考文档**：详细的音色匹配规则见 [references/voice-mapping.md](references/voice-mapping.md)

使用 AskQuestion 让用户确认或调整音色匹配：

```
请确认角色音色匹配：

角色 A (小明 - 年轻男学生):
  推荐: male-qn-daxuesheng (青年大学生音色)
  
角色 B (李总 - 成熟商务男):
  推荐: male-qn-jingying (精英青年音色)

是否确认？或选择调整某个角色的音色。
```

### 4. 文本预处理 - 添加语气词

使用 `speech-2.8-hd` 模型时，根据情绪标签智能添加语气词增强情感表达。

> **参考文档**：语气词使用规则见 [references/emotion-tags.md](references/emotion-tags.md)

**预处理示例**：

原文：
```
小明：今天考试终于结束了！太开心了！
```

处理后：
```
小明：今天考试终于结束了(breath)！太开心了(laughs)！
```

### 5. 分段语音合成

为每段对话调用语音合成：

```json
{
  "server": "user-速推AI",
  "toolName": "text_to_audio",
  "arguments": {
    "text": "处理后的对话文本（含语气词）",
    "voice_id": "该角色的音色ID",
    "model": "speech-2.8-hd",
    "output_format": "url",
    "language_boost": "Chinese"
  }
}
```

> **参考文档**：MCP 工具详细参数见 [references/mcp-tools.md](references/mcp-tools.md)

#### 合成流程

1. 遍历所有对话段落
2. 根据 `speaker_id` 获取对应音色
3. 调用 `text_to_audio` 合成每段音频
4. 记录每段音频的 URL 和时长信息

### 6. 生成完整长音频

将所有分段音频合并为一个完整的长音频。有两种方式：

#### 方式一：使用合并脚本（推荐）

使用 `scripts/merge_audio.py` 脚本将所有分段音频合并成一个完整的长音频文件。

**依赖安装**：
```bash
pip install pydub requests
# macOS 安装 FFmpeg
brew install ffmpeg
```

**基本用法**：
```bash
# 从 dialogue.json 读取 URL 并合并
python scripts/merge_audio.py --input dialogue_output/dialogue.json --output dialogue_output/merged.mp3

# 自定义音频间隔（毫秒）
python scripts/merge_audio.py -i dialogue.json -o merged.mp3 --gap 500

# 保留分段音频文件
python scripts/merge_audio.py -i dialogue.json -o merged.mp3 --keep-segments --segments-dir ./segments
```

> **脚本文件**：[scripts/merge_audio.py](scripts/merge_audio.py)

#### 方式二：顺序播放

在 HTML 页面中实现自动顺序播放功能，模拟长音频效果（无需额外处理）。

### 7. 生成 HTML 展示页面

使用模板生成精美的 HTML 展示页面。

> **模板文件**：[assets/dialogue-template.html](assets/dialogue-template.html)

将对话数据和音频 URL 填充到模板中的占位符：
- `{{title}}` - 对话标题
- `{{scene}}` - 场景描述
- `{{characters}}` - 角色列表
- `{{dialogues}}` - 对话列表（含音频 URL）

### 8. 输出文件

生成以下文件：

```
dialogue_output/
├── dialogue.html          # 完整展示页面
├── dialogue.json          # 对话数据（含音频 URL）
├── merged.mp3             # 合并后的完整长音频
└── segments/              # 分段音频（可选）
    ├── 001_角色A.mp3
    ├── 002_角色B.mp3
    └── ...
```

**生成长音频**：
```bash
cd /Users/m007/codes/translate_api/.cursor/skills/minimax-tts
python scripts/merge_audio.py -i ../../../dialogue_output/dialogue.json -o ../../../dialogue_output/merged.mp3
```

## 完整示例

### 用户请求

> 帮我生成一段两个人讨论今天天气的对话，一男一女

### 执行步骤

**1. 生成对话剧本**

```json
{
  "title": "关于天气的闲聊",
  "scene": "办公室午休时间，两位同事在茶水间偶遇",
  "characters": [
    { "id": "A", "name": "小明", "gender": "male", "age": "young", "personality": "阳光开朗" },
    { "id": "B", "name": "小红", "gender": "female", "age": "young", "personality": "温柔细心" }
  ],
  "dialogues": [
    { "speaker_id": "A", "speaker_name": "小明", "text": "小红，你看今天天气多好啊！阳光明媚的。", "emotion": "开心" },
    { "speaker_id": "B", "speaker_name": "小红", "text": "是啊，难得这么好的天气。不过听说下午可能会下雨呢。", "emotion": "平和" },
    { "speaker_id": "A", "speaker_name": "小明", "text": "真的吗？那我得赶紧把晒的衣服收回去了！", "emotion": "惊讶" },
    { "speaker_id": "B", "speaker_name": "小红", "text": "哈哈，你还挺细心的嘛。记得带伞哦。", "emotion": "愉悦" }
  ]
}
```

**2. 匹配音色**

| 角色 | 音色 ID | 音色名称 |
|-----|--------|---------|
| 小明 | `male-qn-qingse` | 青涩青年音色 |
| 小红 | `female-shaonv` | 少女音色 |

**3. 合成音频** → 为每段对话调用 `text_to_audio`

**4. 生成 HTML** → 填充模板，输出 `dialogue.html`

**5. 输出结果**

```
对话音频已生成！

📁 输出文件：
- dialogue.html - 展示页面（用浏览器打开）
- dialogue.json - 对话数据

🎭 角色音色：
- 小明: male-qn-qingse (青涩青年音色)
- 小红: female-shaonv (少女音色)

🎵 音频数量：4 段
⏱️ 预计总时长：约 30 秒

💡 提示：在浏览器中打开 dialogue.html 即可播放
```

## 注意事项

1. **音色一致性**：同一角色在整个对话中使用相同音色
2. **情绪连贯性**：相邻对话的情绪过渡要自然
3. **文本长度**：单段对话建议 20-100 字，过长可拆分
4. **语气词适度**：每段对话 1-2 个语气词为宜
5. **计费说明**：每 1000 字符 1 积分，每段对话独立计费
