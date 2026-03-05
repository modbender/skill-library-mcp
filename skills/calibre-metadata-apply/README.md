# calibre-metadata-apply

`calibredb` を使って、既存Calibre書籍のメタデータを更新するスキルです。

## このスキルの目的

このスキルは、Calibreライブラリのメタデータ運用を
**「安全に・継続的に・監査可能に」回す** ための実務スキルです。

### 1) 何を解決するか

- 手作業で崩れやすいメタデータ整備（title/authors/publisher/pubdate/tags/sort）を定型化
- 1冊編集とライブラリ横断編集を同じ運用ルールで実施
- 長時間ジョブでもチャットを止めずに進行（ターン分割）

### 2) 何を自動化するか

- 1冊単位の確定編集（確認→dry-run→apply→検証）
- ライブラリ横断の推定タグ付与（本文ではなく既存メタデータのみを利用）
- 高確信候補の自動適用と、低確信候補の保留

### 3) 何をしないか（境界）

- 曖昧な対象に対する即時apply
- 根拠が弱い候補の無条件上書き
- 本文解析が必要な重処理をmainターンで同期実行

### 4) 想定ユースケース

- 「ID指定で論文書誌を修正したい」
- 「マニュアルらしい本に `マニュアル/Manual` を一括付与したい」
- 「論文らしい本を横断抽出して `論文` タグを付けたい」

### 5) 運用ポリシー（要点）

- 高確信な提案のみ自動適用
- 低確信・衝突ケースは保留/再処理
- 保留は `pending-review` タグを付与して管理
- confidence表現は `high/medium/low` に統一
- 長時間処理はターン分割（開始ACK→完了報告）
- 実行中の状態/一時ファイルは完了時に削除（失敗時のみ最小限保持）

## セットアップ

1. このスキルを実行する環境にCalibreをインストールする
   - 必須: `calibredb`
2. PDF調査用に `pdffonts` を使えるようにする（例: `poppler-utils`）
3. `subagent-spawn-command-builder` を導入する（spawn payload生成に使用）

```bash
npx clawhub@latest install subagent-spawn-command-builder
pnpm dlx clawhub@latest install subagent-spawn-command-builder
```

4. `calibredb` と `pdffonts` が `PATH` で実行できることを確認する
5. Calibre Content server に到達できることを確認する
6. `--with-library` は次の形式で指定する
   - `http://HOST:PORT/#LIBRARY_ID`
   - localhost前提にしない（明示的なHOST:PORTを使う）
7. 認証が有効な場合は次を指定する
   - `--username <user>`
   - `--password-env <ENV_VAR>` または `--password <plain>`
8. 認証情報を保存して再利用したい場合は `--save-auth` を使う
   - 既定保存先: `~/.config/calibre-metadata-apply/auth.json`
   - 既定では `username` と `password_env` を保存
   - 平文パスワードも保存する場合のみ `--save-plain-password` を追加

### ユーザーが先に実行すること（例: Ubuntu/WSL）

```bash
sudo apt update
sudo apt install -y calibre poppler-utils
```

## 重要

OpenClawが入っているだけでは不十分です。実行環境側に `calibredb` が必要です。

WindowsではDefender Controlled Folder Access等の影響で書き込みが失敗する場合があります。
`WinError 2/5` などのパス/アクセス系エラーが出る場合は、Calibreライブラリフォルダや実行バイナリを許可リストに追加してください。

## 安全モデル

- 入力はJSONL（1行=1更新）
- `id` 必須
- デフォルトはdry-run（`--apply` 指定時のみ書き込み）

## ライブラリ横断処理（ターン分割）

長時間処理はターン分割で実行し、チャット継続性を優先します。

- 開始ターン:
  - `subagent-spawn-command-builder` で `sessions_spawn` payloadを生成（例: `profile=calibre-meta`）
  - 生成payloadで軽量subagentに解析を委譲
  - `scripts/run_state.mjs` で実行状態を記録
- 完了ターン: 完了通知後、`scripts/handle_completion.mjs` で状態を片付けて結果を提示
- state保存先: `state/runs.json`

### `spawn-profiles.json` に追加する例（`calibre-meta`）

```json
{
  "profiles": {
    "calibre-meta": {
      "model": "openrouter/qwen/qwen3-next-80b-a3b-instruct",
      "thinking": "low",
      "runTimeoutSeconds": 300,
      "cleanup": "keep"
    }
  }
}
```

## 認証キャッシュ（初回保存）

初回だけ認証情報を保存しておくと、以後は `--username` / `--password-env` を省略できます。

```bash
cat references/changes.example.jsonl | node scripts/calibredb_apply.mjs \
  --with-library "http://127.0.0.1:8080/#MyLibrary" \
  --password-env CALIBRE_PASSWORD \
  --save-auth
```

平文パスワードも保存したい場合（非推奨）は次を追加:

```bash
--save-plain-password
```

## クイックテスト（dry-run）

```bash
cat references/changes.example.jsonl | node scripts/calibredb_apply.mjs \
  --with-library "http://127.0.0.1:8080/#MyLibrary"
```
