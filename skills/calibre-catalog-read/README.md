# calibre-catalog-read

Calibreカタログ参照 + 1冊単位のAI読書パイプライン。

注: このパイプラインは、テキスト解析コスト/品質の観点から漫画・コミック系タイトルを対象外にする設計です。

## セットアップ

1. OpenClaw実行環境(このスキルを実行するマシン/ランタイム)にCalibreをインストールする。
   - 必須バイナリ: `calibredb` / `ebook-convert`
2. 上記バイナリがPATHに通っていることを確認する。
3. `subagent-spawn-command-builder` を導入する(spawn payload生成に使用)。

```bash
npx clawhub@latest install subagent-spawn-command-builder
pnpm dlx clawhub@latest install subagent-spawn-command-builder
```

4. Calibre Content serverへ到達できることを確認する。
5. 接続先は必ず明示的な `HOST:PORT` を使う。
   - `http://HOST:PORT/#LIBRARY_ID`
6. 認証が有効な場合は `~/.openclaw/.env` に設定する(推奨)。
   - `CALIBRE_USERNAME=<user>`
   - `CALIBRE_PASSWORD=<password>`
   - 実行時は `--password-env CALIBRE_PASSWORD` を渡す(ユーザー名はenvから自動読込)。
   - 任意で `~/.config/calibre-catalog-read/auth.json` に認証キャッシュ可能。
   - `--save-plain-password` は平文保存のため、明示指示がない限り使わない。

## 重要

OpenClaw単体では不足です。実行環境にCalibreを入れて、必要バイナリを利用可能にしてください。

WindowsではDefender Controlled Folder Accessの影響でメタデータ/ファイル操作が失敗する場合があります。
`WinError 2/5` が出る場合は、Calibreライブラリフォルダや関連バイナリを許可対象に追加してください。

## クイックテスト(カタログ参照)

```bash
node scripts/calibredb_read.mjs list \
  --with-library "http://192.168.11.20:8080/#Calibreライブラリ" \
  --password-env CALIBRE_PASSWORD \
  --limit 5
```

## クイックテスト(1冊パイプライン)

```bash
uv run python scripts/run_analysis_pipeline.py \
  --with-library "http://192.168.11.20:8080/#Calibreライブラリ" \
  --password-env CALIBRE_PASSWORD \
  --book-id 3 --lang ja
```

## サブエージェント入力の分割(推奨)

readツールの行サイズ制限を避けるため、抽出テキストを分割し、`subagent_input.json` 経由で `source_files` を渡します。

```bash
node scripts/prepare_subagent_input.mjs \
  --book-id 3 --title "<title>" --lang ja \
  --text-path /tmp/book_3.txt --out-dir /tmp/calibre_subagent_3
```

## 低テキスト時の安全策

抽出テキストが短すぎる場合、パイプラインは `reason: low_text_requires_confirmation` で停止し、確認を要求します。
`--force-low-text` はユーザー確認後のみ使ってください。

## チャット運用(必須: 2ターン)

チャット面では必ず2ターンに分けて実行します。

1) 開始ターン(高速)
- 対象選定
- `subagent-spawn-command-builder` で `sessions_spawn` payloadを生成
- 生成payloadでspawn
- `run_state.mjs upsert`
- 即時ACK

2) 完了ターン(後続)
- 完了イベント
- `handle_completion.mjs`(内部で `get -> apply -> remove/fail`)

spawnと同一ターンで `poll/wait/apply` を行わないでください。

## spawn payload生成例(builder利用)

まず `subagent-spawn-command-builder` 側の `spawn-profiles.json` に
`calibre-read` プロファイルを定義します。

例:

```json
{
  "version": 1,
  "defaults": {
    "runTimeoutSeconds": 300,
    "cleanup": "keep"
  },
  "profiles": {
    "calibre-read": {
      "model": "openrouter/qwen/qwen3-next-80b-a3b-instruct",
      "thinking": "low",
      "runTimeoutSeconds": 300,
      "cleanup": "keep"
    }
  }
}
```

そのうえで、まずは**スキル呼び出しとして**次の意図で実行します:

- `subagent-spawn-command-builder` を使って `calibre-read` の `sessions_spawn` payloadを生成する
- `task` には `references/subagent-analysis.prompt.md` ベースの解析指示を渡す

内部実装コマンド(低レベル)は次のとおり:

```bash
uv run python ../subagent-spawn-command-builder/scripts/build_spawn_payload.py \
  --profile calibre-read \
  --task "<analysis task text based on references/subagent-analysis.prompt.md>"
```

出力JSONをそのまま `sessions_spawn` に渡します。

注意:
- `--task` は必ず `references/subagent-analysis.prompt.md` の厳格read契約を含む内容にする。
- `read` ツールは `{"path":"..."}` 形式のみを使う(pathなし呼び出し禁止)。
