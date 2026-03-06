#!/usr/bin/env python3
"""
UniFuncs Web Reader API 调用脚本
用法: ./read.py "URL" [选项]
"""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List


class UniFuncsReaderError(Exception):
    """UniFuncs Reader API 错误"""
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


def validate_url(url: str) -> bool:
    """
    验证 URL 格式（宽松检查）

    参数:
        url: 需要验证的 URL

    返回:
        True 如果 URL 看起来合法，否则 False
    """
    try:
        result = urllib.parse.urlparse(url)
        # 有协议+域名，或仅有域名，或仅有路径
        return bool(result.netloc or result.path)
    except Exception:
        return False


def read_url(
    url: str,
    api_key: str,
    format_type: str = "md",
    lite_mode: bool = False,
    include_images: bool = True,
    only_css_selectors: Optional[List[str]] = None,
    wait_for_css_selectors: Optional[List[str]] = None,
    exclude_css_selectors: Optional[List[str]] = None,
    link_summary: bool = False,
    ignore_cache: bool = False,
    set_cookie: Optional[str] = None,
    read_timeout: int = 120000,
    topic: Optional[str] = None,
    preserve_source: bool = False,
    temperature: float = 0.2,
    extract_timeout: int = 120000
) -> Dict[str, Any] | str:
    """
    调用 UniFuncs Reader API

    参数:
        url: 需要阅读的URL
        api_key: API Key
        format_type: 返回格式 (markdown/md/text/txt)
        lite_mode: 是否启用精简模式
        include_images: 是否包含图片
        only_css_selectors: 仅包含匹配CSS选择器的元素
        wait_for_css_selectors: 等待这些CSS选择器元素出现后再解析
        exclude_css_selectors: 排除匹配CSS选择器的元素
        link_summary: 是否将页面中所有链接追加到内容尾部
        ignore_cache: 是否忽略缓存
        set_cookie: 设置Cookie
        read_timeout: 抓取超时时间（毫秒）
        topic: 提取特定主题的内容
        preserve_source: 是否在每个段落添加原文出处
        temperature: 大模型生成内容的随机性 (0.0-1.5)
        extract_timeout: 提取主题内容超时时间（毫秒）

    返回:
        API 响应的 JSON 数据，或纯文本字符串（当 format_type 为 markdown/text 时）
    """
    api_url = "https://api.unifuncs.com/api/web-reader/read"

    # 构建请求数据
    data = {
        "url": url,
        "format": format_type,
        "liteMode": lite_mode,
        "includeImages": include_images,
        "linkSummary": link_summary,
        "ignoreCache": ignore_cache,
        "readTimeout": read_timeout
    }

    # 添加可选参数
    if only_css_selectors:
        data["onlyCSSSelectors"] = only_css_selectors
    if wait_for_css_selectors:
        data["waitForCSSSelectors"] = wait_for_css_selectors
    if exclude_css_selectors:
        data["excludeCSSSelectors"] = exclude_css_selectors
    if set_cookie:
        data["setCookie"] = set_cookie
    if topic:
        data["topic"] = topic
        data["preserveSource"] = preserve_source
        data["temperature"] = temperature
        data["extractTimeout"] = extract_timeout

    # 准备请求
    json_data = json.dumps(data).encode('utf-8')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    req = urllib.request.Request(api_url, data=json_data, headers=headers, method='POST')

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
            raise UniFuncsReaderError(
                f"HTTP {e.code}: {error_data.get('message', '未知错误')}"
            )
        except json.JSONDecodeError:
            raise UniFuncsReaderError(f"HTTP {e.code}: {error_msg}")
    except urllib.error.URLError as e:
        raise UniFuncsReaderError(f"网络错误: {e.reason}")


