#!/usr/bin/env python3
"""
Video Audio Replace - Replace video audio with TTS while preserving timing
"""

import os
import sys
import argparse
import subprocess
import srt
import requests

# Default configuration
DEFAULT_VOICE_ELEVENLABS = "TX3LPaxmHKxFdv7VOQHJ"  # Liam
DEFAULT_ENGINE = "elevenlabs"

# Edge TTS voices
EDGE_VOICES = {
    "zh-CN-YunxiNeural": "zh-CN",
    "zh-CN-XiaoxiaoNeural": "zh-CN",
    "zh-CN-YunyangNeural": "zh-CN",
    "en-US-JennyNeural": "en-US",
    "en-US-GuyNeural": "en-US",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Replace video audio with TTS")
    parser.add_argument("--video", required=True, help="Input video file")
    parser.add_argument("--srt", required=True, help="SRT subtitle file")
    parser.add_argument("--output", help="Output video file")
    parser.add_argument("--voice", default=DEFAULT_VOICE_ELEVENLABS, help="Voice ID")
    parser.add_argument("--engine", default=DEFAULT_ENGINE, choices=["elevenlabs", "edge"])
    parser.add_argument("--speed-range", default="0.85-1.15", help="Speed adjustment range (e.g., 0.85-1.15)")
    return parser.parse_args()


def get_duration(filepath):
    """Get audio/video duration in seconds"""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", filepath],
        capture_output=True, text=True
    )
    return float(result.stdout.strip()) if result.stdout.strip() else 0


def generate_elevenlabs(text, output_path, voice_id, api_key):
    """Generate audio using ElevenLabs API"""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(response.content)
        return True
    print(f"ElevenLabs error: {response.status_code} - {response.text}")
    return False


def generate_edge_tts(text, output_path, voice):
    """Generate audio using Edge TTS"""
    import edge_tts
    import asyncio

    async def run():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)

    try:
        asyncio.run(run())
        return True
    except Exception as e:
        print(f"Edge TTS error: {e}")
        return False


def extract_original_audio(video_file, output_file):
    """Extract audio from video"""
    subprocess.run([
        "ffmpeg", "-y", "-i", video_file, "-vn", "-acodec", "mp3",
        "-ar", "44100", "-ac", "1", output_file
    ], capture_output=True)


def split_audio(audio_file, start_time, duration, output_file):
    """Split audio file from start_time for duration"""
    subprocess.run([
        "ffmpeg", "-y", "-i", audio_file, "-ss", str(start_time),
        "-t", str(duration), "-vn", "-acodec", "mp3", output_file
    ], capture_output=True)


def adjust_speed(input_file, output_file, speed_ratio):
    """Adjust audio speed using atempo"""
    subprocess.run([
        "ffmpeg", "-y", "-i", input_file, "-filter:a", f"atempo={speed_ratio}",
        "-vn", output_file
    ], capture_output=True)


def add_silence(duration, output_file):
    """Generate silence audio"""
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono",
        "-t", str(duration), "-q:a", "9", output_file
    ], capture_output=True)


def concat_audio(files, output_file):
    """Concatenate multiple audio files"""
    concat_list = "/tmp/concat_list.txt"
    with open(concat_list, 'w') as f:
        for file in files:
            f.write(f"file '{file}'\n")

    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
        "-c", "copy", output_file
    ], capture_output=True)
    os.remove(concat_list)


def merge_audio_with_silence(audio_file, silence_duration, output_file):
    """Merge audio with trailing silence"""
    if silence_duration <= 0.01:
        return audio_file

    silence_file = audio_file + ".silence.mp3"
    add_silence(silence_duration, silence_file)

    subprocess.run([
        "ffmpeg", "-y", "-i", audio_file, "-i", silence_file,
        "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1[out]",
        "-map", "[out]", output_file
    ], capture_output=True)
    return output_file


def replace_video_audio(video_file, audio_file, output_file):
    """Replace video audio with new audio"""
    subprocess.run([
        "ffmpeg", "-y", "-i", video_file, "-i", audio_file,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-map", "0:v:0", "-map", "1:a:0",
        "-shortest", output_file
    ], capture_output=True)


