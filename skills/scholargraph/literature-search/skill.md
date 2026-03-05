# Literature Search Skill

## Overview

文献检索引擎，提供跨 11 个学术数据源的智能多源搜索与聚合能力。采用适配器注册表模式，支持互补搜索策略（根据查询自动识别领域并选择最优数据源组合），以及 PDF 批量下载功能。

## Core Capabilities

### 1. 查询扩展 (Query Expansion)
- **智能理解**: 分析模糊的研究兴趣，识别核心主题
- **关键词生成**: 生成核心词、同义词、缩写、相关术语、应用领域
- **交互式对话**: 通过多轮对话逐步明确研究方向
- **结构化输出**: 提供确认信息、关键词列表、追问建议

### 2. 多源检索 (11 个数据源)

**免费数据源 (无需 API Key)**:
- **arXiv**: 预印本论文 (物理/数学/CS), 3 req/s
- **Semantic Scholar**: 200M+ 论文，AI 驱动的学术搜索, 10 req/s
- **OpenAlex**: 250M+ 开放学术元数据，含 OA PDF URL, 10 req/s
- **PubMed**: 35M+ 生物医学文献 (NCBI E-utilities), 3 req/s (10/s with API key)
- **CrossRef**: 150M+ DOI 元数据，引用计数, 5 req/s
- **DBLP**: 计算机科学文献库, 1 req/s
- **Web Search**: 通过 Serper API 的通用网络搜索

**需 API Key 数据源**:
- **IEEE Xplore**: 工程/EE/CS 论文 (需 `IEEE_API_KEY`)
- **CORE**: 开放获取全文聚合 (需 `CORE_API_KEY`)
- **Unpaywall**: DOI-to-OA-PDF 解析 (需 `UNPAYWALL_EMAIL`)，仅用于 PDF URL 解析
- **Google Scholar**: 通过 SerpAPI 代理 (需 `SERPAPI_KEY`)

### 3. 互补搜索策略 (Complementary Search Strategy)
- **领域自动检测**: 根据查询关键词识别学术领域 (biomedical/cs/engineering/physics/general)
- **优先级排序**: 每个领域有独立的数据源优先级列表
- **自动选择**: 默认选择 3-4 个最优数据源
- **领域优先级**:
  - 生物医学: PubMed > Semantic Scholar > OpenAlex > CrossRef
  - 计算机科学: Semantic Scholar > arXiv > DBLP > OpenAlex
  - 工程: IEEE > Semantic Scholar > OpenAlex > CrossRef
  - 物理: arXiv > Semantic Scholar > OpenAlex
  - 通用: Semantic Scholar > OpenAlex > CrossRef > arXiv

### 4. PDF 下载 (PDF Download)
- **多策略 URL 解析**: 直接 URL → Unpaywall → OpenAlex OA → CORE
- **并发控制**: 默认 3 并发下载
- **PDF 验证**: magic bytes (`%PDF` header) 验证
- **跳过已存在**: 避免重复下载
- **元数据索引**: `metadata.json` 映射文件到搜索结果元数据
- **文件大小限制**: 默认 50MB

### 5. 智能排序
- 按引用数排序
- 按发布时间排序
- 按相关性排序

### 6. 信息提取
- 论文标题、作者、摘要
- 发布时间、期刊/会议
- 引用数、DOI、开放获取状态
- 概念标签 (OpenAlex concepts)
- MeSH 术语 (PubMed)

## CLI Usage

### 查询扩展
```bash
# 单次模式 - 快速扩展查询
lit expand "我想做 AI 相关的研究"

# 保存结果到文件
lit expand "Transformer 在 NLP 中的应用" --output keywords.md

# 交互式模式 - 多轮对话明确方向
lit expand "机器学习" --interactive
```

### 文献检索
```bash
# 自动选择最优数据源（基于查询内容）
lit search "transformer attention" --limit 20

# 指定领域提示，优化数据源选择
lit search "CRISPR gene editing" --domain biomedical

# 指定多个数据源（逗号分隔）
lit search "deep learning" --source semantic_scholar,arxiv,openalex --sort citations

# 搜索并下载 PDF
lit search "attention is all you need" --download --limit 3
```

