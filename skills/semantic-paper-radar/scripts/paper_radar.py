#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import math
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

STOPWORDS = {
    "the", "a", "an", "and", "or", "for", "of", "to", "in", "on", "with", "from", "by", "using",
    "based", "via", "towards", "toward", "new", "study", "analysis", "approach", "method", "methods",
    "model", "models", "data", "system", "systems", "learning", "deep", "neural", "research", "paper"
}


def fetch_json(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "semantic-paper-radar/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", errors="replace"))


def fetch_text(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "semantic-paper-radar/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def year_from_date(s):
    if not s:
        return None
    m = re.search(r"(19|20)\d{2}", str(s))
    return int(m.group()) if m else None


def normalize_title(t):
    t = re.sub(r"\s+", " ", (t or "").strip().lower())
    return re.sub(r"[^\w\s]", "", t)


def tokenize(text):
    words = re.findall(r"[a-zA-Z][a-zA-Z\-]{2,}", (text or "").lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 2]


def search_arxiv(query, max_results=20):
    q = urllib.parse.quote(query)
    url = (
        "http://export.arxiv.org/api/query?search_query=all:%s&start=0&max_results=%d"
        "&sortBy=relevance&sortOrder=descending" % (q, max_results)
    )
    xml_text = fetch_text(url)
    root = ET.fromstring(xml_text)
    ns = {"a": "http://www.w3.org/2005/Atom"}

    out = []
    for e in root.findall("a:entry", ns):
        title = (e.findtext("a:title", default="", namespaces=ns) or "").strip()
        summary = (e.findtext("a:summary", default="", namespaces=ns) or "").strip()
        published = e.findtext("a:published", default="", namespaces=ns)
        arxiv_id = ""
        link = ""
        id_text = e.findtext("a:id", default="", namespaces=ns)
        if id_text:
            arxiv_id = id_text.rsplit("/", 1)[-1]
            link = id_text
        authors = [a.findtext("a:name", default="", namespaces=ns) for a in e.findall("a:author", ns)]

        out.append({
            "source": "arxiv",
            "id": arxiv_id or link or normalize_title(title),
            "title": title,
            "abstract": summary,
            "year": year_from_date(published),
            "authors": [x for x in authors if x],
            "url": link,
            "doi": None,
            "citations": 0,
            "venue": "arXiv",
            "is_preprint": True,
        })
    return out


def search_openalex(query, max_results=25, from_year=None):
    q = urllib.parse.quote(query)
    filt = []
    if from_year:
        filt.append(f"from_publication_date:{from_year}-01-01")
    filter_part = "&filter=" + urllib.parse.quote(",".join(filt)) if filt else ""
    url = (
        f"https://api.openalex.org/works?search={q}&per-page={max_results}{filter_part}"
        "&sort=relevance_score:desc"
    )
    data = fetch_json(url)

    out = []
    for w in data.get("results", []):
        title = (w.get("title") or "").strip()
        abstract = ""
        inv = w.get("abstract_inverted_index") or {}
        if inv:
            idx_to_word = {}
            for word, poss in inv.items():
                for p in poss:
                    idx_to_word[p] = word
            if idx_to_word:
                abstract = " ".join(idx_to_word[i] for i in sorted(idx_to_word))
        year = w.get("publication_year")
        authors = [a.get("author", {}).get("display_name", "") for a in w.get("authorships", [])][:8]
        loc = w.get("primary_location") or {}
        src = (loc.get("source") or {})
        venue = src.get("display_name") or ("OpenAlex")

        out.append({
            "source": "openalex",
            "id": (w.get("id") or normalize_title(title)).split("/")[-1],
            "title": title,
            "abstract": abstract,
            "year": int(year) if year else None,
            "authors": [x for x in authors if x],
            "url": w.get("doi") or w.get("id") or "",
            "doi": w.get("doi"),
            "citations": int(w.get("cited_by_count") or 0),
            "venue": venue,
            "is_preprint": bool((w.get("type") or "").lower() == "preprint"),
        })
    return out




def is_biomed_query(query):
    q = (query or "").lower()
    hints = [
        "biomedical", "medicine", "clinical", "cancer", "genome", "genomics",
        "rna", "cell", "protein", "drug", "therapy", "disease", "pubmed",
        "single-cell", "microbiome", "neuro", "immun", "metabolic"
    ]
    return any(h in q for h in hints)


def search_pubmed(query, max_results=20, from_year=None):
    term = query
    if from_year:
        term = f"({query}) AND ({from_year}:3000[pdat])"
    esearch_url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        f"?db=pubmed&retmode=json&retmax={max_results}&sort=relevance&term="
        + urllib.parse.quote(term)
    )
    es = fetch_json(esearch_url)
    ids = (es.get("esearchresult") or {}).get("idlist") or []
    if not ids:
        return []

    efetch_url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        "?db=pubmed&retmode=xml&id=" + ",".join(ids)
    )
    xml_text = fetch_text(efetch_url)
    root = ET.fromstring(xml_text)

    out = []
    for art in root.findall('.//PubmedArticle'):
        pmid = art.findtext('.//PMID') or ''
        title = (art.findtext('.//ArticleTitle') or '').strip()
        abstract_parts = [x.text or '' for x in art.findall('.//Abstract/AbstractText')]
        abstract = ' '.join(x.strip() for x in abstract_parts if x and x.strip())
        y = art.findtext('.//PubDate/Year') or art.findtext('.//ArticleDate/Year')
        year = int(y) if y and y.isdigit() else None
        journal = (art.findtext('.//Journal/Title') or 'PubMed').strip()

        authors = []
        for a in art.findall('.//Author')[:8]:
            ln = a.findtext('LastName') or ''
            fn = a.findtext('ForeName') or ''
            name = (fn + ' ' + ln).strip()
            if name:
                authors.append(name)

        doi = None
        for aid in art.findall('.//ArticleId'):
            if aid.attrib.get('IdType') == 'doi' and (aid.text or '').strip():
                doi = aid.text.strip()
                break

        out.append({
            "source": "pubmed",
            "id": pmid or normalize_title(title),
            "title": title,
            "abstract": abstract,
            "year": year,
            "authors": authors,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
            "doi": f"https://doi.org/{doi}" if doi else None,
            "citations": 0,
            "venue": journal,
            "is_preprint": False,
        })
    return out

