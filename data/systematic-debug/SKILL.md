---
name: systematic-debug
description: Evidence-based debugging through 4 phases. Reproduce, isolate, identify root cause, verify fix. Auto-triggers on errors.
auto_trigger: true
trigger:
  keyword: デバッグ|debug|バグ|bug|動かない|not working|エラー解決|fix error
---

# Systematic Debugging Skill

証拠ベースの体系的デバッグ。4フェーズで根本原因を特定し、修正を検証。

---

## デバッグフェーズ

### Phase 1: 再現（Reproduce）

```yaml
目的: 問題を確実に再現する

手順:
  1. エラーメッセージを正確に記録
  2. 発生条件を特定
     - いつ発生するか？
     - どの操作で発生するか？
     - 毎回発生するか、時々か？
  3. 最小再現手順を作成

チェック項目:
  - [ ] エラーメッセージをコピー
  - [ ] スタックトレースを取得
  - [ ] 発生環境を記録（OS、バージョン等）
  - [ ] 再現手順を文書化
```

### Phase 2: 分離（Isolate）

```yaml
目的: 問題の範囲を絞り込む

手順:
  1. 二分探索で問題箇所を特定
     - 動く状態と動かない状態の差分
     - コミット履歴で変更点を確認
  2. 関連コンポーネントを特定
  3. 依存関係を確認

テクニック:
  - コメントアウトして切り分け
  - ログを追加して実行パスを確認
  - 最小構成で再現を試みる
```

### Phase 3: 特定（Identify）

```yaml
目的: 根本原因を特定する

手順:
  1. 仮説を立てる
  2. 仮説を検証する
  3. 仮説が外れたら次の仮説へ

よくある原因:
  - 型の不一致
  - null/undefinedアクセス
  - 非同期処理の順序問題
  - 環境変数の未設定
  - 依存関係の不整合
  - 権限の問題
  - ネットワークの問題
```

### Phase 4: 検証（Verify）

```yaml
目的: 修正が正しいことを確認する

手順:
  1. 修正を適用
  2. 元の再現手順で問題が解決したか確認
  3. 副作用がないか確認
  4. テストを追加（再発防止）

チェック項目:
  - [ ] 元のエラーが解消
  - [ ] 関連機能に影響なし
  - [ ] テストが追加された
  - [ ] ドキュメント更新（必要に応じて）
```

---

## デバッグツール

### ログ分析

```yaml
コンテナログ:
  command: GET /api/logs
  usage: ゲートウェイの動作確認

プロセス確認:
  command: GET /debug/processes
  usage: 実行中プロセスの確認

環境確認:
  command: GET /api/env-check
  usage: 環境変数の設定状況確認
```

### 一般的なデバッグコマンド

```yaml
TypeScript/JavaScript:
  - console.log() で値を確認
  - debugger ステートメント
  - try-catch でエラーキャッチ

Node.js:
  - NODE_DEBUG=* で詳細ログ
  - --inspect でデバッガ接続

ネットワーク:
  - curl -v でリクエスト詳細
  - fetch + console.log(response)
```

---

## エラーパターン別対処

### 認証エラー

```yaml
症状: 401 Unauthorized, 403 Forbidden
確認事項:
  - APIキー/トークンが設定されているか
  - トークンの有効期限
  - 権限設定
対処:
  - 環境変数を再確認
  - トークンを再生成
  - 権限を確認
```

### 接続エラー

```yaml
症状: ECONNREFUSED, timeout
確認事項:
  - サービスが起動しているか
  - URLが正しいか
  - ファイアウォール設定
対処:
  - プロセス状態を確認
  - URL/ポートを確認
  - ネットワーク設定を確認
```

### 型エラー

```yaml
症状: TypeError, Cannot read property of undefined
確認事項:
  - データの形式
  - null/undefinedチェック
  - 型定義
対処:
  - オプショナルチェーン (?.)
  - デフォルト値 (?? defaultValue)
  - 型ガード
```

### 非同期エラー

```yaml
症状: Promise rejection, async/await問題
確認事項:
  - await の付け忘れ
  - try-catch の範囲
  - 実行順序
対処:
  - すべての Promise に await
  - 適切なエラーハンドリング
  - 実行順序を明示
```

---

## 5 Whys 分析

```yaml
問題発生時に根本原因を追求:

例:
  問題: APIが500エラーを返す
  Why1: データベースクエリが失敗している
  Why2: クエリのパラメータがnull
  Why3: リクエストボディのパースに失敗
  Why4: Content-Typeヘッダーが設定されていない
  Why5: フロントエンドのfetch呼び出しでheadersを設定し忘れ

  根本原因: fetch呼び出しのheaders設定漏れ
  修正: headers: { 'Content-Type': 'application/json' } を追加
```

---

## 連携スキル

| スキル | 連携内容 |
|--------|----------|
| `failure-analyzer` | 失敗分析・学習 |
| `security-review` | セキュリティ関連のバグ |
| `quality-checker` | コード品質問題 |

---

## 使用例

```
「このエラーをデバッグして」→ 4フェーズデバッグ開始
「なぜこのバグが起きた？」→ 5 Whys分析
「動かないんだけど」→ 再現から開始
「エラーを解決して」→ 根本原因特定→修正→検証
```

---

## 更新履歴

```
[2026-02-02] 初期作成
```

---

*推測ではなく、証拠に基づいてデバッグしましょう。*
