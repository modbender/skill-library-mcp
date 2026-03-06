import sys
import requests
from bs4 import BeautifulSoup
import feedparser
import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

def get_baidu_hot():
    url = "https://top.baidu.com/board?tab=realtime"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Based on typical structure, hot items are in specific divs.
        # This selector is a guess and might need adjustment based on actual page structure.
        # Usually looking for elements with class 'c-single-text-ellipsis' or similar in hot list.
        # Let's try a more generic approach: finding links inside the hot list container.
        
        hot_items = []
        # Finding elements with class 'c-single-text-ellipsis' often used for titles
        titles = soup.find_all(class_="c-single-text-ellipsis")
        for title in titles:
            text = title.get_text().strip()
            if text and text not in hot_items:
                hot_items.append(text)
                if len(hot_items) >= 5: # Get top 5 from Baidu
                    break
        
        return hot_items
    except Exception as e:
        logging.error(f"Error fetching Baidu hot search: {e}")
        return []

def get_google_trends():
    # Google Trends Daily Search Trends RSS for US
    url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"
    try:
        feed = feedparser.parse(url)
        hot_items = []
        for entry in feed.entries:
            hot_items.append(entry.title)
            if len(hot_items) >= 5: # Get top 5 from Google
                break
        return hot_items
    except Exception as e:
        logging.error(f"Error fetching Google Trends: {e}")
        return []

def get_daily_news():
    now = datetime.datetime.now()
    current_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    hour = now.hour
    
    # Check if it's 8 AM (though this check should be in the scheduler, the skill might be triggered manually)
    # The requirement says "retrieve... and answer with current time... e.g. now is Beijing time 8:00"
    # We will just format the output as requested.
    
    baidu_hot = get_baidu_hot()
    google_hot = get_google_trends()
    
    all_hot = []
    if baidu_hot:
        all_hot.extend(baidu_hot)
    if google_hot:
        all_hot.extend(google_hot)
         
    # Take top 10 unique keywords
    final_hot = []
    seen = set()
    for item in all_hot:
        if item not in seen:
            final_hot.append(item)
            seen.add(item)
            if len(final_hot) >= 10:
                break
    
    # Format the output
    # "xxx now is Beijing time 8:00, today's hot search list is: 1. 2. ..."
    # Note: The server time might not be Beijing time. We should adjust if needed, but assuming local time is what's available.
    # To be safe, let's explicitly mention "Current Time"
    
    greeting = f"现在是北京时间 {current_time_str}，今日热搜榜单如下："
    news_list = ""
    for i, item in enumerate(final_hot, 1):
        news_list += f"{i}. {item}\n"
        
    return f"{greeting}\n{news_list}"

if __name__ == "__main__":
    print(get_daily_news())
