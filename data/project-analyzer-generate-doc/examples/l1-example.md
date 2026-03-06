# L1 文档示例：project.md

> 实际生成样例（脱敏版本）

---

# Endcy Assistant AI - 系统架构文档

> **L1 项目级文档** | 最后更新：2026-03-03 | 文档版本：2.0.0  
> 生成方式：自底向上汇总（L3 → L2 → L1）

---

## 📋 项目基本信息

| 项目 | 值 |
|------|-----|
| **项目名称** | Endcy Assistant AI (智能助手 AI) |
| **创建时间** | 2026-03 |
| **最后更新** | 2026-03-03 |
| **技术栈** | Java 17+, Spring Boot 3.x, Spring Cloud, MyBatis-Plus |
| **架构模式** | 多数据源查询 + 多模块分层架构 |
| **数据库** | MySQL (主库) + Redis (缓存) |
| **中间件** | Redis, RabbitMQ, Nacos, XXL-JOB |

---

## 🏗️ 核心模块索引

| 模块名 | 职责简述 | 文档路径 | 文件数 | 代码行数 | 关键词 |
|--------|----------|----------|--------|----------|--------|
| **core-api** | 查询核心服务，提供智能查询、多数据源路由、结果优化 | [core-api.md](./core-api.md) | 26 | ~1850 | query, datasource, engine, optimize, router |
| **client-rpc** | RPC 通信客户端，提供查询/数据管理的远程调用 | [client-rpc.md](./client-rpc.md) | 30 | ~1400 | rpc, feign, restclient, sse, flux |
| **admin-api** | 管理后台 API，提供数据管理、日志、任务调度 | [admin-api.md](./admin-api.md) | 14 | ~750 | admin, controller, mq, xxl-job, log |
| **tool-integration** | 工具集成模块，支持天气查询、图片搜索等工具 | [tool-integration.md](./tool-integration.md) | 5 | ~350 | tool, integration, api, weather |
| **data-repository** | 数据持久层，管理数据文档、查询记录、缓存存储 | [data-repository.md](./data-repository.md) | 22 | ~1100 | repository, mybatis, cache, mysql |
| **service-common** | 通用服务组件，提供基础服务、异常、Redis、AOP 等 | [service-common.md](./service-common.md) | 32 | ~1700 | service, redis, nacos, aop, limit |
| **service-domain** | 领域模型定义，包含数据管理枚举、MQ 消息模型 | [service-domain.md](./service-domain.md) | 8 | ~450 | domain, enum, mq, metadata |

**项目统计**: 7 个模块，**137 个 Java 文件**，约 **7600 行代码**

---

## 📂 系统目录结构

```
infypower-energy-ai/
│
├── .ai-doc/                            # 📁 本文档所在目录
│   ├── project.md                      # L1: 本文档 ✅
│   ├── energy-ai-api.md                # L2: energy-ai-api ✅
│   ├── ces-ai-rpc.md                   # L2: ces-ai-rpc ✅
│   ├── energy-admin-api.md             # L2: energy-admin-api ✅
│   ├── energy-ai-mcp.md                # L2: energy-ai-mcp ✅
│   ├── energy-ai-repository.md         # L2: energy-ai-repository ✅
│   ├── service-common.md               # L2: service-common ✅
│   ├── service-domain.md               # L2: service-domain ✅
│   └── infypower-energy-ai/            # L3: 文件级文档
│       ├── energy-ai-api/              # ~28 个 L3 文档
│       ├── ces-ai-rpc/                 # ~32 个 L3 文档
│       └── ...
│
├── energy-ai-api/                      # 模块：AI 应用主服务
│   ├── src/main/java/...
│   └── pom.xml
│
├── ces-ai-rpc/                         # 模块：RPC 客户端
│   ├── src/main/java/...
│   └── pom.xml
│
└── pom.xml                             # 父工程
```

---

## 🔄 系统核心流程

### RAG 智能问答流程

```
┌─────────────────────────────────────────────────────────────────┐
│  用户提问 (AiController)                                         │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  EnergyAiApp.doChatWithRag()                                     │
│  ├─→ IntentAnalysisAgent.analyzeIntent()  意图分析              │
│  │   └─→ 识别业务类型 (KnowledgeBusinessTypeEnum)                │
│  │   └─→ 识别数据来源 (PossibleSourceTypeEnum)                   │
│  │                                                               │
│  ├─→ ChatClientAdvisorFactory.createHybridRetrievalAdvisor()    │
│  │   └─→ AdvisorRetrieverFactory.dynamicCreateRetrievers()      │
│  │       ├─→ VectorDocumentRetriever (本地向量检索)              │
│  │       ├─→ Bm25DocumentRetriever (关键词检索)                  │
│  │       └─→ AliDocumentRetriever (阿里云检索)                   │
│  │                                                               │
│  └─→ HybridRetrievalAdvisor.before()                            │
│      ├─→ QueryExpander (长查询拆分)                              │
│      ├─→ CompletableFuture.supplyAsync() [并行检索]              │
│      ├─→ mergeDocuments() (合并去重)                             │
│      ├─→ doRerank() (重排序，过滤低分)                           │
│      └─→ 构建增强提示词 → LLM                                    │
└─────────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  LLM 生成回答 → 返回用户                                          │
└─────────────────────────────────────────────────────────────────┘
```

### RPC 远程调用流程

