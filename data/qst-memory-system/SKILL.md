---
name: QST Memory Skill
description: 利用 QST 理論（E8 幾何結構、DSI 層次、ICT Collapse）實現高效記憶存取。
---

# QST Memory Skill

**OpenClaw Skill** - QST Matrix-based Memory System

利用 QST 理論（E8 幾何結構、DSI 層次、ICT Collapse）實現高效記憶存取。

## 功能

- **短記憶**：對話上下文緩存 (30 min - 24 hr)
- **長記憶**：長期知識存儲 (JSON/SQLite)
- **混合檢索**：QST + Embedding 語義搜索
- **快速存取**：毫秒級檢索

## 安裝

```bash
cd /root/.openclaw/workspace/skills
git clone https://github.com/ZhuangClaw/qst-memory-system.git qst-memory
```

## 配置

在 `SKILL.md` 同目錄創建 `config.json`：

```json
{
  "e8_dim": 16,
  "top_k": 5,
  "storage_type": "hybrid",
  "embedding_type": "simple"
}
```

## 使用方法

### 基本用法

```python
from qst_memory_skill import QSTMemorySkill

# 初始化
memory = QSTMemorySkill()

# 存儲對話
memory.store("用戶說的話", "user")
memory.store("AI的回覆", "assistant")

# 檢索相關記憶
results = memory.retrieve("查詢關鍵詞")

# 獲取對話上下文
context = memory.get_context()
```

### 進階用法

```python
from qst_memory import QSTMemory

# 完整初始化
memory = QSTMemory(
    e8_dim=16,           # E8 投影維度
    top_k=5               # 檢索返回數量
)

# 存儲對話輪次
memory.store_conversation("user", "你好！", "user")
memory.store_conversation("assistant", "秦王陛下萬歲！", "assistant")

# 檢索
results = memory.retrieve("皇帝", top_k=3)
for r in results:
    print(f"[{r.total_score:.3f}] {r.memory.content}")

# 整合到長期記憶
memory.consolidate()

# 獲取 coherence 狀態
info = memory.get_coherence_info()
print(info)
```

## 架構

```
┌─────────────────────────────────────────────────────────┐
│                   QST Memory Skill                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│   │   Short     │◄──►│    QST     │◄──►│    Long    │   │
│   │   Memory   │    │   Matrix   │    │   Memory   │   │
│   └─────────────┘    └─────────────┘    └─────────────┘   │
│          │                   │                   │        │
│          ▼                   ▼                   ▼        │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│   │Conversation │    │   ICT      │    │   SQLite/   │   │
│   │   Buffer    │    │  Retrieval  │    │    JSON     │   │
│   └─────────────┘    └─────────────┘    └─────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 核心概念

### Coherence (σ)

| σ 值 | 意義 |
|------|------|
| 0.7 | Working Memory |
| 0.85 | Short Memory |
| 0.95 | Medium Memory |
| 1.1 | Long Memory |

### DSI 層次

```
D_n = D_0 - n·φ²
n ∈ [0, 36]
φ = 1.618... (黃金比例)
```

### ICT Collapse

```
P(M) ∝ |⟨Q|Ψ_M⟩|² · exp(-η·V_eth)
```

## API

### QSTMemory

| 方法 | 功能 |
|------|------|
| `store(content, context)` | 存儲記憶 |
| `store_conversation(speaker, content, type)` | 存儲對話 |
| `retrieve(query, top_k)` | 檢索記憶 |
| `get_context()` | 獲取上下文 |
| `consolidate()` | 整合到長期記憶 |
| `decay_all()` | 衰減低 coherence 記憶 |

### QSTMemorySkill (OpenClaw)

| 方法 | 功能 |
|------|------|
| `store(content, context)` | 存儲 |
| `retrieve(query, top_k)` | 檢索 |
| `get_context()` | 上下文 |

## 依賴

- numpy
- (可選) openai - OpenAI Embeddings
- (可選) sentence-transformers - Sentence Embeddings

## 參考

- [QSTv7.1 Framework](/QST-Archive/)
- [E8 Geometry](https://en.wikipedia.org/wiki/E8_(mathematics))
- [Golden Ratio](https://en.wikipedia.org/wiki/Golden_ratio)

---

*基於 QSTv7.1 框架*
*作者：李斯 (丞相)*
