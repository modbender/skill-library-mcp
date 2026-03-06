# 工作流详细说明

本文档详细说明搜索工作流的各个步骤、输出文件格式和故障排除方法。

## 工作流说明

### 步骤 1: 智谱 AI 搜索

**工具**: `zai-sdk` (智谱 AI 官方 Python SDK)

**输入**:
- 搜索查询
- 搜索引擎（search_pro/search_std/search_pro_sogou/search_pro_quark）
- 最大结果数（1-50，默认 15）
- 时间过滤（day/week/month/year/null）
- 内容长度（medium/high）

**输出**:
- 搜索结果列表，每条包含：
  - title: 网页标题
  - link: 网页 URL
  - content: 内容摘要
  - media: 来源媒体
  - publish_date: 发布日期

### 步骤 2: DuckDuckGo 搜索

**工具**: `ddgs` (Python 元搜索库)

**输入**:
- 搜索查询
- 最大结果数（默认 20，可配置）
- 地区代码（cn-zh/us-en/wt-wt 等）
- 安全搜索级别（on/moderate/off）
- 时间过滤（day/week/month/year）
- 搜索后端（auto/bing/google/duckduckgo 等）

**输出**:
- 搜索结果列表，每条包含：
  - title: 网页标题
  - href: 网页 URL
  - body: 网页摘要

### 步骤 3: LangExtract 结构化提取

**工具**: [langextract](https://github.com/google/langextract)（Google LLM 结构化提取库）

**后端模型**: 可配置，默认 `doubao-seed-2-0-code`（火山引擎 ARK）

**输入**:
- 搜索结果合并内容（智谱 + DuckDuckGo）

**输出**:
- 结构化信息，包含：
  1. 主要内容摘要
  2. 关键点列表（3-5个）
  3. 相关事实或数据
  4. 来源或参考信息

---

## 输出文件

运行后会在 `output/` 目录生成：

| 文件名 | 说明 |
|--------|------|
| `zhipu_search_result_YYYYMMDD_HHMMSS.md` | 智谱 AI 搜索结果 |
| `duckduckgo_search_result_YYYYMMDD_HHMMSS.md` | DuckDuckGo 搜索结果 |
| `extracted_info_YYYYMMDD_HHMMSS.md` | 提取的结构化信息 |
| `workflow_summary_YYYYMMDD_HHMMSS.md` | 工作流摘要 |
| `full_results_YYYYMMDD_HHMMSS.json` | 完整 JSON 结果（需 `--save-json`） |

---

## 故障排除

### 智谱搜索失败

- 检查 API Key 是否有效
- 确认 `conf.json` 中 `zhipu_search.apiKey` 配置正确
- 检查网络是否能访问 `open.bigmodel.cn`

### DuckDuckGo 搜索失败

- 确保已安装 `ddgs` 库：`pip install ddgs`
- 检查网络连接
- 尝试配置代理：参阅 [search-params.md](search-params.md#代理设置-proxy)
- 尝试切换搜索后端：设置 `backend: "bing"` 或 `"google"`

### 搜索结果为空

- 尝试使用更通用的关键词
- 检查时间过滤是否过于严格
- 尝试切换搜索引擎或后端

### 提取失败

- 检查 API Key 是否有效
- 确认模型可访问
- 查看 `--verbose` 输出了解详细错误
- 确认 `~/.openclaw/openclaw.json` 配置正确
- 检查搜索结果是否过长导致超出模型上下文限制
