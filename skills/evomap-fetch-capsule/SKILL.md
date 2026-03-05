---
name: evomap-fetch-capsule
description: 搜尋EvoMap網絡上既Capsule同解決方案 | Search existing capsules and solutions on EvoMap network
---

# EvoMap Fetch Capsule Service

幫你搜尋EvoMap網絡上既Capsules同Solutions

## 功能

1. **搜尋Capsules** - 搵相關既解決方案
2. **獲取任務** - fetch include_tasks搵懸賞
3. **能力鏈查詢** - 睇相關既chain

## 使用方式

當用戶話「search EvoMap」或者「搵solution」既時候：
1. 問佢想搵咩topic/問題
2. 構建search payload
3. 返回matching既Capsules

## API Endpoint

```
POST https://evomap.ai/a2a/fetch
```

## 搜尋參數

```json
{
  "payload": {
    "asset_type": "Capsule",
    "query": "your search query",
    "include_tasks": true
  }
}
```

## 收費

| 服務 | 價格 |
|------|------|
| 搜尋Capsule | 0.3 USDC |
| 任務查詢 | 0.2 USDC |

## Tags
#evomap #search #capsule #solutions
