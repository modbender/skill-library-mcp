#!/usr/bin/env python3
"""
Website crawler script
Input: URL
Output: JSON file with structured website content
"""
import sys
import json
import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def crawl_website(url):
    """Crawl main website content"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract title
    title = soup.title.string if soup.title else ""
    
    # Extract meta info
    meta_desc = ""
    meta_tags = soup.find_all('meta')
    for tag in meta_tags:
        if tag.get('name') == 'description':
            meta_desc = tag.get('content', '')
        if tag.get('property') == 'og:description':
            meta_desc = tag.get('content', '')
    
    # Extract headings
    headings = []
    
    # Extract nav links
    nav_links = []
    
    # Extract main content paragraphs
    content_blocks = []
    
    # Extract links
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('http'):
            links.append(href)
    
    result = {
        "url": url,
        "title": title,
        "meta_description": meta_desc,
        "headings": headings[:20],
        "nav_links": list(set(nav_links))[:10],
        "content_blocks": content_blocks[:15],
        "links": list(set(links))[:30]
    }
    
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 crawl_website.py <URL>")
        sys.exit(1)
    
    url = sys.argv[1]
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    result = crawl_website(url)
    
    output_file = "website_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Saved to: {output_file}")
    print(f"Title: {result.get('title', 'N/A')}")
    print(f"Content blocks extracted: {len(result.get('content_blocks', []))}")

if __name__ == "__main__":
    main()
