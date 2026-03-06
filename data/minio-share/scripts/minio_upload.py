#!/usr/bin/env python3
"""
MinIO 文件上传脚本
从环境变量读取配置，上传文件到 MinIO 并生成分享链接
支持自定义文件名（处理特殊字符）和 Markdown 格式输出
"""

import os
import sys
import argparse
import re
import urllib3
from datetime import timedelta
from urllib.parse import urljoin, quote

try:
    from minio import Minio
    from minio.error import S3Error
except ImportError:
    print("Error: minio Python package not installed.", file=sys.stderr)
    print("Install with: pip install minio", file=sys.stderr)
    sys.exit(1)


def sanitize_filename(title, max_length=100):
    """
    清理文件名中的特殊字符
    - 替换非法字符为下划线
    - 限制长度
    - 保留中文、英文、数字、常见符号
    """
    if not title:
        return None
    
    # 移除或替换非法字符
    # Windows 非法字符: < > : " / \ | ? *
    # Unix 非法字符: /
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', title)
    
    # 替换连续的空格和下划线
    sanitized = re.sub(r'[\s_]+', '_', sanitized)
    
    # 移除首尾的空格和下划线
    sanitized = sanitized.strip(' _')
    
    # 限制长度
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rsplit('_', 1)[0]
    
    return sanitized if sanitized else "file"


def get_env_config():
    """从环境变量读取 MinIO 配置"""
    config = {
        'api_url': os.getenv('MINIO_API_URL'),
        'console_url': os.getenv('MINIO_CONSOLE_URL'),
        'access_key': os.getenv('MINIO_ACCESS_KEY'),
        'secret_key': os.getenv('MINIO_SECRET_KEY'),
        'bucket': os.getenv('MINIO_BUCKET'),
    }
    
    missing = [k for k, v in config.items() if not v]
    if missing:
        print(f"Error: Missing environment variables: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)
    
    return config


def parse_endpoint(api_url):
    """解析 API URL 获取 endpoint 和 secure 标志"""
    api_url = api_url.rstrip('/')
    if api_url.startswith('https://'):
        secure = True
        endpoint = api_url.replace('https://', '', 1)
    elif api_url.startswith('http://'):
        secure = False
        endpoint = api_url.replace('http://', '', 1)
    else:
        # 默认 https
        secure = True
        endpoint = api_url
    
    return endpoint, secure


def get_file_extension(file_path):
    """获取文件扩展名"""
    return os.path.splitext(file_path)[1].lower()


def get_content_type(file_path):
    """根据文件扩展名获取 Content-Type"""
    ext = get_file_extension(file_path)
    content_types = {
        # 图片
        '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
        '.gif': 'image/gif', '.webp': 'image/webp', '.bmp': 'image/bmp',
        '.svg': 'image/svg+xml',
        # 视频
        '.mp4': 'video/mp4', '.webm': 'video/webm', '.mov': 'video/quicktime',
        '.avi': 'video/x-msvideo', '.mkv': 'video/x-matroska',
        # 音频
        '.mp3': 'audio/mpeg', '.wav': 'audio/wav', '.m4a': 'audio/mp4',
        # 文档
        '.pdf': 'application/pdf', '.txt': 'text/plain',
    }
    return content_types.get(ext, 'application/octet-stream')


def upload_file(client, bucket, file_path, object_name=None, expiry_days=7):
    """上传文件到 MinIO，设置为 inline 模式以便浏览器预览"""
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    
    if not object_name:
        object_name = os.path.basename(file_path)
    
    # 确保 bucket 存在
    if not client.bucket_exists(bucket):
        print(f"Error: Bucket '{bucket}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    # 获取 Content-Type
    content_type = get_content_type(file_path)
    
    # 上传文件，设置 Content-Disposition: inline 以便浏览器直接预览
    try:
        client.fput_object(
            bucket, 
            object_name, 
            file_path,
            content_type=content_type,
            metadata={'Content-Disposition': 'inline'}
        )
    except S3Error as e:
        print(f"Error uploading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    return object_name


def generate_presigned_url(client, bucket, object_name, expiry_days=7):
    """生成预签名 URL"""
    try:
        url = client.presigned_get_object(
            bucket, 
            object_name,
            expires=timedelta(days=expiry_days)
        )
        return url
    except S3Error as e:
        print(f"Error generating URL: {e}", file=sys.stderr)
        sys.exit(1)


def generate_console_url(console_url, bucket, object_name):
    """生成 Console 预览 URL"""
    # 对 object_name 进行 URL 编码
    encoded_object = quote(object_name, safe='/')
    return f"{console_url.rstrip('/')}/browser/{bucket}/{encoded_object}"


def main():
    parser = argparse.ArgumentParser(description='Upload file to MinIO and generate shareable link')
    parser.add_argument('file_path', help='Path to the file to upload')
    parser.add_argument('--name', '-n', help='Object name in MinIO (default: filename)')
    parser.add_argument('--title', '-t', help='Video/article title to use as filename')
    parser.add_argument('--expiry', '-e', type=int, default=7, help='Link expiry in days (default: 7)')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    parser.add_argument('--insecure', '-k', action='store_true', help='Skip SSL certificate verification')
    
    args = parser.parse_args()
    
    # 确定 object_name
    if args.title:
        # 使用标题作为文件名，保留原始扩展名
        ext = get_file_extension(args.file_path)
        sanitized_title = sanitize_filename(args.title)
        object_name = f"{sanitized_title}{ext}"
    elif args.name:
        object_name = args.name
    else:
        object_name = None  # 使用原始文件名
    
    # 读取配置
    config = get_env_config()
    endpoint, secure = parse_endpoint(config['api_url'])
    
    # 创建自定义 HTTP 客户端（如果需要跳过 SSL 验证）
    http_client = None
    if args.insecure and secure:
        http_client = urllib3.PoolManager(
            cert_reqs='CERT_NONE',
            assert_hostname=False
        )
    
    # 创建 MinIO 客户端
    client = Minio(
        endpoint,
        access_key=config['access_key'],
        secret_key=config['secret_key'],
        secure=secure,
        http_client=http_client
    )
    
    # 上传文件
    object_name = upload_file(
        client, 
        config['bucket'], 
        args.file_path, 
        object_name,
        args.expiry
    )
    
    # 生成链接
    presigned_url = generate_presigned_url(client, config['bucket'], object_name, args.expiry)
    console_url = generate_console_url(config['console_url'], config['bucket'], object_name)
    
    # 输出结果
    if args.json:
        import json
        result = {
            'success': True,
            'object_name': object_name,
            'bucket': config['bucket'],
            'presigned_url': presigned_url,
            'console_url': console_url,
            'expiry_days': args.expiry
        }
        print(json.dumps(result, indent=2))
    else:
        print(presigned_url)


if __name__ == '__main__':
    main()
