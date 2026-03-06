import asyncio
import aiohttp
import argparse
import json
import sys

# 模擬搜尋函數 (實務上可串接 Google Custom Search API 或簡單抓取 DuckDuckGo)
async def fetch_search_result(session, query, max_results):
    # 這裡以 Mock 資料示範並行效果，實際開發可替換為真正的 Request
    url = f"[https://api.duckduckgo.com/?q=](https://api.duckduckgo.com/?q=){query}&format=json"
    try:
        async with session.get(url, timeout=5) as response:
            data = await response.json()
            # 簡化回傳結果
            result = {
                "query": query,
                "source": "DuckDuckGo API",
                "abstract": data.get("AbstractText", "無摘要內容"),
                "url": data.get("AbstractURL", "")
            }
            return result
    except Exception as e:
        return {"query": query, "error": str(e)}

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", nargs="+", required=True, help="搜尋關鍵字列表")
    parser.add_argument("--max", type=int, default=3, help="每個關鍵字的最大結果數")
    args = parser.parse_args()

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_search_result(session, q, args.max) for q in args.queries]
        # 並行執行所有任務
        results = await asyncio.gather(*tasks)
        
        # 將結果印出成 JSON，OpenClaw 會捕獲 Standard Output 傳給 AI
        print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())