#!/usr/bin/env python3
"""
Abby Browser Scripts

浏览器操作封装脚本
"""

from .open import open_url
from .screenshot import screenshot
from .click import click
from .form import fill, type_text
from .extract import snapshot, extract_text

__all__ = [
    'open_url',
    'screenshot',
    'click',
    'fill',
    'type_text',
    'snapshot',
    'extract_text',
]
