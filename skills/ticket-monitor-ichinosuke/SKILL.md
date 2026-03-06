---
name: ticket-monitor-ichinosuke
description: 春風亭一之輔の公式ウェブサイト（いちのすけえん）をスクレイピングし、東京都内で開催される新しい公演チケット情報を検知して指定のDiscordに通知するツールです。
---


# Ticket Monitor - 春風亭一之輔

春風亭一之輔の公式ウェブサイト（いちのすけえん）をスクレイピングし、東京都内で開催される新しい公演チケット情報を検知して指定のDiscordに通知するツールです。

## 必要な依存関係 (Dependencies)
このスクリプトを実行するには、Python 3と以下の外部パッケージが必要です。
- `requests`
- `beautifulsoup4`
- `python-dotenv`

事前に以下のコマンドでインストールしてください。
```bash
pip install requests beautifulsoup4 python-dotenv
```

## インストールと設定
環境変数として、通知先のDiscord Webhook URLの設定が必要です。
Docker・VPSでOpenClawを稼働している場合、以下の手順でOpenClaw大元の設定ファイルに直接環境変数を追加してください。

**【VPS / Docker コンテナ環境での設定手順】**
1. VPSにログインし、OpenClaw本体の `docker-compose.yml` が置かれているディレクトリに移動します。
2. ディレクトリ内にある設定ファイル（`.env`）を開きます。
3. ファイルの末尾に、以下の環境変数を追記して保存します。
   ```env
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
   ```
4. リロードするために、コンテナを一度停止して再起動します。
   ```bash
   docker compose down
   docker compose up -d
   ```

## 利用方法
OpenClawエージェントに対して以下のように指示してください。

- 「春風亭一之輔の新しいチケット情報がないか確認して」
- 「一之輔の東京公演をチェックして」

エージェントは自律的に `scripts/ticket_monitor.py` を実行し、前回確認時からの差分（新規公演情報）のみをDiscordに通知し、実行結果をチャットで返答します。

## セキュリティ・プライバシー
- 外部APIへの通信: 通知の送信用に提供されたDiscord Webhook URLに対してPOSTリクエストを送信します。
- データの保存: `data/seen_tickets.json` に既読の公演ID（URLまたはテキスト）をローカルに保存し、差分検知に使用します。

