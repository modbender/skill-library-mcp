# Docker (VPS) へのデプロイ・連携手順

Hostinger VPS上のDockerで動作しているOpenClawに、本Skillを組み込む手順を説明します。

## 1. ファイルの転送
作成したファイルをVPS上の任意のディレクトリ（例: `~/openclaw-skills/ticket-monitor/`）に転送します。

**必要なファイル:**
- `scripts/ticket_monitor.py`
- `.env` (Webhook URL設定済み)
- `TOOLS.md`
- `data/` フォルダ (空でOK)

## 2. Dockerコンテナへの連携方法
OpenClawのコンテナがこれらのファイルを読み込めるようにします。主に2つの方法があります。

### 方法A: ボリュームマウント (推奨)
`docker-compose.yml` を使用している場合、`volumes` セクションにパスを追加します。

```yaml
services:
  openclaw:
    # ... 他の設定 ...
    volumes:
      - /path/to/your/ticket-monitor:/app/skills/ticket-monitor
```
※ `/app/skills/` はOpenClawがSkillを検索するディレクトリに合わせて調整してください。

### 方法B: Dockerfile でコピー
独自にImageをビルドしている場合は、`Dockerfile` に追記します。
```dockerfile
COPY ./ticket-monitor /app/skills/ticket-monitor
RUN pip install requests beautifulsoup4 python-dotenv
```

## 3. 依存ライブラリのインストール
OpenClawのコンテナ内でスクリプトが動くよう、ライブラリが必要です。

**実行中のコンテナにインストールする場合:**
```bash
docker exec -it <container_id> pip install requests beautifulsoup4 python-dotenv
```
※ 可能であれば、OpenClaw起動時に `requirements.txt` を読み込む設定にするか、Dockerfileに含めるのがベストです。

## 4. TOOLS.md の反映
OpenClawは通常、マウントされたディレクトリ内にある `TOOLS.md` を自動的にスキャンします。
AIに「新しく追加したチケット監視ツールを使って」と指示することで、認識が開始されます。

## 5. 定期実行 (cron)
VPS側の `cron` を使って、Dockerコマンドを定期的に叩くように設定します。

```bash
# crontab -e で設定
0 9 * * * docker exec <container_id> python3 /app/skills/ticket-monitor/scripts/ticket_monitor.py
```
