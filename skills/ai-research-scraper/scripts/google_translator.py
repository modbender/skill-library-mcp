#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.parse
import urllib.request
import json

class GoogleTranslator:
    def translate(self, text, from_lang='auto', to_lang='zh-CN'):
        url = 'https://translate.googleapis.com/translate_a/single'
        params = {
            'client': 'gtx',
            'sl': from_lang,
            'tl': to_lang,
            'dt': 't',
            'q': urllib.parse.quote(text)
        }
        full_url = f"{url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        try:
            response = urllib.request.urlopen(full_url, timeout=5)
            data = response.read().decode('utf-8')
            result = json.loads(data)
            return result[0][0][0]
        except Exception as e:
            print(f"翻译错误: {str(e)}")
            return text