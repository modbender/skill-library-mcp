#!/usr/bin/env python3
"""
AI Daily - AI 大模型日报生成器
自动抓取、筛选、提炼 LLM/Agent 领域热点信息，生成结构化中文简报

Usage:
    python ai_daily.py [--date YYYY-MM-DD] [--output-dir PATH] [--debug]
"""

import os
import sys
import json
import urllib.request
import ssl
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict
import hashlib

# ============== 配置加载 ==============

def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    config_path = Path(__file__).parent.parent / "config" / "sources.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# ============== 数据结构 ==============

@dataclass
class NewsItem:
    """新闻项"""
    title: str
    source: str
    url: str
    published: str
    summary: str = ""
    core_summary: str = ""  # 100 字左右核心内容
    category: str = "general"
    priority: int = 3
    content: str = ""
    raw_data: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'source': self.source,
            'url': self.url,
            'published': self.published,
            'summary': self.summary,
            'category': self.category,
            'priority': self.priority,
        }

@dataclass
class PaperItem:
    """论文项"""
    title: str
    arxiv_id: str
    authors: List[str]
    abstract: str
    categories: List[str]
    pdf_url: str
    published: str
    priority: int = 3
    summary: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'arxiv_id': self.arxiv_id,
            'authors': self.authors,
            'abstract': self.abstract,
            'categories': self.categories,
            'pdf_url': self.pdf_url,
            'published': self.published,
            'priority': self.priority,
            'summary': self.summary,
        }

@dataclass
class KOLPost:
    """KOL 动态"""
    author: str
    content: str
    url: str
    published: str
    priority: int = 3
    summary: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'author': self.author,
            'content': self.content,
            'url': self.url,
            'published': self.published,
            'priority': self.priority,
            'summary': self.summary,
        }

