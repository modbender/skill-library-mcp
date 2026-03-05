# gog 安裝、驗證與使用教學

> 本教學是針對你現在這台 Mac、這個 Clawdbot 環境寫的實戰版說明。

---

## 1. gog 是什麼？

`gog` 是一個 Google Workspace CLI，讓你用指令操作：

- Gmail：搜尋、寄信、草稿、回覆
- Calendar：建立 / 查詢 / 更新行程
- Drive：搜尋檔案、看 metadata
- Docs：匯出內容
- Sheets：讀寫試算表
- Contacts：列出聯絡人

在 Clawdbot 裡，我就是透過 `gog` 幫你排行程、寄信、看雲端檔案。

---

## 2. 安裝 gog

> 這步你已經完成，以下是完整流程，給你或未來別台機器參考。

### 2.1 透過 Homebrew 安裝

```bash
brew install steipete/tap/gogcli
```

確認安裝：

```bash
gog --version
```

---

## 3. 準備 OAuth 憑證（一次性）

gog 需要一組 **OAuth client** 才能幫你操作 Gmail / Calendar 等服務。

### 3.1 在 Google Cloud Console 建立 OAuth Client

1. 前往：<https://console.cloud.google.com/apis/credentials>
2. 選擇或建立一個 GCP 專案。
3. 點 **「建立憑證 → OAuth 用戶端 ID」**。
4. 應用程式類型選：**桌面應用程式（Desktop app）**。
5. 建立後，下載 JSON 檔（檔名類似：
   `client_secret_XXXXXXXXXXXX-xxxxx.apps.googleusercontent.com.json`）。

### 3.2 把 JSON 放到 gog 預期的位置

在這台 Mac 上，我們用的是：

```bash
/Users/user/Library/Application Support/gogcli/credentials.json
```

做法：

```bash
mkdir -p "/Users/user/Library/Application Support/gogcli"
mv ~/Downloads/client_secret_*.json \
  "/Users/user/Library/Application Support/gogcli/credentials.json"
```

### 3.3 告訴 gog 使用這個憑證

```bash
gog auth credentials "/Users/user/Library/Application Support/gogcli/credentials.json"
```

---

## 4. 為每個帳號授權（auth add）

你目前已經幫三個帳號開通：

- `aiagentg888@gmail.com`
- `jackychen0615@gmail.com`
- `step1nework016@gmail.com`

### 4.1 基本授權指令

格式：

```bash
gog auth add <email> --services gmail,calendar,drive,docs,sheets
```

實際例子：

```bash
gog auth add aiagentg888@gmail.com --services gmail,calendar,drive,docs,sheets
```

執行後會：

1. 在終端機顯示一段 URL。
2. 自動開啟瀏覽器。
3. 你在瀏覽器中選擇該帳號並按「同意」。

完成後可用：

```bash
gog auth list
```

確認輸出中該帳號的 services 包含：`calendar,docs,drive,gmail,sheets`。

---

## 5. Calendar：安排行程

### 5.1 建立行程（create）

基本格式：

```bash
gog calendar create <calendarId> \
  --summary "標題" \
  --from "起始時間 ISO" \
  --to   "結束時間 ISO" \
  --account <email>
```

在你的環境中，我們常用：

```bash
cd /Users/user/clawd

gog calendar create primary \
  --summary "和師姐共心（LINE 線上）" \
  --from "2026-02-01T21:00:00+08:00" \
  --to   "2026-02-01T22:00:00+08:00" \
  --location "LINE 線上" \
  --account aiagentg888@gmail.com
```

- `primary`：代表該帳號的主行事曆
- `--account`：決定是哪個 Gmail 的行事曆

### 5.2 查詢某天行程（events）

```bash
cd /Users/user/clawd

gog calendar events primary \
  --from "2026-02-01T00:00:00+08:00" \
  --to   "2026-02-01T23:59:59+08:00" \
  --account aiagentg888@gmail.com
```

這是我每天早上 9 點幫你看行程時實際會跑的指令版本。

---

## 6. Gmail：寄信

### 6.1 簡單純文字信

```bash
cd /Users/user/clawd

gog gmail send \
  --account jackychen0615@gmail.com \
  --to someone@example.com \
  --subject "測試信" \
  --body "這是一封測試信。"
```

### 6.2 多行內容（用 stdin）

```bash
cd /Users/user/clawd

gog gmail send \
  --account step1nework016@gmail.com \
  --to someone@example.com \
  --subject "會議紀要" \
  --body-file - << 'EOF'
嗨，這是今天會議的重點：

1. ...
2. ...

謝謝！
EOF
```

