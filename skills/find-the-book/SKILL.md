---
name: Douban Book Search Skill
description: 当用户想要寻找书籍、根据描述推荐书单、或者查询某类书籍的豆瓣评分时使用此技能。
  这个技能会通过搜索引擎查找豆瓣读书（book.douban.com）的条目，并抓取实时的评分、作者信息和书籍链接；并且自动寻找该书在微信读书(WeChat
  Reading)上的直接阅读https://www.google.com/search?q=%E9%93%BE%E6%8E%A5。适合需要深度阅读或寻找电子书...
---

# Douban Book Search Skill

## Description
当用户想要寻找书籍、根据描述推荐书单、或者查询某类书籍的豆瓣评分时使用此技能。
这个技能会通过搜索引擎查找豆瓣读书（book.douban.com）的条目，并抓取实时的评分、作者信息和书籍链接；并且自动寻找该书在**微信读书(WeChat Reading)**上的直接阅读https://www.google.com/search?q=%E9%93%BE%E6%8E%A5。适合需要深度阅读或寻找电子书资源的用户。

## Dependencies
在使用此技能前，请确保环境中安装了以下库：
- `duckduckgo-search`
- `requests`
- `beautifulsoup4`

安装命令:
```bash
pip install duckduckgo-search requests beautifulsoup4

## Usage Example (Prompt)
当用户输入类似以下请求时调用此 Skill：

"帮我找几本关于时间管理的豆瓣高分书籍" "推荐几本类似《三体》的科幻小说，要有豆瓣链接"

Agent 调用逻辑: search_douban_books(query="时间管理 高分", limit=3)

当你使用 search_books_comprehensive 工具后，请遵循以下 Markdown 格式输出：

书名：加粗，如 《书名》。

评分：标注豆瓣评分（如 ⭐ 8.9）。

阅读资源：

豆瓣详情

📖 微信读书 (如果工具返回了 wechat_link)

简介：简短的一句话推荐语。

回答示例：

《置身事内》 ⭐ 9.1

👉 豆瓣链接 | 📖 微信读书链接

简介：兰小欢教授通俗易懂地讲解中国政府与经济发展的关系。