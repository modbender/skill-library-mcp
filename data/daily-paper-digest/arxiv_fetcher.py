"""
arXiv 论文爬取模块
"""
import arxiv
from datetime import datetime, timedelta
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class ArxivFetcher:
    """arXiv 论文获取器"""
    
    def __init__(self, categories: List[str], max_results: int = 10):
        """
        初始化 arXiv 获取器
        
        Args:
            categories: 论文分类列表，如 ['cs.AI', 'cs.CL']
            max_results: 每个分类最大返回结果数
        """
        self.categories = categories
        self.max_results = max_results
    
    def fetch_daily_papers(self) -> List[Dict]:
        """
        获取每日最新论文
        
        Returns:
            论文列表，每篇论文包含标题、作者、摘要、链接等信息
        """
        papers = []
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime('%Y%m%d')
        
        for category in self.categories:
            try:
                logger.info(f"正在获取 {category} 分类的论文...")
                
                # 构建查询
                search = arxiv.Search(
                    query=f"cat:{category}",
                    max_results=self.max_results,
                    sort_by=arxiv.SortCriterion.SubmittedDate,
                    sort_order=arxiv.SortOrder.Descending
                )
                
                # 获取结果
                for result in search.results():
                    # 只获取最近一天的论文
                    if result.published.date() >= yesterday.date():
                        paper = {
                            'title': result.title,
                            'authors': [author.name for author in result.authors],
                            'abstract': result.summary,
                            'pdf_url': result.pdf_url,
                            'arxiv_url': result.entry_id,
                            'published': result.published.strftime('%Y-%m-%d'),
                            'category': category,
                            'source': 'arxiv'
                        }
                        papers.append(paper)
                        
            except Exception as e:
                logger.error(f"获取 {category} 论文失败: {str(e)}")
        
        logger.info(f"从 arXiv 获取了 {len(papers)} 篇论文")
        return papers
    
    def search_papers(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        搜索特定主题的论文
        
        Args:
            query: 搜索关键词
            max_results: 最大返回结果数
            
        Returns:
            论文列表
        """
        papers = []
        
        try:
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )
            
            for result in search.results():
                paper = {
                    'title': result.title,
                    'authors': [author.name for author in result.authors],
                    'abstract': result.summary,
                    'pdf_url': result.pdf_url,
                    'arxiv_url': result.entry_id,
                    'published': result.published.strftime('%Y-%m-%d'),
                    'source': 'arxiv'
                }
                papers.append(paper)
                
        except Exception as e:
            logger.error(f"搜索论文失败: {str(e)}")
        
        return papers


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    fetcher = ArxivFetcher(categories=['cs.AI', 'cs.CL'], max_results=5)
    papers = fetcher.fetch_daily_papers()
    
    print(f"\n找到 {len(papers)} 篇论文：")
    for i, paper in enumerate(papers, 1):
        print(f"\n{i}. {paper['title']}")
        print(f"   作者: {', '.join(paper['authors'][:3])}")
        print(f"   链接: {paper['arxiv_url']}")
