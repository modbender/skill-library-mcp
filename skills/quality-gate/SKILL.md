---
name: quality-gate
description: Quality gates for code and operations. Enforce build, lint, test pass before deployment. Auto-triggers before commits and deploys.
auto_trigger: true
trigger:
  keyword: デプロイ|deploy|リリース|release|本番|production|コミット|commit
---

# Quality Gate Skill

品質ゲート。デプロイ・コミット前に必須チェックを強制。

---

## 品質ゲートレベル

### Level 1: 開発時（常時）

```yaml
チェック項目:
  - [ ] 構文エラーなし
  - [ ] 型エラーなし（TypeScript）
  - [ ] lint警告なし

失敗時: 警告表示、続行可能
```

### Level 2: コミット前（MUST）

```yaml
チェック項目:
  - [ ] Level 1 すべてパス
  - [ ] テストパス
  - [ ] セキュリティスキャン（基本）

失敗時: コミット拒否
```

### Level 3: デプロイ前（MUST）

```yaml
チェック項目:
  - [ ] Level 2 すべてパス
  - [ ] 全テストパス
  - [ ] セキュリティスキャン（詳細）
  - [ ] 本番設定確認（DEV_MODE=false等）

失敗時: デプロイ拒否
```

---

## 自動チェック項目

### TypeScript/JavaScript

```yaml
構文チェック:
  command: npx tsc --noEmit
  必須: Yes

Lintチェック:
  command: npm run lint
  必須: Yes

テスト:
  command: npm test
  必須: Yes（Level 2以上）

ビルド:
  command: npm run build
  必須: Yes（Level 3）
```

### セキュリティ

```yaml
基本スキャン:
  - 機密情報のハードコード検出
  - 既知の脆弱パターン検出

詳細スキャン:
  - 依存関係の脆弱性（npm audit）
  - OWASP Top 10チェック
  - security-reviewスキル連携
```

### 本番設定

```yaml
確認項目:
  - DEV_MODE !== 'true'
  - DEBUG_ROUTES !== 'true'
  - 必須環境変数の存在
  - シークレットの設定状況
```

---

## ゲート通過フロー

```
コード変更
    ↓
Level 1 チェック
    ↓ パス
コミット要求
    ↓
Level 2 チェック
    ↓ パス
コミット実行
    ↓
デプロイ要求
    ↓
Level 3 チェック
    ↓ パス
デプロイ実行
```

---

## 失敗時の対応

### 構文/型エラー

```yaml
対応:
  1. エラー箇所を特定
  2. systematic-debugスキルで修正
  3. 再チェック
```

### テスト失敗

```yaml
対応:
  1. 失敗テストを特定
  2. 原因を分析
  3. コード修正 or テスト修正
  4. 再チェック
```

### セキュリティ問題

```yaml
対応:
  1. 問題の重大度を確認
  2. CRITICAL/HIGH → 即座に修正
  3. MEDIUM以下 → 修正 or 受容判断
  4. security-reviewスキルで詳細分析
```

---

## レポートフォーマット

```yaml
品質ゲートレポート:
  level: 2
  timestamp: 2026-02-02T12:00:00Z

  checks:
    - name: TypeScript
      status: PASS
      duration: 5s

    - name: Lint
      status: PASS
      duration: 3s

    - name: Tests
      status: FAIL
      details: "2 tests failed"
      failures:
        - test_name: "should validate input"
          error: "Expected true, got false"

  verdict: BLOCKED
  reason: "テスト失敗のためコミットできません"
  action: "失敗テストを修正してください"
```

---

## 連携スキル

| スキル | 連携内容 |
|--------|----------|
| `security-review` | セキュリティスキャン |
| `systematic-debug` | 問題修正 |
| `code-review` | コード品質確認 |

---

## 使用例

```
「コミットして」→ Level 2 ゲートチェック
「デプロイして」→ Level 3 ゲートチェック
「品質チェックして」→ 現在のレベルでチェック
```

---

## 更新履歴

```
[2026-02-02] 初期作成
```
