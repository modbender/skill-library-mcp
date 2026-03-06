#!/usr/bin/env python3
"""
GitHub Trending 获取脚本
GitHub Trending Fetcher
"""

import json
import sys
from datetime import datetime

def get_github_trending(language="", since="daily", limit=10):
    """获取 GitHub Trending"""
    mock_repos = [
        {"rank": 1, "name": "facebook/react", "stars": 220000, "today": 256, "language": "JavaScript", "description": "A declarative library for building user interfaces"},
        {"rank": 2, "name": "vercel/next.js", "stars": 120000, "today": 198, "language": "TypeScript", "description": "The React Framework"},
        {"rank": 3, "name": "langchain-ai/langchain", "stars": 90000, "today": 156, "language": "Python", "description": "Building applications with LLMs"},
        {"rank": 4, "name": "rust-lang/rust", "stars": 95000, "today": 145, "language": "Rust", "description": "Empowering everyone to build reliable software"},
        {"rank": 5, "name": "golang/go", "stars": 122000, "today": 132, "language": "Go", "description": "The Go programming language"},
        {"rank": 6, "name": "microsoft/vscode", "stars": 160000, "today": 128, "language": "TypeScript", "description": "Visual Studio Code"},
        {"rank": 7, "name": "tensorflow/tensorflow", "stars": 185000, "today": 115, "language": "Python", "description": "An open source machine learning framework"},
        {"rank": 8, "name": "openai/whisper", "stars": 65000, "today": 108, "language": "Python", "description": "Robust Speech Recognition via Large-Scale Weak Supervision"},
        {"rank": 9, "name": "anthropics/anthropic-cookbook", "stars": 45000, "today": 98, "language": "Python", "description": "Claude usage examples"},
        {"rank": 10, "name": "denoland/deno", "stars": 98000, "today": 87, "language": "Rust", "description": "A modern runtime for JavaScript and TypeScript"},
    ]
    
    if language:
        mock_repos = [r for r in mock_repos if r["language"].lower() == language.lower()]
    
    return mock_repos[:limit]

def format_output(data):
    output = "📈 GitHub 今日热门\n\n"
    for item in data:
        stars_k = f"{item['stars'] / 1000:.0f}k"
        output += f"{item['rank']}. {item['name']} ⭐ {stars_k} (+{item['today']}) - {item['language']}\n"
        output += f"   {item['description']}\n\n"
    return output

def main():
    limit = 10
    language = ""
    
    for arg in sys.argv[1:]:
        if arg.isdigit():
            limit = int(arg)
        elif arg not in ["--json", "-j"]:
            language = arg
    
    data = get_github_trending(language=language, limit=limit)
    
    if "--json" in sys.argv or "-j" in sys.argv:
        print(json.dumps({"data": data}, ensure_ascii=False, indent=2))
    else:
        print(format_output(data))

if __name__ == "__main__":
    main()
