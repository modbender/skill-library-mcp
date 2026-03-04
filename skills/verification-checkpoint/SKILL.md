---
name: verification-checkpoint
description: Verification checkpoint before completion claims. Ensure tests pass, build succeeds, and functionality works.
auto_trigger: true
trigger:
  keyword: 完了|できた|実装しました|done|finished|complete
---

# Verification Checkpoint Skill

検証チェックポイントスキル。完了宣言前の必須検証。

---

## 完了宣言の条件（MUST）

```yaml
宣言前に必ず確認:
  □ テストが通ること
  □ 型チェックが通ること
  □ ビルドが通ること
  □ 実際に動作すること

すべて✅でないと「完了」と言わない
```

---

## 検証フロー

```
実装完了（自己申告）
    ↓
┌─────────────────────────────────────┐
│ 1. テスト実行                        │
│    npm test / pytest                 │
│    └─ 失敗 → 修正に戻る              │
├─────────────────────────────────────┤
│ 2. 型チェック                        │
│    tsc --noEmit / mypy              │
│    └─ 失敗 → 修正に戻る              │
├─────────────────────────────────────┤
│ 3. ビルド                            │
│    npm run build                     │
│    └─ 失敗 → 修正に戻る              │
├─────────────────────────────────────┤
│ 4. 動作確認                          │
│    手動 or 自動テスト                │
│    └─ 失敗 → 修正に戻る              │
└─────────────────────────────────────┘
    ↓
すべてパス
    ↓
「完了しました」✅
```

---

## 検証コマンド

### TypeScript/JavaScript

```yaml
テスト:
  command: npm test
  期待: 全テストパス

型チェック:
  command: npx tsc --noEmit
  期待: エラーなし

Lint:
  command: npm run lint
  期待: エラーなし

ビルド:
  command: npm run build
  期待: 成功
```

### Python

```yaml
テスト:
  command: pytest
  期待: 全テストパス

型チェック:
  command: mypy .
  期待: エラーなし

Lint:
  command: ruff check .
  期待: エラーなし
```

---

## 検証レベル

### Level 1: 最小検証（小さな変更）

```yaml
対象:
  - タイポ修正
  - コメント追加
  - 設定値変更

必須チェック:
  - [ ] ビルドが通る
```

### Level 2: 標準検証（通常の変更）

```yaml
対象:
  - 機能追加
  - バグ修正
  - リファクタリング

必須チェック:
  - [ ] テストが通る
  - [ ] 型チェックが通る
  - [ ] ビルドが通る
```

### Level 3: 完全検証（重要な変更）

```yaml
対象:
  - 新機能
  - セキュリティ修正
  - 破壊的変更

必須チェック:
  - [ ] テストが通る
  - [ ] 型チェックが通る
  - [ ] ビルドが通る
  - [ ] 手動動作確認
  - [ ] セキュリティレビュー
```

---

## 検証レポート

```yaml
検証チェックポイント:
  timestamp: 2026-02-02T12:00:00Z
  level: 2

  results:
    - name: テスト
      status: PASS
      command: npm test
      duration: 5s
      details: "42 tests passed"

    - name: 型チェック
      status: PASS
      command: npx tsc --noEmit
      duration: 3s

    - name: Lint
      status: PASS
      command: npm run lint
      duration: 2s

    - name: ビルド
      status: PASS
      command: npm run build
      duration: 10s

  verdict: ✅ PASS
  message: "すべての検証に合格しました"
```

---

## 失敗時の対応

### テスト失敗

```yaml
対応フロー:
  1. 失敗したテストを特定
  2. エラーメッセージを分析
  3. systematic-debugスキルで修正
  4. 再検証
```

### 型エラー

```yaml
対応フロー:
  1. エラー箇所を特定
  2. 型定義を確認
  3. 修正（型アノテーション追加等）
  4. 再検証
```

### ビルド失敗

```yaml
対応フロー:
  1. エラーログを確認
  2. 依存関係を確認
  3. 設定ファイルを確認
  4. 修正後再検証
```

---

## 自動実行タイミング

```yaml
トリガー:
  - 「完了しました」「できました」発言前
  - 「実装しました」発言前
  - PRを作成する前
  - デプロイする前

自動チェック:
  1. 直近の変更ファイルを検出
  2. 関連テストを実行
  3. 型チェック実行
  4. ビルド実行
  5. 結果をレポート
```

---

## 禁止事項

```
❌ テスト未実行で「完了」と言う
❌ 型エラーを無視して「完了」と言う
❌ ビルド失敗を無視して「完了」と言う
❌ 「たぶん動く」で「完了」と言う
❌ 「後でテストする」で「完了」と言う
```

---

## 使用例

```
「完了しました」→ 検証チェック自動実行
「できた」→ 検証チェック自動実行
「実装終わった」→ 検証チェック自動実行
```

---

## 連携スキル

| スキル | 連携内容 |
|--------|----------|
| `quality-gate` | 品質ゲート確認 |
| `auto-fix` | 検証失敗時の自動修正 |
| `systematic-debug` | 検証失敗時のデバッグ |

---

## 更新履歴

```
[2026-02-02] 初期作成
```
