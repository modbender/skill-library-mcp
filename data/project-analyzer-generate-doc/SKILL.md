---
name: project-analyzer-generate-doc
description: Hierarchical Context 分层文档生成器。为任意规模 Java/多模块工程生成 L3(文件级)→L2(模块级)→L1(项目级) 三层级文档索引。使用子代理分片 + 上下文压缩策略，规避上下文限制。激活当：用户需要理解工程架构、生成代码文档、创建项目索引、梳理代码结构、为 vibecoding 工具准备上下文。
---

# Project Analyzer Generate Doc

> Hierarchical Context 分层文档生成器 - 让 AI 理解百万行代码工程

## 核心原则

**严格自底向上流程**: `L3 (所有文件) → L2 (所有模块) → L1 (项目全局)`

**绝不跳过任何步骤**: 必须等所有 L3 完成 → 才能生成 L2 → 必须等所有 L2 完成 → 才能生成 L1

**上下文压缩**: 每处理 2-3 个文件自动压缩已处理内容，只保留路径 +1 行摘要

**子代理分片**: 大模块拆分为多个子代理并行处理，每片 10-15 个文件

---

## 激活条件

当用户提到以下关键词时激活：
- "生成项目文档"
- "分析工程架构"
- "创建代码索引"
- "理解这个工程"
- "为 vibecoding 准备文档"
- "Hierarchical Context"
- "三层级文档"
- "L1/L2/L3 文档"

---

## 文档层级结构

```
项目根目录/
├── .ai-doc/                          # 📁 默认输出目录
│   ├── project.md                    # L1: 项目级架构索引 (~10KB)
│   ├── module-a.md                   # L2: 模块级索引 (~5-15KB)
│   ├── module-b.md
│   └── project-name/
│       ├── module-a/                 # L3: 文件级文档
│       │   ├── ClassA.java.md
│       │   └── ClassB.java.md
│       └── module-b/
│           └── ...
├── .gitignore                        # 自动添加 .ai-doc/ 排除规则
├── src/
│   └── ...                           # 源代码
└── pom.xml                           # 项目配置
```

**默认输出路径**: `<项目根目录>/.ai-doc/`

**可选自定义**: 通过 `-OutputPath` 参数指定其他位置

---

## 完整工作流程

### 📋 Step 0: 项目扫描与规划

```powershell
# 1. 扫描所有模块
Get-ChildItem <项目路径> -Directory | Where-Object { $_.Name -notmatch 'target|.git' }

# 2. 统计每个模块的 Java 文件数
foreach ($module in $modules) {
  $count = (Get-ChildItem "$module" -Include *.java -Recurse | Measure-Object).Count
}

# 3. 制定分片策略
# - <20 文件：单子代理
# - 20-50 文件：2-3 个子代理分片
# - >50 文件：按目录拆分为多个子代理
```

**输出**: 模块列表 + 文件数统计 + 分片计划

---

### 📄 Step 1: 生成所有 L3 文件级文档

**核心策略**:
- 每片 10-15 个文件，spawn 多个子代理并行
- 每处理 2-3 个文件 → 压缩上下文（只保留路径 +1 行摘要）
- 简单文件 (<50 行纯定义/枚举/接口) → 简化文档
- 复杂文件 → 完整 L3 文档

**子代理任务模板**:

```markdown
# 任务：为 <模块名> 模块生成 L3 文档（分片 X/Y）

## 源码路径
<绝对路径>

## 输出路径
D:\ai\workspace\docs\<项目名>\<模块名>\

## 本分片文件
<文件列表，10-15 个>

## 要求
1. 为每个文件生成 L3 文档 (*.java.md)
2. 简单文件 (<50 行) → 简化文档（基本信息 + 职责）
3. 复杂文件 → 完整 L3 文档（函数签名、调用关系、关键逻辑行号）
4. **严格上下文压缩**：每处理完 2-3 个文件，压缩已处理内容的完整描述，只保留路径 +1 行摘要
5. 超时前尽可能完成更多文件
6. 完成后返回 JSON 摘要

## L3 文档模板
参考 [references/l3-template.md](references/l3-template.md)

## 返回格式
```json
{
  "module": "<模块名>",
  "chunk": "X/Y",
  "status": "completed|partial",
  "processed": ["File1.java", "File2.java"],
  "summaries": [
    {"file": "File1.java", "lines": 150, "type": "complex", "summary": "一句话摘要"}
  ]
}
```
```

