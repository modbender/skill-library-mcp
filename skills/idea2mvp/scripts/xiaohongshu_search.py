#!/usr/bin/env python3
"""
小红书笔记搜索 - Playwright 自动化浏览器搜索

流程：Playwright 启动浏览器 → 扫码登录 → 搜索关键词 → 点击进入笔记详情 → 提取完整内容
模拟真实用户行为：首页浏览 → 搜索 → 逐个点开感兴趣的笔记阅读 → 返回列表

使用方式：
  自动搜索（推荐）：
    python3 xiaohongshu_search.py --keyword "效率工具推荐"
    python3 xiaohongshu_search.py --keyword "AI工具推荐" --sort popularity_descending
    python3 xiaohongshu_search.py --keyword "宝藏app推荐" --limit 5

  从已有 JSON 解析（离线模式，不需要浏览器）：
    python3 xiaohongshu_search.py --input tmp/xhs_response.json

依赖：
  pip install playwright && python -m playwright install chromium

推荐关键词：效率工具推荐、好用的小众app、独立开发者 产品推荐、宝藏app推荐、AI工具推荐
"""

import argparse
import asyncio
import json
import os
import random
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = os.path.join(os.getcwd(), "tmp")
RESULT_FILE = os.path.join(TMP_DIR, "xhs_results.txt")
BROWSER_DATA_DIR = os.path.join(TMP_DIR, "xhs_browser_data")
XHS_HOME = "https://www.xiaohongshu.com"

SORT_MAP = {
    "general": "comprehensive_sort",
    "time_descending": "time_descending",
    "popularity_descending": "popularity_descending",
}

# ---------------------------------------------------------------------------
# Stealth 注入脚本
# ---------------------------------------------------------------------------

STEALTH_JS = """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
delete navigator.__proto__.webdriver;

Object.defineProperty(navigator, 'plugins', {
    get: () => {
        const p = [
            { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
            { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '' },
            { name: 'Native Client', filename: 'internal-nacl-plugin', description: '' },
        ];
        p.length = 3;
        return p;
    }
});

Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en-US', 'en'] });
Object.defineProperty(navigator, 'language', { get: () => 'zh-CN' });
Object.defineProperty(navigator, 'platform', { get: () => 'MacIntel' });

if (!window.chrome) {
    window.chrome = {
        runtime: {
            onMessage: { addListener: function(){}, removeListener: function(){} },
            sendMessage: function(){},
            connect: function(){ return { onMessage: { addListener: function(){} } }; },
        },
        loadTimes: function(){ return {}; },
        csi: function(){ return {}; },
    };
}

const origQuery = window.navigator.permissions?.query;
if (origQuery) {
    window.navigator.permissions.query = (p) => (
        p.name === 'notifications'
            ? Promise.resolve({ state: Notification.permission })
            : origQuery(p)
    );
}

const _getParam = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(p) {
    if (p === 37445) return 'Intel Inc.';
    if (p === 37446) return 'Intel Iris OpenGL Engine';
    return _getParam.call(this, p);
};

Object.defineProperty(navigator, 'connection', {
    get: () => ({ effectiveType: '4g', rtt: 50, downlink: 10, saveData: false })
});
Object.defineProperty(navigator, 'maxTouchPoints', { get: () => 0 });
Object.defineProperty(window, 'outerWidth', { get: () => window.innerWidth });
Object.defineProperty(window, 'outerHeight', { get: () => window.innerHeight + 85 });
"""

# ---------------------------------------------------------------------------
# 人类行为模拟
# ---------------------------------------------------------------------------

async def _human_delay(min_s=1.0, max_s=3.0):
    """随机等待，模拟人类思考/阅读时间。"""
    await asyncio.sleep(random.uniform(min_s, max_s))


async def _human_scroll_small(page, times=1):
    """轻微滚动，模拟阅读下滑。"""
    for _ in range(times):
        px = random.randint(200, 450)
        await page.evaluate(f"window.scrollBy(0, {px})")
        await _human_delay(1.5, 3.0)


