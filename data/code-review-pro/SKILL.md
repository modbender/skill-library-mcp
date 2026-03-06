---
name: rey-code-review
description: Comprehensive code review for quality, security, and best practices. Quick review for small changes, full review for large changes.
auto_trigger: false
---

# Code Review Skill

包括的なコードレビュー。品質、セキュリティ、ベストプラクティスをチェック。

---

## レビューレベル

### Quick Review（即座レビュー）

```yaml
対象: 小さな変更（1-3ファイル）
所要時間: 30秒-1分

チェック項目:
  - 構文エラー
  - 明らかなバグ
  - 型エラー
  - 未使用変数
  - コーディング規約違反
```

### Standard Review（標準レビュー）

```yaml
対象: 中程度の変更（4-10ファイル）
所要時間: 2-5分

チェック項目:
  - Quick Reviewの全項目
  - ロジックの正確性
  - エラーハンドリング
  - エッジケース処理
  - テストカバレッジ
  - ドキュメント
```

### Full Review（徹底レビュー）

```yaml
対象: 大きな変更、重要な機能
所要時間: 10-20分

チェック項目:
  - Standard Reviewの全項目
  - アーキテクチャ適合性
  - パフォーマンス影響
  - セキュリティ影響
  - 保守性
  - スケーラビリティ
  - 副作用の分析
```

---

## レビュー観点

### 1. 正確性（Correctness）

```yaml
チェック:
  - ロジックが正しいか
  - 期待通りの動作をするか
  - エッジケースが処理されているか
  - null/undefinedが適切に処理されているか

よくある問題:
  - off-by-oneエラー
  - 境界条件の見落とし
  - 型の不一致
  - 非同期処理の順序問題
```

### 2. 可読性（Readability）

```yaml
チェック:
  - 変数名・関数名が適切か
  - コードの意図が明確か
  - 複雑すぎないか
  - コメントが適切か

原則:
  - 自己文書化コード
  - 単一責任の原則
  - 適切な抽象化レベル
```

### 3. 保守性（Maintainability）

```yaml
チェック:
  - 変更が容易か
  - テストが書きやすいか
  - 依存関係が適切か
  - 重複がないか

注意点:
  - マジックナンバーを避ける
  - ハードコードを避ける
  - 適切なモジュール分割
```

### 4. セキュリティ（Security）

```yaml
チェック:
  - インジェクション脆弱性
  - 認証・認可の問題
  - 機密情報の扱い
  - 入力検証

詳細: security-reviewスキルを参照
```

### 5. パフォーマンス（Performance）

```yaml
チェック:
  - 不要なループ
  - N+1問題
  - メモリリーク
  - 重い処理

注意点:
  - 早すぎる最適化は避ける
  - 計測してから最適化
```

---

## レビューコメントフォーマット

```yaml
CRITICAL（必須修正）:
  - セキュリティ脆弱性
  - データ損失リスク
  - 本番障害リスク

MAJOR（修正推奨）:
  - バグの可能性
  - パフォーマンス問題
  - 設計上の問題

MINOR（検討推奨）:
  - コーディング規約違反
  - 可読性の改善
  - ベストプラクティス

NIT（任意）:
  - 細かい指摘
  - スタイルの提案
  - 個人的な好み
```

---

## レビューレポート

```yaml
コードレビューレポート:
  summary:
    files_reviewed: N
    critical: N
    major: N
    minor: N
    nit: N

  verdict: APPROVED / NEEDS_CHANGES / BLOCKED

  findings:
    - severity: CRITICAL/MAJOR/MINOR/NIT
      file: ファイル名
      line: 行番号
      issue: 問題の説明
      suggestion: 修正提案

  positive:
    - 良かった点
```

---

## 連携スキル

| スキル | 連携内容 |
|--------|----------|
| `security-review` | セキュリティ観点 |
| `systematic-debug` | バグ発見時のデバッグ |
| `failure-analyzer` | 問題分析 |
| `quality-checker` | 品質メトリクス |

---

## 使用例

```
「このコードをレビューして」→ Standard Review
「クイックレビューして」→ Quick Review
「徹底的にレビューして」→ Full Review
「セキュリティ観点でレビュー」→ security-review連携
```

---

## 更新履歴

```
[2026-02-02] 初期作成
```

---

*良いコードレビューは、バグを防ぎ、知識を共有し、品質を向上させます。*