**上下文压缩策略**:
```
每处理 2-3 个文件后：
- 保留：文件路径列表 + 1 行摘要/文件
- 丢弃：已生成文档的完整内容、中间思考过程、详细示例
- 目的：为后续文件腾出上下文空间
```

---

### 📁 Step 2: 生成所有 L2 模块级文档

**触发条件**: 所有 L3 文档生成完成

**核心策略**:
- 每个模块 spawn 一个子代理
- 读取该模块所有 L3 文档的**摘要**（而非完整内容）
- 汇总生成 module.md

**子代理任务模板**:

```markdown
# 任务：为 <模块名> 模块生成 L2 文档

## 输入
读取 D:\ai\workspace\docs\<项目名>\<模块名>\ 目录下所有 L3 文档

## 输出
D:\ai\workspace\docs\<项目名>\<模块名>.md

## 要求
1. 读取所有 L3 文档的摘要信息（文件名、行数、类型、职责）
2. 生成 L2 模块级文档，包含：
   - 模块职责概述（200 字）
   - 文件索引表（文件路径 | 职责简述 | 复杂度 | 行数）
   - 公共 API（核心类、核心方法）
   - 依赖关系图（ASCII 或 Markdown 表格）
   - 核心流程（1-3 个关键业务流程）
   - 配置项（如有）
3. **上下文压缩**：读取 L3 时只提取关键信息，不保留完整文档内容
4. 文档大小控制在 5-15KB

## L2 文档模板
参考 [references/l2-template.md](references/l2-template.md)
```

**摘要提取规则**:
```
从每个 L3 文档提取：
- 文件路径
- 行数
- 文件类型（类/接口/枚举/配置）
- 1 行职责描述
- 核心函数签名（仅复杂文件）

不提取：
- 完整方法实现
- 详细调用关系图
- 变更历史
```

---

### 🏗️ Step 3: 生成 L1 项目级文档

**触发条件**: 所有 L2 文档生成完成

**核心策略**:
- spawn 一个子代理
- 读取所有 L2 文档的**核心摘要**（每模块 500 字）
- 汇总生成 project.md

**子代理任务模板**:

```markdown
# 任务：生成 <项目名> 的 L1 项目级文档

## 输入
读取以下 L2 模块级文档：
<列出所有 module.md 路径>

## 输出
D:\ai\workspace\docs\<项目名>\project.md

## 要求
生成 L1 项目级文档，包含：
1. **项目基本信息** - 名称、技术栈、架构模式、数据库、中间件
2. **核心模块索引表** - 模块名 | 职责 | 文档路径 | 文件数 | 关键词
3. **系统架构图** - 模块间依赖关系（ASCII 或 Mermaid）
4. **目录结构** - 完整的工程目录树
5. **核心流程** - 跨模块的核心业务流程（2-4 个）
6. **技术栈汇总** - 框架、中间件、数据库
7. **配置项汇总** - 全局配置
8. **文档覆盖状态** - L3 文档统计

## L1 文档模板
参考 [references/l1-template.md](references/l1-template.md)
```

---

## 文档模板规范

### L3 文件级文档模板

详见 [references/l3-template.md](references/l3-template.md)

**核心字段**:
```markdown
# {文件名} - 代码详解

## 基本信息
- **文件路径**: `{relativePath}`
- **行数**: {lines}
- **文件类型**: {类/接口/枚举/配置}

## 文件职责
{oneLineDescription}

## 核心类/函数
{signatures}

## 依赖关系
{dependencies}
```

### L2 模块级文档模板

详见 [references/l2-template.md](references/l2-template.md)

**核心章节**:
```markdown
# {模块名} - 模块详解

## 模块职责
{200 字概述}

## 文件索引表
| 文件路径 | 职责简述 | 复杂度 | 行数 |

## 公共 API
{核心类和方法}

## 依赖关系
{依赖图}

## 核心流程
{1-3 个流程图}
```