async def _human_mouse_wander(page):
    """鼠标在页面中随意游走。"""
    try:
        vw = await page.evaluate("window.innerWidth")
        vh = await page.evaluate("window.innerHeight")
        for _ in range(random.randint(2, 3)):
            x = random.randint(100, max(200, vw - 100))
            y = random.randint(100, max(200, vh - 100))
            await page.mouse.move(x, y, steps=random.randint(5, 15))
            await _human_delay(0.2, 0.6)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Playwright 浏览器管理
# ---------------------------------------------------------------------------

async def _launch_browser():
    from playwright.async_api import async_playwright

    pw = await async_playwright().start()
    os.makedirs(BROWSER_DATA_DIR, exist_ok=True)

    vw = random.randint(1260, 1400)
    vh = random.randint(850, 950)

    context = await pw.chromium.launch_persistent_context(
        user_data_dir=BROWSER_DATA_DIR,
        headless=False,
        viewport={"width": vw, "height": vh},
        locale="zh-CN",
        timezone_id="Asia/Shanghai",
        user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
        ],
    )
    await context.add_init_script(STEALTH_JS)

    page = context.pages[0] if context.pages else await context.new_page()
    return pw, context, page


async def _check_logged_in(page):
    try:
        el = await page.query_selector('a[href*="/user/profile/"]')
        if el:
            return True
    except Exception:
        pass

    try:
        modal = await page.query_selector(
            '.login-container, [class*="login-modal"], .css-1yv5ss1'
        )
        if modal and await modal.is_visible():
            return False
    except Exception:
        pass

    cookies = await page.context.cookies()
    has_session = any(c["name"] == "web_session" and c["value"] for c in cookies)
    if has_session:
        try:
            btn = await page.query_selector('button:has-text("登录")')
            if btn and await btn.is_visible():
                return False
        except Exception:
            pass
        return True
    return False


async def _ensure_login(page, timeout=120):
    """检测登录，未登录则等待扫码。"""
    if await _check_logged_in(page):
        return True
    print("🔐 请在浏览器中扫码登录小红书...", file=sys.stderr, flush=True)
    print("   （打开手机小红书 APP，扫描浏览器中的二维码）", file=sys.stderr, flush=True)
    start = time.time()
    while time.time() - start < timeout:
        if await _check_logged_in(page):
            print("✅ 登录成功！", file=sys.stderr, flush=True)
            await _human_delay(2.0, 3.5)
            return True
        await asyncio.sleep(2)
    print("❌ 登录超时，请重新运行脚本", file=sys.stderr)
    return False


# ---------------------------------------------------------------------------
# 搜索页：用搜索框输入关键词（模拟真人）
# ---------------------------------------------------------------------------

async def _do_search_via_input(page, keyword):
    """通过页面搜索框输入关键词并搜索，模拟人类操作。"""
    # 点击搜索框
    search_input = await page.query_selector('#search-input, input[name="searchKeyword"], input[placeholder*="搜索"]')
    if not search_input:
        search_input = await page.query_selector('input')
    if not search_input:
        return False

    await search_input.click()
    await _human_delay(0.5, 1.0)

    # 清空已有内容
    await search_input.fill("")
    await _human_delay(0.3, 0.6)

    # 逐字输入，模拟打字
    for char in keyword:
        await search_input.type(char, delay=random.randint(80, 200))
        await asyncio.sleep(random.uniform(0.05, 0.15))

    await _human_delay(0.8, 1.5)

    # 按回车搜索
    await page.keyboard.press("Enter")
    await _human_delay(3.0, 5.0)
    return True


# ---------------------------------------------------------------------------
# 搜索列表页：提取笔记卡片的标题和链接
# ---------------------------------------------------------------------------

