#!/usr/bin/env python3
"""
Suno 歌曲创建工具 (Headless Linux 版) - 使用 hcaptcha-challenger 自动解决验证码

核心流程:
1. 使用已登录的 persistent context 打开 suno.com/create
2. 切换到 Custom 模式，填写歌词/风格/标题
3. 点击 Create → 触发 hCaptcha
4. 使用 hcaptcha-challenger + Gemini API 自动解决 hCaptcha
5. 通过 API 轮询歌曲状态并下载

与原版的区别:
- ✅ 自动检测 Linux 无 GUI 环境并启动 Xvfb 虚拟显示
- ✅ 适配无图形界面的云服务器 / Docker 容器
- ✅ 需要安装: apt install -y xvfb && pip install PyVirtualDisplay

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
import platform
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


# ====== Headless Linux 支持 ======
def _is_headless_linux():
    """检测是否在无 GUI 的 Linux 环境"""
    if platform.system() != "Linux":
        return False
    return not os.environ.get("DISPLAY")


def _setup_virtual_display():
    """
    在 Linux 无 GUI 环境下创建虚拟显示（Xvfb）
    返回 display 对象（需要在结束时 stop）
    """
    try:
        from pyvirtualdisplay import Display
        display = Display(visible=0, size=(1380, 900))
        display.start()
        print("   ✅ Xvfb 虚拟显示已启动 (1380x900)", flush=True)
        return display
    except ImportError:
        print("   ❌ 未安装 PyVirtualDisplay!", flush=True)
        print("   💡 安装方法: sudo apt install -y xvfb && pip install PyVirtualDisplay", flush=True)
        return None
    except Exception as e:
        print(f"   ❌ Xvfb 启动失败: {e}", flush=True)
        print("   💡 请确保已安装 xvfb: sudo apt install -y xvfb", flush=True)
        return None
# ====== Headless Linux 支持结束 ======


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
    支持 Linux 无 GUI 环境（自动启动 Xvfb 虚拟显示）
    """
    os.makedirs(output_dir, exist_ok=True)

    # 配置 hcaptcha-challenger
    agent_config = AgentConfig(
        GEMINI_API_KEY=gemini_key,
        EXECUTION_TIMEOUT=180,  # 3 分钟超时
        RESPONSE_TIMEOUT=60,
        RETRY_ON_FAILURE=True,
    )

    # ====== 检测并启动虚拟显示 ======
    virtual_display = None
    if _is_headless_linux():
        print("\n🖥️ 检测到 Linux 无 GUI 环境，启动 Xvfb 虚拟显示...", flush=True)
        virtual_display = _setup_virtual_display()
        if virtual_display is None:
            print("❌ 无法启动虚拟显示，无法在无 GUI 环境下运行", flush=True)
            return None

    try:
        async with async_playwright() as p:
            print("\n🚀 启动 Chrome (headless=False, Xvfb={})...".format(
                "已启用" if virtual_display else "不需要"
            ), flush=True)
            # Nutze Playwright's Chromium (kein channel='chrome' - braucht echtes Google Chrome)
            context = await p.chromium.launch_persistent_context(
                USER_DATA_DIR,
                headless=False,
                viewport={"width": 1380, "height": 900},
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
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
            await page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(5000)

            if "sign-in" in page.url:
                print("❌ 未登录！请先运行 suno_login.py", flush=True)
                await context.close()
                return None

            print(f"   ✅ 已登录", flush=True)

            # ========== 步骤 2: 切换到 Custom 模式 ==========
            print("📌 步骤 2: 切换到 Custom 模式...", flush=True)
            custom_switched = False
            
            # 先截图看当前页面状态
            await page.screenshot(path="/tmp/suno_debug_before_custom.png")
            print("   📸 已保存切换前截图: /tmp/suno_debug_before_custom.png", flush=True)
            
            # 多种选择器尝试切换 Custom 模式
            custom_selectors = [
                'button:has-text("Custom")',
                'button:has-text("custom")',
                '[data-testid*="custom"]',
                '[role="tab"]:has-text("Custom")',
                # Suno 可能使用 switch/toggle 而非 button
                '[role="switch"]:has-text("Custom")',
                'label:has-text("Custom")',
                'div[role="button"]:has-text("Custom")',
            ]
            for sel in custom_selectors:
                try:
                    btn = page.locator(sel).first
                    if await btn.is_visible(timeout=3000):
                        await btn.click()
                        custom_switched = True
                        print(f"   ✅ 已点击 Custom 按钮 (via {sel})", flush=True)
                        await page.wait_for_timeout(2000)
                        break
                except Exception:
                    continue

            if not custom_switched:
                # 尝试用 JS 搜索所有包含 "Custom" 文字的可点击元素
                print("   ⚠️ 常规选择器未找到，尝试 JS 搜索...", flush=True)
                js_clicked = await page.evaluate("""() => {
                    const all = document.querySelectorAll('button, [role=tab], [role=button], [role=switch], label, a, div[class*=tab], div[class*=toggle]');
                    for (const el of all) {
                        const text = (el.textContent || '').trim();
                        if (text === 'Custom' || text === 'custom') {
                            console.log('Found Custom element:', el.tagName, el.className);
                            el.click();
                            return {found: true, tag: el.tagName, cls: el.className.substring(0, 80)};
                        }
                    }
                    return {found: false};
                }""")
                if js_clicked.get('found'):
                    custom_switched = True
                    print(f"   ✅ 通过 JS 点击了 Custom ({js_clicked.get('tag')}.{js_clicked.get('cls', '')[:30]})", flush=True)
                    await page.wait_for_timeout(2000)
                else:
                    print("   ⚠️ 未找到 Custom 按钮！当前可能是 Song Description 模式", flush=True)
                    # 打印所有可见按钮帮助诊断
                    buttons_info = await page.evaluate("""() => {
                        const btns = document.querySelectorAll('button, [role=tab], [role=button]');
                        return Array.from(btns).filter(b => b.offsetHeight > 0).map(b => ({
                            text: (b.textContent || '').trim().substring(0, 40),
                            tag: b.tagName,
                            cls: b.className.substring(0, 60)
                        }));
                    }""")
                    print(f"   📋 页面上可见的按钮/tab:", flush=True)
                    for bi in buttons_info[:15]:
                        print(f"      [{bi['tag']}] '{bi['text']}' class='{bi['cls']}'", flush=True)
            
            # 截图看切换后状态
            await page.wait_for_timeout(1000)
            await page.screenshot(path="/tmp/suno_debug_after_custom.png")
            print("   📸 已保存切换后截图: /tmp/suno_debug_after_custom.png", flush=True)

            # 等待 Custom 模式的 UI 完全加载
            # Custom 模式应该有 "Lyrics" 相关的 textarea，而非 Song Description
            print("   ⏳ 等待 Custom 模式 UI 加载...", flush=True)
            lyrics_textarea_found = False
            for wait_i in range(15):  # 最多等 30 秒
                await page.wait_for_timeout(2000)
                # 检查是否有歌词相关的 textarea（Custom 模式特征）
                ta_info = await page.evaluate("""() => {
                    const tas = document.querySelectorAll('textarea');
                    return Array.from(tas).map(t => ({
                        placeholder: t.placeholder || '',
                        rows: t.rows,
                        height: t.offsetHeight,
                        visible: t.offsetHeight > 0
                    }));
                }""")
                visible_tas = [t for t in ta_info if t['visible']]
                
                if len(visible_tas) >= 2:
                    # Custom 模式通常有 2 个以上 textarea（歌词 + 风格）
                    print(f"   ✅ Custom UI 已加载 (发现 {len(visible_tas)} 个可见 textarea, 耗时 {(wait_i+1)*2}s)", flush=True)
                    for idx, t in enumerate(visible_tas):
                        print(f"      textarea[{idx}]: h={t['height']} placeholder='{t['placeholder'][:50]}'", flush=True)
                    lyrics_textarea_found = True
                    break
                elif len(visible_tas) == 1:
                    # 只有 1 个 textarea，可能还在 Song Description 模式！
                    ph = visible_tas[0].get('placeholder', '')
                    # 如果 placeholder 包含歌词相关的词，说明已经是 Custom 模式
                    if any(kw in ph.lower() for kw in ['lyric', 'verse', 'write your']):
                        print(f"   ✅ Custom UI 已加载 (1个歌词 textarea, placeholder='{ph[:50]}', 耗时 {(wait_i+1)*2}s)", flush=True)
                        lyrics_textarea_found = True
                        break
                    else:
                        print(f"   ⏳ [{(wait_i+1)*2}s] 只有1个 textarea (placeholder='{ph[:40]}')，可能还在 Description 模式", flush=True)
                        # 再尝试点一次 Custom
                        if wait_i == 3:  # 第 8 秒时再试一次
                            print("   🔄 再次尝试点击 Custom...", flush=True)
                            for sel in custom_selectors:
                                try:
                                    btn = page.locator(sel).first
                                    if await btn.is_visible(timeout=1000):
                                        await btn.click()
                                        print(f"   ✅ 再次点击 Custom (via {sel})", flush=True)
                                        break
                                except Exception:
                                    continue
                else:
                    print(f"   ⏳ [{(wait_i+1)*2}s] 等待 textarea 出现... (当前: {len(visible_tas)}个)", flush=True)
            
            if not lyrics_textarea_found:
                print("   ⚠️ 等待 textarea 超时！截图诊断...", flush=True)
                await page.screenshot(path="/tmp/suno_debug_no_textarea.png")
                try:
                    html_snippet = await page.evaluate("document.body.innerHTML.substring(0, 2000)")
                    print(f"   📄 页面 HTML 片段: {html_snippet[:500]}", flush=True)
                except Exception:
                    pass

            # ========== 步骤 3: 填写歌词 ==========
            print("📌 步骤 3: 填写歌词...", flush=True)
            try:
                # 先收集页面上所有 textarea 的详细信息（包括它所在的 section 标题）
                all_ta_info = await page.evaluate("""() => {
                    const tas = document.querySelectorAll('textarea');
                    return Array.from(tas).map((t, i) => {
                        // 向上查找最近的 section 标题文字（Lyrics / Styles 等）
                        let sectionTitle = '';
                        let el = t;
                        for (let depth = 0; depth < 10; depth++) {
                            el = el.parentElement;
                            if (!el) break;
                            // 查找同级或子元素中的标题/按钮文字
                            const headers = el.querySelectorAll('h1,h2,h3,h4,h5,h6,button,span,label,p');
                            for (const h of headers) {
                                const txt = (h.textContent || '').trim();
                                if (['Lyrics', 'Styles', 'Style', 'Title', 'Song Description'].includes(txt)) {
                                    sectionTitle = txt;
                                    break;
                                }
                            }
                            if (sectionTitle) break;
                        }
                        return {
                            index: i,
                            placeholder: t.placeholder || '',
                            sectionTitle: sectionTitle,
                            visible: t.offsetHeight > 0,
                            height: t.offsetHeight,
                            width: t.offsetWidth,
                            value: t.value || ''
                        };
                    });
                }""")
                print(f"   📋 页面上共 {len(all_ta_info)} 个 textarea:", flush=True)
                for info in all_ta_info:
                    print(f"      [{info['index']}] {info['width']}x{info['height']} section='{info['sectionTitle']}' placeholder='{info['placeholder'][:60]}' visible={info['visible']}", flush=True)

                textareas = page.locator("textarea")
                lyrics_input = None
                lyrics_ta_index = -1

                # ===== 策略 1（最可靠）: 通过 section 标题 "Lyrics" 定位 =====
                for info in all_ta_info:
                    if info['visible'] and info['sectionTitle'] == 'Lyrics':
                        lyrics_input = textareas.nth(info['index'])
                        lyrics_ta_index = info['index']
                        print(f"   🔍 通过 section 标题 'Lyrics' 找到歌词 textarea[{info['index']}]", flush=True)
                        break

                # ===== 策略 2: 精确匹配 placeholder 中的关键词 =====
                if not lyrics_input:
                    lyrics_placeholder_keywords = [
                        "lyrics", "Lyrics", "Write some lyrics",
                        "Write your", "write your", "prompt",
                        "verse", "Verse", "歌词", "instrumental"
                    ]
                    for kw in lyrics_placeholder_keywords:
                        try:
                            el = page.locator(f'textarea[placeholder*="{kw}"]').first
                            if await el.is_visible(timeout=2000):
                                lyrics_input = el
                                ph = await el.get_attribute('placeholder') or ''
                                # 找到对应的 index
                                for info in all_ta_info:
                                    if kw in info['placeholder']:
                                        lyrics_ta_index = info['index']
                                        break
                                print(f"   🔍 通过 placeholder 关键词 '{kw}' 找到歌词文本框 (placeholder='{ph[:60]}')", flush=True)
                                break
                        except Exception:
                            continue

                # ===== 策略 3: 用 JS 直接通过 DOM 层级关系精确查找 Lyrics section 下的 textarea =====
                if not lyrics_input:
                    print("   🔍 尝试通过 JS DOM 层级精确查找 Lyrics textarea...", flush=True)
                    js_lyrics_idx = await page.evaluate("""() => {
                        // 找到页面上所有包含 "Lyrics" 文字的元素
                        const allElements = document.querySelectorAll('*');
                        for (const el of allElements) {
                            // 只匹配直接文字节点内容为 "Lyrics" 的元素
                            const directText = Array.from(el.childNodes)
                                .filter(n => n.nodeType === 3)
                                .map(n => n.textContent.trim())
                                .join('');
                            if (directText === 'Lyrics') {
                                // 找到 "Lyrics" 标签后，向上找共同父容器，再向下找 textarea
                                let parent = el;
                                for (let d = 0; d < 8; d++) {
                                    parent = parent.parentElement;
                                    if (!parent) break;
                                    const ta = parent.querySelector('textarea');
                                    if (ta && ta.offsetHeight > 0) {
                                        // 确认这个 textarea 确实属于 Lyrics section（不是 Styles 的）
                                        const allTas = document.querySelectorAll('textarea');
                                        for (let i = 0; i < allTas.length; i++) {
                                            if (allTas[i] === ta) return i;
                                        }
                                    }
                                }
                            }
                        }
                        return -1;
                    }""")
                    if js_lyrics_idx >= 0:
                        lyrics_input = textareas.nth(js_lyrics_idx)
                        lyrics_ta_index = js_lyrics_idx
                        print(f"   🔍 通过 JS DOM 定位到 Lyrics textarea[{js_lyrics_idx}]", flush=True)

                # ===== 策略 4: 排除 Styles section 的 textarea，选剩下的最高的 =====
                if not lyrics_input:
                    print("   🔍 尝试排除法定位歌词框...", flush=True)
                    visible_tas = [t for t in all_ta_info if t['visible'] and t['height'] > 50]
                    non_style = [t for t in visible_tas if t['sectionTitle'] != 'Styles' and t['sectionTitle'] != 'Style']
                    if non_style:
                        best = max(non_style, key=lambda t: t['height'])
                        lyrics_input = textareas.nth(best['index'])
                        lyrics_ta_index = best['index']
                        print(f"   🔍 排除法选择 textarea[{best['index']}] (section='{best['sectionTitle']}', h={best['height']})", flush=True)
                    elif visible_tas:
                        best = visible_tas[0]
                        lyrics_input = textareas.nth(best['index'])
                        lyrics_ta_index = best['index']
                        print(f"   ⚠️ 排除法无结果，使用第一个可见 textarea[{best['index']}]", flush=True)

                if not lyrics_input:
                    await page.screenshot(path="/tmp/suno_debug_no_lyrics_textarea.png")
                    print("   ❌ 无法找到歌词文本框！截图已保存到 /tmp/suno_debug_no_lyrics_textarea.png", flush=True)
                    await context.close()
                    return None

                # ===== 填写歌词 =====
                # 方法 1: Playwright fill()
                await lyrics_input.click()
                await page.wait_for_timeout(500)
                # 先清空
                await lyrics_input.fill("")
                await page.wait_for_timeout(300)
                await lyrics_input.fill(lyrics)
                await page.wait_for_timeout(500)

                # 验证是否填写成功
                filled_value = await lyrics_input.input_value()
                if filled_value and len(filled_value) > 5:
                    print(f"   ✅ fill() 成功，已填写 {len(filled_value)} 字", flush=True)
                else:
                    # 方法 2: 使用 React 兼容的 nativeInputValueSetter
                    print(f"   ⚠️ fill() 结果不完整 (got {len(filled_value) if filled_value else 0} chars)，尝试 JS 写入...", flush=True)
                    await page.evaluate("""({text, idx}) => {
                        const tas = document.querySelectorAll('textarea');
                        const target = idx >= 0 && idx < tas.length ? tas[idx] : null;
                        if (target) {
                            // 先聚焦
                            target.focus();
                            // 使用 React 兼容的方式设置值
                            const nativeSetter = Object.getOwnPropertyDescriptor(
                                window.HTMLTextAreaElement.prototype, 'value'
                            ).set;
                            nativeSetter.call(target, text);
                            // 触发 React 能感知的事件
                            target.dispatchEvent(new Event('input', { bubbles: true }));
                            target.dispatchEvent(new Event('change', { bubbles: true }));
                            // 额外触发 React 16+ 的合成事件
                            const reactKey = Object.keys(target).find(k => k.startsWith('__reactProps$') || k.startsWith('__reactFiber$'));
                            if (reactKey) {
                                console.log('React 属性检测到:', reactKey);
                            }
                        }
                    }""", {"text": lyrics, "idx": lyrics_ta_index})
                    await page.wait_for_timeout(500)

                    # 方法 3: 如果 JS 写入后仍然为空，使用 type() 模拟逐字输入
                    filled_value2 = await lyrics_input.input_value()
                    if not filled_value2 or len(filled_value2) < 5:
                        print("   ⚠️ JS 写入也未生效，使用 keyboard.type() 逐字输入...", flush=True)
                        await lyrics_input.click()
                        await page.wait_for_timeout(300)
                        # 全选并删除
                        await page.keyboard.press("Meta+a" if platform.system() == "Darwin" else "Control+a")
                        await page.keyboard.press("Backspace")
                        await page.wait_for_timeout(200)
                        # 逐字输入（稍慢但最可靠）
                        await lyrics_input.type(lyrics, delay=10)
                        await page.wait_for_timeout(500)

                # 最终验证
                final_value = await lyrics_input.input_value()
                print(f"   📝 歌词框最终内容: '{final_value[:60]}{'...' if len(final_value)>60 else ''}' ({len(final_value)} 字)", flush=True)

                # 截图验证歌词填写结果
                await page.screenshot(path="/tmp/suno_debug_after_lyrics.png")
                print(f"   📸 已保存歌词填写后截图: /tmp/suno_debug_after_lyrics.png", flush=True)
            except Exception as e:
                print(f"   ❌ 填写歌词失败: {e}", flush=True)
                import traceback
                traceback.print_exc()
                await page.screenshot(path="/tmp/suno_debug_lyrics_error.png")
                await context.close()
                return None

            # ========== 步骤 4: 填写风格标签 ==========
            print("📌 步骤 4: 填写风格标签...", flush=True)
            try:
                style_input = None
                style_ta_index = -1

                # ===== 策略 1（最可靠）: 通过 section 标题 "Styles" 定位 =====
                for info in all_ta_info:
                    if info['visible'] and info['sectionTitle'] in ('Styles', 'Style'):
                        style_input = textareas.nth(info['index'])
                        style_ta_index = info['index']
                        print(f"   🔍 通过 section 标题 '{info['sectionTitle']}' 找到风格 textarea[{info['index']}]", flush=True)
                        break

                # ===== 策略 2: 通过 placeholder 关键词 =====
                if not style_input:
                    style_ph_keywords = [
                        "Style", "style", "genre", "Genre",
                        "tag", "Tag", "Pop", "pop", "Rock", "rock",
                        "风格", "标签", "describe", "Describe"
                    ]
                    for kw in style_ph_keywords:
                        try:
                            el = page.locator(f'textarea[placeholder*="{kw}"]').first
                            if await el.is_visible(timeout=1500):
                                style_input = el
                                print(f"   🔍 通过关键词 '{kw}' 找到风格输入框", flush=True)
                                break
                        except Exception:
                            continue

                # ===== 策略 3: 找一个不是歌词框的可见 textarea =====
                if not style_input:
                    for info in all_ta_info:
                        if info['visible'] and info['height'] > 20 and info['index'] != lyrics_ta_index:
                            style_input = textareas.nth(info['index'])
                            style_ta_index = info['index']
                            print(f"   🔍 排除歌词框后选择 textarea[{info['index']}] 作为风格输入框", flush=True)
                            break

                if style_input:
                    await style_input.click()
                    await page.wait_for_timeout(300)
                    await style_input.fill("")
                    await page.wait_for_timeout(200)
                    await style_input.fill(style)
                    await page.wait_for_timeout(300)
                    # 验证
                    style_val = await style_input.input_value()
                    if style_val:
                        print(f"   ✅ 已填写风格: {style}", flush=True)
                    else:
                        print(f"   ⚠️ fill() 可能未生效，尝试 type()...", flush=True)
                        await style_input.click()
                        await style_input.type(style, delay=10)
                else:
                    print("   ⚠️ 未找到风格输入框", flush=True)
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
                except Exception:
                    pass

                title_filled = False
                # 多种 placeholder 匹配
                title_selectors = [
                    'input[placeholder*="Title"]',
                    'input[placeholder*="title"]',
                    'input[placeholder*="Song"]',
                    'input[placeholder*="Name"]',
                    'input[placeholder*="标题"]',
                    'input[data-testid*="title"]',
                    'input[name*="title"]',
                    'input[aria-label*="title"]',
                ]
                for sel in title_selectors:
                    try:
                        el = page.locator(sel).first
                        if await el.is_visible(timeout=1500):
                            await el.click()
                            await page.wait_for_timeout(200)
                            await el.fill(title)
                            title_filled = True
                            print(f"   ✅ 已填写标题: {title}", flush=True)
                            break
                    except Exception:
                        continue

                # JS fallback: 找到所有 input 并匹配
                if not title_filled:
                    await page.evaluate("""(title) => {
                        const inputs = document.querySelectorAll('input');
                        for (const input of inputs) {
                            const ph = (input.placeholder || '').toLowerCase();
                            if (ph.includes('title') || ph.includes('song') || ph.includes('name')) {
                                const nativeSetter = Object.getOwnPropertyDescriptor(
                                    window.HTMLInputElement.prototype, 'value'
                                ).set;
                                nativeSetter.call(input, title);
                                input.dispatchEvent(new Event('input', { bubbles: true }));
                                input.dispatchEvent(new Event('change', { bubbles: true }));
                                return true;
                            }
                        }
                        return false;
                    }""", title)
                    print(f"   ✅ 已通过 JS 填写标题: {title}", flush=True)
            except Exception as e:
                print(f"   ⚠️ 填写标题失败（非关键）: {e}", flush=True)

            await page.wait_for_timeout(1000)

            # ========== 创建前总览截图 ==========
            await page.screenshot(path="/tmp/suno_step_before_create.png")
            print("   📸 已保存创建前总览截图: /tmp/suno_step_before_create.png", flush=True)

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

    finally:
        # ====== 清理虚拟显示 ======
        if virtual_display:
            virtual_display.stop()
            print("🖥️ Xvfb 虚拟显示已关闭", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Suno 歌曲创建工具 - Headless Linux 版（含 hCaptcha 自动解决）")
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

    # 显示环境信息
    is_headless = _is_headless_linux()
    print("=" * 60, flush=True)
    print("🎵 Suno 歌曲创建工具 (Headless Linux 版)", flush=True)
    print(f"   标题: {args.title}", flush=True)
    print(f"   风格: {args.style}", flush=True)
    print(f"   歌词: {lyrics[:60]}{'...' if len(lyrics)>60 else ''}", flush=True)
    print(f"   Gemini Key: {'已设置' if gemini_key else '未设置'}", flush=True)
    print(f"   环境: {'Linux 无 GUI (将使用 Xvfb)' if is_headless else platform.system() + ' (有 GUI)'}", flush=True)
    print("=" * 60, flush=True)

    result = asyncio.run(create_song(lyrics, args.style, args.title, args.output_dir, gemini_key))
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
