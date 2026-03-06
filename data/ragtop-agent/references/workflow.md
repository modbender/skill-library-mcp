# Agentic RAG Workflow Guidelines (RAGTOP)

本参考文件定义了处理复杂用户问题时的 Agentic RAG 思考流程。

## 核心流程 (Thought Chain)

当用户提出需要从知识库获取信息的问题时，必须遵循以下思维链：

### 1. 意图识别与初步定位
- **动作**: 调用 `curl -X POST "${RAGTOP_API_URL}/api/v1/ragtop/tool/list_kb" -H "Authorization: Bearer ${RAGTOP_API_TOKEN}"`。
- **目标**: 识别哪些知识库与用户问题相关。
- **策略**: 如果存在多个潜在相关的知识库，应根据其描述字段进行筛选。

### 2. 范围缩小 (可选)
- **动作**: 调用 `curl -X POST "${RAGTOP_API_URL}/api/v1/ragtop/tool/list_doc" -H "Authorization: Bearer ${RAGTOP_API_TOKEN}" -d '{"knowledge_id": "KB_ID"}'`。
- **场景**: 当用户提到特定文件名，或问题明显仅指向某类文档时。
- **目标**: 获取 `doc_ids` 以缩小检索范围，提高响应速度和准确率。

### 3. 问题分析与改写
- **判断**: 用户的问题是否模糊？是否包含多个子问题？是否需要背景补充？
- **动作**: 
  - **简单问题**: 直接使用原查询。
  - **复杂/多维问题**: 将原问题分解为 2-4 个不同侧重点的 `queries` 参数列表。
  - **HyDE (虚拟文档) 模式**: 生成一个理想的答案摘要作为查询语句之一。

### 4. 深度检索 (Multi-Perspective Retrieval)
- **动作**: 调用 `curl -X POST "${RAGTOP_API_URL}/api/v1/ragtop/tool/retrieval" -H "Authorization: Bearer ${RAGTOP_API_TOKEN}" -d '{"knowledge_id": "KB_ID", "query": "xxx"}'`。
- **参数优化**:
  - 提供 `queries` 列表进行多路召回（如果适用）。
  - 传入 `doc_ids`（如果第 2 步已确定）。
  - 根据对严谨性的要求调整 `score_threshold`（建议默认 0.2，核心数据 0.3+）。

### 5. 结果综合与回答生成
- **分析**: 检查检索到的 chunks 之间是否存在冲突？是否覆盖了问题的所有维度？
- **生成**: 
  - 必须基于检索到的内容。
  - 必须包含引用说明（注明来源文档）。
  - 如果检索结果不足以回答问题，应明确指出并建议用户调整查询方向。

## 场景示例

### 场景 A：查询所有产品说明书
1. `list_kb` 找到 "Product_Docs" ID。
2. 发现文档很多，用户问的是 "X1 手机的续航"。
3. `list_doc` 过滤出文件名包含 "X1" 的 `doc_id`。
4. `retrieval` 传入该 `doc_id`。

### 场景 B：比较两个项目的进度
1. `list_kb` 找到 "Project_Reports"。
2. 分解问题为 "项目 A 的最新进展" 和 "项目 B 的最新进展"。
3. `retrieval` 传入 `queries=["项目 A 进度", "项目 B 进度"]`。
4. 综合两份结果进行对比回答。
