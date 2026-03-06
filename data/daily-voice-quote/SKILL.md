---
name: daily-voice-quote
description: 每日名言語音任務。產生「語音 + 封面圖靜態影片 +（選配）HeyGen 數位人影片」並發送給主人。
metadata:
  {
    "openclaw":
      {
        "emoji": "🎙️",
        "requires":
          {
            "bins": ["sag", "ffmpeg"],
            "env": ["ELEVENLABS_API_KEY"],
            "optionalBins": ["uv", "python3"],
            "optionalEnv": ["GEMINI_API_KEY", "HEYGEN_API_KEY"],
          },
        "primaryEnv": "ELEVENLABS_API_KEY",
        "install":
          [
            {
              "id": "sag-brew",
              "kind": "brew",
              "formula": "steipete/tap/sag",
              "bins": ["sag"],
              "label": "Install sag — ElevenLabs TTS CLI (brew)",
            },
            {
              "id": "ffmpeg-brew",
              "kind": "brew",
              "formula": "ffmpeg",
              "bins": ["ffmpeg"],
              "label": "Install ffmpeg — audio/video processing (brew)",
            },
            {
              "id": "uv-brew",
              "kind": "brew",
              "formula": "uv",
              "bins": ["uv"],
              "label": "Install uv — Python runner for image generation (brew, optional)",
            },
          ],
        "notes": "Required: ELEVENLABS_API_KEY + sag + ffmpeg for voice generation. Optional: GEMINI_API_KEY + uv for cover image generation (nano-banana-pro). Optional: HEYGEN_API_KEY for digital avatar video. Without ElevenLabs, the built-in tts tool can be used as a fallback.",
      },
  }
---

# Daily Voice Quote 每日名言語音

這個 skill 會在每天早上：
1) 用主人的聲音朗讀一則名人名言（語音）
2) 生成封面圖並合成靜態影片
3) （選配）產生 HeyGen 數位人影片

最終產出三件套：**語音、靜態影片、HeyGen 數位人影片**。

---

## 1. 簡介

每天早上自動選一則名人名言，用主人的聲音念出來，並搭配一張美感封面圖與影片版本發送給主人。若你沒有 HeyGen 帳號，也可以只做「語音 + 靜態影片」。

---

## 2. 前置準備 Checklist

### a) 主人的照片（封面圖生成用）
- 需要 **1–3 張高品質照片**（正臉、清楚、光線好）
- 放到 workspace 的 `avatars/` 目錄
- 如果沒有照片：**請主人提供 1–3 張好看的照片！**

### b) ElevenLabs 帳號 + 語音克隆
- 註冊：https://elevenlabs.io
- 取得 API Key 後，存到你的 OpenClaw config 或環境變數 `ELEVENLABS_API_KEY`
- 語音克隆方式：
  - **方法一（官方 UI）**：主人錄 1–3 分鐘語音 → 上傳到 ElevenLabs Voice Lab
  - **方法二（主人傳語音給你）**：主人傳語音訊息 → 你下載後用 API 上傳克隆：
    ```bash
    curl -X POST "https://api.elevenlabs.io/v1/voices/add" \
      -H "xi-api-key: $ELEVENLABS_API_KEY" \
      -F "name=主人的名字" \
      -F "files=@/path/to/voice-sample.mp3" \
      -F "description=Voice clone for daily quotes"
    ```
    API 會回傳 `voice_id`，記下來。
- 記錄到 TOOLS.md：**Voice Name、Voice ID**

#### 檢查 API Key 和語音

```bash
# 1. 確認 API Key 存在
echo $ELEVENLABS_API_KEY  # 應該有值

# 2. 列出所有可用語音
sag voices

# 3. 測試語音生成
sag -v "YOUR_VOICE_NAME" -o /tmp/test.mp3 "早安，這是一個語音測試。"
```

⚠️ `sag` 所有指令都需要 `ELEVENLABS_API_KEY` 環境變數。如果沒有，請先設定。

#### 沒有 ElevenLabs？用內建 tts 替代

如果暫時沒有 ElevenLabs API Key，可以先用 OpenClaw 內建的 `tts` tool：
```
tts({ text: "早安！今天想分享 Steve Jobs 的一句話..." })
```
音色不會是主人的聲音，但流程可以先跑起來。

### c) HeyGen 帳號 + 數位人 Avatar（選配）
- 註冊：https://heygen.com
- 數位人訓練：主人錄一段 **2 分鐘自拍影片** 上傳訓練
- 記錄：**Avatar ID、Voice ID**
- 如果沒有 HeyGen 帳號 → **跳過 Part 3，只做語音 + 靜態影片**

### d) Channel 設定
- 先確認主人常用的通訊軟體
- **LINE**：需要 `CHANNEL_ACCESS_TOKEN` + `USER_ID / GROUP_ID`
- 其他（Telegram / Discord / WhatsApp 等）：使用 `message` tool 或 `tts` tool

