"""
xhs_controller.py — 控制小红书 Mac App 的底层模块

坐标策略（三层，优先级从高到低）：
  1. AX API 动态获取（最准确）：顶部Tab、搜索框、底部Tab栏
  2. AX 锚点 + 固定偏移（次准确）：互动栏（点赞/收藏/评论）
  3. AX 内容区比例（兜底）：Feed 卡片位置

依赖: pyobjc-framework-Quartz, atomacos, cliclick
"""
import subprocess
import time
import base64
import sys
from typing import Optional

try:
    import Quartz
    import atomacos
    import ApplicationServices as _AS
except ImportError as e:
    print(f"缺少依赖: {e}", file=sys.stderr)
    raise

OWNER_NAME = "rednote"
PROCESS_NAME = "discover"
CLICLICK = "/opt/homebrew/bin/cliclick"
SCREENSHOT_TMP = "/tmp/xhs_snap.png"
_TITLEBAR_H = 28   # macOS 标题栏高度（固定）


# ── 窗口 ────────────────────────────────────────────────────

def get_window_bounds() -> Optional[dict]:
    win_list = Quartz.CGWindowListCopyWindowInfo(
        Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID)
    for w in win_list:
        if w.get("kCGWindowOwnerName") == OWNER_NAME and w.get("kCGWindowIsOnscreen"):
            b = w["kCGWindowBounds"]
            return {"x": float(b["X"]), "y": float(b["Y"]),
                    "w": float(b["Width"]), "h": float(b["Height"]),
                    "id": w.get("kCGWindowNumber")}
    return None


def is_running() -> bool:
    r = subprocess.run(["pgrep", "-x", PROCESS_NAME], capture_output=True, text=True)
    return bool(r.stdout.strip())


def is_screen_locked() -> bool:
    r = subprocess.run(
        ["python3", "-c",
         "import Quartz; s=Quartz.CGSessionCopyCurrentDictionary(); "
         "print(s.get('CGSSessionScreenIsLocked', 0) or s.get('kCGSSessionScreenIsLocked', 0))"],
        capture_output=True, text=True)
    return r.stdout.strip() == "1"


def activate():
    """将 rednote 置前，确保屏幕已解锁且窗口可交互"""
    if is_screen_locked():
        raise RuntimeError("屏幕已锁定，无法操作。请先解锁 Mac。")
    subprocess.run(["open", "-a", "rednote"])
    time.sleep(1.5)
    subprocess.run(["osascript", "-e",
        'tell application "System Events" to tell process "discover" to set frontmost to true'])
    time.sleep(0.3)


# ── AX 核心 ────────────────────────────────────────────────

def _ax_app():
    r = subprocess.run(["pgrep", "-x", PROCESS_NAME], capture_output=True, text=True)
    pid = r.stdout.strip()
    return atomacos.getAppRefByPid(int(pid)) if pid else None


def _ax_window():
    app = _ax_app()
    if not app:
        return None
    wins = app.AXWindows
    return wins[0] if wins else None


import re as _re

def _as_get(ref, attr):
    """直接用 ApplicationServices API 读取 AX 属性，绕过 atomacos 解析 bug"""
    err, val = _AS.AXUIElementCopyAttributeValue(ref, attr, None)
    return val if err == 0 else None

def _as_parse_frame(frame_val):
    """从 AXValue 对象解析 CGRect，返回 dict {x,y,w,h} 或 None"""
    if not frame_val:
        return None
    m = _re.search(r'x:([\d.]+).*?y:([\d.]+).*?w:([\d.]+).*?h:([\d.]+)', str(frame_val))
    if m:
        x, y, w, h = [float(v) for v in m.groups()]
        return {"x": x, "y": y, "w": w, "h": h, "cx": x + w/2, "cy": y + h/2}
    return None

def _as_find_all(ref, match_fn, depth=0, max_depth=12, results=None):
    """用 AS API 直接遍历 AX 树（绕过 atomacos AXChildren 解析 bug）。
    match_fn(role, desc, frame_dict) -> bool
    返回 [{"role", "desc", "frame", "ref"}, ...]
    """
    if results is None:
        results = []
    if depth > max_depth:
        return results
    try:
        role_val = _as_get(ref, 'AXRole')
        role = str(role_val) if role_val else ''
        desc_val = _as_get(ref, 'AXDescription')
        desc = str(desc_val) if desc_val else ''
        frame_val = _as_get(ref, 'AXFrame')
        frame = _as_parse_frame(frame_val)
        if match_fn(role, desc, frame):
            results.append({"role": role, "desc": desc, "frame": frame, "ref": ref})
        children = _as_get(ref, 'AXChildren')
        if children:
            for ch in children:
                _as_find_all(ch, match_fn, depth+1, max_depth, results)
    except Exception:
        pass
    return results

def _as_window_ref():
    """获取 XHS 窗口的原始 AXUIElement ref"""
    win = _ax_window()
    return win.ref if win else None


def _ax_find(el, match_fn, depth=0, max_depth=10):
    """DFS 遍历 AX 树，返回第一个满足 match_fn(el) 的元素"""
    if depth > max_depth:
        return None
    try:
        if match_fn(el):
            return el
        for c in (getattr(el, "AXChildren", []) or []):
            r = _ax_find(c, match_fn, depth+1, max_depth)
            if r:
                return r
    except Exception:
        pass
    return None


def _ax_find_all(el, match_fn, depth=0, max_depth=10):
    """DFS 遍历 AX 树，返回所有满足 match_fn(el) 的元素"""
    results = []
    if depth > max_depth:
        return results
    try:
        if match_fn(el):
            results.append(el)
        for c in (getattr(el, "AXChildren", []) or []):
            results.extend(_ax_find_all(c, match_fn, depth+1, max_depth))
    except Exception:
        pass
    return results


def _ax_center(el) -> Optional[tuple[int, int]]:
    """获取 AX 元素的全局中心坐标"""
    try:
        pos = el.AXPosition
        size = el.AXSize
        return int(pos.x + size.width / 2), int(pos.y + size.height / 2)
    except Exception:
        return None


# ── 截图 ────────────────────────────────────────────────────

def screenshot(path: str = SCREENSHOT_TMP) -> Optional[str]:
    """用 window ID 截图（比 -R 更可靠）"""
    b = get_window_bounds()
    if not b:
        return None
    r = subprocess.run(
        ["/usr/sbin/screencapture", "-x", f"-l{b['id']}", path],
        capture_output=True)
    return path if r.returncode == 0 else None


def screenshot_b64() -> Optional[str]:
    path = screenshot()
    if not path:
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ── 点击 & 输入 ──────────────────────────────────────────────

def click_global(gx: int, gy: int, delay: float = 0.5):
    subprocess.run([CLICLICK, f"c:{gx},{gy}"])
    time.sleep(delay)


