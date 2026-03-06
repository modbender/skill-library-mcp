"""
配置模块 - GitHub Topics Trending 配置
"""
import os

# ============================================================================
# GitHub API 配置
# ============================================================================
GITHUB_TOKEN = os.getenv("GH_TOKEN")
TOPIC = os.getenv("TOPIC", "claude-code")
GITHUB_API_BASE = "https://api.github.com"
GITHUB_PER_PAGE = 100  # GitHub API max per page
GITHUB_MAX_PAGES = 10  # Maximum pages to fetch (1000 repos)

# GitHub 搜索配置
GITHUB_SEARCH_SORT = "stars"  # stars, forks, updated
GITHUB_SEARCH_ORDER = "desc"  # desc, asc

# ============================================================================
# 请求配置
# ============================================================================
FETCH_REQUEST_DELAY = 0.5  # API 请求间隔（秒）


def format_number(num: int) -> str:
    """格式化数字显示"""
    if num >= 1000000:
        return f"{num / 1000000:.1f}M"
    elif num >= 1000:
        return f"{num / 1000:.1f}K"
    return str(num)


def get_repo_url(owner: str, repo_name: str) -> str:
    """生成仓库 URL"""
    return f"https://github.com/{owner}/{repo_name}"
