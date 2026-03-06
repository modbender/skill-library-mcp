#!/usr/bin/env python3
"""
Translation Handler for OpenClaw Agent
由大鱼（主 agent）运行，处理 COM Bridge 触发的翻译请求
"""

import json
import os
import time
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime

QUEUE_DIR = Path.home() / ".openclaw/workspace/.com-translation-queue"
RESULT_DIR = Path.home() / ".openclaw/workspace/.com-translation-results"


def ensure_dirs():
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_DIR.mkdir(parents=True, exist_ok=True)


def get_pending_requests() -> list:
    """获取待翻译的请求"""
    ensure_dirs()
    requests = []
    for f in QUEUE_DIR.glob("*.json"):
        try:
            with open(f, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
                data['file_path'] = str(f)
                requests.append(data)
        except:
            pass
    return requests


def submit_translation_result(request_id: str, translated_text: str):
    """提交翻译结果"""
    result_file = RESULT_DIR / f"{request_id}.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            "translated": translated_text,
            "timestamp": datetime.utcnow().isoformat()
        }, f, ensure_ascii=False)


def cleanup_request(file_path: str):
    """清理已处理的请求"""
    try:
        Path(file_path).unlink()
    except:
        pass


def check_and_translate() -> list:
    """
    检查并返回待翻译的请求
    主 agent（大鱼）需要轮询此函数并进行翻译
    
    Returns:
        待翻译的请求列表，包含 request_id, text, source_lang, target_lang
    """
    return get_pending_requests()


def mark_translated(request: dict, translation: str):
    """
    标记翻译完成
    
    Args:
        request: 请求字典（来自 check_and_translate）
        translation: 翻译后的文本
    """
    submit_translation_result(request['request_id'], translation)
    if 'file_path' in request:
        cleanup_request(request['file_path'])


if __name__ == "__main__":
    # 测试模式 - 列出待翻译请求
    print("Checking for pending translations...")
    pending = check_and_translate()
    print(f"Found {len(pending)} pending requests")
    for req in pending:
        print(f"\n  ID: {req['request_id']}")
        print(f"  {req['source_lang']} -> {req['target_lang']}")
        print(f"  Text: {req['text']}")
