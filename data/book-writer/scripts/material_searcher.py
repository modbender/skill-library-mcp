#!/usr/bin/env python3
"""
素材搜索器 - 从网络搜索相关素材（图片、数据、代码等）
"""

import os
import requests
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class MaterialSearcher:
    """素材搜索器"""

    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化搜索器

        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.google_api_key = os.environ.get("GOOGLE_API_KEY") or self.config.get("google", {}).get("api_key")
        self.google_cse_id = os.environ.get("GOOGLE_CSE_ID") or self.config.get("google", {}).get("cse_id")
        
        if not self.google_api_key or not self.google_cse_id:
            logger.warning("Google API密钥或CSE ID未设置，素材搜索功能将受限")
        
        logger.info("素材搜索器初始化完成")

    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        if not os.path.exists(config_path):
            logger.warning(f"配置文件 {config_path} 不存在，使用默认配置")
            return {}

        try:
            with open(config_path, 'r') as f:
                config = json.load(f) if config_path.endswith('.json') else yaml.safe_load(f)
            logger.info(f"配置文件加载成功: {config_path}")
            return config or {}
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return {}

    def search_images(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        搜索相关图片

        Args:
            query: 搜索查询
            num_results: 结果数量

        Returns:
            List[Dict]: 图片信息列表
        """
        if not self.google_api_key or not self.google_cse_id:
            logger.warning("Google API未配置，返回模拟结果")
            return self._mock_image_search(query, num_results)

        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': self.google_cse_id,
                'q': query,
                'searchType': 'image',
                'num': min(num_results, 10)  # Google API限制每次最多10个结果
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            images = []

            if 'items' in data:
                for item in data['items']:
                    images.append({
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'thumbnail': item.get('thumbnailLink', ''),
                        'context': item.get('image', {}).get('contextLink', ''),
                        'description': item.get('snippet', '')
                    })

            logger.info(f"找到 {len(images)} 张相关图片")
            return images

        except Exception as e:
            logger.error(f"图片搜索失败: {e}")
            return self._mock_image_search(query, num_results)

    def search_code_examples(self, query: str, num_results: int = 3) -> List[Dict[str, str]]:
        """
        搜索代码示例

        Args:
            query: 搜索查询
            num_results: 结果数量

        Returns:
            List[Dict]: 代码示例信息列表
        """
        if not self.google_api_key or not self.google_cse_id:
            logger.warning("Google API未配置，返回模拟结果")
            return self._mock_code_search(query, num_results)

        try:
            # 在GitHub等代码托管平台搜索
            github_query = f"{query} language:python OR language:javascript OR language:java OR language:cpp"
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': self.google_cse_id,
                'q': github_query,
                'num': min(num_results, 10)
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            codes = []

            if 'items' in data:
                for item in data['items']:
                    codes.append({
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'source': 'GitHub' if 'github.com' in item.get('link', '') else 'Other'
                    })

            logger.info(f"找到 {len(codes)} 个相关代码示例")
            return codes

        except Exception as e:
            logger.error(f"代码搜索失败: {e}")
            return self._mock_code_search(query, num_results)

    def search_data_and_statistics(self, query: str, num_results: int = 3) -> List[Dict[str, str]]:
        """
        搜索数据和统计数据

        Args:
            query: 搜索查询
            num_results: 结果数量

        Returns:
            List[Dict]: 数据信息列表
        """
        if not self.google_api_key or not self.google_cse_id:
            logger.warning("Google API未配置，返回模拟结果")
            return self._mock_data_search(query, num_results)

        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': self.google_cse_id,
                'q': f"{query} statistics data chart graph",
                'num': min(num_results, 10)
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            datasets = []

            if 'items' in data:
                for item in data['items']:
                    datasets.append({
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'source': item.get('displayLink', '')
                    })

            logger.info(f"找到 {len(datasets)} 个相关数据源")
            return datasets

        except Exception as e:
            logger.error(f"数据搜索失败: {e}")
            return self._mock_data_search(query, num_results)

    def _mock_image_search(self, query: str, num_results: int) -> List[Dict[str, str]]:
        """模拟图片搜索"""
        logger.info(f"使用模拟模式搜索图片: {query}")
        return [
            {
                'title': f'Sample image for {query}',
                'link': f'https://example.com/image_{i}.jpg',
                'thumbnail': f'https://example.com/thumb_{i}.jpg',
                'context': 'https://example.com/context',
                'description': f'This is a sample image related to {query}'
            }
            for i in range(min(num_results, 3))
        ]

    def _mock_code_search(self, query: str, num_results: int) -> List[Dict[str, str]]:
        """模拟代码搜索"""
        logger.info(f"使用模拟模式搜索代码: {query}")
        return [
            {
                'title': f'{query} code example {i}',
                'link': f'https://github.com/example/repo{i}',
                'snippet': f'// Sample code for {query}\nfunction example() {{\n  // TODO: implement {query}\n}}',
                'source': 'GitHub'
            }
            for i in range(min(num_results, 3))
        ]

    def _mock_data_search(self, query: str, num_results: int) -> List[Dict[str, str]]:
        """模拟数据搜索"""
        logger.info(f"使用模拟模式搜索数据: {query}")
        return [
            {
                'title': f'{query} statistics and data',
                'link': f'https://example.com/data{i}.json',
                'snippet': f'Dataset containing information about {query} trends and statistics',
                'source': 'DataHub'
            }
            for i in range(min(num_results, 3))
        ]

    def download_image(self, image_url: str, save_path: str) -> bool:
        """
        下载图片

        Args:
            image_url: 图片URL
            save_path: 保存路径

        Returns:
            bool: 是否成功下载
        """
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"图片已下载: {save_path}")
            return True
        except Exception as e:
            logger.error(f"下载图片失败: {e}")
            return False

    def generate_figure_description(self, topic: str) -> str:
        """
        生成图表描述

        Args:
            topic: 图表主题

        Returns:
            str: 图表描述
        """
        # 这里可以集成AI模型来生成更精确的图表描述
        descriptions = {
            "machine learning": f"Figure: Overview of {topic} concepts, showing the relationship between training data, model, and predictions.",
            "data science": f"Chart: Distribution of {topic} metrics, illustrating key statistical properties.",
            "programming": f"Diagram: Flowchart demonstrating the {topic} algorithm or process.",
            "mathematics": f"Graph: Mathematical function related to {topic}, showing key properties and behaviors."
        }
        
        default_desc = f"Figure: Visualization of {topic} concepts, showing key relationships and properties."
        return descriptions.get(topic.lower(), default_desc)

    def generate_table_schema(self, topic: str, columns: List[str]) -> Dict[str, Any]:
        """
        生成表格结构

        Args:
            topic: 表格主题
            columns: 列名列表

        Returns:
            Dict: 表格结构
        """
        return {
            "title": f"Table: {topic} Data",
            "description": f"Structured data table for {topic} information",
            "columns": [{"name": col, "type": "string", "description": f"Column for {col}"} for col in columns],
            "sample_rows": []
        }


def main():
    """测试函数"""
    import argparse

    parser = argparse.ArgumentParser(description="素材搜索器测试")
    parser.add_argument("query", help="搜索查询")
    parser.add_argument("--type", choices=["images", "code", "data"], default="images", help="搜索类型")

    args = parser.parse_args()

    searcher = MaterialSearcher()

    if args.type == "images":
        results = searcher.search_images(args.query)
        print(f"找到 {len(results)} 张图片:")
        for img in results:
            print(f"  - {img['title']}: {img['link']}")
    elif args.type == "code":
        results = searcher.search_code_examples(args.query)
        print(f"找到 {len(results)} 个代码示例:")
        for code in results:
            print(f"  - {code['title']}: {code['link']}")
            print(f"    {code['snippet'][:100]}...")
    elif args.type == "data":
        results = searcher.search_data_and_statistics(args.query)
        print(f"找到 {len(results)} 个数据源:")
        for data in results:
            print(f"  - {data['title']}: {data['link']}")
            print(f"    {data['snippet'][:100]}...")


if __name__ == "__main__":
    main()