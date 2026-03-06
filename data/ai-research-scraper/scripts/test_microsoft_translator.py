#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

def test_microsoft_translator():
    text = "This is a test sentence to translate to Chinese."
    api_key = "YOUR_API_KEY"
    endpoint = "https://api.cognitive.microsofttranslator.com"
    location = "eastasia"
    path = "/translate"
    constructed_url = endpoint + path

    params = {
        'api-version': '3.0',
        'from': 'en',
        'to': 'zh-CN'
    }

    headers = {
        'Ocp-Apim-Subscription-Key': api_key,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json'
    }

    body = [{
        'text': text
    }]

    try:
        response = requests.post(constructed_url, params=params, headers=headers, json=body, timeout=30)
        result = response.json()
        
        print(f"翻译前: {text}")
        print(f"翻译后: {result[0]['translations'][0]['text']}")
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        print(f"堆栈跟踪: {traceback.format_exc()}")

test_microsoft_translator()