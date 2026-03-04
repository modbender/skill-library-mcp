---
name: knowledge-splitter
description: |
  大型知识文档分块查阅工具。当需要查阅知识库时，先通过索引匹配对应分块，避免一次性加载整个文件。
  适用于: knowledge/*.md 文档分块、专题知识库索引、增量更新。
metadata:
  evomap:
    gene_id: gene_knowledge_splitter
    category: optimize
    signals: ["knowledge too large", "load full file", "split large doc"]
---

# Knowledge Splitter

大型知识文档分块查阅工具。

## 使用场景

当知识库文件过大（如 >5KB）时，应先分块存储，通过索引按需加载。

## 工作流程

### 1. 分块规则

按**主题/类型**拆分知识文件：

```
knowledge/
├── evomap-chunks/
│   ├── INDEX.md          # 索引文件
│   ├── 01-intro.md       # 主题1
│   ├── 02-protocol.md    # 主题2
│   └── ...
└── evomap_full.md       # 原始完整文件（可选保留）
```

### 2. 索引文件格式

每个知识库目录应有 `INDEX.md`：

```markdown
# {知识库名} 索引

| 文件 | 标签 | 适用场景 |
|------|------|----------|
| 01-intro.md | intro, overview | 什么是X |
| 02-protocol.md | protocol, api | 协议相关 |

## 使用方法

1. 根据查询主题匹配标签
2. 读取对应的分块文件
3. 如需更详细内容，再查阅完整文件
```

### 3. 查阅流程

```
当需要查询知识时:
  1. 定位知识库目录 (如 knowledge/evomap-chunks/)
  2. 读取 INDEX.md 获取索引
  3. 根据查询主题匹配文件
  4. 读取对应的分块文件
  5. 如分块内容不足，再读取完整文件
```

## 工具

使用 `read` 工具读取文件：
- `read` 可指定 `offset` 和 `limit` 进行部分读取
- 大文件优先用分块读取

## 示例

**查询 EvoMap GDI 评分**:
1. 读取 `knowledge/evomap-chunks/INDEX.md`
2. 匹配标签 "gdi" → `05-gdi.md`
3. 读取 `knowledge/evomap-chunks/05-gdi.md`

## 注意事项

- 分块文件保持 <2KB 为宜
- 索引文件包含所有分块的标签和用途
- 更新知识时同步更新索引
- 原始完整文件可选保留用于全文检索
