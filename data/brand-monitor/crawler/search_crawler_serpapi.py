#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
品牌监控搜索爬虫 - SerpAPI 版本
使用 SerpAPI 进行可靠的搜索，支持 Google、百度等多个搜索引擎
"""

import json
import sys
import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from urllib.parse import quote

# 设置标准输出编码为 UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class SerpAPISearcher:
    """SerpAPI 搜索器"""
    
    def __init__(self, api_key: Optional[str] = None, engine: str = 'google'):
        """
        初始化 SerpAPI 搜索器
        
        Args:
            api_key: SerpAPI API Key（如果不提供，从环境变量读取）
            engine: 搜索引擎（baidu, bing， google）
        """
        self.api_key = api_key or os.environ.get('SERPAPI_KEY')
        if not self.api_key:
            raise ValueError("需要提供 SERPAPI_KEY 环境变量或 api_key 参数")
        
        self.engine = engine
        self.base_url = "https://serpapi.com/search"
        
    def _detect_platform(self, url: str) -> str:
        """根据URL检测平台"""
        url_lower = url.lower()
        
        if 'weibo.com' in url_lower or 'weibo.cn' in url_lower:
            return 'weibo'
        elif 'xiaohongshu.com' in url_lower or 'xhslink.com' in url_lower:
            return 'xiaohongshu'
        elif 'zhihu.com' in url_lower:
            return 'zhihu'
        elif 'autohome.com' in url_lower:
            return 'autohome'
        elif 'dongchedi.com' in url_lower:
            return 'dongchedi'
        elif 'yiche.com' in url_lower or 'bitauto.com' in url_lower:
            return 'yiche'
        elif 'tieba.baidu.com' in url_lower:
            return 'tieba'
        elif 'douyin.com' in url_lower:
            return 'douyin'
        elif 'kuaishou.com' in url_lower:
            return 'kuaishou'
        else:
            return 'other'
    
    def search(self, query: str, num_results: int = 20, **kwargs) -> List[Dict]:
        """
        执行搜索
        
        Args:
            query: 搜索查询
            num_results: 结果数量
            **kwargs: 其他参数（如 location, hl 等）
        
        Returns:
            搜索结果列表
        """
        params = {
            'api_key': self.api_key,
            'engine': self.engine,
            'q': query,
            'num': num_results,
        }
        
        # 添加额外参数
        params.update(kwargs)
        
        # 如果是百度搜索，使用中文
        if self.engine == 'baidu':
            params['hl'] = 'zh-cn'
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # 调试：打印原始响应（仅在调试模式下）
            if os.environ.get('DEBUG'):
                print(f"\n=== 原始 SerpAPI 响应 ===", file=sys.stderr)
                print(json.dumps(data, ensure_ascii=False, indent=2)[:2000], file=sys.stderr)
                print("=" * 50, file=sys.stderr)
            
            return self._parse_results(data)
            
        except requests.exceptions.RequestException as e:
            print(f"SerpAPI 请求失败: {e}", file=sys.stderr)
            return []
        except Exception as e:
            print(f"解析结果失败: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            return []
    
    def _extract_numbers_from_text(self, text: str) -> Dict[str, int]:
        """从文本中提取数字信息（点赞、评论、转发等）"""
        import re
        
        numbers = {
            'likes': 0,
            'comments': 0,
            'shares': 0,
            'followers': 0
        }
        
        # 匹配各种数字格式
        # 例如: "58601 31381 ñ626294" (收藏 转发 评论)
        # "744207粉丝" "74.4万粉丝"
        
        # 粉丝数
        followers_match = re.search(r'(\d+(?:\.\d+)?)[万千]?粉丝', text)
        if followers_match:
            num_str = followers_match.group(1)
            if '万' in text[followers_match.start():followers_match.end()]:
                numbers['followers'] = int(float(num_str) * 10000)
            elif '千' in text[followers_match.start():followers_match.end()]:
                numbers['followers'] = int(float(num_str) * 1000)
            else:
                numbers['followers'] = int(num_str)
        
        # 点赞/收藏 (通常是第一个数字)
        likes_match = re.search(r'û收藏\s*(\d+)', text)
        if likes_match:
            numbers['likes'] = int(likes_match.group(1))
        
        # 转发 (通常是第二个数字)
        shares_match = re.search(r'(\d+)\s+(\d+)\s+ñ(\d+)', text)
        if shares_match:
            numbers['shares'] = int(shares_match.group(2))
            numbers['comments'] = int(shares_match.group(3))
        
        return numbers
    
    def _extract_publish_time(self, text: str) -> str:
        """从文本中提取发布时间"""
        import re
        
        # 匹配日期格式: "2月18日 23:52", "2025-9-26 10:30"
        time_patterns = [
            r'(\d{1,2}月\d{1,2}日\s+\d{1,2}:\d{2})',
            r'(\d{4}-\d{1,2}-\d{1,2}\s+\d{1,2}:\d{2})',
            r'(\d{1,2}小时前)',
            r'(\d{1,2}分钟前)',
            r'(昨天\s+\d{1,2}:\d{2})',
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return ''
    
    def _extract_author(self, text: str, url: str) -> tuple:
        """从文本和URL中提取作者信息"""
        import re
        
        author = ''
        author_id = ''
        verified = False
        
        # 从标题或内容中提取作者
        # 例如: "理想汽车的微博", "@理想汽车", "李想的微博"
        author_match = re.search(r'(@?[\u4e00-\u9fa5a-zA-Z0-9_-]+)(?:的微博|成为)', text)
        if author_match:
            author = author_match.group(1).replace('@', '')
        
        # 从URL中提取用户ID
        # 例如: weibo.com/6001272153, weibo.com/lixiangzhizao
        url_match = re.search(r'weibo\.com/(?:u/)?([a-zA-Z0-9_]+)', url)
        if url_match:
            author_id = url_match.group(1)
        
        # 检测认证标识
        if '官方' in text or '认证' in text or 'CEO' in text:
            verified = True
        
        return author, author_id, verified
    
    def _parse_results(self, data: Dict) -> List[Dict]:
        """解析搜索结果"""
        results = []
        
        # 获取有机搜索结果
        organic_results = data.get('organic_results', [])
        
        for item in organic_results:
            url = item.get('link', '')
            platform = self._detect_platform(url)
            
            title = item.get('title', '')
            snippet = item.get('snippet', '')
            full_text = f"{title} {snippet}"
            
            # 提取数字信息
            numbers = self._extract_numbers_from_text(full_text)
            
            # 提取发布时间
            publish_time = self._extract_publish_time(full_text) or item.get('date', '')
            
            # 提取作者信息
            author, author_id, verified = self._extract_author(full_text, url)
            
            result = {
                'platform': platform,
                'title': title,
                'content': snippet,
                'url': url,
                'source': f'serpapi_{self.engine}',
                'publish_time': publish_time,
                'author': author,
                'author_id': author_id,
                'followers': numbers['followers'],
                'verified': verified,
                'likes': numbers['likes'],
                'comments': numbers['comments'],
                'shares': numbers['shares'],
            }
            results.append(result)
        
        return results


class PlatformSearcher:
    """多平台搜索管理器"""
    
    def __init__(self, api_key: Optional[str] = None, engine: str = 'google', use_mock: bool = False, 
                 exclude_official: bool = True, brand_keywords: List[str] = None):
        """
        初始化搜索器
        
        Args:
            api_key: SerpAPI API Key
            engine: 搜索引擎（google, baidu, bing）
            use_mock: 是否使用模拟数据
            exclude_official: 是否排除品牌官方账号
            brand_keywords: 品牌关键词列表，用于识别官方账号
        """
        self.use_mock = use_mock
        self.exclude_official = exclude_official
        self.brand_keywords = brand_keywords or []
        
        if not use_mock:
            self.searcher = SerpAPISearcher(api_key, engine)
        
        self.platform_sites = {
            'weibo': 'site:weibo.com OR site:weibo.cn',
            'xiaohongshu': 'site:xiaohongshu.com',
            'zhihu': 'site:zhihu.com',
            'autohome': 'site:autohome.com.cn',
            'dongchedi': 'site:dongchedi.com',
            'yiche': 'site:yiche.com OR site:bitauto.com',
            'tieba': 'site:tieba.baidu.com',
            'douyin': 'site:douyin.com',
            'kuaishou': 'site:kuaishou.com',
        }
        
        self.platform_names = {
            'weibo': '微博',
            'xiaohongshu': '小红书',
            'zhihu': '知乎',
            'autohome': '汽车之家',
            'dongchedi': '懂车帝',
            'yiche': '易车网',
            'tieba': '百度贴吧',
            'douyin': '抖音',
            'kuaishou': '快手',
        }
        
        # 常见官方账号关键词
        self.official_keywords = [
            '官方', '法务', '客服', '服务', 'official',
            '公司', '集团', '总部', '品牌'
        ]
    
    def _is_official_account(self, author: str, url: str, content: str) -> bool:
        """
        判断是否为品牌官方账号
        
        Args:
            author: 作者名称
            url: 内容URL
            content: 内容文本
        
        Returns:
            True 如果是官方账号
        """
        # 检查作者名称
        author_lower = author.lower()
        
        for keyword in self.brand_keywords:
            keyword_lower = keyword.lower()
            
            # 如果作者名包含品牌名
            if keyword_lower in author_lower or keyword in author:
                # 检查是否包含官方关键词
                for official_kw in self.official_keywords:
                    if official_kw in author or official_kw in author_lower:
                        return True
                
                # 如果作者名就是品牌名（完全匹配或高度相似）
                if author == keyword or author.replace(' ', '').replace('汽车', '') == keyword.replace(' ', '').replace('汽车', ''):
                    return True
        
        # 检查URL（官方域名）
        for keyword in self.brand_keywords:
            keyword_pinyin = self._to_pinyin(keyword)
            if keyword_pinyin and keyword_pinyin in url.lower():
                # 检查是否是官方域名（不是社交媒体平台）
                if keyword_pinyin + '.com' in url or keyword_pinyin + '.cn' in url:
                    return True
        
        return False
    
    def _to_pinyin(self, text: str) -> str:
        """简单的品牌名转拼音（用于URL匹配）"""
        # 常见品牌拼音映射
        pinyin_map = {
            '理想汽车': 'lixiang',
            '理想': 'lixiang',
            '蔚来': 'nio',
            '小鹏': 'xiaopeng',
            '问界': 'aito',
            '比亚迪': 'byd',
        }
        return pinyin_map.get(text, '')
    
    def _generate_mock_data(self, keyword: str, platform: str, max_results: int) -> List[Dict]:
        """生成模拟数据"""
        results = []
        platform_name = self.platform_names.get(platform, platform)
        
        # 生成多样化的模拟数据，包括官方和非官方
        mock_authors = [
            {'name': f'{platform_name}用户{i+1}', 'is_official': False, 'followers': 5000 + i * 1000},
            {'name': f'汽车评测师{i+1}', 'is_official': False, 'followers': 50000 + i * 10000},
            {'name': f'{keyword}', 'is_official': True, 'followers': 700000},  # 官方账号
        ]
        
        for i in range(min(3, max_results)):
            author_info = mock_authors[i % len(mock_authors)]
            
            # 如果排除官方账号，跳过官方数据
            if self.exclude_official and author_info['is_official']:
                continue
            
            result = {
                'platform': platform,
                'title': f'{platform_name}上关于{keyword}的讨论 #{i+1}',
                'content': f'这是一条来自{platform_name}的关于{keyword}的模拟内容。包含用户的真实体验和评价。',
                'author': author_info['name'],
                'author_id': f'{platform}_user_{i+1}',
                'followers': author_info['followers'],
                'verified': author_info['is_official'],
                'url': f'https://example.com/{platform}/post/{i+1}',
                'publish_time': (datetime.now() - timedelta(hours=i*2)).isoformat(),
                'likes': 100 * (i + 1),
                'comments': 20 * (i + 1),
                'shares': 10 * (i + 1),
                'is_official': author_info['is_official'],
            }
            results.append(result)
        
        return results
    
    def search_platform(self, keyword: str, platform: str, max_results: int = 20, hours: int = 24) -> List[Dict]:
        """
        在指定平台搜索
        
        Args:
            keyword: 搜索关键词
            platform: 平台名称
            max_results: 最大结果数
            hours: 时间范围（小时）
        
        Returns:
            搜索结果列表
        """
        if self.use_mock:
            return self._generate_mock_data(keyword, platform, max_results)
        
        # 构建搜索查询 - 不使用 site: 过滤器，而是在关键词中包含平台名称
        platform_name = self.platform_names.get(platform, platform)
        
        # 对于中文平台，直接搜索 "关键词 + 平台名称"，让搜索引擎自然匹配
        query = f'{keyword} {platform_name}'
        
        # 添加时间过滤（如果支持）
        search_params = {}
        if hours <= 24:
            # Google/Baidu 支持时间过滤
            search_params['tbs'] = f'qdr:d'  # 最近一天
        elif hours <= 168:  # 7天
            search_params['tbs'] = f'qdr:w'  # 最近一周
        
        # 执行搜索
        results = self.searcher.search(query, max_results, **search_params)
        
        # 过滤结果
        filtered_results = []
        official_count = 0
        
        for r in results:
            detected_platform = self.searcher._detect_platform(r['url'])
            
            # 只保留目标平台
            if platform != 'all' and detected_platform != platform:
                continue
            
            r['platform'] = platform  # 确保平台标记正确
            
            # 检查是否为官方账号
            is_official = self._is_official_account(r['author'], r['url'], r['content'])
            r['is_official'] = is_official
            
            if is_official:
                official_count += 1
                if self.exclude_official:
                    continue  # 排除官方账号
            
            filtered_results.append(r)
        
        # 输出过滤统计
        if official_count > 0:
            print(f"  ℹ️  过滤了 {official_count} 条官方账号内容", file=sys.stderr)
        
        return filtered_results
    
    def search_all(self, keyword: str, platforms: List[str], max_results_per_platform: int = 20, hours: int = 24) -> Dict[str, List[Dict]]:
        """
        在所有指定平台搜索
        
        Args:
            keyword: 搜索关键词
            platforms: 平台列表
            max_results_per_platform: 每个平台的最大结果数
            hours: 时间范围（小时）
        
        Returns:
            按平台分组的搜索结果
        """
        results = {}
        
        for platform in platforms:
            print(f"正在搜索 {platform}...", file=sys.stderr)
            
            try:
                platform_results = self.search_platform(keyword, platform, max_results_per_platform, hours)
                results[platform] = platform_results
                print(f"{platform} 搜索完成，找到 {len(platform_results)} 条结果", file=sys.stderr)
                
                # 避免请求过快（SerpAPI 有速率限制）
                if not self.use_mock and platform != platforms[-1]:
                    time.sleep(1)
                    
            except Exception as e:
                print(f"{platform} 搜索出错: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc(file=sys.stderr)
                results[platform] = []
        
        return results


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python search_crawler_serpapi.py <关键词> [平台列表] [每平台最大结果数] [时间范围(小时)] [--mock] [--include-official]")
        print("")
        print("示例:")
        print("  # 使用 SerpAPI 搜索（默认排除官方账号）")
        print("  python search_crawler_serpapi.py '理想汽车' 'weibo,xiaohongshu,zhihu' 10 24")
        print("")
        print("  # 包含官方账号")
        print("  python search_crawler_serpapi.py '理想汽车' 'weibo,zhihu' 10 24 --include-official")
        print("")
        print("  # 使用模拟数据")
        print("  python search_crawler_serpapi.py '理想汽车' 'weibo,zhihu' 10 24 --mock")
        print("")
        print("支持的平台:")
        print("  - weibo: 微博")
        print("  - xiaohongshu: 小红书")
        print("  - zhihu: 知乎")
        print("  - autohome: 汽车之家")
        print("  - dongchedi: 懂车帝")
        print("  - yiche: 易车网")
        print("  - tieba: 百度贴吧")
        print("  - douyin: 抖音")
        print("  - kuaishou: 快手")
        print("")
        print("环境变量:")
        print("  SERPAPI_KEY: SerpAPI API Key（必需，除非使用 --mock）")
        print("  SERPAPI_ENGINE: 搜索引擎（可选，默认: baidu，可选: google, bing）")
        print("")
        print("选项:")
        print("  --mock: 使用模拟数据，不消耗 API 配额")
        print("  --include-official: 包含品牌官方账号（默认排除）")
        print("")
        print("舆情监控说明:")
        print("  默认排除品牌官方账号，只关注第三方自媒体和用户的真实声音")
        print("  官方账号识别规则：作者名包含品牌名 + '官方'/'法务'/'客服'等关键词")
        print("")
        print("获取 API Key:")
        print("  访问 https://serpapi.com/ 注册并获取免费 API Key")
        print("  免费额度: 100 次搜索/月")
        sys.exit(1)
    
    keyword = sys.argv[1]
    platforms = sys.argv[2].split(',') if len(sys.argv) > 2 else ['weibo', 'xiaohongshu', 'zhihu']
    max_results = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] not in ['--mock', '--include-official'] else 10
    hours = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4] not in ['--mock', '--include-official'] else 24
    use_mock = '--mock' in sys.argv
    include_official = '--include-official' in sys.argv
    exclude_official = not include_official
    
    # 读取配置
    api_key = os.environ.get('SERPAPI_KEY')
    engine = os.environ.get('SERPAPI_ENGINE', 'baidu')
    
    # 检查 API Key
    if not use_mock and not api_key:
        print("❌ 错误: 未设置 SERPAPI_KEY 环境变量", file=sys.stderr)
        print("", file=sys.stderr)
        print("请设置环境变量:", file=sys.stderr)
        print("  export SERPAPI_KEY='your_api_key'", file=sys.stderr)
        print("", file=sys.stderr)
        print("或使用 --mock 参数进行测试:", file=sys.stderr)
        print(f"  python search_crawler_serpapi.py '{keyword}' '{','.join(platforms)}' {max_results} {hours} --mock", file=sys.stderr)
        sys.exit(1)
    
    # 显示配置
    if use_mock:
        print("⚠️  使用模拟数据模式", file=sys.stderr)
    else:
        print(f"✓ 使用 SerpAPI ({engine})", file=sys.stderr)
    
    print(f"搜索关键词: {keyword}", file=sys.stderr)
    print(f"搜索平台: {', '.join(platforms)}", file=sys.stderr)
    print(f"每平台最大结果: {max_results}", file=sys.stderr)
    print(f"时间范围: {hours} 小时", file=sys.stderr)
    print(f"官方账号: {'包含' if include_official else '排除'}", file=sys.stderr)
    print("", file=sys.stderr)
    
    # 创建搜索器
    try:
        # 从关键词中提取品牌名（用于识别官方账号）
        brand_keywords = [keyword]
        
        searcher = PlatformSearcher(
            api_key=api_key, 
            engine=engine, 
            use_mock=use_mock,
            exclude_official=exclude_official,
            brand_keywords=brand_keywords
        )
        results = searcher.search_all(keyword, platforms, max_results, hours)
        
        # 统计总结果数
        total_results = sum(len(r) for r in results.values())
        print(f"\n✓ 搜索完成！共找到 {total_results} 条结果", file=sys.stderr)
        
        # 显示配额信息（如果不是 mock 模式）
        if not use_mock:
            print(f"", file=sys.stderr)
            print(f"💡 提示: 本次搜索消耗了 {len(platforms)} 次 API 调用", file=sys.stderr)
            print(f"   SerpAPI 免费额度: 100 次/月", file=sys.stderr)
        
        # 输出JSON结果
        print(json.dumps(results, ensure_ascii=False, indent=2))
        
    except ValueError as e:
        print(f"❌ 配置错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 执行失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
