#!/usr/bin/env python3
"""发布文章到微信公众号"""

import sys
import os
import json
import asyncio
import httpx
import time
import re
from typing import Optional

# 微信 API 客户端
class WeChatAPI:
    def __init__(self, config_path='config.json'):
        self.config = self._load_config(config_path)
        self.access_token = None
        self.token_expiry = 0

    def _load_config(self, config_path):
        """加载配置文件"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"配置文件 {config_path} 不存在！\n"
                f"请创建配置文件并填写 AppID 和 AppSecret"
            )

        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 兼容旧版配置
        if 'accounts' not in config.get('wechat', {}):
            print("⚠️  检测到旧版配置格式")
            wechat_config = config['wechat']
            app_id = wechat_config['appId']
            app_secret = wechat_config['appSecret']

            config['wechat'] = {
                'defaultAccount': 'default',
                'accounts': {
                    'default': {
                        'name': '默认账号',
                        'appId': app_id,
                        'appSecret': app_secret,
                        'type': 'subscription',
                        'enabled': True
                    }
                },
                'apiBaseUrl': wechat_config.get('apiBaseUrl', 'https://api.weixin.qq.com'),
                'tokenCacheDir': './.tokens'
            }

        return config

    def _get_account_config(self):
        """获取当前账号配置"""
        wechat_config = self.config.get('wechat', {})
        default_account = wechat_config.get('defaultAccount', 'default')
        accounts = wechat_config.get('accounts', {})

        if default_account not in accounts:
            raise ValueError(f"默认账号 {default_account} 不存在")

        return accounts[default_account], wechat_config.get('apiBaseUrl', 'https://api.weixin.qq.com')

    async def get_access_token(self) -> str:
        """获取 Access Token（带缓存）"""
        # 检查缓存
        if self.access_token and time.time() < self.token_expiry:
            return self.access_token

        # 从文件加载
        account_config = self._get_account_config()[0]
        cache_dir = self.config['wechat'].get('tokenCacheDir', './.tokens')
        cache_file = os.path.join(cache_dir, f"token_cache.json")

        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cache = json.load(f)
                    # 提前 5 分钟刷新
                    if time.time() < cache['expires_at'] - 300:
                        self.access_token = cache['access_token']
                        self.token_expiry = cache['expires_at']
                        return self.access_token
            except Exception as e:
                print(f"⚠️  加载 token 缓存失败: {e}")

        # 从微信服务器获取
        account, base_url = self._get_account_config()
        url = f"{base_url}/cgi-bin/token"
        params = {
            'grant_type': 'client_credential',
            'appid': account['appId'],
            'secret': account['appSecret']
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, params=params)
            result = response.json()

        if 'errcode' in result:
            raise Exception(f"获取 Access Token 失败: {result['errcode']} - {result['errmsg']}")

        self.access_token = result['access_token']
        self.token_expiry = time.time() + result['expires_in']

        # 保存缓存
        os.makedirs(cache_dir, exist_ok=True)
        with open(cache_file, 'w') as f:
            json.dump({
                'access_token': self.access_token,
                'expires_at': self.token_expiry
            }, f)

        print(f"✅ Access Token 获取成功")
        return self.access_token

    async def upload_image(self, image_path: str, is_thumb: bool = False) -> dict:
        """
        上传图片素材

        Args:
            image_path: 图片文件路径
            is_thumb: True=封面图(type=thumb), False=正文图片(type=image)

        Returns:
            dict: { 'media_id': 'xxx', 'url': 'https://...' }
        """
        access_token = await self.get_access_token()
        base_url = self._get_account_config()[1]
        image_type = 'thumb' if is_thumb else 'image'
        url = f"{base_url}/cgi-bin/material/add_material?access_token={access_token}&type={image_type}"

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")

        # 检查文件大小
        file_size = os.path.getsize(image_path)
        size_limit = 64 * 1024 * 1024 if is_thumb else 2 * 1024 * 1024  # 封面64MB，正文2MB
        if file_size > size_limit:
            size_mb = size_limit / 1024 / 1024
            raise Exception(f"图片大小超过 {size_mb}MB 限制: {file_size / 1024 / 1024:.2f}MB")

        # 检查文件格式
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
        if is_thumb:
            # 封面图只支持 JPG、PNG
            allowed_extensions = ['.jpg', '.jpeg', '.png']
        file_ext = os.path.splitext(image_path)[1].lower()
        if file_ext not in allowed_extensions:
            raise Exception(f"不支持的图片格式: {file_ext}，支持的格式: {', '.join(allowed_extensions)}")

        image_type_name = "封面图" if is_thumb else "正文图片"
        print(f"📤 正在上传{image_type_name}: {os.path.basename(image_path)} ({file_size / 1024:.2f}KB)")

        async with httpx.AsyncClient(timeout=60) as client:
            with open(image_path, 'rb') as f:
                # 根据扩展名确定 MIME 类型
                mime_type = 'image/jpeg' if file_ext in ['.jpg', '.jpeg'] else 'image/png'
                files = {
                    'media': (os.path.basename(image_path), f, mime_type)
                }
                response = await client.post(url, files=files)
                result = response.json()

        if 'errcode' in result and result['errcode'] != 0:
            raise Exception(f"上传{image_type_name}失败: {result['errcode']} - {result['errmsg']}")

        media_info = {
            'media_id': result['media_id'],
            'url': result.get('url', '')
        }

        print(f"✅ {image_type_name}上传成功")
        if result.get('url'):
            print(f"   URL: {result['url']}")
        return media_info

    async def process_content_images(self, content: str, base_dir: str = '.') -> tuple[str, dict]:
        """
        处理内容中的本地图片，上传到微信并替换 src

        Args:
            content: HTML 内容
            base_dir: 图片路径的基础目录，默认为当前目录

        Returns:
            tuple: (处理后的 HTML 内容, 上传的图片信息映射)
        """
        # 查找所有 img 标签的 src 属性
        img_pattern = r'<img[^>]*src=["\']([^"\']+)["\'][^>]*>'
        matches = re.findall(img_pattern, content, re.IGNORECASE)

        if not matches:
            print("✓ 未检测到本地图片，跳过上传")
            return content, {}

        print(f"\n📷 检测到 {len(matches)} 张图片，开始处理...\n")

        uploaded_images = {}
        processed_content = content

        image_counter = 1
        for src in matches:
            # 跳过已经是 URL 的图片（http/https 开头）
            if src.startswith(('http://', 'https://')):
                print(f"  [{image_counter}] {src} - 已是 URL，跳过")
                image_counter += 1
                continue

            # 解析图片路径
            if os.path.isabs(src):
                image_path = src
            else:
                image_path = os.path.join(base_dir, src)

            try:
                # 上传图片
                result = await self.upload_image(image_path, is_thumb=False)

                # 替换 src（支持双引号和单引号）
                if result.get('url'):
                    # 替换双引号格式的 src="..."
                    processed_content = processed_content.replace(f'src="{src}"', f'src="{result["url"]}"')
                    # 替换单引号格式的 src='...'
                    processed_content = processed_content.replace(f"src='{src}'", f"src='{result['url']}'")

                    uploaded_images[os.path.basename(src)] = result
                    print(f"  [{image_counter}] {os.path.basename(src)} - 已替换为微信 URL")
                else:
                    print(f"  [{image_counter}] {os.path.basename(src)} - ⚠️ 未返回 URL，保留原始路径")

            except Exception as e:
                print(f"  [{image_counter}] {os.path.basename(src)} - ❌ 上传失败: {e}")

            image_counter += 1

        print(f"\n✓ 图片处理完成，成功上传 {len(uploaded_images)} 张\n")
        return processed_content, uploaded_images

    async def create_draft(self, title: str, content: str, thumb_media_id: str = "") -> str:
        """创建草稿"""
        access_token = await self.get_access_token()
        base_url = self._get_account_config()[1]
        url = f"{base_url}/cgi-bin/draft/add?access_token={access_token}"

        # 生成摘要（去掉 HTML 标签，取前 120 字符）
        plain_text = re.sub(r'<[^>]+>', '', content)
        digest = plain_text[:120].strip()

        article = {
            'title': title,
            'author': '作者',
            'digest': digest,
            'content': content,
            'content_source_url': '',
            'thumb_media_id': thumb_media_id,
            'need_open_comment': 1,
            'only_fans_can_comment': 0,
            'show_cover_pic': 1 if thumb_media_id else 0
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json={'articles': [article]})
            result = response.json()

        if 'errcode' in result and result['errcode'] != 0:
            raise Exception(f"创建草稿失败: {result['errcode']} - {result['errmsg']}")

        return result['media_id']


async def main(title: str, content: str, config_path: str = 'config.json', thumb_image_path: str = "", content_base_dir: str = "."):
    """主函数"""
    print("🚀 开始发布公众号文章...\n")

    try:
        api = WeChatAPI(config_path)

        # 显示当前账号
        account, _ = api._get_account_config()
        print(f"📱 使用账号: {account['name']}\n")

        print(f"📝 文章标题: {title}")
        print(f"📊 文章长度: {len(content)} 字符\n")

        # 上传封面图片
        thumb_media_id = ""
        if thumb_image_path:
            print("📷 处理封面图片...")
            thumb_result = await api.upload_image(thumb_image_path, is_thumb=True)
            thumb_media_id = thumb_result['media_id']
            print()

        # 处理正文图片
        processed_content, uploaded_images = await api.process_content_images(content, content_base_dir)

        # 创建草稿
        media_id = await api.create_draft(title, processed_content, thumb_media_id)

        print(f"✅ 草稿创建成功！")
        print(f"   草稿 ID: {media_id}")
        print(f"   上传封面: {'是' if thumb_media_id else '否'}")
        print(f"   上传正文图: {len(uploaded_images)} 张")
        print(f"   请登录微信公众号后台查看: https://mp.weixin.qq.com/\n")

        return media_id

    except FileNotFoundError as e:
        print(f"\n❌ {e}\n")
        print("💡 提示:")
        print("   1. 请确保已创建 config.json 配置文件")
        print("   2. 参考 config.example.json 模板\n")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ 发布失败: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='发布文章到微信公众号')
    parser.add_argument('title', help='文章标题')
    parser.add_argument('content', help='HTML内容或HTML文件路径')
    parser.add_argument('--config', default='config.json', help='配置文件路径 (默认: config.json)')
    parser.add_argument('--thumb', help='封面图片路径')
    parser.add_argument('--content-dir', default='.', help='正文图片的基础目录 (默认: 当前目录)')
    parser.add_argument('--from-file', action='store_true', help='从文件读取内容')

    args = parser.parse_args()

    # 如果是从文件读取
    if args.from_file:
        with open(args.content, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = args.content

    asyncio.run(main(args.title, content, args.config, args.thumb, args.content_dir))