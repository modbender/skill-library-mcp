#!/usr/bin/env python3
"""
Reddit 数据采集脚本

功能：
- 使用 Reddit 公开 JSON API 搜索帖子
- 按热度公式 (score + num_comments × 2) 排序
- 跨关键词去重
- 输出 posts_raw.json

用法：
    python3 reddit_collector.py \
        --keywords-file <keywords.json 路径> \
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


def get_reddit_headers(config: dict[str, Any]) -> dict[str, str]:
    """
    构建 Reddit API 请求头
    NOTE: Reddit 要求有效的 User-Agent，否则返回 429
    """
    user_agent = config.get("reddit", {}).get("user_agent", "RedditTopicInsight/1.0")
    return {"User-Agent": user_agent}


def get_auth_headers(config: dict[str, Any]):
    """
    获取 OAuth2 认证头（可选）
    如果配置了 REDDIT_CLIENT_ID 和 REDDIT_CLIENT_SECRET 环境变量，
    则使用 OAuth2 认证以获得更高的速率限制
    """
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")

    if not client_id or not client_secret:
        logger.info("未配置 Reddit API 认证，使用公开 API（速率受限）")
        return None

    logger.info("正在获取 Reddit OAuth2 令牌...")
    auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
    data = {"grant_type": "client_credentials"}
    headers = get_reddit_headers(config)

    try:
        resp = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=auth,
            data=data,
            headers=headers,
            timeout=10
        )
        resp.raise_for_status()
        token = resp.json().get("access_token")
        if token:
            logger.info("OAuth2 认证成功")
            return {
                "Authorization": f"Bearer {token}",
                "User-Agent": headers["User-Agent"]
            }
    except requests.RequestException as e:
        logger.warning(f"OAuth2 认证失败，回退到公开 API: {e}")

    return None


def search_reddit(
    keyword: str,
    config: dict[str, Any],
    headers: dict[str, str]
) -> list[dict[str, Any]]:
    """
    搜索 Reddit 帖子

    使用公开 JSON API: https://www.reddit.com/search.json
    或 OAuth2 API: https://oauth.reddit.com/search
    """
    reddit_config = config.get("reddit", {})
    use_oauth = "Authorization" in headers
    base_url = "https://oauth.reddit.com" if use_oauth else reddit_config.get("base_url", "https://www.reddit.com")
    limit = reddit_config.get("search_limit_per_keyword", 50)
    sort = reddit_config.get("search_sort", "relevance")
    time_filter = reddit_config.get("search_time", "year")

    url = f"{base_url}/search.json"
    params = {
        "q": keyword,
        "sort": sort,
        "t": time_filter,
        "limit": min(limit, 100),
        "type": "link"
    }

    posts = []
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=15)

            if resp.status_code == 429:
                wait_time = 60
                logger.warning(f"速率限制，等待 {wait_time} 秒...")
                time.sleep(wait_time)
                continue

            resp.raise_for_status()
            data = resp.json()

            children = data.get("data", {}).get("children", [])
            for child in children:
                post_data = child.get("data", {})
                post = {
                    "post_id": post_data.get("id", ""),
                    "title": post_data.get("title", ""),
                    "subreddit": post_data.get("subreddit", ""),
                    "author": post_data.get("author", ""),
                    "url": f"https://www.reddit.com{post_data.get('permalink', '')}",
                    "score": post_data.get("score", 0),
                    "num_comments": post_data.get("num_comments", 0),
                    "created_utc": post_data.get("created_utc", 0),
                    "selftext_preview": post_data.get("selftext", "")[:200],
                    "matched_keywords": [keyword]
                }
                posts.append(post)

            logger.info(f"关键词 [{keyword}] 搜索到 {len(children)} 条帖子")
            break

        except requests.RequestException as e:
            logger.warning(f"搜索失败（第 {attempt + 1}/{max_retries} 次）: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.error(f"关键词 [{keyword}] 搜索彻底失败，跳过")

    return posts


def calculate_heat_score(post: dict[str, Any]) -> int:
    """
    计算帖子热度分
    公式：score + num_comments × 2
    """
    return post.get("score", 0) + post.get("num_comments", 0) * 2


def deduplicate_posts(all_posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    跨关键词去重
    以 post_id 为主键，合并命中的关键词列表
    """
    seen: dict[str, dict[str, Any]] = {}

    for post in all_posts:
        post_id = post["post_id"]
        if post_id in seen:
            # 合并命中的关键词
            existing_keywords = seen[post_id]["matched_keywords"]
            for kw in post["matched_keywords"]:
                if kw not in existing_keywords:
                    existing_keywords.append(kw)
        else:
            seen[post_id] = post

    return list(seen.values())


def main() -> None:
    parser = argparse.ArgumentParser(description="Reddit 数据采集脚本")
    parser.add_argument(
        "--keywords-file",
        required=True,
        help="关键词 JSON 文件路径"
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

    # 加载配置和关键词
    config = load_json_file(args.config)
    keywords_data = load_json_file(args.keywords_file)

    keywords = [kw["keyword"] for kw in keywords_data.get("keywords", [])]
    if not keywords:
        logger.error("关键词列表为空，请检查 keywords.json")
        sys.exit(1)

    logger.info(f"开始采集，共 {len(keywords)} 个关键词: {keywords}")

    # 尝试获取 OAuth2 认证
    base_headers = get_reddit_headers(config)
    auth_headers = get_auth_headers(config)
    headers = auth_headers if auth_headers else base_headers

    # 搜索所有关键词
    all_posts: list[dict[str, Any]] = []
    request_delay = config.get("reddit", {}).get("request_delay_seconds", 2)

    for i, keyword in enumerate(keywords):
        logger.info(f"[{i + 1}/{len(keywords)}] 搜索关键词: {keyword}")
        posts = search_reddit(keyword, config, headers)
        all_posts.extend(posts)

        # 请求间隔，遵守速率限制
        if i < len(keywords) - 1:
            time.sleep(request_delay)

    if not all_posts:
        logger.error("所有关键词均未搜索到结果，请检查关键词设置")
        sys.exit(1)

    total_searched = len(all_posts)

    # 去重
    unique_posts = deduplicate_posts(all_posts)
    total_after_dedup = len(unique_posts)
    logger.info(f"搜索总计 {total_searched} 条，去重后 {total_after_dedup} 条")

    # 计算热度分并排序
    for post in unique_posts:
        post["heat_score"] = calculate_heat_score(post)

    unique_posts.sort(key=lambda p: p["heat_score"], reverse=True)

    # 构建输出
    output = {
        "metadata": {
            "topic": keywords_data.get("anchor_word", ""),
            "keywords_used": keywords,
            "total_searched": total_searched,
            "total_after_dedup": total_after_dedup,
            "collected_at": datetime.now(timezone.utc).isoformat()
        },
        "posts": unique_posts
    }

    # 确保输出目录存在
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # 写入文件
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    logger.info(f"采集完成！结果已保存到 {args.output}")
    logger.info(f"Top 5 热度帖子:")
    for i, post in enumerate(unique_posts[:5]):
        logger.info(
            f"  {i + 1}. [{post['heat_score']}] {post['title'][:60]} "
            f"(r/{post['subreddit']})"
        )


if __name__ == "__main__":
    main()
