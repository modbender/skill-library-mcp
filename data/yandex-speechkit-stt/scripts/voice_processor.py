#!/usr/bin/env python3
"""
Telegram Voice Auto-Processor для OpenClaw
Мониторит входящие голосовые и автоматически распознаёт через Yandex SpeechKit
"""
import os
import sys
import json
import time
import subprocess
import hashlib

# Конфигурация
WORKSPACE = '/home/mockingjay/.openclaw/workspace'
INBOX_DIR = '/home/mockingjay/.openclaw/media/inbound'
SKILL_DIR = f'{WORKSPACE}/skills/yandex-speechkit-stt'
CONFIG_FILE = f'{SKILL_DIR}/config.json'
PROCESSED_FILE = f'{WORKSPACE}/.voice_processed.json'

def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)

def get_iam_token(config):
    import jwt
    import requests
    
    private_key = config['private_key']
    if '-----BEGIN PRIVATE KEY-----' in private_key:
        private_key = private_key[private_key.find('-----BEGIN PRIVATE KEY-----'):]
    
    now = int(time.time())
    payload = {
        'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
        'iss': config['service_account_id'],
        'sub': config['service_account_id'],
        'iat': now,
        'exp': now + 3600
    }
    
    headers = {'kid': config['id']}
    encoded = jwt.encode(payload, private_key, algorithm='PS256', headers=headers)
    
    response = requests.post(
        'https://iam.api.cloud.yandex.net/iam/v1/tokens',
        json={'jwt': encoded},
        timeout=30
    )
    return response.json()['iamToken']

def speech_to_text(audio_path, folder_id, token):
    import requests
    import subprocess
    import os
    import tempfile
    
    # Проверяем длительность
    result = subprocess.run(
        ['ffmpeg', '-i', audio_path, '2>&1'],
        capture_output=True, text=True
    )
    
    # Парсим длительность из вывода ffmpeg
    duration = 0
    for line in result.stderr.split('\n'):
        if 'Duration:' in line:
            time_str = line.split('Duration:')[1].split(',')[0].strip()
            h, m, s = time_str.split(':')
            duration = int(h) * 3600 + int(m) * 60 + float(s)
            break
    
    with open(audio_path, 'rb') as f:
        audio_data = f.read()
    
    # Если длиннее 30 сек - разбиваем
    if duration > 30:
        print(f"Файл длинный ({duration}с), разбиваем на куски...")
        
        # Разбиваем на чанки по 30 сек
        chunk_dir = tempfile.mkdtemp()
        subprocess.run([
            'ffmpeg', '-i', audio_path,
            '-f', 'segment', '-segment_time', '30',
            '-c', 'copy', f'{chunk_dir}/chunk_%03d.ogg', '-y'
        ], capture_output=True)
        
        full_text = []
        for chunk_file in sorted(os.listdir(chunk_dir)):
            chunk_path = f'{chunk_dir}/{chunk_file}'
            with open(chunk_path, 'rb') as f:
                chunk_data = f.read()
            
            url = f'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?folderId={folder_id}'
            headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'audio/ogg'}
            
            response = requests.post(url, headers=headers, data=chunk_data, timeout=60)
            if response.status_code == 200:
                result = response.json()
                text = result.get('result', '')
                if text:
                    full_text.append(text)
        
        # Чистим
        subprocess.run(['rm', '-rf', chunk_dir])
        
        return ' '.join(full_text), duration
    
    # Короткий файл - обрабатываем сразу
    url = f'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?folderId={folder_id}'
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'audio/ogg'}
    
    response = requests.post(url, headers=headers, data=audio_data, timeout=60)
    result = response.json()
    return result.get('result', ''), duration

def get_processed():
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE) as f:
            return json.load(f)
    return {}

def save_processed(data):
    with open(PROCESSED_FILE, 'w') as f:
        json.dump(data, f)

def send_to_openclaw(text, duration):
    """Отправляем распознанный текст в Telegram чат со статистикой"""
    # ~1.5₽ за минуту
    cost = round(duration / 60 * 1.5, 2)
    
    message = f"🎤 Голосовое ({duration}с)\n\n{text}\n\n💰 ~{cost}₽"
    
    cmd = [
        'openclaw', 'message', 'send',
        '--channel', 'telegram',
        '--target', '271578652',
        '--message', message
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Результат: {result.returncode}")
    if result.stdout:
        print(f"stdout: {result.stdout}")
    if result.stderr:
        print(f"stderr: {result.stderr}")
    return result.returncode == 0

def main():
    print("🎧 Voice Processor запущен...")
    print(f"Мониторим: {INBOX_DIR}")
    
    processed = get_processed()
    config = load_config()
    folder_id = config.get('folder_id') or config['service_account_id']
    
    while True:
        try:
            # Получаем IAM токен (обновляем каждый час)
            token = get_iam_token(config)
            print(f"✓ IAM токен получен")
            
            while True:
                # Сканируем входящие файлы
                for filename in os.listdir(INBOX_DIR):
                    if filename.endswith('.ogg') and not filename.startswith('.'):
                        filepath = os.path.join(INBOX_DIR, filename)
                        
                        # Проверяем, не обработали ли уже
                        file_hash = hashlib.md5(filepath.encode()).hexdigest()
                        if file_hash in processed:
                            continue
                        
                        print(f"🎤 Новое голосовое: {filename}")
                        
                        try:
                            # Распознаём
                            text, duration = speech_to_text(filepath, folder_id, token)
                            print(f"📝 Распознано: {text[:100]}... ({duration}с)")
                            
                            if text:
                                # Отправляем в OpenClaw
                                send_to_openclaw(text, duration)
                                processed[file_hash] = text
                                save_processed(processed)
                                print(f"✓ Отправлено в чат!")
                            else:
                                print("⚠️ Пустой результат")
                                
                        except Exception as e:
                            print(f"❌ Ошибка: {e}")
                
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            time.sleep(5)

if __name__ == '__main__':
    main()
