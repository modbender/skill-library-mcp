---
name: tencent-docs
description: 腾讯文档，支持创建和管理腾讯文档的各类在线文档。当用户需要：(1) 创建在线文档（Word、Excel、幻灯片、智能文档、思维导图、流程图）(2) 查询或搜索文档空间 (3) 管理空间节点和文件夹 (4) 获取文档内容 (5) 更新表格数据 时使用此 skill。
---

# 腾讯文档 MCP 使用指南

腾讯文档 MCP 提供了一套完整的在线文档操作工具，支持创建、查询、编辑多种类型的在线文档。

## 📚 详细参考文档

如需查看每个工具的详细调用示例、参数说明和返回值说明，请参考：
- `references/tool_examples.md` - 包含所有工具的完整调用示例、参数说明、返回值说明及 API 结构、枚举值说明

## ⚙️ 配置要求

### 必需配置

使用腾讯文档 MCP 前，需要先获取访问 Token：

1. 访问 [https://docs.qq.com/open/document/mcp/get-token/](https://docs.qq.com/open/document/mcp/get-token/) 获取你的 Token
2. 将 Token 保存到环境变量 `TENCENT_DOCS_TOKEN`，或在调用时替换 `<YOUR_TOKEN>`

> ⚠️ **如果用户未配置 Token**，请引导用户访问上方链接获取 Token，否则所有工具调用将返回鉴权失败。

### MCP 服务地址

- **访问地址**：`https://docs.qq.com/openapi/mcp`
- 所有请求需在 Header 中携带：`Authorization: <YOUR_TOKEN>`

### 可选配置

- `TENCENT_DOCS_MCP_URL`：MCP 服务地址，默认 `https://docs.qq.com/openapi/mcp`

---

## 🔧 调用方式

腾讯文档 MCP 的标准配置名称为 **`tencent-docs`**，支持以下两种调用方式：

### 方式一：MCP Client 调用（推荐）

**如果当前 Agent 内置了 MCP Client**，请按以下方式配置后直接调用工具，无需手动执行 curl 命令：

```json
{
  "mcpServers": {
    "tencent-docs": {
      "url": "https://docs.qq.com/openapi/mcp",
      "headers": {
        "Authorization": "<YOUR_TOKEN>"
      }
    }
  }
}
```

> 💡 将 `<YOUR_TOKEN>` 替换为你的实际 Token。如未配置，请引导用户访问 [https://docs.qq.com/open/document/mcp/get-token/](https://docs.qq.com/open/document/mcp/get-token/) 获取。

配置完成后，直接通过 MCP Client 调用工具，格式为：

```
mcp: tencent-docs
tool: <工具名称>
arguments: { ... }
```

---

### 方式二：curl 调用（不支持 MCP Client 时使用）

**如果当前 Agent 不支持 MCP Client**，使用 exec 工具执行 curl 命令调用 MCP 服务，将 `arguments` 中的参数替换为实际值：

```bash
DOCS_URL="${TENCENT_DOCS_MCP_URL:-https://docs.qq.com/openapi/mcp}"
DOCS_AUTH="Authorization: ${TENCENT_DOCS_TOKEN}"

curl -s -X POST "$DOCS_URL" \
  -H "$DOCS_AUTH" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"<工具名>","arguments":{<参数>}},"id":1}'
```

### 支持的工具完整列表

> ⚠️ **以下工具列表仅供参考，实际可用工具以调用 `tools/list` 接口返回结果为准。**
>
> 获取最新工具列表：
> ```bash
> curl -s -X POST "${TENCENT_DOCS_MCP_URL:-https://docs.qq.com/openapi/mcp}" \
>   -H "Authorization: ${TENCENT_DOCS_TOKEN}" \
>   -H "Content-Type: application/json" \
>   -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}'
> ```

| 工具名称 | MCP 调用格式 | 功能说明 |
|---------|-------------|---------|
| create_smartcanvas_by_markdown | `create_smartcanvas_by_markdown` | ⭐ 创建智能文档（首选） |
| create_excel_by_markdown | `create_excel_by_markdown` | 创建 Excel 表格 |
| create_slide_by_markdown | `create_slide_by_markdown` | 创建幻灯片 |
| create_mind_by_markdown | `create_mind_by_markdown` | 创建思维导图 |
| create_flowchart_by_mermaid | `create_flowchart_by_mermaid` | 创建流程图 |
| create_word_by_markdown | `create_word_by_markdown` | 创建 Word 文档 |
| query_space_node | `query_space_node` | 查询空间节点 |
| create_space_node | `create_space_node` | 创建空间节点 |
| search_space_file | `search_space_file` | 搜索空间文件 |
| get_content | `get_content` | 获取文档内容 |
| batch_update_sheet_range | `batch_update_sheet_range` | 批量更新表格 |
| create_smartcanvas_element | `create_smartcanvas_element` | 追加智能文档内容 |

**详细调用示例请参考：`references/tool_examples.md`**

## ⭐ 重要：文档类型选择指南

> **首选推荐：智能文档（smartcanvas）**
>
> 在创建文档时，**优先使用 `create_smartcanvas_by_markdown`** 创建智能文档，原因如下：
> - 📝 排版效果更美观，自动优化布局
> - 🎨 支持更丰富的格式（标题、段落、列表、表格、代码块、引用、图片等）
> - 🔧 支持后续通过 `create_smartcanvas_element` 追加内容
> - 📱 跨平台显示效果一致

### 文档类型选择决策树

```
需要创建什么类型的内容？
│
├─ 通用文档内容（报告、笔记、文章等）
│   └─ ✅ 使用 create_smartcanvas_by_markdown（首选）
│
├─ 数据表格（需要计算、筛选、统计）
│   └─ ✅ 使用 create_excel_by_markdown
│
├─ 演示文稿（需要逐页展示、投影演示）
│   └─ ✅ 使用 create_slide_by_markdown
│
├─ 层次化知识整理（知识图谱、大纲）
│   └─ ✅ 使用 create_mind_by_markdown
│
├─ 流程/架构展示（流程图、时序图）
│   └─ ✅ 使用 create_flowchart_by_mermaid
│
└─ 传统 Word 格式导出需求
    └─ 使用 create_word_by_markdown（仅在明确需要时）
```

## 支持的文档类型

| 类型 | doc_type | 推荐度 | 说明 |
|------|----------|--------|------|
| **智能文档** | smartcanvas | ⭐⭐⭐ **首选** | 排版美观，支持丰富组件 |
| Excel | excel | ⭐⭐⭐ | 数据表格专用 |
| 幻灯片 | slide | ⭐⭐⭐ | 演示文稿专用 |
| 思维导图 | mind | ⭐⭐⭐ | 知识图谱专用 |
| 流程图 | flowchart | ⭐⭐⭐ | 流程展示专用 |
| Word | word | ⭐⭐ | 传统格式，排版一般 |
| 收集表 | form | ⭐⭐ | 表单收集 |
| 智能表格 | smartsheet | ⭐⭐ | 高级表格 |
| 白板 | board | ⭐⭐ | 在线白板 |

## 工具列表

> 📖 所有工具的完整调用示例、参数说明和返回值说明，请查阅 `references/tool_examples.md`
>
> ⚠️ **此 skill 中的工具列表仅作使用指导，实际可用工具以调用 `tools/list` 接口返回结果为准。** 如遇工具不存在或参数不符，请先执行 `tools/list` 获取最新工具定义。

### 1. 创建文档类

#### ⭐ create_smartcanvas_by_markdown（首选）

**通用文档首选工具**，通过 Markdown 创建智能文档，排版美观，支持所有 Markdown 基本结构。

**适用场景**：
- 📄 文档、报告、笔记、文章
- 📋 会议纪要、方案说明
- 📚 技术文档、教程
- 🗒️ 任何需要美观排版的内容

> 📖 调用示例请参考：[api_references.md - create_smartcanvas_by_markdown](references/api_references.md#1-create_smartcanvas_by_markdown)

#### create_excel_by_markdown

通过 Markdown 表格创建 Excel，适用于需要数据计算、筛选的场景。

**适用场景**：数据报表、统计表格、需要公式计算的场景

> 📖 调用示例请参考：[api_references.md - create_excel_by_markdown](references/api_references.md#2-create_excel_by_markdown)

#### create_slide_by_markdown

通过 Markdown 创建幻灯片，遵循特定层级结构（`#` 主标题 → `##` 章节 → `###` 页面 → `-` 段落 → 缩进子项正文）。

**适用场景**：演示文稿、项目汇报、培训材料

> 📖 调用示例请参考：[api_references.md - create_slide_by_markdown](references/api_references.md#3-create_slide_by_markdown)

#### create_mind_by_markdown

通过 Markdown 创建思维导图，使用标题层级和列表嵌套表示结构。

**适用场景**：知识图谱、大纲整理、头脑风暴

> 📖 调用示例请参考：[api_references.md - create_mind_by_markdown](references/api_references.md#4-create_mind_by_markdown)

#### create_flowchart_by_mermaid

通过 Mermaid 语法创建流程图，mermaid 字段内容必须全部使用英文。

**适用场景**：流程图、时序图、架构图

> 📖 调用示例请参考：[api_references.md - create_flowchart_by_mermaid](references/api_references.md#5-create_flowchart_by_mermaid)

#### create_word_by_markdown

通过 Markdown 创建 Word 文档。**注意：仅在用户明确要求 Word 格式时使用，否则请使用 smartcanvas**。

> 📖 调用示例请参考：[api_references.md - create_word_by_markdown](references/api_references.md#6-create_word_by_markdown)

### 2. 空间管理类

#### query_space_node

查询空间节点树结构，获取文件夹和文档列表。支持分页，每页返回 20 条。

> 📖 调用示例请参考：[api_references.md - query_space_node](references/api_references.md#7-query_space_node)

#### create_space_node

在空间中创建新节点，支持创建文件夹（`wiki_folder`）、在线文档（`wiki_tdoc`）、链接（`link`）。

> 📖 调用示例请参考：[api_references.md - create_space_node](references/api_references.md#8-create_space_node)

#### search_space_file

在空间内搜索文档，支持按关键词匹配标题和内容，支持分页，每页返回 40 条。

> 📖 调用示例请参考：[api_references.md - search_space_file](references/api_references.md#9-search_space_file)

### 3. 文档操作类

#### get_content

获取文档完整内容，传入 `file_id` 返回文档正文文本。

> 📖 调用示例请参考：[api_references.md - get_content](references/api_references.md#10-get_content)

#### batch_update_sheet_range

批量更新表格单元格内容（仅适用于 Excel），数据从表格末尾追加，不覆盖已有内容。

> 📖 调用示例请参考：[api_references.md - batch_update_sheet_range](references/api_references.md#11-batch_update_sheet_range)

#### create_smartcanvas_element

在已有智能文档中追加内容，这是 smartcanvas 的独特优势。

> 📖 调用示例请参考：[api_references.md - create_smartcanvas_element](references/api_references.md#12-create_smartcanvas_element)

## 常见工作流

### 创建通用文档（推荐方式）

```
1. 优先调用 create_smartcanvas_by_markdown 创建智能文档
2. 从返回结果中获取 file_id 和 url
3. 如需追加内容，调用 create_smartcanvas_element
```

### 组织文档到指定目录

1. 调用 `query_space_node` 查找目标文件夹
2. 调用 `create_space_node` 在目标位置创建文档节点（doc_type 优先选择 smartcanvas）

### 搜索并读取文档

1. 调用 `search_space_file` 搜索文档
2. 从结果中获取 `node_id`（即 `file_id`）
3. 调用 `get_content` 获取文档内容

## 注意事项

- **默认使用 smartcanvas**：除非用户明确指定其他格式，否则创建文档时优先使用智能文档
- Markdown 内容使用 UTF-8 格式，特殊字符无需转义
- 幻灯片必须遵循层级结构，每页包含 2-4 个段落标题
- 分页查询每页返回 20-40 条记录，使用 `has_next` 判断是否有更多
- `node_id` 同时也是文档的 `file_id`
- `create_flowchart_by_mermaid` 的 mermaid 内容必须全部使用英文