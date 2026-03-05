#!/usr/bin/env python3
"""
UniFuncs Web Search API 调用脚本
用法: ./search.py "搜索关键词" [选项]
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from typing import Optional, Dict, Any


class UniFuncsSearchError(Exception):
    """UniFuncs 搜索 API 错误"""
    pass


def get_api_key() -> str:
    """
    获取 API Key - 从环境变量读取

    返回:
        API Key 字符串

    异常:
        SystemExit: 如果未设置 UNIFUNCS_API_KEY 环境变量
    """
    api_key = os.environ.get('UNIFUNCS_API_KEY')
    if not api_key:
        print("错误: 未设置 UNIFUNCS_API_KEY 环境变量", file=sys.stderr)
        print("请访问 https://unifuncs.com/account 获取 API Key", file=sys.stderr)
        sys.exit(1)
    return api_key


def search(
    query: str,
    api_key: str,
    area: str = "global",
    freshness: Optional[str] = None,
    include_images: bool = False,
    page: int = 1,
    count: int = 10,
    format_type: str = "json"
) -> Dict[str, Any] | str:
    """
    调用 UniFuncs 搜索 API

    参数:
        query: 搜索查询词
        api_key: API Key
        area: 搜索地区 (global/cn)
        freshness: 结果时效性 (Day/Week/Month/Year)
        include_images: 是否包含图像搜索
        page: 页码
        count: 每页结果数量 (1-50)
        format_type: 返回格式 (json/markdown/md/text/txt)

    返回:
        API 响应的 JSON 数据，或纯文本字符串（当 format_type 为 markdown/text 时）
    """
    url = "https://api.unifuncs.com/api/web-search/search"

    # 构建请求数据
    data = {
        "query": query,
        "area": area,
        "page": page,
        "count": count,
        "format": format_type,
        "includeImages": include_images
    }

    # 添加可选参数
    if freshness:
        data["freshness"] = freshness

    # 准备请求
    json_data = json.dumps(data).encode('utf-8')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    req = urllib.request.Request(url, data=json_data, headers=headers, method='POST')

    try:
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode('utf-8')
            # 尝试解析为 JSON
            try:
                return json.loads(response_data)
            except json.JSONDecodeError:
                # API 返回的是纯文本格式（markdown/text），直接返回字符串
                return response_data
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode('utf-8')
        try:
            error_data = json.loads(error_msg)
            raise UniFuncsSearchError(
                f"HTTP {e.code}: {error_data.get('message', '未知错误')}"
            )
        except json.JSONDecodeError:
            raise UniFuncsSearchError(f"HTTP {e.code}: {error_msg}")
    except urllib.error.URLError as e:
        raise UniFuncsSearchError(f"网络错误: {e.reason}")


def handle_error(code: int, message: str) -> None:
    """处理 API 错误状态码"""
    error_messages = {
        -20001: "服务器错误，请联系客服确认原因或稍后再试",
        -20011: "无权限访问，账户可能无权限访问该API",
        -20014: "账户被禁用，请联系客服确认账户禁用原因",
        -20021: "API Key无效或已过期，请检查API Key是否正确且有效",
        -20025: "账户余额不足，请检查账户余额是否充足",
        -20033: "请求超出速率限制，降低请求频率或联系UniFuncs提升您的用户级别",
        -30000: "搜索失败，请联系客服确认失败原因",
        -30001: "搜索关键词无效，请检查搜索关键词是否正确"
    }

    error_detail = error_messages.get(code, message)
    print(f"错误 [{code}]: {error_detail}", file=sys.stderr)
    sys.exit(1)


def format_output(response: Dict[str, Any] | str, output_format: str) -> str:
    """格式化输出结果"""
    # 如果已经是字符串（API 返回的文本格式），直接返回
    if isinstance(response, str):
        return response

    code = response.get('code', -1)

    # 检查错误
    if code != 0:
        handle_error(code, response.get('message', '未知错误'))

    # 如果 API 返回的格式已经是文本格式，直接返回
    if output_format in ['markdown', 'md', 'text', 'txt']:
        data = response.get('data', '')
        if isinstance(data, str):
            return data

    # JSON 格式输出
    if output_format == 'json':
        return json.dumps(response, ensure_ascii=False, indent=2)

    # Markdown 格式输出
    data = response.get('data', {})
    web_pages = data.get('webPages', [])
    images = data.get('images', [])

    output = []
    output.append(f"# 搜索结果\n")
    output.append(f"共找到 {len(web_pages)} 条网页结果\n")

    for i, page in enumerate(web_pages, 1):
        output.append(f"\n## {i}. {page.get('name', '无标题')}")
        output.append(f"**URL**: {page.get('url', '')}")
        if page.get('siteName'):
            output.append(f"**来源**: {page.get('siteName')}")
        output.append(f"\n{page.get('snippet', page.get('summary', ''))}\n")

    if images:
        output.append(f"\n---\n\n# 图片结果 ({len(images)} 张)\n")
        for i, img in enumerate(images, 1):
            output.append(f"{i}. ![图片]({img.get('thumbnailUrl', '')})")
            output.append(f"   原图: {img.get('contentUrl', '')}\n")

    return '\n'.join(output)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='UniFuncs 实时搜索 API 调用工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s "今日金价" --page 1 --count 5
        """
    )

    parser.add_argument('query', help='搜索查询词')
    parser.add_argument('--area', choices=['global', 'cn'], default='global',
                        help='搜索地区 (默认: global)')
    parser.add_argument('--freshness', choices=['Day', 'Week', 'Month', 'Year'],
                        help='结果时效性')
    parser.add_argument('--include-images', action='store_true',
                        help='同时搜索图像')
    parser.add_argument('--page', type=int, default=1,
                        help='页码 (默认: 1)')
    parser.add_argument('--count', type=int, default=10,
                        help='每页结果数量，范围 1-50 (默认: 10)')
    parser.add_argument('--format', dest='format_type',
                        choices=['json', 'markdown', 'md', 'text', 'txt'],
                        default='json',
                        help='输出格式 (默认: json)')

    args = parser.parse_args()

    # 验证参数
    if not args.query or not args.query.strip():
        print("错误: 搜索关键词不能为空", file=sys.stderr)
        sys.exit(1)

    if not 1 <= args.count <= 50:
        print("错误: count 参数必须在 1-50 之间", file=sys.stderr)
        sys.exit(1)

    # 获取 API Key
    api_key = get_api_key()

    try:
        # 执行搜索
        response = search(
            query=args.query,
            api_key=api_key,
            area=args.area,
            freshness=args.freshness,
            include_images=args.include_images,
            page=args.page,
            count=args.count,
            format_type=args.format_type
        )

        # 输出结果
        output = format_output(response, args.format_type)
        print(output)

    except UniFuncsSearchError as e:
        print(f"搜索失败: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n搜索已取消", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"未预期的错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
