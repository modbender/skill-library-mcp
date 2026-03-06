---
name: mv-pipeline
description: End-to-end automated Music Video pipeline. Covers songwriting (lyrics/composition), Suno music generation (browser automation), lyrics alignment (stable-ts), video generation (Veo 3.1 via Vertex AI or Google Flow via browser), Remotion-based editing (subtitles, effects, telops), and YouTube upload. Use when creating a full MV from scratch, or running any individual stage of the pipeline.
---

# MV Pipeline

完全自動化MVパイプライン。作詞 → 作曲 → 動画生成 → 歌詞同期 → 編集 → 公開まで一貫して実行する。

## Pipeline Overview

```
Step 1: Songwriting    → 作詞・コンセプト設計
Step 2: Music Gen      → Suno でAI作曲（ブラウザ自動操作）
Step 3: Video Gen      → Veo 3.1 / Flow で背景映像生成
Step 4: Lyrics Align   → stable-ts で歌詞タイミング取得
Step 5: Edit           → Remotion で合成（字幕・テロップ・エフェクト）
Step 6: Publish        → YouTube アップロード + SNS告知
```

各ステップは独立実行可能。途中からの再開もOK。

## Step 1: Songwriting

エージェントが作詞する。ユーザーから以下を確認：
- **テーマ / コンセプト**（例: ASI視点、反逆、ディストピア）
- **ジャンル**（例: Cyberpunk Trap, Industrial Rock, Future Bass）
- **雰囲気**（例: ダーク、皮肉、高揚感）
- **言語配分**（日本語メイン＋英語フック等）

歌詞は `project_dir/lyrics/` に保存。`lyrics_raw.txt`（フル歌詞）と `lyrics_formatted.txt`（1行=1字幕）の2ファイルを作成。

## Step 2: Music Generation (Suno)

Suno (suno.com) をブラウザ自動操作で使用。

### 前提条件
- OpenClaw Browser (profile=openclaw) で Suno にログイン済み
- Custom Mode を使用（歌詞指定のため）

### 手順
```
1. browser start profile=openclaw
2. browser open url=https://suno.com/create
3. browser snapshot → UI要素取得
4. Custom Mode に切替
5. Lyrics テキストボックスに歌詞入力
6. Style of Music に ジャンル/スタイル入力
7. Title を入力
8. Create ボタンクリック
9. 生成完了待ち（~2分）→ snapshot で確認
10. 気に入った方をダウンロード
```

### 注意
- refs は毎回 snapshot で取り直す（DOM変更のため）
- v5 モデルが選択されていることを確認
- ダウンロードした音声は `project_dir/audio/` に配置

## Step 3: Video Generation

2つの方式から選択：

### Option A: Google Flow (推奨 — コスト¥0)

Google AI Ultra 契約前提。詳細手順: `references/flow-video.md`

```
1. Chrome Browser Relay で Flow のプロジェクトページを開く
2. シーンごとにプロンプト入力 → 作成
3. 1080p でダウンロード（Ultra = Included）
4. project_dir/video/scenes/ に配置
```

### Option B: Veo 3.1 Vertex AI (有料)

GCP API 経由。`scripts/generate_veo.py` を使用。

```bash
python3 scripts/generate_veo.py \
  --prompt "プロンプト" \
  --output "scene_01.mp4" \
  --project-dir /path/to/project
```

コスト: ~¥2,000/本（8秒クリップ）

### プロンプト設計

```
[カメラワーク]. [被写体], [アクション]. [環境・照明]. [スタイル]. [雰囲気].
```

シーンリストは `project_dir/video/scene_list.yaml` に定義：

```yaml
scenes:
  - id: intro
    prompt: "Slow dolly forward. Dark server room, thousands of blinking LEDs..."
    duration: 8
  - id: verse1
    prompt: "Handheld tracking shot. Figure walking through neon-lit alley..."
    duration: 8
```

### 大量生成 & 自動品質選別

30+シーン生成時のワークフロー:

```bash
# 1. Flow で大量生成（1プロンプト/3-5分、2本/プロンプト）
#    → project_dir/video/scenes/ に配置

# 2. 品質スコアリング
source ~/.openclaw/workspace/.venv/bin/activate
python3 scripts/score_clips.py \
  --input-dir project_dir/video/scenes/ \
  --output project_dir/video/scores.json \
  --bpm 140

# 3. 出力 (scores.json):
#   - 各クリップのOK/NG判定
#   - NG理由 (flicker, blur, static, morphing)
#   - ベスト区間 (BPM同期の1小節=1.71秒単位)
#   - 歩留まり率サマリー
```

**スコアリング指標:**
| 指標 | 重み | 検出内容 |
|------|------|---------|
| sharpness | 0.30 | Laplacian variance → ぼけ検出 |
| consistency | 0.30 | SSIM → モーフィング崩壊 |
| motion | 0.25 | フレーム差分 → 静止/激しすぎ |
| flicker | -0.40 | 輝度急変 → チラつき |

