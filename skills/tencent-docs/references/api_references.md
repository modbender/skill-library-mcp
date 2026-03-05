# 腾讯文档 MCP 工具完整参考

本文件包含腾讯文档 MCP 所有工具的通用 API 说明、详细调用示例、参数说明和返回值说明。

---

## 通用说明

### 响应结构

所有 API 返回都包含：
- `error`: 错误信息（成功时为空）
- `trace_id`: 调用链追踪 ID

### node_type 枚举值

| 值 | 说明 |
|---|---|
| wiki_folder | 文件夹 |
| wiki_tdoc | 在线文档（请求时使用） |
| wiki_file | 在线文档（返回值中使用） |
| link | 链接 |
| resource | 资源文件 |

### doc_type 枚举值

| 值 | 说明 |
|---|---|
| word | 文字处理文档 |
| excel | 电子表格 |
| form | 收集表 |
| slide | 幻灯片 |
| smartcanvas | 智能文档 |
| smartsheet | 智能表格 |
| board | 白板 |
| mind | 思维导图 |
| flowchart | 流程图 |

### NodeInfo 节点信息结构

```json
{
  "node_id": "节点 ID，同时也是 file_id",
  "title": "节点标题",
  "node_type": "节点类型",
  "has_child": true,
  "doc_type": "文档类型（仅 wiki_file 有效）",
  "url": "访问链接"
}
```

### StringMatrix 表格数据结构

```json
{
  "texts": {
    "rows": [
      {"values": ["单元格1", "单元格2"]},
      {"values": ["单元格3", "单元格4"]}
    ]
  }
}
```

数据从 A1 单元格开始，按行列顺序填充。

### 分页说明

- `query_space_node`：每页 20 条
- `search_space_file`：每页 40 条
- 使用 `has_next` 判断是否有更多数据
- 页码从 0 开始

---

## 工具调用示例

## 1. create_smartcanvas_by_markdown

### 功能说明
通过 Markdown 格式创建智能文档，排版美观，支持所有 Markdown 基本结构。

### 调用示例
```json
{
  "title": "项目需求文档",
  "markdown": "# 项目需求\n\n## 项目背景\n\n本项目旨在开发一套智能文档管理系统...\n\n## 功能需求\n\n- 文档创建功能\n- 文档编辑功能\n- 协作功能\n\n## 技术架构\n\n| 组件 | 技术选型 |\n|------|----------|\n| 前端 | React |\n| 后端 | Go |\n| 数据库 | MySQL |"
}
```

### 参数说明
- `title` (string, 必填): 文档标题
- `markdown` (string, 必填): UTF-8 格式的 Markdown 文本

### 返回值说明
```json
{
  "file_id": "doc_1234567890",
  "url": "https://docs.qq.com/doc/DV2h5cWJ0R1lQb0lH",
  "error": "",
  "trace_id": "trace_1234567890"
}
```

## 2. create_excel_by_markdown

### 功能说明
通过 Markdown 表格创建 Excel，适用于需要数据计算、筛选的场景。

### 调用示例
```json
{
  "title": "销售数据报表",
  "markdown": "| 日期 | 产品 | 销售额 | 销售量 |\n|------|------|--------|--------|\n| 2024-01-01 | 产品A | 10000 | 100 |\n| 2024-01-02 | 产品B | 15000 | 150 |"
}
```

### 参数说明
- `title` (string, 必填): 表格标题
- `markdown` (string, 必填): 包含表格的 Markdown 文本

### 返回值说明
```json
{
  "file_id": "sheet_1234567890",
  "url": "https://docs.qq.com/sheet/DV2h5cWJ0R1lQb0lH",
  "error": "",
  "trace_id": "trace_1234567890"
}
```

## 3. create_slide_by_markdown

### 功能说明
通过 Markdown 创建幻灯片，遵循特定层级结构。

### Markdown 层级结构规范

PPT 必须遵循严格的层级结构：

```
# 一级标题 → PPT 主标题（整个演示文稿的标题）
## 二级标题 → 章节标题（区分不同主题章节）
### 三级标题 → 页面标题（每个幻灯片的标题）
- 列表项 → 段落标题（每页 2-4 个）
    - 子列表项 → 正文内容（每段约 200 字）
```

