#!/usr/bin/env python3
"""
Yandex SpeechKit STT - Распознавание речи из аудио
Использование: python yandex_stt.py <path_to_audio> [folder_id] [iam_token]
"""
import sys
import os
import json
import requests
import uuid

def get_token_iam(folder_id: str, service_account_id: str, private_key: str, key_id: str = None) -> str:
    """Получение IAM токена через сервисный аккаунт (PS256)"""
    import jwt
    import time
    
    now = int(time.time())
    payload = {
        'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
        'iss': service_account_id,
        'sub': service_account_id,
        'iat': now,
        'exp': now + 3600
    }
    
    # Yandex требует PS256
    headers = {'kid': key_id} if key_id else {}
    encoded = jwt.encode(payload, private_key, algorithm='PS256', headers=headers)
    
    response = requests.post(
        'https://iam.api.cloud.yandex.net/iam/v1/tokens',
        json={'jwt': encoded},
        timeout=30
    )
    response.raise_for_status()
    return response.json()['iamToken']

def speech_to_text(audio_path: str, folder_id: str, iam_token: str) -> str:
    """Распознавание речи через Yandex SpeechKit"""
    
    import subprocess
    import tempfile
    
    # Проверяем длительность аудио
    probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
                 '-of', 'default=noprint_wrappers=1:nokey=1', audio_path]
    try:
        result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=10)
        duration = float(result.stdout.strip()) if result.stdout.strip() else 0
    except:
        duration = 0
    
    # Если аудио длиннее 28 секунд, обрезаем
    temp_file = None
    if duration > 28:
        temp_file = tempfile.NamedTemporaryFile(suffix='.ogg', delete=False)
        temp_file.close()
        # Конвертируем в 16kHz mono OGG (opus)
        convert_cmd = ['ffmpeg', '-i', audio_path, '-t', '28', '-ar', '16000', 
                       '-ac', '1', '-c:a', 'libopus', temp_file.name, '-y']
        subprocess.run(convert_cmd, capture_output=True, timeout=30)
        audio_path = temp_file.name
    
    # Читаем аудио файл
    with open(audio_path, 'rb') as f:
        audio_data = f.read()
    
    # URL для Yandex SpeechKit
    url = f'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?folderId={folder_id}'
    
    headers = {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'audio/ogg'
    }
    
    # Отправляем как binary data, не multipart
    response = requests.post(url, headers=headers, data=audio_data, timeout=60)
    
    # Удаляем временный файл
    if temp_file:
        os.unlink(temp_file.name)
    
    response.raise_for_status()
    
    result = response.json()
    if result.get('result'):
        return result['result']
    return ""

def main():
    import os
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python yandex_stt.py <audio_file> [folder_id] [iam_token]")
        print("Или используй переменные окружения / config.json:")
        print("  YANDEX_FOLDER_ID")
        print("  YANDEX_IAM_TOKEN")
        print("  YANDEX_SERVICE_ACCOUNT_ID")
        print("  YANDEX_PRIVATE_KEY")
        
        # Попробуем загрузить из config.json
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        if os.path.exists(config_path):
            with open(config_path) as f:
                config = json.load(f)
            print(f"\n✓ Найден config.json: service_account_id={config.get('service_account_id')}")
        sys.exit(1)
    
    audio_path = sys.argv[1]
    folder_id = sys.argv[2] if len(sys.argv) > 2 else os.environ.get('YANDEX_FOLDER_ID')
    iam_token = sys.argv[3] if len(sys.argv) > 3 else os.environ.get('YANDEX_IAM_TOKEN')
    
    # Загружаем из config.json если не указано
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    key_id = None
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
        # Используем folder_id из конфига (может отличаться от service_account_id)
        if not folder_id:
            folder_id = config.get('folder_id') or config.get('service_account_id')
        if not (os.environ.get('YANDEX_SERVICE_ACCOUNT_ID') or os.environ.get('YANDEX_PRIVATE_KEY')):
            # Очищаем ключ от мусора
            private_key = config.get('private_key', '')
            if '-----BEGIN PRIVATE KEY-----' in private_key:
                private_key = private_key[private_key.find('-----BEGIN PRIVATE KEY-----'):]
            os.environ['YANDEX_SERVICE_ACCOUNT_ID'] = config.get('service_account_id')
            os.environ['YANDEX_PRIVATE_KEY'] = private_key
            os.environ['YANDEX_KEY_ID'] = config.get('id')
            key_id = config.get('id')
    
    # Если нет IAM токена, получаем через service account
    if not iam_token and os.environ.get('YANDEX_SERVICE_ACCOUNT_ID') and os.environ.get('YANDEX_PRIVATE_KEY'):
        service_account_id = os.environ.get('YANDEX_SERVICE_ACCOUNT_ID')
        private_key = os.environ.get('YANDEX_PRIVATE_KEY')
        key_id = key_id or os.environ.get('YANDEX_KEY_ID')
        iam_token = get_token_iam(folder_id, service_account_id, private_key, key_id)
    
    if not folder_id:
        print("Error: folder_id не указан")
        sys.exit(1)
    
    if not iam_token:
        print("Error: iam_token не указан")
        sys.exit(1)
    
    result = speech_to_text(audio_path, folder_id, iam_token)
    print(result)

if __name__ == '__main__':
    main()
