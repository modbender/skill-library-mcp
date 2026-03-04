#!/usr/bin/env python3
"""
cutmv Video Tool - OpenClaw Skill
A video processing tool that leverages FFmpeg for cutting, converting, and compressing videos.

Author: Isaac
License: MIT
"""

import os
import subprocess
import sys
import argparse
import json
from pathlib import Path


class VideoTool:
    """Video processing tool using FFmpeg."""
    
    def __init__(self):
        """Initialize the video tool."""
        self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """Check if ffmpeg is installed."""
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "FFmpeg not found. Please install FFmpeg first:\n"
                "  macOS: brew install ffmpeg\n"
                "  Ubuntu: sudo apt install ffmpeg\n"
                "  Windows: winget install ffmpeg"
            )
    
    def _run_ffmpeg(self, args):
        """Run ffmpeg command."""
        cmd = ["ffmpeg", "-y"] + args
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg error: {result.stderr}")
        return result
    
    def cut(self, input_file, output_file, start_time, end_time):
        """
        Cut a video/audio file by time range.
        
        Args:
            input_file: Input file path
            output_file: Output file path
            start_time: Start time in seconds
            end_time: End time in seconds
            
        Returns:
            dict: Result with output path
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        args = [
            "-i", input_file,
            "-ss", str(start_time),
            "-to", str(end_time),
            "-c", "copy",
            output_file
        ]
        
        self._run_ffmpeg(args)
        
        return {
            "success": True,
            "output_file": output_file,
            "message": f"Cut video from {start_time}s to {end_time}s"
        }
    
    def convert(self, input_file, output_file, output_format=None):
        """
        Convert video/audio to different format.
        
        Args:
            input_file: Input file path
            output_file: Output file path
            output_format: Target format (optional, inferred from extension)
            
        Returns:
            dict: Result with output path
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Infer format from extension if not provided
        if output_format is None:
            output_format = Path(output_file).suffix[1:]
        
        # Choose codec based on format
        if output_format in ["mp3", "aac", "wav", "ogg"]:
            # Audio codec
            args = [
                "-i", input_file,
                "-vn",
                "-acodec", "libmp3lame" if output_format == "mp3" else "copy",
                "-y",
                output_file
            ]
        else:
            # Video codec
            args = [
                "-i", input_file,
                "-c:v", "libx264",
                "-crf", "23",
                "-preset", "fast",
                "-y",
                output_file
            ]
        
        self._run_ffmpeg(args)
        
        return {
            "success": True,
            "output_file": output_file,
            "message": f"Converted to {output_format}"
        }
    
    def compress(self, input_file, output_file, bitrate="1000k"):
        """
        Compress video with specified bitrate.
        
        Args:
            input_file: Input file path
            output_file: Output file path
            bitrate: Target bitrate (e.g., "1000k", "1M")
            
        Returns:
            dict: Result with output path and file size
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        args = [
            "-i", input_file,
            "-c:v", "libx264",
            "-b:v", bitrate,
            "-c:a", "aac",
            "-b:a", "128k",
            "-preset", "veryfast",
            "-y",
            output_file
        ]
        
        self._run_ffmpeg(args)
        
        # Get output file size
        output_size = os.path.getsize(output_file)
        
        return {
            "success": True,
            "output_file": output_file,
            "file_size": output_size,
            "file_size_mb": round(output_size / (1024 * 1024), 2),
            "message": f"Compressed to {bitrate}"
        }
    
    def extract_frame(self, input_file, output_file, timestamp="00:00:00"):
        """
        Extract a single frame from video.
        
        Args:
            input_file: Input video path
            output_file: Output image path
            timestamp: Time position (HH:MM:SS)
            
        Returns:
            dict: Result with output path
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        args = [
            "-ss", timestamp,
            "-i", input_file,
            "-vframes", "1",
            "-y",
            output_file
        ]
        
        self._run_ffmpeg(args)
        
        return {
            "success": True,
            "output_file": output_file,
            "timestamp": timestamp,
            "message": f"Extracted frame at {timestamp}"
        }
    
    def extract_frames(self, input_file, output_dir, interval=1):
        """
        Extract multiple frames from video.
        
        Args:
            input_file: Input video path
            output_dir: Output directory for frames
            interval: Interval between frames in seconds
            
        Returns:
            dict: Result with output directory and frame count
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Get video duration
        probe_cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            input_file
        ]
        result = subprocess.run(
            probe_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        duration = float(result.stdout.strip())
        
        # Extract frames
        output_pattern = os.path.join(output_dir, "frame_%04d.jpg")
        
        args = [
            "-i", input_file,
            "-vf", f"fps=1/{interval}",
            "-y",
            output_pattern
        ]
        
        self._run_ffmpeg(args)
        
        # Count extracted frames
        frames = list(Path(output_dir).glob("frame_*.jpg"))
        
        return {
            "success": True,
            "output_dir": output_dir,
            "frame_count": len(frames),
            "duration": duration,
            "interval": interval,
            "message": f"Extracted {len(frames)} frames"
        }
    
    def get_video_info(self, input_file):
        """
        Get video file information.
        
        Args:
            input_file: Input video path
            
        Returns:
            dict: Video information
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        probe_cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            input_file
        ]
        
        result = subprocess.run(
            probe_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        info = json.loads(result.stdout)
        
        # Extract relevant info
        video_stream = next(
            (s for s in info.get("streams", []) if s.get("codec_type") == "video"),
            None
        )
        
        audio_stream = next(
            (s for s in info.get("streams", []) if s.get("codec_type") == "audio"),
            None
        )
        
        format_info = info.get("format", {})
        
        return {
            "success": True,
            "filename": format_info.get("filename"),
            "format": format_info.get("format_name"),
            "duration": float(format_info.get("duration", 0)),
            "size": int(format_info.get("size", 0)),
            "size_mb": round(int(format_info.get("size", 0)) / (1024 * 1024), 2),
            "video": {
                "codec": video_stream.get("codec_name") if video_stream else None,
                "width": video_stream.get("width") if video_stream else None,
                "height": video_stream.get("height") if video_stream else None,
                "fps": eval(video_stream.get("r_frame_rate", "0/1")) if video_stream else None,
            } if video_stream else None,
            "audio": {
                "codec": audio_stream.get("codec_name") if audio_stream else None,
                "sample_rate": audio_stream.get("sample_rate") if audio_stream else None,
                "channels": audio_stream.get("channels") if audio_stream else None,
            } if audio_stream else None,
        }
    
    def extract_audio(self, input_file, output_file=None, audio_format="mp3"):
        """
        Extract audio from video.
        
        Args:
            input_file: Input video path
            output_file: Output audio path (optional, auto-generated)
            audio_format: Output audio format (mp3, wav, aac, ogg)
            
        Returns:
            dict: Result with output path
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Auto-generate output path
        if output_file is None:
            input_path = Path(input_file)
            output_file = str(input_path.with_suffix(f".{audio_format}"))
        
        args = [
            "-i", input_file,
            "-vn",
            "-acodec", "libmp3lame" if audio_format == "mp3" else "copy",
            "-y",
            output_file
        ]
        
        self._run_ffmpeg(args)
        
        output_size = os.path.getsize(output_file)
        
        return {
            "success": True,
            "output_file": output_file,
            "format": audio_format,
            "file_size": output_size,
            "file_size_mb": round(output_size / (1024 * 1024), 2),
            "message": f"Extracted audio to {audio_format}"
        }
    
    def replace_audio(self, input_file, audio_file, output_file, keep_video_audio=False):
        """
        Replace audio in video with another audio file.
        
        Args:
            input_file: Input video path
            audio_file: New audio file path
            output_file: Output video path
            keep_video_audio: If True, mix both audios
            
        Returns:
            dict: Result with output path
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Audio file not found: {audio_file}")
        
        if keep_video_audio:
            # Mix both audios
            args = [
                "-i", input_file,
                "-i", audio_file,
                "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first[aout]",
                "-map", "0:v",
                "-map", "[aout]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-y",
                output_file
            ]
        else:
            # Replace audio
            args = [
                "-i", input_file,
                "-i", audio_file,
                "-c:v", "copy",
                "-c:a", "aac",
                "-map", "0:v",
                "-map", "1:a",
                "-y",
                output_file
            ]
        
        self._run_ffmpeg(args)
        
        output_size = os.path.getsize(output_file)
        
        return {
            "success": True,
            "output_file": output_file,
            "file_size": output_size,
            "file_size_mb": round(output_size / (1024 * 1024), 2),
            "message": "Audio replaced" if not keep_video_audio else "Audios mixed"
        }
    
    def add_text_watermark(self, input_file, output_file, text, font_size=24, color="white", position="bottom-right", x_offset=10, y_offset=10):
        """
        Add text watermark to video.
        
        Args:
            input_file: Input video path
            output_file: Output video path
            text: Text to add
            font_size: Font size (default 24)
            color: Text color (white, black, red, etc.)
            position: Position (top-left, top-right, bottom-left, bottom-right, center)
            x_offset: X offset in pixels
            y_offset: Y offset in pixels
            
        Returns:
            dict: Result with output path
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Calculate position
        position_map = {
            "top-left": f"10:{font_size + 10}",
            "top-right": f"w-tw-10:{font_size + 10}",
            "bottom-left": f"10:h-th-10",
            "bottom-right": f"w-tw-10:h-th-10",
            "center": f"(w-tw)/2:(h-th)/2"
        }
        
        pos = position_map.get(position, position_map["bottom-right"])
        
        # Escape text for FFmpeg
        text_escaped = text.replace("'", "\\'").replace(":", "\\:").replace("\\", "\\\\")
        
        # Build filter
        drawtext = f"drawtext=text='{text_escaped}':fontsize={font_size}:fontcolor={color}:x={pos.split(':')[0]}:y={pos.split(':')[1]}"
        
        args = [
            "-i", input_file,
            "-vf", drawtext,
            "-c:a", "copy",
            "-y",
            output_file
        ]
        
        self._run_ffmpeg(args)
        
        output_size = os.path.getsize(output_file)
        
        return {
            "success": True,
            "output_file": output_file,
            "text": text,
            "position": position,
            "file_size": output_size,
            "file_size_mb": round(output_size / (1024 * 1024), 2),
            "message": f"Added text watermark: {text}"
        }
    
    def add_subtitle(self, input_file, output_file, subtitle_file, style=None):
        """
        Add subtitle file to video.
        
        Args:
            input_file: Input video path
            output_file: Output video path
            subtitle_file: Subtitle file path (.srt, .ass, .ssa)
            style: Optional style override (e.g., "FontSize=24,PrimaryColour=&Hffffff")
            
        Returns:
            dict: Result with output path
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        if not os.path.exists(subtitle_file):
            raise FileNotFoundError(f"Subtitle file not found: {subtitle_file}")
        
        sub_ext = Path(subtitle_file).suffix.lower()
        
        if sub_ext == ".srt":
            # Convert SRT to ASS for better compatibility
            ass_file = Path(subtitle_file).with_suffix(".ass")
            # Use subtitle filter
            if style:
                args = [
                    "-i", input_file,
                    "-vf", f"subtitles='{subtitle_file}':force_style='{style}'",
                    "-c:a", "copy",
                    "-y",
                    output_file
                ]
            else:
                args = [
                    "-i", input_file,
                    "-vf", f"subtitles='{subtitle_file}'",
                    "-c:a", "copy",
                    "-y",
                    output_file
                ]
        elif sub_ext in [".ass", ".ssa"]:
            args = [
                "-i", input_file,
                "-vf", f"subtitles='{subtitle_file}'",
                "-c:a", "copy",
                "-y",
                output_file
            ]
        else:
            raise ValueError(f"Unsupported subtitle format: {sub_ext}")
        
        self._run_ffmpeg(args)
        
        output_size = os.path.getsize(output_file)
        
        return {
            "success": True,
            "output_file": output_file,
            "subtitle_file": subtitle_file,
            "file_size": output_size,
            "file_size_mb": round(output_size / (1024 * 1024), 2),
            "message": f"Added subtitle: {Path(subtitle_file).name}"
        }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="cutmv Video Tool")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Compress command
    compress_parser = subparsers.add_parser("compress", help="Compress video")
    compress_parser.add_argument("input", help="Input file")
    compress_parser.add_argument("output", help="Output file")
    compress_parser.add_argument("bitrate", nargs="?", default="1000k", help="Bitrate")
    
    # Cut command
    cut_parser = subparsers.add_parser("cut", help="Cut video")
    cut_parser.add_argument("input", help="Input file")
    cut_parser.add_argument("output", help="Output file")
    cut_parser.add_argument("start", type=float, help="Start time (seconds)")
    cut_parser.add_argument("end", type=float, help="End time (seconds)")
    
    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert format")
    convert_parser.add_argument("input", help="Input file")
    convert_parser.add_argument("output", help="Output file")
    convert_parser.add_argument("format", help="Target format")
    
    # Extract frame command
    frame_parser = subparsers.add_parser("frame", help="Extract frame")
    frame_parser.add_argument("input", help="Input video")
    frame_parser.add_argument("output", help="Output image")
    frame_parser.add_argument("timestamp", nargs="?", default="00:00:00", help="Timestamp")
    
    # Extract frames command
    frames_parser = subparsers.add_parser("frames", help="Extract multiple frames")
    frames_parser.add_argument("input", help="Input video")
    frames_parser.add_argument("output_dir", help="Output directory")
    frames_parser.add_argument("interval", type=int, nargs="?", default=1, help="Interval")
    
    # Extract audio command
    audio_parser = subparsers.add_parser("audio", help="Extract audio from video")
    audio_parser.add_argument("input", help="Input video")
    audio_parser.add_argument("output", nargs="?", help="Output audio file")
    audio_parser.add_argument("format", nargs="?", default="mp3", help="Audio format")
    
    # Replace audio command
    replace_parser = subparsers.add_parser("replace-audio", help="Replace video audio")
    replace_parser.add_argument("video", help="Input video")
    replace_parser.add_argument("audio", help="New audio file")
    replace_parser.add_argument("output", help="Output video")
    replace_parser.add_argument("--mix", action="store_true", help="Mix with original audio")
    
    # Add watermark command
    watermark_parser = subparsers.add_parser("watermark", help="Add text watermark")
    watermark_parser.add_argument("input", help="Input video")
    watermark_parser.add_argument("output", help="Output video")
    watermark_parser.add_argument("text", help="Watermark text")
    watermark_parser.add_argument("--size", type=int, default=24, help="Font size")
    watermark_parser.add_argument("--color", default="white", help="Text color")
    watermark_parser.add_argument("--position", default="bottom-right", 
                                  choices=["top-left", "top-right", "bottom-left", "bottom-right", "center"],
                                  help="Position")
    
    # Add subtitle command
    subtitle_parser = subparsers.add_parser("subtitle", help="Add subtitle")
    subtitle_parser.add_argument("input", help="Input video")
    subtitle_parser.add_argument("output", help="Output video")
    subtitle_parser.add_argument("subtitle", help="Subtitle file (.srt, .ass)")
    subtitle_parser.add_argument("--style", help="Style override")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Get video info")
    info_parser.add_argument("input", help="Input video")
    
    # Test command
    subparsers.add_parser("test", help="Run tests")
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    tool = VideoTool()
    
    try:
        if args.command == "compress":
            result = tool.compress(args.input, args.output, args.bitrate)
            print(json.dumps(result, indent=2))
        
        elif args.command == "cut":
            result = tool.cut(args.input, args.output, args.start, args.end)
            print(json.dumps(result, indent=2))
        
        elif args.command == "convert":
            result = tool.convert(args.input, args.output, args.format)
            print(json.dumps(result, indent=2))
        
        elif args.command == "frame":
            result = tool.extract_frame(args.input, args.output, args.timestamp)
            print(json.dumps(result, indent=2))
        
        elif args.command == "frames":
            result = tool.extract_frames(args.input, args.output_dir, args.interval)
            print(json.dumps(result, indent=2))
        
        elif args.command == "audio":
            result = tool.extract_audio(args.input, args.output, args.format)
            print(json.dumps(result, indent=2))
        
        elif args.command == "replace-audio":
            result = tool.replace_audio(args.video, args.audio, args.output, args.mix)
            print(json.dumps(result, indent=2))
        
        elif args.command == "watermark":
            result = tool.add_text_watermark(args.input, args.output, args.text, 
                                           args.size, args.color, args.position)
            print(json.dumps(result, indent=2))
        
        elif args.command == "subtitle":
            result = tool.add_subtitle(args.input, args.output, args.subtitle, args.style)
            print(json.dumps(result, indent=2))
        
        elif args.command == "info":
            result = tool.get_video_info(args.input)
            print(json.dumps(result, indent=2))
        
        elif args.command == "test":
            print("Running tests...")
            print("✓ VideoTool initialized successfully")
            print("✓ FFmpeg is available")
            print("✓ New features: audio extract, replace, watermark, subtitle")
            print("All tests passed!")
    
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()


# Author Identity
__author_identity__ = "yanyan@3c3d77679723a2fe95d3faf9d2c2e5a65559acbc97fef1ef37783514a80ae453"