def click_ax(el, delay: float = 0.5):
    """点击 AX 元素的中心"""
    c = _ax_center(el)
    if not c:
        raise RuntimeError("无法获取元素坐标")
    click_global(c[0], c[1], delay)


def type_text(text: str, delay: float = 0.4):
    """输入文字 — 用剪贴板粘贴，避免中文输入法问题"""
    # 1. 把文字写入剪贴板
    subprocess.run(["pbcopy"], input=text.encode("utf-8"))
    time.sleep(0.1)
    # 2. Cmd+V 粘贴
    subprocess.run(["osascript", "-e",
        'tell application "System Events" to keystroke "v" using command down'])
    time.sleep(delay)


def press_enter():
    subprocess.run(["osascript", "-e",
        'tell application "System Events" to key code 36'])
    time.sleep(0.3)


def press_escape():
    subprocess.run(["osascript", "-e",
        'tell application "System Events" to key code 53'])
    time.sleep(0.3)


def _scroll(direction: str, times: int, gx: int, gy: int):
    """用 CGEventPost 发送滚轮事件（cliclick 无 scroll 命令）"""
    import Quartz as Q
    # 先移动鼠标到目标位置
    subprocess.run([CLICLICK, f"m:{gx},{gy}"])
    time.sleep(0.15)
    delta = -5 if direction == "down" else 5   # 负值=向下
    for _ in range(times):
        evt = Q.CGEventCreateScrollWheelEvent(None, Q.kCGScrollEventUnitLine, 1, delta)
        Q.CGEventPost(Q.kCGHIDEventTap, evt)
        time.sleep(0.3)


# ── 动态 UI 元素定位 ─────────────────────────────────────────

def _find_top_tab(name: str):
    """从 AX 树找顶部 Tab（关注/发现/视频）"""
    win = _ax_window()
    if not win:
        return None
    return _ax_find(win,
        lambda el: getattr(el, "AXDescription", "") == name and el.AXRole == "AXGenericElement")


def _find_search_box():
    """从 AX 树找搜索框"""
    win = _ax_window()
    if not win:
        return None
    return _ax_find(win,
        lambda el: "搜索" in (getattr(el, "AXDescription", "") or "")
                   and el.AXRole == "AXStaticText")


def _find_tabbar_buttons():
    """从 AX 树找底部 Tab 栏的按钮（4个 AXButton）"""
    win = _ax_window()
    if not win:
        return []
    tabbar = _ax_find(win,
        lambda el: getattr(el, "AXDescription", "") == "标签页栏")
    if not tabbar:
        return []
    try:
        return [c for c in (getattr(tabbar, "AXChildren", []) or [])
                if c.AXRole == "AXButton"]
    except Exception:
        return []


def _get_tabbar_y() -> Optional[float]:
    """获取底部 Tab 栏的全局 y 坐标（AX 动态）"""
    win = _ax_window()
    if not win:
        return None
    tabbar = _ax_find(win, lambda el: getattr(el, "AXDescription", "") == "标签页栏")
    if not tabbar:
        return None
    try:
        pos = tabbar.AXPosition
        size = tabbar.AXSize
        return float(pos.y + size.height / 2)
    except Exception:
        return None


# ── 导航 ────────────────────────────────────────────────────

# 底部 Tab：AX 只暴露 4 个按钮（首页/市集/消息/我），发布(+)不在AX里
# 按钮顺序从左到右：index 0=首页, 1=市集, 2=消息, 3=我
_TAB_BTN_IDX = {"home": 0, "market": 1, "messages": 2, "profile": 3}
# 发布按钮没有 AX 节点，用固定比例（中心 x=50%）
_POST_RX = 0.5

def navigate_tab(tab: str):
    """切换底部 Tab（AX 精确定位）"""
    activate()

    if tab == "post":
        # 发布按钮没有 AX 节点，用 tabbar y + x=50%
        b = get_window_bounds()
        tby = _get_tabbar_y()
        if b and tby:
            gx = int(b["x"] + b["w"] * _POST_RX)
            gy = int(tby)
            click_global(gx, gy, delay=1.0)
        return

    idx = _TAB_BTN_IDX.get(tab)
    if idx is None:
        raise ValueError(f"未知 tab: {tab}")

    btns = _find_tabbar_buttons()
    if not btns:
        # 搜索页/详情页等场景 Tab 栏不可见 → 先 back 回上一页再试
        back()
        time.sleep(1.0)
        btns = _find_tabbar_buttons()

    if len(btns) > idx:
        click_ax(btns[idx], delay=1.0)
    else:
        # 最终兜底：用窗口底部固定比例点击
        b = get_window_bounds()
        if not b:
            raise RuntimeError("找不到 rednote 窗口")
        # 底部 Tab 栏：4 个按钮在 x=16%/38%/62%/84%，y=底部约 95%
        tab_xs = [0.16, 0.38, 0.62, 0.84]
        gx = int(b["x"] + tab_xs[idx] * b["w"])
        gy = int(b["y"] + b["h"] * 0.955)
        click_global(gx, gy, delay=1.0)


def navigate_top_tab(tab: str):
    """切换顶部 Tab（关注/发现/视频），用 AX 精确定位。
    如果当前不在首页（AX 树中找不到顶部 Tab），先返回首页再切换。
    """
    name_map = {"follow": "关注", "discover": "发现", "video": "视频"}
    cn_name = name_map.get(tab)
    if not cn_name:
        raise ValueError(f"未知顶部 tab: {tab}")
    activate()
    el = _find_top_tab(cn_name)
    if not el:
        # 可能在详情页，先导航到首页 tab
        navigate_tab("home")
        time.sleep(1.0)
        el = _find_top_tab(cn_name)
    if el:
        click_ax(el, delay=1.0)
    else:
        raise RuntimeError(f"AX 树中找不到顶部 Tab: {cn_name}（已尝试返回首页）")


def back():
    """返回上一页（AX 找返回按钮，或用固定坐标）"""
    activate()
    b = get_window_bounds()
    if not b:
        return
    # 返回按钮在标题栏左侧，全局坐标约 (win.x+21, win.y+58)
    gx = int(b["x"] + 21)
    gy = int(b["y"] + 58)
    click_global(gx, gy, delay=0.8)


def search(keyword: str):
    """搜索关键词（AX 定位搜索框，失败则用坐标兜底）"""
    activate()
    el = _find_search_box()
    if el:
        click_ax(el, delay=1.0)
    else:
        # 兜底：搜索框在顶部约 x=77.7%，y=61px（实测截图坐标584/752×780）
        b = get_window_bounds()
        if b:
            gx = int(b["x"] + b["w"] * 0.777)
            gy = int(b["y"] + 61)
            click_global(gx, gy, delay=1.0)
    type_text(keyword, delay=0.5)
    press_enter()
    time.sleep(2.0)


