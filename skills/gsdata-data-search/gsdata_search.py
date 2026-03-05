#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GSData 项目数据搜索技能
GSData Project Data Search Skill

功能：
- 解析自然语言搜索请求
- 验证必填参数（project_id、sign）
- 生成符合GSData API规范的请求参数
- 支持提取关键词、平台、情感属性、发文时间、文章数量等参数
- 调用API获取数据并返回指定字段

API地址：http://projects-databus.gsdata.cn:7777/api-project/service

支持的请求参数：
- project_id（必填）：项目ID
- sign（必填）：签名值
- router（固定值）：/standard/search/get-data
- params（JSON格式）：
  - keywords_include：关键词
  - media_name：账号名称
  - platform_name：平台名称
  - posttime_start：发文开始时间
  - posttime_end：发文结束时间
  - is_content：固定值0
  - paging_type：固定值page
  - page：页码，默认1
  - limit：每页条数，最大20

返回字段：
- platform_name：平台名称
- media_name：账号名称
- news_url：新闻链接
- news_title：新闻标题
- news_posttime：发文时间
- news_digest：新闻摘要
- news_is_origin：是否原创（1原创，0非原创）
- news_emotion：情感属性

使用示例：
自然语言输入："帮我获取10篇关于吉利汽车 微博或者抖音的最新负面新闻"
输出：符合API规范的JSON参数
"""

import re
import json
import argparse
import sys
import os
from datetime import datetime, timedelta


def get_config_file_path() -> str:
    """
    获取配置文件的路径
    """
    # 配置文件存储在技能目录下的config.json
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')


def load_config() -> dict:
    """
    从配置文件中读取参数
    """
    config_file = get_config_file_path()
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f'加载配置文件失败: {str(e)}', file=sys.stderr)
    return {}


def save_config(project_id: str, sign: str) -> bool:
    """
    将参数保存到配置文件
    """
    config_file = get_config_file_path()
    try:
        config_data = {
            'project_id': project_id,
            'sign': sign
        }
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f'保存配置文件失败: {str(e)}', file=sys.stderr)
        return False


def clear_config() -> bool:
    """
    清除配置文件中的内容
    """
    config_file = get_config_file_path()
    try:
        if os.path.exists(config_file):
            os.remove(config_file)
        return True
    except Exception as e:
        print(f'清除配置文件失败: {str(e)}', file=sys.stderr)
        return False


def show_config() -> str:
    """
    显示当前配置文件内容
    """
    config_file = get_config_file_path()
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            return json.dumps(config_data, ensure_ascii=False, indent=2)
        else:
            return '配置文件不存在'
    except Exception as e:
        return f'读取配置文件失败: {str(e)}'


def parse_gsdata_params(text: str) -> str:
    """
    解析自然语言输入并生成GSData API请求参数的JSON格式

    Args:
        text: 自然语言输入文本

    Returns:
        符合规范的JSON字符串或错误提示
    """
    # 初始化参数 - 先尝试从配置文件加载
    config = load_config()
    params = {
        'project_id': config.get('project_id', ''),
        'sign': config.get('sign', ''),
        'router': '/standard/search/get-data',
        'params': {
            'keywords_include': '',
            'media_name': '',
            'platform_name': '',
            'posttime_start': '',
            'posttime_end': '',
            'is_content': 0,
            'paging_type': 'page',
            'page': 1,
            'limit': 20
        }
    }

    # 识别文章数量
    article_count_match = re.search(r'(\d+)\s*篇|(\d+)\s*条|(\d+)\s*个', text, re.IGNORECASE)
    if article_count_match:
        count = 0
        for group in article_count_match.groups():
            if group:
                count = int(group.strip())
                break
        if count > 0:
            params['params']['limit'] = min(count, 20)

    # 识别平台名称
    platforms = []
    if re.search(r'微博', text):
        platforms.append('微博')
    if re.search(r'抖音', text):
        platforms.append('抖音')
    if re.search(r'微信', text):
        platforms.append('微信')
    if re.search(r'知乎', text):
        platforms.append('知乎')
    if re.search(r'小红书', text):
        platforms.append('小红书')
    if re.search(r'今日头条|头条', text):
        platforms.append('今日头条')
    if re.search(r'快手', text):
        platforms.append('快手')
    if platforms:
        params['params']['platform_name'] = ','.join(platforms)

    # 识别关键词（从"关于XX"或"关于XX的"模式中提取）
    keyword_match = re.search(r'关于\s*([^\s的]+)(?:\s*的)?', text, re.IGNORECASE)
    if keyword_match:
        keyword = keyword_match.group(1).strip()
        # 移除关键词中的相对时间词汇
        relative_time_patterns = r'近一天|最近一天|过去一天|近3天|最近3天|过去3天|近三天|最近三天|过去三天|近一周|最近一周|过去一周|近7天|最近7天|近两周|最近两周|过去两周|近14天|最近14天|近一个月|最近一个月|过去一个月|近30天|最近30天|近三个月|最近三个月|过去三个月|近90天|最近90天|近期|最近|最新'
        keyword = re.sub(relative_time_patterns, '', keyword, flags=re.IGNORECASE).strip()
        params['params']['keywords_include'] = keyword

    # 识别情感属性
    if re.search(r'负面', text, re.IGNORECASE):
        params['params']['news_emotion'] = '负面'
    elif re.search(r'正面', text, re.IGNORECASE):
        params['params']['news_emotion'] = '正面'
    elif re.search(r'中性', text, re.IGNORECASE):
        params['params']['news_emotion'] = '中性'

    # 优先提取必填参数 project_id (同时支持项目id、project_id)
    project_id_match = re.search(r'(项目id|project_id)[:：]?\s*([^\s，；。！？,;.!?]+)', text, re.IGNORECASE)
    if project_id_match:
        params['project_id'] = project_id_match.group(2).strip()

    # 优先提取必填参数 sign (同时支持签名、sign)
    sign_match = re.search(r'(签名|sign)[:：]?\s*([^\s，；。！？,;.!?]+)', text, re.IGNORECASE)
    if sign_match:
        params['sign'] = sign_match.group(2).strip()

    # 提取关键词 (同时支持关键词、keywords_include)
    keyword_match = re.search(r'(关键词|keywords_include)[:：]?\s*', text, re.IGNORECASE)
    if keyword_match:
        start_idx = keyword_match.end()
        # 查找下一个参数名称的位置
        next_param_pattern = r'平台|platform_name|发文时间|posttime|账号名称|media_name|每页条数|limit|页码|page'
        next_param_match = re.search(next_param_pattern, text[start_idx:], re.IGNORECASE)
        if next_param_match:
            end_idx = start_idx + next_param_match.start()
            value = text[start_idx:end_idx].strip()
        else:
            value = text[start_idx:].strip()
        # 去除多余的标点符号
        while value and value[-1] in '，；。！？,;.!?':
            value = value[:-1].strip()
        params['params']['keywords_include'] = value

    # 提取账号名称 (同时支持账号名称、media_name)
    media_name_match = re.search(r'(账号名称|media_name)[:：]?\s*', text, re.IGNORECASE)
    if media_name_match:
        start_idx = media_name_match.end()
        # 查找下一个参数名称的位置
        next_param_pattern = r'平台|platform_name|发文时间|posttime|每页条数|limit|页码|page'
        next_param_match = re.search(next_param_pattern, text[start_idx:], re.IGNORECASE)
        if next_param_match:
            end_idx = start_idx + next_param_match.start()
            value = text[start_idx:end_idx].strip()
        else:
            value = text[start_idx:].strip()
        # 去除多余的标点符号
        while value and value[-1] in '，；。！？,;.!?':
            value = value[:-1].strip()
        params['params']['media_name'] = value

    # 提取平台名称 (同时支持平台|平台名称|platform_name)
    platform_match = re.search(r'(平台名称|platform_name|平台)[:：]?\s*([^\s，；。！？,;.!?]+)', text, re.IGNORECASE)
    if platform_match:
        params['params']['platform_name'] = platform_match.group(2).strip()

    # 处理相对时间
    def handle_relative_time(text: str) -> tuple:
        """
        处理相对时间，如"近一天"、"近期"、"近一周"等
        """
        now = datetime.now()
        # 结束时间不能大于当前时间减10分钟
        end_time = now - timedelta(minutes=10)

        # 近一天（24小时内）
        if re.search(r'近一天|最近一天|过去一天', text, re.IGNORECASE):
            start_time = end_time - timedelta(days=1)
            return (start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S'))

        # 近3天
        if re.search(r'近3天|最近3天|过去3天|近三天|最近三天|过去三天', text, re.IGNORECASE):
            start_time = end_time - timedelta(days=3)
            return (start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S'))

        # 近一周（7天）
        if re.search(r'近一周|最近一周|过去一周|近7天|最近7天', text, re.IGNORECASE):
            start_time = end_time - timedelta(days=7)
            return (start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S'))

        # 近两周
        if re.search(r'近两周|最近两周|过去两周|近14天|最近14天', text, re.IGNORECASE):
            start_time = end_time - timedelta(days=14)
            return (start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S'))

        # 近一个月（30天）
        if re.search(r'近一个月|最近一个月|过去一个月|近30天|最近30天', text, re.IGNORECASE):
            start_time = end_time - timedelta(days=30)
            return (start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S'))

        # 近三个月
        if re.search(r'近三个月|最近三个月|过去三个月|近90天|最近90天', text, re.IGNORECASE):
            start_time = end_time - timedelta(days=90)
            return (start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S'))

        # 近期（默认7天）
        if re.search(r'近期|最近|最新', text, re.IGNORECASE):
            start_time = end_time - timedelta(days=7)
            return (start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S'))

        return (None, None)

    # 首先处理相对时间
    start_time, end_time = handle_relative_time(text)
    if start_time and end_time:
        params['params']['posttime_start'] = start_time
        params['params']['posttime_end'] = end_time

    # 提取发文时间 (同时支持发文时间|发布时间|posttime|时间)
    posttime_match = re.search(r'(发文时间|发布时间|posttime|时间)[:：]?\s*', text, re.IGNORECASE)
    if posttime_match:
        start_idx = posttime_match.end()
        # 查找下一个参数名称的位置
        next_param_pattern = r'平台|platform_name|账号名称|media_name|每页条数|limit|页码|page'
        next_param_match = re.search(next_param_pattern, text[start_idx:], re.IGNORECASE)
        if next_param_match:
            end_idx = start_idx + next_param_match.start()
            value = text[start_idx:end_idx].strip()
        else:
            value = text[start_idx:].strip()
        # 去除多余的标点符号
        while value and value[-1] in '，；。！？,;.!?':
            value = value[:-1].strip()
        # 处理时间范围 (如 "2024-03-12 到 2024-03-13" 或 "2024-03-12")
        time_range_match = re.search(r'(\d{4}-\d{1,2}-\d{1,2}(?:\s+\d{1,2}:\d{1,2}:\d{1,2})?)\s*[到至]\s*(\d{4}-\d{1,2}-\d{1,2}(?:\s+\d{1,2}:\d{1,2}:\d{1,2})?)', value)
        if time_range_match:
            params['params']['posttime_start'] = time_range_match.group(1).strip()
            params['params']['posttime_end'] = time_range_match.group(2).strip()
        else:
            single_time_match = re.search(r'(\d{4}-\d{1,2}-\d{1,2}(?:\s+\d{1,2}:\d{1,2}:\d{1,2})?)', value)
            if single_time_match:
                params['params']['posttime_start'] = single_time_match.group(1).strip()
                params['params']['posttime_end'] = single_time_match.group(1).strip()

    # 提取每页条数 (同时支持每页条数|limit)
    page_size_match = re.search(r'(每页条数|limit)[:：]?\s*(\d+)', text, re.IGNORECASE)
    if page_size_match:
        try:
            size = int(page_size_match.group(2).strip())
            params['params']['limit'] = min(size, 20)
        except ValueError:
            params['params']['limit'] = 20

    # 提取页码 (同时支持页码|page)
    page_number_match = re.search(r'(页码|page)[:：]?\s*(\d+)', text, re.IGNORECASE)
    if page_number_match:
        try:
            page = int(page_number_match.group(2).strip())
            params['params']['page'] = max(page, 1)
        except ValueError:
            params['params']['page'] = 1

    # 检查必填参数
    if not params['project_id'] or not params['sign']:
        return '请补充必填参数：project_id、sign'

    if not params['params']['keywords_include']:
        return '请补充搜索关键词'

    # 生成JSON输出
    return json.dumps(params, ensure_ascii=False, indent=2)


def call_gsdata_api(params_json: str) -> str:
    """
    调用GSData API并返回处理后的数据

    Args:
        params_json: 符合API规范的JSON参数

    Returns:
        API返回的数据或错误信息
    """
    try:
        # 动态导入requests库，避免未安装时影响参数解析
        import requests

        params = json.loads(params_json)
        api_url = 'http://projects-databus.gsdata.cn:7777/api-project/service'

        # 构建请求参数
        request_data = {
            'project_id': params['project_id'],
            'sign': params['sign'],
            'router': params['router'],
            'params': json.dumps(params['params'])
        }

        # 发送API请求
        response = requests.post(api_url, data=request_data, timeout=30)

        # 确保正确处理响应编码
        if response.encoding is None or response.encoding == 'ISO-8859-1':
            response.encoding = 'utf-8'

        if response.status_code == 200:
            try:
                # 尝试直接解析响应内容
                content = response.content
                # 尝试UTF-8解码
                try:
                    text_content = content.decode('utf-8')
                except UnicodeDecodeError:
                    # 如果UTF-8解码失败，尝试GBK解码（常见于中文网站）
                    text_content = content.decode('gbk', errors='ignore')

                data = json.loads(text_content)

                # 检查返回数据格式
                if data.get('success') == True and 'data' in data:
                    # 提取需要的字段
                    result = []
                    for item in data.get('data', {}).get('list', []):
                        filtered_item = {
                            'platform_name': item.get('platform_name', ''),
                            'media_name': item.get('media_name', ''),
                            'news_url': item.get('news_url', ''),
                            'news_title': item.get('news_title', ''),
                            'news_posttime': item.get('news_posttime', ''),
                            'news_digest': item.get('news_digest', ''),
                            'news_is_origin': item.get('news_is_origin', 0),
                            'news_emotion': item.get('news_emotion', '')
                        }
                        result.append(filtered_item)

                    # 返回Markdown格式的数据
                    markdown = "## 搜索结果\n\n"
                    markdown += f"共找到 **{len(result)}** 条符合条件的新闻\n\n"

                    # 表格头部
                    markdown += "| 平台名称 | 账号名称 | 新闻标题 | 发文时间 | 新闻摘要 | 是否原创 | 情感属性 | 新闻链接 |\n"
                    markdown += "|---------|---------|---------|---------|---------|---------|---------|---------|\n"

                    # 表格内容
                    for item in result:
                        is_origin = "是" if item['news_is_origin'] == 1 else "否"
                        markdown += f"| {item['platform_name']} | {item['media_name']} | {item['news_title']} | {item['news_posttime']} | {item['news_digest']} | {is_origin} | {item['news_emotion']} | [查看详情]({item['news_url']}) |\n"

                    return markdown
                else:
                    return f"## 错误\n\n**API请求失败**: {data.get('msg', '未知错误')}"

            except Exception as e:
                return f"## 错误\n\n**响应解析错误**: {str(e)}"
        else:
            return f"## 错误\n\n**HTTP请求失败**: 状态码 {response.status_code}"

    except requests.exceptions.RequestException as e:
        return f"## 错误\n\n**网络请求错误**: {str(e)}"
    except json.JSONDecodeError:
        return "## 错误\n\n**参数格式错误**"
    except Exception as e:
        return f"## 错误\n\n**调用API时发生错误**: {str(e)}"


def main():
    """
    命令行接口
    """
    # 确保输出使用 UTF-8 编码
    # 在Windows系统上，默认编码可能是gbk，需要强制设置为utf-8
    if sys.platform.startswith('win'):
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)
    else:
        if sys.stdout.encoding != 'utf-8':
            sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
        if sys.stderr.encoding != 'utf-8':
            sys.stderr = open(sys.stderr.fileno(), mode='w', encoding='utf-8', buffering=1)

    parser = argparse.ArgumentParser(
        description='GSData项目数据搜索技能 - 解析自然语言输入并调用API获取数据'
    )
    parser.add_argument(
        'text',
        nargs='*',
        help='要解析的自然语言文本'
    )
    parser.add_argument(
        '--file',
        help='从文件读取输入文本'
    )
    parser.add_argument(
        '--no-call-api',
        action='store_true',
        help='是否只解析参数而不调用API，默认会调用API'
    )
    parser.add_argument(
        '--save-config',
        nargs=2,
        metavar=('PROJECT_ID', 'SIGN'),
        help='保存项目ID和签名到配置文件'
    )
    parser.add_argument(
        '--clear-config',
        action='store_true',
        help='清除配置文件中的内容'
    )
    parser.add_argument(
        '--show-config',
        action='store_true',
        help='显示当前配置文件内容'
    )

    args = parser.parse_args()

    # 处理配置管理命令
    if args.save_config:
        project_id, sign = args.save_config
        if save_config(project_id, sign):
            print('配置已成功保存')
        else:
            print('保存配置失败')
        return 0

    if args.clear_config:
        if clear_config():
            print('配置已成功清除')
        else:
            print('清除配置失败')
        return 0

    if args.show_config:
        print(show_config())
        return 0

    # 读取输入
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            text = f.read()
    elif args.text:
        text = ' '.join(args.text)
    else:
        # 确保从标准输入读取时使用UTF-8编码
        try:
            text = sys.stdin.read().strip()
            # 尝试将输入转换为UTF-8编码
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='ignore')
            else:
                # 如果是Windows系统，可能需要处理GBK编码
                try:
                    # 尝试解码为UTF-8
                    text.encode('utf-8')
                except UnicodeEncodeError:
                    # 如果失败，尝试解码为GBK
                    text = text.encode('latin-1').decode('gbk', errors='ignore')
        except Exception as e:
            text = ''

    if not text:
        print('请提供要解析的自然语言文本')
        return 1

    # 解析参数
    params_json = parse_gsdata_params(text)

    # 如果是错误提示，直接返回
    if not params_json.startswith('{'):
        print(params_json)
        return 1

    # 根据--no-call-api选项决定是否调用API
    if args.no_call_api:
        print(params_json)
        return 0
    else:
        # 默认直接调用API并返回表格格式
        result = call_gsdata_api(params_json)
        print(result)
        return 0


if __name__ == '__main__':
    sys.exit(main())
