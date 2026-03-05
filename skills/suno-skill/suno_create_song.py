#!/usr/bin/env python3
"""
Suno 歌曲创建工具 - 使用 hcaptcha-challenger 自动解决验证码

核心流程:
1. 使用已登录的 persistent context 打开 suno.com/create
2. 切换到 Custom 模式，填写歌词/风格/标题
3. 点击 Create → 触发 hCaptcha
4. 使用 hcaptcha-challenger + Gemini API 自动解决 hCaptcha
5. 通过 API 轮询歌曲状态并下载

前置条件:
- 已运行 suno_login.py 完成登录
- 需要 Gemini API Key: https://aistudio.google.com/app/apikey
- pip install hcaptcha-challenger playwright

用法:
    export GEMINI_API_KEY="your_key_here"
    python suno_create_song.py --lyrics "歌词" --style "rock" --title "歌名"
"""
import asyncio
import json
import os
import sys
import time
import re
import argparse
import requests
from playwright.async_api import async_playwright
from hcaptcha_challenger import AgentConfig, AgentV

USER_DATA_DIR = os.path.expanduser("~/.suno/chrome_gui_profile")

# ====== 确保 hcaptcha-challenger 支持 Suno 自定义 hCaptcha 域名 ======
# Suno 使用 hcaptcha-assets-prod.suno.com 而非标准 newassets.hcaptcha.com
# patch_hcaptcha.py 已修改源文件，这里做运行时双保险
try:
    from hcaptcha_challenger.agent.challenger import RoboticArm
    _orig_init = RoboticArm.__init__

    def _patched_init(self, *args, **kwargs):
        _orig_init(self, *args, **kwargs)
        # 替换 XPath 选择器为通用匹配（支持 checkbox-invisible 和 checkbox）
        self._checkbox_selector = "//iframe[contains(@src, '/captcha/v1/') and (contains(@src, 'frame=checkbox') or contains(@src, 'frame=checkbox-invisible'))]"
        self._challenge_selector = "//iframe[contains(@src, '/captcha/v1/') and contains(@src, 'frame=challenge')]"

    RoboticArm.__init__ = _patched_init

    print("   ✅ hCaptcha 域名兼容 patch 已应用", flush=True)
except Exception as e:
    print(f"   ⚠️ hCaptcha patch 跳过: {e}", flush=True)
# ====== Patch 结束 ======
DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output_mp3")
SUNO_API_BASE = "https://studio-api.prod.suno.com"


