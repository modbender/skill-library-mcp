# Spider Recipes

## Recipe 1: E-commerce Product Crawler

```python
from scrapling.spiders import Spider, Response

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://shop.example.com/products"]
    concurrent_requests = 5
    download_delay = 2.0
    
    custom_settings = {
        "RETRY_TIMES": 3,
        "RETRY_DELAY": 5,
    }
    
    async def parse(self, response: Response):
        # Extract products
        for product in response.css('.product-card'):
            yield {
                "name": product.css('.product-name::text').get(),
                "price": product.css('.price::text').get(),
                "rating": product.css('.rating::attr(data-score)').get(),
                "url": product.css('a::attr(href)').get(),
                "extracted_at": datetime.now().isoformat(),
            }
        
        # Follow pagination
        next_page = response.css('.pagination .next::attr(href)').get()
        if next_page:
            yield response.follow(next_page)

# Run with resume
result = ProductSpider(crawldir="./crawl_products").start()
result.items.to_jsonl("products.jsonl")
```

## Recipe 2: Sitemap Crawler

```python
from scrapling.spiders import Spider
import xml.etree.ElementTree as ET

class SitemapSpider(Spider):
    name = "sitemap"
    
    def start_requests(self):
        # Fetch sitemap
        sitemap = Fetcher.get('https://example.com/sitemap.xml')
        root = ET.fromstring(sitemap.body)
        
        for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
            yield Request(url.text, callback=self.parse_page)
    
    async def parse_page(self, response):
        yield {
            "url": response.url,
            "title": response.css('h1::text').get(),
            "word_count": len(response.css('p::text').getall()),
        }
```

## Recipe 3: API-First Spider

```python
class APISpider(Spider):
    """Scrape via API endpoints instead of HTML."""
    
    name = "api_products"
    api_base = "https://api.example.com/v1"
    
    def start_requests(self):
        for page in range(1, 100):
            yield Request(
                f"{self.api_base}/products?page={page}",
                headers={"Authorization": "Bearer TOKEN"},
            )
    
    async def parse(self, response):
        data = response.json()
        for product in data['products']:
            yield product
        
        # Stop when no more results
        if not data['products']:
            raise StopIteration
```

## Recipe 4: Multi-Domain Crawl with Different Handlers

```python
class MultiDomainSpider(Spider):
    name = "multi"
    
    domain_handlers = {
        "shop.example.com": "parse_shop",
        "blog.example.com": "parse_blog",
    }
    
    async def parse(self, response):
        domain = urlparse(response.url).netloc
        handler = getattr(self, self.domain_handlers.get(domain, "parse_default"))
        async for item in handler(response):
            yield item
    
    async def parse_shop(self, response):
        for product in response.css('.product'):
            yield {"type": "product", "data": product.css('h2::text').get()}
    
    async def parse_blog(self, response):
        for article in response.css('article'):
            yield {"type": "article", "data": article.css('h1::text').get()}
```

## Recipe 5: Streaming with Real-time Processing

```python
class StreamingSpider(Spider):
    name = "streaming"
    start_urls = ["https://example.com/items"]
    
    async def parse(self, response):
        for item in response.css('.item'):
            yield {
                "id": item.css('::attr(data-id)').get(),
                "content": item.css('.content::text').get(),
            }

# Consume as stream
spider = StreamingSpider()
async for item in spider.stream():
    print(f"Got item: {item['id']}")
    # Send to database, queue, etc.
```

## Recipe 6: Deep Crawl with Depth Limit

```python
class DeepCrawlSpider(Spider):
    name = "deep_crawl"
    start_urls = ["https://example.com"]
    max_depth = 3
    
    async def parse(self, response):
        depth = response.meta.get('depth', 0)
        
        yield {
            "url": response.url,
            "depth": depth,
            "title": response.css('title::text').get(),
        }
        
        if depth < self.max_depth:
            for link in response.css('a::attr(href)').getall():
                yield response.follow(link, meta={'depth': depth + 1})
```

## Recipe 7: Form Submission Spider

```python
from scrapling.spiders import Spider, FormRequest

class FormSpider(Spider):
    name = "form_search"
    
    def start_requests(self):
        for keyword in ['python', 'scraping', 'data']:
            yield FormRequest(
                url="https://example.com/search",
                formdata={"q": keyword, "category": "all"},
                callback=self.parse_results,
                meta={"keyword": keyword}
            )
    
    async def parse_results(self, response):
        keyword = response.meta['keyword']
        for result in response.css('.search-result'):
            yield {
                "keyword": keyword,
                "title": result.css('h3::text').get(),
                "snippet": result.css('.snippet::text').get(),
            }
```

## Recipe 8: Image/Media Downloader

```python
import os
from urllib.parse import urlparse

class MediaSpider(Spider):
    name = "media"
    download_dir = "./downloads"
    
    async def parse(self, response):
        for img in response.css('img::attr(src)').getall():
            ext = os.path.splitext(urlparse(img).path)[1] or '.jpg'
            filename = f"{hash(img)}{ext}"
            yield response.follow(img, callback=self.save_image, meta={'filename': filename})
    
    async def save_image(self, response):
        path = os.path.join(self.download_dir, response.meta['filename'])
        with open(path, 'wb') as f:
            f.write(response.body)
        yield {"downloaded": path}
```

## Pause/Resume Best Practices

```python
# Start with checkpoint directory
spider = MySpider(crawldir="./crawl_checkpoint")
result = spider.start()

# If interrupted, restart with same crawldir
# Spider automatically resumes from last checkpoint

# To reset and start fresh:
import shutil
shutil.rmtree("./crawl_checkpoint")
spider.start()
```

## Error Handling Patterns

```python
class RobustSpider(Spider):
    name = "robust"
    
    async def parse(self, response):
        try:
            title = response.css('h1::text').get()
            if not title:
                self.logger.warning(f"No title found: {response.url}")
                return
            
            yield {"title": title, "url": response.url}
            
        except Exception as e:
            self.logger.error(f"Error parsing {response.url}: {e}")
            # Spider continues with other requests
```
