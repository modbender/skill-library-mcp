# openclaw-skill-diy-pc-ingest

Discordなどに貼り付けたPCパーツ購入ログ/メモを、OpenClaw経由でNotionのDB(PCConfig / ストレージ / エンクロージャー / PCInput)に反映するためのスキル。

- 雑な情報OK(レシート文、箇条書き、型番だけ、など)
- 迷うところは止めて質問、確実なところは即時反映
- Notion APIは **2025-09-03**(data_sources世代)前提

> このリポジトリには個人のNotion IDやAPIキーは含めません。各自の環境のに設定してください。

---

## できること

- Notionの各テーブルに対して **作成/更新(upsert運用)** を行う
- ストレージはシリアル優先で追記しやすい
- 必要に応じてストレージをPCConfig側にも「構成要素」としてミラー登録できる

---

## セットアップ

### 0) 依存スキル(ClawHub)

このスキルのNotion運用/デバッグ用依存は、ClawHubの `notion-api-automation` です。

- 推奨インストール: `clawhub install notion-api-automation`
- 同梱の `scripts/notion_apply_records.js` は単体でも動作しますが、Notion APIの疎通確認/調査には `notionctl.mjs` が便利です

### 1) Notion Integration を作る

1. https://www.notion.so/my-integrations でIntegrationを作成
2. Tokenを控える
3. 対象のNotionページ/DBをIntegrationに共有(Connect to)

### 1.5) Notion AIでDIY_PCスキーマを作成(推奨)

Notion AIに以下を貼り付けて、DIY_PC用の4テーブル(PCConfig / PCInput / ストレージ / エンクロージャー)を作成してください。
プロパティ名はスクリプトが参照するので、**表記どおり**に作るのが重要です。

```text
以下の要件で、Notion内に「DIY_PC」ページ配下に4つのデータベースを作成してください。各DBのプロパティ名は指定どおりにしてください(表記揺れ禁止)。

### 共通方針
- 日本語のプロパティ名はそのまま使う(例: 「購入日」)。
- 可能な限り “select / multi-select / date / number / checkbox” を適切に使う。
- まずは運用開始できる最小限で良い(あとで追加できる形に)。
- どのDBにも「メモ」(rich text)を入れる。

---

### 1) DB: ストレージ
目的: SSD/HDD/NVMe等の個体管理(シリアル、容量、健康状態、接続先PC、入れ物など)。

必須プロパティ:
- Name (title)
- シリアル (text)
- 種別 (select) 例: SSD, HDD
- 規格 (select) 例: NVMe, SATA
- 容量(GB) (number)
- 購入日 (date)
- 購入店 (text)
- 価格(円) (number)
- 状態 (select) 例: 稼働中, 取外し, 売却
- 健康 (select) 例: 正常, 警告, 損傷, 使用不能
- 健康根拠 (multi-select) 例: Scanner, SMART, 手動確認
- 最終チェック日 (date)
- 現在の接続先PC (select) 例: RecRyzen など(あとで選択肢追加できる形)
- 現在の入れ物 (select) 例: 内蔵, 外付けケース名 など
- メモ (rich text)

---

### 2) DB: エンクロージャー
目的: 外付けケース/ドック/筐体の管理(ベイ数、接続、運用名)。

必須プロパティ:
- Name (title)
- 取り外し表示名 (text)  ※Windowsの「安全な取り外し」で識別できる運用名
- 種別 (select) 例: USBケース, RAIDケース, ドック
- 接続 (select) 例: USB, Thunderbolt, LAN
- ベイ数 (number)
- 購入日 (date)
- 購入店 (text)
- 価格(円) (number)
- 普段つないでるPC (select)
- メモ (rich text)

---

### 3) DB: PCConfig
目的: PC構成部品の記録(部品単位の行)。ストレージ等を「このPCに刺さってる」として記録する用途でも使う。

必須プロパティ:
- Name (title)
- PC (select) 例: RecRyzen
- Category (select) 例: CPU, GPU, RAM, Storage, Motherboard, PSU, Case, Cooler, NIC, Capture, Other
- Spec (rich text)
- Purchase Date (date)
- Purchase Vendor (text)
- Purchase Price (number)
- Installed (checkbox)
- Active (checkbox)
- Status (status)
- Notes (rich text)
- Identifier (text) ※任意(将来使う可能性があるので残す)

---

### 4) DB: PCInput
目的: 解析しきれない入力をとりあえず溜める。後で人間が整形して他DBに移す。

必須プロパティ:
- 名前 (title)
- 型番 (text)
- Serial (text)
- 購入日 (date)
- 購入店 (text)
- 価格(円) (number)
- メモ (rich text)

---

作成後、各DBを「DIY_PC」ページ配下に置いてください。
```

### 1.8) (推奨) Notion操作スキルをインストール(ClawHub)

Notion APIの疎通確認/デバッグ/手作業オペレーション用に、ClawHubの `notion-api-automation` を入れておくと便利。

```bash
clawhub install notion-api-automation
```

### 2) トークン(APIキー)を用意

環境変数で渡す

```bash
export NOTION_API_KEY="<your notion token>"
```

OpenClawでは `~/.openclaw/.env` に書いて起動時に環境変数として読ませる

### 3) NotionのIDを自動検出して設定(推奨)

Notionの `data_source_id` / `database_id` は、Integrationがアクセスできる範囲なら検索で取得できます。
このスキルには初期設定用スクリプトが同梱されているので、通常は手でIDを書く必要はありません。

```bash
cd skills/diy-pc-ingest

# NOTION_API_KEY を設定した状態で実行
node scripts/bootstrap_config.js
```

これで `~/.config/diy-pc-ingest/config.json` が生成されます。

DB名が環境で違う場合は `--names` で指定できます:

```bash
node scripts/bootstrap_config.js --names   pcconfig=PCConfig   pcinput=PCInput   storage=ストレージ   enclosure=エンクロージャー
```

### 3b) 手動設定(うまく検出できない場合)

検索に出ない/同名が複数ある等で失敗する場合は、テンプレをコピーして手で埋めてください。

- テンプレ: `references/config.example.json`
- 配置先: `~/.config/diy-pc-ingest/config.json`

```bash
mkdir -p ~/.config/diy-pc-ingest
cp references/config.example.json ~/.config/diy-pc-ingest/config.json
```

`config.json` の以下を埋めます:
- `notion.targets.*.data_source_id`
- `notion.targets.*.database_id`


## 使い方

このスキルのコア処理は `scripts/notion_apply_records.js` です。

### JSONLを適用(手動)

```bash
cd skills/diy-pc-ingest

node scripts/notion_apply_records.js <<'JSONL'
{"target":"storage","properties":{"Name":"Samsung 970 EVO Plus 1TB (MZ-V7S1T0B/IT)","購入日":"2021-11-21","購入店":"JoshinWeb","価格(円)":14980,"型番":"MZ-V7S1T0B/IT","メモ":"Serial未入力"}}
JSONL
```

### オプション(運用向け)

- `overwrite: true` : 既存値も上書き(nullで消すことも可能)
- `page_id`(または `id`): 指定したNotionページを直接PATCH(upsertをバイパス)
- `archive: true` : ページをアーカイブ(重複整理に便利)
- `mirror_to_pcconfig: true`(storageのみ): PCConfig側にもミラー登録
  - 必要: `現在の接続先PC`, `購入日`, `Name`

---

## 注意

- NotionはDB側のユニーク制約が弱いので、upsertはクライアント側ロジックで行います。
- 重複が起きた場合は `page_id + archive:true` で整理できます。
- IDやトークンを公開リポジトリに含めないでください。

---

## ライセンス

MIT