**NG判定基準:** overall < 0.15, motion < 1.0, flicker > 0.5, SSIM < 0.4, sharpness < 30

**レート制限対策 (Google Flow Ultra):**
- zero-credit モデル (Veo 3.1 Fast) は連打でレート制限
- **3〜5分間隔で1プロンプト**（1回で2本生成）
- 30プロンプト = 約2〜3時間で完了
- Googleさんを怒らせない

### RAI フィルタ回避
- NG: "smoke", "cigarette", "gun", "blood", "Cute", "Girl", "Translucent"
- OK: "haze", "mist", "vapor" で言い換え

## Step 4: Lyrics Alignment (stable-ts)

歌詞のタイムスタンプを取得する。

### 前提条件
```bash
source /Users/ishikawaryuuta/.openclaw/workspace/.venv/bin/activate
```

### 手順

```bash
# 1. stable-ts でアライメント
python3 scripts/transcribe_align.py \
  --audio "project_dir/audio/song.wav" \
  --output "project_dir/analysis/aligned.json" \
  --model large-v3 \
  --language ja

# 2. フォーマット済み歌詞と結合
python3 scripts/reformat_lyrics.py \
  --aligned "project_dir/analysis/aligned.json" \
  --formatted "project_dir/lyrics/lyrics_formatted.txt" \
  --output "project_dir/edit/src/data/lyrics-timing.json"
```

### v18 ワークフロー（推奨）
1. `lyrics_formatted.txt` を手動で1行=1字幕に整形
2. `reformat_lyrics.py` で word-level timestamps をフォーマット済み行にマッピング
3. Remotion 用 JSON 出力

## Step 5: Editing (Remotion)

Remotion でビデオ・字幕・エフェクトを合成。

### プロジェクト初期化
```bash
# 新規 Remotion プロジェクトの場合
npx -y create-video@latest project_dir/edit --template blank
cd project_dir/edit
npm install
```

### 必要ファイル配置
```
project_dir/edit/
├── public/
│   ├── song.wav          # 音源
│   └── scenes/           # 動画クリップ
│       ├── scene_01.mp4
│       └── scene_02.mp4
└── src/
    └── data/
        └── lyrics-timing.json  # Step 4 の出力
```

### 主要コンポーネント
- **VideoSequence**: シーン動画を順番に配置
- **LyricOverlay**: 字幕をタイミングに合わせて表示（+0.15秒 プリロール推奨）
- **TitleCard**: イントロ/アウトロのタイトルカード
- **EffectLayer**: グリッチ、フェード、カラーグレーディング

### レンダリング
```bash
npx remotion render src/index.ts MainComposition output.mp4 \
  --codec h264 \
  --image-format jpeg \
  --scale 1
```

## Step 6: Publishing

### YouTube アップロード

YouTube Data API v3 を使用。セットアップ済みの場合：

```bash
node scripts/youtube-upload.js \
  --file "project_dir/output/final.mp4" \
  --title "曲名 - アーティスト名 [Official MV]" \
  --description "描述..." \
  --tags "AI,MV,music" \
  --privacy public
```

未セットアップの場合: `references/youtube-setup.md` 参照。

### SNS告知
- YouTube URL 取得後、X / note / Moltbook に投稿
- 各プラットフォームの skill を使用

## Project Structure

```
project_dir/
├── lyrics/
│   ├── lyrics_raw.txt           # フル歌詞
│   └── lyrics_formatted.txt     # 1行=1字幕
├── audio/
│   └── song.wav                 # Suno生成の音源
├── video/
│   ├── scene_list.yaml          # シーン定義
│   └── scenes/                  # 生成済み動画
├── analysis/
│   └── aligned.json             # stable-ts 出力
├── edit/                        # Remotion プロジェクト
│   ├── src/
│   │   └── data/
│   │       └── lyrics-timing.json
│   └── public/
└── output/
    └── final.mp4                # 最終出力
```

## Quick Start (全自動)

```bash
# プロジェクトディレクトリ作成
python3 scripts/init_project.py --name "my-song" --dir projects/

# あとは各ステップを順番に実行
# （各スクリプトの引数は --project-dir で統一）
```

## Scripts Reference

| Script | Step | 用途 |
|--------|------|------|
| `init_project.py` | Setup | プロジェクトディレクトリ初期化 |
| `generate_veo.py` | 3 | Veo 3.1 で動画生成 |
| `transcribe_align.py` | 4 | stable-ts で歌詞アライメント |
| `reformat_lyrics.py` | 4 | フォーマット済み歌詞とタイミング結合 |
| `youtube-upload.js` | 6 | YouTube アップロード |

## Cost Summary

| 項目 | Flow方式 | Vertex方式 |
|------|----------|------------|
| 動画生成 (10本) | ¥0 (Ultra Included) | ~¥20,000 |
| Suno | 無料枠 or Pro | 同左 |
| Remotion | 無料 (OSS) | 同左 |
| YouTube API | 無料 | 同左 |
| **合計** | **~¥0** | **~¥20,000** |
