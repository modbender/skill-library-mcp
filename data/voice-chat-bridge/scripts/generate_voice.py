#!/usr/bin/env python3
"""
语音回复生成器
使用 Edge TTS 生成语音文件
"""

import subprocess
import os
import sys
import uuid
import json

VOICE_DIR = os.path.expanduser("~/.openclaw/workspace/voice_output")
CONFIG_FILE = os.path.expanduser("~/.openclaw/workspace/voice_config.json")

def load_config():
    """加载配置"""
    default_config = {
        "domain": "https://your-domain.com",
        "local_port": 8765,
        "voice": "zh-CN-XiaoxiaoNeural"
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except:
            pass
    
    return default_config

def ensure_dir():
    """确保输出目录存在"""
    os.makedirs(VOICE_DIR, exist_ok=True)

def generate_voice(text, config=None):
    """使用 Edge TTS 生成语音文件"""
    if config is None:
        config = load_config()
    
    filename = f"{uuid.uuid4().hex[:8]}.mp3"
    output_path = os.path.join(VOICE_DIR, filename)
    
    edge_tts = "/Library/Frameworks/Python.framework/Versions/3.13/bin/edge-tts"
    voice = config.get("voice", "zh-CN-XiaoxiaoNeural")
    
    cmd = [
        edge_tts,
        "--voice", voice,
        "--text", text,
        "--write-media", output_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0 and os.path.exists(output_path):
            return filename, output_path
        else:
            print(f"生成失败: {result.stderr}")
            return None, None
    except Exception as e:
        print(f"错误: {e}")
        return None, None

def get_url(filename, config):
    """生成 URL"""
    return f"{config['domain']}/{filename}"

def speak(text):
    """生成语音并返回 URL"""
    config = load_config()
    ensure_dir()
    
    # 清理旧文件
    try:
        files = sorted([f for f in os.listdir(VOICE_DIR) if f.endswith('.mp3')],
                      key=lambda f: os.path.getmtime(os.path.join(VOICE_DIR, f)))
        if len(files) > 50:
            for old in files[:-50]:
                os.remove(os.path.join(VOICE_DIR, old))
    except:
        pass
    
    filename, path = generate_voice(text, config)
    if filename:
        url = get_url(filename, config)
        print(f"✅ 语音已生成: {filename}")
        print(f"📁 大小: {os.path.getsize(path) / 1024:.1f} KB")
        print(f"🔗 {url}")
        return url
    return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        speak(" ".join(sys.argv[1:]))
    else:
        print("用法: python3 generate_voice.py '要合成的文字'")
