#!/usr/bin/env python3
"""
🦞 小龙虾多平台视频发布助手
一键上传视频到抖音、视频号、小红书、B 站、YouTube 等平台

Usage: python auto_publisher.py --video "path/to/video.mp4" --platforms all
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# 尝试导入 playwright
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  Playwright 未安装，运行：pip install playwright")
    print("⚠️  然后运行：playwright install")

class VideoPublisher:
    """多平台视频发布器"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "config/accounts.json"
        self.accounts = self.load_accounts()
        self.results = {}
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    
    def load_accounts(self) -> Dict:
        """加载账号配置"""
        config_file = Path(self.config_path)
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 创建默认配置
            default_config = {
                "douyin": {
                    "enabled": True,
                    "username": "",
                    "password": "",
                    "qr_login": True  # 使用二维码登录
                },
                "wechat_channels": {
                    "enabled": True,
                    "username": "",
                    "password": "",
                    "qr_login": True
                },
                "xiaohongshu": {
                    "enabled": True,
                    "username": "",
                    "password": "",
                    "qr_login": True
                },
                "bilibili": {
                    "enabled": True,
                    "username": "",
                    "password": "",
                    "qr_login": False
                },
                "youtube": {
                    "enabled": True,
                    "username": "",
                    "password": "",
                    "qr_login": False
                }
            }
            
            # 保存默认配置
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            
            print(f"📝 已创建默认配置文件：{config_file}")
            print("⚠️  请编辑配置文件，填写账号信息后重新运行")
            
            return default_config
    
    def save_accounts(self):
        """保存账号配置"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.accounts, f, indent=2, ensure_ascii=False)
    
    def start_browser(self, headless: bool = False):
        """启动浏览器"""
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright 未安装")
        
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.context = self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.page = self.context.new_page()
    
    def close_browser(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def login_douyin(self) -> bool:
        """登录抖音"""
        print("📱 正在登录抖音...")
        
        try:
            self.page.goto("https://creator.douyin.com/")
            time.sleep(3)
            
            # 检测是否已登录
            if "发布视频" in self.page.content():
                print("✅ 抖音已登录")
                return True
            
            # 二维码登录
            print("📱 请使用抖音 APP 扫描二维码登录")
            print("⏳ 等待扫码...（60 秒超时）")
            
            # 等待登录（检测页面变化）
            self.page.wait_for_function(
                "() => document.querySelector('.login-container') === null",
                timeout=60000
            )
            
            print("✅ 抖音登录成功")
            return True
            
        except PlaywrightTimeout:
            print("❌ 抖音登录超时")
            return False
        except Exception as e:
            print(f"❌ 抖音登录失败：{e}")
            return False
    
    def publish_douyin(self, video_path: str, title: str, tags: List[str]) -> bool:
        """发布到抖音"""
        print("📱 正在发布到抖音...")
        
        try:
            # 进入发布页面
            self.page.goto("https://creator.douyin.com/publish/")
            time.sleep(3)
            
            # 上传视频
            file_input = self.page.query_selector('input[type="file"]')
            if file_input:
                file_input.set_input_files(video_path)
                print("📹 视频上传中...")
                time.sleep(5)  # 等待上传
                
                # 填写标题
                title_input = self.page.query_selector('textarea[placeholder*="标题"]')
                if title_input:
                    full_title = f"{title} {' '.join(tags[:5])}"
                    title_input.fill(full_title[:100])  # 抖音标题限制 100 字
                    
                    # 发布
                    publish_button = self.page.query_selector('button:has-text("发布")')
                    if publish_button:
                        publish_button.click()
                        print("✅ 抖音视频已发布")
                        return True
            
            print("❌ 抖音发布失败：未找到发布按钮")
            return False
            
        except Exception as e:
            print(f"❌ 抖音发布失败：{e}")
            return False
    
    def login_wechat_channels(self) -> bool:
        """登录视频号"""
        print("💬 正在登录视频号...")
        
        try:
            self.page.goto("https://channels.weixin.qq.com/")
            time.sleep(3)
            
            # 检测是否已登录
            if "发表视频" in self.page.content():
                print("✅ 视频号已登录")
                return True
            
            # 二维码登录
            print("📱 请使用微信扫描二维码登录")
            print("⏳ 等待扫码...（60 秒超时）")
            
            self.page.wait_for_function(
                "() => document.querySelector('.login-box') === null",
                timeout=60000
            )
            
            print("✅ 视频号登录成功")
            return True
            
        except PlaywrightTimeout:
            print("❌ 视频号登录超时")
            return False
        except Exception as e:
            print(f"❌ 视频号登录失败：{e}")
            return False
    
    def publish_wechat_channels(self, video_path: str, title: str, tags: List[str]) -> bool:
        """发布到视频号"""
        print("💬 正在发布到视频号...")
        
        try:
            self.page.goto("https://channels.weixin.qq.com/publish")
            time.sleep(3)
            
            # 上传视频
            file_input = self.page.query_selector('input[type="file"]')
            if file_input:
                file_input.set_input_files(video_path)
                print("📹 视频上传中...")
                time.sleep(5)
                
                # 填写标题
                title_input = self.page.query_selector('input[placeholder*="描述"]')
                if title_input:
                    full_title = f"{title} {' '.join(tags[:3])}"
                    title_input.fill(full_title[:1000])
                    
                    # 发布
                    publish_button = self.page.query_selector('button:has-text("发表")')
                    if publish_button:
                        publish_button.click()
                        print("✅ 视频号视频已发布")
                        return True
            
            print("❌ 视频号发布失败")
            return False
            
        except Exception as e:
            print(f"❌ 视频号发布失败：{e}")
            return False
    
    def login_xiaohongshu(self) -> bool:
        """登录小红书"""
        print("📕 正在登录小红书...")
        
        try:
            self.page.goto("https://creator.xiaohongshu.com/")
            time.sleep(3)
            
            if "发布笔记" in self.page.content():
                print("✅ 小红书已登录")
                return True
            
            print("📱 请使用小红书 APP 扫描二维码登录")
            print("⏳ 等待扫码...（60 秒超时）")
            
            self.page.wait_for_function(
                "() => document.querySelector('.login-container') === null",
                timeout=60000
            )
            
            print("✅ 小红书登录成功")
            return True
            
        except PlaywrightTimeout:
            print("❌ 小红书登录超时")
            return False
        except Exception as e:
            print(f"❌ 小红书登录失败：{e}")
            return False
    
    def publish_xiaohongshu(self, video_path: str, title: str, tags: List[str]) -> bool:
        """发布到小红书"""
        print("📕 正在发布到小红书...")
        
        try:
            self.page.goto("https://creator.xiaohongshu.com/publish")
            time.sleep(3)
            
            file_input = self.page.query_selector('input[type="file"]')
            if file_input:
                file_input.set_input_files(video_path)
                print("📹 视频上传中...")
                time.sleep(5)
                
                title_input = self.page.query_selector('input[placeholder*="标题"]')
                if title_input:
                    title_input.fill(title[:20])  # 小红书标题限制 20 字
                    
                    # 填写内容
                    content = f"{title}\n\n{' '.join(tags)}"
                    content_input = self.page.query_selector('div[contenteditable="true"]')
                    if content_input:
                        content_input.fill(content[:1000])
                    
                    publish_button = self.page.query_selector('button:has-text("发布笔记")')
                    if publish_button:
                        publish_button.click()
                        print("✅ 小红书笔记已发布")
                        return True
            
            print("❌ 小红书发布失败")
            return False
            
        except Exception as e:
            print(f"❌ 小红书发布失败：{e}")
            return False
    
    def login_bilibili(self) -> bool:
        """登录 B 站"""
        print("📺 正在登录 B 站...")
        
        try:
            self.page.goto("https://member.bilibili.com/")
            time.sleep(3)
            
            if "投稿" in self.page.content():
                print("✅ B 站已登录")
                return True
            
            print("📱 请使用 B 站 APP 扫描二维码登录")
            print("⏳ 等待扫码...（60 秒超时）")
            
            self.page.wait_for_function(
                "() => document.querySelector('.login-container') === null",
                timeout=60000
            )
            
            print("✅ B 站登录成功")
            return True
            
        except PlaywrightTimeout:
            print("❌ B 站登录超时")
            return False
        except Exception as e:
            print(f"❌ B 站登录失败：{e}")
            return False
    
    def publish_bilibili(self, video_path: str, title: str, tags: List[str]) -> bool:
        """发布到 B 站"""
        print("📺 正在发布到 B 站...")
        
        try:
            self.page.goto("https://member.bilibili.com/platform/upload/video/frame")
            time.sleep(3)
            
            file_input = self.page.query_selector('input[type="file"]')
            if file_input:
                file_input.set_input_files(video_path)
                print("📹 视频上传中...")
                time.sleep(10)  # B 站上传较慢
                
                # 填写标题
                title_input = self.page.query_selector('input[placeholder*="标题"]')
                if title_input:
                    title_input.fill(title[:80])  # B 站标题限制 80 字
                    
                    # 填写标签
                    for tag in tags[:10]:  # B 站最多 10 个标签
                        tag_input = self.page.query_selector('input[placeholder*="标签"]')
                        if tag_input:
                            tag_input.fill(tag)
                            tag_input.press("Enter")
                            time.sleep(1)
                    
                    publish_button = self.page.query_selector('button:has-text("立即投稿")')
                    if publish_button:
                        publish_button.click()
                        print("✅ B 站视频已投稿")
                        return True
            
            print("❌ B 站发布失败")
            return False
            
        except Exception as e:
            print(f"❌ B 站发布失败：{e}")
            return False
    
    def login_youtube(self) -> bool:
        """登录 YouTube"""
        print("📺 正在登录 YouTube...")
        
        try:
            self.page.goto("https://studio.youtube.com/")
            time.sleep(3)
            
            if "Create" in self.page.content():
                print("✅ YouTube 已登录")
                return True
            
            print("📱 请使用 Google 账号登录")
            print("⏳ 等待登录...（60 秒超时）")
            
            self.page.wait_for_function(
                "() => document.querySelector('ytco-upload-button') !== null",
                timeout=60000
            )
            
            print("✅ YouTube 登录成功")
            return True
            
        except PlaywrightTimeout:
            print("❌ YouTube 登录超时")
            return False
        except Exception as e:
            print(f"❌ YouTube 登录失败：{e}")
            return False
    
    def publish_youtube(self, video_path: str, title: str, tags: List[str]) -> bool:
        """发布到 YouTube"""
        print("📺 正在发布到 YouTube...")
        
        try:
            self.page.goto("https://studio.youtube.com/")
            time.sleep(3)
            
            # 点击创建按钮
            create_button = self.page.query_selector('ytco-upload-button')
            if create_button:
                create_button.click()
                time.sleep(2)
                
                # 上传视频
                file_input = self.page.query_selector('input[type="file"]')
                if file_input:
                    file_input.set_input_files(video_path)
                    print("📹 视频上传中...")
                    time.sleep(10)
                    
                    # 填写标题
                    title_input = self.page.query_selector('input[placeholder*="Title"]')
                    if title_input:
                        title_input.fill(title[:100])
                        
                        # 填写描述
                        desc_input = self.page.query_selector('textarea[placeholder*="Description"]')
                        if desc_input:
                            desc_input.fill(f"{title}\n\n{' '.join(tags)}")
                        
                        # 填写标签
                        tags_input = self.page.query_selector('input[placeholder*="Tags"]')
                        if tags_input:
                            for tag in tags[:10]:
                                tags_input.fill(tag)
                                tags_input.press("Enter")
                                time.sleep(1)
                        
                        # 下一步
                        next_button = self.page.query_selector('button:has-text("Next")')
                        if next_button:
                            next_button.click()
                            time.sleep(2)
                            next_button.click()
                            time.sleep(2)
                            next_button.click()
                            time.sleep(2)
                            
                            # 发布
                            publish_button = self.page.query_selector('button:has-text("Publish")')
                            if publish_button:
                                publish_button.click()
                                print("✅ YouTube 视频已发布")
                                return True
            
            print("❌ YouTube 发布失败")
            return False
            
        except Exception as e:
            print(f"❌ YouTube 发布失败：{e}")
            return False
    
    def publish(self, video_path: str, title: str, tags: List[str], 
                platforms: List[str] = None, headless: bool = False) -> Dict:
        """发布视频到多个平台"""
        
        video_path = Path(video_path)
        if not video_path.exists():
            print(f"❌ 视频文件不存在：{video_path}")
            return {"success": False, "error": "File not found"}
        
        if platforms is None or platforms == ['all']:
            platforms = list(self.accounts.keys())
        
        print(f"\n🦞 小龙虾发布助手")
        print(f"=" * 60)
        print(f"视频：{video_path.name}")
        print(f"标题：{title}")
        print(f"平台：{', '.join(platforms)}")
        print(f"=" * 60)
        
        # 启动浏览器
        self.start_browser(headless=headless)
        
        try:
            for platform in platforms:
                if not self.accounts.get(platform, {}).get('enabled', True):
                    print(f"⏭️  跳过 {platform}（已禁用）")
                    continue
                
                print(f"\n{'='*60}")
                print(f"📍 平台：{platform}")
                print(f"{'='*60}")
                
                # 登录
                login_func = getattr(self, f'login_{platform}', None)
                if login_func:
                    if not login_func():
                        self.results[platform] = False
                        continue
                
                # 发布
                publish_func = getattr(self, f'publish_{platform}', None)
                if publish_func:
                    success = publish_func(str(video_path), title, tags)
                    self.results[platform] = success
                
                time.sleep(3)  # 平台间间隔
            
            # 总结
            print(f"\n{'='*60}")
            print(f"📊 发布结果")
            print(f"{'='*60}")
            for platform, success in self.results.items():
                status = "✅" if success else "❌"
                print(f"  {status} {platform}")
            
            return {
                "success": all(self.results.values()),
                "results": self.results,
                "timestamp": datetime.now().isoformat()
            }
            
        finally:
            self.close_browser()


def generate_caption(topic: str, style: str = 'engaging') -> str:
    """生成文案"""
    templates = {
        'engaging': [
            f"🔥 {topic} - 你觉得怎么样？",
            f"✨ AI 生成的{topic}，太震撼了！",
            f"🤖 用 AI 制作的{topic}，给几分？",
        ],
        'professional': [
            f"探索 AI 技术在{topic}中的应用",
            f"新技术实验：{topic}",
            f"AI 创新：{topic}",
        ],
        'funny': [
            f"POV: {topic} 😂",
            f"当 AI 尝试{topic}... 💀",
            f"没有人：... AI: {topic}",
        ],
    }
    
    import random
    return random.choice(templates.get(style, templates['engaging']))


def generate_hashtags(topic: str, count: int = 15) -> List[str]:
    """生成标签"""
    base_tags = ['#AI', '#AI 视频', '#人工智能', '#科技', '#创新']
    topic_tags = [f'#{topic.replace(" ", "")}', f'#{topic}AI', f'#{topic}生成']
    
    all_tags = base_tags + topic_tags
    return all_tags[:count]


def main():
    parser = argparse.ArgumentParser(description='🦞 小龙虾多平台视频发布助手')
    parser.add_argument('video', help='视频文件路径')
    parser.add_argument('--title', help='视频标题')
    parser.add_argument('--tags', help='标签（逗号分隔）')
    parser.add_argument('--platforms', default='all', 
                       help='发布平台（逗号分隔，或 all）')
    parser.add_argument('--style', default='engaging',
                       choices=['engaging', 'professional', 'funny'],
                       help='文案风格')
    parser.add_argument('--headless', action='store_true',
                       help='无头模式（不显示浏览器）')
    parser.add_argument('--config', default='config/accounts.json',
                       help='账号配置文件路径')
    
    args = parser.parse_args()
    
    # 生成文案和标签
    video_name = Path(args.video).stem
    if not args.title:
        args.title = generate_caption(video_name, args.style)
    
    if not args.tags:
        args.tags = ','.join(generate_hashtags(video_name))
    
    tags = [tag.strip() for tag in args.tags.split(',')]
    
    # 解析平台
    if args.platforms == 'all':
        platforms = None
    else:
        platforms = [p.strip() for p in args.platforms.split(',')]
    
    # 创建发布器
    publisher = VideoPublisher(config_path=args.config)
    
    # 发布
    result = publisher.publish(
        video_path=args.video,
        title=args.title,
        tags=tags,
        platforms=platforms,
        headless=args.headless
    )
    
    # 保存发布记录
    log_file = Path('config/publish_log.json')
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logs = []
    if log_file.exists():
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    
    logs.append({
        'video': str(args.video),
        'title': args.title,
        'tags': tags,
        'result': result
    })
    
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)
    
    print(f"\n📝 发布记录已保存：{log_file}")
    
    sys.exit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()
