---
name: rey-x-api
description: Post to X (Twitter) using official API with OAuth 1.0a. Supports tweets, threads, media. Use when user says "X API", "tweet via API", "post to X".
auto_trigger: false
---

# X API 投稿スキル

X（旧Twitter）公式APIを使った投稿スキル。Workers APIエンドポイント経由。

## アーキテクチャ

```
MoltBot → /x/tweet → Workers (OAuth署名) → X API
```

**重要**: OAuth認証はWorkers側で行われる。MoltBotはWorkersのAPIを呼ぶだけ。

## 必要な環境変数（Cloudflare Workers Secrets）

```
X_API_KEY           # Consumer Key (API Key)
X_API_SECRET        # Consumer Secret (API Secret Key)
X_ACCESS_TOKEN      # Access Token
X_ACCESS_TOKEN_SECRET # Access Token Secret
CDP_SECRET          # API認証用シークレット
```

---

## Workers APIエンドポイント

### ステータス確認
```
GET /x/status
```

### ツイート投稿
```
POST /x/tweet?secret={CDP_SECRET}
Content-Type: application/json

{
  "text": "ツイート内容（最大280文字）",
  "reply_to": "返信先ツイートID（オプション）",
  "quote_tweet_id": "引用ツイートID（オプション）"
}
```

### スレッド投稿
```
POST /x/thread?secret={CDP_SECRET}
Content-Type: application/json

{
  "tweets": ["1つ目のツイート", "2つ目のツイート", ...]
}
```

### ツイート削除
```
DELETE /x/tweet/{tweet_id}?secret={CDP_SECRET}
```

---

## MoltBotからの呼び出し方法

### 1. テキスト投稿

```javascript
// MOLTBOT_URL と CDP_SECRET は環境変数から取得
const response = await fetch(`${env.MOLTBOT_URL}/x/tweet?secret=${env.CDP_SECRET}`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: 'Hello World!' })
});

const result = await response.json();
// { success: true, data: { id: "12345", text: "Hello World!" }, url: "https://x.com/i/status/12345" }
```

### 2. スレッド投稿

```javascript
const response = await fetch(`${env.MOLTBOT_URL}/x/thread?secret=${env.CDP_SECRET}`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    tweets: [
      'AIツールを100個試した',
      '本当に使えるのは5個',
      'その5個を紹介します'
    ]
  })
});

const result = await response.json();
// { success: true, data: [...], url: "https://x.com/i/status/12345", count: 3 }
```

---

## API料金（従量課金）

```
投稿（POST）:
├── ツイート投稿: ~$0.01/回
├── 削除: ~$0.005/回
└── リツイート: ~$0.005/回

読み取り（GET）:
├── ツイート取得: ~$0.005/回
├── ユーザー情報: ~$0.005/回
└── メンション取得: ~$0.01/回

月額上限設定推奨（予算管理）
```

---

## x-browser との使い分け

| 項目 | x-api | x-browser |
|------|-------|-----------|
| **方式** | 公式API | ブラウザ自動化 |
| **コスト** | 従量課金（~$0.01/回） | 無料 |
| **信頼性** | 高い | UI変更で壊れる可能性 |
| **制限** | API制限 | アカウント凍結リスク |
| **機能** | 基本機能のみ | 全機能 |
| **推奨用途** | 自動化、Bot | 手動サポート |

### 推奨

```
ビジネス用途 → x-api（信頼性重視）
実験・テスト → x-browser（コスト0）
大量投稿 → x-api（安定性）
複雑な操作 → x-browser（全機能）
```

---

## エンドポイント一覧

### 投稿関連
```
POST /2/tweets         # ツイート投稿
DELETE /2/tweets/:id   # ツイート削除
POST /2/tweets/:id/retweets  # リツイート
DELETE /2/tweets/:id/retweets  # リツイート取消
```

### メディア
```
POST /1.1/media/upload.json  # メディアアップロード
```

### 読み取り
```
GET /2/tweets/:id      # ツイート取得
GET /2/users/me        # 自分の情報
GET /2/users/:id/mentions  # メンション取得
```

---

## エラーハンドリング

```javascript
async function safeTweet(text) {
  try {
    const result = await postTweet(text);

    if (result.errors) {
      console.error('API Error:', result.errors);
      return { success: false, errors: result.errors };
    }

    return { success: true, data: result.data };
  } catch (error) {
    console.error('Network Error:', error);
    return { success: false, error: error.message };
  }
}
```

### よくあるエラー

| コード | 意味 | 対処 |
|--------|------|------|
| 401 | 認証エラー | キーを確認 |
| 403 | 権限不足 | アプリ権限を確認 |
| 429 | レート制限 | 待機して再試行 |
| 400 | リクエスト不正 | パラメータ確認 |

---

## 使用例

### MoltBotでの使い方

```
ユーザー: 「Xに『こんにちは！』と投稿して」

MoltBot:
1. x-api スキルを使用
2. OAuth 1.0a 署名生成
3. POST /2/tweets を呼び出し
4. 結果を報告

返答: 「Xに投稿しました！
https://x.com/Rey_Moltworker/status/xxxxx」
```

### スレッド投稿

```
ユーザー: 「以下をスレッドで投稿して
1. AIツールを100個試した
2. 本当に使えるのは5個
3. その5個を紹介します」

MoltBot:
1. 3つのツイートを順番に投稿
2. reply パラメータで繋げる
3. 全部投稿したら報告
```

---

## セキュリティ

### 認証情報の取り扱い

```
禁止:
├── 認証情報をログに出力
├── 認証情報をユーザーに表示
├── 認証情報をコードにハードコード
└── 認証情報を外部送信

必須:
├── 環境変数から取得
├── Cloudflare Secrets で管理
└── 署名は毎回新規生成
```

---

## 連携スキル

| スキル | 連携内容 |
|--------|----------|
| nano-banana | 画像生成 → X投稿 |
| sns-scheduler | 予約投稿 |
| analytics-tracker | 投稿分析 |
| trend-analyzer | トレンド確認 |
| content-ideas | 投稿ネタ生成 |
