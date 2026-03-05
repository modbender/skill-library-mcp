# Binance Cookie 獲取教程

本教程說明如何取得 `bn-square-skill` 所需的 Binance 認證資訊。

## 你需要準備的資料

- `BINANCE_COOKIE_HEADER`
- `BINANCE_CSRF_TOKEN`（建議）
- `BINANCE_SESSION_TOKEN`（若請求流程需要）

此外還需要 API path 設定（來自逆向分析）：
- `BINANCE_VALIDATE_SESSION_PATH`
- `BINANCE_PUBLISH_POST_PATH`
- `BINANCE_GET_POST_STATUS_PATH`
- `BINANCE_IMAGE_UPLOAD_PATH`

## Chrome 步驟

1. 使用瀏覽器登入 `https://www.binance.com/en/square`
2. 按 `F12` 開啟 DevTools
3. 切到 `Network` 面板
4. 重新整理頁面
5. 找任一 `/bapi/` 請求，點進去後查看 `Request Headers`
6. 複製 `cookie` header 全值，填入 `BINANCE_COOKIE_HEADER`
7. 若 headers 中有 `x-csrf-token`，複製到 `BINANCE_CSRF_TOKEN`
8. 若 headers 中有 session 相關 token，填入 `BINANCE_SESSION_TOKEN`

## Firefox 步驟

1. 使用瀏覽器登入 `https://www.binance.com/en/square`
2. 按 `F12` 開啟開發者工具
3. 切到 `Network`
4. 重新整理頁面
5. 找任一 `/bapi/` 請求，打開 `Headers`
6. 複製 `Cookie` 欄位內容到 `BINANCE_COOKIE_HEADER`
7. 複製 CSRF/session 對應 header 到環境變數

## 儲存方式 A：`.env`

建立 `.env`（可由 `.env.example` 複製）：

```dotenv
BINANCE_COOKIE_HEADER=csrftoken=...; session=...
BINANCE_CSRF_TOKEN=...
BINANCE_SESSION_TOKEN=...
BINANCE_VALIDATE_SESSION_PATH=/your/validated/path
BINANCE_PUBLISH_POST_PATH=/your/publish/path
BINANCE_GET_POST_STATUS_PATH=/your/status/path
BINANCE_IMAGE_UPLOAD_PATH=/your/upload/path
```

## 儲存方式 B：`config.json`

```json
{
  "apiBaseUrl": "https://www.binance.com",
  "cookieHeader": "csrftoken=...; session=...",
  "csrfToken": "...",
  "sessionToken": "...",
  "endpoints": {
    "validateSessionPath": "/your/validated/path",
    "publishPostPath": "/your/publish/path",
    "getPostStatusPath": "/your/status/path",
    "imageUploadPath": "/your/upload/path",
    "statusQueryParam": "postId"
  },
  "image": {
    "uploadFieldName": "file",
    "maxBytes": 5242880,
    "allowedMimeTypes": ["image/jpeg", "image/png", "image/webp"]
  }
}
```

若使用 `config.json`，可用 `BINANCE_CONFIG_PATH` 指向檔案位置。

## Session 有效期與維護

- Binance session 可能因登入狀態變化、風險驗證、或時間過期而失效
- 建議每次發文前先呼叫 `validate_session`
- 若回傳 `Session expired or unauthorized`，請重新按本教程抓取 cookie

## 常見問題

### Q1: 為什麼明明有 cookie 還是失敗？
- 通常是 cookie 過期、缺少 CSRF header、或 endpoint path 不正確
- 先跑 `scripts/analyze-api.ts` 更新 path，再重試

### Q2: 可以把 `.env` 上傳到 git 嗎？
- 不可以。`.env` 內含敏感資訊，必須保持本地且不可提交

### Q3: 為什麼不同帳號的 header 不同？
- Binance 可能針對帳號、區域、風控策略產生不同 request pattern，屬正常現象
