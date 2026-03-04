#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Abstract base class for STT providers.

This module defines the interface that all STT providers must implement:
- Speech recognition from audio files
- Configuration validation
- Supported formats listing
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseSTTProvider(ABC):
    """
    Abstract base class for all STT providers.

    Defines the common interface that all concrete speech recognition
    providers must implement.
    """

    # Provider name — must be overridden in subclasses
    name: str = "base_provider"

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the provider with configuration.

        Args:
            config: Provider configuration dictionary
        """
        self.config = config

    def get_name(self) -> str:
        """
        Return the provider name.

        Returns:
            str: Provider name
        """
        return self.name

    @abstractmethod
    def recognize(self, audio_file_path: str, language: str = "ru-RU") -> str:
        """
        Recognize speech from an audio file.

        Args:
            audio_file_path: Path to the audio file
            language: Language code (default: "ru-RU")

        Returns:
            str: Recognized text

        Raises:
            NotImplementedError: Must be implemented in subclasses
        """
        pass

    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """
        Get the list of supported audio formats.

        Returns:
            List[str]: List of supported formats

        Raises:
            NotImplementedError: Must be implemented in subclasses
        """
        pass

    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate the provider configuration.

        Args:
            config: Configuration to validate

        Returns:
            bool: True if the configuration is valid, False otherwise

        Raises:
            NotImplementedError: Must be implemented in subclasses
        """
        pass

    @property
    def config(self) -> Dict[str, Any]:
        """
        Get the provider configuration.

        Returns:
            Dict[str, Any]: Provider configuration
        """
        return self._config

    @config.setter
    def config(self, value: Dict[str, Any]) -> None:
        """
        Set the provider configuration.

        Args:
            value: New configuration
        """
        self._config = value

    @property
    def provider_name(self) -> str:
        """
        Get the provider name (alias for name).

        Returns:
            str: Provider name
        """
        return self.name
