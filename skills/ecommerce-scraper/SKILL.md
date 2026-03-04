---
name: ecommerce-scraper
version: 1.0.0
description: 爬取动态电商网站数据。使用Playwright处理JavaScript渲染的页面，支持Cloudflare反爬、隐躲API发现、分页抓取。适用于： (1) 爬取京东/淘宝/拼多多等中国电商， (2) 爬取Amazon/eBay等国际电商， (3) 价格监控和竞品分析， (4) 批量商品数据采集。
---

# E-commerce Scraper

电商动态网站爬虫技能，基于Playwright处理JavaScript渲染。

## 快速开始

### 基础爬取

```python
from playwright.sync_api import sync_playwright

def scrape_page(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        content = page.content()
        browser.close()
        return content
```

### 完整示例：爬取商品列表

```python
from playwright.sync_api import sync_playwright
import json
import re

def scrape_ecommerce_products(url, max_pages=3):
    """爬取电商商品数据"""
    products = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        # 绕过Cloudflare检测
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        for page_num in range(1, max_pages + 1):
            print(f"爬取第 {page_num} 页...")
            page.goto(f"{url}?page={page_num}", wait_until="networkidle", timeout=30000)
            
            # 等待商品加载
            try:
                page.wait_for_selector('.product-item, .goods-item, [class*="product"]', timeout=10000)
            except:
                pass
            
            # 提取商品数据
            items = page.query_selector_all('div[class*="product"], li[class*="item"], .goods-item')
            
            for item in items:
                try:
                    product = {
                        'title': item.query_selector('a[class*="title"], h3, .product-title')?.inner_text().strip(),
                        'price': item.query_selector('[class*="price"], .sale-price, .real-price')?.inner_text().strip(),
                        'link': item.query_selector('a')?.get_attribute('href'),
                        'image': item.query_selector('img')?.get_attribute('src'),
                    }
                    if product['title']:
                        products.append(product)
                except Exception as e:
                    print(f"提取错误: {e}")
            
            # 检查是否有下一页
            next_btn = page.query_selector('button:has-text("下一页"), a:has-text("下一页")')
            if not next_btn:
                break
        
        browser.close()
    
    return products
```

## 核心技巧

### 1. 发现隐藏API (最重要!)

不要直接爬页面，先找API:

```python
def find_hidden_api(url):
    """发现页面隐藏的API端点"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 监听所有网络请求
        api_requests = []
        page.on("response", lambda response: 
            api_requests.append(response.url) 
            if "api" in response.url.lower() or "json" in response.url.lower() 
            else None
        )
        
        page.goto(url, wait_until="networkidle")
        browser.close()
        
        return [r for r in api_requests if r.startswith('http')]
```

**找API技巧:**
- 打开DevTools → Network → 过滤 XHR/Fetch
- 搜索 `__NEXT_DATA__` (Next.js)
- 搜索 `window.__INITIAL_STATE__`
- 查找 `/api/` 结尾的请求

### 2. 绕过Cloudflare

```python
def bypass_cloudflare(url):
    """绕过Cloudflare保护"""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  # 非headless更容易通过
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
            ]
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
        )
        
        page = context.new_page()
        
        # 注入脚本隐藏自动化特征
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
            Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});
        """)
        
        page.goto(url)
        
        # 等待Cloudflare验证完成
        try:
            page.wait_for_selector('body', timeout=15000)
            print("✅ Cloudflare bypassed!")
        except:
            print("⚠️ 可能需要手动验证")
        
        content = page.content()
        browser.close()
        return content
```

### 3. 分页爬取

