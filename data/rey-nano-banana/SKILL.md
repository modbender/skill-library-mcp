---
name: rey-nano-banana
description: Generate images using Nano Banana Pro (Gemini). Supports Japanese text rendering, multiple styles, and platform-optimized outputs.
---

# Nano Banana Pro 画像生成スキル

Gemini 3 Pro Image（Nano Banana Pro）を使った画像生成スキル。日本語テキストのレンダリングに対応。

## 環境設定

### 必要な環境変数
```
GOOGLE_AI_API_KEY: Google AI Studio APIキー（必須）
```

### APIキー取得方法
```
1. Google AI Studio (https://aistudio.google.com/) にアクセス
2. APIキーを作成
3. Cloudflare Workers の環境変数に設定
```

---

## 基本使用方法

### 画像生成コマンド
```bash
~/.claude/skills/nano-banana-pro/generate.py \
  --prompt "プロンプト" \
  --output "/mnt/e/SNS-Output/Images/output.png" \
  --aspect "16:9" \
  --resolution "2K"
```

### パラメータ
| パラメータ | 説明 | デフォルト | オプション |
|-----------|------|-----------|-----------|
| --prompt | 画像生成プロンプト | 必須 | - |
| --output | 出力ファイルパス | ./output.png | - |
| --aspect | アスペクト比 | 1:1 | 16:9, 1:1, 9:16 |
| --resolution | 解像度 | 2K | 1K, 2K, 4K |

---

## プロンプト設計

### 5要素フレームワーク
```
効果的なプロンプトの構成:
├── Subject（主題）: 何を描くか
├── Composition（構図）: どう配置するか
├── Action（動作）: 何をしているか
├── Location（場所）: 背景・環境
└── Style（スタイル）: 絵のタッチ
```

### プロンプト例
```
悪い例（キーワード羅列）:
"modern, minimalist, professional, blue, orange"

良い例（シーン描写）:
"A clean minimalist illustration with modern professional style.
The scene uses warm orange and cool blue color palette.
White background with soft gradient shadows."
```

---

## 日本語テキスト生成（重要）

### 成功のコツ
```
✅ 必須パターン:
"The Japanese text 「テキスト」appears at the bottom
 in white bold Gothic font with dark semi-transparent banner."

❌ 失敗パターン:
"Display the text '成功者の朝習慣' in bold font."
"clean typography space" (テキストなし)
```

### ポイント
- 「」（鉤括弧）で囲む
- "The Japanese text 「xxx」appears..." 形式
- フォント、色、位置、サイズを明示的に指定
- 短いフレーズ（10文字以下推奨）

---

## スタイル別テンプレート

### 1. 水彩イラスト（最も安定）
```
"A cozy [シーン描写]. Hand-drawn illustration style with soft watercolor textures.
Warm [色1] and [色2] tones. Slightly imperfect organic lines, like a skilled illustrator's sketch.
Not too polished, with visible brush strokes.
The Japanese text 「[テキスト]」appears at the bottom
in a casual handwritten-style white font with dark semi-transparent banner.
1280x720 pixels."
```

### 2. アニメ/Kawaii風
```
"Cute anime-style [キャラクター描写], [表情], soft pastel [色] gradient background.
Kawaii Japanese illustration style with sparkles and hearts.
The Japanese text 「[テキスト]」appears at the bottom
in cute rounded white font with [色] semi-transparent banner.
1280x720 pixels."
```

### 3. サイバーパンク/テック風
```
"Futuristic cyberpunk scene, [描写] with neon [色] accents.
Dark background with glowing circuit patterns and holographic elements.
The Japanese text 「[テキスト]」appears in bold futuristic font
with glowing neon effect.
1280x720 pixels."
```

### 4. ミニマル/北欧風
```
"Minimalist Scandinavian design, single line art of [シーン描写],
very simple clean lines on soft beige background.
Lots of white space, calming zen aesthetic.
The Japanese text 「[テキスト]」appears in thin elegant black font
at the bottom center.
1280x720 pixels."
```

### 5. レトロ/Synthwave風
```
"Retro 80s style illustration, bold geometric shapes, neon pink and electric blue colors,
vintage computer aesthetic. Synthwave vibes.
The Japanese text 「[テキスト]」appears in bold retro font
with glowing neon effect at the bottom.
1280x720 pixels."
```

---

## プラットフォーム別最適化

### サイズガイド
| プラットフォーム | アスペクト比 | 解像度 |
|----------------|-------------|--------|
| Note (サムネイル) | 16:9 | 1280x720 |
| X (Twitter) | 16:9 / 1:1 | 1200x675 / 1200x1200 |
| Threads | 1:1 | 1080x1080 |
| Instagram Feed | 1:1 / 4:5 | 1080x1080 / 1080x1350 |
| Instagram Stories | 9:16 | 1080x1920 |
| YouTube サムネイル | 16:9 | 1280x720 (4K推奨) |
| ココナラ | 1:1 | 1280x1280 |

### 出力先ディレクトリ
```
/mnt/e/SNS-Output/
├── Images/
│   ├── Note/
│   ├── YouTube/
│   ├── X/
│   ├── Threads/
│   ├── Instagram/
│   └── Coconala/
```

---

## ハイインパクト画像（YouTubeサムネイル向け）