---

## 7. Drive / Docs / Sheets：查檔與開啟

### 7.1 查最近檔案

```bash
cd /Users/user/clawd

gog drive search "*" --max 5 --account aiagentg888@gmail.com
```

輸出會列出 ID / 檔名 / 修改時間，例如：

```text
ID                                            NAME
1eMQUXRcn9-wELa8cLoK6kXrdnEnkZoMyMzAtCH1Bmes  seo文章
...
1LFAI18uyzl1Zh0WKJrmhT4InrM7wYAl             擬真隱形眼鏡平台+AI智能語音助理)估價單.docx .docx
```

### 7.2 取得檔案 metadata + webViewLink

```bash
cd /Users/user/clawd

gog drive get 1LFAI18uyzl1Zh0WKJrmhT4InrM7wYAl \
  --json \
  --account aiagentg888@gmail.com
```

你會看到類似：

```json
{
  "file": {
    "id": "1LFAI18uyzl1Zh0WKJrmhT4InrM7wYAl",
    "name": "擬真隱形眼鏡平台+AI智能語音助理)估價單.docx .docx",
    "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "webViewLink": "https://docs.google.com/document/d/1LFAI18uyzl1Zh0WKJrmhT4InrM7wYAl/edit?..."
  }
}
```

### 7.3 在本機瀏覽器打開檔案

```bash
open "https://docs.google.com/document/d/1LFAI18uyzl1Zh0WKJrmhT4InrM7wYAl/edit?usp=drivesdk&rtpof=true&sd=true"
```

這就是我剛剛幫你「打開估價單」時做的事。

> **目前限制：** gog 這版沒有直接下載 Drive 檔案到本機的指令，只能查詢、取得連結，下載仍需在瀏覽器裡按「檔案 → 下載」。

---

## 8. 多帳號使用策略

你現在綁定了三個帳號：

- 私人 / AI 測試：`aiagentg888@gmail.com`
- 主要個人：`jackychen0615@gmail.com`
- 其他用途：`step1nework016@gmail.com`

實務建議：

- **排私人行程** → 用 `aiagentg888` 的 calendar
- **排工作 / 對外會議** → 用 `jackychen0615` 的 calendar
- **測試寄信 / 自動化實驗** → 用 `step1nework016`

每次下 gog 指令，只要決定：

```bash
--account 要用哪個帳號
```

我在幫你操作時也會先問清楚：「這個行程 / 這封信要用哪個帳號？」再決定 `--account`。

---

## 9. 常見錯誤與排除

### 9.1 missing --account

訊息：

```text
missing --account (or set GOG_ACCOUNT ...)
```

原因：同一台機器上有多個帳號時，如果沒指定 `--account`，gog 不知道要用哪一個。

解法：在指令後面加上：

```bash
--account 某個@gmail.com
```

或在環境變數中指定預設帳號：

```bash
export GOG_ACCOUNT=某個@gmail.com
```

### 9.2 OAuth client credentials missing

訊息：

```text
OAuth client credentials missing (OAuth client ID JSON)
```

原因：`credentials.json` 沒放到 gog 預期的位置或路徑沒設定。

解法：

1. 確認檔案存在：
   `/Users/user/Library/Application Support/gogcli/credentials.json`
2. 重新執行：

```bash
gog auth credentials "/Users/user/Library/Application Support/gogcli/credentials.json"
```

### 9.3 Google Calendar API has not been used / disabled

訊息：

```text
Google Calendar API has not been used in project ... or it is disabled.
```

原因：GCP 專案還沒啟用 Calendar API。

解法：

1. 前往錯誤訊息裡給的連結（Calendar API 頁面）。
2. 按「啟用」。
3. 等一兩分鐘再重試 gog 指令。

---

## 10. 我（bot）幫你用 gog 的標準流程

之後只要你說「幫我安排行程 / 寄信」：

1. 我會先問：
   - 用哪個帳號？（`--account`）
   - 要不要加視訊連結？
   - 要不要同步給對方？（寄信或 Calendar 邀請）
2. 我先在你機器上實際跑 gog 指令。
3. 成功後，用固定格式回報：
   - 標題、時間、帳號
   - 地點、視訊連結
   - 是否同步給誰
4. 若是錯誤（像 OAuth / API 沒開），我會先自己試、看錯誤，再只把「你需要做的最小步驟」說給你聽。
