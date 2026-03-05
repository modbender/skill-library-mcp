#!/usr/bin/env python3
import sys
import os
import argparse

# Add lib directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "lib"))
from naver_base import perform_search, format_output

def compact_formatter(results):
    output = []
    news = results.get("news_results")
    if news:
        output.append(f"📰 네이버 뉴스 검색 결과 ({len(news)}개)")
        output.append("=" * 30)
        for i, res in enumerate(news[:10], 1):
            news_info = res.get('news_info', {})
            source = news_info.get('press_name', res.get('source', '알 수 없음'))
            date = news_info.get('news_date', res.get('date', ''))
            
            date_info = f" | {date}" if date else ""
            output.append(f"{i}. {res.get('title')}")
            output.append(f"   📰 {source}{date_info}")
            output.append(f"   🔗 {res.get('link')}")
            output.append("")
    
    return "\n".join(output) if output else "뉴스 검색 결과가 없습니다."

def convert_time_to_tbs(time_str):
    """시간 옵션을 SerpAPI tbs 파라미터로 변환"""
    # 네이버 뉴스 엔진은 tbs 파라미터를 지원하지 않음
    # 기본 검색으로 폴백하고 검색어에 "최신" 키워드 추가
    # 또는 Google 엔진의 tbs를 사용할 수 있음
    time_map = {
        "all": "all",
        "1h": "qdr:h",
        "1d": "qdr:d",  # 최근 24시간
        "1w": "qdr:w",
        "1m": "qdr:m"
    }
    return time_map.get(time_str, "all")

def main():
    parser = argparse.ArgumentParser(description="Naver News Search")
    parser.add_argument("query", help="Search query")
    parser.add_argument("-p", "--page", type=int, default=1, help="Page number")
    parser.add_argument("-s", "--sort", default="0", choices=["0", "1", "2"], 
                        help="Sort: 0-Relevance, 1-Latest, 2-Oldest")
    parser.add_argument("-t", "--time", default="all", help="Period (all, 1h, 1d, 1w... or date range)")
    parser.add_argument("-f", "--format", default="compact", choices=["compact", "full", "json"])
    args = parser.parse_args()

    # 시간 파라미터 변환 (tbs 파라미터 형식으로)
    time_param = convert_time_to_tbs(args.time)
    
    # 네이버 뉴스는 period 파라미터를 지원하지 않을 수 있음
    # tbs 파라미터를 사용하여 시간 필터 적용
    params = {
        "engine": "naver",
        "query": args.query,
        "where": "news",
        "page": args.page,
        "sort": args.sort,
        "period": args.time,  # period는 유지 (네이버 호환성)
        "tbs": time_param  # Google 엔진 스타일의 tbs 파라미터
    }
    
    # SerpAPI Naver News 특이사항: sort=1(최신)이 가끔 공백을 반환하면 dd로 대체 시도 고려
    # 최적화: 검색어가 단어 하나이고 --time 옵션 사용 시 "뉴스"를 미리 추가
    if len(args.query.split()) == 1 and args.time != "all":
        params["query"] = f"{args.query} 뉴스"
    
    results = perform_search(params)
    
    # 네이버 뉴스에서 결과가 없을 때: 검색어 보강 로직 (단어만 검색 시)
    if "error" in results and ("Naver hasn't returned any results" in results["error"] or 
                                     "Search failed" in results.get("error", "")):
        # 검색어가 단어 하나인 경우 "뉴스" 추가하여 재시도
        if len(args.query.split()) == 1 and args.query.endswith("뉴스") == False:
            params["query"] = f"{args.query} 뉴스"
            results = perform_search(params)
    
    print(format_output(results, args.format, compact_formatter))

if __name__ == "__main__":
    main()
