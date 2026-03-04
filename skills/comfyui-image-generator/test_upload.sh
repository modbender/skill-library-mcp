#!/bin/bash

# 測試上傳功能的腳本
# 參數: 圖像路徑

if [ $# -ne 1 ]; then
    echo "使用方式: $0 <image_path>"
    exit 1
fi

IMAGE_PATH="$1"

echo "正在上傳圖像到Google Drive..."

python3 -c "
import os
import sys
sys.path.append('/Users/pc8521/clawd')
from tools.drive_tool import get_drive_service

def get_folder_id(folder_name):
    '''Get the ID of a folder in Google Drive'''
    service = get_drive_service()
    
    results = service.files().list(
        q=f\"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'\",
        fields='files(id, name)').execute()
    items = results.get('files', [])
    
    if items:
        return items[0]['id']
    else:
        return None

# 獲取 'Generated Images' 資料夾ID
folder_id = get_folder_id('Generated Images')
if not folder_id:
    print('找不到 Generated Images 資料夾')
    # 嘗試創建資料夾
    try:
        file_metadata = {
            'name': 'Generated Images',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()
        folder_id = folder.get('id')
        print(f'創建了 Generated Images 資料夾，ID: {folder_id}')
    except Exception as e:
        print(f'創建資料夾時出錯: {e}')
        folder_id = None

if folder_id:
    from tools.drive_tool import upload_file
    try:
        result = upload_file('$IMAGE_PATH', folder_id)
        if result:
            print('✅ 已上傳到Google Drive')
        else:
            print('❌ 上傳到Google Drive失敗')
    except Exception as e:
        print(f'❌ 上傳到Google Drive時出錯: {e}')
else:
    print('❌ 無法找到或創建目標資料夾')
"