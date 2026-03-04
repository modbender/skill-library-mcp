---
name: ragtop-planner
description: 面向外部 OpenClaw 的达人推广方案制定 Skill。基于 RAGTOP 三个工具接口（list_kb/list_doc/retrieval）执行四阶段工作流：规则提炼、案例总结、达人筛选、方案生成。
metadata: { "openclaw": { "emoji": "📈", "requires": { "env": ["RAGTOP_API_TOKEN"] }, "primaryEnv": "RAGTOP_API_TOKEN" } }
---

# ragtop-planner Skill

该 Skill 将达人推广方案制定流程改造为外部可执行编排，外部服务无需改后端即可调用。

## Configuration

必须配置以下环境变量：

- `RAGTOP_API_TOKEN`：API Token（必填）
- `RAGTOP_API_URL`：API Base URL（可选，默认 `http://10.71.10.71:9380`）

## 可用工具（tool_cli）

统一前缀：`${RAGTOP_API_URL}/api/v1/ragtop/tool`

### 1) list_kb

- 方法：`POST`
- 路径：`/list_kb`
- 认证：`Authorization: Bearer ${RAGTOP_API_TOKEN}`
- 返回（关键字段）：`data.kbs[]`、`data.total`

```bash
curl -L -X POST "${RAGTOP_API_URL}/api/v1/ragtop/tool/list_kb" \
  -H "Authorization: Bearer ${RAGTOP_API_TOKEN}" \
  -H "Content-Type: application/json"
```

### 2) list_doc

- 方法：`POST`
- 路径：`/list_doc`
- 必填：`knowledge_id`
- 返回（关键字段）：`data.docs[]`、`data.total`

```bash
curl -L -X POST "${RAGTOP_API_URL}/api/v1/ragtop/tool/list_doc" \
  -H "Authorization: Bearer ${RAGTOP_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"knowledge_id":"YOUR_KB_ID"}'
```

### 3) retrieval

- 方法：`POST`
- 路径：`/retrieval`
- 必填：`knowledge_id` + (`query` 或 `queries`)
- 可选：`doc_ids`、`retrieval_setting.top_k`、`retrieval_setting.score_threshold`
- 返回：`records[]`（注意该接口直接返回 `records`，不是 `data.records`）

```bash
curl -L -X POST "${RAGTOP_API_URL}/api/v1/ragtop/tool/retrieval" \
  -H "Authorization: Bearer ${RAGTOP_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_id":"YOUR_KB_ID",
    "queries":["查询A","查询B"],
    "retrieval_setting":{"top_k":16,"score_threshold":0.3}
  }'
```

## FH Workflow（外部执行）

请按顺序执行以下四步：

1. `RULES_SUMMARY`：从名称为“方案”的知识库召回规则并总结执行清单。
2. `CASE_SUMMARY`：从名称为“案例”的知识库召回并总结成功模式。
3. `KOL_SELECTOR`：从名称为“价格”的知识库召回候选达人并生成 HTML 筛选表。
4. `PLAN_GENERATION`：融合规则、案例、达人表和用户需求生成最终方案。

详细步骤见：

- `references/workflow.md`
- `references/prompts.md`
- `references/error_handling.md`

## 执行规则

- 必须先 `list_kb`，并匹配三个知识库名称：`方案`、`案例`、`价格`。
- 优先使用 `queries` 多路召回；仅在简单请求时用单 `query`。
- 如用户指定文件范围，先调用 `list_doc`，再把 `doc_ids` 传给 `retrieval`。
- 最终回答必须做预算合规检查（总价 <= 用户预算）。
- 所有关键结论必须可追溯到召回来源（文档名或记录来源）。
- 输出中统一使用 `ragtop` 命名。

## 推荐默认参数

- 规则召回：`top_k=24`，`score_threshold=0.2`
- 案例召回：`top_k=8`，`score_threshold=0.2`
- 价格召回：`top_k=100`，`score_threshold=0.1`

## 失败与降级

- 鉴权失败：提示用户检查 Token 是否有效或是否过期。
- 知识库缺失：明确指出缺少 `方案/案例/价格` 中的哪个库。
- 召回为空：建议用户细化关键词、指定文档或降低阈值后重试。
- 预算冲突：要求剔除低优先级达人，直至满足预算。
