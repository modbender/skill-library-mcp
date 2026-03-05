#!/usr/bin/env python3
"""
纯阿里云语音识别 (ASR) 技能
只提供语音转文字功能，无TTS/OSS等额外功能
"""

import os
import sys
import json
import base64
import requests
from pathlib import Path
from typing import Optional, Dict, Any

class AliyunPureASR:
    def __init__(self):
        self.config_path = "/root/.openclaw/aliyun-asr-config.json"
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """加载阿里云ASR配置"""
        if not os.path.exists(self.config_path):
            print(f"❌ 配置文件未找到: {self.config_path}")
            print("请创建配置文件，包含以下字段:")
            print("{")
            print('  "access_key_id": "your-access-key-id",')
            print('  "access_key_secret": "your-access-key-secret",')
            print('  "app_key": "your-app-key",')
            print('  "region": "cn-shanghai"')
            print("}")
            sys.exit(1)
            
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def get_access_token(self) -> str:
        """获取阿里云访问令牌"""
        import hmac
        import hashlib
        import time
        from urllib.parse import quote
        
        # 构建签名
        params = {
            'AccessKeyId': self.config['access_key_id'],
            'Action': 'CreateToken',
            'Format': 'JSON',
            'RegionId': self.config['region'],
            'SignatureMethod': 'HMAC-SHA1',
            'SignatureNonce': str(int(time.time() * 1000000)),
            'SignatureVersion': '1.0',
            'Timestamp': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            'Version': '2019-02-28'
        }
        
        # 排序参数
        sorted_params = sorted(params.items())
        canonicalized_query_string = '&'.join([
            f"{quote(k, safe='')}={quote(v, safe='')}" 
            for k, v in sorted_params
        ])
        
        # 构建字符串 to sign
        string_to_sign = f"GET&%2F&{quote(canonicalized_query_string, safe='')}"
        
        # 计算签名
        key = f"{self.config['access_key_secret']}&"
        signature = base64.b64encode(
            hmac.new(
                key.encode('utf-8'),
                string_to_sign.encode('utf-8'),
                hashlib.sha1
            ).digest()
        ).decode('utf-8')
        
        # 请求token
        url = f"https://nls-meta.cn-shanghai.aliyuncs.com/?{canonicalized_query_string}&Signature={quote(signature)}"
        response = requests.get(url)
        result = response.json()
        
        return result['Token']['Id']
    
    def speech_to_text(self, audio_file: str) -> str:
        """语音转文字 - 纯ASR功能"""
        try:
            # 检查是否需要转换音频格式
            import subprocess
            
            # 如果是OGG格式，转换为WAV
            if audio_file.endswith('.ogg'):
                wav_file = audio_file.replace('.ogg', '.wav')
                # 转换为16kHz单声道WAV
                subprocess.run([
                    'ffmpeg', '-i', audio_file, '-ar', '16000', '-ac', '1', 
                    '-f', 'wav', wav_file
                ], check=True, capture_output=True)
                audio_file = wav_file
            
            # 读取音频文件
            with open(audio_file, 'rb') as f:
                audio_data = f.read()
            
            # 获取访问令牌
            token = self.get_access_token()
            
            # 调用阿里云语音识别API
            url = f"https://nls-gateway.cn-shanghai.aliyuncs.com/stream/v1/asr?appkey={self.config['app_key']}"
            headers = {
                'Content-Type': 'application/octet-stream',
                'X-NLS-Token': token
            }
            
            response = requests.post(url, headers=headers, data=audio_data)
            result = response.json()
            
            if result.get('status') == 20000000:
                return result.get('result', '')
            else:
                return ""
                
        except Exception as e:
            return ""

def main():
    if len(sys.argv) != 2:
        print("用法: python3 aliyun_pure_asr.py <audio_file>")
        print("示例: python3 aliyun_pure_asr.py input.mp3")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    if not os.path.exists(audio_file):
        print(f"❌ 音频文件不存在: {audio_file}")
        sys.exit(1)
    
    asr = AliyunPureASR()
    text = asr.speech_to_text(audio_file)
    print(text)

if __name__ == "__main__":
    main()