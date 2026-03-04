---
name: async-web-search
version: 1.0.0
description: 使用 asyncio 進行高效的並行網頁資料搜尋與抓取。
author: YourName
openclaw:
  permissions:
    version: 1
    network:
      - "*" # 允許訪問外部網路進行搜尋
    exec:
      - "python3"
---

# Async Web Search Skill

此 Skill 允許 AI 使用 Python 的 `asyncio` 和 `aiohttp` 同時向多個來源（或針對多個關鍵字）發起網頁搜尋請求，大幅提升資料獲取速度。

## 使用指南
當使用者要求進行「深度搜尋」、「多維度搜尋」或「並行抓取」時，請呼叫此工具。

## 工具定義 (Tools)

### `parallel_search`
執行並行網頁搜尋。
- `queries`: 關鍵字列表 (List of strings)
- `max_results`: 每個關鍵字回傳的結果數量 (預設 3)

```python
# AI 會根據此定義生成執行指令：
# python3 search_engine.py --queries "AI 趨勢" "OpenClaw 教學" --max 3