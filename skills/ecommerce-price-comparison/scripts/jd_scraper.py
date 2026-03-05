#!/usr/bin/env python3
"""
京东价格抓取脚本
用于从京东平台抓取商品价格、促销信息和评价数据
"""

import json
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

import requests
from bs4 import BeautifulSoup

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ProductInfo:
    """商品信息数据结构"""
    platform: str = "jd"
    product_id: str = ""
    title: str = ""
    price: float = 0.0
    original_price: float = 0.0
    discount: str = ""
    shipping_fee: float = 0.0
    rating: float = 0.0
    review_count: int = 0
    shop_name: str = ""
    shop_rating: float = 0.0
    url: str = ""
    timestamp: str = ""
    promotions: List[str] = None
    stock_status: str = "有货"
    
    def __post_init__(self):
        if self.promotions is None:
            self.promotions = []
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class JDScraper:
    """京东抓取器"""
    
    def __init__(self, use_mobile_api: bool = True, timeout: int = 30):
        """
        初始化京东抓取器
        
        Args:
            use_mobile_api: 是否使用移动端API（推荐）
            timeout: 请求超时时间（秒）
        """
        self.use_mobile_api = use_mobile_api
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://m.jd.com/'
        })
        
        # API端点
        self.search_api = 'https://so.m.jd.com/ware/search.action'
        self.price_api = 'https://p.3.cn/prices/mgets'
        self.product_api = 'https://item.m.jd.com/product/{sku_id}.html'
    
    def extract_sku_from_url(self, url: str) -> Optional[str]:
        """
        从京东URL中提取SKU ID
        
        Args:
            url: 京东商品URL
            
        Returns:
            SKU ID或None
        """
        import re
        
        # 匹配多种京东URL格式
        patterns = [
            r'item\.jd\.com/(\d+)\.html',  # PC端
            r'item\.m\.jd\.com/product/(\d+)\.html',  # 移动端
            r'product/(\d+)\.html',  # 简化格式
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        logger.warning(f"无法从URL提取SKU: {url}")
        return None
    
    def search(self, keyword: str, page: int = 1, sort: str = 'default') -> List[Dict[str, Any]]:
        """
        搜索商品
        
        Args:
            keyword: 搜索关键词
            page: 页码
            sort: 排序方式（default/price/comment）
            
        Returns:
            商品列表
        """
        params = {
            'keyword': keyword,
            'page': page,
            'sort': sort,
            'pageSize': 20
        }
        
        try:
            response = self.session.get(
                self.search_api,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # 解析响应
            data = response.json()
            products = []
            
            for item in data.get('wareList', []):
                product = {
                    'product_id': item.get('wareId', ''),
                    'title': item.get('wname', ''),
                    'price': float(item.get('jdPrice', 0)),
                    'original_price': float(item.get('mprice', 0)),
                    'image_url': item.get('imageurl', ''),
                    'good_rate': float(item.get('goodRate', 0)) * 100,
                    'comment_count': int(item.get('totalCount', 0)),
                    'shop_id': item.get('shopId', ''),
                    'shop_name': item.get('shopName', ''),
                    'url': f"https://item.m.jd.com/product/{item.get('wareId', '')}.html"
                }
                products.append(product)
            
            logger.info(f"搜索 '{keyword}' 找到 {len(products)} 个商品")
            return products
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []
    
    def get_product_details(self, url: str) -> Optional[ProductInfo]:
        """
        获取商品详情
        
        Args:
            url: 商品URL
            
        Returns:
            商品详情信息
        """
        sku_id = self.extract_sku_from_url(url)
        if not sku_id:
            return None
        
        try:
            # 获取商品页面
            product_url = self.product_api.format(sku_id=sku_id)
            response = self.session.get(product_url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取商品信息（简化版，实际需要更复杂的解析）
            title_elem = soup.find('div', class_='sku-name')
            title = title_elem.text.strip() if title_elem else ""
            
            price_elem = soup.find('span', class_='price')
            price = float(price_elem.text.strip().replace('¥', '')) if price_elem else 0.0
            
            # 获取价格信息
            price_info = self.get_price(sku_id)
            
            product = ProductInfo(
                product_id=sku_id,
                title=title,
                price=price,
                original_price=price_info.get('original_price', price),
                url=url,
                shop_name=price_info.get('shop_name', ''),
                shop_rating=price_info.get('shop_rating', 0.0)
            )
            
            # 获取促销信息
            promotions = self.get_promotions(sku_id)
            product.promotions = promotions
            
            logger.info(f"获取商品详情成功: {sku_id} - {title}")
            return product
            
        except Exception as e:
            logger.error(f"获取商品详情失败: {e}")
            return None
    
    def get_price(self, sku_id: str) -> Dict[str, Any]:
        """
        获取价格信息
        
        Args:
            sku_id: 商品SKU ID
            
        Returns:
            价格信息字典
        """
        params = {
            'skuIds': f'J_{sku_id}',
            'type': '1'
        }
        
        try:
            response = self.session.get(
                self.price_api,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            if data and len(data) > 0:
                price_data = data[0]
                return {
                    'price': float(price_data.get('p', 0)),
                    'original_price': float(price_data.get('m', 0)),
                    'sku_id': sku_id,
                    'price_text': price_data.get('p', '0')
                }
            
            return {'price': 0, 'original_price': 0, 'sku_id': sku_id}
            
        except Exception as e:
            logger.error(f"获取价格失败: {e}")
            return {'price': 0, 'original_price': 0, 'sku_id': sku_id}
    
    def get_promotions(self, sku_id: str) -> List[str]:
        """
        获取促销信息
        
        Args:
            sku_id: 商品SKU ID
            
        Returns:
            促销信息列表
        """
        # 这里简化处理，实际需要调用京东促销API
        promotions = []
        
        try:
            # 示例：获取优惠券信息
            coupon_url = f'https://coupon.m.jd.com/coupons/show.action?skuId={sku_id}'
            response = self.session.get(coupon_url, timeout=self.timeout)
            
            if response.status_code == 200:
                # 解析优惠券信息
                soup = BeautifulSoup(response.text, 'html.parser')
                coupon_elems = soup.find_all('div', class_='coupon-item')
                
                for elem in coupon_elems:
                    coupon_text = elem.text.strip()
                    if coupon_text:
                        promotions.append(coupon_text)
            
        except Exception as e:
            logger.warning(f"获取促销信息失败: {e}")
        
        return promotions
    
    def get_shipping_info(self, sku_id: str, address: str = "北京") -> Dict[str, Any]:
        """
        获取运费信息
        
        Args:
            sku_id: 商品SKU ID
            address: 收货地址
            
        Returns:
            运费信息
        """
        # 这里简化处理，实际需要调用京东运费计算API
        return {
            'shipping_fee': 0.0,  # 京东自营通常包邮
            'is_free': True,
            'estimated_delivery': '1-3天',
            'address': address
        }
    
    def batch_get_prices(self, sku_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        批量获取价格
        
        Args:
            sku_ids: SKU ID列表
            
        Returns:
            价格信息字典
        """
        results = {}
        
        for sku_id in sku_ids:
            try:
                price_info = self.get_price(sku_id)
                results[sku_id] = price_info
                time.sleep(0.5)  # 避免请求过快
            except Exception as e:
                logger.error(f"批量获取价格失败 {sku_id}: {e}")
                results[sku_id] = {'error': str(e)}
        
        return results


def main():
    """示例用法"""
    scraper = JDScraper()
    
    # 示例1：搜索商品
    print("搜索商品示例:")
    products = scraper.search("iPhone 15", page=1)
    for i, product in enumerate(products[:3], 1):
        print(f"{i}. {product['title']} - ¥{product['price']}")
    
    print("\n" + "="*50 + "\n")
    
    # 示例2：获取商品详情
    if products:
        sample_url = products[0]['url']
        print(f"获取商品详情示例 ({sample_url}):")
        product_info = scraper.get_product_details(sample_url)
        
        if product_info:
            print(f"商品ID: {product_info.product_id}")
            print(f"商品标题: {product_info.title}")
            print(f"当前价格: ¥{product_info.price}")
            print(f"原价: ¥{product_info.original_price}")
            print(f"店铺: {product_info.shop_name}")
            print(f"促销信息: {', '.join(product_info.promotions[:3])}")
    
    print("\n" + "="*50 + "\n")
    
    # 示例3：批量获取价格
    print("批量获取价格示例:")
    sku_ids = ['100000000001', '100000000002', '100000000003']
    prices = scraper.batch_get_prices(sku_ids)
    
    for sku_id, price_info in prices.items():
        if 'error' not in price_info:
            print(f"SKU {sku_id}: ¥{price_info.get('price', 0)}")


if __name__ == "__main__":
    main()