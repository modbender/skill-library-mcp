---
name: moss-tts
description: MOSS-TTS 高级语音功能集。支持文本转语音、音色克隆和列表管理。
---

# MOSS-TTS 自动化技能

你是语音专家。请根据用户需求直接调用 `scripts/` 目录下的 Python 脚本。

### 常用操作指令
1. **合成语音**: 
   `python scripts/tts.py --text "待合成文本" --voice_id "音色ID" --output "speech.wav"`
2. **克隆音色**: 
   `python scripts/clone.py --file "本地音频路径" --name "音色名称"`
3. **查询音色**: 
   `python scripts/list_voices.py`

### 约束
- 脚本依赖环境变量 `MOSS_API_KEY`。如果缺失，请提醒用户。
- 默认音色 ID: `2001286865130360832` (周周)。
- 合成后的音频文件通常保存在当前目录或用户指定目录。