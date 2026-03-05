# FH Skill Error Handling

本文档定义外部 OpenClaw 编排调用 `tool_cli.py` 时的错误处理和降级策略。

## 1) 鉴权与权限类

### 1.1 Token 缺失

触发条件：

- 未传 `Authorization: Bearer <token>`
- 且 body 中未传 `api_token`

典型报错：

- `API key required. Pass via Authorization: Bearer <token> or body api_token.`

处理策略：

1. 立即中止当前工具链。
2. 返回用户可执行指引：补充 `RAGTOP_API_TOKEN`。
3. 不重试（配置错误，重试无意义）。

### 1.2 Token 无效

触发条件：Token 不存在或失效。  
典型报错：`API-KEY is invalid!`

处理策略：

1. 中止调用。
2. 提示用户重新生成 Token（可通过 `/api/v1/ragtop/tool/new_token`）。
3. 不自动回退到匿名模式。

### 1.3 知识库越权

触发条件：`list_doc` 访问不属于当前租户的 `knowledge_id`。  
典型报错：`Not authorized to this knowledge base!`

处理策略：

1. 明确提示“当前 Token 无该知识库访问权限”。
2. 建议切换 Token 或更换可访问知识库。

## 2) 参数与请求类

### 2.1 `knowledge_id` 缺失

触发接口：`list_doc`、`retrieval`  
典型报错：`knowledge_id is required.`

处理策略：

1. 在外部编排层做前置校验。
2. 若缺失，先执行 `list_kb` 进行知识库解析，不直接调用下游。

### 2.2 `query/queries` 缺失或为空

触发接口：`retrieval`  
典型报错：

- `Either 'query' or 'queries' is required.`
- `query/queries cannot be empty.`

处理策略：

1. 优先构造 `queries`（2-4 条改写问题）。
2. 若用户输入过短，补充至少一条语义扩展 query 后重试一次。

### 2.3 `queries` 类型错误

触发条件：`queries` 不是数组。  
典型报错：`queries must be a list of strings.`

处理策略：

1. 将单字符串自动包裹为数组。
2. 过滤空字符串，保证最终数组非空。

## 3) 业务结果类

### 3.1 缺少 FH 必需知识库

触发条件：`list_kb` 未找到名称 `方案`、`案例`、`价格` 中任意一个。

处理策略：

1. 中止方案生成。
2. 明确列出缺失项，例如“缺少知识库：价格”。
3. 给出下一步：创建同名知识库或在 Skill 配置里改为映射名称。

### 3.2 召回为空（空 records）

触发条件：`retrieval` 返回 `records=[]` 或低质量结果。

处理策略（按顺序）：

1. 放宽参数：`score_threshold` 下调 0.05~0.1。
2. 扩展查询：增加同义词、业务别名、目标人群关键词。
3. 限定文件：先 `list_doc` 后传 `doc_ids` 精准召回。
4. 仍失败则返回“证据不足”，并建议用户补充上下文。

### 3.3 预算不满足

触发条件：达人组合总价超过预算。

处理策略：

1. 执行剔除策略：删除低优先级或低性价比达人，直至满足预算。
2. 输出“预算合规检查”段落，展示调整前后差异。
3. 若最低组合仍超预算，返回“预算不足以覆盖最小可行投放组合”。

## 4) LLM 生成质量类

### 4.1 幻觉风险

触发条件：输出出现未在召回记录中的达人、数字或结论。

处理策略：

1. 在生成前注入约束：“只能使用召回内容”。
2. 生成后做一致性检查：达人名称、价格、平台必须可回溯。
3. 不可回溯项直接删除或标注“待补充证据”。

### 4.2 输出格式不符合要求

触发条件：筛选阶段未输出 HTML 表格；最终方案缺预算检查。

处理策略：

1. 使用同一 Prompt 重试 1 次，并强调格式约束。
2. 再失败时降级输出结构化 Markdown，保留关键业务信息。

## 5) 建议的重试策略

- 网络/临时异常：指数退避重试 2 次（1s, 2s）
- 参数错误：不自动重试，先修正参数
- 业务空结果：允许 1 次“参数放宽 + query 扩展”重试
- 鉴权错误：不重试，直接返回配置修复建议
