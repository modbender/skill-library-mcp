# Qwen3-ASR 语音识别服务

## 基本信息

| 项目 | 值 |
|------|-----|
| 模型 | `mlx-community/Qwen3-ASR-1.7B-8bit` |
| 服务进程 | `mlx_audio.server` |
| 监听地址 | `127.0.0.1:8788`（仅本机访问） |
| 协议 | OpenAI-compatible API |
| 运行环境 | `~/.mlx-server/venv/` |
| 启动脚本 | `~/.mlx-server/start-mlx-audio-server.sh` |
| launchd 服务 | `com.mlx-audio-server` |

## API 调用

### 转录音频

```bash
curl -X POST http://127.0.0.1:8788/v1/audio/transcriptions \
  -F "file=@audio.wav" \
  -F "model=mlx-community/Qwen3-ASR-1.7B-8bit" \
  -F "language=zh"
```

### 响应格式

```json
{
  "text": "转录出的文本内容"
}
```

### Python 调用示例

```python
import httpx

ASR_API = "http://127.0.0.1:8788/v1"
ASR_MODEL = "mlx-community/Qwen3-ASR-1.7B-8bit"

with open("audio.wav", "rb") as f:
    response = httpx.post(
        f"{ASR_API}/audio/transcriptions",
        files={"file": ("audio.wav", f, "audio/wav")},
        data={"model": ASR_MODEL, "language": "zh"},
        timeout=600.0
    )
    print(response.json()["text"])
```

## 支持的音频格式

wav, mp3, m4a, flac, ogg, webm

## 特点

- 擅长普通话和粤语识别
- 支持中英混合语音
- 8bit 量化，内存占用约 2.3GB
- 模型按需加载，首次调用会有加载延迟

## 卸载模型（释放内存）

```bash
curl -X DELETE "http://127.0.0.1:8788/models?model_name=mlx-community/Qwen3-ASR-1.7B-8bit"
```

## 管理命令

```bash
# 启动服务
launchctl kickstart gui/$(id -u)/com.mlx-audio-server

# 停止服务
launchctl kill SIGTERM gui/$(id -u)/com.mlx-audio-server

# 查看状态
launchctl print gui/$(id -u)/com.mlx-audio-server

# 查看日志
tail -f ~/.mlx-server/logs/mlx-audio-server.err.log
```

## 注意事项

- 此服务绑定 `127.0.0.1`，仅限本机调用，局域网设备无法直接访问
- 端口 8788 与 Whisper UI（Gradio）共用，可能存在冲突
- 长音频建议先用 ffmpeg 切分为 10 分钟片段再逐段调用