#### 📱 LINE 媒體格式要求（重要！）

LINE 對語音和影片的格式有嚴格限制，格式不對會無法在聊天裡直接點開播放！

**語音訊息（audio message）：**
| 項目 | 要求 |
|------|------|
| 格式 | **M4A**（`.m4a`）— AAC 編碼 |
| 來源 | 必須是 **HTTPS 公開 URL**（不接受本地檔案路徑） |
| duration | 必須提供毫秒數（如 `21000` = 21 秒） |
| ❌ 不行 | MP3 直接發送（LINE 不支援 audio type 用 MP3） |
| ✅ 轉換 | `ffmpeg -i input.mp3 -c:a aac -b:a 128k output.m4a -y` |

**影片訊息（video message）：**
| 項目 | 要求 |
|------|------|
| 格式 | **MP4**（`.mp4`）— H.264 視訊 + AAC 音訊 |
| 來源 | 必須是 **HTTPS 公開 URL**（支援 Range requests） |
| previewImageUrl | 必須提供影片預覽圖 URL（JPEG/PNG） |
| ❌ 不行 | ngrok + Python SimpleHTTPServer（不支援 Range requests，LINE 無法播放） |
| ✅ 可行 | ngrok + Node.js static server、HeyGen CDN URL、任何支援 Range requests 的 CDN |

**公開 URL 方案：**
- **最簡單**：把檔案放到支援 Range requests 的靜態檔案伺服器 + ngrok/cloudflare tunnel
- **免設定**：HeyGen 影片直接用 HeyGen CDN URL（自帶）
- **進階**：上傳到 S3/GCS/Cloudflare R2 等雲端儲存

**LINE Push API 範例：**
```bash
# 語音
curl -s -X POST https://api.line.me/v2/bot/message/push \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LINE_CHANNEL_ACCESS_TOKEN" \
  -d '{
    "to": "YOUR_LINE_USER_ID",
    "messages": [{
      "type": "audio",
      "originalContentUrl": "https://your-domain.com/daily-quote.m4a",
      "duration": 21000
    }]
  }'

# 影片
curl -s -X POST https://api.line.me/v2/bot/message/push \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LINE_CHANNEL_ACCESS_TOKEN" \
  -d '{
    "to": "YOUR_LINE_USER_ID",
    "messages": [{
      "type": "video",
      "originalContentUrl": "https://your-domain.com/daily-quote.mp4",
      "previewImageUrl": "https://your-domain.com/daily-quote-preview.jpg"
    }]
  }'
```

### e) Gemini API Key（封面圖生成）
- 取得：https://aistudio.google.com
- 或改用你喜歡的圖片生成 skill（DALL·E / SD / Midjourney 皆可）

---

## 3. 名言選擇規則

- **非節日**：按照 `day_of_year % 20` 取固定清單
- **節日**：選主題與節日呼應的**真實名人名言**
  - ⚠️ 必須是「名人 + 名言」，不是祝賀詞 / 成語 / 諺語
  - 語音稿開頭可加節日問候
- **極端天氣**：僅颱風 / 暴雨 / 暴雪 / 極端高溫才加提醒

> 節日清單與名言清單在 `references/` 目錄內：
> - `references/holidays.md`
> - `references/quotes.md`

---

## 4. 完整執行流程

### Part 1：語音

**流程：**選名言 → 寫語音稿 → `sag` 生成 → `ffmpeg` 轉 m4a → 發送

**語音稿模板（含情緒標籤）：**
```
早安。[short pause]
今天想分享 {AUTHOR} 的一句話：{QUOTE_ZH} [short pause]
{QUOTE_EN} [short pause]
願這句話為你的一天帶來力量。加油！
```

**產生語音（範例）：**
```bash
# 1. 生成 MP3
ELEVENLABS_API_KEY="YOUR_ELEVENLABS_API_KEY" \
  sag -v "YOUR_VOICE_NAME" \
  --speed 0.95 --stability 1.0 --similarity 0.85 \
  -o /tmp/daily-quote.mp3 "${SCRIPT}"

# 2. 轉換為 M4A（LINE 必須！MP3 不能直接在 LINE 聊天裡播放）
ffmpeg -i /tmp/daily-quote.mp3 -c:a aac -b:a 128k /tmp/daily-quote.m4a -y

# 3. 取得音訊長度（LINE audio message 需要 duration 毫秒數）
#    從 ffmpeg 輸出讀取，例如 time=00:00:21.16 → 21160 ms
#    或用 ffprobe：
ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 /tmp/daily-quote.m4a
# → 乘以 1000 得到毫秒數
```

> 📱 **LINE 用戶注意**：語音必須是 **M4A 格式**（AAC 編碼）才能在聊天裡直接點開播放。MP3 不行！詳見上方「LINE 媒體格式要求」。

### Part 2：封面圖靜態影片

> ⚠️ **超重要：`--input-image` 是讓 AI 重新生成新照片，不是去背剪貼！**

