"""
微信公众号文章阅读 Skill
输入公众号文章 URL，自动抓取正文、清洗排版、输出结构化文本
"""

from .read_wechat_article import read_wechat_article, WeChatArticleReader

__version__ = "1.0.0"
__author__ = "OpenClaw Team"
__description__ = "微信公众号文章抓取和解析Skill"

__all__ = ["read_wechat_article", "WeChatArticleReader"]