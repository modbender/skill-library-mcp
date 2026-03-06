#!/usr/bin/env python3
"""
PubMed-Search: 生物医学文献搜索和分析工具
支持从 PubMed 搜索、获取元数据和深度分析文献
"""

import os
import sys
import json
import argparse
import xml.etree.ElementTree as ET
from urllib.parse import quote
from pathlib import Path
from typing import Optional, Dict, List, Any

try:
    import requests
except ImportError:
    print("错误: 需要安装 requests")
    print("安装命令: pip install requests")
    sys.exit(1)

# 加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # 如果没有安装 python-dotenv，跳过加载


# ============================================
# 配置管理
# ============================================

class Config:
    """配置管理类"""

    def __init__(self):
        self.api_key = os.getenv('PUBMED_API_KEY', '')
        self.email = os.getenv('PUBMED_EMAIL', '')
        self.tool = os.getenv('PUBMED_TOOL', 'pubmed-search-skill')
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def get_params(self, extra_params: dict = None) -> dict:
        """获取 API 请求参数"""
        params = {
            'tool': self.tool,
            'retmode': 'xml'
        }
        if self.api_key:
            params['api_key'] = self.api_key
        if self.email:
            params['email'] = self.email
        if extra_params:
            params.update(extra_params)
        return params


# ============================================
# PubMed 搜索
# ============================================

