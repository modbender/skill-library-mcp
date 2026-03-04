#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audio file processing module using FFmpeg.

This module handles:
1. Audio format conversion
2. Audio normalization
3. File format and size validation
4. Audio preparation for STT providers
"""

import subprocess
import os
import logging
import tempfile
import time
import json
from pathlib import Path
from typing import Dict, Any


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudioProcessor:
    """
    Handles audio file processing using FFmpeg.

    Provides audio conversion between formats, file metadata extraction,
    and preparation of audio data for STT providers.
    """

    def __init__(self) -> None:
        """
        Initialize the audio processor.

        Raises:
            RuntimeError: If FFmpeg is not installed
        """
        self.ffmpeg_available = self.check_ffmpeg_installed()
        if not self.ffmpeg_available:
            raise RuntimeError(
                "FFmpeg not found. Please install FFmpeg to process audio. "
                "Instructions: https://ffmpeg.org/download.html"
            )
        logger.info("AudioProcessor initialized, FFmpeg is available")

    def check_ffmpeg_installed(self) -> bool:
        """
        Check whether FFmpeg is installed on the system.

        Returns:
            bool: True if FFmpeg is installed, False otherwise
        """
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                logger.info("FFmpeg found on the system")
                return True
            else:
                logger.error("FFmpeg did not respond correctly")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.error(f"FFmpeg not found: {e}")
            return False
        except Exception as e:
            logger.error(f"Error checking FFmpeg: {e}")
            return False

    def convert_to_wav(self, input_file: str, output_file: str, sample_rate: int = 48000) -> str:
        """
        Convert an audio file to WAV format.

        Args:
            input_file: Path to the input file
            output_file: Path to the output WAV file
            sample_rate: Sample rate in Hz (default: 48000)

        Returns:
            str: Path to the created WAV file

        Raises:
            FileNotFoundError: If the input file is not found
            RuntimeError: If conversion fails
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")

        logger.info(f"Converting {input_file} to WAV format")

        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        try:
            cmd = [
                'ffmpeg',
                '-i', input_file,
                '-ar', str(sample_rate),    # sample rate
                '-ac', '1',                 # mono
                '-c:a', 'pcm_s16le',        # PCM 16-bit little endian
                '-y',                       # overwrite if exists
                output_file
            ]

            logger.debug(f"Running command: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5-minute timeout
            )

            if result.returncode != 0:
                error_msg = f"FFmpeg error: {result.stderr}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

            if not os.path.exists(output_file):
                raise RuntimeError("Output file was not created")

            logger.info(f"Conversion completed: {output_file}")
            return output_file

        except subprocess.TimeoutExpired:
            error_msg = "Audio conversion timed out"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Audio conversion error: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def convert_ogg_to_wav(self, input_file: str, output_file: str = None) -> str:
        """
        Specialized conversion from OGG Opus to WAV format.

        Args:
            input_file: Path to the OGG file
            output_file: Path to the output WAV file (optional)

        Returns:
            str: Path to the created WAV file

        Raises:
            FileNotFoundError: If the input file is not found
            RuntimeError: If conversion fails
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"OGG file not found: {input_file}")

        if output_file is None:
            output_file = self.generate_temp_filename(input_file, "wav")

        logger.info(f"Converting OGG to WAV: {input_file} -> {output_file}")

        cmd = [
            'ffmpeg',
            '-i', input_file,
            '-ar', '48000',     # 48 kHz sample rate
            '-ac', '1',         # mono
            '-c:a', 'pcm_s16le',
            '-y',
            output_file
        ]

        try:
            logger.debug(f"Running OGG->WAV command: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                error_msg = f"OGG to WAV conversion error: {result.stderr}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

            if not os.path.exists(output_file):
                raise RuntimeError("WAV file was not created")

            logger.info(f"OGG successfully converted to WAV: {output_file}")
            return output_file

        except subprocess.TimeoutExpired:
            error_msg = "OGG to WAV conversion timed out"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"OGG to WAV conversion error: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def convert_to_ogg_opus(self, input_file: str, output_file: str) -> str:
        """
        Convert an audio file to OGG Opus format.

        Args:
            input_file: Path to the input file
            output_file: Path to the output OGG file

        Returns:
            str: Path to the created OGG file

        Raises:
            FileNotFoundError: If the input file is not found
            RuntimeError: If conversion fails
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")

        logger.info(f"Converting {input_file} to OGG Opus format")

        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        cmd = [
            'ffmpeg',
            '-i', input_file,
            '-ar', '48000',
            '-ac', '1',
            '-c:a', 'libopus',
            '-y',
            output_file
        ]

        try:
            logger.debug(f"Running command: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                error_msg = f"FFmpeg error: {result.stderr}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

            if not os.path.exists(output_file):
                raise RuntimeError("Output OGG file was not created")

            logger.info(f"OGG Opus conversion successful: {output_file}")
            return output_file

        except subprocess.TimeoutExpired:
            error_msg = "Audio to OGG Opus conversion timed out"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except RuntimeError:
            raise
        except Exception as e:
            error_msg = f"OGG Opus conversion error: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def get_audio_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get metadata for an audio file.

        Args:
            file_path: Path to the audio file

        Returns:
            Dict[str, Any]: Dictionary with file metadata

        Raises:
            FileNotFoundError: If the file is not found
            RuntimeError: If metadata extraction fails
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        logger.debug(f"Getting file info: {file_path}")

        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                file_path
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                error_msg = f"ffprobe error: {result.stderr}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

            probe_data = json.loads(result.stdout)

            info = {
                'file_path': file_path,
                'file_size': os.path.getsize(file_path),
                'duration': None,
                'format': None,
                'bit_rate': None,
                'sample_rate': None,
                'channels': None,
                'codec': None
            }

            if 'format' in probe_data:
                format_info = probe_data['format']
                info['duration'] = float(format_info.get('duration', 0))
                info['format'] = format_info.get('format_name', 'unknown')
                info['bit_rate'] = int(format_info.get('bit_rate', 0)) if format_info.get('bit_rate') else None

            if 'streams' in probe_data:
                for stream in probe_data['streams']:
                    if stream.get('codec_type') == 'audio':
                        info['sample_rate'] = int(stream.get('sample_rate', 0)) if stream.get('sample_rate') else None
                        info['channels'] = stream.get('channels', 0)
                        info['codec'] = stream.get('codec_name', 'unknown')
                        break

            logger.debug(f"File info retrieved: {info}")
            return info

        except subprocess.TimeoutExpired:
            error_msg = "Timed out while getting file info"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse ffprobe JSON output: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Error getting file info: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def generate_temp_filename(self, original_path: str, extension: str = "wav") -> str:
        """
        Generate a temporary filename based on the original file path.

        Args:
            original_path: Original file path
            extension: Extension for the new file

        Returns:
            str: Path to the temporary file
        """
        original_name = Path(original_path).stem
        timestamp = int(time.time())
        temp_name = f"{original_name}_{timestamp}.{extension}"

        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, "stt_audio", temp_name)

        os.makedirs(os.path.dirname(temp_path), exist_ok=True)

        logger.debug(f"Generated temp filename: {temp_path}")
        return temp_path

    def cleanup_temp_file(self, file_path: str) -> None:
        """
        Delete a temporary file.

        Args:
            file_path: Path to the file to delete
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Temp file deleted: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to delete temp file {file_path}: {e}")

    def validate_audio_file(self, file_path: str) -> bool:
        """
        Validate an audio file.

        Args:
            file_path: Path to the file to validate

        Returns:
            bool: True if the file is valid, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"File does not exist: {file_path}")
                return False

            if os.path.getsize(file_path) == 0:
                logger.error(f"File is empty: {file_path}")
                return False

            info = self.get_audio_info(file_path)

            if info['duration'] is None or info['duration'] <= 0:
                logger.error(f"Invalid audio duration: {file_path}")
                return False

            logger.info(f"File is valid: {file_path}")
            return True

        except Exception as e:
            logger.error(f"File validation error {file_path}: {e}")
            return False