def download_mp3(audio_url, title, clip_id, output_dir):
    """下载 MP3 文件"""
    os.makedirs(output_dir, exist_ok=True)
    safe_title = re.sub(r'[^\w\u4e00-\u9fff\-]', '_', title)
    filename = f"{safe_title}_{clip_id[:8]}.mp3"
    filepath = os.path.join(output_dir, filename)

    print(f"   📥 下载: {filename}", flush=True)
    resp = requests.get(audio_url, stream=True, timeout=120)
    resp.raise_for_status()
    with open(filepath, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    size_mb = os.path.getsize(filepath) / 1024 / 1024
    print(f"   ✅ 已保存: {filepath} ({size_mb:.1f} MB)", flush=True)
    return filepath


async def create_song(lyrics: str, style: str, title: str, output_dir: str, gemini_key: str):
    """
    完整的歌曲创建流程（含 hCaptcha 自动解决）
    """
    os.makedirs(output_dir, exist_ok=True)

    # 配置 hcaptcha-challenger
    agent_config = AgentConfig(
        GEMINI_API_KEY=gemini_key,
        EXECUTION_TIMEOUT=180,  # 3 分钟超时
        RESPONSE_TIMEOUT=60,
        RETRY_ON_FAILURE=True,
    )

    async with async_playwright() as p:
        print("\n🚀 启动 Chrome (headless=False)...", flush=True)
        context = await p.chromium.launch_persistent_context(
            USER_DATA_DIR,
            channel="chrome",
            headless=False,
            viewport={"width": 1380, "height": 900},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
            ignore_default_args=["--enable-automation"],
        )
        await context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
        )
        page = context.pages[0] if context.pages else await context.new_page()

        # 记录新生成的 clip（只跟踪 generate API 的响应）
        new_clip_ids = []

        async def on_response(response):
            url = response.url
            method = response.request.method
            # 只关注 generate API 的 POST 响应
            if method == "POST" and "studio-api" in url and "generate" in url:
                try:
                    data = await response.json()
                    clips = data.get("clips", [])
                    if clips:
                        for c in clips:
                            cid = c.get("id")
                            if cid and cid not in new_clip_ids:
                                new_clip_ids.append(cid)
                        print(f"\n   📡 生成任务已提交！{len(clips)} 首歌曲", flush=True)
                        for c in clips:
                            print(f"      ID: {c.get('id')}, Status: {c.get('status')}", flush=True)
                except:
                    pass

        page.on("response", on_response)

        # ========== 步骤 1: 打开创建页面 ==========
        print("\n📌 步骤 1: 打开创建页面...", flush=True)
        await page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(5000)

        if "sign-in" in page.url:
            print("❌ 未登录！请先运行 suno_login.py", flush=True)
            await context.close()
            return None

        print(f"   ✅ 已登录", flush=True)

        # ========== 步骤 2: 切换到 Custom 模式 ==========
        print("📌 步骤 2: 切换到 Custom 模式...", flush=True)
        try:
            await page.locator('button:has-text("Custom")').first.click(timeout=5000)
            await page.wait_for_timeout(1500)
            print("   ✅ 已切换", flush=True)
        except:
            print("   ℹ️ 可能已在 Custom 模式", flush=True)

        # ========== 步骤 3: 填写歌词 ==========
        print("📌 步骤 3: 填写歌词...", flush=True)
        try:
            lyrics_input = page.locator('textarea[placeholder*="Write some lyrics"]').first
            await lyrics_input.click()
            await page.wait_for_timeout(300)
            await lyrics_input.fill(lyrics)
            print(f"   ✅ 已填写歌词 ({len(lyrics)} 字)", flush=True)
        except Exception as e:
            print(f"   ❌ 填写歌词失败: {e}", flush=True)
            await context.close()
            return None

        # ========== 步骤 4: 填写风格标签 ==========
        print("📌 步骤 4: 填写风格标签...", flush=True)
        try:
            # 尝试多种选择器
            style_input = None
            for sel in ['textarea[placeholder*="touhou"]', 'textarea[placeholder*="Style"]']:
                try:
                    el = page.locator(sel).first
                    if await el.is_visible(timeout=2000):
                        style_input = el
                        break
                except:
                    continue
            if not style_input:
                textareas = page.locator("textarea")
                count = await textareas.count()
                if count >= 2:
                    style_input = textareas.nth(1)
            if style_input:
                await style_input.click()
                await page.wait_for_timeout(300)
                await style_input.fill("")
                await page.wait_for_timeout(200)
                await style_input.fill(style)
                print(f"   ✅ 已填写风格: {style}", flush=True)
        except Exception as e:
            print(f"   ⚠️ 填写风格失败: {e}", flush=True)

        # ========== 步骤 5: 填写标题 ==========
        print("📌 步骤 5: 填写标题...", flush=True)
        try:
            # 标题输入框可能被折叠/隐藏，先尝试展开
            try:
                toggle = page.locator('button:has-text("Title"), [data-testid*="title"]').first
                if await toggle.is_visible(timeout=2000):
                    await toggle.click()
                    await page.wait_for_timeout(500)
            except:
                pass
            title_input = page.locator('input[placeholder="Song Title (Optional)"]').first
            # 通过 JS 直接设置值（绕过 visibility 问题）
            await page.evaluate("""(title) => {
                const inputs = document.querySelectorAll('input[placeholder="Song Title (Optional)"]');
                if (inputs.length > 0) {
                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    nativeInputValueSetter.call(inputs[0], title);
                    inputs[0].dispatchEvent(new Event('input', { bubbles: true }));
                    inputs[0].dispatchEvent(new Event('change', { bubbles: true }));
                }
            }""", title)
            print(f"   ✅ 已填写标题: {title}", flush=True)
        except Exception as e:
            print(f"   ⚠️ 填写标题失败（非关键）: {e}", flush=True)

        await page.wait_for_timeout(1000)

        # ========== 步骤 6: 初始化 hCaptcha 解决器 ==========
        print("📌 步骤 6: 初始化 hCaptcha 解决器...", flush=True)
        agent = AgentV(page=page, agent_config=agent_config)
        print("   ✅ hcaptcha-challenger 已就绪", flush=True)

        # ========== 步骤 7: 点击 Create 按钮 ==========
        print("📌 步骤 7: 点击 Create...", flush=True)
        all_create_btns = page.locator("button").filter(has_text="Create")
        count = await all_create_btns.count()
        print(f"   找到 {count} 个 Create 按钮", flush=True)

        target_btn = None
        for idx in range(count):
            btn = all_create_btns.nth(idx)
            text = (await btn.text_content()).strip()
            box = await btn.bounding_box()
            if box:
                print(f"   [{idx}] '{text[:30]}' at x={box['x']:.0f}, y={box['y']:.0f}, w={box['width']:.0f}", flush=True)
                if box["width"] > 50 and box["y"] > 200:
                    target_btn = btn

        if target_btn:
            await target_btn.click()
            print("   ✅ 已点击 Create", flush=True)
        elif count > 0:
            await all_create_btns.last.click()
            print("   ✅ 已点击最后一个 Create", flush=True)
        else:
            print("   ❌ 没找到 Create 按钮", flush=True)
            await context.close()
            return None

        # ========== 步骤 8: 自动解决 hCaptcha ==========
        print("\n🔒 步骤 8: 等待并解决 hCaptcha...", flush=True)
        print("   （hcaptcha-challenger 将使用 Gemini API 识别图片）", flush=True)

        # 步骤 8a: 等待 hCaptcha checkbox iframe 出现
        print("   🔍 等待 hCaptcha checkbox 出现...", flush=True)
        checkbox_clicked = False
        for wait_i in range(15):  # 最多等 30 秒
            await page.wait_for_timeout(2000)
            # 检查是否有 hCaptcha checkbox iframe
            frames_info = await page.evaluate("""() => {
                return Array.from(document.querySelectorAll('iframe')).map(f => ({
                    src: f.src || '',
                    width: f.offsetWidth,
                    height: f.offsetHeight,
                    visible: f.offsetHeight > 0
                }));
            }""")
            captcha_frames = [f for f in frames_info if '/captcha/v1/' in f.get('src', '') and f.get('visible')]
            if captcha_frames:
                print(f"   ✅ [{(wait_i+1)*2}s] 发现 {len(captcha_frames)} 个 hCaptcha frame", flush=True)
                for cf in captcha_frames:
                    print(f"      {cf['src'][:80]} ({cf['width']}x{cf['height']})", flush=True)

                # 找到 checkbox iframe 并点击
                for frame in page.frames:
                    if '/captcha/v1/' in frame.url and 'frame=checkbox' in frame.url:
                        try:
                            checkbox = frame.locator('#checkbox')
                            if await checkbox.is_visible(timeout=3000):
                                await checkbox.click()
                                checkbox_clicked = True
                                print("   ✅ 已点击 hCaptcha checkbox", flush=True)
                                await page.wait_for_timeout(3000)
                                break
                        except Exception as e:
                            print(f"   ⚠️ 点击 checkbox 失败: {e}", flush=True)
                break
            else:
                # 可能 hCaptcha 不需要（某些情况下 Suno 不弹验证码）
                if new_clip_ids:
                    print(f"   ✅ 无需验证码，generate API 已返回", flush=True)
                    break
                print(f"   ⏳ [{(wait_i+1)*2}s] 等待 hCaptcha...", flush=True)

        if not checkbox_clicked and not new_clip_ids:
            print("   ⚠️ 未检测到 hCaptcha checkbox，尝试继续...", flush=True)
            # 截图诊断
            await page.screenshot(path="/tmp/suno_no_captcha.png")

        # 步骤 8b: 使用 hcaptcha-challenger 解决图片验证
        if checkbox_clicked:
            try:
                signal = await agent.wait_for_challenge()
                print(f"   🔒 hCaptcha 结果: {signal}", flush=True)
                if "SUCCESS" in str(signal):
                    print("   ✅ hCaptcha 已解决！", flush=True)
                else:
                    print(f"   ⚠️ hCaptcha 结果: {signal}（可能需要重试）", flush=True)
            except Exception as e:
                print(f"   ⚠️ hCaptcha 处理异常: {e}", flush=True)
                print("   ℹ️ 继续等待，可能验证码已自动通过...", flush=True)
        elif not new_clip_ids:
            # 没有 checkbox 也没有 clip，尝试直接调用 wait_for_challenge
            try:
                signal = await agent.wait_for_challenge()
                print(f"   🔒 hCaptcha 结果: {signal}", flush=True)
            except Exception as e:
                print(f"   ⚠️ {e}", flush=True)

        # ========== 步骤 9: 等待歌曲生成 ==========
        print("\n⏳ 步骤 9: 等待歌曲生成任务提交...", flush=True)

        # 如果 hCaptcha 通过后 generate API 还没被调用，等一会
        for i in range(12):
            await page.wait_for_timeout(5000)
            elapsed = (i + 1) * 5
            if new_clip_ids:
                print(f"   ✅ [{elapsed}s] 捕获到 {len(new_clip_ids)} 个新 clip!", flush=True)
                break
            print(f"   ⏳ [{elapsed}s] 等待 generate API 响应...", flush=True)

        if not new_clip_ids:
            print("   ❌ 未捕获到新的 clip（generate API 可能未被调用）", flush=True)
            await page.screenshot(path="/tmp/suno_no_new_clips.png")
            await context.close()
            return None

        # ========== 步骤 10: 通过 API 轮询歌曲状态 ==========
        print(f"\n📡 步骤 10: 轮询 clip 状态: {new_clip_ids}", flush=True)

        # 获取 token
        token = await page.evaluate("""async () => {
            if (window.Clerk && window.Clerk.session) {
                return await window.Clerk.session.getToken();
            }
            return null;
        }""")

        if not token:
            print("   ⚠️ 无法获取 token", flush=True)
            await context.close()
            return None

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Referer": "https://suno.com/",
            "Origin": "https://suno.com",
        }

        completed = {}
        for attempt in range(36):  # 最多等 3 分钟
            await page.wait_for_timeout(5000)
            elapsed = (attempt + 1) * 5

            # 每 60 秒刷新 token
            if elapsed % 60 == 0:
                new_token = await page.evaluate("""async () => {
                    if (window.Clerk && window.Clerk.session) {
                        return await window.Clerk.session.getToken();
                    }
                    return null;
                }""")
                if new_token:
                    token = new_token
                    headers["Authorization"] = f"Bearer {token}"

            ids_str = ",".join(new_clip_ids)
            try:
                resp = requests.get(
                    f"{SUNO_API_BASE}/api/feed/?ids={ids_str}",
                    headers=headers,
                    timeout=15,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    items = data if isinstance(data, list) else [data]
                    for item in items:
                        cid = item.get("id")
                        status = item.get("status", "unknown")
                        audio_url = item.get("audio_url", "")

                        if status == "complete" and audio_url and cid not in completed:
                            print(f"   ✅ [{elapsed}s] {cid}: 完成!", flush=True)
                            completed[cid] = item
                        elif status == "error":
                            print(f"   ❌ [{elapsed}s] {cid}: 生成失败", flush=True)
                            err = item.get("metadata", {}).get("error_message", "")
                            if err:
                                print(f"      错误: {err}", flush=True)
                            completed[cid] = item
                        elif cid not in completed:
                            print(f"   ⏳ [{elapsed}s] {cid}: {status}", flush=True)
            except Exception as e:
                print(f"   ⚠️ [{elapsed}s] 查询失败: {e}", flush=True)

            if len(completed) >= len(new_clip_ids):
                break

        # ========== 步骤 11: 下载 ==========
        downloaded = []
        if completed:
            print(f"\n📥 步骤 11: 下载歌曲...", flush=True)
            for cid, clip in completed.items():
                audio_url = clip.get("audio_url", "")
                if audio_url:
                    clip_title = clip.get("title") or title
                    try:
                        filepath = download_mp3(audio_url, clip_title, cid, output_dir)
                        downloaded.append(filepath)
                    except Exception as e:
                        print(f"   ❌ 下载失败: {e}", flush=True)

        await context.close()

        if downloaded:
            print(f"\n{'='*60}", flush=True)
            print(f"🎉 完成！已下载 {len(downloaded)} 首歌曲：", flush=True)
            for f in downloaded:
                print(f"   📁 {f}", flush=True)
            print(f"{'='*60}", flush=True)
        else:
            print("\n❌ 没有歌曲被下载", flush=True)

        return downloaded


def main():
    parser = argparse.ArgumentParser(description="Suno 歌曲创建工具（含 hCaptcha 自动解决）")
    parser.add_argument("--lyrics", type=str, help="歌词内容")
    parser.add_argument("--lyrics-file", type=str, help="歌词文件路径")
    parser.add_argument("--style", type=str, default="rock, electric guitar, energetic, male vocals",
                        help="音乐风格标签")
    parser.add_argument("--title", type=str, default="My Song", help="歌曲标题")
    parser.add_argument("--output-dir", type=str, default=DOWNLOAD_DIR, help="下载目录")
    parser.add_argument("--gemini-key", type=str, default=os.environ.get("GEMINI_API_KEY", ""),
                        help="Gemini API Key（或设置 GEMINI_API_KEY 环境变量）")
    args = parser.parse_args()

    # 读取歌词
    if args.lyrics_file:
        with open(args.lyrics_file, "r") as f:
            lyrics = f.read().strip()
    elif args.lyrics:
        lyrics = args.lyrics
    else:
        print("❌ 请提供 --lyrics 或 --lyrics-file", flush=True)
        sys.exit(1)

    # 检查 Gemini API Key
    gemini_key = args.gemini_key
    if not gemini_key:
        # 尝试从 ~/.suno/.env 读取
        env_file = os.path.expanduser("~/.suno/.env")
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY="):
                        gemini_key = line.strip().split("=", 1)[1]
                        break
    if not gemini_key:
        print("❌ 未设置 Gemini API Key！hCaptcha 无法自动解决", flush=True)
        print("   设置方法 1: export GEMINI_API_KEY='your_key'", flush=True)
        print("   设置方法 2: echo 'GEMINI_API_KEY=your_key' > ~/.suno/.env", flush=True)
        print("   获取地址: https://aistudio.google.com/app/apikey", flush=True)
        sys.exit(1)

    print("=" * 60, flush=True)
    print("🎵 Suno 歌曲创建工具", flush=True)
    print(f"   标题: {args.title}", flush=True)
    print(f"   风格: {args.style}", flush=True)
    print(f"   歌词: {lyrics[:60]}{'...' if len(lyrics)>60 else ''}", flush=True)
    print(f"   Gemini Key: {'已设置' if gemini_key else '未设置'}", flush=True)
    print("=" * 60, flush=True)

    result = asyncio.run(create_song(lyrics, args.style, args.title, args.output_dir, gemini_key))
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