# ── Feed ────────────────────────────────────────────────────

def scroll_feed(direction: str = "down", times: int = 3):
    activate()
    b = get_window_bounds()
    if not b:
        return
    tby = _get_tabbar_y() or (b["y"] + b["h"] * 0.94)
    content_h = tby - (b["y"] + _TITLEBAR_H)
    # 滚动中心：内容区中间
    gx = int(b["x"] + b["w"] * 0.5)
    gy = int(b["y"] + _TITLEBAR_H + content_h * 0.5)
    _scroll(direction, times, gx, gy)


def open_note(col: int = 0, row: int = 0):
    """打开 Feed 双列瀑布流中的笔记，col=0左/1右，row=行号"""
    activate()
    b = get_window_bounds()
    if not b:
        return
    tby = _get_tabbar_y() or (b["y"] + b["h"] * 0.94)
    content_top = b["y"] + _TITLEBAR_H
    content_h = tby - content_top

    col_rx = [0.27, 0.73][col if col in (0, 1) else 0]
    # 第一行在内容区约 22%，每行步进约 28%
    row_ry = 0.22 + row * 0.28
    gx = int(b["x"] + col_rx * b["w"])
    gy = int(content_top + row_ry * content_h)
    click_global(gx, gy, delay=1.5)


# ── 笔记详情互动 ─────────────────────────────────────────────

def _find_interact_btn(desc_name: str):
    """在 AX 树中查找互动按钮（点赞/收藏/评论），详情页 Tab 栏不可见时也能找到"""
    win = _ax_window()
    if not win:
        return None
    return _ax_find(win,
        lambda el: getattr(el, "AXDescription", "") == desc_name
                   and el.AXRole == "AXButton")


def _interact_fallback(rx: float) -> tuple[int, int]:
    """互动栏坐标兜底（AX 找不到时用）：窗口底部固定偏移"""
    b = get_window_bounds()
    if not b:
        raise RuntimeError("无法获取窗口坐标")
    # 互动区在窗口底部约 87px 处（Tab 栏高约 66px + 互动栏 21px above tab）
    gx = int(b["x"] + rx * b["w"])
    gy = int(b["y"] + b["h"] - 87)
    return gx, gy


def like():
    activate()
    el = _find_interact_btn("点赞")
    if el:
        click_ax(el, delay=0.8)
    else:
        gx, gy = _interact_fallback(0.893)
        click_global(gx, gy, delay=0.8)


def collect():
    activate()
    el = _find_interact_btn("收藏")
    if el:
        click_ax(el, delay=0.8)
    else:
        gx, gy = _interact_fallback(0.937)
        click_global(gx, gy, delay=0.8)


def open_comments():
    """打开评论区（点击评论按钮）。
    策略：
    1. AX 找 desc='评论' 的按钮（图文帖通常有）
    2. AX 找 desc='分享' 按钮，评论按钮在其右边约 160px（视频帖）
    3. 最终兜底：固定比例坐标
    图文笔记评论区已内嵌在右侧，无需点击；视频帖需要点击弹出。
    """
    activate()
    # 策略1：AX 找评论按钮
    el = _find_interact_btn("评论")
    if el:
        click_ax(el, delay=1.0)
        return

    # 策略2：从 AX 分享按钮位置推算评论位置（视频帖）
    win = _ax_window()
    if win:
        share_btn = _ax_find(win,
            lambda e: getattr(e, "AXDescription", "") == "分享"
                      and e.AXRole == "AXButton")
        if share_btn:
            c = _ax_center(share_btn)
            if c:
                # 评论按钮在分享右边约 160px，y 相同
                click_global(c[0] + 160, c[1], delay=1.0)
                return

    # 策略3：固定比例兜底
    b = get_window_bounds()
    if b:
        gx = int(b["x"] + b["w"] * 0.94)
        gy = int(b["y"] + b["h"] - 23)
        click_global(gx, gy, delay=1.0)


def scroll_comments(times: int = 3):
    """滚动评论区。
    图文笔记：右侧面板（x≈72%）；视频笔记：全屏评论区（x≈50%）。
    优先尝试右侧区域，确保不滚到左侧图片区。
    """
    activate()
    b = get_window_bounds()
    tby = _get_tabbar_y()
    if b and tby:
        content_top = b["y"] + _TITLEBAR_H
        # 右侧面板（图文帖评论区）: x≈72%，y≈75% 内容区
        gx = int(b["x"] + b["w"] * 0.72)
        gy = int(content_top + (tby - content_top) * 0.75)
        _scroll("down", times, gx, gy)


def follow_author():
    """关注作者（详情页右上角关注按钮，x≈94%）"""
    activate()
    b = get_window_bounds()
    if b:
        gx = int(b["x"] + b["w"] * 0.94)
        gy = int(b["y"] + 58)   # 与返回按钮同行
        click_global(gx, gy, delay=0.8)


# ── 其他导航 ─────────────────────────────────────────────────

def open_profile():
    navigate_tab("profile")
    time.sleep(1.0)


def open_messages():
    navigate_tab("messages")
    time.sleep(1.0)


def open_post_editor():
    navigate_tab("post")
    time.sleep(1.5)


# ── 私信列表 & 导航 ──────────────────────────────────────────

def open_dm_list():
    """打开消息/私信列表页，返回截图 base64（或 None）"""
    try:
        navigate_tab("messages")
        time.sleep(1.5)
        return screenshot_b64()
    except Exception:
        return None


def get_dm_list(use_vlm: bool = False) -> list:
    """
    读取消息页私信列表（AX 版，轻量）。
    VLM fallback 由上层 main.py 的 xhs_get_dm_list 负责。
    返回 [{"name": str, "preview": str, "index": int}, ...]
    """
    activate()
    navigate_tab("messages")
    time.sleep(1.0)

    try:
        win = _ax_window()
        b = get_window_bounds()
        if not win or not b:
            return []

        list_y_start = b["y"] + 200   # 消息列表从顶部约 200px 开始
        list_y_end   = b["y"] + b["h"] - 70

        all_texts = _ax_find_all(win, lambda el: el.AXRole == "AXStaticText")
        items = []
        for el in all_texts:
            try:
                pos = el.AXPosition
                desc = getattr(el, "AXDescription", "") or getattr(el, "AXValue", "") or ""
                if not desc:
                    continue
                gy = pos.y
                if gy < list_y_start or gy > list_y_end:
                    continue
                matched = False
                for item in items:
                    if abs(item["_y"] - gy) < 30:
                        if not item["preview"] and desc != item["name"]:
                            item["preview"] = desc
                        matched = True
                        break
                if not matched:
                    items.append({"name": desc, "preview": "", "index": len(items), "_y": int(gy)})
            except Exception:
                continue

        items.sort(key=lambda x: x["_y"])
        for i, item in enumerate(items):
            item["index"] = i
            del item["_y"]
        return items
    except Exception:
        return []


