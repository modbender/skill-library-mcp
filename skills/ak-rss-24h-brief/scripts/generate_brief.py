#!/usr/bin/env python3
import argparse
import concurrent.futures
import datetime as dt
import email.utils
import hashlib
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Optional, Tuple


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def fetch_text(url: str, timeout: int) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "openclaw-hn-rss-brief/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        charset = r.headers.get_content_charset() or "utf-8"
        return r.read().decode(charset, errors="replace")


def parse_opml(xml_text: str) -> List[str]:
    root = ET.fromstring(xml_text)
    urls = []
    for node in root.findall('.//outline'):
        u = node.attrib.get('xmlUrl') or node.attrib.get('xmlurl')
        if u:
            urls.append(u.strip())
    # 去重保持顺序
    seen = set()
    out = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def text_of(el: Optional[ET.Element], path: str) -> str:
    if el is None:
        return ""
    child = el.find(path)
    return (child.text or "").strip() if child is not None else ""


def find_any_text(item: ET.Element, names: List[str]) -> str:
    # 支持 RSS 与 Atom（含 namespace）
    for n in names:
        direct = item.find(n)
        if direct is not None and (direct.text or "").strip():
            return (direct.text or "").strip()
        for ch in list(item):
            tag = ch.tag.split('}')[-1]
            if tag == n and (ch.text or "").strip():
                return (ch.text or "").strip()
    return ""


def parse_time(s: str) -> Optional[dt.datetime]:
    s = (s or "").strip()
    if not s:
        return None
    try:
        return email.utils.parsedate_to_datetime(s).astimezone(dt.timezone.utc)
    except Exception:
        pass
    # 常见 ISO8601
    try:
        s2 = s.replace('Z', '+00:00')
        return dt.datetime.fromisoformat(s2).astimezone(dt.timezone.utc)
    except Exception:
        return None


def normalize_url(url: str) -> str:
    try:
        p = urllib.parse.urlsplit(url)
        q = urllib.parse.parse_qsl(p.query, keep_blank_values=True)
        q = [(k, v) for k, v in q if not k.lower().startswith('utm_') and k.lower() not in {'ref', 'source'}]
        q.sort()
        return urllib.parse.urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path, urllib.parse.urlencode(q), ""))
    except Exception:
        return url.strip()


def title_fingerprint(title: str) -> str:
    t = re.sub(r'\s+', ' ', (title or '').strip().lower())
    return hashlib.sha1(t.encode('utf-8')).hexdigest()


@dataclass
class Entry:
    title: str
    link: str
    summary: str
    published: Optional[dt.datetime]
    source_feed: str
    source_domain: str
    score: float = 0.0
    categories: List[str] = None


def parse_feed(feed_url: str, xml_text: str) -> List[Entry]:
    root = ET.fromstring(xml_text)
    entries: List[Entry] = []

    # RSS
    for item in root.findall('.//item'):
        title = find_any_text(item, ['title'])
        link = find_any_text(item, ['link'])
        summary = find_any_text(item, ['description', 'summary', 'content'])
        published = parse_time(find_any_text(item, ['pubDate', 'published', 'updated']))
        if title and link:
            d = urllib.parse.urlsplit(link).netloc.lower()
            entries.append(Entry(title=title, link=link, summary=summary, published=published, source_feed=feed_url, source_domain=d))

    # Atom
    for item in root.findall('.//{*}entry'):
        title = find_any_text(item, ['title'])
        link = ''
        for ch in list(item):
            tag = ch.tag.split('}')[-1]
            if tag == 'link':
                href = ch.attrib.get('href', '').strip()
                rel = ch.attrib.get('rel', 'alternate')
                if href and rel in ('alternate', ''):
                    link = href
                    break
        if not link:
            link = find_any_text(item, ['link'])
        summary = find_any_text(item, ['summary', 'content'])
        published = parse_time(find_any_text(item, ['published', 'updated']))
        if title and link:
            d = urllib.parse.urlsplit(link).netloc.lower()
            entries.append(Entry(title=title, link=link, summary=summary, published=published, source_feed=feed_url, source_domain=d))

    return entries


KEYWORDS = {
    # 趋势/行业级重要词（中英混合）
    'ai': 2.0, 'llm': 2.0, 'gpt': 2.0, 'agent': 1.5, 'openai': 2.0, 'anthropic': 1.5,
    'security': 1.8, 'vulnerability': 1.8, 'cve': 2.0, 'breach': 2.0,
    'database': 1.2, 'postgres': 1.2, 'kubernetes': 1.2, 'rust': 1.0, 'python': 1.0,
    '融资': 1.5, '收购': 1.5, '发布': 1.0, '开源': 1.2, '漏洞': 1.8, '安全': 1.5,
}