def handle_error(code: int, message: str) -> None:
    """处理 API 错误状态码"""
    error_messages = {
        -20001: "服务器错误，请联系客服确认原因或稍后再试",
        -20011: "无权限访问，账户可能无权限访问该API",
        -20014: "账户被禁用，请联系客服确认账户禁用原因",
        -20021: "API Key无效或已过期，请检查API Key是否正确且有效",
        -20025: "账户余额不足，请检查账户余额是否充足",
        -20033: "请求超出速率限制，降低请求频率或联系UniFuncs提升您的用户级别",
        -30000: "目标URL非法，请检查URL是否正确",
        -30001: "访问目标URL失败，请检查URL是否正确",
        -30002: "请求超时，请重试抓取",
        -30003: "访问目标URL的内容为空，尝试重新抓取或更换URL",
        -30004: "可能目标URL拒绝访问或需要验证，尝试重新抓取或更换URL"
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
    return json.dumps(response, ensure_ascii=False, indent=2)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='UniFuncs 网页阅读 API 调用工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s '{"url": "https://mp.weixin.qq.com/s/wmoNh44A4ofkawPNVx_g6A", "format": "md"}'
        """
    )

    parser.add_argument('url', help='需要阅读的URL')
    parser.add_argument('--format', dest='format_type',
                        choices=['markdown', 'md', 'text', 'txt'],
                        default='md',
                        help='返回格式 (默认: md)')
    parser.add_argument('--lite-mode', action='store_true',
                        help='启用精简模式，只保留具备可读性的内容')
    parser.add_argument('--no-images', action='store_true',
                        help='不包含图片')
    parser.add_argument('--only-css-selectors', nargs='+',
                        help='仅包含匹配CSS选择器的元素 (如: ".article_content")')
    parser.add_argument('--wait-for-css-selectors', nargs='+',
                        help='等待这些CSS选择器元素出现后再解析 (如: "#main" ".content")')
    parser.add_argument('--exclude-css-selectors', nargs='+',
                        help='排除匹配CSS选择器的元素 (如: "#footer" ".copyright")')
    parser.add_argument('--link-summary', action='store_true',
                        help='将页面中所有链接追加到内容尾部')
    parser.add_argument('--ignore-cache', action='store_true',
                        help='忽略缓存')
    parser.add_argument('--set-cookie', type=str,
                        help='设置Cookie，对于需要验证的页面很有用')
    parser.add_argument('--read-timeout', type=int, default=120000,
                        help='抓取超时时间（毫秒）(默认: 120000)')
    parser.add_argument('--topic', type=str,
                        help='提取页面中某个主题的相关内容（使用大模型）')
    parser.add_argument('--preserve-source', action='store_true',
                        help='在提取内容的每个段落添加原文出处')
    parser.add_argument('--temperature', type=float, default=0.2,
                        help='提取内容时大模型生成内容的随机性，范围 0.0-1.5 (默认: 0.2)')
    parser.add_argument('--extract-timeout', type=int, default=120000,
                        help='提取主题内容超时时间（毫秒）(默认: 120000)')

    args = parser.parse_args()

    # 验证参数
    if not args.url or not args.url.strip():
        print("错误: URL 不能为空", file=sys.stderr)
        sys.exit(1)

    if not validate_url(args.url):
        print("错误: URL 格式不合法，请检查 URL 是否正确", file=sys.stderr)
        sys.exit(1)

    if args.temperature < 0.0 or args.temperature > 1.5:
        print("错误: temperature 参数必须在 0.0-1.5 之间", file=sys.stderr)
        sys.exit(1)

    # 获取 API Key
    api_key = get_api_key()

    try:
        # 执行读取
        response = read_url(
            url=args.url,
            api_key=api_key,
            format_type=args.format_type,
            lite_mode=args.lite_mode,
            include_images=not args.no_images,
            only_css_selectors=args.only_css_selectors,
            wait_for_css_selectors=args.wait_for_css_selectors,
            exclude_css_selectors=args.exclude_css_selectors,
            link_summary=args.link_summary,
            ignore_cache=args.ignore_cache,
            set_cookie=args.set_cookie,
            read_timeout=args.read_timeout,
            topic=args.topic,
            preserve_source=args.preserve_source,
            temperature=args.temperature,
            extract_timeout=args.extract_timeout
        )

        # 输出结果
        output = format_output(response, args.format_type)
        print(output)

    except UniFuncsReaderError as e:
        print(f"读取失败: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n读取已取消", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"未预期的错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