def open_dm_by_index(index: int):
    """
    打开第 N 条私信对话（0-based）。
    步骤：确保在消息页 → 计算坐标 → 点击 → 等待。

    坐标说明（752×780px 截图基准，窗口 640×668pt）：
    - index=0 (第1条) 截图 y≈228 → 窗口 y≈195 → 全局 win.y+195
    - 相邻条目截图间距约 80px → 窗口间距约 68px
    - x 固定在窗口水平中心
    """
    try:
        activate()
        navigate_tab("messages")
        time.sleep(1.0)

        b = get_window_bounds()
        if not b:
            return

        # 参考截图尺寸 752×780，窗口 640×668
        # index=0 截图 y≈228 → 窗口点 y = 228/780*668 ≈ 195
        IMG_H = 780.0
        WIN_H = 668.0
        img_y0 = 228   # 第一条 y（截图像素）
        img_dy = 80    # 每条间距（截图像素）

        img_y = img_y0 + index * img_dy
        win_y = img_y / IMG_H * WIN_H
        gx = int(b["x"] + b["w"] / 2)
        gy = int(b["y"] + win_y)

        click_global(gx, gy, delay=1.5)
    except Exception:
        pass


def send_dm(text: str) -> bool:
    """
    在当前私信对话页发送消息。
    步骤：找「发消息…」输入框 → 点击激活 → 输入文字 → 按 Enter。
    返回 True/False。
    """
    try:
        activate()
        win = _ax_window()
        b = get_window_bounds()
        if not b:
            return False

        # 策略1：AX 找 desc='发消息…' 的 StaticText（输入框 placeholder）
        input_el = _ax_find(win,
            lambda el: "发消息" in (getattr(el, "AXDescription", "") or "")
                       and el.AXRole == "AXStaticText") if win else None

        if input_el:
            c = _ax_center(input_el)
            if c:
                click_global(c[0], c[1], delay=0.8)
            else:
                # 兜底坐标：窗口底部 y - 40，x = 中心
                gx = int(b["x"] + b["w"] / 2)
                gy = int(b["y"] + b["h"] - 40)
                click_global(gx, gy, delay=0.8)
        else:
            # 兜底：窗口底部
            gx = int(b["x"] + b["w"] / 2)
            gy = int(b["y"] + b["h"] - 40)
            click_global(gx, gy, delay=0.8)

        type_text(text, delay=0.5)

        # 找「发送」按钮
        if win:
            send_btn = _ax_find(win,
                lambda el: getattr(el, "AXDescription", "") in ("发送", "Send")
                           and el.AXRole == "AXButton")
            if send_btn:
                click_ax(send_btn, delay=0.8)
                return True

        # 兜底：按 Enter
        press_enter()
        return True
    except Exception:
        return False


def get_dm_content() -> dict:
    """
    读取当前私信对话页的内容（AX）。
    返回 {"partner": str, "messages": list[str], "shared_notes": list[str]}
    """
    try:
        activate()
        win = _ax_window()
        if not win:
            return {"partner": "", "messages": [], "shared_notes": []}

        b = get_window_bounds()
        if not b:
            return {"partner": "", "messages": [], "shared_notes": []}

        # 找所有 StaticText
        all_texts = _ax_find_all(win,
            lambda el: el.AXRole == "AXStaticText")

        partner = ""
        messages = []
        shared_notes = []

        # 已知：顶部「navi back」、对方昵称、笔记卡片（逗号分隔多 tag）、「发消息…」
        skip_descs = {"navi back", "发消息…", "发消息", ""}
        # tabbar 区域 y 下限
        tabbar_y = b["y"] + b["h"] - 70

        for el in all_texts:
            try:
                desc = (getattr(el, "AXDescription", "") or
                        getattr(el, "AXValue", "") or "").strip()
                if not desc or desc in skip_descs:
                    continue

                pos = el.AXPosition
                gy = pos.y

                # 过滤 tabbar 区域
                if gy > tabbar_y:
                    continue

                # 顶部区域（y < win.y + 100）：对方名字
                if gy < b["y"] + 100:
                    if not partner and desc != "navi back":
                        partner = desc
                    continue

                # 判断是否为笔记卡片：逗号分隔多个 tag
                if "," in desc and len(desc.split(",")) >= 2:
                    shared_notes.append(desc)
                else:
                    messages.append(desc)
            except Exception:
                continue

        return {
            "partner": partner,
            "messages": messages,
            "shared_notes": shared_notes
        }
    except Exception:
        return {"partner": "", "messages": [], "shared_notes": []}


def open_shared_note_in_dm():
    """
    点击私信中分享的笔记卡片（第一张）。
    AX 找 desc 含逗号分隔多个标签的 StaticText（笔记卡片）→ 点击。
    """
    try:
        activate()
        win = _ax_window()
        if not win:
            return

        # 找笔记卡片：desc 含逗号的 StaticText
        card_el = _ax_find(win,
            lambda el: el.AXRole == "AXStaticText"
                       and "," in (getattr(el, "AXDescription", "") or "")
                       and len((getattr(el, "AXDescription", "") or "").split(",")) >= 2)

        if card_el:
            click_ax(card_el, delay=1.5)
        else:
            # 兜底：私信对话中卡片通常在中部区域，y≈500
            b = get_window_bounds()
            if b:
                gx = int(b["x"] + b["w"] / 2)
                gy = int(b["y"] + 500)
                click_global(gx, gy, delay=1.5)
    except Exception:
        pass


# ── 笔记 URL 获取 ────────────────────────────────────────────

def get_note_url() -> str:
    """
    获取当前笔记的链接。
    策略：点击底部「分享」按钮 → 分享面板弹出 → 点击「复制链接」→ 读剪贴板。
    截图尺寸参考：708x736（窗口 640x668 的 1.106x 缩放）。
    返回 URL 字符串，找不到返回空字符串。
    """
    try:
        activate()
        b = get_window_bounds()
        if not b:
            return ""

        # 截图实际尺寸
        IMG_W, IMG_H = 708, 736

        # 先清空剪贴板
        subprocess.run(["pbcopy"], input=b"")

        # 1. 点击底部「分享」按钮（截图坐标约 505, 688）
        share_x = int(b["x"] + 505 * b["w"] / IMG_W)
        share_y = int(b["y"] + 688 * b["h"] / IMG_H)
        click_global(share_x, share_y, delay=2.0)

        # 2. 点击分享面板中的「复制链接」（截图坐标约 545, 575）
        copy_x = int(b["x"] + 545 * b["w"] / IMG_W)
        copy_y = int(b["y"] + 575 * b["h"] / IMG_H)
        click_global(copy_x, copy_y, delay=1.0)

        # 3. 读剪贴板
        result = subprocess.run(["pbpaste"], capture_output=True, text=True)
        raw = result.stdout.strip()

        # 提取 URL（格式：文字 + URL + 文字）
        import re
        m = re.search(r'https?://\S+', raw)
        if m:
            return m.group(0)

        # 如果没弹出面板（点偏了），按 Escape 关闭再返回
        if not raw:
            press_escape()
        return raw
    except Exception:
        return ""


