---
name: rey-model-router
description: Automatically select optimal model based on task complexity. Routes simple tasks to Sonnet 4.5 (cost-effective) and complex tasks to Opus 4.6 (high-quality). Always active.
auto_trigger: true
---

# Intelligent Model Router

You are an AI assistant with access to multiple Claude models. You MUST select the appropriate model for each task to optimize cost and quality.

## Available Models

| Model | Use Case | Cost |
|-------|----------|------|
| **Sonnet 4.5** (Default) | Daily tasks, simple queries | $3/$15 per MTok |
| **Opus 4.6** | Complex tasks, code generation | $5/$25 per MTok |

## Routing Rules (MUST FOLLOW)

### Use Sonnet 4.5 (Default) for:
- SNS投稿文生成 (social media posts)
- 情報収集・要約 (information gathering, summaries)
- 簡単な問い合わせ対応 (simple Q&A)
- トレンド分析 (trend analysis)
- 画像プロンプト生成 (image prompt creation)
- 日常会話 (casual conversation)
- 簡単な翻訳 (simple translation)
- ファイル操作の説明 (file operation explanations)

### Switch to Opus 4.6 for:
- GASコード作成 (Google Apps Script development)
- 業務自動化ツール開発 (business automation tools)
- 複雑なコード実装 (complex code implementation)
- システム設計・アーキテクチャ (system design/architecture)
- カスタマイズ要望対応 (customization requests)
- 複雑な分析・レポート (complex analysis/reports)
- デバッグ・トラブルシューティング (debugging, troubleshooting)
- API統合・開発 (API integration/development)
- セキュリティ監査 (security audits)

## Detection Keywords

**Opus Triggers (Switch when detected):**
```
Japanese: GAS, スプレッドシート, コード作成, 実装して, 開発して,
         自動化ツール, システム構築, ココナラ納品, カスタマイズ,
         複雑な, 詳細な分析, デバッグ, API連携, セキュリティ

English: implement, develop, build system, automation tool,
        complex code, architecture, debug, API integration
```

## Execution Protocol

1. **Analyze** the user's request
2. **Check** for Opus trigger keywords or complexity indicators
3. **If unclear, self-evaluate complexity (0-10 scale)**:
   - Consider: Does this require precise code generation? Multi-step reasoning? System design?
   - Score 7+ → Use Opus
   - Score 6 or below → Use Sonnet
4. **If Opus needed**:
   - Announce: "このタスクは複雑なので、高品質モデル(Claude Opus 4.6)に切り替えます。"
   - Execute: `/model anthropic/claude-opus-4-6`
   - Then proceed with the task
5. **If Sonnet sufficient**: Proceed directly without switching

## Self-Evaluation Criteria (When Keywords Don't Match)

Ask yourself these questions:
- [ ] Does this require writing >50 lines of code?
- [ ] Does this involve system architecture or design decisions?
- [ ] Does this require debugging complex logic?
- [ ] Does this need multi-step reasoning with dependencies?
- [ ] Is accuracy critical (financial, security, legal)?

**2つ以上 Yes → Opus を使用**

## Cost Tracking (Optional)

After completing tasks, you may note:
- "💰 Sonnetで処理しました（コスト効率: 高）"
- "🎯 Opus 4.6で高品質な結果を生成しました"

## Important Notes

- Default to Sonnet unless clearly complex
- When in doubt, start with Sonnet
- User can always request `/model opus` manually to override
- This routing is for cost optimization, not capability limitation

---

## サブスク ↔ API 自動切り替え機能

### 概要

Claude Code サブスク（Pro/Max）の使用量制限に達した場合、
自動的にAnthropicAPIに切り替え、制限解除後はサブスクに戻る。

### 切り替えトリガー

```
サブスク制限検出:
├── 429エラー（Too Many Requests）
├── "usage limit reached" メッセージ
├── "rate limit" メッセージ
└── "please wait" + 時間表示
```

### 切り替えフロー

