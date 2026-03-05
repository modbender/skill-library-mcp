"""
HuggingFace 论文爬取模块
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class HuggingFaceFetcher:
    """HuggingFace 每日论文获取器"""
    
    def __init__(self, max_results: int = 10):
        """
        初始化 HuggingFace 获取器
        
        Args:
            max_results: 最大返回结果数
        """
        self.base_url = "https://huggingface.co/papers"
        self.max_results = max_results
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_daily_papers(self) -> List[Dict]:
        """
        获取 HuggingFace 每日热门论文
        
        Returns:
            论文列表
        """
        papers = []
        
        try:
            logger.info("正在获取 HuggingFace 每日论文...")
            
            # 请求页面
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # 解析 HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找论文卡片
            paper_cards = soup.find_all('article', class_='overview-card-wrapper', limit=self.max_results)
            
            for card in paper_cards:
                try:
                    # 提取论文信息
                    title_elem = card.find('h3')
                    title = title_elem.text.strip() if title_elem else "未知标题"
                    
                    # 提取链接
                    link_elem = card.find('a', href=True)
                    paper_link = f"https://huggingface.co{link_elem['href']}" if link_elem else ""
                    
                    # 提取作者
                    authors_elem = card.find('p', class_='text-sm')
                    authors = [authors_elem.text.strip()] if authors_elem else []
                    
                    # 提取摘要
                    abstract_elem = card.find('p', class_='line-clamp-3')
                    abstract = abstract_elem.text.strip() if abstract_elem else ""
                    
                    # 提取点赞数
                    likes_elem = card.find('span', class_='text-sm')
                    likes = likes_elem.text.strip() if likes_elem else "0"
                    
                    paper = {
                        'title': title,
                        'authors': authors,
                        'abstract': abstract,
                        'url': paper_link,
                        'likes': likes,
                        'published': datetime.now().strftime('%Y-%m-%d'),
                        'source': 'huggingface'
                    }
                    papers.append(paper)
                    
                except Exception as e:
                    logger.warning(f"解析单篇论文失败: {str(e)}")
                    continue
            
            logger.info(f"从 HuggingFace 获取了 {len(papers)} 篇论文")
            
        except Exception as e:
            logger.error(f"获取 HuggingFace 论文失败: {str(e)}")
        
        return papers
    
    def fetch_paper_details(self, paper_url: str) -> Dict:
        """
        获取单篇论文的详细信息
        
        Args:
            paper_url: 论文 URL
            
        Returns:
            论文详细信息
        """
        try:
            response = requests.get(paper_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 这里可以根据实际页面结构提取更多信息
            # 返回基本信息
            return {
                'url': paper_url,
                'fetched_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            logger.error(f"获取论文详情失败: {str(e)}")
            return {}


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    fetcher = HuggingFaceFetcher(max_results=5)
    papers = fetcher.fetch_daily_papers()
    
    print(f"\n找到 {len(papers)} 篇论文：")
    for i, paper in enumerate(papers, 1):
        print(f"\n{i}. {paper['title']}")
        print(f"   点赞: {paper['likes']}")
        print(f"   链接: {paper['url']}")
