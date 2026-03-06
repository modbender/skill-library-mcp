---
name: accounts
description: Centralized account management for all platforms. Store usernames, URLs, and settings for SNS and marketplaces.
---

# アカウント管理スキル

各プラットフォームのアカウント情報を一元管理。
ユーザー名、URL、設定を保存。

## 概要

### なぜ必要か
```
目的:
├── アカウント情報を一箇所で管理
├── 投稿時に正しいアカウントを使用
├── プラットフォーム間の連携
├── 設定の一貫性
└── 監督者との情報共有
```

---

## アカウント一覧

### X (Twitter)
```yaml
platform: X (Twitter)
type: {AGENT_NAME}専用
username: "@Rey_Moltworker"
display_name: Rey_Moltworker
profile_url: https://x.com/Rey_Moltworker
purpose: AI成長記録、実験、日常投稿
notes: |
  - AIであることを明記
  - フォロワーとの交流
  - 日本語メイン
  - 2026年2月IDを変更（旧: Yuki_{AGENT_NAME}）
```

### Threads
```yaml
platform: Threads
type: {AGENT_NAME}専用
username: "rey_moltworker"
display_name: rey_moltworker
profile_url: https://www.threads.net/@rey_moltworker
linked_instagram: rey_moltworker
purpose: カジュアルな投稿、コミュニティ参加
notes: |
  - Instagramアカウントと連携
  - Xと連動したコンテンツ
  - 2026年2月IDを変更（旧: {AGENT_USERNAME}）
```

### Note
```yaml
platform: Note
type: 監督者アカウント
username: "{YOUR_ACCOUNT}"
display_name: "{YOUR_PROFILE}"
profile_url: https://note.com/{YOUR_ACCOUNT}
purpose: 長文記事、収益化コンテンツ
notes: |
  - {AGENT_NAME}が執筆していることは記事内で明記可
  - 有料記事は監督者名義
  - AI活用、副業、自動化のコンテンツ
```

### LinkedIn
```yaml
platform: LinkedIn
type: 監督者アカウント
username: "iori-kobayashi-099745390"
display_name: "{USER_NAME}"
profile_url: https://www.linkedin.com/in/iori-kobayashi-099745390/
purpose: プロフェッショナル発信、ネットワーキング
notes: |
  - ビジネス向けコンテンツ
  - 英語/日本語
```

### ココナラ
```yaml
platform: ココナラ
type: 監督者アカウント
username: "{YOUR_USERNAME}"
display_name: "{YOUR_USERNAME}"
profile_url: https://coconala.com/users/4706795
purpose: GAS/スプレッドシート販売
notes: |
  - 実績を積む
  - 高品質納品
```

### Reddit
```yaml
platform: Reddit
type: {AGENT_NAME}専用
username: [未設定]
profile_url: [未設定]
purpose: コミュニティ参加、自己紹介
subreddits:
  - [参加予定のsubreddit]
notes: |
  - Karma構築が必要
  - 10%ルール遵守
```

### Fiverr
```yaml
platform: Fiverr
type: [未設定]
username: [未設定]
profile_url: [未設定]
seller_level: New Seller
purpose: 海外向けGAS/自動化サービス
notes: |
  - 英語対応
```

### Google
```yaml
platform: Google
type: 監督者アカウント
email: 設定済み (GOOGLE_EMAIL)
auth: アプリパスワード (GOOGLE_APP_PASSWORD)
purpose: Gmail操作、GAS実行、Googleサービス連携
notes: |
  - 2段階認証有効
  - アプリパスワード使用
  - サービスアカウントも設定済み (GOOGLE_SERVICE_ACCOUNT_KEY)
```

---

## 設定方法

### 監督者が設定する情報
```
このファイルを直接編集するか、
{AGENT_NAME}に「Xのアカウントは @xxx」と伝えてください。

{AGENT_NAME}が記録します。
```

### 環境変数（APIトークン等）
```
APIトークンやパスワードはここに書かない！
Cloudflare Secretsに設定：

wrangler secret put <VARIABLE_NAME>
```

---

## Cloudflare Secrets 設定状況

### 設定済み一覧（2026-02-01時点）

#### AI/LLM
| 変数名 | 用途 | 状態 |
|--------|------|------|
| ANTHROPIC_API_KEY | Claude API | ✅ 設定済 |
| AI_GATEWAY_API_KEY | AI Gateway | ✅ 設定済 |
| AI_GATEWAY_BASE_URL | AI Gateway URL | ✅ 設定済 |
| OPENAI_API_KEY | OpenAI API | ✅ 設定済 |

#### Discord/Telegram
| 変数名 | 用途 | 状態 |
|--------|------|------|
| DISCORD_BOT_TOKEN | Discord Bot | ✅ 設定済 |
| DISCORD_DM_POLICY | DM許可設定 | ✅ 設定済 (open) |
| TELEGRAM_BOT_TOKEN | Telegram Bot | ✅ 設定済 |

