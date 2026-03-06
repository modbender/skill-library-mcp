# subagent-spawn-command-builder

`sessions_spawn` を**実行せず**、コマンド用payload JSONだけを生成するスキルです。

## 作成意図

このスキルは、以下の課題を解消するために作成しました。

- subagent呼び出し時の `model/thinking/timeout/cleanup` を毎回手で書くとミスが増える
- `agents.list` 依存の運用は、single-agent中心の使い方では設定コストが高い
- 実行まで1つのスキルに含めると責務が重くなり、トラブル時の切り分けが難しくなる

そのため、**「実行」と「生成」を分離**し、このスキルは

- プロファイル(JSON)管理
- `sessions_spawn` payload生成

だけに責務を限定しています。

## 目的

- subagent実行パラメータをJSONプロファイルで管理する
- `sessions_spawn` に渡すJSONを安定して生成する
- 実行は呼び出し側に任せる(このスキルは生成専用)

## 対応パラメータ

生成するpayloadは以下を扱います。

- `task` (required)
- `label` (optional)
- `agentId` (optional)
- `model` (optional)
- `thinking` (optional)
- `runTimeoutSeconds` (optional)
- `cleanup` (`keep|delete`, optional)

## ファイル構成

- テンプレート: `state/spawn-profiles.template.json`
- 実運用設定: `state/spawn-profiles.json`
- 生成スクリプト: `scripts/build_spawn_payload.mjs`
- 生成ログ: `state/build-log.jsonl`

## 使い方

### 1) テンプレートをコピー

```bash
cp skills/subagent-spawn-command-builder/state/spawn-profiles.template.json \
   skills/subagent-spawn-command-builder/state/spawn-profiles.json
```

### 2) `spawn-profiles.json` を編集

`model` などを自分の環境に合わせて設定。

### 3) payloadを生成

```bash
skills/subagent-spawn-command-builder/scripts/build_spawn_payload.mjs \
  --profile heartbeat \
  --task "Analyze recent context and return a compact summary" \
  --label heartbeat-test
```

## 値の優先順位

同じ項目が複数場所にある場合、次の順で採用されます。

1. CLI引数(`--model` など)
2. `profiles.<name>.*`
3. `defaults.*`

`task` は必ずCLIの `--task` を使います。

## 注意

- このスキルは payload/command 生成専用です
- `sessions_spawn` の実行はこのスキルの責務外です
- Python実行コマンドをtaskに含める場合は `python3` を使ってください(`python` は環境によって未定義)。
