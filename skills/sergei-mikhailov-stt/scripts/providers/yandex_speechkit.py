#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yandex SpeechKit provider for speech recognition.

This module implements integration with the Yandex SpeechKit API:
- Speech recognition via Yandex Cloud
- Multiple recognition model support
- API error handling
- Authentication management
"""

import os
import logging
import time
import json
from typing import Dict, Any, List, Tuple
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .base_provider import BaseSTTProvider
from audio_processor import AudioProcessor


logger = logging.getLogger(__name__)


class YandexSpeechKitProvider(BaseSTTProvider):
    """
    Yandex SpeechKit provider for speech recognition.

    Implements integration with the Yandex Cloud SpeechKit API
    for recognizing speech from audio files.
    """

    name = "yandex"

    API_URL = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"

    SUPPORTED_FORMATS = ["ogg", "wav", "mp3", "m4a", "flac", "aac"]

    # Maximum file size (1 MB — Yandex SpeechKit v1 sync API limit)
    MAX_FILE_SIZE = 1 * 1024 * 1024

    REQUEST_TIMEOUT = 30

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the Yandex SpeechKit provider.

        Args:
            config: Configuration with api_key and folder_id

        Raises:
            ValueError: If the configuration is invalid
        """
        super().__init__(config)

        if not self.validate_config(config):
            raise ValueError("Invalid Yandex SpeechKit configuration")

        self.api_key = config.get('api_key')
        self.folder_id = config.get('folder_id')
        self.model = config.get('model', 'general')
        self.lang = config.get('lang', 'ru-RU')
        self.timeout = config.get('timeout', self.REQUEST_TIMEOUT)

        try:
            self.audio_processor = AudioProcessor()
        except RuntimeError as e:
            logger.error(f"AudioProcessor initialization error: {e}")
            raise

        self.session = self._create_session()

        logger.info(f"YandexSpeechKitProvider initialized with model: {self.model}")

    def _create_session(self) -> requests.Session:
        """
        Create an HTTP session with retry settings.

        Returns:
            requests.Session: Configured HTTP session
        """
        session = requests.Session()

        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST"],
            backoff_factor=1
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate Yandex SpeechKit configuration.

        Args:
            config: Configuration to validate

        Returns:
            bool: True if the configuration is valid, False otherwise
        """
        required_fields = ['api_key', 'folder_id']

        for field in required_fields:
            if not config.get(field):
                logger.error(f"Missing required field: {field}")
                return False

        api_key = config['api_key']
        if not isinstance(api_key, str) or len(api_key) < 10:
            logger.error("Invalid API key format")
            return False

        folder_id = config['folder_id']
        if not isinstance(folder_id, str) or len(folder_id) < 1:
            logger.error("Invalid folder_id format")
            return False

        logger.info("Yandex SpeechKit configuration is valid")
        return True

    def get_supported_formats(self) -> List[str]:
        """
        Get formats supported by Yandex SpeechKit.

        Returns:
            List[str]: List of supported formats
        """
        return self.SUPPORTED_FORMATS.copy()

    def recognize(self, audio_file_path: str, language: str = "ru-RU") -> str:
        """
        Recognize speech via the Yandex SpeechKit API.

        Args:
            audio_file_path: Path to the audio file
            language: Language code (default: "ru-RU")

        Returns:
            str: Recognized text

        Raises:
            FileNotFoundError: If the audio file is not found
            ValueError: If the file format is not supported
            RuntimeError: If recognition fails
        """
        logger.info(f"Starting recognition: {audio_file_path}, language: {language}")

        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        file_ext = Path(audio_file_path).suffix.lower().lstrip('.')
        if file_ext not in self.get_supported_formats():
            raise ValueError(f"File format '{file_ext}' is not supported. Supported: {self.get_supported_formats()}")

        try:
            audio_data, audio_format = self._prepare_audio(audio_file_path)

            if len(audio_data) > self.MAX_FILE_SIZE:
                raise ValueError(
                    f"Audio size ({len(audio_data)} bytes) exceeds Yandex SpeechKit v1 limit "
                    f"({self.MAX_FILE_SIZE} bytes). Use the async API for longer recordings."
                )

            response_data = self._make_request(audio_data, language, audio_format)
            recognized_text = self._parse_response(response_data)

            logger.info(f"Recognition complete, text length: {len(recognized_text)}")
            return recognized_text

        except Exception as e:
            logger.error(f"Recognition error: {e}")
            raise

    def _prepare_audio(self, audio_file_path: str) -> Tuple[bytes, str]:
        """
        Prepare audio data for the API request.

        OGG and MP3 are sent directly without conversion.
        All other formats are converted to OGG Opus via ffmpeg.

        Args:
            audio_file_path: Path to the audio file

        Returns:
            Tuple[bytes, str]: (audio data, Yandex API format string: 'oggopus' | 'mp3')

        Raises:
            RuntimeError: If audio preparation fails
        """
        logger.debug(f"Preparing audio: {audio_file_path}")

        file_ext = Path(audio_file_path).suffix.lower().lstrip('.')

        try:
            if file_ext == 'ogg':
                # OGG Opus from Telegram — send as-is
                logger.debug("OGG file, sending without conversion")
                with open(audio_file_path, 'rb') as f:
                    return f.read(), 'oggopus'

            if file_ext == 'mp3':
                # MP3 — send as-is
                logger.debug("MP3 file, sending without conversion")
                with open(audio_file_path, 'rb') as f:
                    return f.read(), 'mp3'

            # Other formats (wav, m4a, flac, aac, etc.) — convert to OGG Opus
            logger.debug(f"Converting {file_ext} → OGG Opus")
            temp_ogg_path = self.audio_processor.generate_temp_filename(audio_file_path, "ogg")
            try:
                ogg_path = self.audio_processor.convert_to_ogg_opus(audio_file_path, temp_ogg_path)
                with open(ogg_path, 'rb') as f:
                    audio_data = f.read()
                logger.debug(f"Conversion complete, size: {len(audio_data)} bytes")
                return audio_data, 'oggopus'
            finally:
                self.audio_processor.cleanup_temp_file(temp_ogg_path)

        except Exception as e:
            error_msg = f"Audio preparation error: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _make_request(self, audio_data: bytes, language: str, audio_format: str) -> Dict[str, Any]:
        """
        Send an HTTP request to the Yandex SpeechKit API.

        Args:
            audio_data: Audio data to recognize
            language: Language code
            audio_format: Audio format for the API ('oggopus' | 'mp3' | 'lpcm')

        Returns:
            Dict[str, Any]: API response

        Raises:
            RuntimeError: If the request fails
        """
        logger.debug(f"Sending API request, audio size: {len(audio_data)} bytes, format: {audio_format}")

        headers = {
            'Authorization': f'Api-Key {self.api_key}',
            'Content-Type': 'application/octet-stream'
        }

        params = {
            'lang': language,
            'folderId': self.folder_id,
            'model': self.model,
            'format': audio_format,
        }

        # LPCM (raw PCM without header) requires sample rate
        if audio_format == 'lpcm':
            params['sampleRateHertz'] = 48000

        try:
            start_time = time.time()

            response = self.session.post(
                self.API_URL,
                headers=headers,
                params=params,
                data=audio_data,
                timeout=self.timeout
            )

            request_duration = time.time() - start_time
            logger.debug(f"Request completed in {request_duration:.2f}s, status: {response.status_code}")

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    logger.debug("API request successful")
                    return response_data
                except json.JSONDecodeError as e:
                    error_msg = f"Failed to parse API response JSON: {e}"
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)

            self._handle_api_error(response)

        except requests.exceptions.Timeout:
            error_msg = "API request timed out"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except requests.exceptions.ConnectionError:
            error_msg = "Failed to connect to the API"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"HTTP request error: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during API request: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _handle_api_error(self, response: requests.Response) -> None:
        """
        Handle an API error response.

        Args:
            response: HTTP response from the API

        Raises:
            RuntimeError: With error description
        """
        error_msg = f"API returned error: HTTP {response.status_code}"

        try:
            error_data = response.json()
            error_code = error_data.get('error_code', 'unknown')
            error_message = error_data.get('error_message', 'Unknown error')

            error_msg += f", code: {error_code}, message: {error_message}"

            if response.status_code == 401:
                error_msg += " (Check your API key)"
            elif response.status_code == 403:
                error_msg += " (Check folder access permissions)"
            elif response.status_code == 429:
                error_msg += " (Too many requests, please retry later)"
            elif response.status_code == 400:
                error_msg += " (Invalid request parameters)"

        except (json.JSONDecodeError, ValueError):
            error_msg += f", response: {response.text[:200]}"

        logger.error(error_msg)
        raise RuntimeError(error_msg)

    def _parse_response(self, response_data: Dict[str, Any]) -> str:
        """
        Parse the API response.

        Args:
            response_data: API response dictionary

        Returns:
            str: Recognized text

        Raises:
            RuntimeError: If the response format is invalid
        """
        logger.debug("Parsing API response")

        if not isinstance(response_data, dict):
            raise RuntimeError("Invalid API response format")

        if 'error_code' in response_data:
            error_code = response_data.get('error_code', 'unknown')
            error_message = response_data.get('error_message', 'Unknown error')
            error_msg = f"API returned error: {error_code} - {error_message}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        result = response_data.get('result', '')

        if not isinstance(result, str):
            error_msg = f"Invalid result format in API response: {type(result)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        logger.debug(f"Text extracted successfully, length: {len(result)}")
        return result.strip()

    def __del__(self) -> None:
        """Clean up resources when the object is deleted."""
        try:
            if hasattr(self, 'session'):
                self.session.close()
                logger.debug("HTTP session closed")
        except Exception as e:
            logger.warning(f"Error closing HTTP session: {e}")
