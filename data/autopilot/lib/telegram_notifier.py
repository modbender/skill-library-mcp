#!/usr/bin/env python3
"""
Telegram Notifier
- 发送 Telegram 通知
- 支持 MarkdownV2 格式，失败回退纯文本
"""

import logging
import re
from typing import Optional

import requests

logger = logging.getLogger(__name__)


def strip_markdown(text: str) -> str:
    """
    清理 markdown 特殊字符，转换为纯文本
    """
    # 移除代码块
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`]+`', '', text)
    
    # 移除粗体/斜体标记
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    
    # 移除链接
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # 移除标题标记
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    
    return text.strip()


def escape_markdown_v2(text: str) -> str:
    """
    转义 MarkdownV2 特殊字符
    """
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


class TelegramNotifier:
    """Telegram 通知器"""
    
    def __init__(self, bot_token: str, chat_id: str):
        """
        初始化 Telegram 通知器
        
        Args:
            bot_token: Telegram Bot Token
            chat_id: 目标 Chat ID
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_base = f"https://api.telegram.org/bot{bot_token}"
    
    def send_with_parse_mode(self, text: str, parse_mode: Optional[str] = "MarkdownV2") -> bool:
        """
        发送消息，指定解析模式
        
        Args:
            text: 消息文本
            parse_mode: 解析模式 ("MarkdownV2", "HTML", None)
        
        Returns:
            是否成功
        """
        url = f"{self.api_base}/sendMessage"
        
        payload = {
            "chat_id": self.chat_id,
            "text": text,
        }
        
        if parse_mode:
            payload["parse_mode"] = parse_mode
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            logger.warning(f"Telegram 发送失败 (parse_mode={parse_mode}): {e}")
            return False
    
    def notify(self, text: str) -> bool:
        """
        发送通知（自动容错）
        
        先尝试 MarkdownV2，失败则回退纯文本
        
        Args:
            text: 消息文本
        
        Returns:
            是否成功
        """
        # 先尝试不加转义的 MarkdownV2（假设用户已经格式化好了）
        if self.send_with_parse_mode(text, "MarkdownV2"):
            return True
        
        # 尝试转义后的 MarkdownV2
        escaped = escape_markdown_v2(text)
        if self.send_with_parse_mode(escaped, "MarkdownV2"):
            return True
        
        # 回退到纯文本
        plain = strip_markdown(text)
        return self.send_with_parse_mode(plain, None)
    
    def send_simple(self, text: str) -> bool:
        """
        发送简单纯文本消息
        
        Args:
            text: 消息文本
        
        Returns:
            是否成功
        """
        return self.send_with_parse_mode(text, None)


def create_notifier_from_config(config: dict) -> Optional[TelegramNotifier]:
    """
    从配置创建通知器
    
    Args:
        config: 配置字典，需要包含 telegram.bot_token 和 telegram.chat_id
    
    Returns:
        TelegramNotifier 或 None（如果配置不完整）
    """
    telegram_config = config.get("telegram", {})
    bot_token = telegram_config.get("bot_token")
    chat_id = telegram_config.get("chat_id")
    
    if not bot_token or not chat_id:
        logger.warning("Telegram 配置不完整，通知功能禁用")
        return None
    
    return TelegramNotifier(bot_token, str(chat_id))


# 通知模板
def format_send_notification(project_name: str, reply: str, intent: str) -> str:
    """格式化发送通知"""
    return f"""📤 Autopilot | {project_name}

意图: {intent}
发送内容:
> {reply[:200]}{'...' if len(reply) > 200 else ''}"""


def format_error_notification(project_name: str, error: str) -> str:
    """格式化错误通知"""
    return f"""❌ Autopilot 错误 | {project_name}

{error}"""


def format_status_notification(project_name: str, 
                               current_task: str,
                               progress: str,
                               codex_status: str,
                               runtime: str,
                               daily_sends: int,
                               max_sends: int) -> str:
    """格式化状态通知"""
    return f"""📊 Autopilot 状态 | {project_name}

当前任务: {current_task}
进度: {progress}
Codex 状态: {codex_status}

运行时间: {runtime} | 今日发送: {daily_sends}/{max_sends}"""
