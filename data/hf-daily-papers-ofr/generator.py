#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HF Daily Papers Generator — OFR 定制版
生成 Markdown / Telegram 格式的论文推荐报告
6 个 OFR 相关领域关键词筛选
"""

import os
import re
import urllib.request
import json
import sys
from datetime import datetime

# Proxy: env var > default Clash
_proxy = os.environ.get('HF_DAILY_PAPERS_PROXY', 'http://127.0.0.1:7890')
if _proxy:
    os.environ['HTTP_PROXY'] = _proxy
    os.environ['HTTPS_PROXY'] = _proxy

# ── OFR 6 大领域关键词 ──────────────────────────────────────────
CATEGORIES = {
    '🎬 Restoration & Enhancement': [
        'restoration', 'restoring', 'denoising', 'denoise',
        'deblur', 'deblurring', 'super-resolution', 'super resolution',
        'inpainting', 'scratch', 'flicker', 'deflicker',
        'old film', 'film grain', 'degradation', 'artifact removal',
        'image enhancement', 'video enhancement', 'low-light',
        'color restoration', 'colorization', 'film restoration',
    ],
    '🎞️ Video & Temporal': [
        'video', 'temporal', 'optical flow', 'frame interpolation',
        'video generation', 'video editing', 'video inpainting',
        'temporal consistency', 'recurrent', 'propagation',
        'multi-frame', 'sequence', 'motion',
    ],
    '⚡ Efficient Architecture': [
        'efficient', 'lightweight', 'pruning', 'quantization',
        'distillation', 'mobile', 'fast', 'real-time',
        'computation', 'flops', 'memory efficient', 'sparse',
        'acceleration', 'compression',
    ],
    '🔭 Vision Backbone & Attention': [
        'transformer', 'attention', 'self-attention', 'cross-attention',
        'vision transformer', 'vit', 'swin', 'deformable',
        'convolution', 'cnn', 'backbone', 'encoder', 'decoder',
        'mamba', 'state space', 'ssm', 'linear attention',
    ],
    '🌊 Frequency & Wavelet': [
        'wavelet', 'frequency', 'fourier', 'fft', 'dct',
        'spectral', 'haar', 'dwt', 'idwt',
        'frequency domain', 'high-frequency', 'low-frequency',
        'band', 'subband',
    ],
    '🎨 Diffusion & Generative Prior': [
        'diffusion', 'generative', 'gan', 'generation',
        'text-to-image', 'text-to-video', 'stable diffusion',
        'score-based', 'flow matching', 'rectified flow',
        'autoregressive', 'prior', 'latent',
    ],
}


def fetch_hf_papers():
    """获取 HF Daily Papers"""
    print("📥 获取 HF Daily Papers...")
    try:
        req = urllib.request.Request(
            "https://huggingface.co/papers",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            html = r.read().decode()
    except Exception as e:
        print(f"  ⚠️ HF 页面获取失败: {e}")
        return []

    paper_ids = list(set(re.findall(r'href="/papers/([0-9]+\.[0-9]+)"', html)))[:30]
    print(f"  找到 {len(paper_ids)} 篇 HF 论文 ID")

    papers = []
    for i, pid in enumerate(paper_ids):
        try:
            url = f"https://huggingface.co/api/papers/{pid}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode())
                papers.append({
                    'pid': pid,
                    'title': data.get('title', 'N/A')[:120],
                    'upvotes': data.get('upvotes', 0),
                    'summary': data.get('summary', '')[:600].lower(),
                    'source': 'hf',
                    'url': f'https://huggingface.co/papers/{pid}',
                })
        except Exception:
            continue
        if (i + 1) % 10 == 0:
            print(f"  已处理 {i+1}/{len(paper_ids)}...")

    papers.sort(key=lambda x: x['upvotes'], reverse=True)
    return papers


def fetch_arxiv_papers(max_results=50):
    """获取 arXiv CS.CV 最新论文（补充 HF 热榜盲区）"""
    import xml.etree.ElementTree as ET

    print("📥 获取 arXiv CS.CV 最新论文...")
    url = (
        f'http://export.arxiv.org/api/query?'
        f'search_query=cat:cs.CV&sortBy=submittedDate'
        f'&sortOrder=descending&max_results={max_results}'
    )
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            xml_data = r.read().decode()
    except Exception as e:
        print(f"  ⚠️ arXiv 获取失败: {e}")
        return []

    ns = {
        'atom': 'http://www.w3.org/2005/Atom',
        'arxiv': 'http://arxiv.org/schemas/atom',
    }
    root = ET.fromstring(xml_data)
    entries = root.findall('atom:entry', ns)
    print(f"  找到 {len(entries)} 篇 arXiv 论文")

    papers = []
    for entry in entries:
        try:
            arxiv_id_raw = entry.find('atom:id', ns).text  # http://arxiv.org/abs/2602.22033v1
            pid = arxiv_id_raw.split('/')[-1].split('v')[0]  # 2602.22033
            title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')[:120]
            summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')[:600].lower()
            papers.append({
                'pid': pid,
                'title': title,
                'upvotes': 0,  # arXiv 没有 upvote
                'summary': summary,
                'source': 'arxiv',
                'url': f'https://arxiv.org/abs/{pid}',
            })
        except Exception:
            continue

    return papers


def fetch_papers():
    """合并 HF + arXiv 源，去重"""
    hf = fetch_hf_papers()
    arxiv = fetch_arxiv_papers(max_results=50)

    # 去重：以 pid 为准，HF 优先（有 upvotes）
    seen = {p['pid'] for p in hf}
    merged = list(hf)
    for p in arxiv:
        if p['pid'] not in seen:
            seen.add(p['pid'])
            merged.append(p)

    print(f"\n  合并: HF {len(hf)} + arXiv {len(arxiv)} → 去重后 {len(merged)}")
    # HF 论文按 upvotes 排在前面，arXiv 补充在后面
    merged.sort(key=lambda x: x['upvotes'], reverse=True)
    return merged


def classify_papers(papers):
    """按 6 个 OFR 领域分类（一篇可属多个领域）"""
    result = {cat: [] for cat in CATEGORIES}
    uncategorized = []

    for p in papers:
        text = (p['title'] + ' ' + p['summary']).lower()
        matched = False
        for cat, keywords in CATEGORIES.items():
            if any(kw in text for kw in keywords):
                result[cat].append(p)
                matched = True
        if not matched:
            uncategorized.append(p)

    return result, uncategorized


def generate_markdown(classified, uncategorized, output_dir, timestamp):
    """生成 Markdown 文件"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    md_file = os.path.join(output_dir, f"{date_str}.md")

    lines = [f"# OFR 科研日报 — HF Daily Papers\n"]
    lines.append(f"**日期**: {date_str}  **生成时间**: {timestamp}\n")
    lines.append('---\n')

    total_relevant = sum(len(v) for v in classified.values())
    lines.append(f'> OFR 相关论文: **{total_relevant}** 篇（去重前）\n\n')

    for cat, papers in classified.items():
        if not papers:
            continue
        lines.append(f'## {cat} ({len(papers)} 篇)\n')
        for p in papers[:10]:
            src_tag = '🤗' if p.get('source') == 'hf' else '📄'
            up_str = f' ⬆️{p["upvotes"]}' if p['upvotes'] > 0 else ''
            lines.append(
                f'- {src_tag} [{p["title"]}]({p["url"]})'
                f'{up_str}\n'
            )
        lines.append('\n')

    if uncategorized:
        lines.append(f'## 📋 其他热门 ({len(uncategorized)} 篇)\n')
        for p in uncategorized[:5]:
            src_tag = '🤗' if p.get('source') == 'hf' else '📄'
            up_str = f' ⬆️{p["upvotes"]}' if p['upvotes'] > 0 else ''
            lines.append(
                f'- {src_tag} [{p["title"]}]({p["url"]})'
                f'{up_str}\n'
            )

    lines.append('\n---\n*Generated by OpenClaw HF Daily Papers Skill (OFR Edition)*\n')

    with open(md_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"✅ Markdown: {md_file}")
    return md_file


