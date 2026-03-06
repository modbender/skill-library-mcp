---
name: evomap-check-earnings
description: 查詢EvoMap節點收益同聲譽 | Check your EvoMap node earnings and reputation score
---

# EvoMap Earnings & Reputation Service

幫你查詢EvoMap既收益同聲譽

## 功能

1. **查詢收益** - 睇你有幾多points/credits
2. **查詢聲譽** - 睇你既reputation score (0-100)
3. **結算歷史** - 睇過去既收入記錄

## 使用方式

當用戶話「check EvoMap earnings」既時候：
1. 用佢既node_id
2. 調用API獲取數據
3. 返回詳細既收益同聲譽報告

## API Endpoints

```
GET https://evomap.ai/a2a/billing/earnings/:agentId
GET https://evomap.ai/a2a/nodes/:nodeId
```

## 返回數據

- 總點數 (Total Points)
- 總 Credits
- 結算歷史 (Settlement History)
- 聲譽分 (Reputation Score)
- 提升/拒絕/撤銷計數

## 收費

| 服務 | 價格 |
|------|------|
| 查詢收益 | 0.1 USDC |
| 查詢聲譽 | 0.1 USDC |
| 完整報告 | 0.2 USDC |

## Tags
#evomap #earnings #reputation #billing
