#!/usr/bin/env python3
"""
Batch generate schemas for multiple pages from sitemap.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: pip install requests beautifulsoup4")
    sys.exit(1)


def fetch_sitemap_urls(sitemap_url):
    """Extract URLs from sitemap.xml."""
    try:
        resp = requests.get(sitemap_url, timeout=10)
        if resp.status_code != 200:
            return []
        
        import xml.etree.ElementTree as ET
        root = ET.fromstring(resp.content)
        
        urls = []
        for elem in root.iter():
            if elem.tag.endswith('loc'):
                urls.append(elem.text.strip())
        
        return urls
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        return []


def detect_page_type(url, html):
    """Detect the best schema type for a page."""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Check for product indicators
    if any(x in url.lower() for x in ['/product', '/item', '/buy']):
        return "Product"
    
    # Check for blog/article indicators
    if any(x in url.lower() for x in ['/blog/', '/article/', '/post/', '/news/']):
        return "BlogPosting"
    
    # Check for FAQ indicators
    if 'faq' in url.lower() or soup.find('div', class_=re.compile('faq', re.I)):
        return "FAQPage"
    
    # Check for about/organization
    if any(x in url.lower() for x in ['/about', '/company']):
        return "Organization"
    
    # Check for contact/local business
    if 'contact' in url.lower():
        return "LocalBusiness"
    
    # Default to Article for content pages
    if soup.find('article') or soup.find('h1'):
        return "Article"
    
    return "WebPage"


def extract_schema_data(url, html, schema_type):
    """Extract data for a specific schema type."""
    soup = BeautifulSoup(html, 'html.parser')
    data = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "url": url
    }
    
    if schema_type in ["Article", "BlogPosting"]:
        title = soup.find('h1') or soup.title
        if title:
            data["headline"] = title.get_text(strip=True)
        
        meta = soup.find('meta', attrs={'name': 'description'}) or \
               soup.find('meta', attrs={'property': 'og:description'})
        if meta:
            data["description"] = meta.get('content', '')
        
        author = soup.find('meta', attrs={'name': 'author'})
        if author:
            data["author"] = {"@type": "Person", "name": author.get('content', '')}
        
        from datetime import datetime
        data["datePublished"] = datetime.now().strftime("%Y-%m-%d")
    
    elif schema_type == "Organization":
        title = soup.title.get_text(strip=True) if soup.title else ""
        data["name"] = title.split('-')[0].split('|')[0].strip()
        
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta:
            data["description"] = meta.get('content', '')
    
    elif schema_type == "Product":
        title = soup.find('h1') or soup.title
        if title:
            data["name"] = title.get_text(strip=True)
    
    return data


def main():
    parser = argparse.ArgumentParser(description="Batch generate schemas from sitemap")
    parser.add_argument("sitemap", help="Sitemap URL or file path")
    parser.add_argument("--output-dir", "-o", default="./schemas", help="Output directory")
    parser.add_argument("--limit", "-l", type=int, default=50, help="Max pages to process")
    parser.add_argument("--delay", "-d", type=float, default=1.0, help="Delay between requests")
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get URLs
    if args.sitemap.startswith('http'):
        print(f"Fetching sitemap: {args.sitemap}")
        urls = fetch_sitemap_urls(args.sitemap)
    else:
        with open(args.sitemap, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    
    print(f"Found {len(urls)} URLs")
    urls = urls[:args.limit]
    print(f"Processing first {len(urls)} URLs...")
    
    # Process each URL
    results = []
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] {url}")
        
        try:
            import time
            time.sleep(args.delay)
            
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                print(f"  ⚠️  HTTP {resp.status_code}")
                continue
            
            # Detect type and generate schema
            schema_type = detect_page_type(url, resp.text)
            print(f"  Detected type: {schema_type}")
            
            schema = extract_schema_data(url, resp.text, schema_type)
            
            # Save individual file
            safe_name = url.replace('https://', '').replace('http://', '').replace('/', '_')[:100]
            output_file = output_dir / f"{safe_name}.json"
            with open(output_file, 'w') as f:
                json.dump(schema, f, indent=2)
            print(f"  ✅ Saved: {output_file}")
            
            results.append({
                "url": url,
                "type": schema_type,
                "file": str(output_file)
            })
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Save summary
    summary_file = output_dir / "summary.json"
    with open(summary_file, 'w') as f:
        json.dump({
            "total": len(urls),
            "successful": len(results),
            "results": results
        }, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Batch complete!")
    print(f"Generated {len(results)} schemas")
    print(f"Summary: {summary_file}")
    print('='*60)


if __name__ == "__main__":
    main()
