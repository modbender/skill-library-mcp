#!/usr/bin/env python3
"""
GitHub Webhook Handler for OpenClaw
Обрабатывает webhooks от GitHub и синхронизирует изменения с OpenClaw
"""

import os
import json
import hashlib
import hmac
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

# Конфигурация
GITHUB_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET', '')
OPENCLAW_PATH = os.getenv('OPENCLAW_PATH', '/usr/local/bin/openclaw')
SKILLS_DIR = os.getenv('OPENCLAW_SKILLS_DIR', '/home/moltbot1/.openclaw/skills')

def verify_signature(payload_body, secret_token, signature_header):
    """Верификация подписи GitHub webhook"""
    if not signature_header:
        return False
    
    hash_object = hmac.new(secret_token.encode('utf-8'), 
                          msg=payload_body, 
                          digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    
    return hmac.compare_digest(expected_signature, signature_header)

def update_skill(skill_name, repo_url, branch='main'):
    """Обновляет навык из GitHub репозитория"""
    skill_dir = os.path.join(SKILLS_DIR, skill_name)
    
    # Создаем директорию если не существует
    if not os.path.exists(skill_dir):
        os.makedirs(skill_dir, exist_ok=True)
        # Клонируем репозиторий
        subprocess.run(['git', 'clone', repo_url, skill_dir], check=True)
    
    # Переходим в директорию и обновляем
    os.chdir(skill_dir)
    subprocess.run(['git', 'fetch', 'origin'], check=True)
    subprocess.run(['git', 'checkout', branch], check=True)
    subprocess.run(['git', 'pull', 'origin', branch], check=True)
    
    # Запускаем установку если есть install.sh
    install_script = os.path.join(skill_dir, 'install.sh')
    if os.path.exists(install_script):
        os.chmod(install_script, 0o755)
        subprocess.run(['./install.sh'], check=True)
    
    # Перезагружаем навык в OpenClaw
    subprocess.run([OPENCLAW_PATH, 'skill', 'reload', skill_name], check=True)
    
    return True

@app.route('/webhook/github', methods=['POST'])
def github_webhook():
    """Обработчик GitHub webhook"""
    # Верификация подписи
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_signature(request.data, GITHUB_SECRET, signature):
        return jsonify({'error': 'Invalid signature'}), 401
    
    event = request.headers.get('X-GitHub-Event')
    payload = request.get_json()
    
    print(f"📦 GitHub event: {event}")
    
    # Обрабатываем push события
    if event == 'push':
        repo_name = payload['repository']['name']
        repo_url = payload['repository']['clone_url']
        branch = payload['ref'].split('/')[-1]
        
        # Определяем имя навыка на основе репозитория
        skill_name = repo_name.replace('_', '-').lower()
        
        try:
            # Обновляем навык
            update_skill(skill_name, repo_url, branch)
            
            # Логируем успех
            commit_message = payload['head_commit']['message'] if 'head_commit' in payload else 'N/A'
            print(f"✅ Updated skill '{skill_name}' from {repo_url} ({branch})")
            print(f"   Commit: {commit_message}")
            
            return jsonify({
                'status': 'success',
                'skill': skill_name,
                'action': 'updated',
                'repository': repo_name,
                'branch': branch
            })
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to update skill: {e}")
            return jsonify({'error': str(e)}), 500
    
    # Обрабатываем release события
    elif event == 'release':
        repo_name = payload['repository']['name']
        release_tag = payload['release']['tag_name']
        
        print(f"🎉 New release: {repo_name} {release_tag}")
        
        return jsonify({
            'status': 'success',
            'event': 'release',
            'repository': repo_name,
            'tag': release_tag
        })
    
    return jsonify({'status': 'ignored', 'event': event}), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'openclaw-github-webhook'})

if __name__ == '__main__':
    # Запуск сервера
    port = int(os.getenv('PORT', 3000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    print(f"🚀 Starting GitHub webhook handler on port {port}")
    print(f"📁 Skills directory: {SKILLS_DIR}")
    print(f"🔧 OpenClaw path: {OPENCLAW_PATH}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)