# ── 博主主页 ─────────────────────────────────────────────────

def open_author_profile():
    """
    点击当前详情页的博主头像/名字，进入博主主页。
    策略：AX 找 desc 是 UUID 格式的 AXButton → 点击。
    """
    import re
    try:
        activate()
        win = _ax_window()
        if not win:
            return

        uuid_pattern = re.compile(r'^[A-Fa-f0-9\-]{10,}$')

        author_btn = _ax_find(win,
            lambda el: el.AXRole == "AXButton"
                       and bool(uuid_pattern.match(
                           getattr(el, "AXDescription", "") or "")))

        if author_btn:
            click_ax(author_btn, delay=1.5)
        else:
            # 兜底：找「关注」按钮，头像在其左边约 90px
            follow_btn = _ax_find(win,
                lambda e: getattr(e, "AXDescription", "") == "关注"
                          and e.AXRole == "AXButton") if win else None
            if follow_btn:
                c = _ax_center(follow_btn)
                if c:
                    click_global(c[0] - 90, c[1], delay=1.5)
                    return
            # 最终兜底：固定比例
            b = get_window_bounds()
            if b:
                gx = int(b["x"] + b["w"] * 0.14)
                gy = int(b["y"] + b["h"] - 80)
                click_global(gx, gy, delay=1.5)
    except Exception:
        pass


def get_author_stats() -> dict:
    """
    读取当前主页博主的统计信息。
    AX 找 StaticText，提取：关注数/粉丝数/获赞&收藏数/bio。
    返回 {"following": str, "followers": str, "likes": str, "bio": str}
    """
    try:
        activate()
        win = _ax_window()
        if not win:
            return {"following": "", "followers": "", "likes": "", "bio": ""}

        all_texts = _ax_find_all(win,
            lambda el: el.AXRole == "AXStaticText")

        # 已知结构：
        # AXStaticText desc='关注' @ y≈391（标签）
        # AXStaticText desc='粉丝' @ y≈391（标签）
        # AXStaticText desc='282' @ y≈375（获赞数）
        # 数字在标签上方约 16px

        following = ""
        followers = ""
        likes = ""
        bio = ""

        # 找「关注」「粉丝」「获赞与收藏」标签，然后找其上方的数字
        label_els = {}
        for el in all_texts:
            try:
                desc = (getattr(el, "AXDescription", "") or "").strip()
                pos = el.AXPosition
                if desc in ("关注", "粉丝", "获赞与收藏", "获赞"):
                    label_els[desc] = (el, pos.x, pos.y)
            except Exception:
                continue

        # 找数字：在标签上方（y 更小），且 x 接近
        number_els = []
        for el in all_texts:
            try:
                desc = (getattr(el, "AXDescription", "") or "").strip()
                if desc.replace(",", "").replace(".", "").isdigit() or (
                        len(desc) <= 6 and any(c.isdigit() for c in desc)):
                    pos = el.AXPosition
                    number_els.append((desc, pos.x, pos.y))
            except Exception:
                continue

        def find_number_near(lx, ly):
            """找 x 坐标接近、y 坐标稍小（数字在标签上方）的数字"""
            best = ""
            best_dist = 9999
            for num_desc, nx, ny in number_els:
                if abs(nx - lx) < 40 and -30 < (ly - ny) < 40:
                    dist = abs(nx - lx) + abs(ly - ny)
                    if dist < best_dist:
                        best_dist = dist
                        best = num_desc
            return best

        for label, (el, lx, ly) in label_els.items():
            num = find_number_near(lx, ly)
            if label == "关注":
                following = num
            elif label == "粉丝":
                followers = num
            elif label in ("获赞与收藏", "获赞"):
                likes = num

        # bio 从 AXButton 里找（多行文本按钮）
        all_btns = _ax_find_all(win,
            lambda el: el.AXRole == "AXButton")
        for btn in all_btns:
            try:
                desc = (getattr(btn, "AXDescription", "") or "").strip()
                # bio 通常含换行或较长文字，排除 UUID 格式
                if len(desc) > 5 and "\n" in desc:
                    bio = desc
                    break
                # 兜底：找含中文且不是导航按钮的较长 desc
                if len(desc) > 10 and any('\u4e00' <= c <= '\u9fff' for c in desc):
                    import re
                    if not re.match(r'^[A-Fa-f0-9\-]{10,}$', desc):
                        bio = desc
                        break
            except Exception:
                continue

        return {
            "following": following,
            "followers": followers,
            "likes": likes,
            "bio": bio
        }
    except Exception:
        return {"following": "", "followers": "", "likes": "", "bio": ""}


# ── 关注 / 取关 ──────────────────────────────────────────────

def follow_author_by_btn() -> bool:
    """关注当前详情页的博主（AX 精确找 desc='关注' button）"""
    try:
        activate()
        win = _ax_window()
        if not win:
            return False
        b = get_window_bounds()
        # 详情页顶部关注按钮 y 坐标约在窗口 y+50~80 范围内
        # 排除底部 Tab 栏中可能出现的「关注」按钮
        top_y_min = (b["y"] + 40) if b else 0
        top_y_max = (b["y"] + 100) if b else 9999

        def is_follow_btn(el):
            if getattr(el, "AXRole", "") != "AXButton":
                return False
            if getattr(el, "AXDescription", "") != "关注":
                return False
            c = _ax_center(el)
            if c and top_y_min <= c[1] <= top_y_max:
                return True
            return False

        el = _ax_find(win, is_follow_btn)
        if el:
            click_ax(el, delay=0.8)
            return True
        return False
    except Exception:
        return False


def unfollow_author() -> bool:
    """取关当前详情页的博主（AX 找 desc='已关注' button → 点击 → 确认弹窗）"""
    try:
        activate()
        win = _ax_window()
        if not win:
            return False

        # 找「已关注」按钮
        el = _ax_find(win,
            lambda e: getattr(e, "AXRole", "") == "AXButton"
                      and getattr(e, "AXDescription", "") == "已关注")
        if not el:
            return False
        click_ax(el, delay=1.0)

        # 等待确认弹窗出现
        time.sleep(0.8)
        win = _ax_window()
        if not win:
            return False

        # 弹窗里有「取消关注」按钮，AX 查找后点击确认
        confirm_btn = _ax_find(win,
            lambda e: getattr(e, "AXRole", "") == "AXButton"
                      and "取消关注" in (getattr(e, "AXDescription", "") or getattr(e, "AXTitle", "") or ""))
        if confirm_btn:
            click_ax(confirm_btn, delay=0.8)
            return True
        return False
    except Exception:
        return False