@dataclass
class DailyReport:
    """日报结构"""
    date: str
    generated_at: str
    total_items: int = 0
    
    # 三个板块（合并核心大事件和官方更新为文章）
    articles: List[NewsItem] = field(default_factory=list)  # 精选文章（合并后的）
    kol_insights: List[KOLPost] = field(default_factory=list)  # KOL 观点
    papers: List[PaperItem] = field(default_factory=list)  # 必读论文
    
    def _generate_paper_summary(self, paper: PaperItem) -> str:
        """为论文生成中文摘要"""
        abstract = paper.abstract.strip()
        
        if not abstract:
            return "本文研究了相关领域的最新进展。"
        
        # 清理 HTML 标签
        import re
        abstract = re.sub(r'<[^>]+>', '', abstract)
        abstract = re.sub(r'\s+', ' ', abstract)
        
        # 简单翻译：提取关键信息生成中文摘要
        title_keywords = paper.title.lower()
        summary_parts = []
        
        # 根据标题关键词生成领域说明
        if 'agent' in title_keywords or 'agent' in abstract.lower():
            summary_parts.append('该研究提出了一个新的智能体方法')
        elif 'reasoning' in title_keywords or 'reasoning' in abstract.lower():
            summary_parts.append('该研究改进了模型的推理能力')
        elif 'benchmark' in title_keywords or 'evaluat' in abstract.lower():
            summary_parts.append('该研究提出了一个新的评估基准')
        elif 'efficient' in title_keywords or 'efficient' in abstract.lower():
            summary_parts.append('该研究提出了一种高效的方法')
        elif 'train' in title_keywords or 'train' in abstract.lower():
            summary_parts.append('该研究提出了一种新的训练方法')
        else:
            summary_parts.append('该研究提出了一个新方法')
        
        # 添加应用场景
        if 'math' in title_keywords or 'math' in abstract.lower():
            summary_parts.append('用于数学问题求解')
        elif 'code' in title_keywords or 'code' in abstract.lower():
            summary_parts.append('用于代码生成和理解')
        elif 'vision' in title_keywords or 'image' in abstract.lower():
            summary_parts.append('用于视觉任务')
        elif 'gui' in title_keywords:
            summary_parts.append('用于图形界面交互')
        
        # 添加效果说明
        if 'improv' in abstract.lower():
            summary_parts.append('显著提升了性能')
        elif 'efficient' in abstract.lower() or 'faster' in abstract.lower():
            summary_parts.append('大幅提高了效率')
        
        summary = '，'.join(summary_parts) + '。'
        
        # 限制长度
        if len(summary) > 80:
            summary = summary[:80] + '...'
        
        return summary
    
    def to_markdown(self) -> str:
        """生成 Markdown 格式报告"""
        md = []
        md.append(f"# 📰 AI 大模型日报 | {self.date}\n")
        md.append(f"*生成时间：{self.generated_at} | 共收录 {self.total_items} 条信息*\n")
        md.append("---\n")
        
        # 1. 精选文章（按质量排序，最多 10 条）
        md.append(f"## 📰 精选文章（{len(self.articles)}/10）\n")
        if self.articles:
            sorted_articles = sorted(self.articles, key=lambda x: -x.priority)
            for i, item in enumerate(sorted_articles, 1):
                source_tag = f"【{item.source}】" if item.source in ['量子位', '机器之心'] else ""
                stars = "⭐" * min(item.priority, 5)
                md.append(f"{i}. {source_tag} {item.title} {stars}\n")
                
                # 生成 100 字左右的核心摘要
                summary_text = item.core_summary if hasattr(item, 'core_summary') and item.core_summary else (item.summary if item.summary else item.content[:300])
                if summary_text:
                    summary_text = summary_text.strip()
                    # 清理 HTML 标签和多余空格
                    import re
                    summary_text = re.sub(r'<[^>]+>', '', summary_text)
                    summary_text = re.sub(r'\s+', ' ', summary_text)
                    # 控制在 80-120 字左右
                    if len(summary_text) > 120:
                        summary_text = summary_text[:120] + '...'
                    md.append(f"\n**📝 核心内容**：{summary_text}\n")
                
                md.append(f"\n[阅读原文]({item.url})\n")
                md.append("")
        else:
            md.append("*今日暂无精选文章*\n")
        
        md.append("---\n")
        
        # 2. KOL 前沿观点（最多 3 条）
        md.append(f"## 💬 KOL 观点（{len(self.kol_insights)}/3）\n")
        if self.kol_insights:
            for item in sorted(self.kol_insights, key=lambda x: -x.priority):
                stars = "⭐" * min(item.priority, 5)
                md.append(f"**@{item.author}** {stars}\n")
                
                # 简短摘要
                content = item.content.strip()[:200]
                import re
                content = re.sub(r'<[^>]+>', '', content)
                content = re.sub(r'\s+', ' ', content)
                if len(content) > 150:
                    content = content[:150] + '...'
                md.append(f"\n**📝 摘要**：{content}\n")
                
                md.append(f"\n[查看原帖]({item.url})\n")
                md.append("")
        else:
            md.append("*今日暂无 KOL 观点*\n")
        
        md.append("---\n")
        
        # 3. 必读硬核论文（最多 3 篇）
        md.append(f"## 📚 推荐论文（{len(self.papers)}/3）\n")
        if self.papers:
            for i, paper in enumerate(sorted(self.papers, key=lambda x: -x.priority), 1):
                stars = "⭐" * min(paper.priority, 5)
                md.append(f"{i}. {paper.title} {stars}\n")
                md.append(f"**作者**: {', '.join(paper.authors[:5])}{'...' if len(paper.authors) > 5 else ''}\n")
                md.append(f"**分类**: {', '.join(paper.categories)}\n")
                
                # 生成中文摘要
                chinese_summary = self._generate_paper_summary(paper)
                md.append(f"\n**📝 摘要**：{chinese_summary}\n")
                
                md.append(f"\n[PDF]({paper.pdf_url}) | [arXiv](https://arxiv.org/abs/{paper.arxiv_id})\n")
                md.append("")
        else:
            md.append("*今日暂无推荐论文*\n")
        
        md.append("---\n")
        md.append(f"*本日报由 AI Daily Skill 自动生成 | 数据源：RSS + Tavily Search + arXiv*\n")
        
        return '\n'.join(md)

# ============== 数据抓取 ==============