async def _get_note_cards_from_list(page):
    """从搜索结果列表中提取笔记卡片的基本信息（标题 + 链接）。"""
    cards = await page.evaluate("""
    () => {
        const results = [];
        // 小红书搜索结果页的笔记卡片
        const selectors = [
            'section.note-item a[href*="/explore/"]',
            'section.note-item a[href*="/search_result/"]',
            '[class*="note-item"] a[href*="/explore/"]',
            '[class*="note-item"] a[href*="/search_result/"]',
            'a[href*="/explore/"]',
        ];

        const seen = new Set();
        for (const sel of selectors) {
            document.querySelectorAll(sel).forEach(a => {
                const href = a.href || '';
                // 只要 explore 链接（笔记详情）
                const match = href.match(/\\/explore\\/([a-f0-9]+)/);
                if (!match) return;
                const noteId = match[1];
                if (seen.has(noteId)) return;
                seen.add(noteId);

                // 从卡片中提取标题
                const card = a.closest('section') || a.closest('[class*="note-item"]') || a.parentElement;
                let title = '';
                if (card) {
                    const titleEl = card.querySelector('.title, [class*="title"], span');
                    title = titleEl ? titleEl.textContent.trim() : '';
                }

                results.push({ id: noteId, title: title, url: href });
            });
            if (results.length > 0) break;
        }
        return results;
    }
    """)
    return cards


# ---------------------------------------------------------------------------
# 笔记详情页：提取完整内容
# ---------------------------------------------------------------------------

async def _extract_note_detail(page):
    """从笔记详情页（弹窗或独立页）提取完整信息。"""
    detail = await page.evaluate("""
    () => {
        const result = {};

        // 标题
        const titleSels = [
            '#detail-title', '.title', '[class*="title"]',
            'div.note-content .title',
        ];
        for (const sel of titleSels) {
            const el = document.querySelector(sel);
            if (el && el.textContent.trim()) {
                result.title = el.textContent.trim();
                break;
            }
        }

        // 正文内容
        const descSels = [
            '#detail-desc', '.desc', '[class*="desc"]',
            'div.note-content .desc', '[class*="note-text"]',
            '.note-scroller .content',
        ];
        for (const sel of descSels) {
            const el = document.querySelector(sel);
            if (el && el.textContent.trim().length > 10) {
                result.desc = el.textContent.trim();
                break;
            }
        }

        // 作者
        const authorSels = [
            '.author .name', '[class*="author"] .name',
            '.user-name', '[class*="username"]', '.nickname',
            '[class*="author-wrapper"] span',
        ];
        for (const sel of authorSels) {
            const el = document.querySelector(sel);
            if (el && el.textContent.trim()) {
                result.user = el.textContent.trim();
                break;
            }
        }

        // 互动数据（点赞、收藏、评论）
        const interactSels = [
            '[class*="like"] .count', '[class*="like"] span[class*="count"]',
            'span.like-wrapper .count',
        ];
        for (const sel of interactSels) {
            const el = document.querySelector(sel);
            if (el) { result.liked_count = el.textContent.trim(); break; }
        }

        const collectSels = [
            '[class*="collect"] .count', '[class*="collect"] span[class*="count"]',
        ];
        for (const sel of collectSels) {
            const el = document.querySelector(sel);
            if (el) { result.collected_count = el.textContent.trim(); break; }
        }

        const commentSels = [
            '[class*="chat"] .count', '[class*="comment"] .count',
        ];
        for (const sel of commentSels) {
            const el = document.querySelector(sel);
            if (el) { result.comment_count = el.textContent.trim(); break; }
        }

        // 标签
        const tags = [];
        document.querySelectorAll('#hash-tag a, a[href*="/search_result/?keyword="]').forEach(el => {
            const t = el.textContent.trim().replace(/^#/, '');
            if (t && t.length < 30 && !tags.includes(t)) tags.push(t);
        });
        result.tags = tags;

        // 发布时间
        const dateSels = ['.date', '[class*="date"]', 'span.time', '[class*="time"]'];
        for (const sel of dateSels) {
            const el = document.querySelector(sel);
            if (el && el.textContent.trim()) {
                result.date = el.textContent.trim();
                break;
            }
        }

        return result;
    }
    """)
    return detail


# ---------------------------------------------------------------------------
# 核心流程：搜索 → 逐个点开笔记详情
# ---------------------------------------------------------------------------

