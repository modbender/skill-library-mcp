#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Speech-to-Text processing module for audio files from OpenClaw.

OpenClaw provides file paths in the format:
/home/user_folder/.openclaw/media/inbound/file_1---9a53bac2-0392-41e7-8300-1c08e8eec027.ogg
"""

import sys
import site
from pathlib import Path

# Activate the virtual environment's packages if .venv exists next to the skill root.
# OpenClaw invokes the script with system Python, so we need to add
# the venv's site-packages to sys.path manually.
_skill_root = Path(__file__).resolve().parent.parent
_venv_dir = _skill_root / ".venv"
if _venv_dir.is_dir():
    _venv_site = list(_venv_dir.glob("lib/python*/site-packages"))
    for sp in _venv_site:
        if str(sp) not in sys.path:
            site.addsitedir(str(sp))

import time
import argparse
import logging
from typing import Dict, Any, List

from config_manager import ConfigManager
from providers import YandexSpeechKitProvider


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class STTProcessor:
    """Processes an audio file from OpenClaw and returns the recognized text."""

    def __init__(self, config_path: str = None) -> None:
        logger.info("Initializing STTProcessor")

        try:
            self.config_manager = ConfigManager()
            self.config = self.config_manager.load_config(config_path)
            self.temp_dir = self.config_manager.create_temp_dir(self.config)

            default_provider = self.config.get('default_provider', 'yandex')
            self.current_provider = self._get_provider(default_provider)

            logger.info(f"STTProcessor initialized, provider: {default_provider}")

        except Exception as e:
            raise RuntimeError(f"Failed to initialize STTProcessor: {e}")

    def process_voice_message(self, file_path: str, language: str = None, provider_name: str = None) -> str:
        """
        Recognize speech from an audio file.

        Args:
            file_path: Path to the audio file from OpenClaw
            language: Language code (defaults to config value)
            provider_name: Provider name (defaults to config value)

        Returns:
            str: Recognized text

        Raises:
            FileNotFoundError: If the file is not found
            ValueError: If the file is invalid
            RuntimeError: If recognition fails
        """
        start_time = time.time()
        logger.info(f"Starting processing: {file_path}")

        # File validation
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Audio file not found or inaccessible: {file_path}")

        file_size = path.stat().st_size
        if file_size == 0:
            raise ValueError("File is empty")
        if file_size > 1 * 1024 * 1024:
            raise ValueError(f"File too large ({file_size} bytes), maximum is 1 MB (Yandex SpeechKit v1 sync API limit)")

        logger.info(f"File: {path.name} ({file_size} bytes)")

        # Resolve provider and language
        provider = self._get_provider(provider_name) if provider_name else self.current_provider
        if language is None:
            language = self.config.get('default_language', 'ru-RU')

        logger.info(f"Provider: {provider.get_name()}, language: {language}")

        # Recognize speech
        recognized_text = provider.recognize(file_path, language)

        logger.info(f"Processing completed in {time.time() - start_time:.2f} seconds")
        return recognized_text

    def _get_provider(self, provider_name: str = None) -> Any:
        if provider_name is None:
            provider_name = self.config.get('default_provider', 'yandex')

        try:
            provider_config = self.config_manager.get_provider_config(self.config, provider_name)

            if provider_name == 'yandex':
                return YandexSpeechKitProvider(provider_config)

            raise ValueError(f"Unknown provider: {provider_name}")

        except Exception as e:
            raise ValueError(f"Failed to initialize provider {provider_name}: {e}")

    def get_available_providers(self) -> List[str]:
        return list(self.config.get('providers', {}).keys())

    def get_config_info(self) -> Dict[str, Any]:
        return {
            'default_provider': self.config.get('default_provider'),
            'default_language': self.config.get('default_language', 'ru-RU'),
            'available_providers': self.get_available_providers(),
            'temp_dir': self.temp_dir,
            'current_provider': self.current_provider.get_name()
        }


def main() -> None:
    """CLI interface for running the STT processor from the command line."""
    parser = argparse.ArgumentParser(description='STT Processor - speech recognition from audio files')
    parser.add_argument('--file', '-f', required=True, help='Path to the audio file')
    parser.add_argument('--language', '-l', default='ru-RU', help='Language code (default: ru-RU)')
    parser.add_argument('--provider', '-p', help='STT provider name')
    parser.add_argument('--config', '-c', help='Path to the configuration file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        processor = STTProcessor(args.config)

        config_info = processor.get_config_info()
        print(f"Provider: {config_info['default_provider']}, language: {config_info['default_language']}")

        recognized_text = processor.process_voice_message(args.file, args.language, args.provider)
        print(f"Result: {recognized_text}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
