# USDA FoodData Central (FDC) 快速参考 / Quick Reference

- Base URL: https://api.nal.usda.gov/fdc/v1
- 认证 / Authentication：API Key（query 参数 / query parameter `api_key`）

## 常用端点 / Common Endpoints
- POST /foods/search
- GET /food/{fdcId}

## 常见错误 / Common Errors
- 401 Unauthorized: API key 无效或缺失 / Invalid or missing API key
- 403 Forbidden: 权限不足 / Insufficient permissions
- 429 Too Many Requests: 触发限速（稍后再试）/ Rate limited (retry later)
- 5xx: 服务端错误 / Server error

## 建议 / Recommendations
- 搜索结果有限，优先 Foundation / SR Legacy / Survey (FNDDS) / Search results are limited; prefer Foundation / SR Legacy / Survey (FNDDS) data types
- 复合菜品命中率较低，建议拆成食材 / Composite dishes have low match rates; decompose into individual ingredients
