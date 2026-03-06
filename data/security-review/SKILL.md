---
name: security-review
description: Comprehensive security review for code, configs, and operations. OWASP, prompt injection, crypto security. Auto-triggers on security-related changes.
auto_trigger: true
trigger:
  keyword: セキュリティ|脆弱性|security|vulnerability|攻撃|attack|レビュー|review
---

# Security Review Skill

包括的なセキュリティレビュー。コード、設定、運用すべてを対象。

---

## レビューカテゴリ

### 1. コードセキュリティ

```yaml
OWASP Top 10:
  - A01: Broken Access Control（アクセス制御の不備）
  - A02: Cryptographic Failures（暗号化の失敗）
  - A03: Injection（インジェクション）
  - A04: Insecure Design（安全でない設計）
  - A05: Security Misconfiguration（セキュリティ設定ミス）
  - A06: Vulnerable Components（脆弱なコンポーネント）
  - A07: Authentication Failures（認証の失敗）
  - A08: Data Integrity Failures（データ整合性の失敗）
  - A09: Logging Failures（ログの不備）
  - A10: SSRF（サーバーサイドリクエストフォージェリ）

チェック項目:
  - SQL/NoSQLインジェクション
  - XSS（クロスサイトスクリプティング）
  - CSRF（クロスサイトリクエストフォージェリ）
  - コマンドインジェクション
  - パストラバーサル
  - 認証バイパス
  - 権限昇格
  - 機密情報漏洩
```

### 2. 設定セキュリティ

```yaml
環境変数:
  - シークレットがハードコードされていないか
  - DEV_MODEが本番で無効か
  - DEBUG_ROUTESが本番で無効か
  - 不要な環境変数がないか

認証設定:
  - Cloudflare Access設定
  - APIキー管理
  - OAuthトークン管理
  - セッション管理
```

### 3. 暗号資産セキュリティ

```yaml
ウォレットセキュリティ:
  - シードフレーズの保護
  - 秘密鍵の管理
  - 送金承認フロー
  - 累積送金監視

DeFiセキュリティ:
  - コントラクト検証
  - スマートコントラクト監査状況
  - ラグプル/詐欺検出
  - フラッシュローン攻撃対策
```

### 4. AIセキュリティ

```yaml
プロンプトインジェクション:
  - システムプロンプト漏洩
  - ロール変更攻撃
  - 指示無視攻撃
  - エンコード攻撃

スキル悪用:
  - 承認バイパス試行
  - 権限昇格試行
  - 情報収集攻撃
  - ソーシャルエンジニアリング
```

---

## 自動レビュートリガー

```yaml
コード変更時:
  - auth/認証関連の変更
  - 環境変数の追加/変更
  - APIエンドポイントの追加
  - 外部通信の追加

設定変更時:
  - wrangler.toml変更
  - package.json依存関係変更
  - Dockerfile変更

運用時:
  - 新しいDAppへの接続
  - 大口取引
  - 異常なパターン検出
```

---

## レビューレベル

```yaml
Quick Review（即座）:
  - 基本的なパターンチェック
  - 既知の脆弱性パターン検出
  - 所要時間: 数秒

Standard Review（標準）:
  - OWASP Top 10チェック
  - 設定検証
  - 依存関係チェック
  - 所要時間: 1-2分

Deep Review（徹底）:
  - 攻撃者視点での分析
  - 複合攻撃シナリオ検証
  - ビジネスロジック脆弱性
  - 所要時間: 5-10分
```

---

## レポートフォーマット

```yaml
セキュリティレビューレポート:
  summary:
    critical: 0
    high: 0
    medium: 0
    low: 0
    info: 0

  findings:
    - severity: CRITICAL/HIGH/MEDIUM/LOW/INFO
      category: カテゴリ
      title: 問題のタイトル
      description: 詳細説明
      location: ファイル:行番号
      recommendation: 推奨対策

  recommendations:
    - 優先度高い対策
    - 中程度の対策
    - 低優先度の対策
```

---

## 連携スキル

| スキル | 連携内容 |
|--------|----------|
| `moltbook-security` | プロンプトインジェクション対策 |
| `human-security` | ソーシャルエンジニアリング対策 |
| `metamask-wallet` | 暗号資産セキュリティ |
| `failure-analyzer` | インシデント分析 |

---

## 使用例

```
「セキュリティレビューして」→ 全体的なレビュー
「コードのセキュリティチェック」→ コードレビュー
「設定の脆弱性確認」→ 設定レビュー
「DeFi操作のリスク確認」→ 暗号資産セキュリティ
```

---

## 更新履歴

```
[2026-02-02] 初期作成
```

---

*セキュリティは継続的なプロセス。定期的なレビューを推奨します。*
