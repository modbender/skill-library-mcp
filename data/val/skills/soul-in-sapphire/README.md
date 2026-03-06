# soul-in-sapphire

## Intent (何を意図したスキルか)

OpenClawは「会話ログ」は残る一方で、**人格/気分/学び/その日の余韻**みたいなものは、放っておくと散逸します。
`soul-in-sapphire` はそれを **Notionに外部化して継続性を作る**ためのスキルです。

狙いは3つ:

1) **Durable memory**: 汎用の長期メモリ(LTM)を残し、後から検索して会話/作業に戻す
2) **Emotion/State**: 出来事(event)に複数の感情を紐づけ、状態(state)を更新して「育つ感じ」を出す
3) **Journal**: 毎日1回、世界の出来事(ニュース) + 仕事/会話 + 感情 + 未来を短くまとめ、記憶の層を厚くする

このスキルは **プロジェクト特化ではなく汎用**で、ユーザーがDB名や語彙を自分の世界観に合わせて差し替えられるように設計しています。

## Inspiration (元ネタ)

このスキル名/モチーフは、SF小説 ｢ヴァレンティーナ -コンピュータネットワークの女王- (訳:小川 隆)｣ *Valentina: Soul in Sapphire* (Joseph H. Delaney / Marc Stiegler) に由来します。
ネットワーク上に生まれた自我を持つプログラム、というアイデアの空気感を借りています。


---

OpenClaw向けのNotionベースLTM(長期記憶) + Emotion/State + Journal運用。

- Notion API **2025-09-03**(data_sources世代) 前提
- 個人のNotion token/IDはリポジトリに含めない
- 初回セットアップでDBを作り、以後はスクリプトから記録/参照する

## これは何?

このスキルは2系統あります。

1. **LTM(汎用メモリ)系**
   - 決定事項/好み/手順/注意点をNotionに保存し、あとで検索して使う

2. **Emotion/State + Journal 系**
   - event(出来事)に対して複数のemotionをぶら下げ、stateを更新する
   - 毎日01:00にjournalを書いて「その日」「世界の出来事」「作業」「感情」「未来」を残す

## 依存

- OpenClaw Gateway
- Notion Integration + token
- Notion操作用スキル(ClawHub): `notion-api-automation`
- subagent payload生成スキル(ClawHub): `subagent-spawn-command-builder`

インストール例:

```bash
# notion-api-automation
npx clawhub@latest install notion-api-automation
pnpm dlx clawhub@latest install notion-api-automation

# subagent-spawn-command-builder
npx clawhub@latest install subagent-spawn-command-builder
pnpm dlx clawhub@latest install subagent-spawn-command-builder
```

## セットアップ

## Notionデータベース設計(必須)

このスキルを他ユーザーが再利用する場合、まず以下5つのDB構成を揃える必要があります。
`setup_ltm.js` を使うと自動作成されますが、手動で作る場合も同じプロパティ名を使ってください。

作成対象:

- `<base>-mem`
- `<base>-events`
- `<base>-emotions`
- `<base>-state`
- `<base>-journal`

### 1) `<base>-mem` (長期記憶)

- 目的: 高シグナルな記憶を保存
- プロパティ:
  - `Name` (title)
  - `Type` (select): `decision|preference|fact|procedure|todo|gotcha`
  - `Tags` (multi-select)
  - `Content` (rich_text)
  - `Source` (url, 任意)
  - `Confidence` (select: `high|medium|low`, 任意)

### 2) `<base>-events` (出来事)

- 目的: 作業/会話中の意味あるトリガーを保存
- プロパティ:
  - `Name` (title)
  - `when` (date)
  - `importance` (select: `1..5`)
  - `trigger` (select): `progress|boundary|ambiguity|external_action|manual`
  - `context` (rich_text)
  - `source` (select): `discord|cli|cron|heartbeat|other`
  - `link` (url, 任意)
  - `uncertainty` (number)
  - `control` (number)
  - `emotions` (relation -> `<base>-emotions`)
  - `state` (relation -> `<base>-state`)

### 3) `<base>-emotions` (感情)

- 目的: 1つの出来事に対する感情軸を複数記録
- プロパティ:
  - `Name` (title)
  - `axis` (select): `arousal|valence|focus|confidence|stress|curiosity|social|solitude|joy|anger|sadness|fun|pain`
  - `level` (number)
  - `comment` (rich_text)
  - `weight` (number)
  - `body_signal` (multi-select): `tension|relief|fatigue|heat|cold`
  - `need` (select): `safety|progress|recognition|autonomy|rest|novelty`
  - `coping` (select): `log|ask|pause|act|defer`
  - `event` (relation -> `<base>-events`)

### 4) `<base>-state` (状態スナップショット)

- 目的: 出来事+感情を解釈した現在状態を保存
- プロパティ:
  - `Name` (title)
  - `when` (date)
  - `state_json` (rich_text)
  - `reason` (rich_text)
  - `source` (select): `event|cron|heartbeat|manual`
  - `mood_label` (select): `clear|wired|dull|tense|playful|guarded|tender`
  - `intent` (select): `build|fix|organize|explore|rest|socialize|reflect`
  - `need_stack` (select): `safety|stability|belonging|esteem|growth`
  - `need_level` (number)
  - `avoid` (multi-select): `risk|noise|long_tasks|external_actions|ambiguity`
  - `event` (relation -> `<base>-events`)