### 调用示例
```json
{
  "title": "项目汇报",
  "markdown": "# 项目汇报\n\n## 项目背景\n\n### 项目概述\n\n- 项目目标\n    - 本项目旨在开发一套智能文档管理系统，提升团队协作效率\n- 项目范围\n    - 系统将涵盖文档创建、编辑、协作等功能\n\n### 市场分析\n\n- 市场需求\n    - 当前市场对智能文档管理系统的需求日益增长\n- 竞争分析\n    - 现有竞品在功能完整性方面存在不足"
}
```

### 参数说明
- `title` (string, 必填): 幻灯片标题
- `markdown` (string, 必填): 遵循幻灯片层级结构的 Markdown 文本

### 返回值说明
```json
{
  "file_id": "slide_1234567890",
  "url": "https://docs.qq.com/slide/DV2h5cWJ0R1lQb0lH",
  "error": "",
  "trace_id": "trace_1234567890"
}
```

## 4. create_mind_by_markdown

### 功能说明
通过 Markdown 创建思维导图，使用标题层级和列表嵌套表示结构。

### 调用示例
```json
{
  "title": "产品功能规划",
  "markdown": "# 产品功能规划\n\n## 核心功能\n\n- 文档管理\n    - 创建文档\n    - 编辑文档\n    - 版本控制\n\n## 协作功能\n\n- 实时协作\n- 评论系统\n- 权限管理"
}
```

### 参数说明
- `title` (string, 必填): 思维导图标题
- `markdown` (string, 必填): 层次化的 Markdown 文本

### 返回值说明
```json
{
  "file_id": "mind_1234567890",
  "url": "https://docs.qq.com/mind/DV2h5cWJ0R1lQb0lH",
  "error": "",
  "trace_id": "trace_1234567890"
}
```

## 5. create_flowchart_by_mermaid

### 功能说明
通过 Mermaid 语法创建流程图。

### 调用示例
```json
{
  "title": "用户登录流程",
  "mermaid": "graph TD\n    A[User Access] --> B{Logged in?}\n    B -->|Yes| C[Go to Home]\n    B -->|No| D[Go to Login Page]\n    D --> E[Enter Username and Password]\n    E --> F{Auth Success?}\n    F -->|Yes| C\n    F -->|No| G[Show Error Message]\n    G --> E"
}
```

### 参数说明
- `title` (string, 必填): 流程图标题
- `mermaid` (string, 必填): 不包含中文的 Mermaid 语法文本

### 返回值说明
```json
{
  "file_id": "flow_1234567890",
  "url": "https://docs.qq.com/flow/DV2h5cWJ0R1lQb0lH",
  "error": "",
  "trace_id": "trace_1234567890"
}
```

## 6. create_word_by_markdown

### 功能说明
通过 Markdown 创建 Word 文档。

### 调用示例
```json
{
  "title": "技术文档",
  "markdown": "# 技术文档\n\n## 系统架构\n\n本文档描述系统的技术架构设计...\n\n## 数据库设计\n\n| 表名 | 说明 |\n|------|------|\n| users | 用户表 |\n| documents | 文档表 |"
}
```

### 参数说明
- `title` (string, 必填): Word 文档标题
- `markdown` (string, 必填): UTF-8 格式的 Markdown 文本

### 返回值说明
```json
{
  "file_id": "word_1234567890",
  "url": "https://docs.qq.com/doc/DV2h5cWJ0R1lQb0lH",
  "error": "",
  "trace_id": "trace_1234567890"
}
```

## 7. query_space_node

### 功能说明
查询空间节点树结构，获取文件夹和文档列表。

### 调用示例
```json
{
  "parent_id": "folder_1234567890",
  "num": 0
}
```

### 参数说明
- `parent_id` (string, 可选): 父节点ID，为空时返回根节点
- `num` (uint32, 可选): 分页页码，从0开始，每页返回20个节点

### 返回值说明
```json
{
  "children": [
    {
      "node_id": "doc_1234567890",
      "title": "项目文档",
      "node_type": "wiki_file",
      "has_child": false,
      "doc_type": "smartcanvas",
      "url": "https://docs.qq.com/doc/DV2h5cWJ0R1lQb0lH"
    }
  ],
  "error": "",
  "has_next": false,
  "trace_id": "trace_1234567890"
}
```

