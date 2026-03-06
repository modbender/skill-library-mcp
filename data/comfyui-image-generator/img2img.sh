#!/bin/bash

# ComfyUI 圖像生成器腳本 (圖生圖版本)
# 參數: $1: 提示詞, $2: 原始圖片路徑, $3: 輸出前綴, $4: 降噪強度 (0.0-1.0, 預設 0.5)

if [ $# -lt 2 ]; then
    echo "使用方式: $0 \"提示詞\" \"圖片路徑\" [輸出前綴] [降噪強度]"
    exit 1
fi

PROMPT="$1"
IMAGE_PATH="$2"
TIMESTAMP=$(date +%Y%m%d)
RAW_PREFIX="${3:-Img2Img_Generated}"
OUTPUT_PREFIX="${TIMESTAMP}_${RAW_PREFIX}"
DENOISE="${4:-0.5}"
SEED=$(date +%s)

# 獲取圖片檔名
IMAGE_FILENAME=$(basename "$IMAGE_PATH")

# 將圖片複製到 ComfyUI 的 input 目錄
cp "$IMAGE_PATH" "/Users/pc8521/Documents/ComfyUI/input/$IMAGE_FILENAME"

# 創建工作流程JSON (全 GGUF 穩定版 - 圖生圖)
cat > /tmp/comfyui_img2img_workflow.json << EOF
{
  "prompt": {
    "1": {
      "inputs": {
        "unet_name": "z_image_turbo-Q3_K_S.gguf"
      },
      "class_type": "UnetLoaderGGUF"
    },
    "2": {
      "inputs": {
        "clip_name": "Qwen3-4B-Q4_K_M.gguf",
        "type": "qwen_image"
      },
      "class_type": "CLIPLoaderGGUF"
    },
    "3": {
      "inputs": {
        "image": "$IMAGE_FILENAME",
        "upload": "image"
      },
      "class_type": "LoadImage"
    },
    "4": {
      "inputs": {
        "text": "$PROMPT",
        "clip": ["2", 0]
      },
      "class_type": "CLIPTextEncode"
    },
    "5": {
      "inputs": {
        "text": "ugly, deformed, mutated, scary, horror, blurry, low quality",
        "clip": ["2", 0]
      },
      "class_type": "CLIPTextEncode"
    },
    "6": {
      "inputs": {
        "pixels": ["3", 0],
        "vae": ["8", 0]
      },
      "class_type": "VAEEncode"
    },
    "7": {
      "inputs": {
        "seed": $SEED,
        "steps": 10,
        "cfg": 1.5,
        "sampler_name": "euler",
        "scheduler": "simple",
        "denoise": $DENOISE,
        "model": ["1", 0],
        "positive": ["4", 0],
        "negative": ["5", 0],
        "latent_image": ["6", 0]
      },
      "class_type": "KSampler"
    },
    "8": {
      "inputs": {
        "vae_name": "ae.safetensors"
      },
      "class_type": "VAELoader"
    },
    "9": {
      "inputs": {
        "samples": ["7", 0],
        "vae": ["8", 0]
      },
      "class_type": "VAEDecode"
    },
    "10": {
      "inputs": {
        "filename_prefix": "$OUTPUT_PREFIX",
        "images": ["9", 0]
      },
      "class_type": "SaveImage"
    }
  }
}
EOF

echo "提交圖生圖生成請求 (Port 8001)..."
RESPONSE=$(curl -s -X POST http://127.0.0.1:8001/prompt -H "Content-Type: application/json" -d @/tmp/comfyui_img2img_workflow.json)

PROMPT_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('prompt_id', 'ERROR'))")
if [ "$PROMPT_ID" = "ERROR" ]; then
    echo "錯誤：API 回傳異常 - $RESPONSE"
    exit 1
fi

echo "已提交請求，ID: $PROMPT_ID"
MAX_CHECKS=60
CHECK_COUNT=0

while [ $CHECK_COUNT -lt $MAX_CHECKS ]; do
    QUEUE_STATUS=$(curl -s http://127.0.0.1:8001/queue)
    RUNNING=$(echo $QUEUE_STATUS | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data['queue_running']))")
    
    if [ "$RUNNING" = "0" ]; then
        IMAGE_PATH=$(find /Users/pc8521/Documents/ComfyUI/output -name "${OUTPUT_PREFIX}_*.png" -mmin -5 | head -n 1)
        if [ -n "$IMAGE_PATH" ]; then
            echo "圖像生成完成: $IMAGE_PATH"
            mkdir -p /Users/pc8521/.openclaw/media
            SAFE_IMAGE_PATH="/Users/pc8521/.openclaw/media/$(basename "$IMAGE_PATH")"
            cp "$IMAGE_PATH" "$SAFE_IMAGE_PATH"
            openclaw message send --channel telegram --target 7725266861 --message "圖生圖生成完成：$PROMPT" --media "$SAFE_IMAGE_PATH"
            
            # 留出呼吸時間
            sleep 3

            # 上傳到 Google Drive
            python3 -c "
import os
import sys
sys.path.append('/Users/pc8521/clawd')
from tools.drive_tool import get_drive_service, upload_file

def get_or_create_folder(folder_name):
    service = get_drive_service()
    results = service.files().list(q=f\"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'\", fields='files(id, name)').execute()
    items = results.get('files', [])
    if items: return items[0]['id']
    file_metadata = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')

folder_id = get_or_create_folder('Generated Images')
if folder_id:
    upload_file('$IMAGE_PATH', folder_id)
"
            exit 0
        fi
    fi
    sleep 10
    CHECK_COUNT=$((CHECK_COUNT + 1))
done

echo "錯誤：超時"
exit 1
