# Deep Research API 参考文档

## 端点

| 方法 | URL |
|------|-----|
| POST | `https://api.unifuncs.com/deepresearch/v1/chat/completions` |
| POST | `https://api.unifuncs.com/deepresearch/v1/create_task` |
| GET | `https://api.unifuncs.com/deepresearch/v1/query_task?task_id={TASK_ID}` |

## 模型版本

| 模型 | 说明 |
|------|------|
| u2 | 最新版本，推荐使用 |
| u1 | 通识模式 |
| u1-pro | 专业模式 |

## 输出类型 (output_type)

| 值 | 说明 |
|------|------|
| report | 万字报告（默认） |
| summary | 精炼摘要 |
| wechat-article | 微信公众号文章 |
| xiaohongshu-article | 小红书文章 |
| zhihu-article | 知乎文章 |