async def run_search(keyword, sort, limit):
    print("🚀 启动浏览器...", file=sys.stderr, flush=True)
    pw, context, page = await _launch_browser()

    try:
        # ① 打开首页
        print("🌐 打开小红书首页...", file=sys.stderr, flush=True)
        await page.goto(XHS_HOME, wait_until="domcontentloaded", timeout=30000)
        await _human_delay(2.5, 4.0)

        # ② 确保登录
        if not await _ensure_login(page):
            return None, None
        print("✅ 已登录", file=sys.stderr, flush=True)

        # ③ 在首页短暂浏览
        await _human_mouse_wander(page)
        await _human_delay(1.5, 3.0)

        # ④ 通过搜索框输入关键词搜索
        print(f"🔍 搜索: {keyword}...", file=sys.stderr, flush=True)
        searched = await _do_search_via_input(page, keyword)
        if not searched:
            # 备用：直接导航到搜索页
            sort_param = SORT_MAP.get(sort, "comprehensive_sort")
            url = f"{XHS_HOME}/search_result?keyword={keyword}&sort={sort_param}&type=1"
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await _human_delay(3.0, 5.0)

        # 如果搜索页触发登录，再次等待
        if not await _check_logged_in(page):
            if not await _ensure_login(page):
                return None, None
            searched = await _do_search_via_input(page, keyword)
            if not searched:
                sort_param = SORT_MAP.get(sort, "comprehensive_sort")
                url = f"{XHS_HOME}/search_result?keyword={keyword}&sort={sort_param}&type=1"
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await _human_delay(3.0, 5.0)

        # ⑤ 在搜索列表页轻微滚动（只滚一次，看第一屏即可）
        await _human_mouse_wander(page)
        await _human_scroll_small(page, times=1)

        # ⑥ 提取搜索列表中的笔记卡片
        cards = await _get_note_cards_from_list(page)
        if not cards:
            print("⚠️ 未找到搜索结果卡片", file=sys.stderr)
            return None, keyword

        # 只取需要的数量，避免过多访问
        target_count = min(limit, len(cards))
        print(f"📋 发现 {len(cards)} 条结果，将查看前 {target_count} 条详情...",
              file=sys.stderr, flush=True)

        # ⑦ 逐个点开笔记，提取详情，模拟人类 "点开→阅读→关闭→再看下一个"
        results = []
        for i, card in enumerate(cards[:target_count]):
            note_id = card.get("id", "")
            card_title = card.get("title", "")
            note_url = f"https://www.xiaohongshu.com/explore/{note_id}"

            print(f"  📖 ({i+1}/{target_count}) {card_title[:30] or note_id}...",
                  file=sys.stderr, flush=True)

            # 点击笔记卡片（小红书搜索页点击卡片会弹出详情弹窗）
            try:
                card_el = await page.query_selector(f'a[href*="/explore/{note_id}"]')
                if card_el:
                    await card_el.click()
                else:
                    # 找不到元素则直接导航
                    await page.goto(note_url, wait_until="domcontentloaded", timeout=20000)
            except Exception:
                await page.goto(note_url, wait_until="domcontentloaded", timeout=20000)

            await _human_delay(2.5, 4.5)

            # 在详情中模拟阅读：滚动 + 鼠标移动
            await _human_mouse_wander(page)
            await _human_scroll_small(page, times=random.randint(1, 2))
            await _human_delay(1.0, 2.5)

            # 提取详情
            detail = await _extract_note_detail(page)

            results.append({
                "id": note_id,
                "title": detail.get("title") or card_title or "",
                "desc": detail.get("desc", ""),
                "type": "normal",
                "user": detail.get("user", ""),
                "liked_count": detail.get("liked_count", "0"),
                "collected_count": detail.get("collected_count", "0"),
                "comment_count": detail.get("comment_count", "0"),
                "tags": detail.get("tags", []),
                "date": detail.get("date", ""),
                "url": note_url,
            })

            # 关闭详情弹窗（按 Escape 或点关闭按钮）返回搜索列表
            try:
                close_btn = await page.query_selector(
                    '[class*="close-circle"], .close-circle, button[class*="close"]'
                )
                if close_btn and await close_btn.is_visible():
                    await close_btn.click()
                else:
                    await page.keyboard.press("Escape")
            except Exception:
                await page.keyboard.press("Escape")

            await _human_delay(1.5, 3.0)

            # 确认回到搜索列表页（检查 URL）
            if "/search_result" not in page.url and "/explore" in page.url:
                await page.go_back(wait_until="domcontentloaded", timeout=15000)
                await _human_delay(2.0, 3.5)

        return results, keyword

    finally:
        await context.close()
        await pw.stop()


