import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import time
import random
import json

def get_weread_link(book_title):
    """
    专门用于搜索微信读书链接的辅助函数
    """
    try:
        # 搜索 wechat reading 域名
        query = f"site:weread.qq.com {book_title}"
        with DDGS() as ddgs:
            # 只取第1条最相关的结果
            results = list(ddgs.text(query, max_results=1))
            
        if results:
            url = results[0]['href']
            # 简单的校验，确保是微信读书的链接
            if "weread.qq.com" in url:
                return url
    except Exception:
        return None
    return None

def search_books_comprehensive(query: str, count: int = 3) -> str:
    """
    搜索豆瓣书籍，并尝试匹配微信读书链接。
    """
    
    # 1. 先搜豆瓣
    douban_query = f"site:book.douban.com/subject {query}"
    print(f"[Debug] Searching Douban for: {douban_query}")

    results = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    try:
        with DDGS() as ddgs:
            ddg_results = list(ddgs.text(douban_query, max_results=count + 3))

        processed_count = 0
        
        for res in ddg_results:
            if processed_count >= count:
                break

            url = res['href']
            # 过滤杂项链接
            if "book.douban.com/subject/" not in url or "/discussion" in url or "/review" in url:
                continue

            # 初始化书籍对象
            title_clean = res['title'].replace("(豆瓣)", "").strip()
            book_info = {
                "title": title_clean,
                "douban_link": url,
                "rating": "N/A",
                "summary": res['body'],
                "wechat_link": None  # 初始化为 None
            }

            # === Step 2: 抓取豆瓣详情 (为了精准评分) ===
            try:
                time.sleep(random.uniform(0.5, 1.0)) # 礼貌延时
                resp = requests.get(url, headers=headers, timeout=5)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    
                    # 修正标题
                    h1 = soup.find('h1')
                    if h1:
                        book_info['title'] = h1.get_text(strip=True)
                        title_clean = book_info['title'] # 更新用于搜索微信读书的标题

                    # 获取评分
                    rating_tag = soup.find('strong', class_='ll rating_num')
                    if rating_tag and rating_tag.text.strip():
                        book_info['rating'] = rating_tag.text.strip()
                    else:
                        book_info['rating'] = "暂无"
            except Exception as e:
                print(f"[Warn] Douban fetch error: {e}")

            # === Step 3: 搜索微信读书链接 (新增功能) ===
            # 只有当确定了书名后，再去搜微信读书，避免无效搜索
            print(f"[Debug] Finding WeChat Reading link for: {title_clean}")
            wechat_url = get_weread_link(title_clean)
            if wechat_url:
                book_info['wechat_link'] = wechat_url

            results.append(book_info)
            processed_count += 1

    except Exception as e:
        return json.dumps({"error": str(e)})

    return json.dumps(results, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # 测试代码
    print(search_books_comprehensive("置身事内", count=1))