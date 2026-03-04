# Whisper 语音识别服务

## 基本信息

| 项目 | 值 |
|------|-----|
| 模型 | `mlx-community/whisper-large-v3-turbo` |
| 模型 ID | `whisper-large-v3-turbo` |
| 服务进程 | `mlx-openai-server` |
| 监听地址 | `0.0.0.0:8787` |
| 本机地址 | `http://localhost:8787` |
| 协议 | OpenAI-compatible API |
| launchd 服务 | `com.mlx-server` |

## API 调用

### 转录音频

```bash
curl -X POST http://localhost:8787/v1/audio/transcriptions \
  -F "file=@audio.wav" \
  -F "model=whisper-large-v3-turbo"
```

### 响应格式

```json
{
  "text": "转录出的文本内容"
}
```

### Python 调用示例（OpenAI SDK）

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8787/v1", api_key="unused")

with open("audio.wav", "rb") as f:
    transcription = client.audio.transcriptions.create(
        model="whisper-large-v3-turbo",
        file=f
    )
    print(transcription.text)
```

## 与 Qwen3-ASR 的区别

| | Whisper | Qwen3-ASR |
|---|---|---|
| 端口 | 8787（局域网可访问） | 8788（仅本机） |
| 多语言 | 支持 99 种语言 | 中英为主 |
| 粤语能力 | 一般 | 较强 |
| 加载方式 | 随主服务常驻 | 按需加载 |

## Whisper Web UI

另有 Gradio 网页界面可用于手动上传转录：

| 项目 | 值 |
|------|-----|
| 地址 | `http://localhost:8788` |
| launchd 服务 | `com.mlx-whisper-ui` |
| 功能 | 上传音频 → Whisper 转录 → Qwen3-14B 校对 |

## 管理命令

Whisper 模型挂载在主 LLM 服务下，管理命令见 `llm-qwen3-14b.md` 中的服务管理部分。
