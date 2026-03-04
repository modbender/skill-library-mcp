"""
阿里云ASR媒体处理器
只负责语音识别，返回文本内容
"""
from .media import process_media

__all__ = ['process_media']