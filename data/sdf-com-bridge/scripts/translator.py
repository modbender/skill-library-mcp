#!/usr/bin/env python3
"""
OpenClaw LLM 翻译层
由主 agent（大鱼）处理实际的翻译工作
"""

import json
import re
import os
import time
from typing import Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
import hashlib


QUEUE_DIR = Path.home() / ".openclaw/workspace/.com-translation-queue"
RESULT_DIR = Path.home() / ".openclaw/workspace/.com-translation-results"


@dataclass
class TranslationRequest:
    """翻译请求"""
    request_id: str
    text: str
    source_lang: str
    target_lang: str
    timestamp: str
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def create(cls, text: str, source: str, target: str) -> "TranslationRequest":
        content_hash = hashlib.md5(f"{text}:{source}:{target}".encode()).hexdigest()[:12]
        return cls(
            request_id=f"{content_hash}_{int(time.time() * 1000)}",
            text=text,
            source_lang=source,
            target_lang=target,
            timestamp=datetime.utcnow().isoformat()
        )


@dataclass
class TranslationResult:
    """翻译结果"""
    original: str
    translated: str
    source_lang: str
    target_lang: str
    success: bool
    error: Optional[str] = None


class OpenClawTranslator:
    """OpenClaw LLM 翻译器 - 通过文件队列触发主 agent 翻译"""
    
    CHINESE_PATTERN = re.compile(r'[\u4e00-\u9fff]')
    
    def __init__(self, sync_timeout: float = 15.0):
        self.sync_timeout = sync_timeout
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        QUEUE_DIR.mkdir(parents=True, exist_ok=True)
        RESULT_DIR.mkdir(parents=True, exist_ok=True)
    
    def _detect_language(self, text: str) -> str:
        if not text:
            return 'en'
        if self.CHINESE_PATTERN.search(text):
            return 'zh'
        return 'en'
    
    def _submit_request(self, request: TranslationRequest) -> None:
        request_file = QUEUE_DIR / f"{request.request_id}.json"
        with open(request_file, 'w', encoding='utf-8') as f:
            json.dump(request.to_dict(), f, ensure_ascii=False, indent=2)
    
    def _wait_for_result(self, request_id: str, timeout: float = None) -> Optional[str]:
        timeout = timeout or self.sync_timeout
        result_file = RESULT_DIR / f"{request_id}.json"
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if result_file.exists():
                try:
                    with open(result_file, 'r', encoding='utf-8') as f:
                        result = json.load(f)
                    result_file.unlink()
                    return result.get('translated', result.get('text'))
                except Exception:
                    return None
            time.sleep(0.1)
        
        return None
    
    def translate(self, text: str, 
                  source_lang: Optional[str] = None,
                  target_lang: Optional[str] = None,
                  sync: bool = True) -> TranslationResult:
        """翻译文本"""
        if not text or not text.strip():
            return TranslationResult(
                original=text,
                translated=text,
                source_lang='unknown',
                target_lang='unknown',
                success=False
            )
        
        if not source_lang or source_lang == 'auto':
            source_lang = self._detect_language(text)
        
        if not target_lang or target_lang == 'auto':
            target_lang = 'en' if source_lang == 'zh' else 'zh'
        
        if source_lang == target_lang:
            return TranslationResult(original=text, translated=text, 
                                    source_lang=source_lang, target_lang=target_lang, success=True)
        
        request = TranslationRequest.create(text, source_lang, target_lang)
        self._submit_request(request)
        
        if sync:
            translated = self._wait_for_result(request.request_id)
            if translated:
                return TranslationResult(original=text, translated=translated,
                                        source_lang=source_lang, target_lang=target_lang, success=True)
        
        return TranslationResult(
            original=text,
            translated=f"[{target_lang.upper()}] {text}",
            source_lang=source_lang,
            target_lang=target_lang,
            success=False,
            error="Waiting for translation"
        )
    
    def quick_translate_en_to_zh(self, text: str) -> str:
        result = self.translate(text, 'en', 'zh', sync=True)
        return result.translated if result.success else text
    
    def quick_translate_zh_to_en(self, text: str) -> str:
        result = self.translate(text, 'zh', 'en', sync=True)
        return result.translated if result.success else text


LLMTranslator = OpenClawTranslator

if __name__ == "__main__":
    translator = OpenClawTranslator()
    print("Translator ready - waiting for requests in", QUEUE_DIR)
