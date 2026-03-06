---
name: x-knowledge-base
version: 1.0.2
description: 自動收集 X 書籤並轉化為 Obsidian 知識庫，配備 AI 濃縮與交叉連結功能，支援自我進化趨勢分析
---

# X Knowledge Base

自動將 X (Twitter) 書籤轉化為 Obsidian Markdown 格式，建立個人知識庫。支援自我進化，根據書籤傾向動態調整關鍵字和趨勢分析。

## 功能

### 基礎功能
- **抓取書籤**：從 X/Twitter 抓書籤內容
- **完整原文**：使用 Jina AI 擷取完整文章內容
- **AI 濃縮**：自動產生一句話摘要、三個重點、應用場景
- **交叉連結**：根據標籤自動建立 wiki-link
- **Obsidian 格式**：YAML frontmatter + wiki-link

### 自我進化功能 ⭐
- **興趣趨勢追蹤**：每次存書籤，自動記錄標籤並統計頻率
- **動態關鍵字調整**：根據趨勢自動調整每日情報關鍵字
- **新興標籤偵測**：發現突然增加的標籤，自動加入追蹤
- **自適應推薦**：根據書籤傾向推薦相關內容

## 安裝

1. 設定 Twitter API 或 bird CLI
2. 設定 Brave Search API（用於趨勢分析）
3. 設定 Jina AI（用於文章擷取）
4. 設定 MiniMax API（用於 AI 濃縮）
5. 設定 Obsidian vault 路徑

## 使用方式

### 檢查書籤
```
"檢查我的書籤" - 抓取並儲存新書籤
```

### 自我進化
```
"今天的趨勢是什麼" - 興趣趨勢報告（含動態調整）
"我的興趣變化了嗎" - 偵測興趣轉變
```

### AI 濃縮
每次存書籤時，自動：
- 產生一句話摘要
- 列出三個重點
- 寫出應用場景

### 交叉連結
根據標籤自動建立相關書籤連結：
```
## 🔗 相關書籤
- [[書籤標題|標籤]]
```

## 檔案結構

```
x-knowledge-base/
├── SKILL.md
├── scripts/
│   ├── fetch_bookmarks.sh      # 抓書籤
│   ├── fetch_article.sh        # Jina AI 抓全文
│   └── save_obsidian.sh        # 存 Obsidian
├── tools/
│   ├── bookmark_enhancer.py    # AI 濃縮 + 交叉連結
│   └── trend_analyzer.py       # 自我進化趨勢分析
└── config/
    ├── interests.yaml           # 興趣標籤配置
    └── trends.json             # 趨勢數據（自動產生）
```

## 自我進化機制

### 1. 興趣趨勢追蹤

每次存書籤時：
1. 擷取書籤的所有標籤
2. 寫入 `trends.json`
3. 統計每個標籤的出現頻率
4. 計算趨勢分數

### 2. 動態關鍵字調整

根據趨勢數據，自動調整每日情報關鍵字：
- 頻率上升的標籤 → 提高優先級
- 新出現的標籤 → 加入觀察名單
- 下降的標籤 → 降低優先級

### 3. 新興標籤偵測

```python
# 趨勢分數計算
new_score = (current_count - previous_count) / previous_count * 100

if new_score > 50%:  # 超過 50% 成長
    alert("新興趨勢！")
```

### 4. 自適應學習

根據書籤傾向：
- 自動調整感興趣的主題權重
- 推薦相似內容
- 預測可能想看的書籤

## 技術細節

### Jina AI 擷取
```bash
https://r.jina.ai/http://x.com/用戶名/status/ID
```

### MiniMax API
- endpoint: https://api.minimax.io/anthropic/v1/messages
- model: MiniMax-M2.5

### 趨勢數據格式 (trends.json)
```json
{
  "last_updated": "2026-02-18T14:00:00Z",
  "tags": {
    "ai": { "count": 15, "trend": "+20%" },
    "video": { "count": 8, "trend": "+5%" },
    "seo": { "count": 12, "trend": "-10%" }
  },
  "new_emerging": ["vibe-coding", "claude-code"],
  "recommended_keywords": ["AI video generation", "Claude automation"]
}
```

## 差異化

| 功能 | x-bookmarks | 我們的 skill |
|------|-------------|--------------|
| 內容深度 | 摘要 | 完整原文 |
| AI 濃縮 | 無 | ✅ 有 |
| 儲存格式 | JSON | Obsidian Markdown |
| 趨勢分析 | 無 | ✅ 有 |
| 交叉連結 | 無 | ✅ 有 |
| **自我進化** | 無 | ✅ ⭐ 有 |

## 依賴

- Python 3.10+
- requests
- Jina AI（免費）
- MiniMax API
- Brave Search API（可選）

## 環境變數（必填/選填）

- `BIRD_AUTH_TOKEN`（必填）
- `BIRD_CT0`（必填）
- `MINIMAX_API_KEY`（選填，不填則略過 AI 濃縮）
- `MINIMAX_ENDPOINT`（選填，預設 `https://api.minimax.io/anthropic/v1/messages`）
- `MINIMAX_MODEL`（選填，預設 `MiniMax-M2.5`）
