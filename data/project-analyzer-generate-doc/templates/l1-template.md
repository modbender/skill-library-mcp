# {项目名} - 系统架构文档

> **L1 项目级文档** | 最后更新：{date} | 文档版本：{version}  
> 生成方式：自底向上汇总（L3 → L2 → L1）

---

## 📋 项目基本信息

| 项目 | 值 |
|------|-----|
| **项目名称** | {projectName} |
| **创建时间** | {createDate} |
| **最后更新** | {updateDate} |
| **技术栈** | {techStack} |
| **架构模式** | {architecturePattern} |
| **数据库** | {database} |
| **中间件** | {middleware} |

---

## 🏗️ 核心模块索引

| 模块名 | 职责简述 | 文档路径 | 文件数 | 代码行数 | 关键词 |
|--------|----------|----------|--------|----------|--------|
| **{module1}** | {summary1} | [{module1}.md]({link1}) | {count1} | {lines1} | {keywords1} |
| **{module2}** | {summary2} | [{module2}.md]({link2}) | {count2} | {lines2} | {keywords2} |

**项目统计**: {moduleCount} 个模块，**{totalFiles} 个 Java 文件**，约 **{totalLines} 行代码**

---

## 📂 系统目录结构

```
{projectName}/
│
├── {module1}/                          # L2: {module1} ✅
│   ├── src/main/java/{package}/
│   │   ├── {Class1}.java
│   │   └── {subPackage}/
│   └── pom.xml
│
├── {module2}/                          # L2: {module2} ✅
│   └── ...
│
└── docs/
    ├── project.md                      # L1: 本文档 ✅
    ├── {module1}.md                    # L2: {module1} ✅
    ├── {module2}.md                    # L2: {module2} ✅
    └── {projectName}/                  # L3: 文件级文档
        ├── {module1}/                  # ~{count1} 个 L3 文档
        └── {module2}/                  # ~{count2} 个 L3 文档
```

---

## 🔄 系统核心流程

### {流程名 1}

```
┌─────────────────────────────────────────────────────────────────┐
│  {步骤 1}                                                        │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  {步骤 2}                                                        │
└─────────────────────────────────────────────────────────────────┘
```

### {流程名 2}

{流程图或文字描述}

---

## 🛠️ 技术栈汇总

### 核心框架

| 技术 | 版本 | 用途 |
|------|------|------|
| {Tech1} | {version} | {usage} |
| {Tech2} | {version} | {usage} |

### 中间件

| 技术 | 用途 |
|------|------|
| {Middleware1} | {usage} |
| {Middleware2} | {usage} |

### 数据库

| 数据库 | 用途 |
|--------|------|
| {Database1} | {usage} |
| {Database2} | {usage} |

### 外部服务

| 服务 | 用途 |
|------|------|
| {Service1} | {usage} |
| {Service2} | {usage} |

---

## ⚙️ 全局配置项

| 配置项 | 来源 | 说明 |
|--------|------|------|
| `{configKey1}` | {ConfigClass} | {description} |
| `{configKey2}` | {ConfigClass} | {description} |

---

## 📊 文档覆盖状态

### L3 文件级文档统计

| 模块 | L3 文档数 | 状态 |
|------|-----------|------|
| {module1} | ~{count1} | ✅ 完成 |
| {module2} | ~{count2} | ✅ 完成 |
| **总计** | **~{totalCount}** | ✅ **100%** |

### 文档层级

| 层级 | 文档数 | 说明 |
|------|--------|------|
| L1 | 1 | project.md (本文档) |
| L2 | {moduleCount} | 模块级文档 (每个模块 1 个) |
| L3 | ~{totalCount} | 文件级文档 (每个 Java 文件 1 个) |

---

## 🔗 相关文档

### L2 模块级文档
- [{module1}.md]({link1}) - {summary1}
- [{module2}.md]({link2}) - {summary2}

### L3 文件级文档
- [{module1}/]({module1Path}) - ~{count1} 个文件
- [{module2}/]({module2Path}) - ~{count2} 个文件

### 系统设计文档
- [CODE_INDEX_SYSTEM.md]({designDocLink}) - 分层代码索引系统设计

---

## 📝 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| {version} | {date} | {changelog} |
| 1.0.0 | {initialDate} | 初始版本 |

---

*本文档由 project-analyzer-generate-doc 生成 | Hierarchical Context L1 项目级索引 | 遵循自底向上完整流程 (L3→L2→L1)*
