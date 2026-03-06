#!/usr/bin/env python3
"""
从 URL 下载 TRTC 场景配置 Excel、巡检结果 Excel 和代码压缩包，并解压代码。

用法:
  python3 download_files.py \
    --config-url "场景配置Excel的URL" \
    --inspect-url "巡检结果Excel的URL" \
    --code-url "代码压缩包的URL" \
    --output-dir "./workspace"

  每个 URL 参数也可以传本地文件路径（自动识别），此时会跳过下载直接复制。

输出: JSON 格式，包含各文件的本地路径。
"""

import argparse
import json
import os
import shutil
import sys
import tempfile
import zipfile
import tarfile
from urllib.parse import urlparse, unquote

try:
    import requests
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests', '-q'])
    import requests


def is_url(path):
    """判断是否为 URL（而非本地路径）。"""
    parsed = urlparse(path)
    return parsed.scheme in ('http', 'https')


def guess_filename_from_url(url):
    """从 URL 中提取文件名。"""
    parsed = urlparse(url)
    path = unquote(parsed.path)
    basename = os.path.basename(path)
    if basename:
        return basename
    return None


def download_file(url, dest_path, timeout=120):
    """下载文件到指定路径。"""
    print(f"正在下载: {url}", file=sys.stderr)
    resp = requests.get(url, timeout=timeout, stream=True, allow_redirects=True)
    resp.raise_for_status()

    # 尝试从 Content-Disposition 获取文件名
    content_disp = resp.headers.get('Content-Disposition', '')
    if 'filename=' in content_disp:
        import re
        fname_match = re.search(r'filename\*?=(?:UTF-8\'\')?["\']?([^"\';]+)', content_disp)
        if fname_match:
            original_name = unquote(fname_match.group(1).strip())
            dest_dir = os.path.dirname(dest_path)
            _, ext = os.path.splitext(original_name)
            _, dest_ext = os.path.splitext(dest_path)
            if ext and not dest_ext:
                dest_path = dest_path + ext

    with open(dest_path, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    file_size = os.path.getsize(dest_path)
    print(f"下载完成: {dest_path} ({file_size} bytes)", file=sys.stderr)
    return dest_path


def copy_local_file(src, dest):
    """复制本地文件。"""
    if os.path.isfile(src):
        shutil.copy2(src, dest)
        print(f"复制本地文件: {src} -> {dest}", file=sys.stderr)
        return dest
    elif os.path.isdir(src):
        if os.path.exists(dest):
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
        print(f"复制本地目录: {src} -> {dest}", file=sys.stderr)
        return dest
    else:
        raise FileNotFoundError(f"本地文件不存在: {src}")


def extract_archive(archive_path, dest_dir):
    """解压压缩包（支持 zip 和 tar.gz）。"""
    os.makedirs(dest_dir, exist_ok=True)

    if zipfile.is_zipfile(archive_path):
        print(f"解压 ZIP: {archive_path} -> {dest_dir}", file=sys.stderr)
        with zipfile.ZipFile(archive_path, 'r') as zf:
            zf.extractall(dest_dir)
    elif tarfile.is_tarfile(archive_path):
        print(f"解压 TAR: {archive_path} -> {dest_dir}", file=sys.stderr)
        with tarfile.open(archive_path, 'r:*') as tf:
            tf.extractall(dest_dir)
    else:
        raise ValueError(f"不支持的压缩格式: {archive_path}")

    # 如果解压后只有一个顶层目录，提升到 dest_dir 层级
    entries = os.listdir(dest_dir)
    if len(entries) == 1:
        single_entry = os.path.join(dest_dir, entries[0])
        if os.path.isdir(single_entry):
            # 将子目录内容提升
            for item in os.listdir(single_entry):
                src = os.path.join(single_entry, item)
                dst = os.path.join(dest_dir, item)
                shutil.move(src, dst)
            os.rmdir(single_entry)

    print(f"解压完成: {dest_dir}", file=sys.stderr)
    return dest_dir


def fetch_file(source, dest_path, file_desc="文件"):
    """统一处理 URL 下载或本地文件复制。"""
    if not source:
        return None

    if is_url(source):
        try:
            return download_file(source, dest_path)
        except Exception as e:
            print(f"下载{file_desc}失败: {e}", file=sys.stderr)
            return None
    else:
        # 本地路径
        try:
            return copy_local_file(source, dest_path)
        except Exception as e:
            print(f"复制{file_desc}失败: {e}", file=sys.stderr)
            return None


def download_and_extract(config_url=None, inspect_url=None, code_url=None, output_dir=None):
    """主函数：下载并解压所有资源文件。"""
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="trtc_inspector_")
    os.makedirs(output_dir, exist_ok=True)

    result = {
        "output_dir": os.path.abspath(output_dir),
        "config_excel": None,
        "inspect_excel": None,
        "code_dir": None,
        "errors": []
    }

    # 1. 下载场景配置 Excel
    if config_url:
        config_path = os.path.join(output_dir, "config.xlsx")
        downloaded = fetch_file(config_url, config_path, "场景配置 Excel")
        if downloaded:
            result["config_excel"] = os.path.abspath(downloaded)
        else:
            result["errors"].append(f"场景配置 Excel 获取失败: {config_url}")

    # 2. 下载巡检结果 Excel
    if inspect_url:
        inspect_path = os.path.join(output_dir, "inspect.xlsx")
        downloaded = fetch_file(inspect_url, inspect_path, "巡检结果 Excel")
        if downloaded:
            result["inspect_excel"] = os.path.abspath(downloaded)
        else:
            result["errors"].append(f"巡检结果 Excel 获取失败: {inspect_url}")

    # 3. 下载代码压缩包并解压
    if code_url:
        if is_url(code_url):
            # 根据 URL 猜测扩展名
            guessed_name = guess_filename_from_url(code_url)
            if guessed_name and ('.zip' in guessed_name.lower() or '.tar' in guessed_name.lower()):
                archive_path = os.path.join(output_dir, guessed_name)
            else:
                archive_path = os.path.join(output_dir, "code_archive.zip")

            downloaded = fetch_file(code_url, archive_path, "代码压缩包")
            if downloaded:
                code_dir = os.path.join(output_dir, "code")
                try:
                    extract_archive(downloaded, code_dir)
                    result["code_dir"] = os.path.abspath(code_dir)
                except Exception as e:
                    result["errors"].append(f"代码解压失败: {e}")
            else:
                result["errors"].append(f"代码压缩包获取失败: {code_url}")
        else:
            # 本地路径
            if os.path.isdir(code_url):
                result["code_dir"] = os.path.abspath(code_url)
            elif os.path.isfile(code_url):
                code_dir = os.path.join(output_dir, "code")
                try:
                    extract_archive(code_url, code_dir)
                    result["code_dir"] = os.path.abspath(code_dir)
                except Exception as e:
                    result["errors"].append(f"代码解压失败: {e}")
            else:
                result["errors"].append(f"代码路径不存在: {code_url}")

    return result


def main():
    parser = argparse.ArgumentParser(description="下载 TRTC 巡检相关资源文件")
    parser.add_argument('--config-url', help='场景配置 Excel 的 URL 或本地路径')
    parser.add_argument('--inspect-url', help='巡检结果 Excel 的 URL 或本地路径')
    parser.add_argument('--code-url', help='代码压缩包的 URL 或本地路径/目录')
    parser.add_argument('--output-dir', default='./workspace', help='输出目录 (默认: ./workspace)')

    args = parser.parse_args()

    if not any([args.config_url, args.inspect_url, args.code_url]):
        parser.error("请至少提供一个 URL/路径参数")

    result = download_and_extract(
        config_url=args.config_url,
        inspect_url=args.inspect_url,
        code_url=args.code_url,
        output_dir=args.output_dir
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
