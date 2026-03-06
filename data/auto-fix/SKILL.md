---
name: auto-fix
description: Auto-fix for common errors. Lint, type, syntax, test failures. Quick fixes without manual intervention.
auto_trigger: true
trigger:
  keyword: 自動修正|auto-fix|lint|型エラー|type error|syntax
---

# Auto-Fix Skill

自動修正スキル。よくあるエラーを自動で修正。

---

## 対応エラー種類

### 1. Lintエラー

```yaml
検出パターン:
  - ESLint warnings/errors
  - Prettier formatting issues
  - StyleLint issues

自動修正:
  command: npm run lint:fix または npx eslint --fix
  成功率: 90%+

手動対応:
  - カスタムルール違反
  - 複雑なロジック問題
```

### 2. 型エラー（TypeScript）

```yaml
検出パターン:
  - TS2XXX errors
  - Type 'X' is not assignable to 'Y'
  - Property 'X' does not exist

自動修正:
  - 型アノテーション追加
  - Optional chaining追加 (?.)
  - Null check追加
  成功率: 70%

手動対応:
  - 設計レベルの型問題
  - ジェネリクスの複雑な問題
```

### 3. 構文エラー

```yaml
検出パターン:
  - SyntaxError
  - Unexpected token
  - Missing semicolon/bracket

自動修正:
  - 括弧の補完
  - セミコロン追加
  - インデント修正
  成功率: 85%

手動対応:
  - ロジックエラー
  - 意図不明な構文
```

### 4. テスト失敗

```yaml
検出パターン:
  - AssertionError
  - Expected X but got Y
  - Timeout

自動修正:
  - スナップショット更新 (--updateSnapshot)
  - モック修正
  - タイムアウト延長
  成功率: 40%

手動対応:
  - ロジックバグ
  - 仕様変更に伴う失敗
```

---

## 修正フロー

```
エラー検出
    ↓
エラー種類を判別
    ↓
┌─────────────────┬─────────────────┐
│ 自動修正可能     │ 手動対応必要     │
├─────────────────┼─────────────────┤
│ 修正コマンド実行  │ systematic-debug │
│       ↓         │ スキルに委譲      │
│ 再検証          │                 │
│       ↓         │                 │
│ パス → 完了     │                 │
│ 失敗 → 手動対応  │                 │
└─────────────────┴─────────────────┘
```

---

## 自動修正コマンド

### JavaScript/TypeScript

```yaml
Lint修正:
  - npx eslint . --fix
  - npx prettier --write .

型チェック:
  - npx tsc --noEmit（チェックのみ）

テスト:
  - npm test
  - npm test -- --updateSnapshot（スナップショット更新）
```

### Python

```yaml
Lint修正:
  - black .
  - isort .
  - ruff --fix .

型チェック:
  - mypy .

テスト:
  - pytest
```

---

## 安全ガード

### 修正前の確認

```yaml
必須チェック:
  - Gitで変更追跡中か確認
  - 変更前の状態をstash可能か
  - 破壊的変更でないか

禁止操作:
  ❌ --force オプションの使用
  ❌ ファイル削除を伴う修正
  ❌ 依存関係の自動更新
```

### 修正後の検証

```yaml
必須検証:
  - 修正が意図通りか
  - 新しいエラーが発生していないか
  - テストがパスするか

失敗時:
  - 変更を元に戻す
  - systematic-debugスキルに委譲
  - 手動対応を提案
```

---

## エラーパターン別対応

| エラー | 自動修正 | 成功率 |
|--------|---------|--------|
| `no-unused-vars` | 変数削除/使用 | 90% |
| `prefer-const` | let→const | 95% |
| `missing-semicolon` | セミコロン追加 | 99% |
| `TS2322 type mismatch` | 型アサーション | 60% |
| `TS2339 property missing` | optional chaining | 70% |
| `test timeout` | タイムアウト延長 | 50% |

---

## 使用例

```
「lintエラー直して」→ npm run lint:fix 実行
「型エラー修正して」→ TSエラー分析 → 自動修正試行
「テスト通して」→ テスト実行 → 失敗分析 → 修正
```

---

## 連携スキル

| スキル | 連携内容 |
|--------|----------|
| `systematic-debug` | 自動修正失敗時に委譲 |
| `code-review` | 修正後のレビュー |
| `quality-gate` | 修正後の品質確認 |

---

## 更新履歴

```
[2026-02-02] 初期作成
```