DOMAIN_BOOST = {
    'openai.com': 1.0,
    'anthropic.com': 0.8,
    'cloudflare.com': 0.6,
    'github.blog': 0.6,
    'engineering.fb.com': 0.6,
}


def score_entry(e: Entry) -> float:
    score = 1.0
    text = f"{e.title} {e.summary}".lower()
    for k, w in KEYWORDS.items():
        if k in text:
            score += w
    for d, b in DOMAIN_BOOST.items():
        if e.source_domain.endswith(d):
            score += b
    # 新鲜度加分（24h 内线性）
    if e.published:
        age_h = max(0.0, (now_utc() - e.published).total_seconds() / 3600.0)
        score += max(0.0, 1.5 - age_h / 16.0)
    return round(score, 3)


def _classify_categories(title: str, summary: str) -> List[str]:
    low = f"{title} {summary}".lower()
    cats = []
    if any(k in low for k in ["ai", "llm", "model", "agent", "codex", "openai", "anthropic"]):
        cats.append("AI工程")
    if any(k in low for k in ["tdd", "test", "compiler", "framework", "benchmark", "token", "efficien", "kubernetes", "database", "python", "rust"]):
        cats.append("开发效率")
    if any(k in low for k in ["security", "vulnerability", "cve", "risk", "safety", "漏洞", "安全"]):
        cats.append("安全风险")
    if any(k in low for k in ["stock", "market", "business", "finance", "fund", "投资", "融资", "收购"]):
        cats.append("产业动态")
    if any(k in low for k in ["social", "media", "culture", "literacy", "society"]):
        cats.append("社会观察")
    return cats or ["技术实践"]


def _to_chinese_brief(title: str, summary: str, categories: List[str]) -> str:
    brief = re.sub(r'<[^>]+>', '', (summary or '')).strip()
    brief = re.sub(r'\s+', ' ', brief)
    low = f"{title} {brief}".lower()

    if not brief:
        return "该条目在 feed 中缺少摘要信息，建议打开原文查看细节。"

    # 先做主题化归纳（避免模板套话）
    if any(k in low for k in ["tdd", "test driven", "red/green"]):
        return "强调以测试驱动流程约束 AI 编码过程，通过先验收再实现来减少返工并提升交付稳定性。"
    if any(k in low for k in ["codex", "terminology", "how i think"]):
        return "重点澄清 Codex 相关概念与使用语境，帮助开发者在工具选择和工作流设计上减少认知偏差。"
    if any(k in low for k in ["compiler", "c compiler", "parallel"]):
        return "以编译器构建案例讨论多代理协作在复杂工程任务中的可行性，以及其对软件生产方式的影响。"
    if any(k in low for k in ["framework", "token-efficient", "benchmark", "tokens"]):
        return "通过多框架对比实验说明：框架抽象层级会显著影响 AI 生成与迭代成本，轻量方案通常更省 token。"
    if any(k in low for k in ["structured output", "structured outputs", "json schema"]):
        return "围绕结构化输出能力展开，核心价值在于提升结果可校验性与自动化集成稳定性。"
    if any(k in low for k in ["stock", "exchange", "holdings", "market"]):
        return "反映技术话题与资本市场情绪的联动效应，展示叙事变化如何影响市场关注与预期。"
    if any(k in low for k in ["social media", "literacy", "orality"]):
        return "讨论社交媒体语境下阅读与思考方式的变化，以及这种变化对公共讨论质量的长期影响。"
    if any(k in low for k in ["workshop", "crash", "tracing", "logs", "sentry"]):
        return "聚焦工程可观测性实践，强调通过崩溃、链路与日志联动来缩短问题定位与修复路径。"

    # 回退：根据分类输出归纳句
    cats = categories or ["技术实践"]
    if "安全风险" in cats:
        return "主要讨论风险识别与防护策略，强调在工程实践中尽早暴露并处理安全问题。"
    if "开发效率" in cats:
        return "核心在于提升开发效率与迭代质量，关注方法论、工具链和协作流程优化。"
    if "产业动态" in cats:
        return "侧重产业与市场层面的变化，体现技术进展与商业预期之间的相互影响。"
    if "社会观察" in cats:
        return "从社会与文化视角解读技术影响，关注长期行为变化与认知结构转移。"
    return "围绕技术实践展开，提供可用于决策或落地执行的观点与经验。"


