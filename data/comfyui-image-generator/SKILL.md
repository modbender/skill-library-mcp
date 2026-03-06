---
name: comfyui-image-generator
description: 使用 ComfyUI 進行文生圖（Text-to-Image）圖像生成。當用戶要求生成圖片、創建圖像、畫圖、或使用本地 AI 圖像生成時使用。亦支援多宮格生成（4格、9格、16格等）。
---

# ComfyUI 圖像生成器技能

## 描述
使用 ComfyUI 生成圖像（文生圖）。當用戶要求生成圖片、創建圖像、畫圖、或使用本地 AI 圖像生成時使用。

## 腳本選擇

### 1. generate_image.sh（單張生成）
```bash
bash /Users/pc8521/clawd/skills/comfyui_image_generator/generate_image.sh "你的提示詞" [輸出前綴] [seed]
```

### 2. generate_grid.sh（多宮格生成）⭐
```bash
bash /Users/pc8521/clawd/skills/comfyui_image_generator/generate_grid.sh "你的提示詞" [輸出前綴] [格數] [seed]
```

#### 參數說明
- 第1個參數：提示詞 (必填)
- 第2個參數：輸出檔名前綴 (可選，預設 "Grid_Image")
- 第3個參數：格數 (可選，預設 4，最大支援 16)
- 第4個參數：Seed 值 (可選，預設當前時間戳)

#### 示例
```bash
# 生成 4 格寫真
bash /Users/pc8521/clawd/skills/comfyui_image_generator/generate_grid.sh "cute catgirl with white hoodie" "Catty_Grid" 4

# 生成 9 格寫真
bash /Users/pc8521/clawd/skills/comfyui_image_generator/generate_grid.sh "beautiful woman, multiple poses" "9Grid" 9

# 生成 16 格
bash /Users/pc8521/clawd/skills/comfyui_image_generator/generate_grid.sh "anime character" "16Grid" 16
```

## 預設參數
- **解析度**: 512x512（多宮格建議使用，速度快）
- **採樣率**: 12步
- **CFG**: 2.0
- **Sampler**: euler
- **Model**: z-image-turbo (Z-Q3 + Qwen3-4B)

## 工作流程 (Node Structure)
如需手動調用 API，請參考 `generate_image.sh` 內的 JSON 結構：
- Node 1: UnetLoaderGGUF (z_image_turbo-Q3_K_S.gguf)
- Node 2: CLIPLoaderGGUF (Qwen3-4B-Q4_K_M.gguf)
- Node 3: EmptyLatentImage (1024x1024)
- Node 4: CLIPTextEncode (positive prompt)
- Node 5: CLIPTextEncode (negative prompt)
- Node 6: VAEDecode
- Node 7: KSampler
- Node 8: VAELoader (ae.safetensors)
- Node 9: SaveImage

## 重要通訊規則
- **Timeout 設置**: 使用 sub-agent 生成圖片時，請設置 `timeoutSeconds: 900` (15分鐘)，以確保有足夠時間完成生成和上傳。
- **絕對禁止合併**: 嚴禁在同一個回覆中同時包含對話與執行指令。必須先發送對話，再獨立執行。
- **靜默執行**: 所有進度導向至日誌檔。
- **呼吸時間**: 發送媒體後 sleep 3 秒。
- **等待時間**: 生成需要約 8 分鐘，請耐心等待腳本完成。

## 輸出位置
- 圖片會保存至: `/Users/pc8521/Documents/ComfyUI/output/`
- 腳本會自動上傳到 Google Drive 的 "Generated Images" 資料夾
