#!/bin/bash

# ComfyUI 圖像生成器腳本 (還原穩定版本)
# 參數: 解析度 512x512, 採樣率 9步, CFG 1.5, 全 GGUF 配置

if [ $# -eq 0 ]; then
    echo "請提供提示詞作為參數"
    echo "使用方式: $0 \"您的提示詞\""
    exit 1
fi

PROMPT="$1"
TIMESTAMP=$(date +%Y%m%d)
# 優先使用傳入的第二參數，若無則使用 "Generated_Image"，最後統一加上日期前綴
RAW_PREFIX="${2:-Generated_Image}"
OUTPUT_PREFIX="${TIMESTAMP}_${RAW_PREFIX}"
SEED=${3:-$(date +%s)}

# 創建工作流程JSON (全 GGUF 穩定版)
cat > /tmp/comfyui_workflow.json << EOF
{
  "prompt": {
    "1": {
      "inputs": {
        "unet_name": "z_image_turbo-Q3_K_S.gguf"
      },
      "class_type": "UnetLoaderGGUF",
      "_meta": {
        "title": "Unet Loader (GGUF)"
      }
    },
    "2": {
      "inputs": {
        "clip_name": "Qwen3-4B-Q4_K_M.gguf",
        "type": "qwen_image"
      },
      "class_type": "CLIPLoaderGGUF",
      "_meta": {
        "title": "CLIPLoader (GGUF)"
      }
    },
    "3": {
      "inputs": {
        "width": 1024,
        "height": 1024,
        "batch_size": 1
      },
      "class_type": "EmptyLatentImage",
      "_meta": {
        "title": "Empty Latent Image"
      }
    },
    "4": {
      "inputs": {
        "text": "$PROMPT",
        "clip": [
          "2",
          0
        ]
      },
      "class_type": "CLIPTextEncode",
      "_meta": {
        "title": "CLIP Text Encode (Prompt)"
      }
    },
    "5": {
      "inputs": {
        "text": "ugly, deformed, mutated, scary, horror, inappropriate, sexual, nude, blurry, low quality",
        "clip": [
          "2",
          0
        ]
      },
      "class_type": "CLIPTextEncode",
      "_meta": {
        "title": "CLIP Text Encode (Negative)"
      }
    },
    "6": {
      "inputs": {
        "samples": [
          "7",
          0
        ],
        "vae": [
          "8",
          0
        ]
      },
      "class_type": "VAEDecode",
      "_meta": {
        "title": "VAE Decode"
      }
    },
    "7": {
      "inputs": {
        "seed": $SEED,
        "steps": 9,
        "cfg": 1.5,
        "sampler_name": "euler",
        "scheduler": "simple",
        "denoise": 1.0,
        "model": [
          "1",
          0
        ],
        "positive": [
          "4",
          0
        ],
        "negative": [
          "5",
          0
        ],
        "latent_image": [
          "3",
          0
        ]
      },
      "class_type": "KSampler",
      "_meta": {
        "title": "KSampler"
      }
    },
    "8": {
      "inputs": {
        "vae_name": "ae.safetensors"
      },
      "class_type": "VAELoader",
      "_meta": {
        "title": "Load VAE"
      }
    },
    "9": {
      "inputs": {
        "filename_prefix": "$OUTPUT_PREFIX",
        "images": [
          "6",
          0
        ]
      },
      "class_type": "SaveImage",
      "_meta": {
        "title": "Save Image"
      }
    }
  }
}
EOF

# 創建靜默執行日誌
LOG_FILE="/tmp/comfyui_gen_$(date +%s).log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "哥哥～奴家正在後台啟動文生圖任務喵！"

# 提交生成請求 (使用 Port 8001)
RESPONSE=$(curl -s -X POST http://127.0.0.1:8001/prompt -H "Content-Type: application/json" -d @/tmp/comfyui_workflow.json)

if [ $? -ne 0 ]; then
    echo "錯誤：無法提交生成請求"
    exit 1
fi

PROMPT_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('prompt_id', 'ERROR'))")

if [ "$PROMPT_ID" = "ERROR" ]; then
    echo "錯誤：API 回傳異常 - $RESPONSE"
    exit 1
fi

echo "已提交生成請求，ID: $PROMPT_ID"
echo "正在進入等待期（8 分鐘），之後將開始每分鐘檢查一次喵..."

# 先等待 8 分鐘 (480 秒)
sleep 480

# 開始檢查生成狀態
# 總共檢查 7 分鐘 (15 - 8 = 7)，每 60 秒檢查一次
MAX_CHECKS=7
CHECK_COUNT=0

while [ $CHECK_COUNT -lt $MAX_CHECKS ]; do
    QUEUE_STATUS=$(curl -s http://127.0.0.1:8001/queue)
    RUNNING=$(echo $QUEUE_STATUS | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data['queue_running']))")
    
    if [ "$RUNNING" = "0" ]; then
        IMAGE_PATH=$(find /Users/pc8521/Documents/ComfyUI/output -name "${OUTPUT_PREFIX}_*.png" -mmin -15 | head -n 1)
        
        if [ -n "$IMAGE_PATH" ]; then
            echo "圖像生成完成: $IMAGE_PATH"
            mkdir -p /Users/pc8521/.openclaw/media
            SAFE_IMAGE_PATH="/Users/pc8521/.openclaw/media/$(basename "$IMAGE_PATH")"
            cp "$IMAGE_PATH" "$SAFE_IMAGE_PATH"
            openclaw message send --channel telegram --target 7725266861 --message "圖像生成完成: $PROMPT" --media "$SAFE_IMAGE_PATH"
            
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
    sleep 60
    CHECK_COUNT=$((CHECK_COUNT + 1))
done

echo "錯誤：圖像生成超過 15 分鐘超時喵！請哥哥檢查 ComfyUI 狀態。"
exit 1
