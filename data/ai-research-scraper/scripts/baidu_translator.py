#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import hashlib
import random

class BaiduTranslator:
    def __init__(self, app_id, secret_key):
        self.app_id = app_id
        self.secret_key = secret_key
        self.url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'

    def translate(self, text, from_lang='auto', to_lang='zh'):
        salt = str(random.randint(32768, 65536))
        sign = hashlib.md5(f"{self.app_id}{text}{salt}{self.secret_key}".encode()).hexdigest()
        params = {
            'q': text,
            'from': from_lang,
            'to': to_lang,
            'appid': self.app_id,
            'salt': salt,
            'sign': sign
        }
        try:
            response = requests.get(self.url, params=params, timeout=5)
            result = response.json()
            if 'trans_result' in result:
                return result['trans_result'][0]['dst']
            else:
                print(f"翻译错误: {result}")
                return text
        except Exception as e:
            print(f"翻译错误: {str(e)}")
            return text