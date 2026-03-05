import sys
import os
import yt_dlp
from faster_whisper import WhisperModel
import json
import tqdm


def extract_audio(video_path: str) -> str:
    """从视频中提取音频"""
    import ffmpeg

    audio_path = os.path.splitext(video_path)[0] + '.wav'
    stream = ffmpeg.input(video_path)
    stream = ffmpeg.output(stream, audio_path, acodec='pcm_s16le', ar=16000)
    ffmpeg.run(stream, overwrite_output=True, quiet=True)
    return audio_path


def transcribe_audio(audio_path: str, model: WhisperModel) -> dict:
    """使用Faster Whisper转录音频

    Args:
        audio_path: 音频文件路径
        model: Faster Whisper模型
    """

    # 获取转录结果和信息
    result, info = model.transcribe(audio=audio_path)

    # 收集所有片段，带进度条
    segments = []
    with tqdm.tqdm(total=info.duration, unit="seconds", desc="Transcribing") as pbar:
        for segment in result:
            segments.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text
            })
            pbar.update(segment.end - pbar.n)

    # 获取完整文本
    text = "".join([seg["text"] for seg in segments])

    return {
        "text": text,
        "segments": segments
    }


def save_subtitle(audio_path: str, result: dict, output_folder: str, subtitle_format: str = 'txt'):
    """保存字幕文件

    Args:
        audio_path: 音频文件路径
        result: Faster Whisper 转录结果
        output_folder: 输出目录
        subtitle_format: 字幕格式，支持: txt, srt, vtt, json
    """
    # 获取不带扩展名的音频文件名
    audio_filename = os.path.splitext(os.path.basename(audio_path))[0]
    output_path = os.path.join(output_folder, f"{audio_filename}.{subtitle_format.lower()}")

    if subtitle_format.lower() == 'txt':
        # 纯文本格式：直接保存所有文本
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result['text'].strip())

    elif subtitle_format.lower() == 'json':
        # JSON格式
        import json
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    elif subtitle_format.lower() == 'srt':
        # SRT格式
        with open(output_path, 'w', encoding='utf-8') as f:
            for idx, seg in enumerate(result['segments'], 1):
                # SRT时间格式: HH:MM:SS,mmm
                start_time = format_srt_time(seg['start'])
                end_time = format_srt_time(seg['end'])
                # 清理文本，去除多余空格
                text = seg['text'].strip()
                f.write(f"{idx}\n{start_time} --> {end_time}\n{text}\n\n")

    elif subtitle_format.lower() == 'vtt':
        # VTT格式
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            for seg in result['segments']:
                # VTT时间格式: HH:MM:SS.mmm
                start_time = format_vtt_time(seg['start'])
                end_time = format_vtt_time(seg['end'])
                # 清理文本，去除多余空格
                text = seg['text'].strip()
                f.write(f"{start_time} --> {end_time}\n{text}\n\n")

    return output_path


