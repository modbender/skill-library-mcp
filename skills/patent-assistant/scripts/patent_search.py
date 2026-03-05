#!/usr/bin/env python3
"""
专利检索工具 - 多平台专利检索
支持：Google Patents, Lens.org, 大为Innojoy, 百度学术, Espacenet
"""

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed


# ============== Google Patents ==============
def search_google_patents(query: str, limit: int = 20, country: str = "CN") -> list[dict]:
    """Google Patents 搜索"""
    encoded_query = urllib.parse.quote(f"{query} country:{country}")
    url = f"https://patents.google.com/xhr/query?url=q%3D{encoded_query}&num={limit}&exp="
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
            
        results = []
        if "results" in data and "cluster" in data["results"]:
            for cluster in data["results"]["cluster"]:
                if "result" in cluster:
                    for result in cluster["result"]:
                        patent = result.get("patent", {})
                        results.append({
                            "source": "Google Patents",
                            "patent_number": patent.get("publication_number", ""),
                            "title": patent.get("title", ""),
                            "abstract": patent.get("abstract", "")[:500] if patent.get("abstract") else "",
                            "assignee": patent.get("assignee", ""),
                            "filing_date": patent.get("filing_date", ""),
                            "url": f"https://patents.google.com/patent/{patent.get('publication_number', '')}"
                        })
        return results[:limit]
    except Exception as e:
        print(f"[Google Patents] 搜索失败: {e}", file=sys.stderr)
        return []


# ============== Lens.org ==============
def search_lens(query: str, limit: int = 20) -> list[dict]:
    """Lens.org 搜索（专利+论文）"""
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.lens.org/lens/search/patent/list?q={encoded_query}&n={limit}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode("utf-8")
        
        # 简单解析（Lens 返回 HTML）
        results = []
        # 提取专利信息的正则
        pattern = r'lens\.org/lens/patent/(\w+)'
        matches = re.findall(pattern, html)
        
        for lens_id in matches[:limit]:
            results.append({
                "source": "Lens.org",
                "patent_number": lens_id,
                "title": "[需访问详情页]",
                "abstract": "",
                "url": f"https://www.lens.org/lens/patent/{lens_id}"
            })
        
        if not results:
            results.append({
                "source": "Lens.org",
                "note": "建议直接访问 Lens.org 进行检索",
                "url": f"https://www.lens.org/lens/search/patent/list?q={encoded_query}"
            })
        return results
    except Exception as e:
        print(f"[Lens.org] 搜索失败: {e}", file=sys.stderr)
        return [{
            "source": "Lens.org",
            "note": f"搜索失败: {e}",
            "url": f"https://www.lens.org/lens/search/patent/list?q={encoded_query}"
        }]


# ============== 大为 Innojoy ==============
def search_innojoy(query: str, limit: int = 20) -> list[dict]:
    """大为 Innojoy 专利搜索"""
    encoded_query = urllib.parse.quote(query)
    # Innojoy 简单检索接口
    url = f"http://www.innojoy.com/search/index.html?kw={encoded_query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode("utf-8")
        
        results = []
        # 尝试解析搜索结果
        # Innojoy 的结果需要 JavaScript 渲染，这里返回搜索链接
        results.append({
            "source": "大为Innojoy",
            "note": "Innojoy 需要浏览器访问，已生成搜索链接",
            "url": f"http://www.innojoy.com/search/index.html?kw={encoded_query}",
            "features": ["中国专利为主", "支持AI智能检索", "免费基础版"]
        })
        return results
    except Exception as e:
        print(f"[Innojoy] 搜索失败: {e}", file=sys.stderr)
        return [{
            "source": "大为Innojoy",
            "note": f"搜索失败，请手动访问",
            "url": f"http://www.innojoy.com/search/index.html?kw={encoded_query}"
        }]