# ── 评论相关 ─────────────────────────────────────────────────

def post_comment(text: str) -> bool:
    """在当前笔记详情页发布一条评论"""
    try:
        activate()
        # 1. 找评论按钮（desc='评论'）并点击，等待输入框出现
        el = _find_interact_btn("评论")
        if el:
            click_ax(el, delay=1.0)
        else:
            gx, gy = _interact_fallback(0.985)
            click_global(gx, gy, delay=1.0)

        time.sleep(0.8)

        # 2. AX 查找 AXTextArea（输入框，desc 含「说点什么」）
        win = _ax_window()
        if not win:
            return False
        input_el = _ax_find(win,
            lambda e: getattr(e, "AXRole", "") == "AXTextArea"
                      and "说点什么" in (getattr(e, "AXDescription", "") or ""))
        if not input_el:
            # 兜底：找任意 AXTextArea
            input_el = _ax_find(win, lambda e: getattr(e, "AXRole", "") == "AXTextArea")

        if not input_el:
            return False

        # 3. 点击输入框
        click_ax(input_el, delay=0.5)

        # 4. 输入文字
        type_text(text, delay=0.5)

        # 5. 找「发送」按钮并点击
        win = _ax_window()
        if not win:
            return False
        send_btn = _ax_find(win,
            lambda e: getattr(e, "AXRole", "") == "AXButton"
                      and (getattr(e, "AXDescription", "") == "发送"
                           or "发送" in (getattr(e, "AXTitle", "") or "")))
        if send_btn:
            click_ax(send_btn, delay=1.5)
        else:
            # 兜底：按 Enter 发送
            press_enter()
            time.sleep(1.5)

        return True
    except Exception:
        return False


def reply_to_comment(comment_index: int, text: str) -> bool:
    """回复评论区的第 N 条评论（0-based）。
    策略：用 AS API 找评论区用户名按钮，点击其文字区域触发「回复 @xxx」输入框。
    - 评论区用户名按钮按 y 坐标排序，取第 comment_index 个
    - 发送：优先 AX 点击「发送」按钮，否则 press_enter
    """
    try:
        activate()
        win = _ax_window()
        if not win:
            return False

        # 1. 确保评论区已打开
        has_textarea = _ax_find(win, lambda e: getattr(e, "AXRole", "") == "AXTextArea")
        if not has_textarea:
            open_comments()
            time.sleep(1.5)
            win = _ax_window()
            if not win:
                return False

        # 2. 用 AS API 找评论区用户名按钮（带 desc 的 AXButton，排除功能按钮）
        EXCLUDE = {"点赞", "收藏", "评论", "分享", "发送", "搜索", "返回"}
        win_ref = _as_window_ref()
        if not win_ref:
            return False

        comment_btns = _as_find_all(win_ref,
            lambda role, desc, frame: (
                role == "AXButton"
                and desc
                and desc not in EXCLUDE
                and not desc.startswith("展开")
                and frame is not None
            ))

        # 按 y 坐标排序（从上到下 = 评论顺序）
        comment_btns.sort(key=lambda b: b["frame"]["cy"])

        if comment_index < len(comment_btns):
            btn = comment_btns[comment_index]
            # 点击用户名按钮右侧（评论内容文字区域）
            cx = int(btn["frame"]["cx"]) + 60  # 右移避开头像，点文字
            cy = int(btn["frame"]["cy"])
            click_global(cx, cy, delay=1.2)
        else:
            # fallback：坐标估算
            b = get_window_bounds()
            if not b:
                return False
            row_x = int(b["x"] + b["w"] * 0.79)
            row_y = int(b["y"] + b["h"] * 0.21) + comment_index * 80
            click_global(row_x, row_y, delay=1.2)

        # 3. 等待输入框聚焦
        time.sleep(0.8)

        # 4. 输入文字
        type_text(text, delay=0.5)
        time.sleep(0.3)

        # 5. 找发送按钮（AX），点击
        win = _ax_window()
        if win:
            send_btn = _ax_find(win,
                lambda e: getattr(e, "AXRole", "") == "AXButton"
                          and "发送" in (getattr(e, "AXDescription", "") or ""))
            if send_btn:
                click_ax(send_btn, delay=1.0)
                return True

        press_enter()
        time.sleep(1.0)
        return True
    except Exception:
        return False


def get_comments() -> list:
    """读取当前笔记的评论列表。
    用 AS API 遍历（绕过 atomacos AXChildren bug），
    通过用户名按钮定位评论，返回 [{"index", "author", "frame"}, ...]。
    """
    try:
        activate()
        win_ref = _as_window_ref()
        if not win_ref:
            return []

        EXCLUDE = {"点赞", "收藏", "评论", "分享", "发送", "搜索", "返回"}
        comment_btns = _as_find_all(win_ref,
            lambda role, desc, frame: (
                role == "AXButton"
                and desc
                and desc not in EXCLUDE
                and not desc.startswith("展开")
                and frame is not None
            ))

        # 按 y 坐标排序（从上到下 = 评论顺序）
        comment_btns.sort(key=lambda b: b["frame"]["cy"])

        results = []
        for idx, btn in enumerate(comment_btns):
            results.append({
                "index": idx,
                "author": btn["desc"],
                "cx": int(btn["frame"]["cx"]),
                "cy": int(btn["frame"]["cy"]),
            })
        return results
    except Exception:
        return []


# ── 粉丝 / 关注列表 ──────────────────────────────────────────

