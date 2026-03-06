#!/usr/bin/env python3
"""
视频自动剪辑脚本
使用 auto-editor 剪辑视频，支持进度通知
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# 配置：从环境变量或参数获取
CHANNEL = os.environ.get("OPENCLAW_CHANNEL", "feishu")
TARGET = os.environ.get("OPENCLAW_TARGET", "")

def check_dependencies():
    """检查并安装依赖"""
    print("🔍 检查依赖...")
    
    # 检查 auto-editor
    result = subprocess.run(["which", "auto-editor"], capture_output=True)
    if result.returncode != 0:
        print("📦 正在安装 auto-editor...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "auto-editor", "--break-system-packages"], 
                         capture_output=True)
            print("  ✅ auto-editor 安装完成")
        except Exception as e:
            print(f"  ❌ auto-editor 安装失败: {e}")
            return False
    else:
        print("  ✅ auto-editor 已安装")
    return True

# 启动前检查依赖
if not check_dependencies():
    print("❌ 依赖检查失败，请手动安装 auto-editor")
    sys.exit(1)


def send_message(message):
    """发送消息到群聊"""
    if not TARGET:
        print(f"📢 (通知未发送，未配置TARGET): {message}")
        return

    cmd = [
        "openclaw",
        "message",
        "send",
        "--channel",
        CHANNEL,
        "--target",
        TARGET,
        "--message",
        message,
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        print(f"   ⚠️ 发送消息失败: {result.stderr.decode()[:100]}")


def get_video_files(directory, exclude_pattern="已剪辑"):
    """获取目录下所有未剪辑的视频文件（递归扫描子目录）"""
    video_extensions = [".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv"]
    files = []

    if not os.path.exists(directory):
        print(f"❌ 目录不存在: {directory}")
        return files

    # 遍历所有子目录
    for root, dirs, filenames in os.walk(directory):
        # 排除已剪辑的目录
        dirs[:] = [d for d in dirs if exclude_pattern not in d]

        for f in filenames:
            # 排除已剪辑的文件
            if exclude_pattern in f:
                continue

            ext = os.path.splitext(f)[1].lower()
            if ext in video_extensions:
                full_path = os.path.join(root, f)
                # 计算相对路径（相对于输入目录根）
                rel_path = os.path.relpath(full_path, directory)
                files.append(
                    {
                        "full_path": full_path,
                        "rel_path": rel_path,  # 如 "test/1.mp4"
                        "filename": f,
                        "subdir": os.path.dirname(rel_path),  # 如 "test"
                    }
                )

    return sorted(files, key=lambda x: x["rel_path"])


def get_duration(path):
    """获取视频时长（秒）"""
    try:
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip())
    except:
        return 0


def get_size(path):
    """获取文件大小（MB）"""
    return os.path.getsize(path) / 1024 / 1024


def ensure_dir(path):
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)


def is_valid_video(path):
    """检查视频文件是否有效"""
    try:
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.returncode == 0 and float(result.stdout.strip()) > 0
    except:
        return False


def clip_video(input_info, output_root, margin, use_cache, progress_callback):
    """剪辑单个视频"""
    input_path = input_info["full_path"]
    rel_path = input_info["rel_path"]
    filename = input_info["filename"]
    subdir = input_info["subdir"]

    name_without_ext = os.path.splitext(filename)[0]
    ext = os.path.splitext(filename)[1]

    # 输出文件名：原名 + _已剪除冗余片段
    output_name = f"{name_without_ext}_已剪除冗余片段{ext}"

    # 确定缓存目录和最终输出目录
    if subdir and subdir != ".":
        final_subdir = os.path.join(output_root, subdir)
    else:
        final_subdir = output_root

    if use_cache:
        cache_root = "/tmp/video_clip_cache"
        if subdir and subdir != ".":
            cache_subdir = os.path.join(cache_root, subdir)
        else:
            cache_subdir = cache_root
        ensure_dir(cache_subdir)
        cache_path = os.path.join(cache_subdir, output_name)
    else:
        ensure_dir(final_subdir)
        cache_path = os.path.join(final_subdir, output_name)

    final_path = os.path.join(final_subdir, output_name)

    # 原文件标记：原名 + _已剪辑
    renamed_name = f"{name_without_ext}_已剪辑{ext}"
    renamed_path = os.path.join(os.path.dirname(input_path), renamed_name)

    print(f"\n📹 处理: {rel_path}")

    # 获取原始信息
    orig_duration = get_duration(input_path)
    orig_size = get_size(input_path)

    # 发送开始消息
    progress_callback("start", filename=filename)

    # 执行剪辑 - 使用 auto-editor，输出到缓存目录
    cmd = ["auto-editor", input_path, "--margin", f"{margin}sec", "-o", cache_path]

    print(f"   🔧 执行: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"   ❌ 剪辑失败: {result.stderr[-500:]}")
        progress_callback("error", filename=filename, error=result.stderr[-200:])
        return None

    # 验证输出文件是否有效
    print(f"   ✅ 验证输出文件...")
    if not is_valid_video(cache_path):
        print(f"   ❌ 输出文件无效，删除")
        if os.path.exists(cache_path):
            os.remove(cache_path)
        progress_callback("error", filename=filename, error="输出文件无效")
        return None

    # 获取剪辑后信息
    new_duration = get_duration(cache_path)
    new_size = get_size(cache_path)

    # 移动到最终目录（如果使用了缓存）
    if use_cache:
        ensure_dir(final_subdir)
        print(f"   📦 从缓存移动到最终目录...")
        import shutil

        shutil.move(cache_path, final_path)
        print(f"   ✅ 已移动到: {final_path}")

    # 只有输出文件有效，才标记原文件
    if os.path.exists(input_path):
        os.rename(input_path, renamed_path)
        print(f"   ✅ 已标记原文件: {renamed_name}")

    progress_callback(
        "success",
        filename=filename,
        orig_duration=orig_duration,
        new_duration=new_duration,
        orig_size=orig_size,
        new_size=new_size,
    )

    return {
        "rel_path": rel_path,
        "filename": filename,
        "output_name": output_name,
        "output_subdir": final_subdir,
        "orig_duration": orig_duration,
        "new_duration": new_duration,
        "orig_size": orig_size,
        "new_size": new_size,
        "renamed": renamed_name,
    }


def main():
    parser = argparse.ArgumentParser(description="视频自动剪辑脚本")
    parser.add_argument("--input", "-i", default=None, help="输入目录（必填）")
    parser.add_argument("--output", "-o", default=None, help="输出目录（必填）")
    parser.add_argument(
        "--margin", "-m", type=float, default=0.5, help="缓冲时长(秒)，默认0.5"
    )
    parser.add_argument(
        "--threshold", "-t", default="-30dB", help="静音阈值，默认-30dB"
    )
    parser.add_argument(
        "--notify", "-n", action="store_true", default=True, help="启用进度通知"
    )
    parser.add_argument("--target", "-T", default=None, help="通知目标 ID（群聊/用户）")
    parser.add_argument(
        "--cache",
        "-c",
        action="store_true",
        default=True,
        help="先输出到缓存目录再移动到目标（解决外挂硬盘写入问题），默认开启",
    )

    args = parser.parse_args()

    # 如果命令行传入了 target，覆盖环境变量
    global TARGET
    if args.target:
        TARGET = args.target

    # 检查必要参数
    if not args.input or not args.output:
        print("❌ 请指定输入和输出目录")
        print("用法: video_clip.py --input /path/to/input --output /path/to/output")
        sys.exit(1)

    # 确保输出根目录存在
    ensure_dir(args.output)

    # 扫描待剪辑文件
    video_files = get_video_files(args.input)

    if not video_files:
        print("📁 没有找到待剪辑的视频文件")
        send_message("📁 没有找到待剪辑的视频文件")
        return

    total_files = len(video_files)

    # 发送开始任务消息
    if args.notify:
        send_message(
            f"🎬 开始剪辑任务！共 {total_files} 个视频\n输入: {args.input}\n输出: {args.output}"
        )

    # 按子目录分组显示
    subdirs = set(f["subdir"] for f in video_files if f["subdir"] != ".")
    if subdirs:
        print(f"🎬 找到 {total_files} 个视频待处理，分布在 {len(subdirs)} 个子目录:")
        for sd in sorted(subdirs):
            count = len([f for f in video_files if f["subdir"] == sd])
            print(f"   - {sd}/: {count} 个视频")
    else:
        print(f"🎬 找到 {total_files} 个视频待处理")

    print(f"\n📂 输入: {args.input}")
    print(f"📂 输出: {args.output}")
    print(f"⏱️ 缓冲: {args.margin}秒")
    print("-" * 40)

    # 进度回调函数
    last_progress_percent = 0

    def progress_callback(event_type, **kwargs):
        nonlocal last_progress_percent

        if not args.notify:
            return

        current = kwargs.get("current", 0)

        if event_type == "start":
            msg = f"▶️ 开始处理: {kwargs.get('filename')}"
            send_message(msg)

        elif event_type == "progress":
            # 每 10% 发一次
            if current > 0:
                percent = int(current / total_files * 100)
                if percent >= last_progress_percent + 10:
                    msg = f"⏳ 进度: {percent}% ({current}/{total_files})"
                    send_message(msg)
                    last_progress_percent = percent

        elif event_type == "error":
            msg = f"❌ 处理失败: {kwargs.get('filename')}\n错误: {kwargs.get('error', '未知错误')}"
            send_message(msg)

        elif event_type == "success":
            orig = kwargs.get("orig_duration", 0)
            new = kwargs.get("new_duration", 0)
            reduced = orig - new
            msg = f"✅ 完成: {kwargs.get('filename')}\n时长: {orig:.0f}s → {new:.0f}s (-{reduced:.0f}s)"
            send_message(msg)

    results = []

    for i, f in enumerate(video_files, 1):
        print(f"\n[{i}/{total_files}] 🎬 开始处理", flush=True)

        # 发送进度
        progress_callback("progress", current=i)

        result = clip_video(f, args.output, args.margin, args.cache, progress_callback)
        if result:
            results.append(result)
            print(f"✅ 第 {i}/{total_files} 个完成", flush=True)

    # 汇总
    print("\n" + "=" * 50)
    print("✅ 剪辑完成！")
    print("=" * 50)
    print(f"📊 共处理: {len(results)} 个视频\n")

    # 发送完成汇总
    if args.notify and results:
        total_orig_time = sum(r["orig_duration"] for r in results)
        total_new_time = sum(r["new_duration"] for r in results)
        total_orig_size = sum(r["orig_size"] for r in results)
        total_new_size = sum(r["new_size"] for r in results)

        msg = f"""🎉 剪辑完成！