## 8. create_space_node

### 功能说明
在空间中创建新节点（文件夹、文档或链接）。

### 调用示例
```json
{
  "parent_node_id": "folder_1234567890",
  "title": "新建页面文档1",
  "node_type": "wiki_tdoc",
  "wiki_tdoc_node": {
    "title": "新建页面文档",
    "doc_type": "smartcanvas"
  }
}
```

### 参数说明
- `parent_node_id` (string, 可选): 父节点ID，为空或在根目录创建时可不传
- `title` (string, 必填): 节点标题
- `node_type` (string, 必填): 节点类型（wiki_folder/wiki_tdoc/link）
- `is_before` (bool, 可选): 插入位置，true 表示插入到父节点子列表开头，false 表示插入到末尾
- `wiki_folder_node` (object, 可选): 文件夹节点配置，node_type 为 wiki_folder 时必填
- `wiki_tdoc_node` (object, 可选): 在线文档节点配置，node_type 为 wiki_tdoc 时必填
- `link_node` (object, 可选): 链接节点配置，node_type 为 link 时必填

### 返回值说明
```json
{
  "node_info": {
    "node_id": "doc_1234567890",
    "title": "新建页面文档",
    "node_type": "wiki_file",
    "has_child": false,
    "doc_type": "smartcanvas",
    "url": "https://docs.qq.com/doc/DV2h5cWJ0R1lQb0lH"
  },
  "error": "",
  "trace_id": "trace_1234567890"
}
```

## 9. search_space_file

### 功能说明
在空间内搜索文档。

### 调用示例
```json
{
  "pattern": "项目文档",
  "queryby": 2,
  "descending": true,
  "num": 0
}
```

### 参数说明
- `pattern` (string, 必填): 搜索关键词
- `queryby` (int32, 可选): 排序方式（1-创建时间，2-修改时间）
- `descending` (bool, 可选): 排序方向（true-降序）
- `num` (uint32, 可选): 分页页码，从0开始，每页返回40条

### 返回值说明
```json
{
  "nodes": [
    {
      "node_id": "doc_1234567890",
      "title": "项目文档",
      "node_type": "wiki_file",
      "has_child": false,
      "doc_type": "smartcanvas",
      "url": "https://docs.qq.com/doc/DV2h5cWJ0R1lQb0lH"
    }
  ],
  "error": "",
  "has_next": false,
  "trace_id": "trace_1234567890"
}
```

## 10. get_content

### 功能说明
获取文档完整内容。

### 调用示例
```json
{
  "file_id": "doc_1234567890"
}
```

### 参数说明
- `file_id` (string, 必填): 文档唯一标识符

### 返回值说明
```json
{
  "content": "# 项目文档\n\n这是文档的完整内容...",
  "error": "",
  "trace_id": "trace_1234567890"
}
```

## 11. batch_update_sheet_range

### 功能说明
批量更新表格单元格内容。数据将从表格末尾开始追加新行，不会覆盖已有内容。

### 调用示例
```json
{
  "file_id": "sheet_1234567890",
  "texts": {
    "rows": [
      {"values": ["姓名", "年龄", "部门"]},
      {"values": ["张三", "25", "技术部"]},
      {"values": ["李四", "30", "产品部"]}
    ]
  }
}
```

### 参数说明
- `file_id` (string, 必填): 表格唯一标识符
- `texts` (object, 必填): 二维文本数组，数据从 A1 单元格开始按行列顺序填充

### 返回值说明
```json
{
  "update_num": 6,
  "error": "",
  "trace_id": "trace_1234567890"
}
```

## 12. create_smartcanvas_element

### 功能说明
在已有智能文档中追加内容。

### 调用示例
```json
{
  "file_id": "doc_1234567890",
  "markdown": "## 新增内容\n\n这是追加到文档末尾的新内容..."
}
```

### 参数说明
- `file_id` (string, 必填): 文档唯一标识符
- `markdown` (string, 必填): 要追加的 Markdown 内容

### 返回值说明
```json
{
  "error": "",
  "trace_id": "trace_1234567890"
}
```
