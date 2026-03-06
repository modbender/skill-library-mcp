#!/usr/bin/env python3
"""
FFmpeg 视频工具箱
支持多种视频操作：拼接、烧录字幕、格式转换、剪辑等
"""

import os
import sys
import argparse
import subprocess
import re
import glob

TARGET = None

# 支持的视频格式
VIDEO_EXTENSIONS = ['.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.m4v', '.webm', '.mpg', '.mpeg', '.3gp', '.ogv']

def send_message(msg):
    """发送消息到群聊"""
    if not TARGET:
        print(msg)
        return
    subprocess.run([
        "openclaw", "message", "send",
        "--channel", "feishu",
        "--target", TARGET,
        "--message", msg
    ], capture_output=True)

def get_video_files(directory, pattern="*"):
    """获取目录下所有视频文件"""
    files = []
    if not os.path.exists(directory):
        return files
    for f in os.listdir(directory):
        ext = os.path.splitext(f)[1].lower()
        if ext in VIDEO_EXTENSIONS:
            files.append(os.path.join(directory, f))
    return sorted(files)

def get_video_info(video_path):
    """获取视频信息"""
    cmd = ["ffprobe", "-v", "error", "-show_entries", 
           "format=duration,size,format_name", "-of", "default=noprint_wrappers=1:nokey=1", video_path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        lines = result.stdout.strip().split('\n')
        info = {}
        for line in lines:
            if '=' in line:
                key, val = line.split('=', 1)
                info[key] = val
        return info
    except:
        return {}

def find_subtitle(video_path, subtitle_dir):
    """根据视频名找对应的字幕文件"""
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    for suffix in ["_已剪除冗余片段", "_已剪辑", "_已烧录字幕"]:
        if video_name.endswith(suffix):
            video_name = video_name[:-len(suffix)]
    
    if os.path.exists(subtitle_dir):
        for f in os.listdir(subtitle_dir):
            if f.startswith(video_name) and f.endswith(".srt"):
                return os.path.join(subtitle_dir, f)
    return None

def cmd_concat(input_dir, output_file, target_id=None):
    """拼接多个视频"""
    global TARGET
    if target_id:
        TARGET = target_id
    
    video_files = get_video_files(input_dir)
    if not video_files:
        send_message("📁 没有找到视频文件")
        return False
    
    # 创建临时文件列表
    list_file = "/tmp/concat_list.txt"
    with open(list_file, "w") as f:
        for vf in video_files:
            f.write(f"file '{vf}'\n")
    
    send_message(f"🔗 开始拼接 {len(video_files)} 个视频...")
    
    cmd = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", "-y", output_file]
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in process.stdout:
        print(line, end='')
    
    process.wait()
    os.remove(list_file)
    
    if process.returncode == 0:
        send_message(f"✅ 拼接完成: {output_file}")
        return True
    else:
        send_message(f"❌ 拼接失败")
        return False

def cmd_burn(input_dir, subtitle_dir, output_dir, target_id=None):
    """烧录字幕"""
    global TARGET
    if target_id:
        TARGET = target_id
    
    video_files = get_video_files(input_dir)
    video_files = [f for f in video_files if "已烧录" not in os.path.basename(f)]
    
    if not video_files:
        send_message("📁 没有找到待烧录的视频")
        return False
    
    total = len(video_files)
    send_message(f"🎬 开始烧录字幕！共 {total} 个视频")
    
    success = 0
    for i, video_path in enumerate(video_files, 1):
        video_name = os.path.basename(video_path)
        
        subtitle_path = find_subtitle(video_path, subtitle_dir)
        if not subtitle_path:
            send_message(f"⚠️ 找不到字幕: {video_name}")
            continue
        
        name_without_ext = os.path.splitext(video_name)[0]
        ext = os.path.splitext(video_name)[1]
        output_name = name_without_ext + "_已烧录字幕" + ext
        output_path = os.path.join(output_dir, output_name)
        
        send_message(f"▶️ 烧录: {video_name}")
        
        cmd = ["ffmpeg", "-i", video_path, "-vf", f"subtitles='{subtitle_path}'", "-c:a", "copy", "-y", output_path]
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stderr:
            print(line, end='')
        
        process.wait()
        
        if process.returncode == 0:
            success += 1
            send_message(f"✅ 完成: {output_name}")
        else:
            send_message(f"❌ 失败: {video_name}")
    
    send_message(f"🎉 烧录完成！成功 {success}/{total}")
    return True

def cmd_convert(input_dir, output_dir, output_ext, target_id=None):
    """格式转换"""
    global TARGET
    if target_id:
        TARGET = target_id
    
    video_files = get_video_files(input_dir)
    if not video_files:
        send_message("📁 没有找到视频文件")
        return False
    
    total = len(video_files)
    send_message(f"🔄 开始转换格式！共 {total} 个视频 → {output_ext}")
    
    success = 0
    for video_path in video_files:
        video_name = os.path.basename(video_path)
        name_without_ext = os.path.splitext(video_name)[0]
        output_name = name_without_ext + output_ext
        output_path = os.path.join(output_dir, output_name)
        
        send_message(f"🔄 转换: {video_name} → {output_ext}")
        
        cmd = ["ffmpeg", "-i", video_path, "-c:a", "copy", "-y", output_path]
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stderr:
            print(line, end='')
        
        process.wait()
        
        if process.returncode == 0:
            success += 1
            send_message(f"✅ 完成: {output_name}")
        else:
            send_message(f"❌ 失败: {video_name}")
    
    send_message(f"🎉 转换完成！成功 {success}/{total}")
    return True

def cmd_info(input_dir):
    """查看视频信息"""
    video_files = get_video_files(input_dir)
    if not video_files:
        print("📁 没有找到视频文件")
        return
    
    print(f"\n📹 找到 {len(video_files)} 个视频:\n")
    for vf in video_files:
        info = get_video_info(vf)
        duration = float(info.get('duration', 0))
        size = int(info.get('size', 0))
        size_mb = size / 1024 / 1024
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        
        name = os.path.basename(vf)
        print(f"📄 {name}")
        print(f"   时长: {minutes}分{seconds}秒 | 大小: {size_mb:.1f}MB | 格式: {info.get('format_name', 'N/A')}")
        print()

def main():
    global TARGET
    
    parser = argparse.ArgumentParser(description="FFmpeg 视频工具箱")
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # concat 子命令
    concat_parser = subparsers.add_parser("concat", help="拼接视频")
    concat_parser.add_argument("-i", "--input", required=True, help="输入目录")
    concat_parser.add_argument("-o", "--output", required=True, help="输出文件")
    concat_parser.add_argument("-t", "--target", default=None, help="通知目标")
    
    # burn 子命令
    burn_parser = subparsers.add_parser("burn", help="烧录字幕")
    burn_parser.add_argument("-i", "--input", required=True, help="视频目录")
    burn_parser.add_argument("-s", "--subtitle", required=True, help="字幕目录")
    burn_parser.add_argument("-o", "--output", required=True, help="输出目录")
    burn_parser.add_argument("-t", "--target", default=None, help="通知目标")
    
    # convert 子命令
    convert_parser = subparsers.add_parser("convert", help="格式转换")
    convert_parser.add_argument("-i", "--input", required=True, help="输入目录")
    convert_parser.add_argument("-o", "--output", required=True, help="输出目录")
    convert_parser.add_argument("-e", "--ext", required=True, help="目标扩展名（如 .mp4, .mkv）")
    convert_parser.add_argument("-t", "--target", default=None, help="通知目标")
    
    # info 子命令
    info_parser = subparsers.add_parser("info", help="查看视频信息")
    info_parser.add_argument("-i", "--input", required=True, help="视频目录")
    
    args = parser.parse_args()
    
    TARGET = args.target or os.environ.get("OPENCLAW_TARGET")
    
    if args.command == "concat":
        cmd_concat(args.input, args.output, TARGET)
    elif args.command == "burn":
        cmd_burn(args.input, args.subtitle, args.output, TARGET)
    elif args.command == "convert":
        cmd_convert(args.input, args.output, args.ext, TARGET)
    elif args.command == "info":
        cmd_info(args.input)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