**好的 prompt 範例：**
```
Generate a vertical 9:16 portrait of this person wearing a traditional outfit,
standing in a festive scene with soft lantern lights. The person is smiling
confidently. Overlay elegant text: “{QUOTE_ZH} — {AUTHOR}”.
Cinematic lighting, Instagram story style.
```

**壞的 prompt（不要用）：**
```
Paste this person onto a red background...
Cut out the person and place into the scene...
```

**生成封面圖（範例，用 nano-banana-pro skill）：**
```bash
GEMINI_API_KEY="YOUR_GEMINI_API_KEY" \
uv run /opt/homebrew/lib/node_modules/openclaw/skills/nano-banana-pro/scripts/generate_image.py \
  --prompt "YOUR_PROMPT" \
  --input-image "/path/to/avatars/photo.jpg" \
  --filename "/tmp/daily-quote-cover.png" \
  --resolution 2K
```

**合成靜態影片（封面圖 + 語音 = 影片）：**
```bash
# 合成 MP4（H.264 + AAC）— LINE 可直接播放的格式
ffmpeg -loop 1 -i /tmp/daily-quote-cover.png -i /tmp/daily-quote.mp3 \
  -c:v libx264 -tune stillimage -c:a aac -b:a 128k \
  -pix_fmt yuv420p -shortest \
  -vf "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2" \
  /tmp/daily-quote-static.mp4 -y

# 截取預覽圖（LINE video message 必須提供 previewImageUrl）
ffmpeg -i /tmp/daily-quote-static.mp4 -vframes 1 -q:v 2 /tmp/daily-quote-preview.jpg -y
```

> 📱 **LINE 用戶注意**：影片必須是 **MP4 格式**（H.264 視訊 + AAC 音訊），且需要透過支援 Range requests 的 HTTPS URL 提供，LINE 才能在聊天裡直接點開播放。同時必須提供預覽圖 URL。詳見上方「LINE 媒體格式要求」。

### Part 3：HeyGen 數位人影片（選配）

**注意：**傳給 HeyGen 的文稿請移除情緒標籤（如 `[short pause]`）。

```bash
HEYGEN_API_KEY="YOUR_HEYGEN_API_KEY" \
python3 /path/to/heygen/generate_video.py \
  --text "${SCRIPT_PLAIN}" \
  --avatar-id "YOUR_AVATAR_ID" \
  --voice-id "YOUR_HEYGEN_VOICE_ID" \
  --dimension "720x1280" \
  --aspect-ratio "9:16" \
  --output /tmp/daily-quote-heygen.mp4
```

如果沒有 HeyGen 帳號，直接跳過本段即可。

---

## 5. Cron Job 設定範例

### LINE 版
```json
{
  "name": "每日名言語音",
  "schedule": { "kind": "cron", "expr": "0 6 * * *", "tz": "Asia/Taipei" },
  "payload": {
    "kind": "agentTurn",
    "model": "anthropic/claude-sonnet-4",
    "message": "請執行 daily-voice-quote：產生語音 + 靜態影片（選配 HeyGen），並送到 LINE。使用環境變數：YOUR_LINE_CHANNEL_ACCESS_TOKEN / YOUR_LINE_USER_ID / YOUR_AUDIO_PUBLIC_URL。"
  }
}
```

### 非 LINE 版（Telegram / Discord / WhatsApp 等）
```json
{
  "name": "每日名言語音",
  "schedule": { "kind": "cron", "expr": "0 6 * * *", "tz": "Asia/Taipei" },
  "payload": {
    "kind": "agentTurn",
    "model": "anthropic/claude-sonnet-4",
    "message": "請執行 daily-voice-quote：產生語音 + 靜態影片（選配 HeyGen），並用 message/tts 工具送到當前 channel。"
  }
}
```

---

## 6. 常見問題 FAQ

**Q1：沒有主人照片怎麼辦？**
- A：請主人提供 1–3 張清晰照片。沒有照片就無法生成封面圖。

**Q2：沒有 ElevenLabs 怎麼辦？**
- A：可改用內建 `tts` tool 先產生語音，但音色就不是主人的聲音。

**Q3：HeyGen 額度不足怎麼辦？**
- A：先只做語音 + 靜態影片，等額度恢復再補數位人影片。

**Q4：如何更換名言清單？**
- A：直接編輯 `references/quotes.md`，或在腳本中指定 `QUOTES_FILE`。

**Q5：LINE 聊天裡點語音/影片沒反應或無法播放？**
- A：檢查格式！語音必須是 **M4A**（不是 MP3），影片必須是 **MP4**（H.264+AAC）。URL 必須是 HTTPS 且支援 Range requests（Python SimpleHTTPServer 不支援！用 Node.js static server 或 CDN）。

---

## 附：腳本位置

- `scripts/send-daily-quote.sh`：完整 bash 腳本（無硬編碼，全部用環境變數）
- `references/quotes.md`：名言清單
- `references/holidays.md`：節日清單