### L1 项目级文档模板

详见 [references/l1-template.md](references/l1-template.md)

**核心章节**:
```markdown
# {项目名} - 系统架构

## 项目基本信息
{技术栈、架构模式}

## 核心模块索引表
| 模块名 | 职责 | 文档路径 | 文件数 | 关键词 |

## 系统架构图
{模块依赖关系}

## 核心流程
{跨模块流程}

## 技术栈汇总
{框架、中间件、数据库}
```

---

## 子代理分片策略

### 上下文监控阈值

| 阈值 | 动作 |
|------|------|
| 30% | 正常处理 |
| 40% | 预警，准备压缩 |
| 50% | **强制压缩**：丢弃已处理文件的完整内容，只保留路径 +1 行摘要 |
| 60% | 停止当前任务，报告进度 |

### 分片规则

```yaml
# 默认配置
chunk_strategy:
  files_per_subagent: 12        # 每个子代理处理文件数
  max_parallel_subagents: 5     # 最大并行子代理数
  context_threshold: 0.40       # 40% 预警阈值
  compress_threshold: 0.50      # 50% 强制压缩阈值
  compression_interval: 3       # 每处理 3 个文件压缩一次
  
# 文件复杂度估算
file_complexity:
  simple: "< 50 行，纯定义/枚举/接口"  # 简化文档
  normal: "50-200 行"                 # 标准 L3 文档
  complex: "> 200 行"                 # 详细 L3 文档
```

### 上下文压缩操作

```javascript
// 伪代码：上下文压缩策略
function compressContext(processedFiles) {
  if (contextUsage < 0.50) return;
  
  // 保留关键信息
  keep([
    'processed_file_paths',      // 文件路径列表
    'one_line_summaries',        // 每文件 1 行摘要
    'current_task',              // 当前任务描述
    'output_path'                // 输出路径
  ]);
  
  // 丢弃占用上下文的内容
  discard([
    'full_generated_doc_content', // 已生成文档的完整内容
    'intermediate_thoughts',      // 中间思考过程
    'detailed_examples',          // 详细示例
    'complete_function_bodies'    // 完整函数体
  ]);
}
```

---

## 激活后的标准流程

### 1. 确认项目路径

```
用户：请为 E:\projects\my-project 生成文档

AI: 收到！开始扫描项目结构...

# 执行扫描
Get-ChildItem E:\projects\my-project -Directory
Get-ChildItem E:\projects\my-project -Include *.java -Recurse | Measure-Object
```

### 2. 制定分片计划

```
扫描完成！发现 7 个模块，共 231 个 Java 文件：

| 模块 | 文件数 | 分片数 |
|------|--------|--------|
| module-a | 86 | 6 片 |
| module-b | 60 | 4 片 |
| module-c | 32 | 2 片 |
| ... | ... | ... |

现在开始 Step 1：生成所有 L3 文件级文档
```

### 3. 并行生成 L3

```
# Spawn 5 个子代理（达到上限）
sessions_spawn(label: "L3-module-a-chunk1", ...)
sessions_spawn(label: "L3-module-a-chunk2", ...)
sessions_spawn(label: "L3-module-b-chunk1", ...)
...

# 等待完成 → 继续 spawn 剩余子代理
# 每个子代理内部执行上下文压缩
```

### 4. 汇总生成 L2

```
所有 L3 文档完成！共生成 149 个文件级文档。

现在开始 Step 2：生成 7 个模块的 L2 文档...

# Spawn 5 个子代理
sessions_spawn(label: "L2-module-a", ...)
sessions_spawn(label: "L2-module-b", ...)
...
```

### 5. 生成 L1

```
所有 L2 文档完成！

现在开始 Step 3：生成 L1 项目级文档...

# Spawn 1 个子代理
sessions_spawn(label: "L1-project", ...)
```

### 6. 完成报告

```
✅ Hierarchical Context 文档生成完成！

## 生成结果

| 层级 | 数量 | 说明 |
|------|------|------|
| L3 | 149 | 文件级文档 |
| L2 | 7 | 模块级文档 |
| L1 | 1 | 项目级文档 |

## 文档位置
D:\ai\workspace\docs\my-project\

## Git 提交
git add docs/
git commit -m "docs: 生成 Hierarchical Context 三层级文档"
```