class PubMedSearch:
    """PubMed 搜索类"""

    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': f'{config.tool}/1.0 ({config.email or "anonymous"})'
        })

    def generate_search_url(self, term=None, title=None, author=None, journal=None,
                           start_date=None, end_date=None, num_results=10) -> str:
        """
        根据用户输入的字段生成 PubMed 搜索 URL

        Args:
            term: 通用搜索词
            title: 标题搜索词
            author: 作者姓名
            journal: 期刊名称
            start_date: 开始日期 (YYYY/MM/DD)
            end_date: 结束日期 (YYYY/MM/DD)
            num_results: 返回结果数量

        Returns:
            完整的搜索 URL
        """
        base_url = f"{self.config.base_url}/esearch.fcgi"
        query_parts = []

        if term:
            query_parts.append(quote(term))
        if title:
            query_parts.append(f"{quote(title)}[Title]")
        if author:
            query_parts.append(f"{quote(author)}[Author]")
        if journal:
            query_parts.append(f"{quote(journal)}[Journal]")
        if start_date and end_date:
            query_parts.append(f"{start_date}:{end_date}[Date - Publication]")

        query = " AND ".join(query_parts)

        params = self.config.get_params({
            "db": "pubmed",
            "term": query,
            "retmax": str(num_results)
        })

        return f"{base_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"

    def search_articles(self, search_url: str) -> List[str]:
        """
        从 PubMed 搜索结果中解析文章 ID

        Args:
            search_url: 搜索 URL

        Returns:
            PMID 列表
        """
        try:
            response = self.session.get(search_url)
            if response.status_code != 200:
                print(f"错误: 无法获取搜索结果 (状态码: {response.status_code})")
                return []

            root = ET.fromstring(response.content)
            id_list = root.find("IdList")

            if id_list is not None:
                return [id_elem.text for id_elem in id_list.findall("Id")]
            else:
                print("未找到搜索结果")
                return []

        except Exception as e:
            print(f"搜索文章时出错: {e}")
            return []

    def get_metadata(self, pmid: str) -> Optional[Dict[str, Any]]:
        """
        使用 PubMed API 通过 PMID 获取文章的详细元数据

        Args:
            pmid: PubMed ID

        Returns:
            文章元数据字典
        """
        try:
            url = f"{self.config.base_url}/efetch.fcgi"
            params = self.config.get_params({
                "db": "pubmed",
                "id": pmid
            })

            response = self.session.get(url, params=params)

            if response.status_code != 200:
                print(f"错误: 无法获取元数据 (状态码: {response.status_code})")
                return None

            root = ET.fromstring(response.content)
            article = root.find(".//Article")

            if article is None:
                print(f"未找到 PMID: {pmid} 的文章数据")
                return None

            # 提取标题
            title_elem = article.find(".//ArticleTitle")
            title = title_elem.text if title_elem is not None else "无标题"

            # 提取摘要
            abstract_elem = article.find(".//Abstract/AbstractText")
            abstract = abstract_elem.text if abstract_elem is not None else "无摘要"

            # 提取作者
            authors = []
            for author_elem in article.findall(".//Author"):
                last_name = author_elem.find(".//LastName")
                if last_name is not None and last_name.text:
                    authors.append(last_name.text)
            authors_str = ", ".join(authors) if authors else "无作者信息"

            # 提取期刊
            journal_elem = article.find(".//Journal/Title")
            journal = journal_elem.text if journal_elem is not None else "无期刊信息"

            # 提取发表日期
            pub_date_elem = article.find(".//PubDate/Year")
            pub_date = pub_date_elem.text if pub_date_elem is not None else "无发表日期"

            # 提取 DOI
            doi = ""
            doi_elem = article.find(".//ArticleId[@IdType='doi']")
            if doi_elem is not None:
                doi = doi_elem.text

            return {
                "PMID": pmid,
                "Title": title,
                "Authors": authors_str,
                "Journal": journal,
                "Publication Date": pub_date,
                "Abstract": abstract,
                "DOI": doi
            }

        except Exception as e:
            print(f"获取元数据时出错: {e}")
            return None

    def search_by_keywords(self, keywords: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        使用关键词搜索文章

        Args:
            keywords: 搜索关键词
            num_results: 返回结果数量

        Returns:
            文章元数据列表
        """
        search_url = self.generate_search_url(term=keywords, num_results=num_results)
        print(f"搜索 URL: {search_url}")

        pmids = self.search_articles(search_url)
        articles = []

        for pmid in pmids:
            metadata = self.get_metadata(pmid)
            if metadata:
                articles.append(metadata)

        return articles

    def search_advanced(self, term=None, title=None, author=None, journal=None,
                      start_date=None, end_date=None, num_results=10) -> List[Dict[str, Any]]:
        """
        高级搜索

        Args:
            term: 通用搜索词
            title: 标题搜索词
            author: 作者姓名
            journal: 期刊名称
            start_date: 开始日期
            end_date: 结束日期
            num_results: 返回结果数量

        Returns:
            文章元数据列表
        """
        search_url = self.generate_search_url(
            term=term, title=title, author=author, journal=journal,
            start_date=start_date, end_date=end_date, num_results=num_results
        )
        print(f"搜索 URL: {search_url}")

        pmids = self.search_articles(search_url)
        articles = []

        for pmid in pmids:
            metadata = self.get_metadata(pmid)
            if metadata:
                articles.append(metadata)

        return articles

    def download_pdf(self, pmid: str, output_dir: str = ".") -> str:
        """
        尝试下载全文 PDF 或提供文章链接

        Args:
            pmid: PubMed ID
            output_dir: 输出目录

        Returns:
            下载结果或错误信息
        """
        try:
            print(f"正在尝试获取 PMID: {pmid} 的全文")

            # 获取文章信息检查是否有 PMC ID
            metadata = self.get_metadata(pmid)
            if not metadata:
                return f"错误: 无法获取 PMID {pmid} 的信息"

            efetch_url = f"{self.config.base_url}/efetch.fcgi"
            params = self.config.get_params({
                "db": "pubmed",
                "id": pmid
            })

            response = self.session.get(efetch_url, params=params)
            if response.status_code != 200:
                return f"错误: 无法获取文章数据 (状态码: {response.status_code})"

            root = ET.fromstring(response.content)
            pmc_id_elem = root.find(".//ArticleId[@IdType='pmc']")

            if pmc_id_elem is None:
                pubmed_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                return f"未找到 PMC ID\n可以在以下位置查看文章: {pubmed_url}"

            pmc_id = pmc_id_elem.text
            pmc_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/"

            pmc_response = self.session.get(pmc_url)
            if pmc_response.status_code != 200:
                return f"无法访问 PMC 文章页面 (状态码: {pmc_response.status_code})\n{pmc_url}"

            # 检查是否开放获取
            if "This article is available under a" not in pmc_response.text:
                return f"该文章不是完全开放获取\n可以在以下位置查看: {pmc_url}"

            # 尝试下载 PDF
            pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/pdf"
            pdf_response = self.session.get(pdf_url)

            if pdf_response.status_code != 200:
                return f"无法下载 PDF (状态码: {pdf_response.status_code})\n可以直接访问: {pmc_url}"

            # 保存 PDF 文件
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            filename = output_path / f"PMID_{pmid}_PMC_{pmc_id}.pdf"
            with open(filename, 'wb') as f:
                f.write(pdf_response.content)

            return f"PDF 已下载: {filename}"

        except Exception as e:
            return f"下载 PDF 时出错: {e}"

    def generate_analysis(self, metadata: Dict[str, Any]) -> str:
        """
        生成深度论文分析提示

        Args:
            metadata: 文章元数据

        Returns:
            分析提示文本
        """
        title = metadata.get('Title', '无标题')
        authors = metadata.get('Authors', '无作者')
        journal = metadata.get('Journal', '无期刊')
        pub_date = metadata.get('Publication Date', '无日期')
        abstract = metadata.get('Abstract', '无摘要')
        pmid = metadata.get('PMID', '')
        doi = metadata.get('DOI', '')

        prompt = f"""# 论文深度分析

## 基本信息
- **标题**: {title}
- **作者**: {authors}
- **期刊**: {journal}
- **发表日期**: {pub_date}
- **PMID**: {pmid}
- **DOI**: {doi}

## 摘要
{abstract}

---

## 分析要求

作为科学论文分析专家，请对上述论文进行全面分析：

### 1. 研究背景与意义
- 该研究领域的背景是什么？
- 研究的重要性和创新点在哪里？

### 2. 主要研究问题或假设
- 研究试图解决什么问题？
- 研究假设是什么？

### 3. 方法论概述
- 采用了什么研究方法？
- 实验设计是否合理？

### 4. 关键发现与结果
- 主要的研究结果是什么？
- 数据是否支持结论？

### 5. 结论与影响
- 研究的主要结论是什么？
- 对该领域有什么影响？

### 6. 研究局限性
- 研究存在哪些局限性？
- 如何改进？

### 7. 未来研究方向
- 基于该研究，未来可以探索哪些方向？

### 8. 与相关研究的关系
- 该研究与领域内其他研究的关系如何？
- 是否与已知结果一致？

### 9. 总体评价
- 对该研究的总体评价
- 适用性和可靠性评估

请基于论文信息进行全面、客观的分析。如果摘要中缺少某些信息，请指出这一点，并根据专业知识提供可能的推断或建议。
"""
        return prompt


# ============================================
# 输出处理
# ============================================

class OutputHandler:
    """输出处理类"""

    @staticmethod
    def format_console(articles: List[Dict[str, Any]], show_abstract: bool = False) -> str:
        """格式化控制台输出"""
        if not articles:
            return "未找到文章"

        lines = []
        for i, article in enumerate(articles, 1):
            lines.append(f"\n{'='*80}")
            lines.append(f"[{i}] {article.get('Title', '无标题')}")
            lines.append(f"作者: {article.get('Authors', '无作者')}")
            lines.append(f"期刊: {article.get('Journal', '无期刊')} ({article.get('Publication Date', '无日期')})")
            lines.append(f"PMID: {article.get('PMID', 'N/A')}")
            if article.get('DOI'):
                lines.append(f"DOI: {article['DOI']}")
            if show_abstract:
                abstract = article.get('Abstract', '无摘要')
                # 限制摘要长度
                if len(abstract) > 500:
                    abstract = abstract[:500] + "..."
                lines.append(f"\n摘要:\n{abstract}")

        return "\n".join(lines)

    @staticmethod
    def format_json(articles: List[Dict[str, Any]]) -> str:
        """格式化 JSON 输出"""
        return json.dumps(articles, ensure_ascii=False, indent=2)

    @staticmethod
    def format_markdown(articles: List[Dict[str, Any]]) -> str:
        """格式化 Markdown 输出"""
        if not articles:
            return "# 搜索结果\n\n未找到文章"

        lines = ["# PubMed 搜索结果\n"]
        lines.append(f"共找到 {len(articles)} 篇文章\n")

        for i, article in enumerate(articles, 1):
            lines.append(f"## {i}. {article.get('Title', '无标题')}\n")
            lines.append(f"- **作者**: {article.get('Authors', '无作者')}")
            lines.append(f"- **期刊**: {article.get('Journal', '无期刊')} ({article.get('Publication Date', '无日期')})")
            lines.append(f"- **PMID**: {article.get('PMID', 'N/A')}")
            if article.get('DOI'):
                lines.append(f"- **DOI**: {article['DOI']}")
            lines.append(f"\n**摘要**:\n{article.get('Abstract', '无摘要')}\n")
            lines.append("---\n")

        return "\n".join(lines)

    @staticmethod
    def save_output(content: str, output_path: str) -> bool:
        """保存输出到文件"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✓ 输出已保存到: {output_file}")
            return True

        except Exception as e:
            print(f"错误: 保存文件失败: {e}")
            return False