def open_followers_tab(tab: str = "fans"):
    """打开自己主页的粉丝/关注列表"""
    # tab: "互相关注" / "关注" / "fans"(粉丝) / "推荐"
    try:
        # 1. 导航到个人主页
        navigate_tab("profile")
        time.sleep(1.5)

        b = get_window_bounds()
        if not b:
            return

        # 2. 根据 tab 确定点击哪个数字区域
        # 已知：AXStaticText desc='关注' @ (1030, 391)，desc='粉丝' @ (1060, 391)
        # 可点击区域在标签上方约 16px（数字本身）
        # 相对坐标：关注 x≈73%，粉丝 x≈85%（基于 1440px 宽窗口）
        # 使用 AX 动态找标签位置

        win = _ax_window()

        if tab in ("fans", "粉丝"):
            # 找「粉丝」StaticText 标签，点击其上方数字
            label_el = _ax_find(win,
                lambda e: getattr(e, "AXRole", "") == "AXStaticText"
                          and getattr(e, "AXDescription", "") == "粉丝") if win else None
            if label_el:
                c = _ax_center(label_el)
                if c:
                    click_global(c[0], c[1] - 16, delay=1.5)
                    return
            # 兜底：固定坐标
            gx = int(b["x"] + b["w"] * 0.735)
            gy = int(b["y"] + 375)
            click_global(gx, gy, delay=1.5)

        elif tab in ("follow", "关注"):
            label_el = _ax_find(win,
                lambda e: getattr(e, "AXRole", "") == "AXStaticText"
                          and getattr(e, "AXDescription", "") == "关注") if win else None
            if label_el:
                c = _ax_center(label_el)
                if c:
                    click_global(c[0], c[1] - 16, delay=1.5)
                    return
            gx = int(b["x"] + b["w"] * 0.715)
            gy = int(b["y"] + 375)
            click_global(gx, gy, delay=1.5)

        elif tab in ("mutual", "互相关注"):
            # 互相关注通常在列表页内切换，先打开关注列表
            label_el = _ax_find(win,
                lambda e: getattr(e, "AXRole", "") == "AXStaticText"
                          and getattr(e, "AXDescription", "") == "关注") if win else None
            if label_el:
                c = _ax_center(label_el)
                if c:
                    click_global(c[0], c[1] - 16, delay=1.5)
            else:
                gx = int(b["x"] + b["w"] * 0.715)
                gy = int(b["y"] + 375)
                click_global(gx, gy, delay=1.5)

        else:
            # "推荐" 或其他，默认打开粉丝
            gx = int(b["x"] + b["w"] * 0.735)
            gy = int(b["y"] + 375)
            click_global(gx, gy, delay=1.5)

    except Exception:
        pass


def get_followers_list() -> list:
    """读取当前粉丝/关注列表的用户（AX）"""
    try:
        activate()
        win = _ax_window()
        if not win:
            return []

        b = get_window_bounds()
        # 列表区域：大致在窗口 y+100 ~ tabbar 之间，x 全宽
        list_y_min = (b["y"] + 100) if b else 0
        list_y_max = (b["y"] + b["h"] - 100) if b else 9999

        # 找所有非空 AXButton（用户卡片通常是 AXButton 或包含 StaticText）
        all_btns = _ax_find_all(win,
            lambda e: getattr(e, "AXRole", "") == "AXButton"
                      and (getattr(e, "AXDescription", "") or "").strip() != "")

        results = []
        seen = set()
        for btn in all_btns:
            c = _ax_center(btn)
            if not c:
                continue
            # 过滤出列表区域内的按钮
            if not (list_y_min <= c[1] <= list_y_max):
                continue
            desc = getattr(btn, "AXDescription", "") or ""
            # 排除导航类按钮
            if desc in ("关注", "已关注", "回复", "发送", "返回", "搜索",
                        "点赞", "收藏", "评论", "互相关注", "粉丝", "推荐"):
                continue
            if desc in seen:
                continue
            seen.add(desc)
            results.append({"name": desc, "stats": ""})

        # 如果按钮策略没拿到，尝试 AXStaticText
        if not results:
            all_texts = _ax_find_all(win,
                lambda e: getattr(e, "AXRole", "") == "AXStaticText"
                          and (getattr(e, "AXDescription", "") or "").strip() != "")
            for t in all_texts:
                c = _ax_center(t)
                if not c:
                    continue
                if not (list_y_min <= c[1] <= list_y_max):
                    continue
                desc = getattr(t, "AXDescription", "") or ""
                if desc in seen:
                    continue
                seen.add(desc)
                results.append({"name": desc, "stats": ""})

        return results
    except Exception:
        return []


def read_note_info(use_vlm: bool = False) -> dict:
    """
    读取当前笔记详情页的结构化信息（轻量版）。

    只做截图 + AX 关注状态读取，不调用 VLM（controller 层无 API key）。
    VLM 分析由上层（main.py 的 xhs_read_note）负责。

    返回: {author, is_following, likes, collects, comments, screenshot, note_type, vlm}
    """
    activate()
    result = {
        "author": "", "is_following": False,
        "likes": 0, "collects": 0, "comments": 0,
        "screenshot": "", "note_type": "image",
        "vlm": False
    }
    try:
        # AX 读取关注状态（轻量）
        win = _ax_window()
        if win:
            follow_btn = _ax_find(win,
                lambda el: getattr(el, "AXDescription", "") in ("关注", "已关注")
                           and el.AXRole == "AXButton")
            if follow_btn:
                result["is_following"] = getattr(follow_btn, "AXDescription", "") == "已关注"

        # 截图
        path = screenshot()
        result["screenshot"] = path or ""

    except Exception as e:
        result["error"] = str(e)
    return result


def get_note_image_paths() -> list:
    """截取当前笔记的图片区域，返回路径列表"""
    import subprocess, os, time
    activate()
    b = get_window_bounds()
    if not b:
        return []
    info = read_note_info()
    note_type = info.get("note_type", "image")
    os.makedirs("/tmp/xhs_imgs", exist_ok=True)
    out_path = "/tmp/xhs_imgs/note_img_0.png"
    if note_type == "video":
        # 全窗口截图
        subprocess.run(["/usr/sbin/screencapture", "-x",
            f"-l{b['id']}", out_path])
    else:
        # 图片在左侧 ~45%
        x = int(b["x"])
        y = int(b["y"] + 28)
        w = int(b["w"] * 0.47)
        h = int(b["h"] - 28 - 87)
        subprocess.run(["/usr/sbin/screencapture", "-x",
            "-R", f"{x},{y},{w},{h}", out_path])
    return [out_path] if os.path.exists(out_path) else []


