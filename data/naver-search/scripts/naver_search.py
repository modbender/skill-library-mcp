#!/usr/bin/env python3
"""
Naver Search Aggregator (Integrated Wrapper)
모든 카테고리(웹, 뉴스, 쇼핑, 이미지, 비디오)의 결과를 취합하여 한 번에 보여줍니다.
"""

import sys
import os
import argparse
import subprocess
import json

def run_script(script_name, query, extra_args=None):
    """개별 스크립트를 실행하여 JSON 결과를 반환합니다."""
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    cmd = ["python3", script_path, query, "--format", "json"]
    if extra_args:
        cmd.extend(extra_args)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception:
        return None

def main():
    parser = argparse.ArgumentParser(description="Naver Search Aggregator")
    parser.add_argument("query", help="검색어")
    parser.add_argument("-e", "--engine", default="naver",
                        choices=["naver", "naver_news", "naver_shopping", "naver_images", "naver_videos", "naver_booking"],
                        help="검색 엔진 (default: naver)")
    parser.add_argument("-f", "--format", default="compact", choices=["compact", "full", "json"],
                        help="출력 포맷")
    
    # 하위 스크립트용 인자들 (라우팅 시 사용)
    parser.add_argument("-p", "--page", type=int, default=1)
    parser.add_argument("-n", "--num", type=int)
    parser.add_argument("-s", "--sort")
    parser.add_argument("-t", "--time")

    args, unknown = parser.parse_known_args()

    # 1. 개별 엔진 검색 (Routing)
    if args.engine != "naver":
        script_map = {
            "naver_news": ("naver_news.py", ["-p", "-s", "-t"]),
            "naver_shopping": ("naver_shopping.py", ["-p", "-s"]),
            "naver_images": ("naver_images.py", ["-n"]),
            "naver_videos": ("naver_video.py", ["-p"]),
            "naver_booking": ("naver_booking.py", []),
        }
        target_script, supported = script_map.get(args.engine, ("naver_web.py", []))
        cmd = ["python3", os.path.join(os.path.dirname(__file__), target_script), args.query, "--format", args.format]
        if "-p" in supported: cmd.extend(["--page", str(args.page)])
        if "-n" in supported and args.num: cmd.extend(["--num", str(args.num)])
        if "-s" in supported and args.sort: cmd.extend(["--sort", args.sort])
        if "-t" in supported and args.time: cmd.extend(["--time", args.time])
        subprocess.run(cmd)
        return

    # 2. 통합 검색 (Aggregating)
    if args.format == "json":
        # 모든 결과를 취합하여 하나의 JSON으로 반환
        combined = {
            "web": run_script("naver_web.py", args.query),
            "news": run_script("naver_news.py", args.query),
            "shopping": run_script("naver_shopping.py", args.query),
            "images": run_script("naver_images.py", args.query),
            "videos": run_script("naver_video.py", args.query)
        }
        print(json.dumps(combined, indent=2, ensure_ascii=False))
        return

    # Compact/Full 포맷 - 요약 출력
    print(f"\n🔍 '{args.query}'에 대한 네이버 통합 검색 결과\n" + "="*50)
    
    # 뉴스 (최신순)
    news = run_script("naver_news.py", args.query, ["--sort", "1"])
    if news and news.get("news_results"):
        print("\n📰 최신 뉴스")
        for res in news["news_results"][:3]:
            news_info = res.get('news_info', {})
            source = news_info.get('press_name', res.get('source', ''))
            date = news_info.get('news_date', res.get('date', ''))
            info = f" ({source} | {date})" if source or date else ""
            print(f"  • {res.get('title')}{info}")
    
    # 쇼핑
    shopping = run_script("naver_shopping.py", args.query)
    if shopping and shopping.get("shopping_results"):
        print("\n🛒 쇼핑 트렌드")
        for res in shopping["shopping_results"][:3]:
            price = f"[{res.get('price')}]" if res.get('price') else ""
            print(f"  • {res.get('title')} {price}")

    # 이미지
    images = run_script("naver_images.py", args.query, ["--num", "3"])
    if images and images.get("images_results"):
        print("\n🖼️ 이미지")
        titles = [res.get('title', '이미지') for res in images["images_results"][:3]]
        print(f"  • {', '.join(titles)}")

    # 비디오
    videos = run_script("naver_video.py", args.query)
    if videos and videos.get("video_results"):
        print("\n🎥 비디오")
        for res in videos["video_results"][:2]:
            print(f"  • {res.get('title')} ({res.get('source', '')})")

    # 웹 결과 요약
    web = run_script("naver_web.py", args.query)
    if web and web.get("organic_results"):
        print("\n📊 웹 검색 결과 (추천)")
        for res in web["organic_results"][:3]:
            print(f"  • {res.get('title')} - {res.get('link')}")

    print("\n" + "="*50 + "\n💡 상세 정보는 -e [엔진명] 옵션으로 확인하세요. (ex: -e naver_news)")

if __name__ == "__main__":
    main()
