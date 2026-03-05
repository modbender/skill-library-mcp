import requests
import xml.etree.ElementTree as ET
import json
import argparse
from textblob import TextBlob

RSS_FEEDS = [
    "https://cointelegraph.com/rss",
    "https://www.coindesk.com/arc/outboundfeeds/rss/"
]

def fetch_rss_news(feed_url, limit=5):
    news_items = []
    try:
        response = requests.get(feed_url, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            count = 0
            for item in root.findall('.//item'):
                if count >= limit:
                    break
                
                title = item.find('title').text if item.find('title') is not None else "No Title"
                description = item.find('description').text if item.find('description') is not None else ""
                
                news_items.append({
                    "source": feed_url,
                    "title": title,
                    "description": description[:200] + "..." if len(description) > 200 else description
                })
                count += 1
    except Exception as e:
        print(f"Error fetching {feed_url}: {e}", file=sys.stderr)
    return news_items

def analyze_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity

def main():
    parser = argparse.ArgumentParser(description='Fetch crypto news and sentiment.')
    args = parser.parse_args()

    all_news = []
    for feed in RSS_FEEDS:
        all_news.extend(fetch_rss_news(feed))

    processed_news = []
    for news in all_news:
        sentiment = analyze_sentiment(news['title'] + " " + news['description'])
        sentiment_label = "NEUTRAL"
        if sentiment > 0.1:
            sentiment_label = "POSITIVE"
        elif sentiment < -0.1:
            sentiment_label = "NEGATIVE"
        
        processed_news.append({
            "title": news['title'],
            "sentiment_score": round(sentiment, 2),
            "sentiment_label": sentiment_label
        })

    print(json.dumps(processed_news, indent=2))

if __name__ == "__main__":
    import sys
    main()