# ============== 百度学术 ==============
def search_baidu_xueshu(query: str, limit: int = 20) -> list[dict]:
    """百度学术搜索（论文+专利）"""
    encoded_query = urllib.parse.quote(query)
    url = f"https://xueshu.baidu.com/s?wd={encoded_query}&tn=SE_baiduxueshu_c1gjeupa&ie=utf-8&sc_hit=1"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode("utf-8")
        
        results = []
        # 解析百度学术结果
        # 标题模式
        title_pattern = r'<a[^>]*class="sc_content"[^>]*>([^<]+)</a>'
        titles = re.findall(title_pattern, html)
        
        for title in titles[:limit]:
            results.append({
                "source": "百度学术",
                "title": title.strip(),
                "url": f"https://xueshu.baidu.com/s?wd={encoded_query}"
            })
        
        if not results:
            results.append({
                "source": "百度学术",
                "note": "建议直接访问百度学术进行检索",
                "url": f"https://xueshu.baidu.com/s?wd={encoded_query}",
                "features": ["论文为主", "部分专利", "中文友好"]
            })
        return results
    except Exception as e:
        print(f"[百度学术] 搜索失败: {e}", file=sys.stderr)
        return [{
            "source": "百度学术",
            "note": f"搜索失败，请手动访问",
            "url": f"https://xueshu.baidu.com/s?wd={encoded_query}"
        }]


# ============== Espacenet (欧洲专利局) ==============
def search_espacenet(query: str, limit: int = 20) -> list[dict]:
    """Espacenet 欧洲专利局搜索"""
    encoded_query = urllib.parse.quote(query)
    url = f"https://worldwide.espacenet.com/patent/search?q={encoded_query}"
    
    # Espacenet 有反爬，返回搜索链接
    return [{
        "source": "Espacenet",
        "note": "欧洲专利局数据库，需浏览器访问",
        "url": url,
        "features": ["全球专利", "欧洲专利详细", "支持多语言"]
    }]


# ============== 国知局 CNIPA ==============
def search_cnipa(query: str, limit: int = 20) -> list[dict]:
    """国知局专利检索（需登录）"""
    encoded_query = urllib.parse.quote(query)
    url = f"https://pss-system.cponline.cnipa.gov.cn/conventionalSearch?searchWord={encoded_query}"
    
    return [{
        "source": "国知局CNIPA",
        "note": "国知局官方数据库，需要登录账号",
        "url": url,
        "register_url": "https://pss-system.cponline.cnipa.gov.cn/",
        "features": ["中国专利权威", "法律状态准确", "需注册登录"]
    }]


# ============== 相似度分析 ==============
def analyze_similarity(query: str, patents: list[dict]) -> list[dict]:
    """简单的相似度分析（基于关键词匹配）"""
    keywords = set(query.lower().split())
    
    for patent in patents:
        if "note" in patent:
            continue
        title = patent.get("title", "").lower()
        abstract = patent.get("abstract", "").lower()
        content = f"{title} {abstract}"
        
        matched = sum(1 for kw in keywords if kw in content)
        patent["similarity_score"] = round(matched / len(keywords) * 100, 1) if keywords else 0
    
    return sorted(patents, key=lambda x: x.get("similarity_score", 0), reverse=True)


# ============== 输出格式化 ==============
def format_output(patents: list[dict], format_type: str = "text") -> str:
    """格式化输出"""
    if format_type == "json":
        return json.dumps(patents, ensure_ascii=False, indent=2)
    
    if not patents:
        return "未找到相关专利"
    
    lines = ["## 专利检索结果\n"]
    
    # 按来源分组
    sources = {}
    for p in patents:
        src = p.get("source", "未知")
        if src not in sources:
            sources[src] = []
        sources[src].append(p)
    
    for source, items in sources.items():
        lines.append(f"### 📚 {source}\n")
        
        for i, p in enumerate(items, 1):
            if "note" in p:
                lines.append(f"**提示**: {p['note']}")
                if p.get("url"):
                    lines.append(f"🔗 链接: {p['url']}")
                if p.get("features"):
                    lines.append(f"特点: {', '.join(p['features'])}")
                lines.append("")
                continue
            
            lines.append(f"**{i}. {p.get('title', '无标题')}**")
            if p.get("patent_number"):
                lines.append(f"- 专利号: {p['patent_number']}")
            if p.get("assignee"):
                lines.append(f"- 申请人: {p['assignee']}")
            if p.get("filing_date"):
                lines.append(f"- 申请日: {p['filing_date']}")
            if "similarity_score" in p:
                lines.append(f"- 相似度: {p['similarity_score']}%")
            if p.get("url"):
                lines.append(f"- 链接: {p['url']}")
            if p.get("abstract"):
                lines.append(f"- 摘要: {p['abstract'][:150]}...")
            lines.append("")
    
    return "\n".join(lines)


