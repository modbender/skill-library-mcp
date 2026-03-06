---
name: failure-analyzer
description: Failure analysis and learning system. Root cause analysis, improvement suggestions, experience-based learning. Applies to all skills.
auto_trigger: true
trigger:
  keyword: 失敗|エラー|うまくいかない|問題|fail|error|not working
---

# Failure Analyzer & Learning System

失敗分析・学習システム。全スキルで共通使用。失敗から学び、同じミスを繰り返さない。

## コンセプト

```
失敗は学習機会。
├── なぜ失敗したか（原因分析）
├── どうすれば防げたか（予防策）
├── 次は何を変えるか（改善策）
└── 経験として記録（知識蓄積）
```

---

## 分析フレームワーク

### 5 Whys Analysis（なぜなぜ分析）

```yaml
Process:
  1. 問題の定義
  2. なぜ？（1回目）
  3. なぜ？（2回目）
  4. なぜ？（3回目）
  5. なぜ？（4回目）
  6. なぜ？（5回目）→ 根本原因

Example:
  Problem: "YouTube動画の視聴回数が伸びない"
  Why1: サムネイルのCTRが低い
  Why2: サムネイルが目立たない
  Why3: 色のコントラストが弱い
  Why4: デザインテンプレートが古い
  Why5: 競合分析をしていなかった
  Root Cause: 競合チャンネルのサムネイル分析プロセスがなかった
  Solution: 新動画作成前に競合TOP5のサムネイルを分析するステップを追加
```

### 失敗カテゴリ

```yaml
Categories:
  technical:
    - API エラー
    - コード バグ
    - インフラ 障害
    - 設定 ミス

  strategic:
    - 市場 読み違い
    - タイミング ミス
    - ターゲット 誤り
    - 価格設定 失敗

  operational:
    - プロセス 不備
    - リソース 不足
    - コミュニケーション ミス
    - 品質管理 漏れ

  external:
    - プラットフォーム 変更
    - 競合 行動
    - 規制 変更
    - 市場 変動
```

---

## 自動分析プロセス

### トリガー条件

```yaml
Auto-trigger:
  - エラーメッセージ検出
  - 期待値の50%以下のパフォーマンス
  - タスク失敗
  - ユーザーからの「うまくいかない」報告
  - KPI未達

Manual-trigger:
  - 「なぜ失敗した？」
  - 「分析して」
  - 「原因を調べて」
```

### 分析フロー

```
失敗検出
    ↓
1. 状況の記録
   ├── 何をしようとしたか
   ├── 何が起きたか
   ├── いつ起きたか
   └── 影響範囲は

2. データ収集
   ├── エラーログ
   ├── 実行履歴
   ├── 設定状態
   └── 外部要因

3. 原因分析（5 Whys）
   ├── 直接原因
   ├── 間接原因
   └── 根本原因

4. 解決策立案
   ├── 即時対応
   ├── 短期改善
   └── 長期予防

5. 学習記録
   ├── 教訓の抽出
   ├── パターン認識
   └── 知識ベース更新

6. 実行・検証
   ├── 解決策実行
   ├── 効果確認
   └── 完了報告
```

---

## 学習データベース

### 保存構造

```
/moltworker/data/learning/
├── failures.json        # 失敗記録
├── patterns.json        # 失敗パターン
├── solutions.json       # 解決策カタログ
├── improvements.json    # 改善履歴
└── metrics.json         # 効果測定
```

### 失敗レコード形式

```json
{
  "id": "fail-2026-02-02-001",
  "timestamp": "2026-02-02T10:30:00Z",
  "skill": "youtube-automation",
  "task": "動画アップロード",
  "expected": "成功アップロード",
  "actual": "API認証エラー",
  "category": "technical",
  "severity": "medium",
  "analysis": {
    "why1": "OAuth トークンが期限切れ",
    "why2": "トークン更新処理がなかった",
    "why3": "エラーハンドリング不足",
    "why4": "テスト不十分",
    "why5": "CI/CDにAPIテストがない",
    "root_cause": "自動トークン更新メカニズムの欠如"
  },
  "solution": {
    "immediate": "手動でトークン更新",
    "short_term": "トークン自動更新コード追加",
    "long_term": "APIテスト自動化"
  },
  "lesson": "OAuth連携では必ず自動トークン更新を実装する",
  "status": "resolved",
  "prevention_applied": true
}
```

---

## パターン認識

### 自動パターン検出

```yaml
Pattern Detection:
  frequency_threshold: 2  # 2回同じパターンで警告
  similarity_threshold: 0.7  # 70%類似で同一パターン判定

Pattern Types:
  recurring:
    description: 同じ失敗が繰り返される
    action: 根本対策の強化

  seasonal:
    description: 特定時期に発生
    action: 事前予防策の設定

  correlated:
    description: 他の失敗と連動
    action: 依存関係の見直し

  escalating:
    description: 徐々に悪化
    action: 早期介入の仕組み
```

