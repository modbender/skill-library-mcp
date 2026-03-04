# Deep Search API 参考文档

## 端点

| 方法 | URL |
|------|-----|
| POST | `https://api.unifuncs.com/deepsearch/v1/chat/completions` |
| POST | `https://api.unifuncs.com/deepsearch/v1/create_task` |
| GET | `https://api.unifuncs.com/deepsearch/v1/query_task?task_id={TASK_ID}` |

## 模型版本

| 模型 | 说明 |
|------|------|
| s2 | 最新版本，推荐使用 |
| s1 | 旧版本 |

## 请求参数

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| model | string | 是 | 模型版本：`s2`、`s1` |
| messages | array | 是 | 消息数组，OpenAI格式 |
| stream | boolean | 否 | 是否流式响应，默认 `true` |
| max_depth | number | 否 | 研究最大深度，建议 `25` |
