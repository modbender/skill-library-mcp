# Qwen3-14B 本地推理服务

## 基本信息

| 项目 | 值 |
|------|-----|
| 模型 | `Qwen/Qwen3-14B-MLX-4bit` |
| 模型 ID | `qwen3-14b` |
| 参数量 | 14B（4bit 量化） |
| 服务进程 | `mlx-openai-server` |
| 监听地址 | `0.0.0.0:8787` |
| 本机地址 | `http://localhost:8787` |
| 协议 | OpenAI-compatible API |
| 最大并发 | 2 |
| Prompt 缓存 | 10 条 |
| launchd 服务 | `com.mlx-server` |
| 配置文件 | `~/.mlx-server/config.yaml` |

## API 调用

### Chat Completions

```bash
curl -X POST http://localhost:8787/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-14b",
    "messages": [
      {"role": "system", "content": "你是一个有帮助的助手。"},
      {"role": "user", "content": "你好"}
    ],
    "temperature": 0.7,
    "max_tokens": 2048
  }'
```

### 流式输出

```bash
curl -X POST http://localhost:8787/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-14b",
    "messages": [{"role": "user", "content": "写一首诗"}],
    "stream": true
  }'
```

### Python 调用示例（OpenAI SDK）

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8787/v1", api_key="unused")

# 普通调用
response = client.chat.completions.create(
    model="qwen3-14b",
    messages=[
        {"role": "system", "content": "你是一个有帮助的助手。"},
        {"role": "user", "content": "解释量子计算"}
    ],
    temperature=0.7,
    max_tokens=2048
)
print(response.choices[0].message.content)

# 流式调用
stream = client.chat.completions.create(
    model="qwen3-14b",
    messages=[{"role": "user", "content": "写一首诗"}],
    stream=True
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## 模型特点

- Qwen3 系列旗舰模型，支持思维链推理（think 模式）
- 中英双语能力强，擅长中文理解和生成
- 支持长上下文
- 4bit 量化，Apple Silicon 上运行流畅

## 注意事项

- 模型默认启用思维链，响应中可能包含 `<think>...</think>` 标签，使用时建议正则过滤：
  ```python
  import re
  text = re.sub(r'<think>.*?</think>\s*', '', text, flags=re.DOTALL)
  ```
- `api_key` 参数必须传但值随意，填 `"unused"` 即可

## 服务管理

```bash
# 启动
launchctl kickstart gui/$(id -u)/com.mlx-server

# 停止
launchctl kill SIGTERM gui/$(id -u)/com.mlx-server

# 重启
launchctl kickstart -k gui/$(id -u)/com.mlx-server

# 查看状态
launchctl print gui/$(id -u)/com.mlx-server

# 查看日志
tail -f ~/.mlx-server/logs/server.log
```

## 同服务下的其他模型

此服务（端口 8787）同时托管以下模型，详见各自文档：

- `gemma-3-12b` → 见 `llm-gemma3-12b.md`
- `whisper-large-v3-turbo` → 见 `asr-whisper.md`
- `qwen3-embedding-0.6b` / `qwen3-embedding-4b` → 见 `embedding-qwen3.md`