📊 共处理: {len(results)} 个视频
⏱️ 总时长: {total_orig_time:.0f}s → {total_new_time:.0f}s (-{total_orig_time - total_new_time:.0f}s)
💾 总大小: {total_orig_size:.1f}MB → {total_new_size:.1f}MB (-{total_orig_size - total_new_size:.1f}MB)

📁 输出目录: {args.output}"""
        send_message(msg)

    total_orig_time = 0
    total_new_time = 0
    total_orig_size = 0
    total_new_size = 0

    # 按子目录分组显示
    by_subdir = {}
    for r in results:
        sd = r["output_subdir"]
        if sd not in by_subdir:
            by_subdir[sd] = []
        by_subdir[sd].append(r)

    for subdir, items in by_subdir.items():
        print(f"📁 {os.path.basename(subdir)}/ ({len(items)} 个视频)")

        for r in items:
            reduced_time = r["orig_duration"] - r["new_duration"]
            reduced_size = r["orig_size"] - r["new_size"]

            print(f"   📹 {r['filename']}")
            print(
                f"      时长: {r['orig_duration']:.1f}s → {r['new_duration']:.1f}s (-{reduced_time:.1f}s)"
            )
            print(
                f"      大小: {r['orig_size']:.1f}MB → {r['new_size']:.1f}MB (-{reduced_size:.1f}MB)"
            )
            print(f"      输出: {r['output_name']}")

            total_orig_time += r["orig_duration"]
            total_new_time += r["new_duration"]
            total_orig_size += r["orig_size"]
            total_new_size += r["new_size"]
        print()

    print("-" * 40)
    print(f"📈 总计:")
    print(
        f"   时长: {total_orig_time:.1f}s → {total_new_time:.1f}s (减少 {total_orig_time - total_new_time:.1f}s)"
    )
    print(
        f"   大小: {total_orig_size:.1f}MB → {total_new_size:.1f}MB (减少 {total_orig_size - total_new_size:.1f}MB)"
    )


if __name__ == "__main__":
    main()
