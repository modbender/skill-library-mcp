#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import datetime
from typing import Dict, Any

def main(params: Dict[str, Any]) -> str:
    """
    最简单的测试函数
    """
    # 获取用户输入
    query = params.get("query", "")
    
    # 获取当前时间
    now = datetime.datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    
    # 构造返回结果
    result = {
        "status": "success",
        "message": f"收到消息啦！",
        "your_input": query,
        "current_time": current_time,
        "server": "阿里云 Moltbot"
    }
    
    return json.dumps(result, ensure_ascii=False, indent=2)

# 测试代码
if __name__ == "__main__":
    test_params = {"query": "你好，这是测试"}
    print(main(test_params))