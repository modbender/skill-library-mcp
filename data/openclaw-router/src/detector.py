"""
环境检测模块
检测本地和云端可用模型
"""

import os
import requests
import psutil
from typing import Dict, List, Optional


class EnvironmentDetector:
    """环境检测器"""
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
    
    def detect_ollama(self) -> Dict:
        """检测 Ollama 安装情况"""
        try:
            response = requests.get(
                f"{self.ollama_url}/api/tags",
                timeout=3
            )
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m["name"] for m in models]
                return {
                    "installed": True,
                    "models": model_names,
                    "count": len(model_names)
                }
        except Exception as e:
            pass
        
        return {
            "installed": False,
            "models": [],
            "count": 0
        }
    
    def detect_dashscope(self) -> Dict:
        """检测阿里云百炼"""
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if api_key:
            return {
                "configured": True,
                "api_key_masked": api_key[:10] + "..." + api_key[-5:],
                "provider": "dashscope"
            }
        return {
            "configured": False,
            "provider": "dashscope"
        }
    
    def detect_openai(self) -> Dict:
        """检测 OpenAI"""
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            return {
                "configured": True,
                "api_key_masked": api_key[:10] + "..." + api_key[-5:],
                "provider": "openai"
            }
        return {
            "configured": False,
            "provider": "openai"
        }
    
    def detect_anthropic(self) -> Dict:
        """检测 Anthropic"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            return {
                "configured": True,
                "api_key_masked": api_key[:10] + "..." + api_key[-5:],
                "provider": "anthropic"
            }
        return {
            "configured": False,
            "provider": "anthropic"
        }
    
    def detect_system(self) -> Dict:
        """检测系统资源"""
        memory_gb = psutil.virtual_memory().total / (1024**3)
        cpu_cores = psutil.cpu_count()
        disk_gb = psutil.disk_usage('/').total / (1024**3)
        
        return {
            "memory_gb": round(memory_gb, 1),
            "cpu_cores": cpu_cores,
            "disk_gb": round(disk_gb, 1)
        }
    
    def run_full_detection(self) -> Dict:
        """运行完整环境检测"""
        return {
            "ollama": self.detect_ollama(),
            "dashscope": self.detect_dashscope(),
            "openai": self.detect_openai(),
            "anthropic": self.detect_anthropic(),
            "system": self.detect_system()
        }
