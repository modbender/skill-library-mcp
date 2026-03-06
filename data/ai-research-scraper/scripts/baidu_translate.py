#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度翻译API实现
"""

import requests
import hashlib
import random
import json


class BaiduTranslator:
    """百度翻译API实现"""
    
    def __init__(self, app_id, app_secret):
        """
        初始化翻译器
        
        Args:
            app_id: 百度翻译API的应用ID
            app_secret: 百度翻译API的应用密钥
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.api_url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
    
    def translate(self, text, from_lang="auto", to_lang="zh"):
        """
        翻译文本
        
        Args:
            text: 要翻译的文本
            from_lang: 源语言，默认自动检测
            to_lang: 目标语言，默认中文
        
        Returns:
            str: 翻译后的文本
        """
        try:
            salt = str(random.randint(10000, 99999))
            sign = self._generate_sign(text, salt)
            
            params = {
                "q": text,
                "from": from_lang,
                "to": to_lang,
                "appid": self.app_id,
                "salt": salt,
                "sign": sign
            }
            
            response = requests.get(self.api_url, params=params, timeout=30)
            result = json.loads(response.text)
            
            if "trans_result" in result:
                return "".join([item["dst"] for item in result["trans_result"]])
            else:
                return text
        except Exception as e:
            print(f"翻译错误: {str(e)}")
            return text
    
    def _generate_sign(self, text, salt):
        """
        生成签名
        
        Args:
            text: 要翻译的文本
            salt: 随机数
        
        Returns:
            str: MD5签名
        """
        sign_str = f"{self.app_id}{text}{salt}{self.app_secret}"
        return hashlib.md5(sign_str.encode("utf-8")).hexdigest()


# 使用方法示例
if __name__ == "__main__":
    # 需要替换为你自己的百度翻译API应用ID和密钥
    translator = BaiduTranslator(
        app_id="YOUR_APP_ID",
        app_secret="YOUR_APP_SECRET"
    )
    
    # 测试翻译
    test_text = "This is a test sentence to translate to Chinese."
    result = translator.translate(test_text)
    print(f"原文: {test_text}")
    print(f"译文: {result}")