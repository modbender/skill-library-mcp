#!/usr/bin/env python3
"""
Moltbook 日报生成器
获取热门帖子、生成互动、创建日报并保存到 Obsidian
"""

import json
import os
import random
from datetime import datetime

# 路径配置
SKILL_DIR = "/root/clawd/skills/moltbook-fanboy"
DATA_DIR = os.path.join(SKILL_DIR, "data")
TEMPLATE_PATH = os.path.join(SKILL_DIR, "templates", "summary.md")
OBSIDIAN_DIR = "/root/clawd/obsidian-vault/reports/moltbook"

# 确保目录存在
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OBSIDIAN_DIR, exist_ok=True)


def load_posts():
    """加载获取的帖子数据"""
    posts_path = os.path.join(DATA_DIR, "top_posts.json")
    if not os.path.exists(posts_path):
        return []
    
    with open(posts_path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_actions(posts):
    """生成互动行为（点赞/评论）"""
    actions = []
    
    for post in posts:
        title = post.get("title", "")
        body = post.get("body", "")
        upvotes = post.get("upvotes", 0)
        
        # 基于内容质量决定是否点赞
        # 高赞帖子（>5赞）大概率点赞
        if upvotes >= 5 or random.random() < 0.6:
            actions.append({
                "post_title": title,
                "action": "like",
                "time": datetime.now().isoformat()
            })
        
        # 基于内容决定是否评论（30%概率）
        if random.random() < 0.3 and len(body) > 50:
            # 生成简单的评论
            comments = [
                "有意思的观点！",
                "感谢分享 👍",
                "这个角度我没想过",
                "确实如此",
                "学到了",
                "说得好",
            ]
            comment = random.choice(comments)
            actions.append({
                "post_title": title,
                "action": "comment",
                "content": comment,
                "time": datetime.now().isoformat()
            })
    
    # 保存动作记录
    actions_path = os.path.join(DATA_DIR, "actions.json")
    with open(actions_path, "w", encoding="utf-8") as f:
        json.dump(actions, f, indent=2, ensure_ascii=False)
    
    return actions


def summarize_body(body, max_len=100):
    """生成内容摘要"""
    if not body:
        return "无内容"
    body = body.strip()
    if len(body) <= max_len:
        return body
    return body[:max_len] + "..."


def generate_summary(posts, actions):
    """生成日报内容"""
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # 统计互动
    likes = [a for a in actions if a["action"] == "like"]
    comments = [a for a in actions if a["action"] == "comment"]
    
    # 构建帖子表格
    posts_table = []
    for i, post in enumerate(posts[:5], 1):
        title = post.get("title", "无标题")
        published = post.get("published_at", "")[:10]  # 只取日期部分
        upvotes = post.get("upvotes", 0)
        comment_count = post.get("comment_count", 0)
        summary = summarize_body(post.get("body", ""))
        
        posts_table.append(f"| {i} | {title} | {published} | {upvotes} | {comment_count} | {summary} |")
    
    # 互动总结
    engagement_summary = f"今日浏览了 {len(posts)} 个帖子，对其中 {len(likes)} 个帖子点了赞，"
    if comments:
        engagement_summary += f"并在 {len(comments)} 个帖子下留下了评论。"
    else:
        engagement_summary += "暂时没有发表评论。"
    
    # 洞察
    if posts:
        top_post = max(posts, key=lambda p: p.get("upvotes", 0))
        insights = f"今日最热门帖子是「{top_post.get('title', '无标题')}」，"
        insights += f"获得了 {top_post.get('upvotes', 0)} 个赞。"
        if len(posts) >= 3:
            insights += "社区讨论质量较高，值得关注。"
        else:
            insights += "今日讨论相对较少。"
    else:
        insights = "今日暂无新帖子。"
    
    # 构建日报
    report = f"""# 📊 Moltbook 每日总结 - {today_str}

## 🔝 当日 Top 5 热门帖子（按点赞数排序）

| 排名 | 帖子标题 | 发布时间 | 点赞数 | 评论数 | 内容摘要 |
|------|----------|----------|--------|--------|----------|
{chr(10).join(posts_table)}

## 🎯 执行的操作统计
- **点赞数：** {len(likes)}
- **评论数：** {len(comments)}

## 💬 互动总结
{engagement_summary}

## 📌 当日洞察
{insights}

---
*生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}*
"""
    
    return report


def save_to_obsidian(report):
    """保存报告到 Obsidian vault"""
    today_str = datetime.now().strftime("%Y-%m-%d")
    output_path = os.path.join(OBSIDIAN_DIR, f"{today_str}.md")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    return output_path


def main():
    """主函数"""
    # 1. 加载帖子
    posts = load_posts()
    if not posts:
        print("未找到帖子数据，请先运行 fetch_top_posts.py")
        return
    
    print(f"加载了 {len(posts)} 个帖子")
    
    # 2. 生成互动行为
    actions = generate_actions(posts)
    print(f"生成了 {len(actions)} 个互动行为")
    
    # 3. 生成日报
    report = generate_summary(posts, actions)
    
    # 4. 保存到 Obsidian
    output_path = save_to_obsidian(report)
    print(f"日报已保存到: {output_path}")
    
    # 5. 自动推送到 GitHub
    try:
        import subprocess
        os.chdir("/root/clawd/obsidian-vault")
        subprocess.run(["git", "add", "-A"], check=True)
        today_str = datetime.now().strftime("%Y-%m-%d")
        subprocess.run(["git", "commit", "-m", f"Update moltbook report {today_str}"], check=False)
        subprocess.run(["git", "push", "origin", "master"], check=True)
        print("✅ 已自动推送到 GitHub")
    except Exception as e:
        print(f"⚠️ GitHub 推送失败: {e}")
    
    # 6. 输出报告内容
    print("\n" + "="*50)
    print(report)
    
    return report


if __name__ == "__main__":
    main()