### PDF 下载
```bash
# 检索并下载 PDF
lit download "transformer" --limit 5

# 指定下载目录
lit download "large language model" --limit 3 --output ./papers
```

## API Usage

### 查询扩展
```typescript
import QueryExpander from './scripts/query-expander';

const expander = new QueryExpander();
await expander.initialize();

// 单次扩展
const result = await expander.expandQuery('我想做 AI 相关的研究');
console.log(expander.formatResult(result));

// 交互式扩展
const conversationHistory = [];
const result2 = await expander.interactiveExpand(
  '深度学习',
  conversationHistory
);
```

### 简单搜索
```typescript
import LiteratureSearch from './scripts/search';

const searcher = new LiteratureSearch();
await searcher.initialize();

// 自动选择数据源搜索
const results = await searcher.search("transformer attention", {
  limit: 10,
  sortBy: 'relevance'
});

// 指定领域搜索（自动选择最优数据源）
const bioResults = await searcher.search("protein folding", {
  limit: 10,
  domainHint: 'biomedical'
});
```

### 高级搜索
```typescript
// 指定多个数据源
const results = await searcher.search("machine learning", {
  sources: ['semantic_scholar', 'openalex', 'crossref'],
  limit: 20,
  filters: {
    yearRange: [2022, 2024],
    categories: ['cs.LG', 'cs.AI'],
    minCitations: 10
  },
  sortBy: 'citations'
});

// 按作者搜索
const byAuthor = await searcher.searchByAuthor("Yann LeCun", {
  limit: 15,
  sortBy: 'date'
});
```

### PDF 下载
```typescript
import { PdfDownloader } from './scripts/pdf-downloader';

const downloader = new PdfDownloader({
  outputDir: './papers',
  concurrency: 3,
  skipExisting: true
}, searcher.getRegistry());

const downloads = await downloader.downloadResults(results.results);
console.log(`Downloaded ${downloads.length} PDFs`);
```

### 搜索策略
```typescript
// 获取搜索策略实例
const strategy = searcher.getStrategy();

// 检测查询的学术领域
const domain = strategy.detectDomain("CRISPR gene editing");
// => "biomedical"

// 获取推荐的数据源组合
const sources = strategy.selectSources("deep learning", searcher.getRegistry());
// => ["semantic_scholar", "arxiv", "dblp", "openalex"]
```

## Output Format

### SearchResult 类型
```typescript
interface SearchResult {
  id: string;              // 论文唯一标识
  title: string;           // 标题
  authors: string[];       // 作者列表
  abstract: string;        // 摘要
  publishDate: string;     // 发布日期
  source: string;          // 数据源
  url: string;             // 论文链接
  pdfUrl?: string;         // PDF链接
  citations?: number;      // 引用数
  venue?: string;          // 期刊/会议
  keywords?: string[];     // 关键词
  doi?: string;            // DOI
  snippet?: string;        // 摘要片段
  openAccess?: boolean;    // 开放获取
  concepts?: string[];     // 概念标签 (OpenAlex)
  meshTerms?: string[];    // MeSH 术语 (PubMed)
  journal?: string;        // 期刊名称
}
```

## Architecture

### 适配器模式 (Adapter Pattern)
```
SearchSourceAdapter (interface)
├── AbstractSearchAdapter (base class, rate limiting)
│
├── ArxivAdapter          (free, physics/cs)
├── SemanticScholarAdapter(free, general)
├── WebAdapter            (free, general)
├── OpenAlexAdapter       (free, multidisciplinary)
├── PubMedAdapter         (free/freemium, biomedical)
├── CrossRefAdapter       (free, general)
├── DblpAdapter           (free, cs)
├── IeeeAdapter           (freemium, engineering)
├── CoreAdapter           (freemium, general)
├── UnpaywallAdapter      (free, DOI-to-PDF only)
└── GoogleScholarAdapter  (paid, general)
```

