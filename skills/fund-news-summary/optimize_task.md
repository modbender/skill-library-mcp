# 优化任务：基金新闻并发性能

## 当前问题
1. _mock_search 是模拟方法，需要改成真正调用搜索 API
2. 需要用 aiohttp 异步调用 Brave Search API
3. 保持现有的 RateLimiter 并发控制

## 优化目标
1. 真正实现 Brave Search API 调用
2. 添加更智能的错误处理和指数退避重试
3. 使用 asyncio.gather 并发处理 5 个基金，但受限于 RateLimiter

## Brave Search API 格式
- URL: https://api.search.brave.com/res/v1/web/search
- Headers: X-Subscription-Token: {BRAVE_API_KEY}
- 参数: q={query}, count=5, search_lang=zh

## 输出格式
保持现有的 Telegram 报告格式不变

请编辑 fund_news.py 实现以上优化
