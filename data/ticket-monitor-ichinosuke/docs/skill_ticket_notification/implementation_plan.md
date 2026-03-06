# 実装計画：春風亭一之輔 チケット監視Skill

春風亭一之輔の東京公演チケット情報を定期的に監視し、新しい情報があればDiscordに通知するツールを作成します。

## ユーザーレビューが必要な事項

- **チケットサイトのURL**: デフォルトでイープラス（春風亭一之輔 検索結果）を使用しますが、特定の公演ページなど、他に対象としたいURLがあればお知らせください。
- **実行頻度**: スクリプト自体は1回限りの実行ですが、OpenClaw側で「1日1回」実行するスケジューリング設定（cron等）が必要になる可能性があります。

## 提案される変更

### [Scripts]

#### [NEW] [ticket_monitor.py](file:///Users/mukaikazuma/Desktop/AIエージェント開発/OpenClawSkill-ticket検索/scripts/ticket_monitor.py)
監視のメインロジック。以下の機能を持ちます：
- `requests` と `BeautifulSoup` を使用した特定URLのスクレイピング。
- 公演名、日時、URLを取得。
- 以前に通知した内容と照合（`seen_tickets.json` を使用）。
- 新規情報があれば Discord Webhook へ送信。

#### [NEW] [seen_tickets.json](file:///Users/mukaikazuma/Desktop/AIエージェント開発/OpenClawSkill-ticket検索/data/seen_tickets.json)
通知済みのチケットIDやURLを保存する永続化ファイル。

### [Config]

#### [NEW] [.env](file:///Users/mukaikazuma/Desktop/AIエージェント開発/OpenClawSkill-ticket検索/.env)
Discord Webhook URLを保存するための環境変数ファイル。

#### [MODIFY] [TOOLS.md](file:///Users/mukaikazuma/Desktop/AIエージェント開発/OpenClawSkill-ticket検索/TOOLS.md)
OpenClawがこのツールを呼び出せるよう、ツールの説明と引数（もしあれば）を定義します。

## 検証計画

### 自動テスト
- `scripts/ticket_monitor.py` を手動で実行し、スクレイピングの結果が正しく解析されるか確認。
- ダミーのWebhook URLを使用して通知処理の動作を確認。

### 手動確認
- 実際に1回実行し、Discordに（既存情報がある場合は初回通知として）メッセージが届くか確認。
- 既読ファイルが生成され、2回目以降の実行で重複通知が行われないことを確認。

---

## ClawHub 対応へのパッケージング変更

OpenClawエージェント経由で簡単にインストールできるよう、公式の `SKILL.md` フォーマットに準拠した構成に変更します。

### [DELETE] [TOOLS.md](file:///Users/mukaikazuma/Desktop/AIエージェント開発/OpenClawSkill-ticket検索/TOOLS.md)
古い独自フォーマットのツール定義ファイルを削除します。

### [NEW] [SKILL.md](file:///Users/mukaikazuma/Desktop/AIエージェント開発/OpenClawSkill-ticket検索/SKILL.md)
ClawHubがパースしてインストール情報を取得するための公式定義ファイルを作成します。以下の情報を含みます：
- **YAML Frontmatter (`metadata.clawdbot`)**:
  - `name`: ticket-monitor-ichinosuke
  - `description`: 春風亭一之輔の東京公演チケットを監視しDiscordに通知します。
  - `requires.env`: `DISCORD_WEBHOOK_URL` を指定。
  - `files`: `scripts/*` を依存ファイルとして指定。
- **Markdown 説明文**: ツールの使い方、必要な権限、外部送信先（Discord API）などを明記。

### パッケージ構成
このフォルダ（`OpenClawSkill-ticket検索`）全体がひとつのClawHubパッケージとして完結するようにし、`clawhub push` で直接アップロードできる状態にします。
