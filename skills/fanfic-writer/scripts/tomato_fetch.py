"""
Tomato Novel (番茄小说) Genre Fetcher
Fetches trending genres/data from 番茄小说

【说明】
- 此脚本为可选功能，用于主动爬取番茄热门题材做推荐
- 主要流程：用户直接指定题材，无需爬取
- 如需使用：python tomato_fetch.py <output_dir>
- 如果网站屏蔽爬取，使用示例数据或用户手动提供题材

【推荐用法】
用户直接说："我想写一本都市异能的小说"
→ 跳过此脚本，直接进入大纲生成
"""
import urllib.request
import json
import re
from pathlib import Path

def fetch_tomato_rankings():
    """
    Fetch popular genres/themes from 番茄小说
    
    Returns:
        dict: genre data for analysis
    """
    
    # 番茄小说热门分类页面
    # Note: 实际爬取可能需要处理反爬机制
    urls = [
        "https://fanqienovel.com/library/",
        "https://fanqienovel.com/rank/",
    ]
    
    genres_data = {
        "source": "番茄小说",
        "fetch_time": None,
        "genres": []
    }
    
    # Placeholder implementation
    # 实际使用时需要根据番茄网站的HTML结构调整解析逻辑
    
    # 热门题材示例数据（实际应从网站抓取）
    popular_genres = [
        {
            "name": "都市异能",
            "trend_score": 95,
            "description": "现代都市背景下的超能力/系统故事",
            "avg_words": 800000,
            "hot_books": ["书名A", "书名B"]
        },
        {
            "name": "玄幻修仙",
            "trend_score": 90,
            "description": "传统修仙、升级打怪",
            "avg_words": 1200000,
            "hot_books": ["书名C", "书名D"]
        },
        {
            "name": "历史架空",
            "trend_score": 85,
            "description": "穿越历史、权谋争霸",
            "avg_words": 1000000,
            "hot_books": ["书名E"]
        },
        {
            "name": "游戏竞技",
            "trend_score": 80,
            "description": "电竞、游戏世界",
            "avg_words": 600000,
            "hot_books": ["书名F"]
        },
        {
            "name": "科幻末世",
            "trend_score": 75,
            "description": "末日生存、星际文明",
            "avg_words": 900000,
            "hot_books": ["书名G"]
        }
    ]
    
    genres_data["genres"] = popular_genres
    genres_data["fetch_time"] = "manual_sample"  # 实际应为时间戳
    
    return genres_data

def save_genre_data(data, book_dir):
    """Save fetched genre data"""
    output_path = Path(book_dir) / "genre_data.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Genre data saved to: {output_path}")

def format_genre_for_prompt(genres_data):
    """Format genre data for the analysis prompt"""
    lines = ["=== 番茄小说热门题材数据 ===", ""]
    
    for g in genres_data.get("genres", []):
        lines.append(f"题材: {g['name']}")
        lines.append(f"热度: {g['trend_score']}/100")
        lines.append(f"描述: {g['description']}")
        lines.append(f"常见字数: {g['avg_words']:,} 字")
        lines.append(f"代表作: {', '.join(g['hot_books'])}")
        lines.append("")
    
    return "\n".join(lines)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: tomato_fetch.py <output_dir>")
        print("Fetches genre data from 番茄小说 for novel planning")
        sys.exit(1)
    
    output_dir = sys.argv[1]
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print("Fetching tomato novel genre data...")
    # In full implementation, this would actually scrape the website
    data = fetch_tomato_rankings()
    save_genre_data(data, output_dir)
    
    # Also save formatted version for prompts
    formatted = format_genre_for_prompt(data)
    formatted_path = Path(output_dir) / "genre_data_formatted.txt"
    with open(formatted_path, 'w', encoding='utf-8') as f:
        f.write(formatted)
    print(f"Formatted data saved to: {formatted_path}")
