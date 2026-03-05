import sys
import json
from scrapling import StealthyFetcher

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No query provided"}))
        sys.exit(1)
        
    query = sys.argv[1]
    fetcher = StealthyFetcher()
    url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
    
    try:
        page = fetcher.fetch(url)
        results = []
        for block in page.css('div.result'):
            title = block.css('a.result__a::text').get()
            link = block.css('a.result__a::attr(href)').get()
            snippet = block.css('a.result__snippet::text').get()
            if title and link:
                results.append({"source": "scrapling", "title": title, "link": link, "snippet": snippet})
        print(json.dumps(results))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