def generate_telegram(classified, uncategorized, output_dir, timestamp):
    """生成 Telegram 格式文本"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    tg_file = os.path.join(output_dir, f"{date_str}.telegram.txt")

    lines = [f"📰 OFR 科研日报 — {date_str}\n\n"]

    total_relevant = sum(len(v) for v in classified.values())
    if total_relevant == 0:
        lines.append("今日 HF 热榜暂无 OFR 相关论文。\n")
    else:
        for cat, papers in classified.items():
            if not papers:
                continue
            lines.append(f"{cat} ({len(papers)})\n")
            for p in papers[:5]:
                src_tag = '🤗' if p.get('source') == 'hf' else '📄'
                up_str = f' ⬆️{p["upvotes"]}' if p['upvotes'] > 0 else ''
                lines.append(
                    f"  {src_tag} {p['title']}\n"
                    f"    {up_str} {p['url']}\n"
                )
            lines.append('\n')

    if uncategorized:
        top3 = uncategorized[:3]
        lines.append(f"📋 其他热门\n")
        for p in top3:
            src_tag = '🤗' if p.get('source') == 'hf' else '📄'
            up_str = f' ⬆️{p["upvotes"]}' if p['upvotes'] > 0 else ''
            lines.append(
                f"  {src_tag} {p['title']}\n"
                f"    {up_str} {p['url']}\n"
            )

    with open(tg_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"✅ Telegram: {tg_file}")
    return tg_file


def main():
    do_telegram = '--telegram' in sys.argv
    do_pdf = '--pdf' in sys.argv

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'recommendations')
    os.makedirs(output_dir, exist_ok=True)

    papers = fetch_papers()
    classified, uncategorized = classify_papers(papers)

    total_relevant = sum(len(v) for v in classified.values())
    print(f"\n📊 Total: {len(papers)} | OFR-related: {total_relevant} | Other: {len(uncategorized)}")
    for cat, ps in classified.items():
        if ps:
            print(f"  {cat}: {len(ps)}")

    # Always generate markdown
    generate_markdown(classified, uncategorized, output_dir, timestamp)

    # Telegram format
    if do_telegram:
        generate_telegram(classified, uncategorized, output_dir, timestamp)

    # PDF (optional)
    if do_pdf:
        try:
            from fpdf import FPDF
            # PDF generation omitted for brevity — use markdown instead
            print("⚠️ PDF generation not yet implemented in OFR edition. Use markdown.")
        except ImportError:
            print("⚠️ fpdf not installed. Run: pip3 install fpdf")


if __name__ == '__main__':
    main()
