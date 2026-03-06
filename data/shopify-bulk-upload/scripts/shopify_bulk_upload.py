#!/usr/bin/env python3
"""
Shopify Bulk Product Uploader
从 Excel/CSV 批量上传商品到 Shopify
"""

import os
import sys
import json
import time
import logging
import argparse
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/upload.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 尝试导入依赖
try:
    import pandas as pd
    import requests
    from dotenv import load_dotenv
except ImportError as e:
    print(f"缺少依赖，请安装: pip install pandas requests python-dotenv openpyxl")
    sys.exit(1)

# 加载配置
load_dotenv()

# ============ 配置 ============
CONFIG = {
    "batch_size": 10,
    "retry_count": 3,
    "retry_delay": 2,
    "image_timeout": 30,
    "default_status": "active",
}

class ShopifyUploader:
    def __init__(self, store_url=None, access_token=None):
        self.store_url = store_url or os.getenv("SHOPIFY_STORE_URL")
        self.access_token = access_token or os.getenv("SHOPIFY_ACCESS_TOKEN")
        self.api_version = os.getenv("SHOPIFY_API_VERSION", "2024-01")
        self.session = requests.Session()
        self.session.headers.update({
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json",
        })
        self.created_products = []
        self.failed_products = []
        
    def _make_request(self, method, endpoint, data=None, params=None):
        """发送 API 请求"""
        url = f"{self.store_url}/admin/api/{self.api_version}/{endpoint}"
        
        for attempt in range(CONFIG["retry_count"]):
            try:
                if method.upper() == "GET":
                    response = self.session.get(url, params=params, timeout=30)
                elif method.upper() == "POST":
                    response = self.session.post(url, json=data, timeout=60)
                elif method.upper() == "PUT":
                    response = self.session.put(url, json=data, timeout=60)
                elif method.upper() == "DELETE":
                    response = self.session.delete(url, timeout=30)
                else:
                    raise ValueError(f"不支持的 HTTP 方法: {method}")
                
                if response.status_code in [200, 201]:
                    return response.json()
                elif response.status_code == 429:
                    # Rate limited
                    wait_time = int(response.headers.get("Retry-After", 60))
                    logger.warning(f"Rate limited, 等待 {wait_time} 秒...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"API 错误: {response.status_code} - {response.text}")
                    if attempt < CONFIG["retry_count"] - 1:
                        time.sleep(CONFIG["retry_delay"])
                        continue
                    return None
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"请求失败: {e}")
                if attempt < CONFIG["retry_count"] - 1:
                    time.sleep(CONFIG["retry_delay"])
                    continue
                return None
        
        return None
    
    def upload_image(self, product_id, image_url):
        """上传产品图片"""
        try:
            # 下载图片
            img_response = requests.get(image_url, timeout=CONFIG["image_timeout"])
            if img_response.status_code != 200:
                logger.warning(f"无法下载图片: {image_url}")
                return None
            
            # 上传到 Shopify
            files = {
                'file': ('image.jpg', img_response.content, 'image/jpeg')
            }
            data = {
                'image': {
                    'attachment': img_response.content.hex()
                }
            }
            
            # 使用 base64 上传
            import base64
            b64_image = base64.b64encode(img_response.content).decode('utf-8')
            data = {
                'image': {
                    'src': image_url  # Shopify 可以直接从 URL 下载
                }
            }
            
            endpoint = f"products/{product_id}/images.json"
            result = self._make_request("POST", endpoint, data)
            
            if result:
                logger.info(f"图片上传成功: {image_url}")
                return result.get('image', {}).get('id')
            return None
            
        except Exception as e:
            logger.error(f"图片上传失败: {e}")
            return None
    
    def create_product(self, product_data):
        """创建单个产品"""
        try:
            # 构建产品数据
            product = {
                "product": {
                    "title": product_data.get("title", ""),
                    "body_html": product_data.get("description", ""),
                    "vendor": product_data.get("vendor", ""),
                    "product_type": product_data.get("product_type", ""),
                    "status": product_data.get("status", CONFIG["default_status"]),
                    "tags": product_data.get("tags", ""),
                    "variants": [],
                    "options": []
                }
            }
            
            # 处理变体
            variant_titles = []
            if product_data.get("option1_name") and product_data.get("option1_value"):
                variant_titles.append(product_data["option1_name"])
                product["product"]["options"].append({
                    "name": product_data["option1_name"]
                })
                
                # 创建变体
                variant = {
                    "price": str(product_data.get("price", "0")),
                    "sku": product_data.get("sku", ""),
                    "inventory_management": "shopify",
                    "inventory_quantity": int(product_data.get("inventory_quantity", 0)),
                }
                
                if product_data.get("compare_at_price"):
                    variant["compare_at_price"] = str(product_data["compare_at_price"])
                if product_data.get("weight"):
                    variant["weight"] = float(product_data["weight"])
                    variant["weight_unit"] = product_data.get("weight_unit", "kg")
                    
                if product_data.get("option1_value"):
                    variant["option1"] = product_data["option1_value"]
                if product_data.get("option2_value"):
                    variant["option2"] = product_data["option2_value"]
                    if product_data.get("option2_name") and len(product["product"]["options"]) < 2:
                        product["product"]["options"].append({
                            "name": product_data["option2_name"]
                        })
                    variant["option2"] = product_data["option2_value"]
                    
                product["product"]["variants"].append(variant)
            else:
                # 没有变体，创建默认变体
                variant = {
                    "price": str(product_data.get("price", "0")),
                    "sku": product_data.get("sku", ""),
                    "inventory_management": "shopify",
                    "inventory_quantity": int(product_data.get("inventory_quantity", 0)),
                }
                if product_data.get("compare_at_price"):
                    variant["compare_at_price"] = str(product_data["compare_at_price"])
                if product_data.get("weight"):
                    variant["weight"] = float(product_data["weight"])
                    variant["weight_unit"] = product_data.get("weight_unit", "kg")
                product["product"]["variants"].append(variant)
            
            # 发送创建请求
            endpoint = "products.json"
            result = self._make_request("POST", endpoint, product)
            
            if result and "product" in result:
                product_id = result["product"]["id"]
                logger.info(f"产品创建成功: {product_data.get('title')} (ID: {product_id})")
                
                # 上传图片
                images = product_data.get("images", "")
                if images:
                    image_urls = [img.strip() for img in images.split(",")]
                    for img_url in image_urls:
                        if img_url:
                            self.upload_image(product_id, img_url)
                
                return result["product"]
            else:
                logger.error(f"产品创建失败: {product_data.get('title')}")
                self.failed_products.append({
                    "title": product_data.get("title"),
                    "reason": "API 返回失败",
                    "data": product_data
                })
                return None
                
        except Exception as e:
            logger.error(f"创建产品异常: {e}")
            self.failed_products.append({
                "title": product_data.get("title"),
                "reason": str(e),
                "data": product_data
            })
            return None
    
    def upload_from_file(self, file_path):
        """从文件批量上传"""
        file_path = Path(file_path)
        
        # 读取文件
        if file_path.suffix.lower() == '.csv':
            df = pd.read_csv(file_path)
        elif file_path.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            logger.error(f"不支持的文件格式: {file_path.suffix}")
            return
        
        # 转换为字典列表
        products = df.to_dict('records')
        total = len(products)
        
        logger.info(f"开始上传 {total} 个商品...")
        
        for i, product_data in enumerate(products, 1):
            logger.info(f"上传进度: {i}/{total}")
            result = self.create_product(product_data)
            if result:
                self.created_products.append(result)
            
            # 批次间隔
            if i % CONFIG["batch_size"] == 0:
                logger.info(f"已完成 {i}/{total}，休息 2 秒...")
                time.sleep(2)
        
        # 保存结果
        self.save_results()
        
        logger.info(f"上传完成! 成功: {len(self.created_products)}, 失败: {len(self.failed_products)}")
    
    def save_results(self):
        """保存结果到文件"""
        output_dir = Path("../output")
        output_dir.mkdir(exist_ok=True)
        
        # 保存成功的商品
        with open(output_dir / "products_created.json", "w", encoding="utf-8") as f:
            json.dump(self.created_products, f, ensure_ascii=False, indent=2)
        
        # 保存失败的商品
        with open(output_dir / "products_failed.json", "w", encoding="utf-8") as f:
            json.dump(self.failed_products, f, ensure_ascii=False, indent=2)
        
        logger.info(f"结果已保存到 {output_dir}")


