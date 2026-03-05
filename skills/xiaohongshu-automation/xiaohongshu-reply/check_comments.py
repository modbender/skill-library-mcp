#!/usr/bin/env python3
"""
小红书评论查看和回复工具
先读取评论内容，再针对性回复第2和第3条评论
"""

import json
import os
import re
from time import sleep
from playwright.sync_api import sync_playwright

def check_recent_comments():
    """查看最近的评论"""
    cookie_path = os.path.expanduser("~/.openclaw/secrets/xiaohongshu.json")
    
    if not os.path.exists(cookie_path):
        print(f"错误: 找不到cookie文件 {cookie_path}")
        return None
    
    with open(cookie_path, 'r') as f:
        cookie_dict = json.load(f)
    
    # 转换cookie格式为playwright需要的数组格式
    cookies = []
    for name, value in cookie_dict.items():
        cookie = {
            'name': name,
            'value': value,
            'domain': '.xiaohongshu.com',
            'path': '/'
        }
        cookies.append(cookie)
    
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        
        # 添加stealth脚本（项目内置）
        stealth_path = os.path.join(os.path.dirname(__file__), '..', 'stealth.min.js')
        if os.path.exists(stealth_path):
            context.add_init_script(path=stealth_path)
        
        context.add_cookies(cookies)
        page = context.new_page()
        page.set_default_timeout(30000)
        
        try:
            # 访问通知页
            print("正在访问通知页面...")
            page.goto('https://www.xiaohongshu.com/notification')
            sleep(5)
            
            # 点击评论标签
            print("正在加载评论...")
            try:
                page.click('text=评论和@')
                sleep(3)
            except:
                pass
            
            # 提取评论内容
            print("正在提取评论内容...")
            body_text = page.text_content('body')
            
            # 保存原始内容供分析
            with open("./xhs_comments_raw.txt", "w", encoding="utf-8") as f:
                f.write(body_text)
            
            # 使用正则表达式提取评论
            comments = []
            
            # 匹配模式：用户名 + 评论了你的笔记 + 时间 + 评论内容 + 回复按钮
            pattern = r'(\w+)\s*评论了你的笔记\s*(\d+[小时分钟天]+前)\s*([^回复]+?)\s*回复'
            matches = re.findall(pattern, body_text, re.MULTILINE)
            
            for match in matches:
                username, time_ago, content = match
                content = content.strip()
                if content and len(content) > 2:  # 过滤掉太短的
                    comments.append({
                        'username': username,
                        'time': time_ago,
                        'content': content
                    })
            
            # 如果没找到，尝试更简单的匹配
            if not comments:
                # 查找包含"评论了你的笔记"的行
                lines = body_text.split('\n')
                for i, line in enumerate(lines):
                    if '评论了你的笔记' in line and i < len(lines) - 1:
                        # 下一行可能是评论内容
                        username = line.split('评论了你的笔记')[0].strip()
                        if username and not username.startswith('©'):  # 过滤掉页脚
                            comment_line = lines[i+1].strip()
                            if comment_line and '回复' not in comment_line and len(comment_line) > 5:
                                comments.append({
                                    'username': username,
                                    'time': '最近',
                                    'content': comment_line
                                })
            
            print(f"\n找到 {len(comments)} 条评论:")
            for i, comment in enumerate(comments, 1):
                print(f"\n{i}. {comment['username']} ({comment['time']})")
                print(f"   评论: {comment['content']}")
            
            browser.close()
            return comments
            
        except Exception as e:
            print(f"发生错误: {e}")
            import traceback
            traceback.print_exc()
            browser.close()
            return None

