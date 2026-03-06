# Gemma 3 12B 本地推理服务

## 基本信息

| 项目 | 值 |
|------|-----|
| 模型 | `mlx-community/gemma-3-text-12b-it-4bit` |
| 模型 ID | `gemma-3-12b` |
| 参数量 | 12B（4bit 量化） |
| 服务进程 | `mlx-openai-server` |
| 监听地址 | `0.0.0.0:8787` |
| 本机地址 | `http://localhost:8787` |
| 协议 | OpenAI-compatible API |
| 最大并发 | 2 |
| Prompt 缓存 | 10 条 |
| launchd 服务 | `com.mlx-server` |

## API 调用

### Chat Completions

```bash
curl -X POST http://localhost:8787/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma-3-12b",
    "messages": [
      {"role": "user", "content": "Explain recursion in simple terms"}
    ],
    "temperature": 0.7,
    "max_tokens": 2048
  }'
```

### Python 调用示例（OpenAI SDK）

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8787/v1", api_key="unused")

response = client.chat.completions.create(
    model="gemma-3-12b",
    messages=[{"role": "user", "content": "Explain recursion in simple terms"}],
    temperature=0.7,
    max_tokens=2048
)
print(response.choices[0].message.content)
```

## 模型特点

- Google Gemma 3 系列，text-only 版本（纯文本推理，不含视觉能力）
- 英文能力突出，适合英文写作、代码生成、逻辑推理
- Instruction-tuned（it），可直接对话使用
- 4bit 量化，Apple Silicon 上运行流畅

## 与 Qwen3-14B 的选型建议

| | Qwen3-14B | Gemma 3 12B |
|---|---|---|
| 中文能力 | 强 | 一般 |
| 英文能力 | 强 | 强 |
| 代码生成 | 强 | 强 |
| 思维链推理 | 内置 think 模式 | 无 |
| 参数量 | 14B | 12B |
| 推荐场景 | 中文任务、需要深度推理 | 英文任务、快速响应 |

## 服务管理

与 Qwen3-14B 共用同一服务进程，管理命令见 `llm-qwen3-14b.md`。
