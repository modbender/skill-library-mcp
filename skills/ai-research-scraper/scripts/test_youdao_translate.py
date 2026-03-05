#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import hashlib
import random

def test_youdao_translate():
    text = "This is a test sentence to translate to Chinese."
    app_id = "YOUR_APP_ID"
    app_secret = "YOUR_APP_SECRET"
    
    try:
        # 生成签名
        salt = str(random.randint(10000, 99999))
        sign_str = f"{app_id}{text}{salt}{app_secret}"
        sign = hashlib.md5(sign_str.encode("utf-8")).hexdigest()
        
        # 构建请求
        url = "https://openapi.youdao.com/api"
        params = {
            "q": text,
            "from": "auto",
            "to": "zh-CN",
            "appKey": app_id,
            "salt": salt,
            "sign": sign
        }
        
        # 发送请求
        response = requests.get(url, params=params, timeout=30)
        data = response.json()
        
        # 提取翻译结果
        if "translation" in data:
            translated = data["translation"][0]
            print(f"原文: {text}")
            print(f"译文: {translated}")
        else:
            print(f"翻译错误: {data}")
    except Exception as e:
        print(f"翻译错误: {str(e)}")
        return text

test_youdao_translate()