```
┌─────────────────────────────────────────────────────────────────┐
│  energy-admin-api / energy-ai-api                                │
│  └─→ @Autowired EnergyAiFeignService                            │
│      └─→ EnergyAiClient.qa()                                     │
│          ├─→ WebClient.post("/api/ai/qa")                        │
│          ├─→ KnowledgeAIQueryParam                               │
│          └─→ CommonResMsgDTO<AIAnswerRet>                        │
└─────────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  远程 AI 服务                                                      │
│  ├─→ 同步问答：CommonResMsgDTO<AIAnswerRet>                      │
│  └─→ 流式问答：Flux<AIStreamResponse> (SSE)                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ 技术栈汇总

### 核心框架

| 技术 | 版本 | 用途 |
|------|------|------|
| Java | 17+ | 开发语言 |
| Spring Boot | 3.x | 应用框架 |
| Spring Cloud | 2023.x | 微服务框架 |
| MyBatis-Plus | - | ORM 框架 |

### 中间件

| 技术 | 用途 |
|------|------|
| Nacos | 配置中心 + 服务注册 |
| Redis | 缓存、限流、会话存储 |
| RabbitMQ | 异步消息处理 |
| XXL-JOB | 分布式任务调度 |

### 数据库

| 数据库 | 用途 |
|--------|------|
| MySQL | 主数据库 (业务数据、查询记录) |
| Redis | 缓存数据库 (热点数据缓存) |

### 外部服务

| 服务 | 用途 |
|------|------|
| OpenWeather API | 天气查询工具 |
| Unsplash API | 图片搜索工具 |

---

## ⚙️ 全局配置项

| 配置项 | 来源 | 说明 |
|--------|------|------|
| Nacos 配置 | `@EnableDiscoveryClient` | 服务注册与配置中心 |
| `queryProperties.cacheEnabled` | QueryProperties | 启用缓存查询 |
| `queryProperties.cacheTtl` | QueryProperties | 缓存过期时间 (秒) |
| `queryProperties.minScore` | QueryProperties | 结果优化最低分数 (建议 0.5-0.7) |
| `queryProperties.maxParallel` | QueryProperties | 最大并行查询数 |
| `@EnableAsync` | Spring Boot | 启用异步方法 |
| `@EnableTransactionManagement` | Spring Boot | 启用数据库事务 |

---

## 📊 文档覆盖状态

### L3 文件级文档统计

| 模块 | L3 文档数 | 状态 |
|------|-----------|------|
| core-api | ~26 | ✅ 完成 |
| client-rpc | ~30 | ✅ 完成 |
| admin-api | ~14 | ✅ 完成 |
| tool-integration | ~5 | ✅ 完成 |
| data-repository | ~22 | ✅ 完成 |
| service-common | ~32 | ✅ 完成 |
| service-domain | ~8 | ✅ 完成 |
| **总计** | **~137** | ✅ **100%** |

### 文档层级

| 层级 | 文档数 | 说明 |
|------|--------|------|
| L1 | 1 | project.md (本文档) |
| L2 | 7 | 模块级文档 (每个模块 1 个) |
| L3 | ~137 | 文件级文档 (每个 Java 文件 1 个) |

---

## 🔗 相关文档

### L2 模块级文档
- [core-api.md](./core-api.md) - 查询核心服务
- [client-rpc.md](./client-rpc.md) - RPC 通信客户端
- [admin-api.md](./admin-api.md) - 管理后台 API
- [tool-integration.md](./tool-integration.md) - 工具集成
- [data-repository.md](./data-repository.md) - 数据持久层
- [service-common.md](./service-common.md) - 通用服务组件
- [service-domain.md](./service-domain.md) - 领域模型

### L3 文件级文档
- [core-api/](./endcy-assistant-ai/core-api/) - ~26 个文件
- [client-rpc/](./endcy-assistant-ai/client-rpc/) - ~30 个文件
- [admin-api/](./endcy-assistant-ai/admin-api/) - ~14 个文件
- [tool-integration/](./endcy-assistant-ai/tool-integration/) - ~5 个文件
- [data-repository/](./endcy-assistant-ai/data-repository/) - ~22 个文件
- [service-common/](./endcy-assistant-ai/service-common/) - ~32 个文件
- [service-domain/](./endcy-assistant-ai/service-domain/) - ~8 个文件

---

## 📝 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 2.0.0 | 2026-03-03 | 基于完整 L3→L2→L1 流程重新生成，覆盖全部 7 个模块 137 个文件 |
| 1.1.0 | 2026-03-03 | 基于 L3→L2→L1 自底向上流程生成 |
| 1.0.0 | 2026-03-03 | 初始版本 |

---

*本文档由 project-analyzer-generate-doc 生成 | Hierarchical Context L1 项目级索引 | 遵循自底向上完整流程 (L3→L2→L1)*

---

## 📍 文档位置说明

本文档位于项目根目录的 `.ai-doc/` 文件夹下：

```
endcy-assistant-ai/
├── .ai-doc/
│   ├── project.md          ← 本文档 (L1)
│   ├── core-api.md         ← L2 模块级
│   └── core-api/           ← L3 文件级
│       └── *.java.md
└── src/
    └── core-api/           ← 源代码
```

从本文档可以：
1. 快速了解整个项目的架构和技术栈
2. 点击 L2 链接查看具体模块详情
3. 从 L2 继续深入到 L3 查看具体文件实现
4. 理解跨模块的核心业务流程
