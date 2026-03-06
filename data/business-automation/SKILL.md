---
name: business-automation
description: Automate business workflows. Connect tools, create pipelines, reduce manual tasks. Build custom automation for enterprises.
auto_trigger: false
---

# Business Automation

ビジネスワークフロー自動化。ツール連携、パイプライン作成、手作業削減。

## 収益ポテンシャル

- **プロジェクト単価**: $500-3,000
- **月額保守**: $100-300/月
- **月収目安**: $800-5,000/月

## 対応自動化

### セールス・マーケティング
- リード獲得 → CRM登録
- フォーム送信 → Salesforce/HubSpot
- LinkedIn接続 → 自動フォローアップ
- ウェビナー登録 → メールシーケンス

### カスタマーサポート
- チケット分類・割り当て
- 自動返信テンプレート
- エスカレーションルール
- FAQ自動回答

### 人事・採用
- 応募受付 → スクリーニング
- 面接スケジュール調整
- オンボーディング自動化
- アカウント作成ワークフロー

### データ処理
- ファイル処理自動化
- レポート生成
- データ同期
- バックアップ

## 使用方法

### 基本自動化
```
「フォーム送信をSlackに通知する自動化を作成」
「新規リードをHubSpotに自動登録」
```

### 複雑なワークフロー
```
「自動化ワークフロー作成
 トリガー: [trigger_event]
 条件: [if_condition]
 アクション1: [action1]
 アクション2: [action2]
 通知: [notification_channel]」
```

## 対応ツール連携

### CRM
- Salesforce, HubSpot, Pipedrive, Zoho CRM

### コミュニケーション
- Slack, Microsoft Teams, Discord, Email

### 生産性
- Notion, Google Workspace, Microsoft 365, Airtable

### 開発
- GitHub, GitLab, Jira, Linear

## ワークフロー設計

### 基本構造
```yaml
name: lead_to_crm
trigger:
  type: webhook
  source: contact_form

steps:
  - name: validate
    action: validate_data

  - name: enrich
    action: data_lookup

  - name: create_contact
    action: crm_create

  - name: notify
    action: slack_message
```

## 価格プラン

### Starter ($500)
- 3つの自動化
- 基本ツール連携
- 1ヶ月サポート

### Professional ($1,500)
- 10つの自動化
- 複雑なワークフロー
- カスタム統合

### Enterprise ($3,000+)
- 無制限自動化
- 専用開発
- SLA付きサポート

## ROI計算例

```
Before: 手作業 500分/日
After: 自動化 100分/日
節約: 400分/日 = 6.6時間/日
```
