# Qwen3 Embedding 向量化服务

## 基本信息

本机提供两个不同规模的 Embedding 模型，均通过主 LLM 服务器暴露。

| 项目 | 小模型 | 大模型 |
|------|--------|--------|
| 模型 | `mlx-community/Qwen3-Embedding-0.6B-4bit-DWQ` | `mlx-community/Qwen3-Embedding-4B-4bit-DWQ` |
| 模型 ID | `qwen3-embedding-0.6b` | `qwen3-embedding-4b` |
| 参数量 | 0.6B | 4B |
| 适用场景 | 快速检索、低延迟 | 高精度语义匹配 |

### 共用服务信息

| 项目 | 值 |
|------|-----|
| 服务进程 | `mlx-openai-server` |
| 监听地址 | `0.0.0.0:8787` |
| 本机地址 | `http://localhost:8787` |
| 协议 | OpenAI-compatible API |
| launchd 服务 | `com.mlx-server` |

## API 调用

### 生成向量

```bash
curl -X POST http://localhost:8787/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-embedding-0.6b",
    "input": "要向量化的文本"
  }'
```

### 批量向量化

```bash
curl -X POST http://localhost:8787/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-embedding-4b",
    "input": ["文本一", "文本二", "文本三"]
  }'
```

### 响应格式

```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "index": 0,
      "embedding": [0.0123, -0.0456, ...]
    }
  ],
  "model": "qwen3-embedding-0.6b",
  "usage": {
    "prompt_tokens": 5,
    "total_tokens": 5
  }
}
```

### Python 调用示例（OpenAI SDK）

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8787/v1", api_key="unused")

# 单条
response = client.embeddings.create(
    model="qwen3-embedding-0.6b",
    input="要向量化的文本"
)
vector = response.data[0].embedding

# 批量
response = client.embeddings.create(
    model="qwen3-embedding-4b",
    input=["文本一", "文本二", "文本三"]
)
vectors = [d.embedding for d in response.data]
```

## 选型建议

- **qwen3-embedding-0.6b**：日常检索、RAG pipeline 中的文档索引，速度快、内存占用低
- **qwen3-embedding-4b**：需要高精度语义匹配的场景，如细粒度相似度排序
