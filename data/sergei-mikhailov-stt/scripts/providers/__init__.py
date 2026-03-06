#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STT providers package for speech recognition.

This package contains implementations of various speech recognition providers:
- Yandex SpeechKit
- Google Speech-to-Text (extensible)
- OpenAI Whisper (extensible)
- Custom providers (extensible)
"""

from .base_provider import BaseSTTProvider
from .yandex_speechkit import YandexSpeechKitProvider

__all__ = ['BaseSTTProvider', 'YandexSpeechKitProvider']
