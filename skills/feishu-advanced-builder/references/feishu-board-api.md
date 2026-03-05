# Feishu Board API Notes（给 Agent 的精简参考）

## 目标

从自然语言生成图表（Mermaid/PlantUML），并写入飞书画板（Whiteboard）。

## 已验证/参考到的关键接口

> 说明：官方文档页面为前端动态渲染，直接抓取文本常为空。以下以用户提供信息 + Feishu-MCP 源码行为为准。

### 1) 获取 tenant_access_token

- `POST /auth/v3/tenant_access_token/internal`
- Base URL: `https://open.feishu.cn/open-apis`
- Body:

```json
{
  "app_id": "<FEISHU_APP_ID>",
  "app_secret": "<FEISHU_APP_SECRET>"
}
```

### 2) 在 Docx 中创建 Whiteboard 块

- `POST /docx/v1/documents/{docId}/blocks/{parentBlockId}/children?document_revision_id=-1`
- 关键：`block_type = 43`（whiteboard）

示例：

```json
{
  "children": [
    { "block_type": 43 }
  ],
  "index": 0
}
```

创建后建议再请求块详情，解析 whiteboard token：

- `GET /docx/v1/documents/{docId}/blocks/{blockId}?document_revision_id=-1`

### 3) 向画板写入 Mermaid/PlantUML

根据 Feishu-MCP `feishuApiService.ts`：

- `POST /board/v1/whiteboards/{whiteboardToken}/nodes/plantuml`
- Body 字段：

```json
{
  "plant_uml_code": "<Mermaid or PlantUML source>",
  "style_type": 1,
  "syntax_type": 2
}
```

- `syntax_type`:
  - `1` = PlantUML
  - `2` = Mermaid

## 权限（最小集合）

- `board:whiteboard:node:create`
- `board:whiteboard:node:read`
- `docx:document`

## 与用户研究一致的点

- 两阶段流程：先在文档中创建 whiteboard 块，再填充图语法。
- 白板能力由 `board` 命名空间接口承载。
- `block_type: 43` 对应 whiteboard。

## 常见失败

1. **code != 0 / 403**：权限未开通或未发布审核。
2. **token 解析失败**：块详情字段结构可能因版本变化而不同；需打印 block detail 进行字段定位。
3. **语法渲染失败**：Mermaid/PlantUML 本身语法错误，先本地检查语法。
