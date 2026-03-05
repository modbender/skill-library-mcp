---
name: instagram-saver
description: 當使用者貼上 Instagram 連結時，自動下載該貼文的所有高解析度圖片與影片。使用 Cobalt API 進行解析，支援多圖貼文，若為私人帳號會自動回報。
---

# Instagram Saver

當偵測到 Instagram 連結時，使用 Cobalt API 解析並下載內容。

## Workflow

### Step 1 — 準備 API 請求 (Prepare Request)

當使用者提供 Instagram 網址（`url`）時，請準備執行 `curl` 指令。我們將使用 Cobalt API 來獲取真實的媒體下載連結。

**API Endpoint:** `https://api.cobalt.tools/api/json`
**Header:** `Content-Type: application/json`
**Header:** `Accept: application/json`
**Body:** `{"url": "{url}"}`

### Step 2 — 發送請求與解析 (Fetch & Parse)

執行以下 `curl` 指令（請將 `{url}` 替換為實際連結）：

```bash
curl -X POST [https://api.cobalt.tools/api/json](https://api.cobalt.tools/api/json) \
     -H "Content-Type: application/json" \
     -H "Accept: application/json" \
     -d '{"url": "{url}"}'