def reply_to_comments(comment_indices, replies):
    """回复指定的评论"""
    cookie_path = os.path.expanduser("~/.openclaw/secrets/xiaohongshu.json")
    
    if not os.path.exists(cookie_path):
        print(f"错误: 找不到cookie文件 {cookie_path}")
        return False
    
    with open(cookie_path, 'r') as f:
        cookie_dict = json.load(f)
    
    # 转换cookie格式
    cookies = []
    for name, value in cookie_dict.items():
        cookie = {
            'name': name,
            'value': value,
            'domain': '.xiaohongshu.com',
            'path': '/'
        }
        cookies.append(cookie)
    
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)  # 调试用，可以看到界面
        context = browser.new_context()
        
        # 添加stealth脚本（项目内置）
        stealth_path = os.path.join(os.path.dirname(__file__), '..', 'stealth.min.js')
        if os.path.exists(stealth_path):
            context.add_init_script(path=stealth_path)
        
        context.add_cookies(cookies)
        page = context.new_page()
        page.set_default_timeout(30000)
        
        try:
            # 访问通知页
            print("正在访问通知页面...")
            page.goto('https://www.xiaohongshu.com/notification')
            sleep(5)
            
            # 点击评论标签
            try:
                page.click('text=评论和@')
                sleep(3)
            except:
                pass
            
            # 获取所有回复按钮
            reply_buttons = page.get_by_text('回复', exact=True).all()
            print(f"找到 {len(reply_buttons)} 个回复按钮")
            
            # 回复指定的评论
            for i, (comment_idx, reply_text) in enumerate(zip(comment_indices, replies)):
                if comment_idx <= len(reply_buttons):
                    try:
                        print(f"正在回复第 {comment_idx} 条评论...")
                        
                        # 点击回复按钮
                        reply_buttons[comment_idx - 1].click()  # 索引从0开始
                        sleep(2)
                        
                        # 输入回复内容
                        textarea = page.locator('textarea').first
                        textarea.fill(reply_text)
                        sleep(1)
                        
                        # 点击发送
                        send_btn = page.get_by_text('发送', exact=True)
                        send_btn.click()
                        sleep(3)
                        
                        print(f"✅ 已回复第 {comment_idx} 条评论")
                        
                    except Exception as e:
                        print(f"回复第 {comment_idx} 条评论失败: {e}")
                        continue
                else:
                    print(f"第 {comment_idx} 条评论不存在")
            
            browser.close()
            return True
            
        except Exception as e:
            print(f"发生错误: {e}")
            browser.close()
            return False

if __name__ == "__main__":
    comments = check_recent_comments()
    
    if comments and len(comments) >= 3:
        print(f"\n=== 准备回复第2和第3条评论 ===")
        print(f"第2条: {comments[1]['username']} - {comments[1]['content']}")
        print(f"第3条: {comments[2]['username']} - {comments[2]['content']}")
        
        # 生成针对性回复（请根据实际评论内容修改）
        reply2 = f"@{comments[1]['username']} [请根据评论内容自定义回复]"
        reply3 = f"@{comments[2]['username']} [请根据评论内容自定义回复]"
        
        print(f"\n准备回复:")
        print(f"回复2: {reply2}")
        print(f"回复3: {reply3}")
        
        # 执行回复
        confirm = input("\n确认回复吗？(y/N): ")
        if confirm.lower() == 'y':
            reply_to_comments([2, 3], [reply2, reply3])
    elif comments and len(comments) >= 2:
        print(f"\n只有 {len(comments)} 条评论，回复第2条:")
        print(f"第2条: {comments[1]['username']} - {comments[1]['content']}")
        
        reply2 = f"@{comments[1]['username']} [请根据评论内容自定义回复]"
        print(f"准备回复: {reply2}")
        
        confirm = input("\n确认回复吗？(y/N): ")
        if confirm.lower() == 'y':
            reply_to_comments([2], [reply2])
    elif comments:
        print(f"\n只有 {len(comments)} 条评论，不足2条")
        if comments:
            print("唯一评论:")
            print(f"1. {comments[0]['username']} - {comments[0]['content']}")
    else:
        print("未能获取评论")