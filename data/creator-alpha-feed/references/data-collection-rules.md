# 数据采集规则

## 总原则
- 能用 API 就用 API
- API 不可用时，降级 browser 抓取
- 报告中必须记录降级原因

## X(Twitter)
- 采集顺序：首页流 → 白名单账号 → 关键词
- 优先 browser 抓取（x.com）
- 评论抓取：只保留高价值评论（有数据/链接/实操洞察）

## 其他源
- Hacker News：API优先，失败则页面抓取
- TechCrunch：RSS/API优先，失败则页面抓取
- Reddit/ProductHunt/GitHub：按可用性 API 或 browser

## 质量过滤
- 优先：可复用方法论、实操步骤、副业变现相关
- 降权：纯热度、纯情绪、无信息增量内容

## 浏览器性能
- 同时 tab 不超过 7
- 抓完即关，结束保留 0~1 tab