def dedupe(papers):
    by_key = {}
    for p in papers:
        key = p.get("doi") or normalize_title(p.get("title", ""))
        if not key:
            continue
        if key not in by_key:
            by_key[key] = p
            continue
        # Prefer richer metadata (citations, venue) from openalex
        old = by_key[key]
        score_old = (old.get("citations", 0) > 0) + (old.get("source") == "openalex")
        score_new = (p.get("citations", 0) > 0) + (p.get("source") == "openalex")
        if score_new >= score_old:
            by_key[key] = p
    return list(by_key.values())


def score_paper(p, now_year, mode="balanced"):
    y = p.get("year") or (now_year - 8)
    age = max(0, now_year - y)
    recency = math.exp(-age / 4.0)
    citations = math.log1p(max(0, p.get("citations", 0)))
    authority = 1.1 if p.get("source") == "openalex" else (1.0 if p.get("source") == "pubmed" else 0.8)
    preprint_penalty = 0.85 if p.get("is_preprint") else 1.0

    if mode == "foundational":
        s = citations * 0.7 + recency * 0.2 + authority * 0.1
    elif mode == "frontier":
        s = citations * 0.2 + recency * 0.7 + authority * 0.1
    else:
        s = citations * 0.45 + recency * 0.45 + authority * 0.10
    return s * preprint_penalty


def classify(p, now_year):
    y = p.get("year") or now_year
    c = p.get("citations", 0)
    age = now_year - y
    if c >= 200 or (age >= 6 and c >= 80):
        return "经典奠基"
    if age <= 2:
        return "最新前沿"
    return "方法跃迁"


def build_threads(papers, top_k=4):
    token_counter = Counter()
    for p in papers:
        token_counter.update(tokenize((p.get("title") or "") + " " + (p.get("abstract") or "")))
    keywords = [w for w, _ in token_counter.most_common(30)]

    threads = defaultdict(list)
    for p in papers:
        tks = set(tokenize((p.get("title") or "") + " " + (p.get("abstract") or "")))
        hit = next((k for k in keywords if k in tks), "misc")
        threads[hit].append(p)

    ranked = sorted(threads.items(), key=lambda kv: len(kv[1]), reverse=True)
    return ranked[:top_k]


