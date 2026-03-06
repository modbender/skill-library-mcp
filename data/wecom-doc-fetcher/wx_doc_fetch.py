#!/usr/bin/env python3
"""
企业微信开发者文档 → Markdown 转换工具

用法:
    python wx_doc_fetch.py <URL> [输出文件]
    python wx_doc_fetch.py https://developer.work.weixin.qq.com/document/path/94670 output.md

依赖:
    pip install requests playwright
    playwright install chromium  # 首次使用

Cookie 配置:
    在浏览器 DevTools → Network → 任意请求 → Copy as cURL
    把 -b '...' 里的 cookie 字符串粘贴到下方 COOKIES_RAW
    （仅在 playwright 自动提取 doc_id 失败时作为备用）
"""

import re
import sys
import json
import random
import argparse
import requests
from pathlib import Path

# ── 配置：粘贴浏览器 Cookie（从 DevTools → Copy as cURL 获取）─────────────────
COOKIES_RAW = """
wwrtx.i18n_lan=zh; ww_lang=cn,zh; wwapidoc.sid=YOUR_SID_HERE
"""
# ─────────────────────────────────────────────────────────────────────────────

BASE = "https://developer.work.weixin.qq.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Origin": BASE,
    "Referer": BASE + "/",
}


def parse_cookies(raw: str) -> dict:
    cookies = {}
    for part in raw.strip().split(";"):
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            cookies[k.strip()] = v.strip()
    return cookies


def get_doc_id_via_playwright(path_id: str) -> str:
    """用 Playwright 加载页面，拦截 fetchCnt 请求，从 POST body 提取 doc_id"""
    from playwright.sync_api import sync_playwright

    url = f"{BASE}/document/path/{path_id}"
    doc_id = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        def on_request(request):
            nonlocal doc_id
            if "fetchCnt" in request.url and request.method == "POST":
                body = request.post_data or ""
                m = re.search(r"doc_id=(\d+)", body)
                if m:
                    doc_id = m.group(1)

        page.on("request", on_request)
        page.goto(url, wait_until="networkidle", timeout=20000)
        browser.close()

    if doc_id:
        return doc_id
    raise ValueError(
        f"Playwright 未能从页面请求中提取 doc_id，请用 --doc-id 手动指定\n"
        f"方法：浏览器 DevTools → Network → fetchCnt 请求 → Payload → doc_id 的值"
    )


def get_doc_id(path_id: str, session: requests.Session) -> str:
    """提取 doc_id：优先用 Playwright 拦截请求，失败则回退到静态 HTML 解析"""
    # 方法1：Playwright 拦截（最可靠）
    try:
        return get_doc_id_via_playwright(path_id)
    except Exception as e:
        print(f"[warn] Playwright 提取失败（{e}），尝试静态解析…", file=sys.stderr)

    # 方法2：静态 HTML 正则（备用）
    url = f"{BASE}/document/path/{path_id}"
    r = session.get(url, timeout=15)
    r.raise_for_status()
    for pattern in [
        r'"doc_id"\s*:\s*(\d+)',
        r"doc_id[\"'\s:=]+(\d+)",
        r"docId[\"'\s:=]+(\d+)",
    ]:
        m = re.search(pattern, r.text)
        if m:
            return m.group(1)

    raise ValueError(
        f"无法自动提取 doc_id，请用 --doc-id 手动指定\n"
        f"方法：浏览器 DevTools → Network → fetchCnt 请求 → Payload → doc_id 的值"
    )


def fetch_doc(doc_id: str, session: requests.Session) -> dict:
    """调用 fetchCnt API"""
    url = f"{BASE}/docFetch/fetchCnt?lang=zh_CN&ajax=1&f=json&random={random.randint(100000, 999999)}"
    r = session.post(
        url,
        data={"doc_id": doc_id},
        headers={**HEADERS, "Content-Type": "application/x-www-form-urlencoded"},
        timeout=15,
    )
    r.raise_for_status()
    body = r.json()

    # 响应结构可能是 {"data": {...}} 或 {"result": {...}}
    return body.get("data") or body.get("result") or body