```python
def scrape_with_pagination(base_url, max_pages=10):
    """分页爬取所有商品"""
    all_products = []
    page_num = 1
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        while page_num <= max_pages:
            url = f"{base_url}&page={page_num}" if '?' in base_url else f"{base_url}?page={page_num}"
            print(f"爬取第 {page_num}/{max_pages} 页: {url}")
            
            page = browser.new_page()
            try:
                page.goto(url, wait_until="networkidle", timeout=30000)
            except Exception as e:
                print(f"页面加载失败: {e}")
                break
            
            # 检查是否最后一页
            next_btn = page.query_selector('button:has-text("下一页"), a:has-text("下一页")')
            if not next_btn:
                print("没有更多页面了")
                break
            
            # 提取数据...
            page_num += 1
            browser.close()
    
    return all_products
```

### 4. 常见电商平台选择器

```python
# 平台特定选择器
SELECTORS = {
    'jd': {
        'product': '.gl-item',
        'title': '.p-name em',
        'price': '.p-price strong i',
        'shop': '.p-shop',
    },
    'taobao': {
        'product': '.item',
        'title': '.title',
        'price': '.price',
        'shop': '.shop',
    },
    'amazon': {
        'product': '[data-component-type="s-search-result"]',
        'title': 'h2 a span',
        'price': '.a-price-whole',
        'rating': '.a-icon-alt',
    },
    'generic': {
        'product': '[class*="product"], [class*="item"], [data-testid*="product"]',
        'title': '[class*="title"], h2, h3, a[class*="title"]',
        'price': '[class*="price"], [class*="cost"], [class*="amount"]',
    }
}
```

## 脚本资源

### scripts/scrape.py

通用电商爬虫脚本 (基础版):

```bash
python3 scripts/scrape.py scrape --url "https://example.com/products" --max-pages 5 --output products.json
```

### scripts/scrape_v2.py

**支持登录的增强版** (推荐):

```bash
# 1. 扫码登录 (会打开浏览器窗口)
python3 scripts/scrape_v2.py login --platform jd
python3 scripts/scrape_v2.py login --platform taobao

# 2. 登录后自动保存Cookie，之后爬取无需再登录
python3 scripts/scrape_v2.py scrape --platform jd --keyword "燃气烤箱灶" --max-pages 3 --output result.json
```

**支持平台**: `jd` (京东), `taobao` (淘宝), `pdd` (拼多多)

### scripts/api_discovery.py

隐藏API发现脚本:

```bash
python3 scripts/api_discovery.py "https://example.com"
```

### scripts/cloudflare_bypass.py

Cloudflare绕过脚本:

```bash
python3 scripts/cloudflare_bypass.py "https://example.com" --output page.html
```

## 常见问题

### Q: 爬取速度慢怎么办?
```python
# 使用并发加速
from concurrent.futures import ThreadPoolExecutor

def scrape_concurrently(urls):
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(scrape_page, urls)
    return list(results)
```

### Q: 被封IP怎么办?
1. 使用代理: `browser = p.chromium.launch(proxy={"server": "http://proxy"})`
2. 添加随机延迟: `time.sleep(random.uniform(1, 3))`
3. 轮换User-Agent

### Q: 数据提取不完整?
1. 检查是否需要滚动加载: `page.evaluate("window.scrollTo(0, document.body.scrollHeight)")`
2. 等待懒加载: `page.wait_for_load_state("networkidle")`
3. 使用JavaScript渲染: `page.evaluate("document.querySelectorAll...")`

### Q: 选择器失效?
- 使用属性选择器: `[data-testid="product-title"]`
- 使用文本匹配: `page.locator("text=立即购买")`
- 使用CSS和XPath组合

## 反爬注意事项

1. **遵守robots.txt**: `page.goto(url + "/robots.txt")`
2. **设置合理间隔**: 每次请求间隔1-3秒
3. **使用真实浏览器**: 避免被检测为自动化
4. **处理验证码**: 遇到验证码时暂停或通知人类

## 输出格式

爬取结果可保存为:

```json
[
  {
    "title": "商品名称",
    "price": "¥99.00",
    "shop": "店铺名",
    "link": "https://...",
    "image": "https://...",
    "collected_at": "2026-02-26T15:00:00Z"
  }
]
```