# ============================================
# 主程序
# ============================================

def main():
    parser = argparse.ArgumentParser(
        description='PubMed-Search: 生物医学文献搜索和分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 关键词搜索
  %(prog)s search --keywords "COVID-19 vaccine" --results 10

  # 高级搜索
  %(prog)s search --term "cancer" --author "Smith" --journal "Nature" --start-date "2020" --end-date "2023"

  # 获取文章元数据
  %(prog)s metadata --pmid "12345678"

  # 深度分析
  %(prog)s analyze --pmid "12345678" --output analysis.md

  # 下载 PDF
  %(prog)s download --pmid "12345678" --output-dir ./papers/
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 搜索命令
    search_parser = subparsers.add_parser('search', help='搜索文章')
    search_parser.add_argument('--keywords', help='搜索关键词')
    search_parser.add_argument('--term', help='通用搜索词')
    search_parser.add_argument('--title', help='标题搜索词')
    search_parser.add_argument('--author', help='作者姓名')
    search_parser.add_argument('--journal', help='期刊名称')
    search_parser.add_argument('--start-date', help='开始日期 (YYYY/MM/DD)')
    search_parser.add_argument('--end-date', help='结束日期 (YYYY/MM/DD)')
    search_parser.add_argument('--results', type=int, default=10, help='返回结果数量 (默认: 10)')
    search_parser.add_argument('--output', help='输出文件路径')
    search_parser.add_argument('--format', choices=['console', 'json', 'markdown'],
                              default='console', help='输出格式 (默认: console)')
    search_parser.add_argument('--show-abstract', action='store_true', help='显示摘要')

    # 元数据命令
    metadata_parser = subparsers.add_parser('metadata', help='获取文章元数据')
    metadata_parser.add_argument('--pmid', required=True, help='PubMed ID')
    metadata_parser.add_argument('--output', help='输出文件路径')
    metadata_parser.add_argument('--format', choices=['console', 'json', 'markdown'],
                                default='console', help='输出格式 (默认: console)')

    # 分析命令
    analyze_parser = subparsers.add_parser('analyze', help='深度分析文章')
    analyze_parser.add_argument('--pmid', required=True, help='PubMed ID')
    analyze_parser.add_argument('--output', help='输出文件路径')

    # 下载命令
    download_parser = subparsers.add_parser('download', help='下载文章 PDF')
    download_parser.add_argument('--pmid', required=True, help='PubMed ID')
    download_parser.add_argument('--output-dir', default='.', help='输出目录 (默认: 当前目录)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # 加载配置
    config = Config()
    searcher = PubMedSearch(config)

    if args.command == 'search':
        # 搜索文章
        if args.keywords:
            articles = searcher.search_by_keywords(args.keywords, args.results)
        else:
            articles = searcher.search_advanced(
                term=args.term, title=args.title, author=args.author,
                journal=args.journal, start_date=args.start_date,
                end_date=args.end_date, num_results=args.results
            )

        if not articles:
            print("未找到匹配的文章")
            return 0

        # 格式化输出
        if args.format == 'json':
            output = OutputHandler.format_json(articles)
        elif args.format == 'markdown':
            output = OutputHandler.format_markdown(articles)
        else:
            output = OutputHandler.format_console(articles, args.show_abstract)

        # 输出结果
        print(output)

        # 保存到文件
        if args.output:
            OutputHandler.save_output(output, args.output)

    elif args.command == 'metadata':
        # 获取元数据
        metadata = searcher.get_metadata(args.pmid)

        if not metadata:
            print(f"未找到 PMID: {args.pmid} 的元数据")
            return 1

        # 格式化输出
        if args.format == 'json':
            output = OutputHandler.format_json([metadata])
        elif args.format == 'markdown':
            output = OutputHandler.format_markdown([metadata])
        else:
            output = OutputHandler.format_console([metadata], show_abstract=True)

        print(output)

        if args.output:
            OutputHandler.save_output(output, args.output)

    elif args.command == 'analyze':
        # 深度分析
        metadata = searcher.get_metadata(args.pmid)

        if not metadata:
            print(f"未找到 PMID: {args.pmid} 的元数据")
            return 1

        analysis = searcher.generate_analysis(metadata)

        print(analysis)

        if args.output:
            OutputHandler.save_output(analysis, args.output)

    elif args.command == 'download':
        # 下载 PDF
        result = searcher.download_pdf(args.pmid, args.output_dir)
        print(result)

    return 0


if __name__ == '__main__':
    sys.exit(main())