---

## 错误处理

### 子代理超时

```
问题：子代理处理大模块时超时（5 分钟限制）

解决：
1. 检查已生成的文件
2. 将剩余文件拆分为更小的分片（每片 5-8 个文件）
3. 缩短超时时间到 3 分钟，快速失败快速重试
4. 记录已完成进度，避免重复劳动
```

### 上下文爆炸

```
问题：子代理上下文使用率超过 60%

解决：
1. 立即触发强制压缩
2. 如果仍超过 60%，停止当前子代理
3. 将剩余文件拆分为更小的分片
4. 为新分片 spawn 新的子代理
```

### 模块扫描失败

```
问题：无法找到模块目录或源码文件

解决：
1. 确认项目路径正确
2. 检查是否有权限访问
3. 尝试使用绝对路径
4. 如果项目不在本地，请求用户提供源码位置
```

---

## 配置项

在 `TOOLS.md` 中添加：

```markdown
### Project Analyzer

- 默认分片大小：12 文件/子代理
- 上下文阈值：40% 预警，50% 强制压缩
- 最大并行：5 子代理
- 简单文件阈值：50 行
- 超时时间：300 秒（5 分钟）
```

---

## 使用示例

### 基础用法

```
用户：为 E:\projects\infypower-energy-ai 生成 Hierarchical Context 文档

AI: 收到！开始执行完整流程：

Step 1: 扫描项目结构...
Step 2: 生成所有 L3 文档（149 个文件）...
Step 3: 生成所有 L2 文档（7 个模块）...
Step 4: 生成 L1 项目文档...

✅ 完成！生成 157 个文档文件。
```

### 增量更新

```
用户：energy-ai-api 模块有代码变更，更新文档

AI: 收到！执行增量更新：

1. 检测变更文件（git diff）
2. 只更新变更文件的 L3 文档
3. 重新汇总生成 energy-ai-api.md (L2)
4. 更新 project.md (L1) 的统计信息
```

### 单模块生成

```
用户：只生成 ces-ai-rpc 模块的文档

AI: 收到！执行单模块流程：

1. 扫描 ces-ai-rpc 模块（32 个文件）
2. 分片生成 L3 文档（2 个子代理）
3. 汇总生成 ces-ai-rpc.md (L2)

注意：不生成 L1 项目文档（需要所有模块完成）
```

---

## 性能参考

### 生成时间估算

| 工程规模 | L3 生成 | L2 生成 | L1 生成 | 总计 |
|----------|---------|---------|---------|------|
| 1 万行 (50 文件) | ~5 分钟 | ~2 分钟 | ~1 分钟 | ~8 分钟 |
| 10 万行 (200 文件) | ~20 分钟 | ~8 分钟 | ~2 分钟 | ~30 分钟 |
| 100 万行 (2000 文件) | ~3 小时 | ~30 分钟 | ~5 分钟 | ~3.5 小时 |

### Token 消耗估算

| 阶段 | 每文件/模块 | 总计 (200 文件) |
|------|-------------|-----------------|
| L3 生成 | 150k tokens/文件 | 30M tokens |
| L2 生成 | 200k tokens/模块 | 1.4M tokens (7 模块) |
| L1 生成 | 500k tokens/项目 | 500k tokens |

---

## 相关文件

- L3 模板：[references/l3-template.md](references/l3-template.md)
- L2 模板：[references/l2-template.md](references/l2-template.md)
- L1 模板：[references/l1-template.md](references/l1-template.md)
- 上下文压缩指南：[references/context-compression.md](references/context-compression.md)
- 断点续传指南：[references/checkpoint-resume.md](references/checkpoint-resume.md)
- 增量更新流程：[references/incremental-update.md](references/incremental-update.md)

## 版本

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.1.0 | 2026-03-03 | 添加断点续传、增量更新、L1 样例 |
| 1.0.0 | 2026-03-03 | 初始版本，基于 Infypower Energy AI 项目实战经验 |
