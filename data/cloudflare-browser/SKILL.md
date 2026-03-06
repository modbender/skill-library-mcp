---
name: cloudflare-browser
description: Control headless Chrome via Cloudflare Browser Rendering HTTP API. Use for screenshots, page navigation, form filling, and browser automation in Cloudflare Workers environment.
---

# Cloudflare Browser Rendering (HTTP API)

HTTP経由でヘッドレスブラウザを操作するスキル。WebSocket CDPの代わりにHTTP APIを使用。

## 前提条件

- `CDP_SECRET` 環境変数が設定済み
- Worker URL（例: `https://your-worker.workers.dev`）

## API エンドポイント

すべてのエンドポイントは `?secret=<CDP_SECRET>` クエリパラメータが必要。

### 基本API

| エンドポイント | メソッド | 用途 |
|---------------|---------|------|
| `/browser/test` | GET | ブラウザ動作確認 |
| `/browser/screenshot` | POST | スクリーンショット取得 |
| `/browser/navigate` | POST | ページ遷移＋コンテンツ取得 |
| `/browser/execute` | POST | JavaScript実行 |
| `/browser/form` | POST | フォーム入力・送信 |
| `/browser/click` | POST | 要素クリック |
| `/browser/sequence` | POST | 複数アクションの連続実行 |

---

## 使用方法

### 環境変数
```bash
export MOLTBOT_URL="https://your-worker.workers.dev"
export CDP_SECRET="your-secret"
```

### curlでの呼び出し例

#### スクリーンショット
```bash
curl -X POST "${MOLTBOT_URL}/browser/screenshot?secret=${CDP_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "viewport": {"width": 1280, "height": 720},
    "fullPage": false,
    "format": "png"
  }'
```

#### ページナビゲーション＋テキスト取得
```bash
curl -X POST "${MOLTBOT_URL}/browser/navigate?secret=${CDP_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "extractText": true,
    "extractHtml": false
  }'
```

#### フォーム入力・送信
```bash
curl -X POST "${MOLTBOT_URL}/browser/form?secret=${CDP_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/login",
    "fields": [
      {"selector": "#email", "value": "user@example.com"},
      {"selector": "#password", "value": "password123"}
    ],
    "submit": "#login-button",
    "screenshotAfter": true
  }'
```

#### 要素クリック
```bash
curl -X POST "${MOLTBOT_URL}/browser/click?secret=${CDP_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "selector": "button.submit",
    "waitAfter": 2000,
    "screenshotAfter": true
  }'
```

#### 複数アクションの連続実行（sequence）
```bash
curl -X POST "${MOLTBOT_URL}/browser/sequence?secret=${CDP_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://x.com",
    "actions": [
      {"type": "waitForSelector", "selector": "[data-testid=\"tweetTextarea_0\"]"},
      {"type": "type", "selector": "[data-testid=\"tweetTextarea_0\"]", "text": "Hello World!"},
      {"type": "wait", "ms": 1000},
      {"type": "click", "selector": "[data-testid=\"tweetButton\"]"},
      {"type": "wait", "ms": 3000},
      {"type": "screenshot"}
    ]
  }'
```

---

## API詳細

### POST /browser/screenshot

URLのスクリーンショットを取得。

**リクエスト:**
```json
{
  "url": "https://example.com",      // 必須
  "viewport": {                       // オプション（デフォルト: 1280x720）
    "width": 1280,
    "height": 720
  },
  "fullPage": false,                  // オプション: ページ全体をキャプチャ
  "format": "png",                    // オプション: png or jpeg
  "quality": 80,                      // オプション: jpeg品質 (1-100)
  "waitMs": 2000                      // オプション: レンダリング待機時間
}
```

**レスポンス:**
```json
{
  "ok": true,
  "data": "base64エンコードされた画像",
  "url": "https://example.com/",
  "title": "Example Domain"
}
```

### POST /browser/navigate

ページ遷移してコンテンツを取得。

**リクエスト:**
```json
{
  "url": "https://example.com",       // 必須
  "waitFor": "#main-content",         // オプション: 待機するセレクタ
  "extractText": true,                // オプション: テキスト抽出
  "extractHtml": false,               // オプション: HTML抽出
  "waitMs": 2000                      // オプション: 追加待機時間
}
```

**レスポンス:**
```json
{
  "ok": true,
  "url": "https://example.com/",
  "title": "Example Domain",
  "text": "ページのテキスト内容",
  "html": "<html>...</html>"
}
```

### POST /browser/execute

ページ上でJavaScriptを実行。

**リクエスト:**
```json
{
  "url": "https://example.com",       // 必須
  "script": "() => document.title",   // 必須: 実行するスクリプト
  "args": [],                         // オプション: スクリプトへの引数
  "waitMs": 1000                      // オプション: 実行前待機
}
```

**レスポンス:**
```json
{
  "ok": true,
  "url": "https://example.com/",
  "title": "Example Domain",
  "result": "スクリプトの戻り値"
}
```

### POST /browser/form

フォーム入力と送信。

**リクエスト:**
```json
{
  "url": "https://example.com/login", // 必須
  "fields": [                         // 必須: 入力フィールド
    {"selector": "#email", "value": "user@example.com"},
    {"selector": "#password", "value": "secret"}
  ],
  "submit": "#login-button",          // オプション: 送信ボタン
  "waitAfterSubmit": 3000,            // オプション: 送信後待機
  "screenshotAfter": true             // オプション: 送信後スクリーンショット
}
```

