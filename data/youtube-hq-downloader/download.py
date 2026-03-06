#!/usr/bin/env python3
"""
YouTube Highest Quality Downloader
Youtube最高码率下载器 - 从YouTube下载视频最高清无声版本和纯音频，然后合并为有声视频

用法:
    python3 download.py "YouTube_URL" [输出文件名] [输出目录]
    python3 download.py "https://www.youtube.com/watch?v=xxxxx" "我的视频"
"""

import subprocess
import os
import sys
import shlex
import shutil

def run_command(cmd, cwd=None, capture=True):
    """执行shell命令"""
    print(f"🔧 执行: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=capture, text=True)
    if result.returncode != 0:
        print(f"❌ 命令执行失败: {cmd}")
        if result.stderr:
            print(f"   错误: {result.stderr}")
        return False
    return True

def check_yt_dlp():
    """检查 yt-dlp 是否已安装"""
    # 先检查系统路径 (brew安装的)
    yt_dlp_path = shutil.which("yt-dlp")
    if yt_dlp_path:
        return yt_dlp_path
    
    # 检查本地虚拟环境
    script_dir = os.path.dirname(os.path.abspath(__file__))
    local_venv = os.path.join(script_dir, ".venv", "bin", "yt-dlp")
    if os.path.exists(local_venv):
        return local_venv
    
    return None

def get_yt_dlp():
    """获取 yt-dlp 路径"""
    yt_dlp = check_yt_dlp()
    
    if yt_dlp:
        print(f"✅ 找到 yt-dlp: {yt_dlp}")
        return yt_dlp
    
    print("❌ 未找到 yt-dlp，请先安装: brew install yt-dlp")
    return None

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n用法示例:")
        print('  python3 download.py "https://www.youtube.com/watch?v=dMBW1G4U54g"')
        print('  python3 download.py "https://www.youtube.com/watch?v=dMBW1G4U54g" "MacBookAir"')
        print('  python3 download.py "https://www.youtube.com/watch?v=dMBW1G4U54g" "MacBookAir" "~/Downloads"')
        sys.exit(1)
    
    url = sys.argv[1]
    output_name = sys.argv[2] if len(sys.argv) > 2 else "merged"
    output_dir = os.path.expanduser(sys.argv[3] if len(sys.argv) > 3 else "~/Movies")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 文件路径
    video_file = os.path.join(output_dir, f"{output_name}_video.mp4")
    audio_file = os.path.join(output_dir, f"{output_name}_audio.m4a")
    output_file = os.path.join(output_dir, f"{output_name}_combined.mp4")
    
    # 获取 yt-dlp
    yt_dlp = get_yt_dlp()
    if not yt_dlp:
        sys.exit(1)
    
    print(f"\n📥 Step 1: Downloading video (highest quality)...")
    # bestvideo without ext filter to get highest quality (may be WebM)
    cmd1 = f'{yt_dlp} -f "bestvideo" "{url}" -o "{video_file}"'
    if not run_command(cmd1):
        print("❌ 视频下载失败!")
        sys.exit(1)
    
    print(f"\n📥 步骤2: 下载音频...")
    cmd2 = f'{yt_dlp} -x --audio-format m4a "{url}" -o "{audio_file}"'
    if not run_command(cmd2):
        print("❌ 音频下载失败!")
        sys.exit(1)
    
    print(f"\n🔧 Step 3: Merging video and audio...")
    # For WebM videos, need to re-encode; for MP4, can copy
    cmd3 = f'ffmpeg -i "{video_file}" -i "{audio_file}" -c:v libx264 -c:a aac -shortest "{output_file}" -y'
    if not run_command(cmd3):
        print("❌ 合并失败!")
        sys.exit(1)
    
    # 清理临时文件
    print("\n🧹 清理临时文件...")
    for f in [video_file, audio_file]:
        if os.path.exists(f):
            try:
                os.remove(f)
                print(f"   已删除: {f}")
            except:
                pass
    
    print(f"\n✅ 完成!")
    print(f"📁 输出文件: {output_file}")
    os.system(f'ls -lh "{output_file}"')

if __name__ == "__main__":
    main()
