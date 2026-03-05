#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio

async def test_googletrans():
    try:
        from googletrans import Translator
        translator = Translator()
        
        text = "This is a test sentence to translate to Chinese."
        result = await translator.translate(text, dest='zh-CN')
        
        print(f"翻译前: {text}")
        print(f"翻译后: {result.text}")
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        print(f"堆栈跟踪: {traceback.format_exc()}")

asyncio.run(test_googletrans())