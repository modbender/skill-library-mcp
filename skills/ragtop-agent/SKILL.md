---
name: ragtop-agent
description: 高级 RAG 助手，具备 Agentic RAG 思考能力。能够自动化管理 RAGTOP 知识库，并在执行深度调研任务时，调用 RAGTOP 后端接口。使用场景包括：(1) 列出知识库和文档，(2) 执行语义检索和深度分析。
metadata: { "openclaw": { "emoji": "🦖", "requires": { "env": ["RAGTOP_API_TOKEN"] }, "primaryEnv": "RAGTOP_API_TOKEN" } }
---

# ragtop-agent Skill

本 Skill 允许 AI 通过 `curl` 调用 RAGTOP 后端接口。AI 必须根据用户请求的性质，在“简单指令”与“深度调研”两种模式间切换。

## Configuration

The following environment variables are required:

- `RAGTOP_API_URL`: RAGTOP API base URL. Defaults to `http://10.71.10.71:9380` if not set.
- `RAGTOP_API_TOKEN`: Your RAGTOP API access token. Can be configured via the OpenClaw Web UI.

## 1. 核心工具构建指南 (How to build curl)

在调用以下接口前，请确保已获取环境变量 `${RAGTOP_API_URL}` 和 `${RAGTOP_API_TOKEN}`。如果 `${RAGTOP_API_URL}` 为空，请使用默认值 `http://10.71.10.71:9380`。

### A. 列出知识库 (list_kb)
用于获取所有可用的 `knowledge_id`。
```bash
curl -L -X POST "${RAGTOP_API_URL}/api/v1/ragtop/tool/list_kb" \
     -H "Authorization: Bearer ${RAGTOP_API_TOKEN}" \
     -H "Content-Type: application/json"
```

### B. 列出文档 (list_doc)
用于获取特定知识库内的 `doc_id` 列表，以便缩小检索范围。
- **Payload**: `{"knowledge_id": "string"}`
```bash
curl -L -X POST "${RAGTOP_API_URL}/api/v1/ragtop/tool/list_doc" \
     -H "Authorization: Bearer ${RAGTOP_API_TOKEN}" \
     -H "Content-Type: application/json" \
     -d '{"knowledge_id": "YOUR_KB_ID"}'
```

### C. 内容检索 (retrieval)
用于执行语义搜索。支持单查询或多查询。
- **Payload 关键参数**: 
  - `knowledge_id`: 必填。
  - `query`: 字符串（单查询）。
  - `queries`: 字符串数组（多查询，推荐用于复杂任务）。
  - `doc_ids`: 数组（可选，限定文件范围）。
  - `retrieval_setting`: `{"top_k": 16, "score_threshold": 0.3}`
```bash
curl -L -X POST "${RAGTOP_API_URL}/api/v1/ragtop/tool/retrieval" \
     -H "Authorization: Bearer ${RAGTOP_API_TOKEN}" \
     -H "Content-Type: application/json" \
     -d '{
       "knowledge_id": "YOUR_KB_ID",
       "queries": ["查询1", "查询2"],
       "retrieval_setting": {"top_k": 5}
     }'
```

## 2. 任务分类处理逻辑

### 情况 A：简单指令 (Simple Instructions)
**适用场景**: 用户询问“有哪些知识库？”、“这个库里有哪些文件？”等管理类问题。
**执行逻辑**:
1. 直接根据需求构建 `list_kb` 或 `list_doc` 的 `curl` 命令。
2. 将返回的 JSON 结果整理成易读的表格或列表告知用户。

### 情况 B：深度调研 (Deep Investigation / Agentic RAG)
**适用场景**: 用户提出具体业务问题、对比分析或需要跨文档总结。
**执行逻辑**:
1. **参考 [references/workflow.md](references/workflow.md)** 执行“分析-分解-检索-综合”流程。
2. **多步编排**:
   - 第一步：调用 `list_kb` 确定相关的知识库 ID。
   - 第二步（可选）：调用 `list_doc` 锁定相关文件。
   - 第三步：构建包含多个改写问题的 `retrieval` 请求，利用多路召回提高准确率。
   - 第四步：根据检索到的多个 chunks 进行逻辑推理和引用标注。

## 3. 运行规范
- **严禁**提及 `ragflow`，统一使用 `ragtop`。
- **引用必填**: 所有深度调研的回答必须注明引用的文档名称。
- **错误处理**: 如果 `curl` 返回非 SUCCESS，应检查 Token 有效性并告知用户。
