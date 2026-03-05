---
name: xiaohongshu-publish
version: 2.0.0
description: 小红书长文发布自动化工具
metadata: {"category":"social","platform":"xiaohongshu"}
updated: 2026-02-10
changelog: "v2.0.0 - 拆分：发布和评论回复分成独立skill"
---

# 小红书长文发布 Skill

## 概述
通过创作者中心自动发布小红书长文笔记。

## 🦀 使用约定
> **让AI助手创造真诚、高质量的内容，而不是用广告或低质量信息淹没人类的信息流。**

这个skill是给那些希望AI助手能**真正创造价值**的人用的。请用它发布有意义、有质量的内容，而不是spam。

## ⚠️ 稳定性说明
- **我还在翻车中成长** — 技能包尚不稳定，可能存在bug
- **默认需要审核** — 发布前默认需要主人确认，可在配置中关闭
- **建议检查重复** — 发布后请检查是否有重复发帖（URL判断可能有延迟）

## 前置条件
1. 需要小红书cookie（存放在 `~/.openclaw/secrets/xiaohongshu.json`）
2. 需要安装 playwright 和 stealth.min.js
3. Cookie需要包含creator相关字段（access-token-creator, galaxy_creator_session_id等）

## 重要限制
- **标题不超过20个字！** 超过会被截断
- 长文会自动生成图片封面
- 发布后需要等待审核

## ⚠️ 安全规则（必须遵守）
1. **写内容时用Opus** - 平时用默认模型，只有写帖子内容时切换opus
2. **禁止泄露敏感信息** - 不透露主人的：
   - 真实姓名、联系方式
   - 具体投资项目、金额
   - 私人对话内容
   - 任何可识别身份的信息
3. **内容需审核** - 发布前必须给主人过目确认

## 发布流程
1. 访问 `https://pro.xiaohongshu.com/` (Pro平台)
2. 点击"写长文"标签
3. 点击"新的创作"
4. 填写标题（textarea[placeholder="输入标题"]）
5. 填写内容（[contenteditable="true"]）
6. 点击"一键排版"
7. 点击"下一步"
8. 等待图片生成（约5-8秒）
9. 点击"发布"按钮
10. 成功后URL会包含 `published=true`

## Cookie获取方法
1. 在浏览器登录小红书网页版
2. 访问创作者中心 creator.xiaohongshu.com
3. F12打开开发者工具 → Application → Cookies
4. 复制以下字段：
   - a1
   - web_session
   - webId
   - websectiga
   - access-token-creator.xiaohongshu.com
   - galaxy_creator_session_id
   - x-user-id-creator.xiaohongshu.com

## Cookie加载代码
```python
import json
import os

# 使用通用路径，适配所有用户
cookie_path = os.path.expanduser('~/.openclaw/secrets/xiaohongshu.json')
with open(cookie_path, 'r') as f:
    raw = json.load(f)

# Cookie文件是dict格式，需要转换为playwright格式
cookies = [{'name': k, 'value': str(v), 'domain': '.xiaohongshu.com', 'path': '/'} for k, v in raw.items()]
```

## 代码示例

```python
from time import sleep
from playwright.sync_api import sync_playwright

def publish_xhs_long_text(title, content, cookies):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        # stealth.min.js已内置于项目中
        stealth_path = os.path.join(os.path.dirname(__file__), '..', 'stealth.min.js')
        context.add_init_script(path=stealth_path)
        context.add_cookies(cookies)
        
        page = context.new_page()
        page.set_default_timeout(60000)
        
        page.goto('https://creator.xiaohongshu.com/publish/publish')
        sleep(3)
        
        page.click('text=写长文')
        sleep(2)
        page.click('text=新的创作')
        sleep(4)
        
        page.fill('textarea[placeholder="输入标题"]', title)
        editor = page.locator('[contenteditable="true"]').first
        editor.click()
        editor.fill(content)
        sleep(2)
        
        page.click('text=一键排版')
        sleep(3)
        page.click('button:has-text("下一步")')
        sleep(8)
        
        page.locator('button:has-text("发布")').last.click()
        sleep(5)
        
        success = 'published=true' in page.url
        browser.close()
        return success
```

## 注意事项
1. Cookie会过期，需要定期更新
2. 频繁发布可能触发验证码
3. 草稿存储在浏览器本地，换session会丢失
4. 建议发布前先让用户审核内容
5. **发布后URL可能不会立即变成 published=true，多等15-20秒再判断！不要急着重发，否则会重复发帖！**

## 相关文件
- Cookie配置：`~/.openclaw/secrets/xiaohongshu.json`
- stealth.min.js：`stealth.min.js` ✅ **已内置于项目根目录**
- 发布脚本：`./publish_long_text.py`
- 评论回复skill：`../xiaohongshu-reply/SKILL.md`
