#!/usr/bin/env python3
"""
Reddit 详情获取脚本

功能：
- 读取 posts_raw.json，取 Top N 帖子
- 获取每个帖子的完整内容和分层采样评论
- 评论采样策略：高票 8 条 + 热门 4 条 + 最新 3 条
- 正文截断 3000 字符，评论截断 200 字符
- 输出 posts_detail.json

用法：
    python3 reddit_detail_fetcher.py \
        --input <posts_raw.json 路径> \
        --output <输出文件路径> \
        --config <配置文件路径>
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def load_json_file(file_path: str) -> dict[str, Any]:
    """加载 JSON 文件"""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def truncate_text(text: str, max_chars: int) -> str:
    """截断文本到指定字符数"""
    if not text or len(text) <= max_chars:
        return text or ""
    return text[:max_chars] + "...（已截断）"


def get_headers(config: dict[str, Any]) -> dict[str, str]:
    """构建请求头"""
    user_agent = config.get("reddit", {}).get("user_agent", "RedditTopicInsight/1.0")
    return {"User-Agent": user_agent}


def fetch_post_comments(
    post_id: str,
    sort_method: str,
    headers: dict[str, str],
    limit: int = 20
) -> list[dict[str, Any]]:
    """
    获取帖子评论

    调用 Reddit 公开 API:
    https://www.reddit.com/comments/{post_id}.json?sort={sort}&limit={limit}
    """
    url = f"https://www.reddit.com/comments/{post_id}.json"
    params = {"sort": sort_method, "limit": limit}
    max_retries = 3

    for attempt in range(max_retries):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=15)

            if resp.status_code == 429:
                logger.warning("速率限制，等待 60 秒...")
                time.sleep(60)
                continue

            resp.raise_for_status()
            data = resp.json()

            if not isinstance(data, list) or len(data) < 2:
                return []

            comments_data = data[1].get("data", {}).get("children", [])
            comments = []

            for child in comments_data:
                if child.get("kind") != "t1":
                    continue
                comment_data = child.get("data", {})
                comments.append({
                    "comment_id": comment_data.get("id", ""),
                    "author": comment_data.get("author", "[deleted]"),
                    "body": comment_data.get("body", ""),
                    "score": comment_data.get("score", 0),
                    "created_utc": comment_data.get("created_utc", 0)
                })

            return comments

        except requests.RequestException as e:
            logger.warning(f"获取评论失败（第 {attempt + 1}/{max_retries} 次）: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)

    return []


def fetch_post_detail(
    post_id: str,
    headers: dict[str, str]
) :
    """
    获取帖子完整正文

    通过评论 API 同时返回帖子正文
    """
    url = f"https://www.reddit.com/comments/{post_id}.json"
    max_retries = 3

    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=headers, timeout=15)

            if resp.status_code == 429:
                logger.warning("速率限制，等待 60 秒...")
                time.sleep(60)
                continue

            resp.raise_for_status()
            data = resp.json()

            if not isinstance(data, list) or len(data) < 1:
                return None

            post_children = data[0].get("data", {}).get("children", [])
            if post_children:
                return post_children[0].get("data", {}).get("selftext", "")

            return None

        except requests.RequestException as e:
            logger.warning(f"获取帖子详情失败（第 {attempt + 1}/{max_retries} 次）: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)

    return None


def sample_comments(
    post_id: str,
    headers: dict[str, str],
    sampling_config: dict[str, int],
    comment_max_chars: int
) -> list[dict[str, Any]]:
    """
    分层采样评论

    策略：
    - 高票评论（sort=top）：默认 8 条
    - 热门评论（sort=hot）：默认 4 条
    - 最新评论（sort=new）：默认 3 条

    跨排序方式以 comment_id 去重
    """
    sort_mapping = {
        "high_vote": ("top", sampling_config.get("high_vote", 8)),
        "hot": ("hot", sampling_config.get("hot", 4)),
        "latest": ("new", sampling_config.get("latest", 3))
    }

    seen_ids: set[str] = set()
    sampled_comments: list[dict[str, Any]] = []

    for layer_name, (sort_method, count) in sort_mapping.items():
        raw_comments = fetch_post_comments(
            post_id, sort_method, headers, limit=count * 2
        )

        added = 0
        for comment in raw_comments:
            if added >= count:
                break
            cid = comment["comment_id"]
            if cid in seen_ids:
                continue
            seen_ids.add(cid)

            # 截断评论内容
            comment["body"] = truncate_text(comment["body"], comment_max_chars)
            comment["sampling_layer"] = layer_name
            sampled_comments.append(comment)
            added += 1

        # 请求间隔，避免速率限制
        time.sleep(1)

    return sampled_comments


def main() -> None:
    parser = argparse.ArgumentParser(description="Reddit 详情获取脚本")
    parser.add_argument(
        "--input",
        required=True,
        help="posts_raw.json 路径"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="输出文件路径"
    )
    parser.add_argument(
        "--config",
        required=True,
        help="配置文件路径"
    )
    args = parser.parse_args()

    # 加载配置
    config = load_json_file(args.config)
    raw_data = load_json_file(args.input)

    detail_config = config.get("detail", {})
    collection_config = config.get("collection", {})

    top_n = collection_config.get("top_n", 10)
    body_max_chars = detail_config.get("body_max_chars", 3000)
    comment_max_chars = detail_config.get("comment_max_chars", 200)
    sampling_config = detail_config.get("comment_sampling", {
        "high_vote": 8,
        "hot": 4,
        "latest": 3
    })

    # 取 Top N 帖子
    all_posts = raw_data.get("posts", [])
    top_posts = all_posts[:top_n]

    if not top_posts:
        logger.error("帖子列表为空，请先运行 reddit_collector.py")
        sys.exit(1)

    logger.info(f"开始获取 Top {len(top_posts)} 帖子的详情和评论...")

    headers = get_headers(config)
    request_delay = config.get("reddit", {}).get("request_delay_seconds", 2)

    detailed_posts: list[dict[str, Any]] = []

    for i, post in enumerate(top_posts):
        post_id = post["post_id"]
        logger.info(
            f"[{i + 1}/{len(top_posts)}] 获取帖子: {post['title'][:50]}..."
        )

        # 获取完整正文
        selftext = fetch_post_detail(post_id, headers)
        if selftext is None:
            logger.warning(f"帖子 {post_id} 可能已删除，跳过")
            continue

        time.sleep(request_delay)

        # 分层采样评论
        comments = sample_comments(
            post_id, headers, sampling_config, comment_max_chars
        )

        detailed_post = {
            "post_id": post_id,
            "title": post["title"],
            "subreddit": post["subreddit"],
            "author": post["author"],
            "url": post["url"],
            "score": post["score"],
            "num_comments": post["num_comments"],
            "heat_score": post["heat_score"],
            "selftext": truncate_text(selftext, body_max_chars),
            "comments": comments
        }
        detailed_posts.append(detailed_post)

        logger.info(f"  → 正文 {len(selftext)} 字符，采样 {len(comments)} 条评论")

        time.sleep(request_delay)

    # 构建输出
    output = {
        "metadata": {
            "topic": raw_data.get("metadata", {}).get("topic", ""),
            "top_n": top_n,
            "fetched_at": datetime.now(timezone.utc).isoformat()
        },
        "posts": detailed_posts
    }

    # 确保输出目录存在
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # 写入文件
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    logger.info(f"详情获取完成！共获取 {len(detailed_posts)} 个帖子")
    logger.info(f"结果已保存到 {args.output}")


if __name__ == "__main__":
    main()
