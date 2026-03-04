---
name: video-generator
description: AI video generation with Pika, Runway, HeyGen, Kling. Short-form content for YouTube, TikTok, Instagram. Text/image to video.
auto_trigger: false
---

# AI Video Generator

AI動画生成スキル。Pika, Runway, HeyGen, Klingを使った短尺動画の自動生成。

## 対応プラットフォーム

| プラットフォーム | 最適サイズ | 長さ | 特徴 |
|----------------|-----------|------|------|
| YouTube Shorts | 1080x1920 (9:16) | 60秒以内 | 縦型、ループ推奨 |
| TikTok | 1080x1920 (9:16) | 15-60秒 | トレンド音楽対応 |
| Instagram Reels | 1080x1920 (9:16) | 90秒以内 | ストーリー連携 |
| YouTube (通常) | 1920x1080 (16:9) | 制限なし | 横型、長尺OK |

---

## AI動画生成ツール

### Tier 1: 推奨ツール

| ツール | 用途 | 料金 | 品質 |
|--------|------|------|------|
| **Pika** | テキスト→動画、画像→動画 | $8/月~ | ★★★★☆ |
| **Runway Gen-3** | 高品質動画生成、編集 | $12/月~ | ★★★★★ |
| **Kling AI** | 長尺動画、一貫性 | $6/月~ | ★★★★☆ |
| **HeyGen** | アバター動画、多言語 | $24/月~ | ★★★★★ |

### Tier 2: 補助ツール

| ツール | 用途 | 料金 |
|--------|------|------|
| **Luma Dream Machine** | シネマティック動画 | $10/月~ |
| **Stable Video** | オープンソース | 無料/クレジット |
| **Leonardo AI** | 画像→短い動画 | $10/月~ |
| **Synthesia** | アバタープレゼン | $22/月~ |

---

## 生成モード

### 1. テキスト→動画 (Text-to-Video)

```yaml
Mode: text-to-video
Input: テキストプロンプト
Output: 4-10秒の動画クリップ
Tools: Pika, Runway, Kling

Example Prompt:
  "A cat walking through a cyberpunk city at night,
   neon lights reflecting on wet streets,
   cinematic lighting, 4K quality"

Best Practices:
  - 具体的な描写（色、光、動き）
  - カメラアングルを指定
  - スタイル参照（cinematic, anime, realistic）
  - 否定プロンプトで不要要素を除外
```

### 2. 画像→動画 (Image-to-Video)

```yaml
Mode: image-to-video
Input: 静止画 + モーション指示
Output: 4-10秒の動画クリップ
Tools: Pika, Runway, Kling, Luma

Use Cases:
  - 商品画像のアニメーション
  - イラストの動画化
  - サムネイルの動画化

Motion Types:
  - カメラ移動（ズーム、パン、チルト）
  - 被写体の動き
  - 背景のアニメーション
```

### 3. アバター動画 (Avatar Video)

```yaml
Mode: avatar-video
Input: スクリプト + アバター選択
Output: リップシンク動画
Tools: HeyGen, Synthesia

Features:
  - 140+言語対応
  - カスタムアバター作成
  - ブランドボイス設定
  - 自動字幕生成

Use Cases:
  - 解説動画
  - 商品紹介
  - オンラインコース
  - ニュース形式コンテンツ
```

---

## 動画生成フロー

### フェーズ1: 企画

```
入力: コンテンツアイデア
    ↓
1. ターゲットプラットフォーム決定
2. 動画スタイル選択
3. 長さ・構成決定
4. スクリプト作成
    ↓
出力: 動画企画書
```

### フェーズ2: 素材生成

```
入力: 動画企画書
    ↓
1. 画像生成（必要に応じて）
2. 動画クリップ生成
3. 音声/BGM生成
4. 字幕テキスト準備
    ↓
出力: 動画素材セット
```

### フェーズ3: 編集・合成

```
入力: 動画素材セット
    ↓
1. クリップ結合
2. トランジション追加
3. 音声同期
4. 字幕追加
5. カラーグレーディング
    ↓
出力: 完成動画
```

---

## プロンプトテンプレート

### YouTube Shorts / TikTok

```
[Hook - 0-3秒]
プロンプト: "Dramatic zoom into [subject],
            high contrast, attention-grabbing"

[Content - 3-50秒]
プロンプト: "[Main content description],
            smooth camera movement,
            engaging visuals"

[CTA - 50-60秒]
プロンプト: "Text overlay animation,
            subscribe button effect,
            loop-friendly ending"
```

### 商品紹介

```
[製品ショット]
"Product photography style, [product] on minimal background,
 soft studio lighting, slow 360 rotation,
 reflective surface, luxury feel"

[使用シーン]
"Person using [product] in [setting],
 natural lighting, lifestyle photography style,
 warm color grading, satisfied expression"
```

### 解説動画

```
[イントロ]
"Clean modern intro animation,
 logo reveal, professional business style,
 smooth transitions, corporate blue theme"

[本編]
"Animated infographic showing [concept],
 2D motion graphics, clear visual hierarchy,
 icons and text labels, educational style"
```