### POST /browser/click

要素をクリック。

**リクエスト:**
```json
{
  "url": "https://example.com",       // 必須
  "selector": "button.submit",        // 必須: クリック対象
  "waitAfter": 2000,                  // オプション: クリック後待機
  "screenshotAfter": true             // オプション: クリック後スクリーンショット
}
```

### POST /browser/sequence

複数アクションを連続実行。SNS投稿など複雑な操作に最適。

**リクエスト:**
```json
{
  "url": "https://example.com",       // 必須: 開始URL
  "actions": [                        // 必須: アクションリスト
    {"type": "navigate", "url": "https://..."},
    {"type": "click", "selector": "..."},
    {"type": "type", "selector": "...", "text": "..."},
    {"type": "wait", "ms": 1000},
    {"type": "waitForSelector", "selector": "..."},
    {"type": "screenshot"},
    {"type": "execute", "script": "..."}
  ],
  "viewport": {"width": 1280, "height": 720}
}
```

**アクションタイプ:**
| type | パラメータ | 説明 |
|------|-----------|------|
| navigate | url | 別URLに遷移 |
| click | selector | 要素をクリック |
| type | selector, text | テキスト入力 |
| wait | ms | 指定ミリ秒待機 |
| waitForSelector | selector | 要素が表示されるまで待機 |
| screenshot | - | スクリーンショット取得 |
| execute | script | JavaScript実行 |

**レスポンス:**
```json
{
  "ok": true,
  "url": "最終URL",
  "title": "最終ページタイトル",
  "results": [
    {"action": "click:#btn", "result": "ok"},
    {"action": "type:#input", "result": "ok"},
    {"action": "screenshot", "result": "screenshot_0"}
  ],
  "screenshots": ["base64画像1", "base64画像2"]
}
```

---

## SNS投稿パターン

### X(Twitter)投稿
```json
{
  "url": "https://x.com/compose/tweet",
  "actions": [
    {"type": "waitForSelector", "selector": "[data-testid=\"tweetTextarea_0\"]"},
    {"type": "type", "selector": "[data-testid=\"tweetTextarea_0\"]", "text": "投稿内容"},
    {"type": "wait", "ms": 1000},
    {"type": "click", "selector": "[data-testid=\"tweetButton\"]"},
    {"type": "wait", "ms": 3000},
    {"type": "screenshot"}
  ]
}
```

### Threads投稿
```json
{
  "url": "https://threads.net",
  "actions": [
    {"type": "click", "selector": "[aria-label=\"New post\"]"},
    {"type": "waitForSelector", "selector": "[data-contents=\"true\"]"},
    {"type": "type", "selector": "[data-contents=\"true\"]", "text": "投稿内容"},
    {"type": "wait", "ms": 1000},
    {"type": "click", "selector": "[data-testid=\"post-button\"]"},
    {"type": "wait", "ms": 3000},
    {"type": "screenshot"}
  ]
}
```

### Coconalaログイン
```json
{
  "url": "https://coconala.com/login",
  "actions": [
    {"type": "type", "selector": "#email", "text": "メールアドレス"},
    {"type": "type", "selector": "#password", "text": "パスワード"},
    {"type": "click", "selector": "button[type=\"submit\"]"},
    {"type": "wait", "ms": 5000},
    {"type": "screenshot"}
  ]
}
```

### note.com投稿
```json
{
  "url": "https://note.com/new",
  "actions": [
    {"type": "waitForSelector", "selector": ".editor"},
    {"type": "type", "selector": ".title-input", "text": "記事タイトル"},
    {"type": "type", "selector": ".editor", "text": "記事本文..."},
    {"type": "screenshot"}
  ]
}
```

---

## エラーハンドリング

### よくあるエラー
| エラー | 原因 | 対処 |
|--------|------|------|
| 401 Unauthorized | CDP_SECRET不一致 | シークレット確認 |
| selector not found | セレクタが存在しない | セレクタ更新 |
| timeout | ページ読み込みが遅い | waitMs増加 |
| navigation failed | URLが無効 | URL確認 |

### リトライ戦略
```
1回目失敗 → 5秒待機 → リトライ
2回目失敗 → 15秒待機 → リトライ
3回目失敗 → エラー報告
```

---

## セキュリティ注意事項

- CDP_SECRETは絶対に公開しない
- ログインCookieは自動管理されない（毎回ログイン or セッション管理が必要）
- 過度な自動化はアカウント凍結リスクあり
- 投稿間隔は最低30分空ける（SNS系）

---

## 他スキルとの連携

| スキル | 連携方法 |
|--------|---------|
| x-browser | sequence APIでX投稿 |
| threads-poster | sequence APIでThreads投稿 |
| coconala-seller | form/sequence APIで商品管理 |
| note-publisher | sequence APIで記事投稿 |
| nano-banana | 画像生成後、screenshot APIで確認 |

---

## トラブルシューティング

### ブラウザが起動しない
```bash
# テストエンドポイントで確認
curl "${MOLTBOT_URL}/browser/test?secret=${CDP_SECRET}"
```

### セレクタが見つからない
1. 手動でサイトを開いてセレクタを確認
2. DevToolsでdata-testid属性を探す
3. 待機時間を増やす（waitForSelector使用）

### ログインが維持されない
- HTTPリクエストごとに新しいブラウザセッションが作成される
- ログインが必要な操作は sequence で一連の流れとして実行
