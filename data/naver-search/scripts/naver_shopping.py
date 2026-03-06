#!/usr/bin/env python3
import sys
import os
import argparse

# Add lib directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "lib"))
from naver_base import perform_search, format_output

def compact_formatter(results):
    output = []
    # naver_shopping 엔진은 shopping_results 필드 사용
    shopping = results.get("shopping_results", [])
    if shopping:
        output.append(f"🛒 네이버 쇼핑 검색 결과 ({len(shopping)}개)")
        output.append("=" * 30)
        for i, res in enumerate(shopping[:10], 1):
            price = f" | 💰 {res.get('price')}" if res.get('price') else ""
            rating = f" | ⭐ {res.get('rating')}" if res.get('rating') else ""
            reviews = f"({res.get('reviews')})" if res.get('reviews') else ""
            # naver_shopping 엔진에서는 source 필드가 판매처명인 경우가 많음
            stores = f" | 🏪 {res.get('source', res.get('stores', ''))}" if (res.get('source') or res.get('stores')) else ""
            
            output.append(f"{i}. {res.get('title')}")
            output.append(f"   💵 정보: {price}{rating}{reviews}{stores}")
            
            if "additional" in res:
                specs = ", ".join([f"{s.get('name', s.get('title', ''))}: {s.get('value', '')}" for s in res['additional'][:3]])
                if specs:
                    output.append(f"   🔹 스펙: {specs}")
            
            output.append(f"   🔗 {res.get('link')}")
            output.append("")
    
    return "\n".join(output) if output else "쇼핑 검색 결과가 없습니다."

def main():
    parser = argparse.ArgumentParser(description="Naver Shopping Search (Specialized)")
    parser.add_argument("query", help="Search query")
    parser.add_argument("-p", "--page", type=int, default=1, help="Page number")
    parser.add_argument("-s", "--sort", help="Sort options (예: price_asc, price_dsc, rel)")
    parser.add_argument("-f", "--format", default="compact", choices=["compact", "full", "json"])
    args = parser.parse_args()

    # naver 엔진의 nexearch 사용 (가장 안정적)
    params = {
        "engine": "naver",
        "query": args.query,
        "where": "nexearch",
        "page": args.page
    }
    if args.sort:
        params["sort_by"] = args.sort
        
    results = perform_search(params)
    print(format_output(results, args.format, compact_formatter))

if __name__ == "__main__":
    main()
