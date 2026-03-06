"""
Video/Audio Downloader - Support online videos and local files
"""

import os
import subprocess
import json
import re
import html
from pathlib import Path
from typing import Tuple, Optional, List, Dict, Any

import yt_dlp


class Downloader:
    """Handle video and audio downloading."""

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True, parents=True)

    def get_audio(self, source: str) -> Tuple[str, dict]:
        """
        Get audio from video URL or local file.

        Returns:
            Tuple of (audio_path, video_info)
        """
        if self._is_local_file(source):
            return self._extract_audio(source)
        else:
            return self._download_audio(source)

    def get_video(self, source: str) -> Tuple[str, dict]:
        """
        Get video file from URL or local file path.

        Args:
            source: Video URL or local file path

        Returns:
            Tuple of (video_path, video_info)
            video_info contains: title, url, platform, duration
        """
        if self._is_local_file(source):
            return self._validate_local_video(source)
        else:
            return self._download_video(source)

    def get_subtitles(
        self, source: str
    ) -> Tuple[Optional[str], Optional[List[Dict[str, Any]]], Optional[Dict[str, Any]]]:
        """
        Try to get subtitles from online source.

        Returns:
            (subtitle_text, timestamped_segments, video_info)
            - subtitle_text: merged plain subtitle text
            - timestamped_segments: [{"start": float, "end": float, "text": str}, ...]
            - video_info: basic metadata from platform
        """
        if self._is_local_file(source):
            return None, None, None
        return self._download_subtitles(source)

    def _is_local_file(self, path: str) -> bool:
        """Check if source is a local file."""
        if os.path.exists(path):
            return True
        if not path.startswith(("http://", "https://")):
            return True
        return False

    def _detect_platform(self, url: str) -> str:
        """Detect video platform."""
        url_lower = url.lower()
        if "bilibili.com" in url_lower or "b23.tv" in url_lower:
            return "Bilibili"
        elif "youtube.com" in url_lower or "youtu.be" in url_lower:
            return "YouTube"
        else:
            return "Unknown"

    def _download_audio(self, url: str) -> Tuple[str, dict]:
        """Download audio from online video."""
        output_template = str(self.data_dir / "%(id)s.%(ext)s")

        ydl_opts = {
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "outtmpl": output_template,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "64",
                }
            ],
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
            "http_chunk_size": 10485760,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info.get("id", "unknown")
            title = info.get("title", "Unknown Title")
            audio_path = str(self.data_dir / f"{video_id}.mp3")

        return audio_path, {
            "title": title,
            "url": url,
            "platform": self._detect_platform(url),
            "duration": info.get("duration", 0),
        }

    def _download_subtitles(
        self, url: str
    ) -> Tuple[Optional[str], Optional[List[Dict[str, Any]]], Optional[Dict[str, Any]]]:
        """Download subtitles (manual first, then auto captions) and parse text."""
        output_template = str(self.data_dir / "%(id)s.%(ext)s")
        sublangs = [
            "zh-Hans",
            "zh-Hant",
            "zh-CN",
            "zh-TW",
            "zh",
            "en-US",
            "en-GB",
            "en",
        ]
        ydl_opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": sublangs,
            "subtitlesformat": "vtt/srt/best",
            "outtmpl": output_template,
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
            "http_chunk_size": 10485760,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
        except Exception:
            return None, None, None

        video_info = {
            "title": info.get("title", "Unknown Title"),
            "url": url,
            "platform": self._detect_platform(url),
            "duration": info.get("duration", 0),
        }

        video_id = info.get("id", "unknown")
        subtitle_file = self._find_subtitle_file(video_id)
        if subtitle_file is None:
            return None, None, video_info

        segments = self._parse_subtitle_file(subtitle_file)
        if not segments:
            return None, None, video_info

        subtitle_text = " ".join(seg["text"] for seg in segments if seg.get("text")).strip()
        if not subtitle_text:
            return None, None, video_info
        return subtitle_text, segments, video_info

    def _find_subtitle_file(self, video_id: str) -> Optional[Path]:
        """Pick the best available subtitle file downloaded by yt-dlp."""
        candidates = []
        for ext in ("vtt", "srt"):
            candidates.extend(self.data_dir.glob(f"{video_id}*.{ext}"))
        if not candidates:
            return None

        lang_priority = [
            ".zh-Hans.",
            ".zh-Hant.",
            ".zh-CN.",
            ".zh-TW.",
            ".zh.",
            ".en-US.",
            ".en-GB.",
            ".en.",
        ]
        ext_priority = {"vtt": 0, "srt": 1}

        def rank(path: Path):
            name = path.name
            lang_rank = len(lang_priority)
            for i, marker in enumerate(lang_priority):
                if marker in name:
                    lang_rank = i
                    break
            return (lang_rank, ext_priority.get(path.suffix.lstrip(".").lower(), 99), len(name))

        candidates.sort(key=rank)
        return candidates[0]

    def _parse_subtitle_file(self, path: Path) -> List[Dict[str, Any]]:
        """Parse vtt/srt subtitles to timestamped segments."""
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = path.read_text(encoding="utf-8", errors="ignore")

        lines = content.splitlines()
        segments = []
        current_start = None
        current_end = None
        current_text_lines = []

        for raw_line in lines:
            line = raw_line.strip()

            if not line:
                if current_start is not None and current_text_lines:
                    text = self._clean_subtitle_text(" ".join(current_text_lines))
                    if text:
                        segments.append(
                            {"start": current_start, "end": current_end, "text": text}
                        )
                current_start = None
                current_end = None
                current_text_lines = []
                continue

            if line.startswith("WEBVTT") or line.startswith("NOTE"):
                continue
            if line.isdigit():
                continue

            if "-->" in line:
                start_token, end_token = [x.strip() for x in line.split("-->", 1)]
                end_token = end_token.split(" ")[0].strip()
                current_start = self._parse_subtitle_time(start_token)
                current_end = self._parse_subtitle_time(end_token)
                current_text_lines = []
                continue

            if current_start is not None:
                current_text_lines.append(line)

        if current_start is not None and current_text_lines:
            text = self._clean_subtitle_text(" ".join(current_text_lines))
            if text:
                segments.append({"start": current_start, "end": current_end, "text": text})
        return segments

    def _parse_subtitle_time(self, token: str) -> float:
        """Parse subtitle timestamp string into seconds."""
        normalized = token.strip().replace(",", ".")
        parts = normalized.split(":")
        try:
            if len(parts) == 3:
                hours = float(parts[0])
                minutes = float(parts[1])
                seconds = float(parts[2])
                return hours * 3600 + minutes * 60 + seconds
            if len(parts) == 2:
                minutes = float(parts[0])
                seconds = float(parts[1])
                return minutes * 60 + seconds
            return float(parts[0])
        except ValueError:
            return 0.0

    def _clean_subtitle_text(self, text: str) -> str:
        text = re.sub(r"<[^>]+>", "", text)
        text = html.unescape(text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _extract_audio(self, video_path: str) -> Tuple[str, dict]:
        """Extract audio from local video file."""
        video_file = Path(video_path)

        # Validate
        if not video_file.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        video_extensions = {
            ".mp4",
            ".avi",
            ".mkv",
            ".mov",
            ".flv",
            ".wmv",
            ".webm",
            ".m4v",
        }
        if video_file.suffix.lower() not in video_extensions:
            raise ValueError(f"Unsupported video format: {video_file.suffix}")

        # Extract audio
        audio_path = str(self.data_dir / f"{video_file.stem}.mp3")

        cmd = [
            "ffmpeg",
            "-i",
            video_path,
            "-vn",
            "-acodec",
            "libmp3lame",
            "-ab",
            "64k",
            "-ar",
            "44100",
            "-y",
            audio_path,
        ]

        result = subprocess.run(cmd, capture_output=True, check=True)

        return audio_path, {
            "title": video_file.stem,
            "url": video_path,
            "platform": "Local",
        }

    def _download_video(self, url: str) -> Tuple[str, dict]:
        """Download video file from online source."""
        output_template = str(self.data_dir / "%(id)s.%(ext)s")

        ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "outtmpl": output_template,
            "merge_output_format": "mp4",
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
            "http_chunk_size": 10485760,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info.get("id", "unknown")
            title = info.get("title", "Unknown Title")
            duration = info.get("duration", 0)
            video_path = str(self.data_dir / f"{video_id}.mp4")

        return video_path, {
            "title": title,
            "url": url,
            "platform": self._detect_platform(url),
            "duration": duration,
        }

    def _validate_local_video(self, video_path: str) -> Tuple[str, dict]:
        """Validate local video file and return info."""
        video_file = Path(video_path)

        # Validate file exists
        if not video_file.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # Validate video extension
        video_extensions = {
            ".mp4",
            ".avi",
            ".mkv",
            ".mov",
            ".flv",
            ".wmv",
            ".webm",
            ".m4v",
        }
        if video_file.suffix.lower() not in video_extensions:
            raise ValueError(f"Unsupported video format: {video_file.suffix}")

        # Get video duration using ffprobe
        duration = self._get_video_duration(video_path)

        return str(video_file.absolute()), {
            "title": video_file.stem,
            "url": video_path,
            "platform": "Local",
            "duration": duration,
        }

    def _get_video_duration(self, video_path: str) -> float:
        """Get video duration in seconds using ffprobe."""
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            video_path,
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, check=True, text=True)
            data = json.loads(result.stdout)
            duration = float(data.get("format", {}).get("duration", 0))
            return duration
        except (subprocess.CalledProcessError, json.JSONDecodeError, ValueError):
            # Fallback: return 0 if duration cannot be determined
            return 0.0
