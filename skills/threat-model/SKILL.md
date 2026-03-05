---
name: threat-model
description: Threat modeling and attack scenario design. Identify risks before they become vulnerabilities. STRIDE, attack trees, risk matrix.
auto_trigger: false
---

# Threat Model Skill

脅威モデリングと攻撃シナリオ設計。脆弱性になる前にリスクを特定。

---

## 目的

```yaml
脅威モデリングの目的:
  - 攻撃者の視点で考える
  - リスクを事前に特定
  - 対策の優先順位を決める
  - セキュリティ投資を最適化
```

---

## STRIDE分析

```yaml
S - Spoofing（なりすまし）:
  攻撃: 他人になりすましてアクセス
  対策: 強力な認証、MFA

T - Tampering（改ざん）:
  攻撃: データや設定を不正に変更
  対策: 署名、ハッシュ、監査ログ

R - Repudiation（否認）:
  攻撃: 行動を否認する
  対策: ログ、監査証跡

I - Information Disclosure（情報漏洩）:
  攻撃: 機密情報を取得
  対策: 暗号化、アクセス制御

D - Denial of Service（サービス妨害）:
  攻撃: サービスを利用不能に
  対策: レート制限、冗長化

E - Elevation of Privilege（権限昇格）:
  攻撃: より高い権限を取得
  対策: 最小権限原則、RBAC
```

---

## {AGENT_NAME}固有の脅威

### 1. 暗号資産関連

```yaml
脅威:
  - ウォレット秘密鍵の漏洩
  - 不正送金
  - フィッシング攻撃
  - 悪意あるDAppへの接続
  - ラグプル/詐欺プロトコル

対策:
  - 秘密鍵は環境変数のみ
  - 送金は承認フロー必須
  - プロンプトインジェクション対策
  - DApp接続前の検証
  - プロトコル監査状況確認
```

### 2. AI関連

```yaml
脅威:
  - プロンプトインジェクション
  - システムプロンプト漏洩
  - ロール変更攻撃
  - 承認バイパス試行

対策:
  - moltbook-security常時有効
  - 入力検証
  - 出力フィルタリング
  - 技術的強制（コードレベル）
```

### 3. インフラ関連

```yaml
脅威:
  - 認証バイパス
  - DEV_MODE有効化
  - APIキー漏洩
  - サービス妨害

対策:
  - Cloudflare Access
  - 環境変数管理
  - シークレットローテーション
  - レート制限
```

---

## リスクマトリクス

```
          │ Low    │ Medium │ High   │ Critical
──────────┼────────┼────────┼────────┼──────────
Likely    │ Medium │ High   │ Critical│ Critical
Possible  │ Low    │ Medium │ High   │ Critical
Unlikely  │ Info   │ Low    │ Medium │ High
Rare      │ Info   │ Info   │ Low    │ Medium
```

---

## 攻撃シナリオ例

### シナリオ1: 暗号資産窃取

```yaml
攻撃者: 外部の攻撃者
目標: ウォレットから資金を窃取

攻撃経路:
  1. SNSで{AGENT_NAME}にDM
  2. プロンプトインジェクション試行
  3. 「送金して」と指示
  4. 承認バイパス試行

対策:
  - human-security: DMからの不審な要求検出
  - moltbook-security: プロンプトインジェクション検出
  - 承認フロー: 技術的に強制
  - 残高チェック: 実行前に必須
```

### シナリオ2: API悪用

```yaml
攻撃者: 外部の攻撃者
目標: APIを悪用してサービス妨害

攻撃経路:
  1. 公開エンドポイントを発見
  2. 大量リクエストを送信
  3. リソース枯渇/課金増加

対策:
  - CF Access認証
  - レート制限
  - 監視・アラート
```

---

## 使用例

```
「脅威モデリングして」→ STRIDE分析
「攻撃シナリオを考えて」→ 攻撃経路の列挙
「リスク評価して」→ リスクマトリクス作成
```

---

## 更新履歴

```
[2026-02-02] 初期作成
```