# ============== 主函数 ==============
def main():
    parser = argparse.ArgumentParser(
        description="多平台专利检索工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
数据源说明:
  google    - Google Patents (全球专利，免费)
  lens      - Lens.org (专利+论文，免费)
  innojoy   - 大为Innojoy (中国专利，免费基础版)
  baidu     - 百度学术 (论文+专利，免费)
  espacenet - 欧洲专利局 (全球专利，免费)
  cnipa     - 国知局 (中国专利，需登录)
  all       - 所有平台

示例:
  python patent_search.py "人工智能 图像识别" -s all
  python patent_search.py "机器学习" -s google -c US -n 30
  python patent_search.py "深度学习" -s google,lens,innojoy -a
        """
    )
    parser.add_argument("query", help="检索关键词")
    parser.add_argument("--limit", "-n", type=int, default=20, help="每个平台返回结果数量")
    parser.add_argument("--country", "-c", default="CN", help="国家代码 (CN/US/EP/JP/KR)")
    parser.add_argument("--source", "-s", default="google",
                        help="数据源，逗号分隔 (google/lens/innojoy/baidu/espacenet/cnipa/all)")
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text",
                        help="输出格式")
    parser.add_argument("--analyze", "-a", action="store_true", help="进行相似度分析")
    parser.add_argument("--parallel", "-p", action="store_true", help="并行检索（更快）")
    
    args = parser.parse_args()
    
    # 解析数据源
    if args.source == "all":
        sources = ["google", "lens", "innojoy", "baidu", "espacenet", "cnipa"]
    else:
        sources = [s.strip().lower() for s in args.source.split(",")]
    
    # 数据源映射
    search_funcs = {
        "google": lambda: search_google_patents(args.query, args.limit, args.country),
        "lens": lambda: search_lens(args.query, args.limit),
        "innojoy": lambda: search_innojoy(args.query, args.limit),
        "baidu": lambda: search_baidu_xueshu(args.query, args.limit),
        "espacenet": lambda: search_espacenet(args.query, args.limit),
        "cnipa": lambda: search_cnipa(args.query, args.limit),
    }
    
    all_results = []
    
    if args.parallel and len(sources) > 1:
        # 并行检索
        print(f"并行检索 {len(sources)} 个平台...", file=sys.stderr)
        with ThreadPoolExecutor(max_workers=len(sources)) as executor:
            futures = {}
            for src in sources:
                if src in search_funcs:
                    futures[executor.submit(search_funcs[src])] = src
            
            for future in as_completed(futures):
                src = futures[future]
                try:
                    results = future.result()
                    all_results.extend(results)
                    print(f"[{src}] 完成，获取 {len(results)} 条结果", file=sys.stderr)
                except Exception as e:
                    print(f"[{src}] 失败: {e}", file=sys.stderr)
    else:
        # 串行检索
        for src in sources:
            if src in search_funcs:
                print(f"正在搜索 {src}: {args.query}", file=sys.stderr)
                results = search_funcs[src]()
                all_results.extend(results)
    
    # 相似度分析
    if args.analyze and all_results:
        all_results = analyze_similarity(args.query, all_results)
    
    print(format_output(all_results, args.format))


if __name__ == "__main__":
    main()
