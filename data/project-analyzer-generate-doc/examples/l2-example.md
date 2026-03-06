# L2 文档示例：core-api.md

> 实际生成样例（脱敏版本）

---

## 📋 基本信息

| 项目 | 值 |
|------|-----|
| **模块路径** | `core-api/src/main/java/com/endcy/ai/core/` |
| **最后更新** | 2026-03-03 |
| **主要语言** | Java |
| **框架** | Spring Boot, Spring Cloud |

---

## 🎯 模块职责

智能助手应用的核心查询引擎模块，提供基于多数据源的智能查询能力。
通过 `QueryEngine` 实现数据库查询 + 缓存查询 + API 查询的多路召回，并支持结果优化排序。

---

## 📁 文件索引 (L3 汇总)

| 文件路径 | 职责简述 | 复杂度 | 行数 | L3 文档 |
|----------|----------|--------|------|---------|
| `CoreApplication.java` | Spring Boot 启动类，含健康检查接口 | 简单 | 28 | ✅ |
| `EngineFactory.java` | 查询引擎工厂，根据场景动态创建数据源 | 复杂 | 125 | ✅ |
| `QueryEngine.java` | 查询引擎实现，支持并行查询和结果优化 | 复杂 | 168 | ✅ |
| `CacheDataSource.java` | 缓存数据源查询 | 中等 | 62 | ✅ |
| `DatabaseDataSource.java` | 数据库查询器 | 中等 | 48 | ✅ |

**模块统计**: 26 个文件，约 1850 行代码，5 个复杂文件，14 个中等文件，7 个简单文件

---

## 🔌 公共 API

### 核心类

| 类名 | 类型 | 说明 |
|------|------|------|
| `CoreApplication` | `@SpringBootApplication` | 应用启动类，提供健康检查端点 `GET /health` |
| `EngineFactory` | `@Component` | 工厂类，根据 `QueryContext` 创建合适的数据源 |
| `QueryEngine` | `IQueryEngine` | 查询引擎，实现查询路由和结果优化 |

### REST 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `GET /health` | GET | 健康检查接口，返回应用状态 |
| `POST /api/query` | POST | 智能查询接口 |
| `POST /api/query/batch` | POST | 批量查询接口 |

---

## 🔗 依赖关系

```
core-api (本模块)
│
├── 外部依赖
│   ├── Spring Boot (应用框架)
│   ├── Spring Cloud (微服务框架)
│   ├── Redis (缓存)
│   └── MySQL (主数据库)
│
├── 内部依赖
│   └── common-utils (通用工具模块)
│
└── 被依赖
    └── admin-api (管理后台调用本模块)
```

---

## 🔄 核心流程

### 智能查询流程

```
用户查询
    │
    ▼
EngineFactory.createDataSource()
    │
    ├─→ DataSourceRouter.getRoute()
    │   ├─→ DatabaseDataSource (数据库查询)
    │   ├─→ CacheDataSource (缓存查询)
    │   └─→ ApiDataSource (API 查询)
    │
    └─→ QueryEngine.execute()
            │
            ├─→ QueryParser.parse() (查询解析)
            │
            ├─→ CompletableFuture.supplyAsync() [并行查询]
            │   ├─→ DataSource 1
            │   ├─→ DataSource 2
            │   └─→ DataSource 3
            │
            ├─→ mergeResults() (合并去重)
            │
            ├─→ optimizeResults() (结果优化，过滤低分)
            │
            └─→ 返回最终结果
```

---

## ⚙️ 配置项

| 配置项 | 来源 | 默认值 | 说明 |
|--------|------|--------|------|
| `queryProperties.cacheEnabled` | QueryProperties | true | 启用缓存查询 |
| `queryProperties.cacheTtl` | QueryProperties | 300 | 缓存过期时间 (秒) |
| `queryProperties.minScore` | QueryProperties | 0.6 | 结果优化最低分数 |
| `queryProperties.maxParallel` | QueryProperties | 3 | 最大并行查询数 |

---

## ⚠️ 注意事项

1. **方法废弃**: `EngineFactory` 中除 `createDataSource` 外，其他方法均已废弃
2. **并行查询**: `QueryEngine` 使用 `CompletableFuture` 并行执行多个数据源
3. **结果去重**: 合并查询结果时基于 `Result.getId()` 去重

---

## 🔗 相关文档

### 下级 L3 文档
- [CoreApplication.java.md](./.ai-doc/core-api/CoreApplication.java.md)
- [EngineFactory.java.md](./.ai-doc/core-api/EngineFactory.java.md)
- [QueryEngine.java.md](./.ai-doc/core-api/QueryEngine.java.md)

### 上级 L1 文档
- [project.md](./.ai-doc/project.md)

---

*本文档由 project-analyzer-generate-doc 生成 | Hierarchical Context L2 模块级索引 | 基于 26 个 L3 文件摘要汇总*

---

## 📍 文档位置说明

本文档位于项目根目录的 `.ai-doc/` 文件夹下：

```
endcy-assistant-ai/
├── .ai-doc/
│   ├── core-api.md    ← 本文档
│   ├── project.md
│   └── core-api/
│       └── *.java.md       ← L3 文档
└── src/
    └── core-api/      ← 源代码
```
