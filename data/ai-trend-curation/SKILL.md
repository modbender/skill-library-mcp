---
name: ai-trend-curation
description: Curate and post AI trend tweets from X (Twitter) with quote suggestions.
metadata:
  {
    "openclaw":
      {
        "emoji": "🤖",
        "requires": { "bins": ["xurl"], "scripts": ["scripts/ai_trends.js"] },
      },
  }
---

# ai-trend-curation

X (Twitter) から AI 関連のトレンドツイートを収集・キュレーションし、Slack に投稿する。

## ワークフロー

### Step 1: ツイート検索

```bash
node scripts/ai_trends.js search
```

xurl CLI で日本語・英語の AI 関連ツイートを検索。いいね100以上（日本語）/ 500以上（英語）をフィルタ。

### Step 2: キュレーション（エージェント実行）

検索結果をもとに、エージェントが以下を判断:
- 5-8件を選定（日本語3-5件 + 英語3-5件のバランス）
- 驚き屋・煽り系は排除。実務者・技術者の実践ベース投稿を優先
- 各ツイートに category, author_desc, text_ja(英語の場合), quote_suggestion を付与

### Step 3: 重複チェック

```bash
node scripts/ai_trends.js check-recent
```

最近投稿済みのURLと重複しないか確認。

### Step 4: Block Kit フォーマット

```bash
node scripts/ai_trends.js format-blocks \
  --tweets='[{...curated tweets...}]' \
  --summary="今日のAIトレンド要約"
```

### Step 5: Slack 投稿

`openclaw message send` で親メッセージ + スレッド返信を投稿。

### Step 6: 投稿済みマーク

```bash
node scripts/ai_trends.js mark-posted --urls='["url1","url2"]'
```

## 選定フィルター

- @yusaku_0426 が引用して付加価値を出せるか
- 元ツイートの発信者がRTしてくれそうか（批判・揚げ足取りNG）

## 引用ツイート案のペルソナ

一人称「僕」、丁寧語 or 体言止め。情報整理型キュレーター。
5-100文字で簡潔に。「最高！」「同意です」のような薄いリアクションは絶対NG。

## 引用パターン (A-H)

- A: 要点抜粋+補足解説
- B: 注目ポイント指摘（「地味に重要なのは〜」）
- C: 活用報告（「試してみた」＋体験）
- D: 共感（短い一言で同意）
- E: 一行要約（本質をワンフレーズに凝縮）
- F: 問いかけ・展開（「これ〜にも応用できそう」）
- G: 比較・接続（別ツール/事例と比較）
- H: 数字・データ強調

## カテゴリ

- :rocket: new_release
- :hammer_and_wrench: tools
- :microscope: research
- :thought_balloon: opinions
- :bulb: tips