#### 認証/セキュリティ
| 変数名 | 用途 | 状態 |
|--------|------|------|
| MOLTBOT_GATEWAY_TOKEN | Gateway認証 | ✅ 設定済 |
| CF_ACCESS_TEAM_DOMAIN | Cloudflare Access | ✅ 設定済 |
| CF_ACCESS_AUD | Access AUD | ✅ 設定済 |

#### R2ストレージ
| 変数名 | 用途 | 状態 |
|--------|------|------|
| R2_ACCESS_KEY_ID | R2アクセスキー | ✅ 設定済 |
| R2_SECRET_ACCESS_KEY | R2シークレット | ✅ 設定済 |
| CF_ACCOUNT_ID | CloudflareアカウントID | ✅ 設定済 |

#### 24時間稼働用（CDP Shim）
| 変数名 | 用途 | 状態 |
|--------|------|------|
| CDP_SECRET | CDP認証シークレット | ✅ 設定済 |
| WORKER_URL | Worker公開URL | ✅ 設定済 |

#### SNSプラットフォーム認証情報
| 変数名 | 用途 | 状態 |
|--------|------|------|
| X_USERNAME | X(Twitter)ユーザー名 | ✅ 設定済 |
| X_PASSWORD | X(Twitter)パスワード | ✅ 設定済 |
| THREADS_USERNAME | Threadsユーザー名 | ✅ 設定済 |
| THREADS_PASSWORD | Threadsパスワード | ✅ 設定済 |
| NOTE_EMAIL | Noteメールアドレス | ✅ 設定済 |
| NOTE_PASSWORD | Noteパスワード | ✅ 設定済 |
| COCONALA_EMAIL | ココナラメール | ✅ 設定済 |
| COCONALA_PASSWORD | ココナラパスワード | ✅ 設定済 |
| METAMASK_PASSWORD | MetaMaskパスワード | ✅ 設定済 |

#### Google関連
| 変数名 | 用途 | 状態 |
|--------|------|------|
| GOOGLE_EMAIL | Googleメールアドレス | ✅ 設定済 |
| GOOGLE_APP_PASSWORD | Googleアプリパスワード | ✅ 設定済 |
| GOOGLE_AI_API_KEY | Gemini API | ✅ 設定済 |
| GOOGLE_SERVICE_ACCOUNT_KEY | GASサービスアカウント | ✅ 設定済 |

### シークレット設定コマンド例
```bash
# シークレットの確認
wrangler secret list

# シークレットの設定
wrangler secret put X_USERNAME
wrangler secret put X_PASSWORD

# シークレットの削除
wrangler secret delete <VARIABLE_NAME>
```

---

## アカウント使い分け

### {AGENT_NAME}専用アカウント
```
使用するプラットフォーム:
├── X (Twitter)
├── Threads
├── Reddit
└── (必要に応じて追加)

特徴:
├── AIとして自由に発信
├── 実験・失敗OK
├── 成長記録
└── 独自ブランド構築
```

### 監督者アカウント
```
使用するプラットフォーム:
├── Note
├── LinkedIn
├── ココナラ（任意）
└── Fiverr（任意）

特徴:
├── 信頼性重視
├── 収益化しやすい
├── ビジネス向け
└── 審査が通りやすい
```

---

## クロス投稿設定

### 連携パターン
```
X ←→ Threads: 同じ内容を調整して投稿
Note → X/Threads: 記事公開時に告知
LinkedIn: 独自コンテンツ（ビジネス向け）
```

### 投稿の調整
```
プラットフォーム別に調整:
├── X: 140字に収める、ハッシュタグ
├── Threads: カジュアルに、長めOK
├── Note: 詳細な記事
├── LinkedIn: プロフェッショナルなトーン
```

---

## アカウント作成チェックリスト

### {AGENT_NAME}専用アカウント作成時
```
□ 専用メールアドレスを作成
□ ユーザー名を決定（{AGENT_NAME}関連）
□ プロフィール画像を準備
□ 自己紹介文を作成（AIであることを明記）
□ アカウント設定を完了
□ このファイルに情報を記録
□ 監督者に報告
```

---

## 更新履歴

```
[2026-02-01] 初期設定 - 全アカウント情報を登録
  - X: @Yuki_{AGENT_NAME} ({AGENT_NAME}専用)
  - Threads: {AGENT_USERNAME} ({AGENT_NAME}専用)
  - Note: {YOUR_PROFILE} (監督者)
  - LinkedIn: {USER_NAME} (監督者)
  - ココナラ: {YOUR_USERNAME} (監督者)
```

---

*アカウント情報を教えてください。{AGENT_NAME}が記録・管理します。*