def format_srt_time(seconds: float) -> str:
    """将秒数转换为SRT时间格式 HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def format_vtt_time(seconds: float) -> str:
    """将秒数转换为VTT时间格式 HH:MM:SS.mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def download_videos(json_input: str) -> dict:
    """
    下载视频并转录

    Args:
        json_input: JSON字符串，支持以下参数:
            - urls: 视频URL列表 (必须)
            - output: 下载保存路径 (默认: "./downloads")
            - model: Faster Whisper模型名称 (默认: "small")
            - transcribe: 是否进行转录 (默认: True)
            - subtitle_format: 字幕格式，支持: txt, srt, vtt, json (默认: "txt")
            - download_subtitle: 是否下载视频自带字幕 (默认: False)
            - overwrite_subtitle: 是否覆盖已存在的字幕文件 (默认: True)

    Returns:
        结果字典
    """
    try:
        params = json.loads(json_input)
    except json.JSONDecodeError as e:
        return {"success": False, "message": f"JSON解析失败: {str(e)}", "downloaded": [], "transcripts": []}

    urls = params.get("urls", [])
    output_path = params.get("output", "./downloads")
    model_name = params.get("model", "small")
    transcribe = params.get("transcribe", True)  # 是否进行转录
    subtitle_format = params.get("subtitle_format", "txt")  # 字幕格式
    download_subtitle = params.get("download_subtitle", False)  # 是否下载视频自带字幕
    overwrite_subtitle = params.get("overwrite_subtitle", True)  # 是否覆盖已存在的字幕文件

    if not urls:
        return {"success": False, "message": "URL列表为空", "downloaded": [], "transcripts": []}

    os.makedirs(output_path, exist_ok=True)

    downloaded = []
    video_list = []  # 存储下载后的视频信息，用于后续转录

    # ========== 第一步：下载所有视频 ==========
    print("=" * 50)
    print("开始下载视频...")
    print("=" * 50)

    with yt_dlp.YoutubeDL({}) as ydl:
        for idx, url in enumerate(urls):
            try:
                # 先获取视频信息，确定文件夹名称
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', f'video_{idx + 1}')
                # 清理文件名中的非法字符
                safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).strip()
                video_folder = os.path.join(output_path, safe_title)
                os.makedirs(video_folder, exist_ok=True)

                # 检查视频是否已存在
                video_path = ydl.prepare_filename(info)
                if os.path.exists(video_path):
                    print(f"[{video_title}] 文件已存在，跳过下载")
                    downloaded.append(url)
                    video_list.append({
                        "title": video_title,
                        "url": url,
                        "video_path": video_path,
                        "video_folder": video_folder
                    })
                    print(f"[{video_title}] 已添加到转录队列")
                    continue

                # 下载视频到对应文件夹
                ydl_opts = {
                    'outtmpl': f'{video_folder}/%(title)s.%(ext)s',
                    'format': 'bestvideo+bestaudio/best',
                    'progress_hooks': [lambda d, t=video_title: print_progress(d, t)],
                }

                # 如果需要下载视频自带的字幕
                if download_subtitle:
                    ydl_opts['writesubtitles'] = True
                    ydl_opts['subtitleslangs'] = ['zh-Hans', 'zh-CN', 'zh-TW', 'en', 'ja', 'all']
                    ydl_opts['subtitlesformat'] = subtitle_format

                def print_progress(d, title):
                    if d['status'] == 'downloading':
                        total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                        downloaded_bytes = d.get('downloaded_bytes', 0)
                        speed = d.get('speed', 0)

                        # 格式化文件大小
                        def format_size(bytes_val):
                            if bytes_val >= 1024 * 1024 * 1024:
                                return f"{bytes_val / 1024 / 1024 / 1024:.2f} GB"
                            elif bytes_val >= 1024 * 1024:
                                return f"{bytes_val / 1024 / 1024:.2f} MB"
                            elif bytes_val >= 1024:
                                return f"{bytes_val / 1024:.2f} KB"
                            else:
                                return f"{bytes_val} B"

                        speed_str = f"{speed / 1024 / 1024:.2f} MB/s" if speed else "N/A"
                        if total > 0:
                            percent = downloaded_bytes / total * 100
                            print(f"\r[{title}] {format_size(downloaded_bytes)} / {format_size(total)} ({percent:.1f}%) | 速度: {speed_str}", end='', flush=True)
                        else:
                            # 没有总大小时，只显示已下载大小和速度
                            print(f"\r[{title}] 已下载: {format_size(downloaded_bytes)} | 速度: {speed_str}", end='', flush=True)
                    elif d['status'] == 'finished':
                        total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)

                        def format_size(bytes_val):
                            if bytes_val >= 1024 * 1024 * 1024:
                                return f"{bytes_val / 1024 / 1024 / 1024:.2f} GB"
                            elif bytes_val >= 1024 * 1024:
                                return f"{bytes_val / 1024 / 1024:.2f} MB"
                            elif bytes_val >= 1024:
                                return f"{bytes_val / 1024:.2f} KB"
                            else:
                                return f"{bytes_val} B"

                        print(f"\n[{title}] 下载完成! 文件大小: {format_size(total)}")

                with yt_dlp.YoutubeDL(ydl_opts) as ydl_video:
                    ydl_video.download([url])
                    video_path = ydl_video.prepare_filename(info)

                if os.path.exists(video_path):
                    downloaded.append(url)
                    video_list.append({
                        "title": video_title,
                        "url": url,
                        "video_path": video_path,
                        "video_folder": video_folder
                    })
                    print(f"[{video_title}] 已添加到转录队列")
            except Exception as e:
                print(f"下载失败 {url}: {str(e)}")

    # ========== 第二步：转录所有视频 ==========
    if not transcribe:
        # 不需要转录，只下载视频
        print("\n" + "=" * 50)
        print("视频下载完成 (跳过转录)")
        print("=" * 50)
        return {
            "success": True,
            "message": f"成功下载 {len(downloaded)} 个视频 (跳过转录)",
            "downloaded": downloaded,
            "transcripts": []
        }

    print("\n" + "=" * 50)
    print(f"视频下载完成，开始转录 {len(video_list)} 个视频...")
    print("=" * 50)

    # 使用 Faster Whisper 加载模型
    # device: "auto" 自动选择 CUDA 或 CPU
    # compute_type: "auto" 自动选择最佳精度 (float16 for CUDA, int8 for CPU)
    model = WhisperModel(model_name, device="auto", compute_type="auto")
    transcripts = []
    for idx, video_info in enumerate(video_list):
        video_title = video_info["title"]
        url = video_info["url"]
        video_path = video_info["video_path"]
        video_folder = video_info["video_folder"]

        # 检查字幕文件是否已存在
        audio_filename = os.path.splitext(os.path.basename(video_path))[0]
        subtitle_path = os.path.join(video_folder, f"{audio_filename}.{subtitle_format.lower()}")
        if os.path.exists(subtitle_path) and not overwrite_subtitle:
            print(f"\n[{idx + 1}/{len(video_list)}] 字幕文件已存在，跳过转录: {video_title}")
            transcripts.append({
                "title": video_title,
                "url": url,
                "transcript": subtitle_path,
                "format": subtitle_format
            })
            continue

        print(f"\n[{idx + 1}/{len(video_list)}] 正在提取音频: {video_title}")
        try:
            audio_path = extract_audio(video_path)
            print(f"[{idx + 1}/{len(video_list)}] 正在转录: {video_title}")

            transcript = transcribe_audio(audio_path, model)
            print()  # 换行

            # 保存字幕文件
            print(f"[{idx + 1}/{len(video_list)}] 正在保存字幕文件...")
            transcript_filename = save_subtitle(audio_path, transcript, video_folder, subtitle_format)
            print(f"[{idx + 1}/{len(video_list)}] 字幕文件已保存")

            transcripts.append({
                "title": video_title,
                "url": url,
                "transcript": transcript_filename,
                "format": subtitle_format
            })
            print(f"[{idx + 1}/{len(video_list)}] 转录完成: {video_title}")
        except Exception as e:
            print(f"转录失败 {video_title}: {str(e)}")
            transcripts.append({
                "title": video_title,
                "url": url,
                "transcript": None,
                "error": str(e)
            })

    return {
        "success": True,
        "message": f"成功下载 {len(downloaded)} 个视频，完成 {len([t for t in transcripts if t.get('transcript')])} 个转录",
        "downloaded": downloaded,
        "transcripts": transcripts
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python video_parser.py '<JSON字符串>'")
        print()
        print("参数说明:")
        print("  urls: 视频URL列表 (必须)")
        print("  output: 下载保存路径 (默认: './downloads')")
        print("  model: Faster Whisper模型 (默认: 'small', 可选: tiny/base/small/medium/large/large-v2/large-v3/turbo)")
        print("  transcribe: 是否转录 (默认: True)")
        print("  subtitle_format: 字幕格式 (默认: 'txt', 可选: txt/srt/vtt/json)")
        print("  download_subtitle: 是否下载视频自带字幕 (默认: False)")
        print("  overwrite_subtitle: 是否覆盖已存在的字幕文件 (默认: True)")
        print()
        print('示例1 - 下载并转录: python video_parser.py \'{"urls":["URL"],"output":"./downloads"}\'')
        print('示例2 - 只下载不转录: python video_parser.py \'{"urls":["URL"],"output":"./downloads","transcribe":false}\'')
        print('示例3 - 生成SRT字幕: python video_parser.py \'{"urls":["URL"],"output":"./downloads","subtitle_format":"srt"}\'')
        print('示例4 - 下载视频自带字幕: python video_parser.py \'{"urls":["URL"],"output":"./downloads","download_subtitle":true}\'')
        print('示例5 - 不覆盖已有字幕: python video_parser.py \'{"urls":["URL"],"overwrite_subtitle":false}\'')
        sys.exit(1)

    json_input = ''.join(sys.argv[1:])
    result = download_videos(json_input)
    print(result['message'])
    print(result['transcripts'])