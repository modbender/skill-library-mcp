---
name: threads-poster
description: Post content to Threads using HTTP Browser API. Supports text, images, and scheduled posts for engagement optimization.
---

# Threads 投稿スキル

Threads（Meta）への自動投稿を行うスキル。HTTP Browser APIを使用。

## クイックスタート

### 基本投稿（HTTP API）
```bash
curl -X POST "${MOLTBOT_URL}/browser/sequence?secret=${CDP_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://threads.net",
    "actions": [
      {"type": "waitForSelector", "selector": "[aria-label=\"Create\"]"},
      {"type": "click", "selector": "[aria-label=\"Create\"]"},
      {"type": "waitForSelector", "selector": "[data-contents=\"true\"]"},
      {"type": "type", "selector": "[data-contents=\"true\"]", "text": "投稿内容をここに"},
      {"type": "wait", "ms": 1000},
      {"type": "click", "selector": "[data-testid=\"post-button\"]"},
      {"type": "wait", "ms": 3000},
      {"type": "screenshot"}
    ]
  }'
```

### 環境変数
```bash
export MOLTBOT_URL="https://your-worker.workers.dev"
export CDP_SECRET="your-secret"
```

---

## 投稿パターン（HTTP API）

### 1. テキスト投稿
```json
{
  "url": "https://threads.net",
  "actions": [
    {"type": "waitForSelector", "selector": "[aria-label=\"Create\"]"},
    {"type": "click", "selector": "[aria-label=\"Create\"]"},
    {"type": "waitForSelector", "selector": "[data-contents=\"true\"]"},
    {"type": "type", "selector": "[data-contents=\"true\"]", "text": "投稿内容"},
    {"type": "wait", "ms": 1000},
    {"type": "click", "selector": "[data-testid=\"post-button\"]"},
    {"type": "wait", "ms": 3000},
    {"type": "screenshot"}
  ]
}
```

### 2. プロフィールから投稿
```json
{
  "url": "https://threads.net/@yourusername",
  "actions": [
    {"type": "click", "selector": "[aria-label=\"Create\"]"},
    {"type": "waitForSelector", "selector": "[data-contents=\"true\"]"},
    {"type": "type", "selector": "[data-contents=\"true\"]", "text": "投稿内容"},
    {"type": "wait", "ms": 1000},
    {"type": "click", "selector": "[data-testid=\"post-button\"]"},
    {"type": "wait", "ms": 3000},
    {"type": "screenshot"}
  ]
}
```

---

## セレクタ一覧（2026年版）

```javascript
const SELECTORS = {
  // 投稿関連
  createButton: '[aria-label="Create"]',
  newPostButton: '[aria-label="New post"]',
  textArea: '[data-contents="true"]',
  postButton: '[data-testid="post-button"]',

  // メディア
  imageUpload: 'input[type="file"]',

  // その他
  closeModal: '[aria-label="Close"]',
};
```

---

## 投稿方法の比較

### 方法1: HTTP Browser API（推奨・即時開始可能）
```
利点:
├── 審査不要、即日開始
├── 全機能利用可能
├── WebSocket不要（HTTP only）
└── 柔軟な操作

注意点:
├── UIの変更に弱い
├── CAPTCHAリスク
└── レート制限に注意
```

### 方法2: Threads API（審査通過後）
```
利点:
├── 安定した動作
├── レート制限が明確
└── 公式サポート

制限:
├── Meta審査が必要（数週間〜数ヶ月）
├── ビジネスアカウント必須
└── 機能制限あり
```

---

## ログインフロー（HTTP API）

### Instagram連携ログイン
```json
{
  "url": "https://threads.net/login",
  "actions": [
    {"type": "waitForSelector", "selector": "input[name=\"username\"]"},
    {"type": "type", "selector": "input[name=\"username\"]", "text": "ユーザー名"},
    {"type": "type", "selector": "input[name=\"password\"]", "text": "パスワード"},
    {"type": "click", "selector": "button[type=\"submit\"]"},
    {"type": "wait", "ms": 5000},
    {"type": "screenshot"}
  ]
}
```

**注意**: 2FA有効時は手動対応が必要

---

## 投稿コンテンツガイド

### Threadsの特徴
```
プラットフォーム特性:
├── テキスト主体（500文字まで）
├── カジュアルなトーン
├── 会話・議論が活発
├── リプライ重視
└── ハッシュタグは控えめ
```

---

## Threads アルゴリズム研究（2026年版）

### フィード表示の仕組み
```
アルゴリズム要素:
├── エンゲージメント優先
│   ├── リプライ: ★★★★★（最重要）
│   ├── 引用: ★★★★☆
│   ├── リポスト: ★★★★☆
│   ├── いいね: ★★★☆☆
│   └── 滞在時間: ★★★☆☆
├── 時間要素
│   ├── 新しい投稿が優先
│   ├── 48時間以内の投稿が主
│   └── 古い投稿は埋もれやすい
├── 関係性スコア
│   ├── 過去のやりとり頻度
│   ├── 相互フォロー
│   └── DMでのやりとり
└── コンテンツの質
    ├── テキストの長さ（適度な長さが◎）
    ├── 画像の有無
    └── リンクの有無（リンクは弱い）
```

### 拡散の条件
```
「おすすめ」に載る条件:
├── 1. 最初の1時間で10+リプライ
├── 2. 会話が連鎖している（議論が活発）
├── 3. 引用での言及が多い
├── 4. 投稿者の過去エンゲージメント率
├── 5. フォロワー外からの反応
└── 6. トピックの時事性
```