def main():
    parser = argparse.ArgumentParser(description="Shopify 批量上传工具")
    parser.add_argument("-f", "--file", default="../assets/products.xlsx", help="商品数据文件路径")
    parser.add_argument("-s", "--store", help="Shopify 店铺 URL")
    parser.add_argument("-t", "--token", help="Shopify Access Token")
    args = parser.parse_args()
    
    # 检查配置
    if not args.store and not os.getenv("SHOPIFY_STORE_URL"):
        print("错误: 请设置 SHOPIFY_STORE_URL 环境变量或使用 -s 参数")
        sys.exit(1)
    if not args.token and not os.getenv("SHOPIFY_ACCESS_TOKEN"):
        print("错误: 请设置 SHOPIFY_ACCESS_TOKEN 环境变量或使用 -t 参数")
        sys.exit(1)
    
    # 检查文件
    file_path = Path(args.file)
    if not file_path.exists():
        # 尝试使用模板
        template_path = Path("../assets/products-template.xlsx")
        if template_path.exists():
            file_path = template_path
            print(f"使用模板文件: {file_path}")
        else:
            print(f"错误: 文件不存在: {args.file}")
            sys.exit(1)
    
    # 创建上传器并执行
    uploader = ShopifyUploader(args.store, args.token)
    uploader.upload_from_file(file_path)


if __name__ == "__main__":
    main()
