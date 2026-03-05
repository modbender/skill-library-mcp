"""
视觉识别模块
支持：图像理解、OCR、截图分析

支持的模型：
- Claude-3 (Opus/Sonnet/Haiku)
- GPT-4o / GPT-4 Turbo
- 阿里云 qwen-vl-max / qwen-vl-plus
"""

import base64
import os
from typing import Optional


class VisionRecognizer:
    """视觉识别器"""
    
    def __init__(self, provider: Optional[str] = None):
        """
        初始化视觉识别器
        
        Args:
            provider: 提供商 ('anthropic', 'openai', 'dashscope')
                     默认自动检测
        """
        self.provider = provider or self._auto_detect_provider()
        self.api_key = self._get_api_key()
    
    def _auto_detect_provider(self) -> str:
        """自动检测可用的提供商"""
        if os.getenv('ANTHROPIC_API_KEY'):
            return 'anthropic'
        elif os.getenv('OPENAI_API_KEY'):
            return 'openai'
        elif os.getenv('DASHSCOPE_API_KEY'):
            return 'dashscope'
        else:
            raise ValueError("未找到任何视觉 API Key")
    
    def _get_api_key(self) -> str:
        """获取 API Key"""
        if self.provider == 'anthropic':
            return os.getenv('ANTHROPIC_API_KEY', '')
        elif self.provider == 'openai':
            return os.getenv('OPENAI_API_KEY', '')
        elif self.provider == 'dashscope':
            return os.getenv('DASHSCOPE_API_KEY', '')
        else:
            return ''
    
    def _encode_image(self, image_path: str) -> str:
        """将图片编码为 base64"""
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def analyze_image(self, image_path: str, prompt: str = "描述这张图片") -> dict:
        """
        分析图片内容
        
        Args:
            image_path: 图片路径
            prompt: 提示词
        
        Returns:
            分析结果
        """
        image_base64 = self._encode_image(image_path)
        
        if self.provider == 'anthropic':
            return self._analyze_with_claude(image_base64, prompt)
        elif self.provider == 'openai':
            return self._analyze_with_gpt4(image_base64, prompt)
        elif self.provider == 'dashscope':
            return self._analyze_with_qwen_vl(image_base64, prompt)
        else:
            raise ValueError(f"不支持的提供商：{self.provider}")
    
    def _analyze_with_claude(self, image_base64: str, prompt: str) -> dict:
        """使用 Claude-3 分析图片"""
        import requests
        
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        payload = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 1024,
            "messages": [{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }]
        }
        
        response = requests.post(url, json=payload, headers=headers)
        result = response.json()
        
        return {
            "success": response.status_code == 200,
            "content": result.get('content', [{}])[0].get('text', ''),
            "provider": 'anthropic',
            "model": 'claude-3-sonnet'
        }
    
    def _analyze_with_gpt4(self, image_base64: str, prompt: str) -> dict:
        """使用 GPT-4o 分析图片"""
        import requests
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4o",
            "messages": [{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }]
        }
        
        response = requests.post(url, json=payload, headers=headers)
        result = response.json()
        
        return {
            "success": response.status_code == 200,
            "content": result.get('choices', [{}])[0].get('message', {}).get('content', ''),
            "provider": 'openai',
            "model": 'gpt-4o'
        }
    
    def _analyze_with_qwen_vl(self, image_base64: str, prompt: str) -> dict:
        """使用阿里云 qwen-vl 分析图片"""
        import requests
        
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "qwen-vl-max",
            "input": {
                "messages": [{
                    "role": "user",
                    "content": [
                        {
                            "image": f"data:image/png;base64,{image_base64}"
                        },
                        {
                            "text": prompt
                        }
                    ]
                }]
            }
        }
        
        response = requests.post(url, json=payload, headers=headers)
        result = response.json()
        
        return {
            "success": response.status_code == 200,
            "content": result.get('output', {}).get('choices', [{}])[0].get('message', {}).get('content', ''),
            "provider": 'dashscope',
            "model": 'qwen-vl-max'
        }
    
    def extract_text(self, image_path: str) -> dict:
        """OCR 文字提取"""
        return self.analyze_image(
            image_path,
            "提取图片中的所有文字，保持原有格式"
        )
    
    def describe_screenshot(self, image_path: str) -> dict:
        """描述截图内容"""
        return self.analyze_image(
            image_path,
            "详细描述这张截图的内容，包括：1.界面布局 2.所有可见文字 3.按钮和交互元素 4.整体功能推测"
        )
    
    def analyze_ui_elements(self, image_path: str) -> dict:
        """分析 UI 元素"""
        return self.analyze_image(
            image_path,
            "分析这个界面的所有 UI 元素，包括按钮、输入框、菜单等，并说明它们的位置和功能"
        )


# 快捷函数
def recognize_image(image_path: str, prompt: str = "描述这张图片") -> str:
    """快速识别图片"""
    recognizer = VisionRecognizer()
    result = recognizer.analyze_image(image_path, prompt)
    return result.get('content', '') if result.get('success') else f"识别失败：{result}"


def extract_text_from_image(image_path: str) -> str:
    """快速 OCR"""
    recognizer = VisionRecognizer()
    result = recognizer.extract_text(image_path)
    return result.get('content', '') if result.get('success') else f"OCR 失败：{result}"
