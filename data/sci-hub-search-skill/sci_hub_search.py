#!/usr/bin/env python3
"""
Sci-Hub-Search: 学术文献搜索和下载工具
支持通过 DOI、标题、关键词搜索并下载 Sci-Hub 上的论文
"""

import os
import sys
import json
import argparse
import urllib3
from pathlib import Path
from typing import Optional, Dict, List, Any

try:
    from scihub import SciHub
except ImportError:
    print("错误: 需要安装 scihub 库")
    print("安装命令: pip install scihub")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("错误: 需要安装 requests")
    print("安装命令: pip install requests")
    sys.exit(1)

# 禁用 HTTPS 证书验证警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ============================================
# 配置管理
# ============================================

class Config:
    """配置管理类"""

    def __init__(self):
        self.scihub_base_url = os.getenv('SCIHUB_BASE_URL', '')
        self.timeout = int(os.getenv('DOWNLOAD_TIMEOUT', '30'))


# ============================================
# Sci-Hub 搜索
# ============================================

class SciHubSearch:
    """Sci-Hub 搜索类"""

    def __init__(self, config: Config):
        self.config = config
        self.sh = self._create_scihub_instance()

    def _create_scihub_instance(self):
        """创建 SciHub 实例"""
        sh = SciHub()
        sh.timeout = self.config.timeout
        return sh

    def search_by_doi(self, doi: str) -> Dict[str, Any]:
        """
        通过 DOI 在 Sci-Hub 上搜索论文

        Args:
            doi: Digital Object Identifier

        Returns:
            论文信息字典
        """
        try:
            result = self.sh.fetch(doi)
            return {
                'doi': doi,
                'pdf_url': result['url'],
                'status': 'success',
                'title': result.get('title', ''),
                'author': result.get('author', ''),
                'year': result.get('year', '')
            }
        except Exception as e:
            return {
                'doi': doi,
                'status': 'not_found',
                'error': str(e)
            }

    def search_by_title(self, title: str) -> Dict[str, Any]:
        """
        通过标题在 Sci-Hub 上搜索论文
        首先从 CrossRef 获取 DOI，然后使用 DOI 搜索

        Args:
            title: 论文标题

        Returns:
            论文信息字典
        """
        try:
            # 从 CrossRef 获取 DOI
            url = f"https://api.crossref.org/works?query.title={title}&rows=1"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data['message']['items']:
                    doi = data['message']['items'][0]['DOI']
                    result = self.search_by_doi(doi)
                    result['search_title'] = title
                    return result
                else:
                    return {
                        'title': title,
                        'status': 'not_found',
                        'error': 'No papers found in CrossRef'
                    }
            else:
                return {
                    'title': title,
                    'status': 'error',
                    'error': f'CrossRef API error: {response.status_code}'
                }
        except Exception as e:
            return {
                'title': title,
                'status': 'error',
                'error': str(e)
            }

    def search_by_keyword(self, keyword: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        通过关键词搜索论文

        Args:
            keyword: 搜索关键词
            num_results: 返回结果数量

        Returns:
            论文信息列表
        """
        papers = []

        try:
            # 使用 CrossRef API 搜索
            url = f"https://api.crossref.org/works?query={keyword}&rows={num_results}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                for item in data['message']['items']:
                    doi = item.get('DOI')
                    if doi:
                        result = self.search_by_doi(doi)
                        if result['status'] == 'success':
                            # 添加额外信息
                            result['keyword'] = keyword
                            # 如果标题为空，尝试从 CrossRef 获取
                            if not result.get('title'):
                                result['title'] = item.get('title', [''])[0] if item.get('title') else ''
                        papers.append(result)

        except Exception as e:
            print(f"关键词搜索出错: {e}")

        return papers

    def download_paper(self, identifier: str, output_path: str, is_url: bool = False) -> bool:
        """
        下载论文 PDF

        Args:
            identifier: DOI 或 PDF URL
            output_path: 输出文件路径
            is_url: 是否为直接 URL

        Returns:
            是否下载成功
        """
        try:
            if is_url:
                # 直接使用 URL 下载
                result = self.sh.download(identifier, path=output_path)
                return result is not None
            else:
                # 使用 DOI 搜索并下载
                result = self.sh.fetch(identifier)
                if result and 'url' in result:
                    return self.sh.download(result['url'], path=output_path) is not None
                return False
        except Exception as e:
            print(f"下载出错: {e}")
            return False

    def get_metadata(self, doi: str) -> Dict[str, Any]:
        """
        获取论文元数据

        Args:
            doi: Digital Object Identifier

        Returns:
            论文元数据字典
        """
        result = self.search_by_doi(doi)
        if result['status'] == 'success':
            return {
                'doi': doi,
                'title': result.get('title', ''),
                'author': result.get('author', ''),
                'year': result.get('year', ''),
                'pdf_url': result.get('pdf_url', ''),
                'status': 'success'
            }
        else:
            return {
                'error': f"Could not find metadata for DOI {doi}",
                'status': 'error'
            }


# ============================================
# 输出处理
# ============================================

class OutputHandler:
    """输出处理类"""

    @staticmethod
    def format_console(result: Dict[str, Any] | List[Dict[str, Any]], show_url: bool = True) -> str:
        """格式化控制台输出"""
        if isinstance(result, list):
            # 多个结果
            if not result:
                return "未找到论文"
            lines = []
            for i, paper in enumerate(result, 1):
                lines.append(f"\n{'='*80}")
                lines.append(f"[{i}] {paper.get('title', '无标题')}")
                lines.append(f"作者: {paper.get('author', '未知')}")
                lines.append(f"年份: {paper.get('year', '未知')}")
                lines.append(f"DOI: {paper.get('doi', 'N/A')}")
                if show_url and paper.get('pdf_url'):
                    lines.append(f"PDF URL: {paper['pdf_url']}")
            return "\n".join(lines)
        else:
            # 单个结果
            if result.get('status') == 'success':
                lines = [
                    f"标题: {result.get('title', '无标题')}",
                    f"作者: {result.get('author', '未知')}",
                    f"年份: {result.get('year', '未知')}",
                    f"DOI: {result.get('doi', 'N/A')}"
                ]
                if show_url and result.get('pdf_url'):
                    lines.append(f"PDF URL: {result['pdf_url']}")
                return "\n".join(lines)
            else:
                return f"未找到论文: {result.get('error', '未知错误')}"

    @staticmethod
    def format_json(result: Dict[str, Any] | List[Dict[str, Any]]) -> str:
        """格式化 JSON 输出"""
        return json.dumps(result, ensure_ascii=False, indent=2)

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
        description='Sci-Hub-Search: 学术文献搜索和下载工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 通过 DOI 搜索
  %(prog)s search --doi "10.1002/jcad.12075"

  # 通过标题搜索
  %(prog)s search --title "CRISPR gene editing"

  # 通过关键词搜索
  %(prog)s search --keyword "artificial intelligence" --results 10

  # 获取元数据
  %(prog)s metadata --doi "10.1002/jcad.12075"

  # 下载论文
  %(prog)s download --doi "10.1002/jcad.12075" --output paper.pdf

  # 通过 URL 下载
  %(prog)s download --url "https://sci-hub.se/xxxxx" --output paper.pdf
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 搜索命令
    search_parser = subparsers.add_parser('search', help='搜索论文')
    search_group = search_parser.add_mutually_exclusive_group(required=True)
    search_group.add_argument('--doi', help='DOI (Digital Object Identifier)')
    search_group.add_argument('--title', help='论文标题')
    search_group.add_argument('--keyword', help='关键词')
    search_parser.add_argument('--results', type=int, default=10, help='返回结果数量 (仅用于关键词搜索, 默认: 10)')
    search_parser.add_argument('--output', help='输出文件路径')
    search_parser.add_argument('--format', choices=['console', 'json'], default='console', help='输出格式 (默认: console)')
    search_parser.add_argument('--hide-url', action='store_true', help='隐藏 PDF URL')

    # 元数据命令
    metadata_parser = subparsers.add_parser('metadata', help='获取论文元数据')
    metadata_parser.add_argument('--doi', required=True, help='DOI (Digital Object Identifier)')
    metadata_parser.add_argument('--output', help='输出文件路径')
    metadata_parser.add_argument('--format', choices=['console', 'json'], default='console', help='输出格式 (默认: console)')

    # 下载命令
    download_parser = subparsers.add_parser('download', help='下载论文 PDF')
    download_group = download_parser.add_mutually_exclusive_group(required=True)
    download_group.add_argument('--doi', help='DOI (Digital Object Identifier)')
    download_group.add_argument('--url', help='直接 PDF URL')
    download_parser.add_argument('--output', required=True, help='输出 PDF 文件路径')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # 加载配置
    config = Config()
    searcher = SciHubSearch(config)

    if args.command == 'search':
        if args.doi:
            result = searcher.search_by_doi(args.doi)
        elif args.title:
            result = searcher.search_by_title(args.title)
        else:  # keyword
            result = searcher.search_by_keyword(args.keyword, args.results)

        # 格式化输出
        if args.format == 'json':
            output = OutputHandler.format_json(result)
        else:
            output = OutputHandler.format_console(result, show_url=not args.hide_url)

        print(output)

        if args.output:
            OutputHandler.save_output(output, args.output)

    elif args.command == 'metadata':
        metadata = searcher.get_metadata(args.doi)

        if args.format == 'json':
            output = OutputHandler.format_json(metadata)
        else:
            output = OutputHandler.format_console(metadata, show_url=True)

        print(output)

        if args.output:
            OutputHandler.save_output(output, args.output)

    elif args.command == 'download':
        print("正在下载论文...")

        if args.url:
            success = searcher.download_paper(args.url, args.output, is_url=True)
        else:  # doi
            success = searcher.download_paper(args.doi, args.output, is_url=False)

        if success:
            print(f"✓ 论文已成功下载到: {args.output}")
        else:
            print(f"✗ 下载失败，请检查 DOI 或 URL 是否正确")
            return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
