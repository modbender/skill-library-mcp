# FH Agentic Workflow (RAGTOP / OpenClaw)

本文档把 `api/cli/chat/fh/chat_fh.py` 的内部工作流重写为可由外部 OpenClaw Skill 执行的编排规范。

## 0) 前置约束

- 所有接口统一前缀：`/api/v1/ragtop/tool/*`
- 认证优先使用请求头：`Authorization: Bearer ${RAGTOP_API_TOKEN}`
- `RAGTOP_API_URL` 为空时默认：`http://10.71.10.71:9380`
- 命名中统一使用 `ragtop`，不要输出 `ragflow`

## 1) 工具清单

- `list_kb`：列出当前租户下知识库
- `list_doc`：列出某个知识库内文档
- `retrieval`：语义检索（支持 `query` 或 `queries`）

## 2) 四阶段编排（与 FH 对齐）

### Step1: RULES_SUMMARY（规则提炼）

目标：从“方案”知识库提炼可执行规则清单。  
输入：用户问题 `user_query`。  
工具调用：

1. `list_kb` 找到名称为 `方案` 的 `knowledge_id`。
2. 用 `retrieval` 对 `方案` 库做高覆盖召回（建议 `queries` 2-4 条）。

推荐 payload（示例）：

```bash
curl -L -X POST "${RAGTOP_API_URL}/api/v1/ragtop/tool/retrieval" \
  -H "Authorization: Bearer ${RAGTOP_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_id": "KB_RULES_ID",
    "queries": ["营销方案硬性要求", "预算与平台约束", "执行步骤与禁忌"],
    "retrieval_setting": {"top_k": 24, "score_threshold": 0.2}
  }'
```

LLM处理：使用 `FH_RULES_SUMMARY_PROMPT`（见 `prompts.md`）输出规则执行清单。  
输出：`rules_content`（后续步骤复用）。

### Step2: CASE_SUMMARY（案例总结）

目标：围绕用户需求提炼可复用成功模式。  
输入：`user_query`、案例知识库。  
工具调用：

1. 如需缩小范围，先 `list_doc`（可按文件名过滤 `doc_ids`）。
2. 用 `retrieval` 在“案例”库召回（建议 `top_k=5~10`）。

推荐 payload（示例）：

```bash
curl -L -X POST "${RAGTOP_API_URL}/api/v1/ragtop/tool/retrieval" \
  -H "Authorization: Bearer ${RAGTOP_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_id": "KB_CASES_ID",
    "queries": ["用户原始需求", "相似成功案例", "预算分配与执行节奏"],
    "retrieval_setting": {"top_k": 8, "score_threshold": 0.2}
  }'
```

LLM处理：使用 `FH_CASE_SUMMARY_PROMPT`。  
输出：`cases_summary`，并保留来源文档信息用于引用。

### Step3: KOL_SELECTOR（达人筛选）

目标：在预算和规则约束下筛选达人候选。  
输入：`rules_content`、`user_query`、价格知识库。  
工具调用：

1. 用 `retrieval` 在“价格”库做广覆盖召回（建议 `top_k=50~100`）。

推荐 payload（示例）：

```bash
curl -L -X POST "${RAGTOP_API_URL}/api/v1/ragtop/tool/retrieval" \
  -H "Authorization: Bearer ${RAGTOP_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_id": "KB_PRICES_ID",
    "queries": ["达人价格 表", "平台 预算 匹配", "KOL KOC 组合"],
    "retrieval_setting": {"top_k": 100, "score_threshold": 0.1}
  }'
```

LLM处理：使用 `FH_KOL_SELECTOR_PROMPT`，仅输出 HTML 表格或“未找到符合条件的达人”。  
输出：`filtered_price_table`。

### Step4: PLAN_GENERATION（方案生成）

目标：生成最终营销方案。  
输入：`rules_content`、`cases_summary`、`filtered_price_table`、`user_query`。  
工具调用：无新增调用（纯 LLM 合成）。  
LLM处理：使用 `FH_PLAN_GENERATION_PROMPT`。  
输出：最终方案（必须含预算合规检查、分层策略、引用来源）。

## 3) 结果格式建议

- 规则阶段：结构化清单（必须执行/建议执行）
- 案例阶段：简明策略摘要 + 可追溯来源
- 筛选阶段：HTML 表格（达人名称、平台、粉丝数、层级、价格、推荐理由）
- 最终阶段：完整方案（预算汇总、分层投放、执行节奏、达人明细、风险与兜底）

## 4) 外部编排伪代码

```text
1. kbs = list_kb()
2. kb_rules, kb_cases, kb_prices = resolve_by_name(kbs, ["方案","案例","价格"])
3. rules_records = retrieval(kb_rules, queries_for_rules)
4. rules_content = llm(FH_RULES_SUMMARY_PROMPT.format(rules_content=join(rules_records)))
5. case_records = retrieval(kb_cases, queries_for_cases)
6. cases_summary = llm(FH_CASE_SUMMARY_PROMPT.format(cases_content=join(case_records), user_query=user_query))
7. price_records = retrieval(kb_prices, queries_for_prices, top_k=100)
8. filtered_price_table = llm(FH_KOL_SELECTOR_PROMPT.format(rules=rules_content, kol_price_tables=join(price_records), user_query=user_query))
9. final_plan = llm(FH_PLAN_GENERATION_PROMPT.format(rules=rules_content, cases_summary=cases_summary, kol_price_tables=filtered_price_table, user_query=user_query))
10. return final_plan + citations
```
