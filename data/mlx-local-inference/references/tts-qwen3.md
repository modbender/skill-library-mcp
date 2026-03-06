# Qwen3-TTS 语音合成（未启用）

## 基本信息

| 项目 | 值 |
|------|-----|
| 模型 | `mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit` |
| 状态 | 已下载，未部署服务 |
| 缓存路径 | `~/.cache/huggingface/hub/models--mlx-community--Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit/` |

## 当前状态

模型权重已缓存在本机，但未配置到任何运行中的服务。如需启用，可通过 `mlx-audio` 加载：

### 命令行调用

```bash
~/.mlx-server/venv/bin/mlx_audio.tts.generate \
  --model mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit \
  --text "你好，这是一段测试语音"
```

### Python 调用

```python
from mlx_audio.tts import generate

generate(
    model="mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit",
    text="你好，这是一段测试语音"
)
```

### 如需作为 API 服务运行

可通过 `mlx_audio.server` 提供 TTS 能力，目前该服务仅配置了 ASR，如需同时提供 TTS 需调整启动参数。

## 备注

此模型为 CustomVoice 版本，支持自定义音色克隆。8bit 量化，内存占用约 2GB。
