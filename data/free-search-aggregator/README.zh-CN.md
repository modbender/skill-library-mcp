<p align="center">
  <img src="assets/hero.jpg?v=6d74a19" alt="Free Search Aggregator" width="100%" />
</p>

<h1 align="center">Free Search Aggregator</h1>

<p align="center">
12 源搜索聚合器：自动故障切换、配额感知、任务级多查询检索，
并将结果统一存入 <code>memory/</code>。6 个无需密钥即可使用的搜索源。
</p>

---

## 核心能力

- **12 个搜索提供商** — 6 个无需 API 密钥即用
- **自动 failover**：提供商失败 → 立即切换到下一个
- **配额管理**：本地每日追踪，80% 时发出警告
- **任务搜索**：自动扩展查询、分组结果、去重合并
- **并发预设**：`@dual`（2线程）、`@deep`（3线程+更深查询）
- **结果持久化**：缓存/索引/报告三层结构化存储

---

## 提供商一览

| 提供商 | 是否需密钥 | 免费额度 | 索引来源 | 说明 |
|--------|-----------|---------|---------|------|
| `brave` | BRAVE_API_KEY | 2000次/天 | Brave 独立索引 | 高质量，隐私友好 |
| `exa` | EXA_API_KEY | ~33次/天（1000/月） | 神经语义+网页 | 语义搜索，独特结果 |
| `tavily` | TAVILY_API_KEY | 1000次/天 | 网页（AI 优化） | 专为 AI agent 设计 |
| `duckduckgo` | 无 | ~500次/天 | Bing+自有 | 无密钥，隐私友好 |
| `bing_html` | 无 | ~300次/天 | 微软 Bing RSS | 无密钥，XML feed 稳定 |
| `mojeek` | 无（或MOJEEK_API_KEY） | 200次/天 | Mojeek 独立索引 | 非 Google/Bing 镜像 |
| `serper` | SERPER_API_KEY | 2500次/天 | Google | 免费额度最大 |
| `searchapi` | SEARCHAPI_API_KEY | 100次/月 | Google/Bing 多引擎 | 多引擎支持 |
| `google_cse` | GOOGLE_API_KEY + GOOGLE_CX | 100次/天 | Google 官方 | 官方 Google API |
| `baidu` | BAIDU_API_KEY | 200次/天 | 百度 | 中文内容效果最好 |
| `wikipedia` | 无 | 1000次/天 | Wikipedia | 事实性/百科查询 |
| `searxng` | 无 | 无限（自托管） | 元搜索聚合 | 需自托管实例 |

**全部密钥配置后：总配额 8400+ 次/天**

---

## 快速开始

```bash
# 普通搜索（无需任何配置即可使用）
scripts/search "米兰今日天气 2026" --max-results 5

# 任务搜索（多查询并行）
scripts/search task "@dual 对比 Claude 与 GPT-4 在代码生成上的差异" --max-results 5

# 深度研究模式
scripts/search task "@deep 自动驾驶安全技术 2026" --max-results 8 --max-queries 10

# 本地配额状态
scripts/status

# 真实配额（支持的提供商）
scripts/remaining --real

# 清理旧缓存
scripts/gc --cache-days 14
```

---

## 各提供商配置指南

### Bing RSS (`bing_html`) — 无需密钥
开箱即用。使用 Bing 内置 RSS 接口（`format=rss`），绕过反爬检测，返回稳定 XML 结果。

### Mojeek — 无需密钥（可选 API Key）
**开箱即用**（HTML 抓取模式）。如需更高稳定性和额度：
1. 注册：https://www.mojeek.com/services/search/api/
2. 设置 `MOJEEK_API_KEY` → 自动切换为官方 JSON API 模式

### Wikipedia — 无需密钥，支持多语言
修改 `providers.yaml` 中的 `lang` 配置切换语言：
```yaml
wikipedia:
  lang: zh   # en | zh | it | de | fr | ja ...
```

### Exa.ai — 语义搜索
1. 注册：https://exa.ai/
2. 设置 `EXA_API_KEY`
3. 免费额度：1000次/月（≈33次/天）
4. 支持 `auto`（自动）/ `neural`（语义）/ `keyword`（关键词）模式

### Google Custom Search
1. 申请 API Key：https://developers.google.com/custom-search/v1/introduction
2. 创建搜索引擎获取 CX：https://programmablesearchengine.google.com/
3. 设置 `GOOGLE_API_KEY` 和 `GOOGLE_CX`
4. 免费：100次/天

### 百度千帆 AI Search
1. 注册：https://cloud.baidu.com/
2. 设置 `BAIDU_API_KEY`
3. 中文内容检索效果最优

### SearXNG — 需自托管实例
公共实例对服务端请求限速严格，建议自托管：
```bash
docker run -d -p 8080:8080 searxng/searxng
```
然后在 `providers.yaml` 中：
```yaml
searxng:
  endpoint: http://localhost:8080
  enabled: true
```

---

## CLI 用法

```bash
python -m free_search "<query>"
python -m free_search task "<task>" [--workers 1|2|3] [--max-queries N]
python -m free_search status [--real] [--compact]
python -m free_search remaining --real [--probe]
python -m free_search gc --cache-days 14 [--report-days 90]
```

---

## Python API

```python
from free_search import search, task_search, get_quota_status, get_real_quota

# 普通搜索
payload = search("最新 LLM 评测", max_results=5)

# 任务搜索（多查询聚合）
task_payload = task_search(
    "对比 Claude 与 GPT-4 在代码生成上的差异",
    max_results_per_query=5,
    max_queries=6,
    max_workers=2,
)

# 配额状态
status = get_quota_status()
real = get_real_quota()
```

---

## 数据组织

所有搜索产物统一写入 `memory/`：

- `memory/search-cache/YYYY-MM-DD/*.json` — 原始结果缓存（14天）
- `memory/search-index/search-index.jsonl` — 追加式索引
- `memory/search-reports/YYYY-MM-DD/*.md` — 可读报告（长期保留）

---

## 真实配额支持情况

| 提供商 | 真实配额查询 | 说明 |
|--------|------------|------|
| `tavily` | ✅ 支持 | 官方 usage 接口 |
| `searchapi` | ✅ 支持 | 官方 account 接口 |
| `brave` | ⚠️ 探测（消耗一次请求） | 通过响应头读取 |
| `serper` | ❌ 不支持 | 无公开配额接口 |
| `duckduckgo/bing/mojeek/wikipedia` | — | 无配额概念 |
| `exa/google_cse/baidu` | ❌ 不支持 | 无公开配额接口 |

---

## 使用建议

- 默认 `workers=1`，仅在需要时使用 `@dual/@deep`
- `SearXNG` 和 `YaCy` 需要自托管，默认禁用
- `MOJEEK_API_KEY` 为可选项，不设置时自动使用 HTML 抓取
- 建议配置 `BRAVE_API_KEY` + `TAVILY_API_KEY` 获得最佳体验