class DataFetcher:
    """数据抓取器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        
        # 获取环境变量
        self.tavily_api_key = os.environ.get('TAVILY_API_KEY', '')
        self.github_token = os.environ.get('GITHUB_TOKEN', '')
    
    def fetch_url(self, url: str, timeout: int = 30, use_browser_ua: bool = False) -> str:
        """通用 URL 抓取"""
        # 机器之心需要使用真实浏览器 UA
        if use_browser_ua or 'jiqizhixin' in url:
            ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        else:
            ua = 'Mozilla/5.0 (compatible; AIDaily/1.0; +https://example.com/bot)'
        
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': ua,
                'Accept': 'application/rss+xml, application/xml, text/xml',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
            }
        )
        
        try:
            with urllib.request.urlopen(req, context=self.ssl_context, timeout=timeout) as response:
                return response.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"[WARN] Failed to fetch {url}: {e}", file=sys.stderr)
            return ""
    
    def fetch_rss(self, url: str) -> List[NewsItem]:
        """解析 RSS/Atom Feed 或网页"""
        # 特殊处理机器之心（Cloudflare 防护）
        if 'jiqizhixin.com' in url:
            return self.fetch_jiqizhixin()
        
        xml_data = self.fetch_url(url)
        if not xml_data:
            return []
        
        items = []
        try:
            root = ET.fromstring(xml_data)
            
            # 检测 Feed 类型
            if root.tag == 'rss':
                channel = root.find('channel')
                if channel is None:
                    return []
                entries = channel.findall('item')
            elif 'Atom' in root.tag or root.tag == '{http://www.w3.org/2005/Atom}feed':
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                entries = root.findall('atom:entry', ns)
            else:
                entries = root.findall('item') or root.findall('entry')
            
            for entry in entries:
                # 提取字段
                title_elem = entry.find('title')
                title = title_elem.text.strip() if title_elem is not None and title_elem.text else ""
                
                link_elem = entry.find('link')
                if link_elem is not None:
                    link = link_elem.get('href', link_elem.text) if hasattr(link_elem, 'get') else (link_elem.text or "")
                else:
                    link = ""
                
                # 尝试多个字段获取内容
                desc_elem = entry.find('description') or entry.find('summary') or entry.find('content') or entry.find('content/encoded')
                content = ""
                if desc_elem is not None:
                    if desc_elem.text:
                        content = self._clean_html(desc_elem.text)
                    # 尝试 atom:content
                    if not content:
                        content_elem = entry.find('{http://purl.org/rss/1.0/modules/content/}encoded')
                        if content_elem is not None and content_elem.text:
                            content = self._clean_html(content_elem.text)
                
                # 36 氪特殊处理：content 可能在 CDATA 中
                if not content:
                    import re
                    cdata_match = re.search(r'<!\[CDATA\[(.+?)\]\]>', str(ET.tostring(entry, encoding='unicode')))
                    if cdata_match:
                        content = self._clean_html(cdata_match.group(1))
                
                date_elem = entry.find('pubDate') or entry.find('published') or entry.find('updated')
                published = date_elem.text if date_elem is not None and date_elem.text else datetime.now().isoformat()
                
                if title and link:
                    items.append(NewsItem(
                        title=title,
                        source=url,
                        url=link,
                        published=published,
                        content=content,
                        category="rss"
                    ))
        
        except ET.ParseError as e:
            print(f"[WARN] RSS parse error for {url}: {e}", file=sys.stderr)
        
        return items
    
    def fetch_jiqizhixin(self) -> List[NewsItem]:
        """抓取机器之心网页（绕过 Cloudflare）"""
        items = []
        try:
            # 尝试直接访问 API
            api_url = "https://www.jiqizhixin.com/api/articles?limit=20"
            data = self.fetch_url(api_url)
            if data:
                import json
                result = json.loads(data)
                articles = result.get('data', {}).get('articles', [])
                for article in articles[:20]:
                    title = article.get('title', '')
                    url = article.get('url', '')
                    summary = article.get('abstract', '')
                    published = article.get('published_at', datetime.now().isoformat())
                    
                    if title and url:
                        items.append(NewsItem(
                            title=title,
                            source='机器之心',
                            url=f"https://www.jiqizhixin.com{url}" if url.startswith('/') else url,
                            published=published,
                            content=summary,
                            category="media"
                        ))
        except Exception as e:
            print(f"[WARN] 机器之心抓取失败：{e}", file=sys.stderr)
        
        return items
    
    def _clean_html(self, html: str) -> str:
        """清理 HTML 标签"""
        if not html:
            return ""
        text = re.sub(r'<[^>]+>', '', html)
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        return text.strip()
    
    def fetch_article_content(self, url: str) -> str:
        """抓取文章正文内容"""
        html = self.fetch_url(url, timeout=15)
        if not html:
            return ""
        
        # 简单提取正文（移除 script、style 等）
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<nav[^>]*>.*?</nav>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<header[^>]*>.*?</header>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<footer[^>]*>.*?</footer>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # 提取段落
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', text, flags=re.DOTALL | re.IGNORECASE)
        if paragraphs:
            # 取前 3 段作为摘要素材
            content = ' '.join([self._clean_html(p) for p in paragraphs[:3]])
            return content
        
        # 如果没有段落，返回清理后的全文（截取前 500 字）
        return self._clean_html(text)[:500]
    
    def fetch_tavily(self, query: str, max_results: int = 10) -> List[KOLPost]:
        """使用 Tavily Search 搜索"""
        if not self.tavily_api_key:
            print("[WARN] TAVILY_API_KEY not set, skipping Tavily search", file=sys.stderr)
            return []
        
        url = "https://api.tavily.com/search"
        payload = {
            "query": query,
            "max_results": max_results,
            "include_answer": False,
            "search_depth": "basic",
            "time_range": "day"
        }
        
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.tavily_api_key}'
            }
        )
        
        try:
            with urllib.request.urlopen(req, context=self.ssl_context, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            posts = []
            for item in result.get('results', []):
                try:
                    posts.append(KOLPost(
                        author="Unknown",
                        content=self._clean_html(item.get('content', '')),
                        url=item.get('url', ''),
                        published=datetime.now().isoformat()
                    ))
                except Exception as e:
                    if debug_mode:
                        print(f"[WARN] Failed to create KOLPost: {e}", file=sys.stderr)
            
            return posts
        except Exception as e:
            print(f"[WARN] Tavily search failed: {e}", file=sys.stderr)
            return []
    
    def fetch_arxiv(self, categories: List[str], keywords: List[str], max_results: int = 20) -> List[PaperItem]:
        """从 arXiv 获取论文"""
        papers = []
        
        for category in categories:
            # 构建搜索查询
            keyword_query = ' OR '.join([f'all:"{kw}"' for kw in keywords[:5]])  # 限制关键词数量
            search_query = f"cat:{category} AND ({keyword_query})"
            
            url = f"http://export.arxiv.org/api/query?search_query={urllib.parse.quote(search_query)}&start=0&max_results={max_results//len(categories)}&sortBy=submittedDate&sortOrder=descending"
            
            xml_data = self.fetch_url(url)
            if not xml_data:
                continue
            
            try:
                root = ET.fromstring(xml_data)
                ns = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
                
                for entry in root.findall('atom:entry', ns):
                    title_elem = entry.find('atom:title', ns)
                    title = title_elem.text.strip() if title_elem is not None else ""
                    
                    summary_elem = entry.find('atom:summary', ns)
                    abstract = summary_elem.text.strip() if summary_elem is not None else ""
                    
                    id_elem = entry.find('atom:id', ns)
                    arxiv_id = id_elem.text.split('/')[-1] if id_elem is not None else ""
                    
                    published_elem = entry.find('atom:published', ns)
                    published = published_elem.text if published_elem is not None else ""
                    
                    # 获取作者
                    authors = []
                    for author in entry.findall('atom:author', ns):
                        name_elem = author.find('atom:name', ns)
                        if name_elem is not None:
                            authors.append(name_elem.text)
                    
                    # 获取分类
                    cats = []
                    for cat in entry.findall('atom:category', ns):
                        term = cat.get('term', '')
                        if term:
                            cats.append(term)
                    
                    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                    
                    if title and arxiv_id:
                        papers.append(PaperItem(
                            title=title,
                            arxiv_id=arxiv_id,
                            authors=authors,
                            abstract=abstract,
                            categories=cats,
                            pdf_url=pdf_url,
                            published=published
                        ))
            
            except ET.ParseError as e:
                print(f"[WARN] arXiv parse error: {e}", file=sys.stderr)
        
        return papers

# ============== LLM 处理 ==============

class LLMProcessor:
    """LLM 内容处理器"""
    
    def __init__(self, model: str = "qwen3.5-plus"):
        self.model = model
        self.api_key = os.environ.get('ALIBABA_CLOUD_API_KEY', '')
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    def filter_noise(self, items: List[NewsItem], min_priority: int = 3) -> List[NewsItem]:
        """使用 LLM 过滤低质量内容"""
        # 简单规则过滤（实际应该调用 LLM）
        exclude_keywords = ['sponsor', 'advertisement', 'webinar', 'promo', '广告', '赞助']
        
        filtered = []
        for item in items:
            text = (item.title + ' ' + item.content).lower()
            
            # 检查排除关键词
            if any(kw.lower() in text for kw in exclude_keywords):
                continue
            
            # 如果 content 为空但有标题，也保留（很多 RSS 只返回标题）
            if len(item.content) < 10 and len(item.title) < 10:
                continue
            
            # 初步评分
            priority = self._calculate_priority(item)
            if priority >= min_priority:
                item.priority = priority
                filtered.append(item)
        
        return filtered
    
    def _calculate_priority(self, item: NewsItem) -> int:
        """计算内容优先级（1-10）"""
        priority = 5  # 基础分
        
        # 关键词加分（每项 +1，最多加 3 分）
        hot_keywords = [
            'GPT', 'Claude', 'Gemini', 'LLaMA', 'Qwen', '通义千问',
            'transformer', 'agent', 'reasoning', 'MoE', '混合专家',
            'fine-tuning', 'RLHF', 'RAG', 'prompt', '提示词',
            '大模型', '语言模型', '多模态', 'Agent', '智能体'
        ]
        
        text = (item.title + ' ' + item.content).lower()
        keyword_score = 0
        for kw in hot_keywords:
            if kw.lower() in text:
                keyword_score += 1
                if keyword_score >= 3:
                    break
        priority += keyword_score
        
        # 中文媒体加分（量子位、机器之心已经是高优先级，这里不再重复）
        if item.source in ['量子位', '机器之心']:
            priority += 1
        
        # 标题长度适中加分（太短可能是标题党，太长可能不够精炼）
        if 20 <= len(item.title) <= 60:
            priority += 1
        
        # 有摘要/内容加分
        if len(item.content) > 100 or len(item.summary) > 50:
            priority += 1
        
        return min(priority, 10)
    
    def summarize(self, item: NewsItem) -> str:
        """生成简短摘要"""
        # 优先使用已有摘要
        if item.summary:
            return item.summary
        
        # 从内容提取
        content = item.content[:500] if item.content else ""
        
        if content:
            # 取前 2-3 句作为摘要
            sentences = re.split(r'[.!?。！？]', content)
            summary = '. '.join([s.strip() for s in sentences[:2] if s.strip()])
            return summary if summary else content[:200]
        
        # 从标题生成有意义的摘要
        if item.title:
            title = item.title
            # 提取关键词
            keywords = []
            if any(kw in title for kw in ['大模型', 'LLM', 'GPT', 'Claude', 'Qwen']):
                keywords.append('大模型技术')
            if any(kw in title for kw in ['融资', '投资', '收购']):
                keywords.append('投融资动态')
            if any(kw in title for kw in ['发布', '上线', '开源']):
                keywords.append('产品发布')
            if any(kw in title for kw in ['Karpathy', 'LeCun', 'Hinton']):
                keywords.append('专家观点')
            if any(kw in title for kw in ['英伟达', 'NVIDIA', 'GPU', '芯片']):
                keywords.append('硬件动态')
            
            if keywords:
                return f"本文报道了{item.source}关于{'、'.join(keywords)}的最新动态。"
            else:
                return f"本文报道了{item.source}的最新 AI 行业动态。"
        
        return ""
    
    def rate_paper(self, paper: PaperItem) -> int:
        """评估论文重要性（1-10）"""
        priority = 5  # 基础分
        
        # 关键词匹配（每项 +1，最多加 3 分）
        hot_keywords = [
            'large language model', 'LLM', 'agent', 'reasoning', 'MoE',
            'mixture of experts', 'transformer', 'multimodal', 'vision-language',
            '大模型', '语言模型', '智能体', '推理', '多模态'
        ]
        text = (paper.title + ' ' + paper.abstract).lower()
        
        keyword_score = 0
        for kw in hot_keywords:
            if kw in text:
                keyword_score += 1
                if keyword_score >= 3:
                    break
        priority += keyword_score
        
        # 多作者加分（合作研究通常质量更高）
        if len(paper.authors) > 5:
            priority += 1
        if len(paper.authors) > 10:
            priority += 1
        
        # 知名机构加分
        prestigious = ['MIT', 'Stanford', 'Berkeley', 'Google', 'Meta', 'OpenAI', 'Microsoft', 'CMU']
        for author in paper.authors:
            if any(inst in author for inst in prestigious):
                priority += 1
                break
        
        return min(priority, 10)

# ============== 主流程 ==============

def generate_daily_report(date: Optional[str] = None, output_dir: Optional[str] = None, debug: bool = False):
    global debug_mode
    debug_mode = debug
    """生成日报主函数"""
    
    # 设置日期
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    print(f"🚀 开始生成 AI 日报 | 日期：{date}")
    
    # 加载配置
    config = load_config()
    
    # 设置输出目录
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = Path(__file__).parent.parent / "output"
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 初始化
    fetcher = DataFetcher(config)
    processor = LLMProcessor()
    report = DailyReport(date=date, generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # 1. 抓取 RSS Feed
    print("📡 抓取 RSS Feed...")
    all_rss_items = []
    
    for feed_group in ['official', 'media']:
        feeds = config['rssFeeds'].get(feed_group, [])
        for feed in feeds:
            if debug:
                print(f"  - {feed['name']}: {feed['url']}")
            items = fetcher.fetch_rss(feed['url'])
            for item in items:
                item.source = feed['name']
                item.category = feed_group
                # 根据配置设置优先级
                item.priority = feed.get('priority', 3)
            all_rss_items.extend(items)
    
    print(f"  ✓ 获取 {len(all_rss_items)} 条 RSS 内容")
    
    # 过滤和总结
    filtered_rss = processor.filter_noise(all_rss_items, config['filter']['minPriority'])
    for item in filtered_rss:
        if not item.summary:
            item.summary = processor.summarize(item)
    
    # 为高优先级文章抓取网页内容并生成核心摘要（100 字左右）
    print("📝 生成核心摘要...")
    sorted_for_fetch = sorted(filtered_rss, key=lambda x: -x.priority)[:10]
    for i, item in enumerate(sorted_for_fetch, 1):
        if item.priority >= 7:  # 只为高优先级文章抓取
            print(f"  [{i}/10] 抓取：{item.title[:50]}...")
            try:
                content = fetcher.fetch_article_content(item.url)
                if content:
                    # 提取关键信息生成 100 字左右摘要
                    sentences = re.split(r'[.!?。！？]', content)
                    core_parts = []
                    char_count = 0
                    for sent in sentences:
                        sent = sent.strip()
                        if len(sent) > 10 and char_count < 120:
                            core_parts.append(sent)
                            char_count += len(sent)
                    item.core_summary = '。'.join(core_parts) + '。' if core_parts else item.summary
            except Exception as e:
                if debug:
                    print(f"  [WARN] 摘要生成失败：{e}")
    
    # 提升量子位和机器之心的优先级
    for item in filtered_rss:
        if item.source in ['量子位', '机器之心']:
            item.priority = min(item.priority + 2, 10)  # 额外 +2 优先级，最高 10
    
    # 按优先级排序
    sorted_items = sorted(filtered_rss, key=lambda x: -x.priority)
    
    # 实施来源配额：量子位最多 80%（8 条/10 条）
    max_quantum = 8  # 量子位最多 8 条
    quantum_count = 0
    selected_items = []
    
    # 第一轮：选择非量子位的高优先级文章（至少 2 条）
    for item in sorted_items:
        if item.source != '量子位' and len(selected_items) < 10 - max_quantum:
            selected_items.append(item)
    
    # 第二轮：选择量子位文章（最多 8 条）
    for item in sorted_items:
        if item.source == '量子位' and quantum_count < max_quantum:
            selected_items.append(item)
            quantum_count += 1
    
    # 第三轮：如果还有空位，补充其他高优先级文章
    for item in sorted_items:
        if len(selected_items) >= 10:
            break
        if item not in selected_items:
            selected_items.append(item)
    
    # 最终限制 10 条
    report.articles = selected_items[:10]
    
    # 2. 抓取 KOL 动态（Tavily）
    print("🐦 抓取 KOL 动态...")
    all_kol_posts = []
    
    if fetcher.tavily_api_key:
        for kol in config['tavilySearch']['kolQueries']:
            if debug:
                print(f"  - {kol['name']}: {kol['query']}")
            try:
                posts = fetcher.fetch_tavily(
                    kol['query'],
                    config['tavilySearch']['maxResults']
                )
                for post in posts:
                    post.author = kol['name']
                    post.priority = kol.get('priority', 3)
                all_kol_posts.extend(posts)
            except Exception as e:
                if debug:
                    print(f"  [WARN] {kol['name']} 失败：{e}")
        
        print(f"  ✓ 获取 {len(all_kol_posts)} 条 KOL 动态")
    else:
        print("  ⚠ 未配置 TAVILY_API_KEY，跳过 KOL 动态抓取")
    
    report.kol_insights = all_kol_posts[:3]  # 限制最多 3 条
    
    # 3. 抓取 arXiv 论文
    print("📚 抓取 arXiv 论文...")
    papers = fetcher.fetch_arxiv(
        config['arxiv']['categories'],
        config['arxiv']['keywords'],
        config['arxiv']['maxResults']
    )
    
    print(f"  ✓ 获取 {len(papers)} 篇论文")
    
    # 评估论文
    for paper in papers:
        paper.priority = processor.rate_paper(paper)
    
    report.papers = sorted(papers, key=lambda x: -x.priority)[:3]  # 限制最多 3 篇
    
    # 统计
    report.total_items = (
        len(report.articles) +
        len(report.kol_insights) +
        len(report.papers)
    )
    
    # 生成 Markdown
    print("📝 生成报告...")
    markdown = report.to_markdown()
    
    # 保存文件
    filename = f"AI-Daily-{date}.md"
    output_file = output_path / filename
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"✅ 日报已保存至：{output_file}")
    print(f"📊 统计：精选文章 {len(report.articles)} | KOL 观点 {len(report.kol_insights)} | 论文 {len(report.papers)}")
    
    return output_file

# ============== CLI ==============

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Daily - 生成大模型日报')
    parser.add_argument('--date', type=str, help='指定日期 (YYYY-MM-DD)，默认为今天')
    parser.add_argument('--output-dir', type=str, help='输出目录')
    parser.add_argument('--debug', action='store_true', help='调试模式')
    
    args = parser.parse_args()
    
    try:
        output_file = generate_daily_report(
            date=args.date,
            output_dir=args.output_dir,
            debug=args.debug
        )
        
        # 输出到 stdout（方便 OpenClaw 读取）
        print("\n" + "="*60)
        print("📰 今日简报预览:")
        print("="*60)
        
        with open(output_file, 'r', encoding='utf-8') as f:
            # 只显示前 50 行
            lines = f.readlines()[:50]
            print(''.join(lines))
            if len(lines) == 50:
                print("\n... (完整报告见输出文件)")
    
    except Exception as e:
        print(f"❌ 生成失败：{e}", file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