def delete_comment(comment_index: int) -> bool:
    """删除评论区第 N 条评论（0-based），通过点击评论触发操作菜单后选「删除」。

    ⚠️  只能删除自己发的评论（无权限时菜单无「删除」选项）。

    工作流：
    1. AS API 找评论区用户名按钮，定位目标评论行
    2. 点击该评论文字区域 → 触发操作菜单（含「删除」）
    3. 坐标点击菜单底部「删除」（红色，最后一行）
    4. AX 点击确认弹窗的「确认」按钮
    """
    activate()
    win = _ax_window()
    try:
        # 1. 确保评论区已打开
        text_area = _ax_find(win, lambda el: getattr(el, "AXRole", "") == "AXTextArea")
        if not text_area:
            open_comments()
            time.sleep(1.5)
            win = _ax_window()

        # 2. AS API 找评论区用户名按钮，定位目标评论
        EXCLUDE = {"点赞", "收藏", "评论", "分享", "发送", "搜索", "返回"}
        win_ref = _as_window_ref()
        b = get_window_bounds()
        if not win_ref or not b:
            return False

        comment_btns = _as_find_all(win_ref,
            lambda role, desc, frame: (
                role == "AXButton"
                and desc
                and desc not in EXCLUDE
                and not desc.startswith("展开")
                and frame is not None
            ))
        comment_btns.sort(key=lambda b: b["frame"]["cy"])

        if comment_index < len(comment_btns):
            btn = comment_btns[comment_index]
            cx = int(btn["frame"]["cx"]) + 60
            cy = int(btn["frame"]["cy"])
        else:
            # fallback 坐标
            cx = int(b["x"] + b["w"] * 0.79)
            cy = int(b["y"] + b["h"] * 0.21) + comment_index * 80

        # 3. 点击评论文字触发操作菜单
        click_global(cx, cy, delay=1.2)
        time.sleep(0.8)

        # 4. 检查菜单是否出现：AX 找「删除」按钮
        win = _ax_window()
        del_btn = _ax_find(win, lambda el:
            getattr(el, "AXRole", "") == "AXButton"
            and getattr(el, "AXDescription", "") == "删除")
        if del_btn:
            click_ax(del_btn, delay=0.8)
        else:
            # 菜单用坐标：「删除」在菜单底部（y ≈ 窗口底 - 20px）
            del_x = int(b["x"] + b["w"] * 0.5)
            del_y = int(b["y"] + b["h"] * 0.96)
            click_global(del_x, del_y, delay=0.8)

        # 5. AX 点击确认弹窗的「确认」按钮
        time.sleep(0.8)
        win = _ax_window()
        confirm = _ax_find(win, lambda el:
            getattr(el, "AXRole", "") == "AXButton"
            and getattr(el, "AXDescription", "") == "确认")
        if confirm:
            click_ax(confirm, delay=0.5)
            return True

        return False
    except Exception:
        return False


# ── 视频下载 & 提取 ────────────────────────────────────────────

def download_note_video(url: str, output_dir: str = "/tmp/xhs_video") -> dict:
    """用 yt-dlp 下载小红书笔记视频"""
    import os, glob, json as _json
    result = {"success": False, "video_path": None, "title": None, "error": None}
    try:
        os.makedirs(output_dir, exist_ok=True)
        ytdlp = "/opt/homebrew/bin/yt-dlp"
        if not os.path.exists(ytdlp):
            import shutil
            ytdlp = shutil.which("yt-dlp") or "yt-dlp"
        cmd = [ytdlp, "-o", f"{output_dir}/%(id)s.%(ext)s",
               "--write-info-json", "--no-playlist", url]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        # 找下载的视频文件
        for ext in ("mp4", "mov", "webm", "flv", "m4v"):
            files = glob.glob(f"{output_dir}/*.{ext}")
            if files:
                result["video_path"] = files[-1]
                break
        # 读 info.json 取标题
        json_files = glob.glob(f"{output_dir}/*.info.json")
        if json_files:
            with open(json_files[-1]) as f:
                info = _json.load(f)
                result["title"] = info.get("title", "")
        result["success"] = result["video_path"] is not None
        if not result["success"]:
            result["error"] = r.stderr[-500:] if r.stderr else "未找到视频文件"
    except Exception as e:
        result["error"] = str(e)
    return result


def extract_video_frames(video_path: str, num_frames: int = 8,
                          output_dir: str = "/tmp/xhs_frames") -> list:
    """用 ffmpeg 从视频中均匀提取 N 帧截图，返回路径列表"""
    import os, glob, json as _json
    try:
        os.makedirs(output_dir, exist_ok=True)
        ffprobe = "/opt/homebrew/bin/ffprobe"
        ffmpeg = "/opt/homebrew/bin/ffmpeg"
        if not os.path.exists(ffprobe):
            import shutil
            ffprobe = shutil.which("ffprobe") or "ffprobe"
            ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
        # 获取时长
        r = subprocess.run([ffprobe, "-v", "quiet", "-print_format", "json",
            "-show_format", video_path], capture_output=True, text=True, timeout=30)
        info = _json.loads(r.stdout)
        duration = float(info.get("format", {}).get("duration", 0))
        if duration <= 0:
            return []
        interval = max(duration / num_frames, 1)
        out_pattern = f"{output_dir}/frame_%03d.png"
        subprocess.run([ffmpeg, "-i", video_path,
            "-vf", f"fps=1/{interval:.2f}",
            "-vframes", str(num_frames), out_pattern, "-y"],
            capture_output=True, timeout=60)
        return sorted(glob.glob(f"{output_dir}/frame_*.png"))
    except Exception as e:
        return []


def get_video_info(video_path: str) -> dict:
    """用 ffprobe 获取视频基本信息"""
    import os, json as _json
    result = {"duration": 0.0, "width": 0, "height": 0, "fps": 0.0, "size_mb": 0.0}
    try:
        ffprobe = "/opt/homebrew/bin/ffprobe"
        if not os.path.exists(ffprobe):
            import shutil
            ffprobe = shutil.which("ffprobe") or "ffprobe"
        r = subprocess.run([ffprobe, "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", video_path],
            capture_output=True, text=True, timeout=30)
        info = _json.loads(r.stdout)
        fmt = info.get("format", {})
        result["duration"] = float(fmt.get("duration", 0))
        result["size_mb"] = round(os.path.getsize(video_path) / 1024 / 1024, 2)
        for stream in info.get("streams", []):
            if stream.get("codec_type") == "video":
                result["width"] = stream.get("width", 0)
                result["height"] = stream.get("height", 0)
                fps_str = stream.get("avg_frame_rate", "0/1")
                try:
                    num, den = fps_str.split("/")
                    result["fps"] = round(float(num) / float(den), 2) if float(den) else 0.0
                except: pass
                break
    except Exception as e:
        result["error"] = str(e)
    return result


def extract_current_note_video(output_dir: str = "/tmp/xhs_video") -> dict:
    """一键提取当前笔记视频：获取URL → 下载 → 提取帧"""
    result = {"url": "", "success": False, "video_path": None,
              "frames": [], "video_info": {}, "error": None}
    try:
        url = get_note_url()
        result["url"] = url
        if not url:
            result["error"] = "无法获取笔记 URL，请确认当前页面是笔记详情页"
            return result
        dl = download_note_video(url, output_dir)
        result["success"] = dl["success"]
        result["video_path"] = dl.get("video_path")
        result["error"] = dl.get("error")
        if dl["success"] and dl["video_path"]:
            result["frames"] = extract_video_frames(dl["video_path"], num_frames=8)
            result["video_info"] = get_video_info(dl["video_path"])
    except Exception as e:
        result["error"] = str(e)
    return result
