#!/usr/bin/env python3
"""
搜索中国历史政治斗争事件的主流与非主流观点。

用法:
    python search_views.py <事件名称> [--lang zh|en|both] [--max-results 10]

示例:
    python search_views.py "玄武门之变"
    python search_views.py "王莽篡汉" --lang both
    python search_views.py "安史之乱" --max-results 15

环境变量:
    TAVILY_API_KEY - Tavily API 密钥（必须）

输出:
    结构化 JSON，包含主流观点、非主流观点（民间论坛 + 海外学者）的摘要。
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass, field, asdict

try:
    from tavily import TavilyClient
except ImportError:
    print("错误: 请先安装 tavily-python\n  pip install tavily-python", file=sys.stderr)
    sys.exit(1)


@dataclass
class ViewResult:
    title: str
    url: str
    snippet: str
    source_type: str  # mainstream / folk / overseas


@dataclass
class SearchReport:
    event: str
    mainstream: list[ViewResult] = field(default_factory=list)
    folk: list[ViewResult] = field(default_factory=list)
    overseas: list[ViewResult] = field(default_factory=list)


# ---------------------------------------------------------------------------
# 搜索策略配置
# ---------------------------------------------------------------------------

MAINSTREAM_QUERIES_ZH = [
    "{event} 历史评价",
    "{event} 学术研究 论文",
    "{event} 正史记载 分析",
]

FOLK_QUERIES_ZH = [
    "{event} 知乎 争议",
    "{event} 贴吧 讨论 真相",
    "{event} 民间 另一种说法",
    "{event} 阴谋论 野史",
]

OVERSEAS_QUERIES_ZH = [
    "{event} 海外学者 观点",
    "{event} 翻案 重新评价",
    "{event} 不同解读 新视角",
]

MAINSTREAM_QUERIES_EN = [
    "{event_en} Chinese history scholarly analysis",
    "{event_en} academic perspective historical evaluation",
]

OVERSEAS_QUERIES_EN = [
    "{event_en} revisionist interpretation",
    "{event_en} alternative historical view controversy",
    "{event_en} Western sinology perspective",
]

# 事件名称中英对照（常见事件）
EVENT_TRANSLATIONS = {
    "玄武门之变": "Xuanwu Gate Incident",
    "安史之乱": "An Lushan Rebellion",
    "靖难之役": "Jingnan Campaign",
    "王莽篡汉": "Wang Mang usurpation",
    "七国之乱": "Rebellion of the Seven States",
    "巫蛊之祸": "Witchcraft Incident Han dynasty",
    "陈桥兵变": "Chenqiao Mutiny",
    "土木堡之变": "Tumu Crisis",
    "甘露之变": "Sweet Dew Incident Tang",
    "八王之乱": "War of the Eight Princes",
    "高平陵之变": "Gaoping Tombs Incident",
    "党锢之祸": "Disasters of Partisan Prohibitions",
    "武周革命": "Wu Zetian Zhou dynasty",
    "牛李党争": "Niu-Li Factional Strife",
    "九子夺嫡": "Nine Princes struggle for succession Kangxi",
    "戊戌变法": "Hundred Days Reform",
    "靖康之变": "Jingkang Incident",
    "沙丘之变": "Shaqiu Incident Qin dynasty",
    "大礼议": "Great Rites Controversy Ming",
    "东林党争": "Donglin Movement Ming dynasty",
    "文字狱": "Literary Inquisition Qing dynasty",
    "鳌拜专权": "Oboi regency Kangxi",
    "三家分晋": "Partition of Jin",
    "商鞅变法": "Shang Yang reforms",
    "王安石变法": "Wang Anshi reforms",
    "庆元党禁": "Qingyuan Partisan Ban",
}

# 来源域名分类
FOLK_DOMAINS = [
    "zhihu.com", "tieba.baidu.com", "tianya.cn", "douban.com",
    "bilibili.com", "weibo.com", "toutiao.com", "sohu.com",
]

MAINSTREAM_DOMAINS = [
    "cnki.net", "cssn.cn", "guoxue.com", "cass.cn",
    "wikipedia.org", "baike.baidu.com", "britannica.com",
    "jstor.org", "academia.edu",
]


def classify_source(url: str) -> str:
    """根据 URL 域名判断来源类型。"""
    url_lower = url.lower()
    for domain in FOLK_DOMAINS:
        if domain in url_lower:
            return "folk"
    for domain in MAINSTREAM_DOMAINS:
        if domain in url_lower:
            return "mainstream"
    # 英文域名大概率是海外来源
    if any(tld in url_lower for tld in [".edu", ".ac.uk", ".org"]):
        return "overseas"
    return "mainstream"


def search_tavily(client: TavilyClient, query: str, max_results: int = 5) -> list[dict]:
    """执行单次 Tavily 搜索。"""
    try:
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced",
            include_answer=False,
        )
        return response.get("results", [])
    except Exception as e:
        print(f"  搜索出错 [{query[:30]}...]: {e}", file=sys.stderr)
        return []


def get_event_english(event: str) -> str:
    """获取事件的英文名称。"""
    if event in EVENT_TRANSLATIONS:
        return EVENT_TRANSLATIONS[event]
    # 没有预设翻译就用拼音+关键词
    return f"{event} Chinese history"


def run_search(event: str, lang: str, max_results: int) -> SearchReport:
    """执行多维度搜索并汇总结果。"""
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        print("错误: 请设置环境变量 TAVILY_API_KEY", file=sys.stderr)
        sys.exit(1)

    client = TavilyClient(api_key=api_key)
    report = SearchReport(event=event)
    seen_urls = set()

    def add_results(raw_results: list[dict], default_type: str):
        for r in raw_results:
            url = r.get("url", "")
            if url in seen_urls:
                continue
            seen_urls.add(url)
            source_type = classify_source(url)
            # 如果分类与搜索意图不符，优先用搜索意图
            if default_type == "folk" and source_type == "mainstream":
                source_type = "folk"
            elif default_type == "overseas" and source_type == "mainstream":
                source_type = "overseas"

            vr = ViewResult(
                title=r.get("title", ""),
                url=url,
                snippet=r.get("content", "")[:500],
                source_type=source_type,
            )
            if vr.source_type == "folk":
                report.folk.append(vr)
            elif vr.source_type == "overseas":
                report.overseas.append(vr)
            else:
                report.mainstream.append(vr)

    per_query = max(2, max_results // 5)

    # --- 中文搜索 ---
    if lang in ("zh", "both"):
        print(f"🔍 搜索主流观点（中文）...", file=sys.stderr)
        for q in MAINSTREAM_QUERIES_ZH:
            results = search_tavily(client, q.format(event=event), per_query)
            add_results(results, "mainstream")

        print(f"🔍 搜索民间讨论（中文）...", file=sys.stderr)
        for q in FOLK_QUERIES_ZH:
            results = search_tavily(client, q.format(event=event), per_query)
            add_results(results, "folk")

        print(f"🔍 搜索非主流/翻案观点（中文）...", file=sys.stderr)
        for q in OVERSEAS_QUERIES_ZH:
            results = search_tavily(client, q.format(event=event), per_query)
            add_results(results, "overseas")

    # --- 英文搜索 ---
    if lang in ("en", "both"):
        event_en = get_event_english(event)
        print(f"🔍 Searching mainstream views (English)...", file=sys.stderr)
        for q in MAINSTREAM_QUERIES_EN:
            results = search_tavily(client, q.format(event_en=event_en), per_query)
            add_results(results, "mainstream")

        print(f"🔍 Searching alternative views (English)...", file=sys.stderr)
        for q in OVERSEAS_QUERIES_EN:
            results = search_tavily(client, q.format(event_en=event_en), per_query)
            add_results(results, "overseas")

    return report


def format_markdown(report: SearchReport) -> str:
    """将搜索结果格式化为 Markdown。"""
    lines = []
    lines.append(f"# 「{report.event}」多元观点搜索报告\n")

    def section(title: str, items: list[ViewResult]):
        lines.append(f"## {title}（共 {len(items)} 条）\n")
        if not items:
            lines.append("_暂无搜索结果_\n")
            return
        for i, v in enumerate(items, 1):
            lines.append(f"### {i}. {v.title}\n")
            lines.append(f"- **来源**: [{v.url}]({v.url})")
            lines.append(f"- **摘要**: {v.snippet}\n")

    section("📚 主流/学术观点", report.mainstream)
    section("💬 民间讨论与争议", report.folk)
    section("🌏 海外学者/非主流解读", report.overseas)

    lines.append("---")
    lines.append(f"_共搜索到 {len(report.mainstream) + len(report.folk) + len(report.overseas)} 条不重复结果_")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="搜索中国历史政治斗争事件的主流与非主流观点",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python search_views.py "玄武门之变"
  python search_views.py "王莽篡汉" --lang both --format markdown
  python search_views.py "安史之乱" --max-results 15 --format json
        """,
    )
    parser.add_argument("event", help="历史政治斗争事件名称（中文）")
    parser.add_argument(
        "--lang",
        choices=["zh", "en", "both"],
        default="both",
        help="搜索语言: zh=仅中文, en=仅英文, both=中英双语（默认）",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="每个类别的最大结果数（默认 10）",
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="markdown",
        help="输出格式: json 或 markdown（默认）",
    )

    args = parser.parse_args()

    report = run_search(args.event, args.lang, args.max_results)

    if args.format == "json":
        output = json.dumps(asdict(report), ensure_ascii=False, indent=2)
        print(output)
    else:
        print(format_markdown(report))


if __name__ == "__main__":
    main()