### 5要素
```
1. アニメキャラ: 表情豊かな顔
2. ネオン/グロー: 光る効果、稲妻
3. 大胆なテキスト: 縁取り、グラデーション
4. 高コントラスト: ビビッドカラー
5. 動的構図: 斜め、アクション
```

### 驚き顔テンプレート
```
"Anime girl with shocked expression, wide open sparkling eyes and open mouth,
long flowing [髪色] hair with dynamic movement.
Vibrant neon [色1] and [色2] gradient background with electric lightning effects.
Sparkles and energy particles floating around.
The Japanese text 「[テキスト]」appears HUGE and TILTED at 15 degree angle,
in massive bold white font with thick black outline and bright [色] glow effect.
Cyberpunk anime style, high contrast, eye-catching.
1280x720 pixels."
```

---

## シュルレアリスム/アート系

### テキストなし画像
```
用途:
├── 世界観・雰囲気重視
├── 哲学的・瞑想的なコンセプト
├── アート作品
└── 技術的ビジュアル（分解図、X線等）
```

### 不可能建築（エッシャー風）
```
"Surrealist impossible architecture in the style of M.C. Escher.
A girl walking on an infinite staircase that loops back onto itself, defying gravity.
Multiple gravity directions in the same scene.
Dreamlike atmosphere with soft purple and gold twilight.
NO TEXT. Hyperdetailed surrealist digital art.
1280x720 pixels."
```

### ダブルイメージ（隠し絵）
```
"Double image optical illusion art. When viewed from far, looks like a woman's face.
When viewed closely, reveals a detailed landscape - hair becomes waterfall,
eye becomes lake, nose becomes mountain ridge.
Warm sunset colors. NO TEXT.
1280x720 pixels."
```

---

## AI感を減らすテクニック

### 手描き質感キーワード
```
効果的なキーワード:
├── hand-drawn
├── sketch
├── watercolor textures
├── visible brush strokes
├── slightly imperfect
├── organic shapes
└── like someone's notes
```

### スタイル別効果
| 用途 | スタイル指定 |
|------|-------------|
| サムネイル | hand-drawn + watercolor textures |
| 概念図 | doodle style + pencil textures |
| ステップ図 | notebook sketch + colored pencil |
| プロフィール | watercolor + magazine illustration |

---

## エラーハンドリング

### よくあるエラー
```
対処法:
├── APIキー未設定 → 環境変数を確認
├── レート制限 → 少し待ってリトライ
├── 生成失敗 → プロンプトを調整
├── 日本語が乱れる → フォント指定を明確に
└── サイズが違う → aspect パラメータを確認
```

### リトライ戦略
```
1回目失敗 → 5秒待機 → リトライ
2回目失敗 → プロンプト調整 → リトライ
3回目失敗 → エラー報告
```

---

## セキュリティ連携

### 画像内容チェック
```
生成前に確認:
├── 不適切な内容が含まれていないか
├── 著作権侵害がないか
├── 商標侵害がないか
└── 有名人の肖像がないか
```

### APIキー保護
```
絶対にしないこと:
├── APIキーをログに出力
├── APIキーをコードにハードコード
└── APIキーを公開リポジトリにコミット
```

---

## 商品画像生成（product-image-generator 連携）

### ココナラ用サムネイル
```bash
# IT・プログラミング系
~/.claude/skills/nano-banana-pro/generate.py \
  --prompt "Professional tech service thumbnail, dark navy blue gradient background,
minimalist code icon with cyan accent, corporate professional look.
The Japanese text 「GAS自動化」appears at the bottom in bold white font.
1280x1280 pixels." \
  --output "/mnt/e/SNS-Output/Images/Coconala/gas-thumbnail.png" \
  --aspect "1:1" \
  --resolution "2K"
```

### カテゴリ別デザイン
```
IT系: ダークブルー + シアン、プロフェッショナル
ライティング系: ベージュ + オレンジ、親しみやすい
デザイン系: カラフル、クリエイティブ
ビジネス系: 白 + ネイビー、信頼感
```

---

## 使用例

### Note サムネイル
```bash
~/.claude/skills/nano-banana-pro/generate.py \
  --prompt "A cozy morning scene with a person meditating at sunrise.
Hand-drawn illustration style with soft watercolor textures.
Warm orange and soft purple tones.
The Japanese text 「成功者の朝習慣」appears at the bottom
in a casual handwritten-style white font with dark semi-transparent banner.
1280x720 pixels." \
  --output "/mnt/e/SNS-Output/Images/Note/2026-02-01-朝習慣.png" \
  --aspect "16:9" \
  --resolution "2K"
```

### YouTube サムネイル（ハイインパクト）
```bash
~/.claude/skills/nano-banana-pro/generate.py \
  --prompt "Anime girl with shocked expression, wide open sparkling eyes,
long flowing pink hair with dynamic movement.
Vibrant neon pink and electric blue gradient background with lightning effects.
The Japanese text 「AIが全部変わった」appears HUGE at the bottom
in massive bold white font with thick black outline and pink glow.
Cyberpunk anime style, high contrast.
1280x720 pixels." \
  --output "/mnt/e/SNS-Output/Images/YouTube/2026-02-01-AI-shock.png" \
  --aspect "16:9" \
  --resolution "4K"
```
