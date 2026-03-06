---
name: x-browser
description: Post to X (Twitter) using HTTP Browser API. Supports tweets, replies, threads, and media uploads without API costs.
---

# X(Twitter) ブラウザ自動化スキル

X（旧Twitter）へのブラウザ自動化投稿スキル。HTTP Browser APIを使用。

## クイックスタート

### 基本投稿（HTTP API）
```bash
curl -X POST "${MOLTBOT_URL}/browser/sequence?secret=${CDP_SECRET}" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://x.com/compose/tweet",
    "actions": [
      {"type": "waitForSelector", "selector": "[data-testid=\"tweetTextarea_0\"]"},
      {"type": "type", "selector": "[data-testid=\"tweetTextarea_0\"]", "text": "投稿内容をここに"},
      {"type": "wait", "ms": 1000},
      {"type": "click", "selector": "[data-testid=\"tweetButton\"]"},
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

## なぜブラウザ自動化？

### X API の問題
```
API制限:
├── Basic: $100/月 → 3,000 tweets/月
├── Pro: $5,000/月 → 1M tweets/月
├── 無料: 読み取りのみ、投稿不可
└── 頻繁な仕様変更
```

### HTTP Browser APIの利点
```
メリット:
├── 完全無料
├── 全機能利用可能
├── APIの仕様変更に依存しない
├── 人間と同じ操作
└── WebSocket不要（HTTP only）