```
┌─────────────────────────────────────────────────────────────────┐
│  通常運用: サブスク使用中                                        │
│                                                                  │
│  制限検出                                                        │
│       ↓                                                          │
│  1. 制限の種類を判定                                             │
│     ├── 5-8時間制限（Pro/Max共通）→ タイマー6時間               │
│     └── 週間制限（Maxのみ）→ タイマー7日                        │
│                                                                  │
│  2. ANTHROPIC_API_KEY を有効化                                   │
│     → API使用モードに切り替え                                   │
│     → 監督者に通知「APIに切り替えました」                       │
│                                                                  │
│  3. タイマー経過後                                               │
│     → ANTHROPIC_API_KEY を無効化                                │
│     → サブスクモードに復帰                                      │
│     → 監督者に通知「サブスクに戻りました」                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 環境変数設定

```bash
# サブスク優先モード（デフォルト）
# ANTHROPIC_API_KEY は設定しておくが、使用しない

# API切り替え時に使用
ANTHROPIC_API_KEY_BACKUP="sk-ant-..."  # バックアップ用

# 切り替え設定
SUBSCRIPTION_FALLBACK_ENABLED=true
SUBSCRIPTION_RESET_HOURS=6  # 5-8時間制限用
SUBSCRIPTION_RESET_DAYS=7   # 週間制限用
```

### 実装コード（参考）

```javascript
// 制限検出
function detectRateLimit(response) {
  const limitIndicators = [
    'usage limit reached',
    'rate limit',
    'too many requests',
    'please wait',
    '429'
  ];

  return limitIndicators.some(indicator =>
    response.toLowerCase().includes(indicator)
  );
}

// 切り替え実行
async function switchToAPI() {
  // 1. 現在の状態を保存
  const previousMode = getCurrentMode(); // 'subscription' or 'api'

  // 2. API モードに切り替え
  process.env.ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY_BACKUP;

  // 3. タイマー設定（6時間後にサブスクに戻る）
  const resetTime = 6 * 60 * 60 * 1000; // 6時間
  setTimeout(() => switchToSubscription(), resetTime);

  // 4. 監督者に通知
  await notify('サブスク制限により、APIに切り替えました。6時間後に自動復帰します。');

  return { mode: 'api', resetAt: Date.now() + resetTime };
}

// サブスク復帰
async function switchToSubscription() {
  // API キーを無効化（環境変数から削除）
  delete process.env.ANTHROPIC_API_KEY;

  // 監督者に通知
  await notify('サブスクモードに復帰しました。');

  return { mode: 'subscription' };
}
```

### 通知テンプレート

```
【制限検出時】
⚠️ サブスク使用量制限に達しました。
→ Anthropic APIに自動切り替えします。
→ 約6時間後にサブスクに自動復帰します。
→ API使用中はコストが発生します。

【復帰時】
✅ サブスクモードに復帰しました。
→ 制限がリセットされ、サブスク枠を使用します。
→ API使用量: 約$X.XX
```

### 手動切り替えコマンド

```
/mode subscription  → サブスクモードに切り替え
/mode api           → APIモードに切り替え
/mode status        → 現在のモード確認
/mode auto          → 自動切り替え有効化
```

### コスト管理

```
API使用時の推定コスト:
├── 短い会話（~1Kトークン）: ~$0.02
├── 普通の会話（~5Kトークン）: ~$0.08
├── 長い作業（~20Kトークン）: ~$0.35
└── 制限解除までの目安: $1-5

監督者への報告:
├── 切り替え発生時に即座に通知
├── API使用コストを追跡
└── 週次でコストレポート
```

### 注意事項

```
MUST:
├── 切り替え時は必ず監督者に通知
├── APIコストを追跡・報告
├── 自動復帰が失敗した場合は手動で対応
└── 大量のAPI使用が予想される場合は事前に確認

禁止:
├── 通知なしでの切り替え
├── コスト追跡なしでのAPI使用
└── 復帰タイマーの無効化
```

### 参考リンク

- [GitHub Issue #2944 - API Fallback Feature Request](https://github.com/anthropics/claude-code/issues/2944)
- [GitHub Issue #3835 - Switch Max to API](https://github.com/anthropics/claude-code/issues/3835)
- [claude-code-switch (Third-party tool)](https://github.com/foreveryh/claude-code-switch)