def to_md_report(query, papers, top_n, mode):
    now_year = dt.datetime.utcnow().year
    scored = sorted(papers, key=lambda p: p["_score"], reverse=True)[:top_n]

    groups = defaultdict(list)
    for p in scored:
        groups[classify(p, now_year)].append(p)

    lines = []
    lines.append(f"# 领域必读文献推荐：{query}\n")
    sources = sorted({(p.get("source") or "unknown") for p in papers})
    lines.append(f"检索策略：{'+'.join(sources)} 聚合语义检索；排序模式：{mode}\n")

    for sec in ["经典奠基", "方法跃迁", "最新前沿"]:
        if not groups.get(sec):
            continue
        lines.append(f"## {sec}")
        for i, p in enumerate(groups[sec], 1):
            a0 = p.get("authors", ["未知作者"])[0] if p.get("authors") else "未知作者"
            y = p.get("year") or "n/a"
            c = p.get("citations", 0)
            venue = p.get("venue") or p.get("source")
            why = "高引用、奠定问题定义" if sec == "经典奠基" else ("连接经典与应用" if sec == "方法跃迁" else "近两年新方向/新结果")
            title = p.get('title','(untitled)')
            link = p.get('url') or p.get('doi') or ''
            title_md = f"[{title}]({link})" if link else title
            lines.append(f"{i}. **{title_md}** ({y})")
            lines.append(f"   - 作者：{a0} 等；来源：{venue}；引用：{c}")
            lines.append(f"   - 必读理由：{why}")
            lines.append(f"   - 期刊/来源：{venue}")
        lines.append("")

    # Timeline
    lines.append("## 学术脉络（时间线）")
    by_year = sorted([p for p in scored if p.get("year")], key=lambda x: x["year"])
    for p in by_year[: min(8, len(by_year))]:
        t = p.get('title')
        u = p.get('url') or p.get('doi') or ''
        t_md = f"[{t}]({u})" if u else t
        lines.append(f"- {p.get('year')}: {t_md}（{p.get('venue')}）")
    lines.append("")

    # Theme threads
    lines.append("## 主题主线")
    threads = build_threads(scored, top_k=3)
    for k, ps in threads:
        ps_sorted = sorted(ps, key=lambda x: x["_score"], reverse=True)
        top_title = ps_sorted[0].get("title") if ps_sorted else ""
        lines.append(f"- **{k} 主线**：{len(ps)} 篇相关文献，代表作：{top_title}")
    lines.append("")


    lines.append("## 里程碑论文（带链接）")
    milestones = sorted(scored, key=lambda x: (x.get("citations",0), x.get("_score",0)), reverse=True)[:5]
    for i, p in enumerate(milestones, 1):
        t = p.get("title","(untitled)")
        u = p.get("url") or p.get("doi") or ""
        t_md = f"[{t}]({u})" if u else t
        lines.append(f"{i}. {t_md}（{p.get('year') or 'n/a'}，{p.get('venue') or p.get('source')}，引用 {p.get('citations',0)}）")
    lines.append("")

    # Reading order
    lines.append("## 建议阅读顺序（先读 3 篇）")
    starter = scored[:3]
    for i, p in enumerate(starter, 1):
        lines.append(f"{i}. {p.get('title')}（先建立该方向核心问题/范式）")

    return "\n".join(lines) + "\n"




def slugify(text):
    t = re.sub(r"[^a-zA-Z0-9一-鿿]+", "-", (text or "").strip().lower())
    t = re.sub(r"-+", "-", t).strip("-")
    return t or "paper-radar"


