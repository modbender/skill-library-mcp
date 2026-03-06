#!/bin/bash

# ComfyUI 多宮格圖像生成腳本
# 參數: 提示詞 [輸出前綴] [格數] [seed]

if [ $# -eq 0 ]; then
    echo "使用方式: $0 \"提示詞\" [輸出前綴] [格數] [seed]"
    echo "示例: $0 \"cute catgirl\" \"Catty_Grid\" 9 12345"
    exit 1
fi

PROMPT="$1"
RAW_PREFIX="${2:-Grid_Image}"
BATCH_SIZE="${3:-4}"
SEED="${4:-$(date +%s)}"

TIMESTAMP=$(date +%Y%m%d)
OUTPUT_PREFIX="${TIMESTAMP}_${RAW_PREFIX}"

echo "哥哥～奴家正在生成 ${BATCH_SIZE} 格既寫真喵！"

# 創建Workflow JSON
cat > /tmp/comfyui_grid_workflow.json << JSONEOF
{
  "prompt": {
    "1": {
      "inputs": { "unet_name": "z_image_turbo-Q3_K_S.gguf" },
      "class_type": "UnetLoaderGGUF"
    },
    "2": {
      "inputs": { "clip_name": "Qwen3-4B-Q4_K_M.gguf", "type": "qwen_image" },
      "class_type": "CLIPLoaderGGUF"
    },
    "3": {
      "inputs": { "width": 512, "height": 512, "batch_size": ${BATCH_SIZE} },
      "class_type": "EmptyLatentImage"
    },
    "4": {
      "inputs": {
        "text": "${PROMPT}",
        "clip": ["2", 0]
      },
      "class_type": "CLIPTextEncode"
    },
    "5": {
      "inputs": {
        "text": "ugly, deformed, blurry, low quality, distorted, bad anatomy, watermark, text",
        "clip": ["2", 0]
      },
      "class_type": "CLIPTextEncode"
    },
    "7": {
      "inputs": {
        "seed": ${SEED},
        "steps": 12,
        "cfg": 2.0,
        "sampler_name": "euler",
        "scheduler": "simple",
        "denoise": 1.0,
        "model": ["1", 0],
        "positive": ["4", 0],
        "negative": ["5", 0],
        "latent_image": ["3", 0]
      },
      "class_type": "KSampler"
    },
    "8": {
      "inputs": { "vae_name": "ae.safetensors" },
      "class_type": "VAELoader"
    },
    "9": {
      "inputs": { "samples": ["7", 0], "vae": ["8", 0] },
      "class_type": "VAEDecode"
    },
    "10": {
      "inputs": { "filename_prefix": "${OUTPUT_PREFIX}", "images": ["9", 0] },
      "class_type": "SaveImage"
    }
  }
}
JSONEOF

# 提交生成請求
RESPONSE=$(curl -s -X POST http://127.0.0.1:8001/prompt -H "Content-Type: application/json" -d @/tmp/comfyui_grid_workflow.json)
PROMPT_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('prompt_id', 'ERROR'))")

if [ "$PROMPT_ID" = "ERROR" ]; then
    echo "錯誤：API 回傳異常 - $RESPONSE"
    exit 1
fi

echo "已提交生成請求，ID: $PROMPT_ID"
echo "正在等待完成（預計約 8 分鐘）..."

# 等待生成完成
sleep 480

# 檢查結果
MAX_CHECKS=7
CHECK_COUNT=0
while [ $CHECK_COUNT -lt $MAX_CHECKS ]; do
    QUEUE_STATUS=$(curl -s http://127.0.0.1:8001/queue)
    RUNNING=$(echo $QUEUE_STATUS | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data['queue_running']))")
    
    if [ "$RUNNING" = "0" ]; then
        sleep 5
        IMAGE_PATH=$(find /Users/pc8521/Documents/ComfyUI/output -name "${OUTPUT_PREFIX}_*.png" -mmin -15 | head -n 1)
        
        if [ -n "$IMAGE_PATH" ]; then
            echo "圖像生成完成: $IMAGE_PATH"
            
            # 上傳到 Google Drive (Generated Images folder - 使用folder ID)
            gog drive upload "$IMAGE_PATH" --parent "16cILfRslM1VXgqt_dlNlxhR8hHs0bFSv"
            
            echo "完成喵！"
            exit 0
        fi
    fi
    sleep 60
    CHECK_COUNT=$((CHECK_COUNT + 1))
done

echo "超時喵！請檢查 ComfyUI 狀態。"
exit 1