### 搜索流程
```
Query → Strategy (domain detect) → Select Sources → Parallel Search → Merge → Filter → Sort → Deduplicate → Results
                                                                                                            ↓
                                                                                              (optional) PDF Download
```

## Environment Variables

```bash
# 学术数据源 API Keys (可选，扩展搜索覆盖范围)
NCBI_API_KEY          # PubMed 高速访问 (10 req/s vs 3 req/s)
IEEE_API_KEY          # IEEE Xplore 工程文献
CORE_API_KEY          # CORE 开放获取全文
UNPAYWALL_EMAIL       # Unpaywall OA PDF 解析
CROSSREF_MAILTO       # CrossRef 礼貌池 (更高速率限制)
SERPAPI_KEY           # Google Scholar (via SerpAPI)
SERPER_API_KEY        # Web 搜索 (via Serper)
OPENALEX_MAILTO       # OpenAlex 高速访问 (100 req/s vs 10 req/s)
```

## Best Practices

1. **使用领域提示**: `--domain biomedical` 自动选择最优数据源组合
2. **配置邮箱**: 设置 `CROSSREF_MAILTO` 和 `UNPAYWALL_EMAIL` 提升访问速率
3. **使用查询扩展**: 对于模糊的研究兴趣，先用 `expand` 命令生成具体关键词
4. **组合数据源**: 不同数据源覆盖不同范围的文献
5. **合理排序**: 根据目的选择排序方式 (引用数/时间/相关性)
6. **批量下载 PDF**: 使用 `lit download` 批量下载开放获取论文
7. **缓存结果**: 避免重复检索相同内容
8. **定期更新**: 关注新发表论文，保持知识更新

## Troubleshooting

### 问题：检索结果太少
- 尝试扩大检索词范围
- 增加数据源数量 (`--source semantic_scholar,openalex,crossref`)
- 使用 `--domain` 指定领域
- 检查拼写是否正确

### 问题：结果质量不高
- 使用引用数排序 (`--sort citations`)
- 添加时间过滤
- 指定高质量数据源 (`--source semantic_scholar`)

### 问题：API限制
- 配置 API Key 提升速率限制
- 配置 `CROSSREF_MAILTO`/`OPENALEX_MAILTO` 进入礼貌池
- 使用合理的请求间隔

### 问题：PDF 下载失败
- 并非所有论文都有开放获取 PDF
- 配置 `UNPAYWALL_EMAIL` 启用 Unpaywall 解析
- 检查网络连接

## File Structure

```
literature-search/
├── skill.md                    # 本说明文档
└── scripts/
    ├── search.ts               # 搜索引擎核心（使用适配器注册表）
    ├── types.ts                # 类型定义
    ├── query-expander.ts       # 查询扩展脚本
    ├── search-strategy.ts      # 互补搜索策略
    ├── pdf-downloader.ts       # PDF 下载器
    └── adapters/               # 搜索源适配器
        ├── base.ts             # 适配器接口与抽象基类
        ├── registry.ts         # 适配器注册表
        ├── index.ts            # 导出
        ├── arxiv-adapter.ts    # arXiv
        ├── semantic-scholar-adapter.ts  # Semantic Scholar
        ├── web-adapter.ts      # Web Search
        ├── openalex-adapter.ts # OpenAlex
        ├── pubmed-adapter.ts   # PubMed
        ├── crossref-adapter.ts # CrossRef
        ├── dblp-adapter.ts     # DBLP
        ├── ieee-adapter.ts     # IEEE Xplore
        ├── core-adapter.ts     # CORE
        ├── unpaywall-adapter.ts # Unpaywall
        └── google-scholar-adapter.ts # Google Scholar (SerpAPI)
```

## Related Documentation

- [QUERY_EXPANSION.md](../../QUERY_EXPANSION.md) - 查询扩展功能详细文档
