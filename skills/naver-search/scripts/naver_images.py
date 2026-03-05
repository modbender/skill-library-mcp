#!/usr/bin/env python3
import sys
import os
import argparse

# Add lib directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "lib"))
from naver_base import perform_search, format_output

def compact_formatter(results):
    output = []
    images = results.get("images_results")
    if images:
        output.append(f"🖼️ 네이버 이미지 검색 결과 ({len(images)}개)")
        output.append("=" * 30)
        for i, res in enumerate(images[:20], 1): # Images can show more
            output.append(f"{i}. {res.get('title', '이미지')}")
            output.append(f"   📷 출처: {res.get('source', '알 수 없음')}")
            output.append(f"   🔗 {res.get('link')}")
            if res.get('thumbnail'):
                output.append(f"   🖼️ {res.get('thumbnail')}")
            output.append("")
    
    return "\n".join(output) if output else "이미지 검색 결과가 없습니다."

def main():
    parser = argparse.ArgumentParser(description="Naver Image Search")
    parser.add_argument("query", help="Search query")
    parser.add_argument("-n", "--num", type=int, default=10, help="Number of results (max 100)")
    parser.add_argument("-f", "--format", default="compact", choices=["compact", "full", "json"])
    args = parser.parse_args()

    params = {
        "engine": "naver",
        "query": args.query,
        "where": "image",
        "num": min(args.num, 100)
    }
    
    results = perform_search(params)
    print(format_output(results, args.format, compact_formatter))

if __name__ == "__main__":
    main()