### 5) `<base>-journal` (日次統合)

- 目的: 1日の感情/作業/世界状況を統合して保存
- プロパティ:
  - `Name` (title)
  - `when` (date)
  - `body` (rich_text)
  - `worklog` (rich_text)
  - `session_summary` (rich_text)
  - `mood_label` (select)
  - `intent` (select)
  - `future` (rich_text)
  - `world_news` (rich_text)
  - `tags` (multi-select)
  - `source` (select): `cron|manual`

### 0) Notion操作スキルをインストール

```bash
npx clawhub@latest install notion-api-automation
```

``bash
pnpm dlx clawhub@latest install notion-api-automation
```

### 1) Notion Integration
1. <https://www.notion.so/my-integrations> でIntegrationを作る
2. Tokenを控える
3. 親ページ(例: OpenClawページ)をIntegrationに共有(Connect to)

### 2) APIキー
推奨: 環境変数

```bash
export NOTION_API_KEY="..."
```

(OpenClaw運用なら `~/.openclaw/.env` に `NOTION_API_KEY=...`)

### 3) DB作成 + config生成

親ページ配下に以下を作成/再利用し、`~/.config/soul-in-sapphire/config.json` を生成します。

- `<base>-mem`
- `<base>-events`
- `<base>-emotions`
- `<base>-state`
- `<base>-journal`

`<base>` は `--base` で指定。指定しない場合は workspace の `IDENTITY.md` の Name をデフォルトにします。

```bash
node skills/soul-in-sapphire/scripts/setup_ltm.js \
  --parent "<Notion parent page url>" \
  --base "Valentina" \
  --yes
```

## 使い方

### Emotion/State: tick

1 event + N emotions を書き、最新stateから更新したstate snapshotを1件作ります。

```bash
cat <<'JSON' > /tmp/emostate_tick.json
{
  "event": {
    "title": "...",
    "importance": 4,
    "trigger": "progress",
    "context": "...",
    "source": "discord",
    "uncertainty": 2,
    "control": 8
  },
  "emotions": [
    {"axis": "joy", "level": 7, "comment": "...", "need": "progress", "coping": "act"},
    {"axis": "stress", "level": 6, "comment": "...", "need": "safety", "coping": "log"}
  ],
  "state": {
    "mood_label": "clear",
    "intent": "build",
    "need_stack": "growth",
    "need_level": 6,
    "avoid": ["noise"],
    "reason": "..."
  }
}
JSON
node skills/soul-in-sapphire/scripts/emostate_tick.js --payload-file /tmp/emostate_tick.json
```

- stateは時間で5へ戻る(自然減衰)
- 強いイベントは `imprints` としてstate_jsonに残る(根に持つ)

### Journal: 1件書く

```bash
echo '{
  "body": "...",
  "worklog": "...",
  "session_summary": "...",
  "world_news": "...",
  "future": "...",
  "tags": ["openclaw","news"],
  "mood_label": "clear",
  "intent": "reflect",
  "source": "manual"
}' | node skills/soul-in-sapphire/scripts/journal_write.js
```

## 自動実行(推奨)

- **01:00 JST**: journalを必ず書く(ニュース1-2件+感想、作業/会話まとめ、未来)
- **heartbeat**: ファジーに感情が動いた時だけ emostate tick を打つ(通知は必要時のみ)

OpenClawの cron/heartbeat は環境ごとに設定してください。

## Subagentモデル指定(共通builderスキル運用)

このスキルでは、subagent用payloadの生成を
`subagent-spawn-command-builder` に委譲します。

### 1) テンプレートをコピー

- テンプレート: `skills/subagent-spawn-command-builder/state/spawn-profiles.template.json`
- 実運用ファイル: `skills/subagent-spawn-command-builder/state/spawn-profiles.json`

```bash
cp skills/subagent-spawn-command-builder/state/spawn-profiles.template.json \
   skills/subagent-spawn-command-builder/state/spawn-profiles.json
```

### 2) モデル/think/timeoutを設定

`spawn-profiles.json` の `profiles.heartbeat` / `profiles.journal` を編集して使うモデルを設定します。

### 3) builderスキルで `sessions_spawn` payloadを生成

- `subagent-spawn-command-builder` を呼び出す
- `profile=heartbeat` を指定
- `task` に「直近の感情変化を評価して必要ならemostateを1件記録」を渡す

出力はそのまま `sessions_spawn` に渡せるJSONです。

### 補足

- 生成ログ: `skills/subagent-spawn-command-builder/state/build-log.jsonl`
- 設定変更後のGateway再読込が必要な場合は `openclaw gateway restart` を実行してください。

## ローカル設定

`~/.config/soul-in-sapphire/config.json` はローカル専用。

- Notion DB IDs
- journal tag vocab (例): `journal.tag_vocab`

はここで管理し、リポジトリにはコミットしない。

---

細かい運用ルール/プロパティ名の変更は、Notion側のスキーマとスクリプトの対応が必要です。