# ---------------------------------------------------------------------------
# 结果格式化
# ---------------------------------------------------------------------------

def format_as_text(notes, keyword):
    lines = [f'小红书搜索 - "{keyword}"', "=" * 50, ""]

    for i, n in enumerate(notes, 1):
        title = n.get("title") or "(无标题)"
        desc = n.get("desc", "")
        if len(desc) > 300:
            desc = desc[:300] + "..."
        tags = ", ".join(n.get("tags", [])[:8])
        liked = n.get("liked_count", "0")
        collected = n.get("collected_count", "0")
        comments = n.get("comment_count", "0")
        date = n.get("date", "")

        lines.append(f"#{i} {title}")
        lines.append(f"  ❤️ {liked}  ⭐ {collected}  💬 {comments}")
        if desc:
            lines.append(f"  {desc}")
        lines.append(f"  作者: {n.get('user') or '未知'}")
        if tags:
            lines.append(f"  标签: {tags}")
        if date:
            lines.append(f"  时间: {date}")
        if n.get("url"):
            lines.append(f"  {n['url']}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 离线 JSON 解析（兼容旧模式）
# ---------------------------------------------------------------------------

def parse_notes_from_json(data):
    notes = []
    if not data or not isinstance(data, dict):
        return notes
    items = data.get("data", {}).get("items", [])
    if not items:
        items = data.get("items", [])
    for item in items:
        nc = item.get("note_card") or item.get("noteCard") or item
        if not nc:
            continue
        user = nc.get("user", {})
        interact = nc.get("interact_info", {})
        tag_list = nc.get("tag_list", [])
        nid = item.get("id", nc.get("note_id", nc.get("id", "")))
        notes.append({
            "id": nid,
            "title": nc.get("display_title", nc.get("title", "")),
            "desc": nc.get("desc", ""),
            "type": nc.get("type", ""),
            "user": user.get("nickname", user.get("nick_name", "")) if isinstance(user, dict) else str(user),
            "liked_count": interact.get("liked_count", "0") if isinstance(interact, dict) else "0",
            "collected_count": "0",
            "comment_count": "0",
            "tags": [t.get("name", "") for t in tag_list if t.get("name")] if tag_list else [],
            "date": "",
            "url": f"https://www.xiaohongshu.com/explore/{nid}" if nid else "",
        })
    return notes


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="小红书笔记搜索（Playwright 自动化）")
    parser.add_argument("--keyword", type=str, default="效率工具推荐", help="搜索关键词")
    parser.add_argument("--sort", type=str, default="general",
                        choices=["general", "time_descending", "popularity_descending"],
                        help="排序: general / time_descending / popularity_descending")
    parser.add_argument("--limit", type=int, default=5, help="查看笔记详情的数量（默认 5）")
    parser.add_argument("--input", type=str, default=None, help="从 JSON 文件解析（离线模式）")
    args = parser.parse_args()

    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            try:
                data = json.loads(f.read())
            except json.JSONDecodeError as e:
                print(f"❌ JSON 解析失败: {e}", file=sys.stderr)
                sys.exit(1)
        notes = parse_notes_from_json(data)[:args.limit]
        keyword = args.keyword
    else:
        try:
            from playwright.async_api import async_playwright  # noqa: F401
        except ImportError:
            print(
                "❌ 缺少 playwright，请运行: "
                "pip install playwright && python -m playwright install chromium",
                file=sys.stderr,
            )
            sys.exit(1)

        notes, keyword = asyncio.run(run_search(args.keyword, args.sort, args.limit))
        if not notes:
            sys.exit(1)

    if not notes:
        print(f"💡 未找到 '{args.keyword}' 相关笔记", file=sys.stderr)
        sys.exit(1)

    text = format_as_text(notes, keyword)
    os.makedirs(TMP_DIR, exist_ok=True)
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    print(f"\n📄 结果已保存到 {RESULT_FILE}", file=sys.stderr)


if __name__ == "__main__":
    main()