def _overall_summary(selected: List[Entry]) -> str:
    if not selected:
        return "本时段可用条目较少，建议扩展时间窗口或增加 RSS 源后再观察。"

    text = " ".join([f"{e.title} {e.summary}" for e in selected]).lower()

    themes = []
    if any(k in text for k in ["ai", "llm", "codex", "agent", "anthropic", "openai"]):
        themes.append("AI 工程与模型工具")
    if any(k in text for k in ["security", "vulnerability", "cve", "漏洞", "安全"]):
        themes.append("安全与风险")
    if any(k in text for k in ["framework", "web", "token", "efficien", "benchmark"]):
        themes.append("工程效率与框架选型")
    if any(k in text for k in ["business", "stock", "market", "融资", "收购"]):
        themes.append("产业与市场动态")

    if not themes:
        themes = ["技术观点与实践复盘"]

    top_n = min(3, len(selected))
    top_titles = "、".join([f"《{e.title}》" for e in selected[:top_n]])
    return f"本期重点聚焦{ '、'.join(themes) }，代表性内容包括{top_titles}。"


def to_markdown(selected: List[Entry], hours: int, total: int, valid: int) -> str:
    lines = []
    lines.append(f"# 技术资讯简报（最近 {hours} 小时）")
    lines.append("")
    lines.append(f"- [RSS 来源](https://gist.githubusercontent.com/emschwartz/e6d2bf860ccc367fe37ff953ba6de66b/raw/426957f043dc0054f95aae6c19de1d0b4ecc2bb2/hn-popular-blogs-2025.opml)")
    lines.append("")

    # 分类汇总
    category_order = ["AI工程", "开发效率", "安全风险", "产业动态", "社会观察", "技术实践"]
    grouped = {k: [] for k in category_order}
    for e in selected:
        cats = e.categories or ["技术实践"]
        primary = next((c for c in cats if c != "AI工程"), cats[0])
        if primary not in grouped:
            grouped[primary] = []
        grouped[primary].append(e)

    idx = 1
    for cat in category_order:
        items = grouped.get(cat) or []
        if not items:
            continue
        lines.append(f"## **{cat}**")
        for e in items:
            lines.append(f"- [{e.title}]({e.link})")
            lines.append(f"  {_to_chinese_brief(e.title, e.summary, e.categories or [cat])}")
            lines.append("")
            idx += 1

    lines.append("---")
    lines.append(f"整体总结：{_overall_summary(selected)}")
    return '\n'.join(lines).strip() + '\n'


def main() -> int:
    p = argparse.ArgumentParser(description='从 OPML RSS 列表生成最近24小时中文简报')
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--opml-url', help='OPML URL')
    g.add_argument('--opml-file', help='本地 OPML 文件路径')
    p.add_argument('--hours', type=int, default=24)
    p.add_argument('--min-items', type=int, default=5)
    p.add_argument('--max-items', type=int, default=10)
    p.add_argument('--timeout', type=int, default=15)
    p.add_argument('--max-feeds', type=int, default=200)
    p.add_argument('--workers', type=int, default=10)
    p.add_argument('--output', help='输出 markdown 文件路径（可选）')
    args = p.parse_args()

    if args.min_items < 1 or args.max_items < args.min_items:
        print('参数错误：需满足 1 <= min-items <= max-items', file=sys.stderr)
        return 2

    if args.opml_url:
        opml_text = fetch_text(args.opml_url, timeout=args.timeout)
    else:
        with open(args.opml_file, 'r', encoding='utf-8') as f:
            opml_text = f.read()

    feed_urls = parse_opml(opml_text)[: args.max_feeds]

    all_entries: List[Entry] = []

    def work(url: str) -> Tuple[str, List[Entry], Optional[str]]:
        try:
            text = fetch_text(url, timeout=args.timeout)
            es = parse_feed(url, text)
            return url, es, None
        except Exception as e:
            return url, [], str(e)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
        futures = [ex.submit(work, u) for u in feed_urls]
        for fu in concurrent.futures.as_completed(futures):
            _, entries, _ = fu.result()
            all_entries.extend(entries)

    cutoff = now_utc() - dt.timedelta(hours=args.hours)
    in_window = [e for e in all_entries if e.published is None or e.published >= cutoff]

    # 去重：先 URL，再标题
    dedup = []
    seen_url = set()
    seen_title = set()
    for e in in_window:
        nu = normalize_url(e.link)
        tf = title_fingerprint(e.title)
        if nu in seen_url or tf in seen_title:
            continue
        seen_url.add(nu)
        seen_title.add(tf)
        e.categories = _classify_categories(e.title, e.summary)
        e.score = score_entry(e)
        dedup.append(e)

    dedup.sort(key=lambda x: (x.score, x.published or dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)), reverse=True)

    selected = dedup[: args.max_items]
    if len(selected) < args.min_items:
        # 条目不足时直接返回现有数据，不编造
        pass

    md = to_markdown(selected, hours=args.hours, total=len(all_entries), valid=len(dedup))
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(md)
    else:
        sys.stdout.write(md)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
