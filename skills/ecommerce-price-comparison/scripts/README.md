# 抓取脚本说明

本目录包含各电商平台的价格抓取脚本。

## 脚本列表

### 核心抓取脚本
1. `jd_scraper.py` - 京东价格抓取
2. `taobao_scraper.py` - 淘宝价格抓取
3. `tmall_scraper.py` - 天猫价格抓取
4. `pdd_scraper.py` - 拼多多价格抓取

### 辅助脚本
5. `price_comparator.py` - 价格比较和评分
6. `report_generator.py` - 生成比较报告
7. `price_history.py` - 价格历史追踪
8. `batch_processor.py` - 批量处理

## 环境要求

### Python版本
- Python 3.8+
- 建议使用虚拟环境

### 依赖包
```bash
pip install playwright beautifulsoup4 requests pandas numpy
playwright install chromium
```

### 可选依赖
```bash
# 数据可视化
pip install matplotlib seaborn

# 数据库存储
pip install sqlite3 pymongo

# 异步处理
pip install aiohttp asyncio
```

## 使用说明

### 基本调用
```python
from jd_scraper import JDScraper

# 初始化抓取器
scraper = JDScraper()

# 搜索商品
products = scraper.search("iPhone 15")

# 获取商品详情
product_details = scraper.get_product_details(products[0]['url'])

# 获取价格
price_info = scraper.get_price(product_details['product_id'])
```

### 配置文件
创建 `config.yaml` 文件：

```yaml
# 代理设置
proxy:
  enabled: false
  http: "http://proxy.example.com:8080"
  https: "https://proxy.example.com:8080"

# 请求设置
request:
  timeout: 30
  retry_times: 3
  delay_between_requests: 1.0

# 浏览器设置
browser:
  headless: true
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# 平台特定设置
platforms:
  jd:
    use_mobile_api: true
  taobao:
    use_playwright: true
  pdd:
    check_baoyou: true
```

## 脚本详细说明

### jd_scraper.py

#### 功能
- 京东商品搜索
- 价格信息获取
- 优惠券信息提取
- 评价数据抓取

#### 主要类和方法
```python
class JDScraper:
    def search(self, keyword, page=1, sort='default'):
        """搜索商品"""
        
    def get_product_details(self, url):
        """获取商品详情"""
        
    def get_price(self, sku_id):
        """获取价格信息"""
        
    def get_promotions(self, sku_id):
        """获取促销信息"""
```

### taobao_scraper.py

#### 功能
- 淘宝商品搜索
- 价格和销量获取
- 店铺信息提取
- 反爬机制处理

#### 注意事项
- 淘宝反爬严格，需要频繁更换IP
- 建议使用浏览器自动化
- 注意处理登录状态

### tmall_scraper.py

#### 功能
- 天猫商品搜索
- 品牌官方店识别
- 正品保障信息
- 售后服务信息

#### 特点
- 数据结构相对规范
- 品牌信息完整
- 价格相对稳定

### pdd_scraper.py

#### 功能
- 拼多多商品搜索
- 百亿补贴识别
- 团购价格获取
- 运费政策解析

#### 特点
- 价格波动大
- 促销活动多
- 需要仔细计算实际成本

## 错误处理

### 常见错误
1. **网络错误**: 请求超时、连接失败
2. **解析错误**: 页面结构变化
3. **反爬错误**: IP被封、验证码
4. **数据错误**: 价格格式异常

### 重试机制
```python
def safe_request(url, max_retries=3):
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=30)
            return response
        except Exception as e:
            if i == max_retries - 1:
                raise
            time.sleep(2 ** i)  # 指数退避
```

## 性能优化

### 并发处理
```python
import asyncio
from aiohttp import ClientSession

async def fetch_multiple(urls):
    async with ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

### 缓存机制
```python
from functools import lru_cache
import json
import os

class CachedScraper:
    def __init__(self, cache_dir='cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_cached(self, key, ttl=3600):
        """获取缓存数据"""
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        if os.path.exists(cache_file):
            if time.time() - os.path.getmtime(cache_file) < ttl:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        return None
```

## 测试

### 单元测试
```python
import unittest
from jd_scraper import JDScraper

class TestJDScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = JDScraper()
    
    def test_search(self):
        results = self.scraper.search("测试商品")
        self.assertIsInstance(results, list)
    
    def test_price_format(self):
        price = self.scraper.get_price("100000000001")
        self.assertRegex(price, r'^\d+(\.\d{2})?$')
```

### 集成测试
```bash
# 运行所有测试
python -m pytest tests/

# 运行特定平台测试
python -m pytest tests/test_jd_scraper.py

# 生成测试报告
python -m pytest --html=report.html
```

## 维护指南

### 定期检查
1. **每周**: 检查各脚本是否正常工作
2. **每月**: 更新反爬策略和用户代理
3. **每季度**: 检查API变化和页面结构更新

### 日志记录
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
```

## 贡献指南

### 代码规范
- 遵循PEP 8
- 添加类型提示
- 编写文档字符串
- 包含单元测试

### 提交流程
1. Fork仓库
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 许可证
本项目采用MIT许可证。详见LICENSE文件。