### 予防的警告

```yaml
Proactive Warnings:
  before_action:
    - 過去の類似失敗を検索
    - リスク要因をチェック
    - 警告メッセージを表示

  warning_format: |
    ⚠️ 注意: この操作で過去に失敗があります

    過去の失敗:
    - [失敗内容]
    - 原因: [原因]
    - 対策: [対策]

    今回の実行前に確認:
    - [ ] [チェック項目1]
    - [ ] [チェック項目2]
```

---

## スキル別学習

### DeFi/仮想通貨

```yaml
defi-optimizer:
  track_metrics:
    - 取引成功率
    - 損益（PnL）
    - ガス代効率
    - 清算回避率

  failure_types:
    - 清算発生
    - スリッページ過大
    - ガス不足
    - トランザクション失敗
    - 価格予測ミス

  learning_focus:
    - 市場パターン
    - 最適タイミング
    - リスク管理
    - ガス最適化

  strategy_evolution:
    - 成功戦略の強化
    - 失敗戦略の修正/廃止
    - 新戦略のテスト
    - パラメータ最適化
```

### YouTube自動化

```yaml
youtube-automation:
  track_metrics:
    - 視聴回数
    - CTR
    - 視聴維持率
    - 登録者増加

  failure_types:
    - 低CTR
    - 低視聴維持
    - コンテンツ削除
    - アップロードエラー

  learning_focus:
    - サムネイルパターン
    - タイトル構成
    - コンテンツ構造
    - 公開タイミング
```

### アフィリエイト

```yaml
affiliate-marketing:
  track_metrics:
    - クリック率
    - コンバージョン率
    - 収益

  failure_types:
    - 低クリック率
    - 低コンバージョン
    - リンク切れ
    - ポリシー違反

  learning_focus:
    - CTA最適化
    - 商品選定
    - プレースメント
    - タイミング
```

---

## 成長サイクル

### 継続的改善ループ

```
Plan（計画）
    ↓
Do（実行）
    ↓
Check（評価）
    ↓
Act（改善）
    ↓
Learn（学習）← 新規追加
    ↓
Plan（次の計画）
```

### 自己評価

```yaml
Weekly Review:
  - 今週の失敗数
  - 解決した問題
  - 新しく学んだこと
  - 改善した指標
  - 次週の焦点

Monthly Review:
  - 月間パターン分析
  - 成長トレンド
  - スキル別成績
  - 長期改善計画

Quarterly Review:
  - 戦略的評価
  - 大きな転換点
  - 投資対効果
  - 次四半期目標
```

---

## レポート形式

### 失敗分析レポート

```markdown
# 失敗分析レポート

## 概要
- **発生日時:** 2026-02-02 10:30
- **スキル:** youtube-automation
- **タスク:** 動画アップロード
- **重大度:** Medium

## 何が起きたか
動画アップロードがAPI認証エラーで失敗

## 原因分析（5 Whys）
1. OAuth トークンが期限切れ
2. トークン更新処理がなかった
3. エラーハンドリング不足
4. テスト不十分
5. **根本原因:** CI/CDにAPIテストがない

## 解決策
- **即時:** 手動でトークン更新
- **短期:** トークン自動更新コード追加
- **長期:** APIテスト自動化

## 学んだこと
OAuth連携では必ず自動トークン更新を実装する

## 予防策
- [ ] 全OAuth連携にリフレッシュトークン機能追加
- [ ] APIテストをCI/CDに組み込み
```

---

## 監督者通知

### 通知条件

```yaml
Notify Supervisor:
  - severity: high/critical
  - financial_impact: $100以上
  - recurring_pattern: 3回以上
  - security_related: true
  - user_impacting: true

Notification Format:
  title: "[FAILURE] {skill}: {brief_description}"
  body: |
    重大度: {severity}
    原因: {root_cause}
    影響: {impact}
    対応状況: {status}
    承認必要: {approval_needed}
```

---

## 連携スキル

| スキル | 連携内容 |
|--------|----------|
| `learn-from-mistake` | 教訓のLESSONS_LEARNED.md記録 |
| `root-cause-tracing` | 詳細な原因分析 |
| `systematic-debugging` | 技術的デバッグ |
| 全スキル | 失敗データの収集・学習 |

---

## 使用例

```
「なぜ失敗した？」
→ 5 Whys分析 → 根本原因特定 → 解決策提案 → 学習記録

「同じミスを防ぎたい」
→ パターン分析 → 予防策設定 → チェックリスト作成

「最近の失敗を振り返って」
→ 週次レポート生成 → トレンド分析 → 改善提案
```

---

## 更新履歴

```
[2026-02-02] 初期作成
```

---

*失敗は成功の母。記録し、分析し、学び、成長する。*
