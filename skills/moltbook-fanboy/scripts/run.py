#!/usr/bin/env python3
"""
Moltbook Fanboy - Daily Summary Generator
This script fetches top posts and generates a daily summary.
The agent should autonomously generate engagement actions (likes/comments) based on post content.
"""

import json
import os
from datetime import datetime
import subprocess
import sys

# Configuration
MAX_POSTS = 5
DATA_DIR = "/root/clawd/skills/moltbook-fanboy/data"
TEMPLATE_PATH = "/root/clawd/skills/moltbook-fanboy/templates/summary.md"
FETCH_SCRIPT = "/root/clawd/skills/moltbook-fanboy/scripts/fetch_top_posts.py"

def ensure_data_dir():
    """Ensure data directory exists."""
    os.makedirs(DATA_DIR, exist_ok=True)

def fetch_top_posts():
    """Run fetch_top_posts.py to get top posts."""
    try:
        result = subprocess.run(
            [sys.executable, FETCH_SCRIPT],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            print(f"Error fetching posts: {result.stderr}", file=sys.stderr)
            return []
        
        # Load fetched posts
        posts_file = os.path.join(DATA_DIR, "top_posts.json")
        if os.path.exists(posts_file):
            with open(posts_file, "r", encoding="utf-8") as f:
                posts = json.load(f)
            print(f"成功获取 {len(posts)} 个热门帖子", file=sys.stderr)
            return posts
        else:
            print("未找到帖子数据文件", file=sys.stderr)
            return []
    except Exception as e:
        print(f"获取帖子时出错: {e}", file=sys.stderr)
        return []

def load_template():
    """Load the summary markdown template."""
    try:
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"加载模板时出错: {e}", file=sys.stderr)
        return None

def load_actions():
    """Load engagement actions if they exist."""
    actions_file = os.path.join(DATA_DIR, "actions.json")
    if os.path.exists(actions_file):
        try:
            with open(actions_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"加载互动记录时出错: {e}", file=sys.stderr)
            return []
    return []

def generate_summary(posts, actions, template):
    """Generate the final markdown summary."""
    if not template:
        return "# 错误：无法加载模板文件\n\n请检查模板文件是否存在。"
    
    if len(posts) == 0:
        return "# Moltbook 每日总结\n\n今日未获取到热门帖子。"
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Count actions
    total_likes = len([a for a in actions if a.get("action") == "like"])
    total_comments = len([a for a in actions if a.get("action") == "comment"])
    
    # Ensure we have at least 5 posts (pad with empty if needed)
    while len(posts) < 5:
        posts.append({
            "title": "",
            "published_at": "",
            "upvotes": 0,
            "comment_count": 0,
            "body": ""
        })
    
    # Build engagement summary
    engagement_parts = []
    if total_likes > 0:
        engagement_parts.append(f"共点赞 {total_likes} 个帖子")
    if total_comments > 0:
        engagement_parts.append(f"共评论 {total_comments} 个帖子")
    
    if engagement_parts:
        engagement_summary = f"今日与 {len(posts)} 个热门帖子进行了互动。{', '.join(engagement_parts)}。"
    else:
        engagement_summary = f"今日浏览了 {len(posts)} 个热门帖子，但未进行互动。"
    
    # Add details about comments if any
    if total_comments > 0:
        comment_details = []
        for action in actions:
            if action.get("action") == "comment":
                comment_details.append(f"- 对「{action.get('post_title', '未知')}」评论：{action.get('content', '')}")
        if comment_details:
            engagement_summary += "\n\n评论详情：\n" + "\n".join(comment_details[:5])  # Limit to 5 comments
    
    # Build insights
    if posts:
        total_upvotes = sum(p.get("upvotes", 0) for p in posts if p.get("title"))
        avg_upvotes = total_upvotes // len([p for p in posts if p.get("title")]) if [p for p in posts if p.get("title")] else 0
        top_post = next((p for p in posts if p.get("title")), None)
        
        insights = []
        if top_post:
            insights.append(f"- 最热门帖子：「{top_post.get('title', '')}」，获得 {top_post.get('upvotes', 0)} 个点赞")
        if avg_upvotes > 0:
            insights.append(f"- 平均点赞数：{avg_upvotes}")
        if total_upvotes > 0:
            total_comments_from_posts = sum(p.get("comment_count", 0) for p in posts if p.get("title"))
            insights.append(f"- 社区总互动量：{total_upvotes} 个点赞 + {total_comments_from_posts} 条评论")
        
        if not insights:
            insights = ["- 今日暂无特别洞察"]
    else:
        insights = ["- 今日暂无数据"]
    
    # Replace placeholders in template
    summary = template.format(
        date=today,
        title_1=posts[0].get("title", "") if posts else "",
        published_at_1=posts[0].get("published_at", "") if posts else "",
        upvotes_1=posts[0].get("upvotes", 0) if posts else 0,
        comments_1=posts[0].get("comment_count", 0) if posts else 0,
        summary_1=(posts[0].get("body", "")[:100] + "...") if posts and posts[0].get("body") else "",
        title_2=posts[1].get("title", "") if len(posts) > 1 else "",
        published_at_2=posts[1].get("published_at", "") if len(posts) > 1 else "",
        upvotes_2=posts[1].get("upvotes", 0) if len(posts) > 1 else 0,
        comments_2=posts[1].get("comment_count", 0) if len(posts) > 1 else 0,
        summary_2=(posts[1].get("body", "")[:100] + "...") if len(posts) > 1 and posts[1].get("body") else "",
        title_3=posts[2].get("title", "") if len(posts) > 2 else "",
        published_at_3=posts[2].get("published_at", "") if len(posts) > 2 else "",
        upvotes_3=posts[2].get("upvotes", 0) if len(posts) > 2 else 0,
        comments_3=posts[2].get("comment_count", 0) if len(posts) > 2 else 0,
        summary_3=(posts[2].get("body", "")[:100] + "...") if len(posts) > 2 and posts[2].get("body") else "",
        title_4=posts[3].get("title", "") if len(posts) > 3 else "",
        published_at_4=posts[3].get("published_at", "") if len(posts) > 3 else "",
        upvotes_4=posts[3].get("upvotes", 0) if len(posts) > 3 else 0,
        comments_4=posts[3].get("comment_count", 0) if len(posts) > 3 else 0,
        summary_4=(posts[3].get("body", "")[:100] + "...") if len(posts) > 3 and posts[3].get("body") else "",
        title_5=posts[4].get("title", "") if len(posts) > 4 else "",
        published_at_5=posts[4].get("published_at", "") if len(posts) > 4 else "",
        upvotes_5=posts[4].get("upvotes", 0) if len(posts) > 4 else 0,
        comments_5=posts[4].get("comment_count", 0) if len(posts) > 4 else 0,
        summary_5=(posts[4].get("body", "")[:100] + "...") if len(posts) > 4 and posts[4].get("body") else "",
        total_likes=total_likes,
        total_comments=total_comments,
        engagement_summary=engagement_summary,
        insights="\n".join(insights)
    )
    
    return summary

def main():
    """Main execution: fetch posts and generate summary."""
    ensure_data_dir()
    
    # Fetch top posts
    posts = fetch_top_posts()
    
    # Load actions (should be generated by agent autonomously)
    actions = load_actions()
    
    # Load template
    template = load_template()
    
    # Generate summary
    summary = generate_summary(posts, actions, template)
    
    return summary

if __name__ == "__main__":
    output = main()
    # Print ONLY the summary to stdout (for cron)
    print(output)
