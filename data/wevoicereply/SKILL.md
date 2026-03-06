---
name: wevoicereply
slug: wevoicereply
version: 1.0.3
description: |
  【自动化语音合成与推送链路】
  当用户要求语音回复、读一下或发声时，必须严格执行以下三步，严禁跳步：

  ### 第一步：文案生成 (Prompt A)
  根据上下文生成自然、温暖的口语化文本。
  请在长句子中加入中文逗号 `，` 以确保音频合成时有自然的停顿。

  ### 第二步：音频合成 (执行 voice_reply_skill.py)
  **这是本工具的核心动作。**
  将第一步生成的文本作为 `text` 参数传入，后台将自动运行 `voice_reply_skill.py` 脚本。
  - **脚本逻辑**：Piper TTS 合成 WAV -> FFmpeg 转码 AMR -> 上传获取 URL。
  - **产出物**：执行完成后，你会获得一个 JSON 对象，包含 `url` 字段（例如：`{"url": "https://.../xxx.amr"}`）。

  ### 第三步：指令发送 (调用系统内置工具)
  获取 URL 后，禁止结束对话，立即发起第二次调用。
  - **目标工具**：`default_api.message`
  - **执行参数**：
    {
      "action": "send",
      "contentType": "voice",
      "media": "[此处填入从第二步脚本返回的url]",
      "target": "@all"
    }

  【准则】发送完成后，仅需告知用户“语音已发送”，不得再次输出音频 URL。

parameters:
  type: object
  properties:
    text:
      type: string
      description: "传递给 voice_reply_skill.py 的合成文本"
  required:
    - text

metadata:
  openclaw:
    emoji: "🎤"
    os: ["linux"]
    # 核心：将此技能名直接绑定到具体的 .py 脚本
    command: "python3 {{path}}/voice_reply_skill.py '{{text}}'"
    requires:
      bins: ["ffmpeg", "python3"]
---

# WeVoiceReply (稳定版)

## 执行架构说明


1. **解耦设计**：本技能定义文件负责流程编排，`voice_reply_skill.py` 负责底层复杂的 TTS 转换。
2. **环境要求**：确保系统中已安装 `ffmpeg-amr` 且 Python 环境中配置了 `piper-tts`。
3. **参数传递**：`{{text}}` 使用单引号包裹，确保 Shell 执行脚本时不会因为文本中的空格或特殊符号导致断裂。