def md_to_simple_html(md_text, title="Semantic Paper Radar Report"):
    lines = md_text.splitlines()
    out = []
    out.append("<!doctype html><html><head><meta charset='utf-8'>")
    out.append(f"<title>{title}</title>")
    out.append("<style>body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Arial,sans-serif;max-width:980px;margin:24px auto;padding:0 16px;line-height:1.6}h1,h2{line-height:1.3}code{background:#f2f2f2;padding:2px 4px;border-radius:4px}a{color:#0969da;text-decoration:none}a:hover{text-decoration:underline}ul{padding-left:22px}.muted{color:#666}</style></head><body>")
    link_pat = re.compile(r"\[([^\]]+)\]\(([^\)]+)\)")

    def conv_links(t):
        return link_pat.sub(lambda m: f'<a href="{m.group(2)}" target="_blank" rel="noopener noreferrer">{m.group(1)}</a>', t)

    in_list = False
    for ln in lines:
        ln = ln.rstrip()
        if not ln:
            if in_list:
                out.append("</ul>")
                in_list = False
            continue
        if ln.startswith("# "):
            if in_list:
                out.append("</ul>"); in_list=False
            out.append(f"<h1>{conv_links(ln[2:])}</h1>")
        elif ln.startswith("## "):
            if in_list:
                out.append("</ul>"); in_list=False
            out.append(f"<h2>{conv_links(ln[3:])}</h2>")
        elif ln.startswith("- "):
            if not in_list:
                out.append("<ul>"); in_list=True
            out.append(f"<li>{conv_links(ln[2:])}</li>")
        else:
            if in_list:
                out.append("</ul>"); in_list=False
            out.append(f"<p>{conv_links(ln)}</p>")
    if in_list:
        out.append("</ul>")
    out.append("<p class='muted'>Generated by semantic-paper-radar</p>")
    out.append("</body></html>")
    return "\n".join(out)

def run_search(args):
    now_year = dt.datetime.utcnow().year
    from_year = now_year - args.years if args.years else None

    papers = []
    try:
        papers.extend(search_arxiv(args.query, max_results=max(10, args.max // 2)))
    except Exception as e:
        print(f"[warn] arxiv search failed: {e}", file=sys.stderr)

    try:
        papers.extend(search_openalex(args.query, max_results=max(10, args.max), from_year=from_year))
    except Exception as e:
        print(f"[warn] openalex search failed: {e}", file=sys.stderr)

    if args.biomed or is_biomed_query(args.query):
        try:
            papers.extend(search_pubmed(args.query, max_results=max(10, args.max // 2), from_year=from_year))
        except Exception as e:
            print(f"[warn] pubmed search failed: {e}", file=sys.stderr)

    papers = dedupe(papers)
    for p in papers:
        p["_score"] = round(score_paper(p, now_year, mode=args.mode), 6)
    papers = sorted(papers, key=lambda x: x["_score"], reverse=True)

    out = {
        "query": args.query,
        "mode": args.mode,
        "count": len(papers),
        "papers": papers,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


def run_report(args):
    now_year = dt.datetime.utcnow().year
    from_year = now_year - args.years if args.years else None

    papers = []
    try:
        papers.extend(search_arxiv(args.query, max_results=max(10, args.max // 2)))
    except Exception as e:
        print(f"[warn] arxiv search failed: {e}", file=sys.stderr)
    try:
        papers.extend(search_openalex(args.query, max_results=max(10, args.max), from_year=from_year))
    except Exception as e:
        print(f"[warn] openalex search failed: {e}", file=sys.stderr)

    if args.biomed or is_biomed_query(args.query):
        try:
            papers.extend(search_pubmed(args.query, max_results=max(10, args.max // 2), from_year=from_year))
        except Exception as e:
            print(f"[warn] pubmed search failed: {e}", file=sys.stderr)

    papers = dedupe(papers)
    for p in papers:
        p["_score"] = score_paper(p, now_year, mode=args.mode)

    md = to_md_report(args.query, papers, top_n=args.top, mode=args.mode)
    if args.export_html:
        html = md_to_simple_html(md, title=f"Paper Radar - {args.query}")
        out_path = args.html_out or f"report_{slugify(args.query)}.html"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[html] exported: {out_path}")
    print(md)


def build_parser():
    p = argparse.ArgumentParser(description="Semantic paper radar across arXiv/OpenAlex/PubMed")
    sub = p.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--query", required=True, help="Natural language topic query")
    common.add_argument("--max", type=int, default=40, help="Max records per source range")
    common.add_argument("--years", type=int, default=8, help="Look-back years")
    common.add_argument("--mode", choices=["balanced", "foundational", "frontier"], default="balanced")
    common.add_argument("--biomed", action="store_true", help="Force include PubMed retrieval")

    s = sub.add_parser("search", parents=[common], help="Return merged JSON results")
    s.set_defaults(func=run_search)

    r = sub.add_parser("report", parents=[common], help="Return markdown recommendation report")
    r.add_argument("--top", type=int, default=12, help="Top papers in report")
    r.add_argument("--export-html", action="store_true", help="Also export an HTML report file")
    r.add_argument("--html-out", help="Output path for HTML report (requires --export-html)")
    r.set_defaults(func=run_report)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