def clean_md(content: str, source_url: str = "") -> str:
    """清理 content_md，使其符合标准 Obsidian Markdown"""

    # 1. 移除 [TOC]
    content = re.sub(r"^\[TOC\]\s*\n?", "", content)

    # 2. 修复 ##标题 缺空格 → ## 标题
    content = re.sub(r"^(#{1,6})([^\s#\n])", r"\1 \2", content, flags=re.MULTILINE)

    # 3. 移除页内锚点链接 [text](#12977) 或 [text](#12977/子标题) → text
    content = re.sub(r"\[([^\]]+)\]\(#\d+[^)]*\)", r"\1", content)

    # 4. HTML 换行 → 空格（表格内常见）
    content = re.sub(r"</?br\s*/?>", " ", content, flags=re.IGNORECASE)

    # 5. <b>text</b> → **text**
    content = re.sub(r"<b>(.*?)</b>", r"**\1**", content, flags=re.DOTALL)

    # 6. <code>text</code> → `text`
    content = re.sub(r"<code>(.*?)</code>", r"`\1`", content)

    # 7. <font color="...">text</font> → text（去掉颜色标签，保留内容）
    content = re.sub(r"<font[^>]*>(.*?)</font>", r"\1", content, flags=re.DOTALL)

    # 8. !!#rrggbb text!! → text（企业微信自定义颜色语法，去掉标记保留内容）
    content = re.sub(r"!!#[0-9a-fA-F]{6}\s+(.*?)!!", r"\1", content)

    # 9. 去掉表格行的前导空格（Obsidian 不渲染缩进的表格）
    content = re.sub(r"^[ \t]+([\|])", r"\1", content, flags=re.MULTILINE)

    # 9b. 表格前确保有空行（紧跟在文字后的表格 Obsidian 不渲染）
    # 匹配"不以 | 开头的行"后面紧跟"以 | 开头的行"，在两者之间插入空行
    content = re.sub(r"^([^|\n][^\n]*)\n(\|)", r"\1\n\n\2", content, flags=re.MULTILINE)

    # 10. 多余空行压缩（超过 2 个连续空行 → 1 个）
    content = re.sub(r"\n{3,}", "\n\n", content)

    # 10. 添加来源注释
    header = f"> 来源：{source_url}\n\n" if source_url else ""

    return header + content.strip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="企业微信文档转 Markdown")
    parser.add_argument("url", help="文档 URL，如 .../document/path/94670")
    parser.add_argument("output", nargs="?", help="输出 .md 文件路径（不填则打印到 stdout）")
    parser.add_argument("--doc-id", help="手动指定 doc_id（跳过页面解析）")
    parser.add_argument("--cookies", help="Cookie 字符串（覆盖脚本内 COOKIES_RAW）")
    args = parser.parse_args()

    # 从 URL 提取 path_id
    m = re.search(r"/path/(\d+)", args.url)
    if not m:
        print("错误：URL 格式不正确，应包含 /path/<数字>", file=sys.stderr)
        sys.exit(1)
    path_id = m.group(1)

    # 构建 session
    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.update(parse_cookies(args.cookies or COOKIES_RAW))

    # 获取 doc_id
    try:
        doc_id = args.doc_id or get_doc_id(path_id, session)
    except ValueError as e:
        print(f"错误：{e}", file=sys.stderr)
        sys.exit(1)
    print(f"[info] path_id={path_id}  doc_id={doc_id}", file=sys.stderr)

    # 拉取文档
    data = fetch_doc(doc_id, session)
    content_md = data.get("content_md", "")
    if not content_md:
        print(f"错误：未获取到 content_md\n响应片段：{json.dumps(data)[:300]}", file=sys.stderr)
        sys.exit(1)

    # 清理
    result = clean_md(content_md, source_url=args.url)

    # 输出
    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"[done] 已写入：{args.output}", file=sys.stderr)
    else:
        print(result)


if __name__ == "__main__":
    main()