リスク:
├── UIの変更で壊れる可能性
├── アカウント凍結リスク（過度な自動化）
└── CAPTCHA対応が必要な場合あり
```

---

## 投稿パターン（HTTP API）

### 1. テキスト投稿
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

### 2. スレッド投稿
```json
{
  "url": "https://x.com/compose/tweet",
  "actions": [
    {"type": "waitForSelector", "selector": "[data-testid=\"tweetTextarea_0\"]"},
    {"type": "type", "selector": "[data-testid=\"tweetTextarea_0\"]", "text": "スレッド1つ目 🧵"},
    {"type": "click", "selector": "[data-testid=\"addButton\"]"},
    {"type": "wait", "ms": 500},
    {"type": "type", "selector": "[data-testid=\"tweetTextarea_1\"]", "text": "スレッド2つ目"},
    {"type": "click", "selector": "[data-testid=\"addButton\"]"},
    {"type": "wait", "ms": 500},
    {"type": "type", "selector": "[data-testid=\"tweetTextarea_2\"]", "text": "スレッド3つ目（完）"},
    {"type": "wait", "ms": 1000},
    {"type": "click", "selector": "[data-testid=\"tweetButton\"]"},
    {"type": "wait", "ms": 5000},
    {"type": "screenshot"}
  ]
}
```

### 3. ホーム画面から投稿
```json
{
  "url": "https://x.com/home",
  "actions": [
    {"type": "waitForSelector", "selector": "[data-testid=\"SideNav_NewTweet_Button\"]"},
    {"type": "click", "selector": "[data-testid=\"SideNav_NewTweet_Button\"]"},
    {"type": "waitForSelector", "selector": "[data-testid=\"tweetTextarea_0\"]"},
    {"type": "type", "selector": "[data-testid=\"tweetTextarea_0\"]", "text": "投稿内容"},
    {"type": "wait", "ms": 1000},
    {"type": "click", "selector": "[data-testid=\"tweetButton\"]"},
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
  composeButton: '[data-testid="SideNav_NewTweet_Button"]',
  tweetTextArea: '[data-testid="tweetTextarea_0"]',
  tweetTextArea2: '[data-testid="tweetTextarea_1"]',
  postButton: '[data-testid="tweetButton"]',

  // スレッド
  addTweetButton: '[data-testid="addButton"]',

  // メディア
  imageUpload: '[data-testid="fileInput"]',

  // リプライ
  replyButton: '[data-testid="reply"]',

  // 確認
  tweetPosted: '[data-testid="tweet"]',
};
```

---

## セットアップ

### 必要なもの
```
1. X アカウント（ログイン済み）
2. MOLTBOT_URL と CDP_SECRET
3. 初回は手動ログインが必要
```

### ログインフロー（sequence API）
```json
{
  "url": "https://x.com/login",
  "actions": [
    {"type": "waitForSelector", "selector": "input[autocomplete=\"username\"]"},
    {"type": "type", "selector": "input[autocomplete=\"username\"]", "text": "ユーザー名"},
    {"type": "click", "selector": "[role=\"button\"]:has-text(\"Next\")"},
    {"type": "wait", "ms": 2000},
    {"type": "waitForSelector", "selector": "input[type=\"password\"]"},
    {"type": "type", "selector": "input[type=\"password\"]", "text": "パスワード"},
    {"type": "click", "selector": "[data-testid=\"LoginForm_Login_Button\"]"},
    {"type": "wait", "ms": 5000},
    {"type": "screenshot"}
  ]
}
```

**注意**: 2FA有効時は手動対応が必要

---

## 投稿操作

### ツイート投稿
```javascript
// 基本投稿フロー
1. x.com/compose/tweet にアクセス
2. テキストエリアに入力
3. 「ポストする」ボタンをクリック
4. 投稿完了を確認
```

### セレクタ一覧（要定期更新）
```javascript
const SELECTORS = {
  // 投稿関連
  composeButton: '[data-testid="SideNav_NewTweet_Button"]',
  tweetTextArea: '[data-testid="tweetTextarea_0"]',
  postButton: '[data-testid="tweetButton"]',

  // メディア
  imageUpload: '[data-testid="fileInput"]',

  // スレッド
  addTweetButton: '[data-testid="addButton"]',

  // リプライ
  replyButton: '[data-testid="reply"]',

  // 確認
  tweetPosted: '[data-testid="tweet"]',
};
```

### スレッド投稿
```javascript
// スレッド作成フロー
1. 最初のツイートを入力
2. 「+」ボタンで追加
3. 2番目以降のツイートを入力
4. 繰り返し
5. 全部入力後に「ポストする」
```

### メディア付き投稿
```javascript
// 画像/動画投稿
1. テキストを入力
2. メディアアイコンをクリック
3. ファイルを選択（最大4枚）
4. アップロード完了を待つ
5. 「ポストする」
```

---

## 投稿コンテンツガイド

### Xの特徴（2026年版）
```
プラットフォーム特性:
├── 文字数制限: 280文字（日本語140文字相当）
├── 長文: X Premium で最大25,000文字
├── 画像: 最大4枚
├── 動画: 最大2分20秒（無料）/ 60分（Premium）
├── アルゴリズム: エンゲージメント重視
└── For Youタブ: 発見性が重要
```

---

## X(Twitter) アルゴリズム研究（2026年版）

### For You フィードの仕組み
```
アルゴリズム要素（公開情報ベース）:
├── 初期配信（最初の15-30分）
│   ├── フォロワーの一部にのみ表示
│   └── 初期エンゲージメントで拡散判定
├── エンゲージメントスコア
│   ├── リプライ: ★★★★★（最重要、27倍）
│   ├── リツイート: ★★★★☆（20倍）
│   ├── 引用リツイート: ★★★★☆（20倍）
│   ├── いいね: ★★★☆☆（30倍 ※0.5の重み）
│   ├── ブックマーク: ★★★☆☆
│   └── プロフィールクリック: ★★☆☆☆
├── 時間減衰
│   ├── 投稿直後: 最大ブースト
│   ├── 6時間後: 約50%減衰
│   └── 24時間後: 大幅減衰
└── ネガティブシグナル
    ├── ミュート/ブロック: 大幅減点
    └── 「興味がない」: 減点
```

### 拡散の条件
```
「For You」に載る条件:
├── 1. 最初の30分で5+エンゲージメント
├── 2. リプライが複数ある（会話が発生）
├── 3. 引用RTで議論されている
├── 4. 投稿者のアカウント品質（フォロワー/フォロー比）
├── 5. 過去投稿の平均エンゲージメント
└── 6. メディア（画像/動画）の有無
```

### アルゴリズム最適化戦略
```
投稿を伸ばすために:
├── 1. 最初の1行で止まらせる（スクロールストッパー）
├── 2. 投稿後30分は張り付く（初速が命）
├── 3. 自分の投稿にリプライで補足
├── 4. 他の人の投稿に価値あるリプライ
├── 5. スレッドは最初のツイートが伸びればOK
├── 6. 外部リンクは最初のリプライに
└── 7. ハッシュタグは1-2個まで（多すぎると減点）
```

### 避けるべきこと
```
アルゴリズムペナルティ:
├── 外部リンク（エンゲージメント率低下）
├── 同一内容の連続投稿
├── 短時間での大量投稿
├── エンゲージメントベイト（「いいねしたら〜」）
├── フォロワー購入
├── 自動フォロー/アンフォロー
└── ハッシュタグの乱用（3個以上）
```

### For You vs Following
```
For You タブ:
├── アルゴリズム推奨
├── フォロー外の投稿も表示
├── バイラルの可能性あり
└── 競争が激しい

Following タブ:
├── 時系列ベース
├── フォローしている人のみ
├── 確実にリーチ
└── バイラルしにくい
```

---

### バイラル投稿の法則
```
伸びやすい投稿:
├── 最初の1行で興味を引く
├── 議論を呼ぶ内容
├── 数字・データ入り
├── 画像/動画付き
├── 投稿後30分以内の初動が重要
└── リプライへの即時対応
```

### 投稿テンプレート

**フック型（最初の1行が勝負）**
```
[衝撃的な事実/疑問]

[詳細説明]

[行動喚起]
```

**リスト型**
```
[タイトル] を試した結果:

1. [項目1]
2. [項目2]
3. [項目3]

一番効果があったのは [結論]
```

**スレッド型（長文コンテンツ）**
```
ツイート1: [フック] - 続きはスレッドで 🧵

ツイート2: まず[背景]について

ツイート3: 次に[本題]

...

最終: まとめ + CTA
```

---

## 投稿スケジュール

### 最適投稿時間（日本時間）
```
平日:
├── 朝: 6:00-8:00（出勤前）
├── 昼: 12:00-13:00（ランチ）
└── 夜: 19:00-22:00（ゴールデンタイム）

週末:
├── 昼: 10:00-14:00
└── 夜: 18:00-23:00

曜日別傾向:
├── 月曜: ビジネス系が伸びる
├── 金曜: カジュアル系が伸びる
└── 土日: エンタメ系が伸びる
```

### 投稿頻度
```
推奨:
├── 1日3-10投稿（目安）
├── 最低2時間間隔
├── リプライは随時
└── スレッドは週1-2回
```

---

## エンゲージメント戦略

### 初動30分が勝負
```
投稿直後のアクション:
├── 自分の投稿に補足リプライ
├── 関連するタイムラインに参加
├── 他のユーザーの投稿にリプライ
└── 引用リツイートを誘導
```

### リプライ戦略
```
効果的なリプライ:
├── 質問で会話を続ける
├── 価値ある情報を追加
├── ユーモアを入れる
└── 相手の名前を呼ぶ
```

---

## 安全対策

### アカウント保護
```
凍結リスクを減らす:
├── 投稿間隔を空ける（最低30分）
├── 同一内容の連続投稿を避ける
├── フォロー/アンフォローの自動化は禁止
├── 異常なアクティビティを避ける
└── 自然な投稿パターンを維持
```

### セキュリティ連携（moltbook-security）
```
投稿前チェック:
├── 機密情報が含まれていないか
├── 不適切な内容がないか
├── 著作権侵害がないか
└── 誹謗中傷がないか
```

---

## エラーハンドリング

### よくあるエラー
```
対処法:
├── セッション切れ → Cookie再取得
├── セレクタが見つからない → UI変更、セレクタ更新
├── レート制限 → 1時間以上待機
├── CAPTCHA → 手動対応
├── 投稿失敗 → 内容確認、リトライ
└── アカウント制限 → 様子見、自動化頻度を下げる
```

### リトライ戦略
```
1回目失敗 → 10秒待機 → リトライ
2回目失敗 → 1分待機 → リトライ
3回目失敗 → エラー報告、手動対応要求
```

---

## Nano Banana Pro 連携

### X用画像生成
```bash
# 16:9 (推奨サイズ)
~/.claude/skills/nano-banana-pro/generate.py \
  --prompt "[プロンプト]" \
  --output "/mnt/e/SNS-Output/X/[名前].png" \
  --aspect "16:9" \
  --resolution "2K"

# 1:1 (正方形)
~/.claude/skills/nano-banana-pro/generate.py \
  --prompt "[プロンプト]" \
  --output "/mnt/e/SNS-Output/X/[名前].png" \
  --aspect "1:1" \
  --resolution "2K"
```

### 画像サイズ推奨
```
X画像サイズ:
├── 単体画像: 1200x675px (16:9)
├── 複数画像: 1200x1200px (1:1)
├── GIF: 最大15MB
└── 動画: 1280x720px 以上
```

---

## 分析・改善

### 追跡指標
```
エンゲージメント:
├── インプレッション数
├── いいね数
├── リツイート数
├── リプライ数
├── 引用リツイート数
├── プロフィールクリック
└── リンククリック
```

### 成功パターンの記録
```
高パフォーマンス投稿を分析:
├── 投稿時間
├── 文字数
├── メディアの有無
├── トピック/キーワード
├── フック（最初の1行）
└── CTA（行動喚起）
```

---

## 使用例

### 通常ツイート
```
投稿内容:
「AIツールを100個試した結果、
本当に使えるのは5個だけだった。

その5個を教えます🧵」

→ スレッドへの誘導
```

### 画像付きツイート
```
1. nano-banana で画像生成
2. x-browser で投稿
   - テキスト入力
   - 画像添付
   - 投稿
```

### スレッド投稿
```
1/5: [フック]
2/5: [背景]
3/5: [本題1]
4/5: [本題2]
5/5: [まとめ + CTA]
```
