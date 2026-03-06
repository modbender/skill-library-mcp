#!/usr/bin/env python3
"""
書籤增強工具
1. AI 濃縮 - 自動產生摘要（使用 MiniMax API）
2. 交叉連結 - 自動建立 wiki-link
"""

import os
import re
import time
import requests
from pathlib import Path

BOOKMARKS_DIR = Path(os.getenv("BOOKMARKS_DIR", "/home/ubuntu/clawd/memory/bookmarks"))
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_ENDPOINT = os.getenv("MINIMAX_ENDPOINT", "https://api.minimax.io/anthropic/v1/messages")
MINIMAX_MODEL = os.getenv("MINIMAX_MODEL", "MiniMax-M2.5")


def call_minimax(prompt, system_prompt="你是一個專業的AI內容分析師，擅長產生簡潔的濃縮摘要。"):
    """呼叫 MiniMax API（安全：讀環境變數）"""
    if not MINIMAX_API_KEY:
        print("⚠️ 未設定 MINIMAX_API_KEY，略過 AI 濃縮")
        return None

    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MINIMAX_MODEL,
        "messages": [
            {"role": "user", "content": f"{system_prompt}\n\n{prompt}"}
        ],
        "temperature": 0.4,
        "max_tokens": 800
    }

    try:
        response = requests.post(MINIMAX_ENDPOINT, headers=headers, json=data, timeout=45)
        if response.status_code >= 400:
            print(f"❌ MiniMax API 錯誤 {response.status_code}: {response.text[:300]}")
            return None

        result = response.json() if response.content else {}

        # Anthropic-compatible 回應
        if isinstance(result.get("content"), list):
            text_chunks = []
            for item in result.get("content", []):
                if item.get("type") in ("text", "thinking"):
                    val = item.get("text") or item.get("thinking")
                    if val:
                        text_chunks.append(val)
            return "\n".join(text_chunks).strip() or None

        # OpenAI-ish 回應
        choices = result.get("choices") or []
        if choices:
            return (((choices[0] or {}).get("message") or {}).get("content") or "").strip() or None

        print(f"❌ 無法解析 API 回應: {result}")
        return None
    except Exception as e:
        print(f"❌ 請求錯誤: {e}")
        return None


def get_all_bookmarks():
    bookmarks = []
    if not BOOKMARKS_DIR.exists():
        return bookmarks

    for f in BOOKMARKS_DIR.rglob("*.md"):
        if f.name.startswith("."):
            continue
        if f.name in ["INDEX.md", "urls.txt"]:
            continue
        if "test-" in f.name:
            continue

        content = f.read_text(encoding="utf-8", errors="ignore")
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = title_match.group(1) if title_match else f.stem
        tags = re.findall(r"#(\w+)", content)
        url_match = re.search(r"\*\*原始連結\*\*：(.+)", content)
        url = url_match.group(1).strip() if url_match else ""

        bookmarks.append({
            "path": str(f),
            "filename": f.name.replace(".md", ""),
            "title": title,
            "tags": tags,
            "url": url,
            "content": content,
        })
    return bookmarks


def find_related_bookmarks(current_bookmark, all_bookmarks, limit=3):
    current_tags = set(current_bookmark.get("tags") or [])
    related = []

    for b in all_bookmarks:
        if b.get("path") == current_bookmark.get("path"):
            continue
        overlap = current_tags & set(b.get("tags") or [])
        if overlap:
            related.append({
                "filename": b.get("filename"),
                "title": b.get("title"),
                "overlap": len(overlap),
                "tags": sorted(list(overlap)),
            })

    related.sort(key=lambda x: x["overlap"], reverse=True)
    return related[:limit]


def generate_ai_summary(bookmark):
    content = bookmark.get("content", "")
    title = bookmark.get("title", "(untitled)")
    truncated = content[:3000]

    prompt = f"""請為以下文章產生濃縮摘要，格式如下：

## 📌 一句話摘要
（一句話概括文章核心，20字以內）

## 🎯 三個重點
1. （重點一）
2. （重點二）
3. （重點三）

## 💡 應用場景
（這篇文章的實際應用場景，2-3個）

---

文章標題：{title}

文章內容：
{truncated}

---

請用繁體中文回覆，格式要清晰。"""

    return call_minimax(prompt)


def add_ai_summary(bookmark, summary):
    path = Path(bookmark["path"])
    content = path.read_text(encoding="utf-8", errors="ignore")

    if "## 📌 一句話摘要" in content or "## 📝 AI 濃縮" in content:
        print("  ⏭️  跳過（已有摘要）")
        return False

    summary_block = f"\n\n---\n\n## 📝 AI 濃縮\n\n{summary}\n"
    path.write_text(content + summary_block, encoding="utf-8")
    return True


def add_cross_links(bookmarks):
    updated = 0
    for bookmark in bookmarks:
        related = find_related_bookmarks(bookmark, bookmarks)
        if not related:
            continue

        path = Path(bookmark["path"])
        content = path.read_text(encoding="utf-8", errors="ignore")
        if "## 🔗 相關書籤" in content:
            continue

        links_block = "\n\n## 🔗 相關書籤\n\n"
        for r in related:
            links_block += f"- [[{r['filename']}|{r['title']}]] ({', '.join(r['tags'])})\n"

        path.write_text(content + links_block, encoding="utf-8")
        updated += 1

    return updated


def process_bookmarks(limit=5, skip_ai=False):
    print("📚 書籤增強工具")
    print("=" * 50)

    bookmarks = get_all_bookmarks()
    print(f"✅ 找到 {len(bookmarks)} 個書籤")

    print("\n🔗 加入交叉連結...")
    updated = add_cross_links(bookmarks)
    print(f"✅ 已更新 {updated} 個書籤的交叉連結")

    if skip_ai:
        print("\n⏭️  跳過 AI 濃縮")
        return

    print("\n🤖 AI 濃縮處理...")
    count = 0
    for i, bookmark in enumerate(bookmarks[:limit]):
        print(f"\n[{i+1}/{limit}] {bookmark.get('title', '')[:40]}...")
        content = Path(bookmark["path"]).read_text(encoding="utf-8", errors="ignore")
        if "## 📝 AI 濃縮" in content or "## 📌 一句話摘要" in content:
            print("  ⏭️  跳過（已有摘要）")
            continue

        summary = generate_ai_summary(bookmark)
        if summary:
            add_ai_summary(bookmark, summary)
            print("  ✅ 已加入摘要")
            count += 1
        else:
            print("  ⚠️ 略過（API 未設定或回應失敗）")

        time.sleep(1)

    print(f"\n✅ 完成！已處理 {count} 個書籤")


if __name__ == "__main__":
    import sys
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    skip = "--skip-ai" in sys.argv
    process_bookmarks(limit=limit, skip_ai=skip)