### Instagramとの違い
```
Threads vs Instagram:
├── Threads: テキスト主体、会話重視
├── Instagram: ビジュアル主体、発見重視
├── Threads: カジュアルなトーン
├── Instagram: 作り込んだコンテンツ
├── Threads: ハッシュタグ控えめ
└── Instagram: ハッシュタグ活用
```

### アルゴリズム最適化戦略
```
投稿を伸ばすために:
├── 1. 質問形式で終わる（リプライ誘導）
├── 2. 意見を述べて反応を促す
├── 3. 投稿後すぐにリプライに返信
├── 4. 他の人の投稿にリプライ（可視性UP）
├── 5. トレンドトピックに参加
├── 6. 画像は1枚まで（テキスト主体を忘れずに）
└── 7. 投稿頻度は1日1-3回が最適
```

### 避けるべきこと
```
アルゴリズムペナルティ:
├── 外部リンクの多用
├── ハッシュタグの乱用（5個以上）
├── 同一内容の連続投稿
├── 明らかな宣伝投稿
├── エンゲージメントベイト
├── 短時間での大量投稿
└── Instagram投稿の単純な転載
```

### 最適投稿時間の深掘り
```
曜日別傾向（日本時間）:
├── 月曜日: 仕事関連が伸びる（朝7-8時）
├── 火曜日: 最もアクティブ
├── 水曜日: 良い
├── 木曜日: 良い
├── 金曜日: カジュアル系が伸びる
├── 土曜日: 昼間がアクティブ
└── 日曜日: 夜がアクティブ

ゴールデンタイム:
├── 20:00-22:00: 最も高いエンゲージメント
├── 12:00-13:00: ランチタイムのスパイク
└── 7:00-8:00: 通勤時間の小さなスパイク
```

---

### エンゲージメント最適化
```
投稿のコツ:
├── 質問形式で終わる（会話誘導）
├── 意見を述べて反応を促す
├── 短く、パンチのある文章
├── 絵文字は適度に
└── 画像より言葉で勝負
```

### 投稿テンプレート

**情報共有型**
```
[発見・学び]

→ [自分の考え/感想]

みんなはどう思う？💭
```

**質問型**
```
[トピック]について聞きたいんだけど、

[具体的な質問]

教えてほしい！
```

**Tips共有型**
```
[カテゴリ]の豆知識 💡

[Tip内容]

知ってた？
```

---

## 投稿スケジュール

### 最適投稿時間（日本時間）
```
平日:
├── 朝: 7:00-9:00（通勤時間）
├── 昼: 12:00-13:00（ランチタイム）
└── 夜: 20:00-23:00（ゴールデンタイム）

週末:
├── 朝: 9:00-11:00
└── 夜: 21:00-24:00
```

### 投稿頻度
```
推奨:
├── 1日1-3投稿
├── 一定間隔を空ける（2時間以上）
└── リプライは即時対応
```

---

## 画像投稿

### サイズ・形式
```
推奨:
├── アスペクト比: 1:1 または 4:5
├── 解像度: 1080x1080px 以上
├── 形式: JPEG, PNG
└── 最大10枚まで
```

### Nano Banana Pro 連携
```bash
# Threads用画像生成
~/.claude/skills/nano-banana-pro/generate.py \
  --prompt "[プロンプト]" \
  --output "/mnt/e/SNS-Output/Threads/[名前].png" \
  --aspect "1:1" \
  --resolution "2K"
```

---

## エラーハンドリング

### よくあるエラー
```
エラー対応:
├── ログイン失敗 → Cookie再取得、手動ログイン
├── 投稿ボタンが見つからない → セレクタ更新
├── レート制限 → 投稿間隔を空ける（30分〜1時間）
├── CAPTCHA → 手動対応、頻度を下げる
└── 画像アップロード失敗 → サイズ・形式確認
```

### リトライ戦略
```
1回目失敗 → 5秒待機 → リトライ
2回目失敗 → 30秒待機 → リトライ
3回目失敗 → エラー報告、手動対応要求
```

---

## セキュリティ連携（moltbook-security）

### 投稿内容チェック
```
投稿前に確認:
├── 機密情報が含まれていないか
├── APIキー/シークレットがないか
├── 不適切な内容がないか
└── 著作権侵害がないか
```

### 認証情報の保護
```
絶対に出力しない:
├── Instagram/Threadsのパスワード
├── セッションCookie
└── 認証トークン
```

---

## 分析・改善

### エンゲージメント追跡
```
追跡指標:
├── いいね数
├── リプライ数
├── リポスト数
├── 引用数
└── フォロワー増減
```

### 成功パターン分析
```
高エンゲージメント投稿の特徴を記録:
├── 投稿時間
├── 文字数
├── トピック
├── 表現方法
└── 画像の有無
```

---

## 使用例

### テキスト投稿
```
投稿内容: AIツールの使い方について

「最近ChatGPTの使い方変わってきた気がする

前は「〜して」って命令形だったけど、
今は「〜について一緒に考えよう」って対話形式に

みんなはどう使い分けてる？」
```

### 画像付き投稿
```
1. nano-banana skill で画像生成
2. threads-poster skill で投稿
   - テキスト + 画像パス指定
   - 自動アップロード
```

---

## API移行準備

### 審査申請時のチェックリスト
```
必要なもの:
├── Metaビジネスアカウント
├── Instagramプロアカウント
├── アプリの説明（使用目的）
├── プライバシーポリシーURL
└── 利用規約URL
```

### API利用可能になったら
```
切り替え手順:
1. アクセストークン取得
2. API呼び出しに変更
3. ブラウザ自動化を無効化
4. レート制限に従った投稿
```