def main():
    args = parse_args()

    # Get API key
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if args.engine == "elevenlabs" and not api_key:
        print("Error: ELEVENLABS_API_KEY not set. Use --engine edge for free TTS.")
        sys.exit(1)

    # Parse speed range
    speed_min, speed_max = map(float, args.speed_range.split("-"))

    # Create temp directory
    temp_dir = "/tmp/video_audio_replace"
    os.makedirs(temp_dir, exist_ok=True)

    # Output file
    if not args.output:
        args.output = args.video.replace(".mp4", "_tts.mp4")

    print(f"Processing: {args.video}")
    print(f"Subtitles: {args.srt}")
    print(f"Engine: {args.engine}")
    print(f"Voice: {args.voice}")

    # Read subtitles
    with open(args.srt, 'r', encoding='utf-8') as f:
        subtitles = list(srt.parse(f.read()))

    print(f"Total subtitles: {len(subtitles)}")

    # Step 1: Extract original audio
    print("\n[1/5] Extracting original audio...")
    original_audio = f"{temp_dir}/original.mp3"
    extract_original_audio(args.video, original_audio)

    # Step 2: Generate TTS for each subtitle
    print("[2/5] Generating TTS audio...")
    tts_files = []
    for i, sub in enumerate(subtitles):
        text = sub.content.strip()
        if not text:
            continue

        output_file = f"{temp_dir}/tts_{i:03d}.mp3"

        if args.engine == "elevenlabs":
            success = generate_elevenlabs(text, output_file, args.voice, api_key)
        else:
            success = generate_edge_tts(text, output_file, args.voice)

        if success:
            tts_files.append((i, output_file, sub.start.total_seconds(),
                            (sub.end - sub.start).total_seconds()))
            print(f"  [{i+1}/{len(subtitles)}] Generated")
        else:
            print(f"  [{i+1}/{len(subtitles)}] Failed")

    # Step 3: Align each segment to original timing
    print("[3/5] Aligning audio segments...")

    aligned_files = []
    for i, tts_file, start_time, target_duration in tts_files:
        # Get original audio segment
        orig_file = f"{temp_dir}/orig_{i:03d}.mp3"
        split_audio(original_audio, start_time, target_duration, orig_file)
        orig_duration = get_duration(orig_file)

        # Get TTS duration
        tts_duration = get_duration(tts_file)

        # Calculate speed ratio
        if tts_duration > 0:
            speed_ratio = tts_duration / target_duration
            # Clamp to valid range
            speed_ratio = max(speed_min, min(speed_max, speed_ratio))
        else:
            speed_ratio = 1.0

        # Adjust speed
        aligned_file = f"{temp_dir}/aligned_{i:03d}.mp3"
        adjust_speed(tts_file, aligned_file, speed_ratio)
        adjusted_duration = get_duration(aligned_file)

        # Add silence to fill gap
        silence_duration = target_duration - adjusted_duration
        final_file = f"{temp_dir}/final_{i:03d}.mp3"
        merge_audio_with_silence(aligned_file, silence_duration, final_file)
        aligned_files.append(final_file)

        print(f"  Segment {i+1}: {tts_duration:.2f}s -> {adjusted_duration:.2f}s (1/{speed_ratio:.2f}x) + {silence_duration:.2f}s silence")

    # Step 4: Merge all segments
    print("[4/5] Merging audio segments...")
    merged_audio = f"{temp_dir}/merged.mp3"
    concat_audio(aligned_files, merged_audio)
    merged_duration = get_duration(merged_audio)

    # Pad to match video duration if needed
    video_duration = get_duration(args.video)
    if merged_duration < video_duration:
        final_audio = f"{temp_dir}/final_audio.mp3"
        silence_needed = video_duration - merged_duration
        print(f"  Adding {silence_needed:.2f}s silence at end...")

        silence_file = f"{temp_dir}/end_silence.mp3"
        add_silence(silence_needed, silence_file)

        subprocess.run([
            "ffmpeg", "-y", "-i", merged_audio, "-i", silence_file,
            "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1[out]",
            "-map", "[out]", final_audio
        ], capture_output=True)
    else:
        final_audio = merged_audio

    # Step 5: Replace video audio
    print("[5/5] Creating output video...")
    replace_video_audio(args.video, final_audio, args.output)

    final_duration = get_duration(args.output)
    print(f"\n✅ Done! Output: {args.output}")
    print(f"Duration: {final_duration:.2f}s")


if __name__ == "__main__":
    main()
