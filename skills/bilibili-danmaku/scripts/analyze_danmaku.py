#!/usr/bin/env python3
"""
对弹幕文本做：
1) 词频统计 + 词云图（WordCloud）
2) 情感分析（SnowNLP）
3) 舆情分析报告（Markdown）

依赖：jieba, snownlp, wordcloud, pillow, numpy
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
from collections import Counter
from datetime import datetime
from typing import Dict, List, Tuple


def _load_deps():
    try:
        import jieba  # type: ignore
        from snownlp import SnowNLP  # type: ignore
        from wordcloud import WordCloud  # type: ignore
    except Exception as e:
        print("[error] 缺少依赖：jieba / snownlp / wordcloud")
        print(f"[error] detail: {e}")
        print("[hint] 先执行: bash scripts/ensure_env.sh")
        raise SystemExit(3)
    return jieba, SnowNLP, WordCloud


DEFAULT_STOPWORDS = {
    "我们", "你们", "他们", "这个", "那个", "一个", "什么", "就是", "还是", "因为", "所以", "如果", "以及", "而且", "但是", "然后", "不是",
    "可以", "需要", "已经", "还有", "可能", "觉得", "比较", "一些", "这种", "这样", "一下", "一下子", "现在", "今天", "昨天", "这里", "那里",
    "视频", "弹幕", "啊", "哦", "嗯", "呃", "吧", "吗", "呢", "了", "的", "是", "在", "都", "也", "我", "你", "他", "她", "它", "就", "与", "和",
    "哈哈", "哈哈哈", "hhh", "hh", "233", "666", "www", "bilibili", "哔哩哔哩", "给我", "给你", "那边", "这边", "真的", "感觉", "太", "很", "有点",
}

NOISE_PATTERNS = [
    re.compile(r"^[\W_]+$"),
    re.compile(r"^(ha)+$", re.I),
    re.compile(r"^(h){2,}$", re.I),
    re.compile(r"^(哈){2,}$"),
    re.compile(r"^(啊){2,}$"),
    re.compile(r"^(嗯){2,}$"),
    re.compile(r"^(呃){2,}$"),
    re.compile(r"^(233)+$"),
    re.compile(r"^(666)+$"),
    re.compile(r"^[a-z]{1,2}$", re.I),
]

TOKEN_ALIAS = {
    "哔哩哔哩": "b站",
    "bilibili": "b站",
    "up": "up主",
}


def load_texts_from_csv(csv_path: str) -> List[str]:
    texts: List[str] = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            t = (row.get("text") or "").strip()
            if t:
                texts.append(t)
    return texts


def normalize_text(s: str) -> str:
    s = s.strip()
    s = re.sub(r"\s+", "", s)
    return s


def normalize_token(token: str) -> str:
    t = token.strip().lower()
    if not t:
        return ""
    # 去除首尾噪声符号
    t = re.sub(r"^[^\w\u4e00-\u9fff]+|[^\w\u4e00-\u9fff]+$", "", t)
    if not t:
        return ""
    # 压缩重复字符（例如 哈哈哈哈哈 -> 哈哈）
    t = re.sub(r"(.)\1{2,}", r"\1\1", t)
    # 别名合并
    t = TOKEN_ALIAS.get(t, t)
    return t


def tokenize_with_jieba(text: str, jieba_mod) -> List[str]:
    words = []
    for w in jieba_mod.cut(text, cut_all=False):
        w = w.strip().lower()
        if not w:
            continue
        # 仅保留中英文数字相关 token
        if not re.search(r"[\u4e00-\u9fffA-Za-z0-9]", w):
            continue
        words.append(w)
    return words


def _parse_inline_stopwords(extra: str) -> set[str]:
    if not extra:
        return set()
    parts = re.split(r"[,，\s]+", extra.strip())
    return {p.strip().lower() for p in parts if p.strip()}


def _load_stopwords_file(path: str) -> set[str]:
    out: set[str] = set()
    if not path or not os.path.exists(path):
        return out
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip().lower()
            if not s or s.startswith("#"):
                continue
            out.add(s)
    return out


def build_stopwords(extra_files: List[str], inline_extra: str) -> set[str]:
    stopwords = set(DEFAULT_STOPWORDS)

    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_file = os.path.join(skill_dir, "references", "stopwords.default.txt")
    stopwords |= _load_stopwords_file(default_file)

    for p in extra_files:
        stopwords |= _load_stopwords_file(p)

    stopwords |= _parse_inline_stopwords(inline_extra)
    return stopwords


def detect_drop_reason(token: str, stopwords: set[str], min_token_len: int) -> str | None:
    if not token:
        return "empty"
    if token in stopwords:
        return "stopword"
    if re.fullmatch(r"\d+", token):
        return "number"
    if len(token) > 24:
        return "too_long"
    if len(token) < min_token_len:
        return "too_short"
    if len(token) == 1 and re.fullmatch(r"[\u4e00-\u9fff]", token):
        return "single_cn"
    for pat in NOISE_PATTERNS:
        if pat.fullmatch(token):
            return "noise_pattern"
    return None


def clean_terms(
    terms: List[str],
    stopwords: set[str],
    min_token_len: int,
    stats: Dict[str, int],
) -> List[str]:
    out: List[str] = []
    for t in terms:
        stats["raw_tokens"] += 1
        n = normalize_token(t)
        reason = detect_drop_reason(n, stopwords, min_token_len)
        if reason:
            stats[f"drop_{reason}"] += 1
            continue
        out.append(n)
        stats["kept_tokens"] += 1
    return out


def find_font_path() -> str:
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Songti.ttc",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return ""


def build_wordcloud_png(
    WordCloudCls,
    word_counts: List[Tuple[str, int]],
    out_png: str,
    max_words: int = 260,
) -> None:
    freq = {w: c for w, c in word_counts if c >= 2}
    if not freq:
        freq = {"弹幕": 10, "视频": 6}

    font_path = find_font_path()

    wc = WordCloudCls(
        width=1800,
        height=1000,
        background_color="white",
        max_words=max_words,
        min_font_size=12,
        max_font_size=240,
        prefer_horizontal=0.92,
        margin=2,
        collocations=False,
        relative_scaling=0.35,
        font_path=font_path or None,
    )

    wc.generate_from_frequencies(freq)
    wc.to_file(out_png)


def classify_sentiment(score: float, pos_th: float, neg_th: float) -> str:
    if score >= pos_th:
        return "positive"
    if score <= neg_th:
        return "negative"
    return "neutral"


def write_markdown_report(
    out_md: str,
    meta: Dict,
    total: int,
    sentiment: Dict[str, int],
    avg_score: float,
    top_words: List[Tuple[str, int]],
    top_pos: List[Tuple[str, float]],
    top_neg: List[Tuple[str, float]],
    pos_th: float,
    neg_th: float,
    cleaning_stats: Dict[str, int],
    docfreq_removed: int,
) -> None:
    pos_pct = sentiment["positive"] / total * 100 if total else 0
    neu_pct = sentiment["neutral"] / total * 100 if total else 0
    neg_pct = sentiment["negative"] / total * 100 if total else 0

    def fmt_pairs(ps, limit=10):
        return "、".join([f"{w}({c})" for w, c in ps[:limit]]) if ps else "无"

    if neg_pct - pos_pct >= 8:
        trend = "负向主导"
    elif pos_pct - neg_pct >= 8:
        trend = "正向主导"
    else:
        trend = "分歧/中性主导"

    with open(out_md, "w", encoding="utf-8") as f:
        f.write("# B站弹幕舆情分析报告\n\n")
        f.write(f"- 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- 视频：{meta.get('title','')}\n")
        f.write(f"- BVID：{meta.get('bvid','')}  CID：{meta.get('cid','')}\n")
        f.write(f"- 弹幕样本量：{total}\n")
        f.write("- 分析方法：jieba 分词 + SnowNLP 情感打分\n")
        f.write(
            f"- 清洗统计：原始token {cleaning_stats.get('raw_tokens',0)} → 保留 {cleaning_stats.get('kept_tokens',0)}，"
            f"剔除高频干扰词 {docfreq_removed}\n\n"
        )

        f.write("## 1) 情感分析\n\n")
        f.write(f"- 正向：{sentiment['positive']}（{pos_pct:.1f}%）\n")
        f.write(f"- 中性：{sentiment['neutral']}（{neu_pct:.1f}%）\n")
        f.write(f"- 负向：{sentiment['negative']}（{neg_pct:.1f}%）\n")
        f.write(f"- 平均情绪分（0-1）：{avg_score:.3f}\n")
        f.write(f"- 阈值：positive >= {pos_th:.2f}, negative <= {neg_th:.2f}\n")
        f.write(f"- 总体判断：**{trend}**\n\n")

        f.write("## 2) 热词与关注点\n\n")
        f.write(f"- 高频关键词：{fmt_pairs(top_words)}\n")
        f.write("- 解读：高频词反映受众即时关注焦点，可用于提炼内容钩子与风险点。\n\n")

        f.write("## 3) 典型弹幕（情绪极值）\n\n")
        f.write("### 正向代表\n")
        if top_pos:
            for t, s in top_pos[:5]:
                f.write(f"- ({s:.3f}) {t}\n")
        else:
            f.write("- 无\n")

        f.write("\n### 负向代表\n")
        if top_neg:
            for t, s in top_neg[:5]:
                f.write(f"- ({s:.3f}) {t}\n")
        else:
            f.write("- 无\n")

        f.write("\n## 4) 舆情结论（运营口径）\n\n")
        if trend == "负向主导":
            f.write("- 负向反馈明显，建议优先识别争议源并快速补充事实口径。\n")
            f.write("- 评论区可置顶澄清信息，避免误解继续发酵。\n")
        elif trend == "正向主导":
            f.write("- 受众认可度较高，可放大高频正向看点做二次传播。\n")
            f.write("- 建议沉淀高共鸣弹幕，用于封面文案/二创素材。\n")
        else:
            f.write("- 讨论以中性/分歧为主，建议做分层沟通。\n")
            f.write("- 对争议点给解释，对共鸣点给强化。\n")


def main() -> int:
    jieba_mod, SnowNLP, WordCloudCls = _load_deps()

    parser = argparse.ArgumentParser(description="分析B站弹幕：词云 + 情感 + 舆情")
    parser.add_argument("--csv", required=True, help="fetch_danmaku.py 输出的 csv 文件")
    parser.add_argument("--meta", default="", help="fetch_danmaku.py 输出的 meta.json（可选）")
    parser.add_argument("--outdir", default="./output", help="输出目录")
    parser.add_argument("--name", default="bilibili_danmaku", help="输出名前缀")

    parser.add_argument("--stopwords-file", action="append", default=[], help="自定义停用词文件（可重复传）")
    parser.add_argument("--extra-stopwords", default="", help="额外停用词，逗号分隔")
    parser.add_argument("--min-token-len", type=int, default=2, help="最小词长（默认2）")
    parser.add_argument("--min-word-freq", type=int, default=2, help="热词最小频次（默认2）")
    parser.add_argument("--max-doc-freq-ratio", type=float, default=0.65, help="过高文档频率阈值（0~1）")
    parser.add_argument("--max-doc-freq-token-len", type=int, default=2, help="只对短词做高频剔除（默认长度<=2）")
    parser.add_argument("--disable-docfreq-clean", action="store_true", help="关闭高文档频率干扰词剔除")

    parser.add_argument("--pos-threshold", type=float, default=0.60, help="SnowNLP正向阈值")
    parser.add_argument("--neg-threshold", type=float, default=0.40, help="SnowNLP负向阈值")
    parser.add_argument("--max-words", type=int, default=260, help="词云最多词数")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    texts = [normalize_text(x) for x in load_texts_from_csv(args.csv)]
    texts = [t for t in texts if t]

    if not texts:
        print("[error] CSV中无有效弹幕文本")
        return 2

    meta = {}
    if args.meta and os.path.exists(args.meta):
        with open(args.meta, "r", encoding="utf-8") as f:
            meta_raw = json.load(f)
        src = meta_raw.get("source") or {}
        vid = meta_raw.get("video") or {}
        meta = {
            "bvid": src.get("bvid") or vid.get("bvid"),
            "cid": src.get("cid"),
            "title": vid.get("title") or "",
        }

    stopwords = build_stopwords(args.stopwords_file, args.extra_stopwords)

    # 1) jieba 分词 + 清洗
    stats: Dict[str, int] = Counter()
    all_terms: List[str] = []
    doc_freq: Counter[str] = Counter()

    for t in texts:
        raw_terms = tokenize_with_jieba(t, jieba_mod)
        cleaned = clean_terms(raw_terms, stopwords, args.min_token_len, stats)
        all_terms.extend(cleaned)

        uniq = set(cleaned)
        for token in uniq:
            doc_freq[token] += 1

    wc_counter = Counter(all_terms)

    docfreq_removed_tokens: List[str] = []
    if not args.disable_docfreq_clean and texts:
        ratio = max(0.0, min(1.0, args.max_doc_freq_ratio))
        doc_threshold = max(1, int(len(texts) * ratio))
        for token, df in doc_freq.items():
            if df >= doc_threshold and len(token) <= args.max_doc_freq_token_len:
                if token in wc_counter:
                    del wc_counter[token]
                    docfreq_removed_tokens.append(token)

    top_words = [(w, c) for w, c in wc_counter.most_common(300) if c >= args.min_word_freq]

    # 2) SnowNLP 情感
    sentiment = {"positive": 0, "neutral": 0, "negative": 0}
    scored: List[Tuple[str, float, str]] = []
    total_score = 0.0
    for t in texts:
        try:
            score = float(SnowNLP(t).sentiments)  # 0~1
        except Exception:
            score = 0.5
        cls = classify_sentiment(score, args.pos_threshold, args.neg_threshold)
        sentiment[cls] += 1
        total_score += score
        scored.append((t, score, cls))

    avg_score = total_score / len(texts)
    top_pos = sorted([(t, s) for t, s, c in scored if c == "positive"], key=lambda x: x[1], reverse=True)
    top_neg = sorted([(t, s) for t, s, c in scored if c == "negative"], key=lambda x: x[1])

    # 3) 输出
    prefix = args.name
    top_words_json = os.path.join(args.outdir, f"{prefix}_top_words.json")
    sentiment_json = os.path.join(args.outdir, f"{prefix}_sentiment.json")
    cloud_png = os.path.join(args.outdir, f"{prefix}_wordcloud.png")
    report_md = os.path.join(args.outdir, f"{prefix}_report.md")

    with open(top_words_json, "w", encoding="utf-8") as f:
        json.dump(top_words, f, ensure_ascii=False, indent=2)

    with open(sentiment_json, "w", encoding="utf-8") as f:
        json.dump(
            {
                "total": len(texts),
                "distribution": sentiment,
                "avg_score": avg_score,
                "thresholds": {"pos": args.pos_threshold, "neg": args.neg_threshold},
                "engine": "SnowNLP",
                "cleaning": {
                    "stopwords_count": len(stopwords),
                    "raw_tokens": stats.get("raw_tokens", 0),
                    "kept_tokens": stats.get("kept_tokens", 0),
                    "dropped": {
                        "stopword": stats.get("drop_stopword", 0),
                        "number": stats.get("drop_number", 0),
                        "too_short": stats.get("drop_too_short", 0),
                        "single_cn": stats.get("drop_single_cn", 0),
                        "noise_pattern": stats.get("drop_noise_pattern", 0),
                        "empty": stats.get("drop_empty", 0),
                    },
                    "docfreq_removed_tokens": docfreq_removed_tokens[:120],
                },
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    build_wordcloud_png(WordCloudCls, top_words, cloud_png, max_words=args.max_words)

    write_markdown_report(
        out_md=report_md,
        meta=meta,
        total=len(texts),
        sentiment=sentiment,
        avg_score=avg_score,
        top_words=top_words,
        top_pos=top_pos,
        top_neg=top_neg,
        pos_th=args.pos_threshold,
        neg_th=args.neg_threshold,
        cleaning_stats=stats,
        docfreq_removed=len(docfreq_removed_tokens),
    )

    print("[ok] 分析完成")
    print(f"[ok] total: {len(texts)}")
    print(f"[ok] top_words: {top_words_json}")
    print(f"[ok] sentiment: {sentiment_json}")
    print(f"[ok] wordcloud_png: {cloud_png}")
    print(f"[ok] report_md: {report_md}")
    print(
        f"[ok] cleaning: raw={stats.get('raw_tokens',0)} kept={stats.get('kept_tokens',0)} "
        f"docfreq_removed={len(docfreq_removed_tokens)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
