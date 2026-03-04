---
name: voice-memo
description: Manage voice memos — add transcriptions, search, and list recent memos with summaries and action items.
metadata:
  {
    "openclaw":
      {
        "emoji": "🎙️",
        "requires": { "scripts": ["scripts/voice_memo.js"] },
      },
  }
---

# voice-memo

ボイスメモの管理。文字起こしテキストの保存、要約・キーワード抽出、検索。

## Script

```bash
# メモ追加（要約・トピック・決定事項はエージェントが分析して渡す）
node scripts/voice_memo.js add \
  --content="今日のミーティングでプロダクトロードマップについて議論した" \
  --summary="Q2ロードマップを議論。モバイル優先に決定。" \
  --topics="ロードマップ,Q2,モバイル" \
  --decisions="モバイルアプリをQ2最優先|デザインレビュー隔週化" \
  --action_items="UIモック作成（来週金曜）|スパイクチケット作成"

# キーワード検索
node scripts/voice_memo.js search --query="ロードマップ" --limit=10

# 直近メモ一覧
node scripts/voice_memo.js list --days=7 --limit=10

# 特定日のメモ件数
node scripts/voice_memo.js count --date=2026-02-24
```

## 要約ワークフロー

ユーザーがボイスメモのテキスト（文字起こし）を送信した場合:

1. テキストを分析して以下を抽出:
   - summary: 2-3文の日本語要約
   - topics: 関連キーワード最大5つ（カンマ区切り）
   - decisions: 決定事項（パイプ区切り、なければ空）
   - action_items: アクションアイテム「誰が何をいつまでに」（パイプ区切り、なければ空）
2. `voice_memo.js add` で記録
3. ユーザーに結果を返信

## 返信フォーマット

```
✅ ボイスメモ保存しました

📝 *要約*
Q2ロードマップを議論。モバイル優先に決定。

✅ *決定事項*
• モバイルアプリをQ2最優先
• デザインレビュー隔週化

📋 *アクションアイテム*
• UIモック作成（来週金曜）
• スパイクチケット作成

🏷️ ロードマップ, Q2, モバイル
```

## デイリースレッド

毎朝8時にボイスメモスレッドを作成: `:studio_microphone: YYYY-MM-DD（曜日）のボイスメモスレッド`
毎晩21時にメモ未記録なら リマインダーを送信。
