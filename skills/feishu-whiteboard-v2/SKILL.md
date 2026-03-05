---
name: feishu-whiteboard
description: Create and fill Feishu/Lark Whiteboard (画板) content from natural language requests by generating Mermaid or PlantUML code and calling Feishu Open API directly. Use when user asks to draw流程图/思维导图/架构图/时序图 in Feishu docs or wants AI-generated board diagrams.
---

# Feishu Board (画板) Skill

将用户自然语言需求转成 Mermaid/PlantUML，然后通过飞书开放平台 API 创建并填充画板。

## 核心流程（必须按顺序）

1. **理解意图**：判断图类型（流程图、时序图、类图、甘特图、思维导图等）。
2. **生成图语法**：优先生成 Mermaid；若用户明确要求 PlantUML 则用 PlantUML。
3. **调用脚本**：执行 `scripts/feishu-board.js` 完成“创建画板块 + 填充节点”。
4. **回报结果**：返回文档链接、画板 token、节点创建结果。

## 环境变量

在执行前确认：

- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`

可选：

- `FEISHU_BASE_URL`（默认 `https://open.feishu.cn/open-apis`）

## 参数约定

- `docId`: 文档 ID（非完整 URL）
- `parentBlockId`: 插入位置父块（通常可先用 `docId` 作为根块）
- `syntaxType`: `mermaid` 或 `plantuml`
- `codeFile`: 临时代码文件路径

## 推荐执行方式

先把图语法写入临时文件，再执行一体化命令：

```bash
node skills/feishu-whiteboard/scripts/feishu-board.js run \
  --doc-id <DOC_ID> \
  --parent-block-id <PARENT_BLOCK_ID> \
  --syntax-type mermaid \
  --code-file /tmp/board.mmd
```

## 子命令

- `run`: 一步完成（创建画板块 + 填充语法节点）
- `create-whiteboard`: 只创建画板块并解析 whiteboard token
- `fill-diagram`: 向已有画板 token 填充 Mermaid/PlantUML
- `get-tenant-token`: 仅测试鉴权

## 失败处理

- 若报权限不足，提示补齐 scope（至少）：
  - `board:whiteboard:node:create`
  - `board:whiteboard:node:read`
  - `docx:document`
- 若无法从 block 解析出 token：先返回 `block_id`，提示用户检查文档块结构权限或改用已有 whiteboard token。

## 参考资料

需要接口细节时读取：

- `references/feishu-board-api.md`
