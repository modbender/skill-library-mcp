#!/usr/bin/env python3
"""
小红书长文发布脚本
使用playwright通过创作者中心发布长文笔记
"""

import json
import os
from time import sleep
from playwright.sync_api import sync_playwright

# 使用通用路径，适配所有用户
COOKIE_PATH = os.path.expanduser("~/.openclaw/secrets/xiaohongshu.json")
STEALTH_JS_PATH = os.path.join(os.path.dirname(__file__), '..', 'stealth.min.js')  # 用户需自行配置此文件路径

def load_cookies():
    """加载cookie配置"""
    with open(COOKIE_PATH, 'r') as f:
        data = json.load(f)
    
    # 转换为playwright格式
    cookies = [
        {'name': 'a1', 'value': data.get('a1', ''), 'domain': '.xiaohongshu.com', 'path': '/'},
        {'name': 'web_session', 'value': data.get('web_session', ''), 'domain': '.xiaohongshu.com', 'path': '/'},
        {'name': 'webId', 'value': data.get('webId', ''), 'domain': '.xiaohongshu.com', 'path': '/'},
        {'name': 'websectiga', 'value': data.get('websectiga', ''), 'domain': '.xiaohongshu.com', 'path': '/'},
    ]
    
    # 添加creator相关cookie（如果有）
    creator_cookies = [
        'access-token-creator.xiaohongshu.com',
        'galaxy_creator_session_id', 
        'x-user-id-creator.xiaohongshu.com',
        'customer-sso-sid',
        'customerClientId'
    ]
    
    for key in creator_cookies:
        if key in data:
            cookies.append({
                'name': key,
                'value': data[key],
                'domain': '.xiaohongshu.com',
                'path': '/'
            })
    
    return cookies


def publish_long_text(title: str, content: str, headless: bool = True) -> dict:
    """
    发布小红书长文
    
    Args:
        title: 标题（不超过20字！）
        content: 正文内容
        headless: 是否无头模式
    
    Returns:
        dict: {'success': bool, 'url': str, 'message': str}
    """
    
    # 检查标题长度
    if len(title) > 20:
        print(f"⚠️ 标题超过20字，将被截断: {title[:20]}...")
        title = title[:20]
    
    cookies = load_cookies()
    
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context()
        context.add_init_script(path=STEALTH_JS_PATH)
        context.add_cookies(cookies)
        
        page = context.new_page()
        page.set_default_timeout(60000)
        
        try:
            print('🔍 访问创作者中心 (Pro)...')
            page.goto('https://pro.xiaohongshu.com/')
            sleep(3)
            
            print('📝 进入长文编辑...')
            page.click('text=写长文')
            sleep(2)
            page.click('text=新的创作')
            sleep(4)
            
            print('📝 填写标题和内容...')
            page.fill('textarea[placeholder="输入标题"]', title)
            editor = page.locator('[contenteditable="true"]').first
            editor.click()
            editor.fill(content)
            sleep(2)
            
            print('🎨 一键排版...')
            page.click('text=一键排版')
            sleep(3)
            
            print('➡️ 下一步...')
            page.click('button:has-text("下一步")')
            sleep(8)  # 等待图片生成
            
            print('🚀 发布...')
            page.locator('button:has-text("发布")').last.click()
            sleep(5)
            
            # 检查结果
            current_url = page.url
            success = 'published=true' in current_url
            
            browser.close()
            
            if success:
                print('🎉 发布成功！')
                return {'success': True, 'url': current_url, 'message': '发布成功'}
            else:
                print(f'❌ 发布可能失败，URL: {current_url}')
                return {'success': False, 'url': current_url, 'message': '发布结果不确定'}
                
        except Exception as e:
            browser.close()
            print(f'❌ 发布失败: {e}')
            return {'success': False, 'url': '', 'message': str(e)}


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='发布小红书长文')
    parser.add_argument('--title', required=True, help='标题（不超过20字）')
    parser.add_argument('--content', required=True, help='正文内容')
    parser.add_argument('--visible', action='store_true', help='显示浏览器窗口')
    
    args = parser.parse_args()
    
    result = publish_long_text(
        title=args.title,
        content=args.content,
        headless=not args.visible
    )
    
    print(f"结果: {result}")