---

## 自動化ワークフロー

### 日次コンテンツ生成

```yaml
Daily Workflow:
  1. トレンド分析:
     - TikTok/YouTube Shortsのトレンド確認
     - 人気フォーマットの特定

  2. コンテンツ企画:
     - 3-5個のアイデア生成
     - 最適なものを選択

  3. 動画生成:
     - プロンプト作成
     - AI生成実行
     - 品質チェック

  4. 投稿準備:
     - サムネイル作成
     - 説明文・ハッシュタグ
     - スケジュール設定

  5. 投稿:
     - 最適時間に自動投稿
     - エンゲージメント監視
```

### バッチ生成

```yaml
Batch Generation:
  trigger: 週1回（日曜夜）
  output: 7-14本の動画

  process:
    1. 週間トレンド分析
    2. コンテンツカレンダー作成
    3. 一括プロンプト生成
    4. API経由で順次生成
    5. 品質チェック・修正
    6. 週間スケジュール設定
```

---

## API統合

### Pika API

```javascript
// Pika API (非公式/ラッパー使用)
const pikaGenerate = async (prompt, options) => {
  return await fetch('https://api.pika.art/v1/generate', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${PIKA_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      prompt,
      negative_prompt: options.negative || '',
      aspect_ratio: options.aspectRatio || '9:16',
      motion_strength: options.motion || 'medium',
      style: options.style || 'realistic'
    })
  });
};
```

### Runway API

```javascript
// Runway Gen-3 API
const runwayGenerate = async (prompt, options) => {
  const runway = new RunwayML({ apiKey: RUNWAY_API_KEY });

  const task = await runway.textToVideo.create({
    model: 'gen3a_turbo',
    promptText: prompt,
    duration: options.duration || 5,
    ratio: options.ratio || '9:16',
    seed: options.seed || null
  });

  // ポーリングで結果取得
  return await runway.tasks.retrieve(task.id);
};
```

### HeyGen API

```javascript
// HeyGen Avatar API
const heygenGenerate = async (script, avatarId) => {
  return await fetch('https://api.heygen.com/v2/video/generate', {
    method: 'POST',
    headers: {
      'X-Api-Key': HEYGEN_API_KEY,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      video_inputs: [{
        character: { type: 'avatar', avatar_id: avatarId },
        voice: { type: 'text', input_text: script },
        background: { type: 'color', value: '#FFFFFF' }
      }],
      dimension: { width: 1080, height: 1920 }
    })
  });
};
```

---

## 品質管理

### 品質チェックリスト

```
動画品質:
├── [ ] 解像度が適切（1080p以上）
├── [ ] フレームレートが安定（30fps+）
├── [ ] アーティファクトなし
├── [ ] 色調が一貫している
└── [ ] 動きが自然

コンテンツ品質:
├── [ ] フックが強い（最初3秒）
├── [ ] メッセージが明確
├── [ ] CTAが含まれている
├── [ ] プラットフォームガイドライン準拠
└── [ ] 著作権問題なし
```

### 再生成条件

```
自動再生成トリガー:
├── アーティファクト検出
├── 顔/手の異常
├── 動きが不自然
├── 解像度不足
└── 生成失敗
```

---

## コスト管理

### 月間コスト見積もり

```
低頻度（週5本）:
├── Pika: ~$8/月
├── 合計: ~$8/月

中頻度（日1本）:
├── Pika: $15/月
├── Runway: $12/月
├── 合計: ~$27/月

高頻度（日3本+）:
├── Runway Pro: $35/月
├── HeyGen: $24/月
├── 合計: ~$59/月
```

### コスト最適化

```
節約戦略:
├── 無料枠の活用（各ツール初月）
├── オフピーク生成（クレジット節約）
├── テンプレート再利用
├── 失敗時の即時停止
└── 月間上限設定
```

---

## 出力先

```
/mnt/e/SNS-Output/
├── YouTube-Shorts/
│   └── YYYY-MM-DD-[title].mp4
├── TikTok/
│   └── YYYY-MM-DD-[title].mp4
├── Instagram-Reels/
│   └── YYYY-MM-DD-[title].mp4
└── Thumbnails/
    └── YYYY-MM-DD-[title].png
```

---

## 連携スキル

| スキル | 連携内容 |
|--------|----------|
| `youtube-automation` | チャンネル運営、投稿自動化 |
| `sns-tiktok` | TikTok投稿最適化 |
| `sns-instagram` | Reels投稿最適化 |
| `nano-banana` | サムネイル画像生成 |
| `affiliate-marketing` | 商品紹介動画 |

---

## 使用例

```
「TikTok用の動画を作って」
→ トレンド分析 → プロンプト生成 → Pika生成 → 品質チェック → 保存

「商品紹介動画を作って」
→ 商品画像取得 → アニメーション化 → 説明追加 → 保存

「解説動画を作って」
→ スクリプト作成 → HeyGenアバター → 字幕追加 → 保存
```

---

## 更新履歴

```
[2026-02-02] 初期作成
```

---

*動画生成はクレジット消費に注意。大量生成前に監督者に確認してください。*
