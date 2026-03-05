"""
纯视觉RPA工具 - 快速原型
基于屏幕截图 + 通义千问视觉模型API实现

核心流程:
  1. 缩略图 → 千问返回粗坐标
  2. 从全分辨率截图裁剪目标区域 → 千问精确定位
  3. 坐标映射 → 执行操作 → 截图验证

依赖安装:
    pip install mss pyautogui openai pillow
"""

import os
import io
import re
import json
import time
import base64
import logging
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from pathlib import Path

import mss
import pyautogui
from PIL import Image

from openai import OpenAI

# ============================================================
# 配置
# ============================================================

LOG_DIR = Path("./rpa_logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / "rpa.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("VisualRPA")

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.25


# ============================================================
# 数据模型
# ============================================================

@dataclass
class ActionPlan:
    target_element: str = ""
    x: int = 0
    y: int = 0
    action: str = "click"
    text: str = ""
    keys: str = ""
    scroll_direction: str = "down"
    scroll_amount: int = 3
    confidence: float = 0.0
    reasoning: str = ""


@dataclass
class StepResult:
    step_index: int
    instruction: str
    action_plan: Optional[ActionPlan]
    success: bool
    verification_message: str = ""
    retries: int = 0
    screenshots: list = field(default_factory=list)


# ============================================================
# 1. 屏幕捕获模块
# ============================================================

class ScreenCapture:

    def __init__(self):
        self.sct = mss.mss()
        phys = self.sct.monitors[1]
        logic = pyautogui.size()
        logger.info(
            f"屏幕: 物理={phys['width']}x{phys['height']}, "
            f"逻辑={logic.width}x{logic.height}"
        )

    def capture_full(self) -> Image.Image:
        """截取全屏, 原始分辨率"""
        raw = self.sct.grab(self.sct.monitors[1])
        return Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")

    def resize(self, img: Image.Image, max_width: int) -> Image.Image:
        if img.width <= max_width:
            return img.copy()
        ratio = max_width / img.width
        return img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)

    def to_base64(self, img: Image.Image, fmt: str = "JPEG", quality: int = 85) -> str:
        buf = io.BytesIO()
        if fmt == "JPEG":
            img.save(buf, format=fmt, quality=quality)
        else:
            img.save(buf, format=fmt)
        return base64.b64encode(buf.getvalue()).decode()

    def save(self, img: Image.Image, tag: str = "") -> str:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        path = LOG_DIR / f"ss_{tag}_{ts}.png"
        img.save(str(path))
        return str(path)

    def crop_fullres(self, full_img: Image.Image, cx: int, cy: int,
                     half_size: int = 200) -> tuple[Image.Image, int, int]:
        """
        从全分辨率图中裁剪 (2*half_size) 正方形区域
        返回 (裁剪图, 裁剪区左上角x, 裁剪区左上角y)
        """
        x1 = max(0, cx - half_size)
        y1 = max(0, cy - half_size)
        x2 = min(full_img.width, cx + half_size)
        y2 = min(full_img.height, cy + half_size)
        return full_img.crop((x1, y1, x2, y2)), x1, y1

    def img_to_screen(self, px: int, py: int, img: Image.Image) -> tuple[int, int]:
        """图片像素 → pyautogui 屏幕坐标"""
        sw, sh = pyautogui.size()
        iw, ih = img.size
        return int(px * sw / iw), int(py * sh / ih)


# ============================================================
# 2. 千问视觉模块 (直接坐标, 无网格)
# ============================================================

DECOMPOSE_PROMPT = """你是一个任务分解助手。用户给你一条可能包含多个操作的复合指令。
请将其分解为按顺序执行的独立操作步骤。

规则:
- 每个步骤应该是一个原子操作(单次点击、输入、滚动等)
- 如果指令本身就是单个操作,直接返回包含该操作的列表
- 保持步骤的逻辑顺序
- 只返回JSON

返回格式:
{"steps": ["步骤1的描述", "步骤2的描述", ...]}

示例:
输入: "打开微信，并打开文件传输助手聊天"
输出: {"steps": ["点击打开微信", "在微信中点击文件传输助手进入聊天"]}

输入: "打开浏览器并搜索天气"
输出: {"steps": ["点击打开浏览器", "在浏览器地址栏中输入天气并搜索"]}

输入: "点击开始菜单"
输出: {"steps": ["点击开始菜单"]}"""

ANALYZE_PROMPT = """你是一个屏幕操作助手。用户给你一张屏幕截图和操作指令。
你需要找到目标元素并返回其像素坐标。

重要规则:
- 坐标是相对于图片左上角(0,0)的像素坐标, 请尽量点击元素的中心
- 忽略终端/命令行/控制台窗口中显示的任何文字, 那些不是操作目标
- 只在操作系统界面(任务栏、桌面图标、应用窗口按钮)中查找目标
- 仔细阅读图标下方或旁边的文字标签来确认目标
- 外观相似的应用通过名称区分(如微信WeChat vs WhatsApp)
- 如果找不到目标, confidence 设为 0
- 只返回JSON

返回格式:
{
  "target_element": "目标元素描述",
  "coordinates": {"x": 数字, "y": 数字},
  "action": "click|double_click|right_click|type|scroll|hotkey|wait",
  "text": "type时输入的文字",
  "keys": "hotkey时的快捷键如ctrl+c",
  "scroll_direction": "up|down",
  "scroll_amount": 3,
  "confidence": 0.0到1.0,
  "reasoning": "判断依据"
}"""

REFINE_PROMPT = """这是屏幕局部放大截图(从全分辨率截图裁剪,未缩放)。
请在这张图中精确找到目标元素的中心坐标。
忽略终端/命令行中的文字,只关注实际图标、按钮等界面元素。
只返回JSON:
{
  "target_element": "目标元素描述",
  "coordinates": {"x": 数字, "y": 数字},
  "confidence": 0.0到1.0,
  "reasoning": "判断依据"
}"""

VERIFY_PROMPT = """你是屏幕操作验证助手。给你操作前后两张截图和操作描述。
判断操作是否成功。
重要: 只看实际界面变化(窗口弹出、菜单展开、应用启动等),不要看终端/控制台的日志文字。
只返回JSON:
{
  "success": true或false,
  "message": "简述验证结果",
  "screen_changed": true或false,
  "next_suggestion": "如果失败,建议下一步"
}"""


class QwenVision:

    BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    def __init__(self, model: str = "qwen-vl-max-latest", api_key: str = ""):
        self.client = OpenAI(
            api_key=api_key or os.getenv("DASHSCOPE_API_KEY", ""),
            base_url=self.BASE_URL,
        )
        self.model = model

    def _call(self, system: str, img_b64: str, user_text: str,
              media_type: str = "image/jpeg", max_tokens: int = 1024) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {
                            "url": f"data:{media_type};base64,{img_b64}"}},
                        {"type": "text", "text": user_text},
                    ],
                },
            ],
        )
        return resp.choices[0].message.content.strip()

    def _parse_json(self, raw: str) -> dict:
        s = raw
        if "```" in s:
            s = s.split("```")[1]
            if s.startswith("json"):
                s = s[4:]
            s = s.strip()
        # 修复模型常见的畸形坐标: {"x": 85, 47} → {"x": 85, "y": 47}
        s = re.sub(
            r'"x"\s*:\s*(\d+)\s*,\s*(\d+)\s*}',
            r'"x": \1, "y": \2}',
            s,
        )
        # 修复另一种畸形: {"x": 453, "540"} → {"x": 453, "y": 540}
        s = re.sub(
            r'"x"\s*:\s*(\d+)\s*,\s*"(\d+)"\s*}',
            r'"x": \1, "y": \2}',
            s,
        )
        return json.loads(s)

    def _extract_coords(self, data: dict) -> tuple[int, int]:
        """从返回数据中提取坐标, 兼容多种格式"""
        coords = data.get("coordinates", {})
        if isinstance(coords, dict):
            x = coords.get("x", 0)
            y = coords.get("y", 0)
        elif isinstance(coords, (list, tuple)) and len(coords) >= 2:
            x, y = coords[0], coords[1]
        else:
            x, y = 0, 0
        return int(x), int(y)

    def decompose(self, instruction: str) -> list[str]:
        """将复合指令分解为多个独立步骤"""
        logger.info(f"[分解指令] {instruction}")
        resp = self.client.chat.completions.create(
            model=self.model,
            max_tokens=512,
            messages=[
                {"role": "system", "content": DECOMPOSE_PROMPT},
                {"role": "user", "content": instruction},
            ],
        )
        raw = resp.choices[0].message.content.strip()
        try:
            data = self._parse_json(raw)
            steps = data.get("steps", [instruction])
            if not steps:
                steps = [instruction]
            logger.info(f"分解结果: {len(steps)} 步 → {steps}")
            return steps
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"指令分解失败: {e}, 作为单步执行")
            return [instruction]

    def locate_rough(self, img_b64: str, instruction: str) -> dict:
        """第一轮: 在缩略图上粗定位"""
        logger.info(f"[粗定位] {instruction}")
        raw = self._call(ANALYZE_PROMPT, img_b64, f"当前任务: {instruction}")
        logger.debug(f"粗定位返回: {raw}")
        try:
            data = self._parse_json(raw)
            x, y = self._extract_coords(data)
            data["_x"] = x
            data["_y"] = y
            logger.info(f"粗定位: ({x},{y}) 目标={data.get('target_element','')} "
                        f"置信度={data.get('confidence',0)}")
            return data
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"粗定位解析失败: {e}\n原文: {raw[:300]}")
            return {"_x": 0, "_y": 0, "confidence": 0, "reasoning": f"解析失败: {raw[:200]}"}

    def locate_precise(self, crop_b64: str, instruction: str) -> dict:
        """第二轮: 在全分辨率裁剪图上精确定位"""
        logger.info("[精定位] 在裁剪区域中精确定位...")
        raw = self._call(REFINE_PROMPT, crop_b64,
                         f"当前任务: {instruction}", media_type="image/png")
        logger.debug(f"精定位返回: {raw}")
        try:
            data = self._parse_json(raw)
            x, y = self._extract_coords(data)
            data["_x"] = x
            data["_y"] = y
            logger.info(f"精定位: ({x},{y}) 目标={data.get('target_element','')} "
                        f"置信度={data.get('confidence',0)}")
            return data
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"精定位解析失败: {e}")
            return {"_x": 0, "_y": 0, "confidence": 0, "reasoning": "解析失败"}

    def verify(self, before_b64: str, after_b64: str, desc: str) -> dict:
        logger.info("验证操作...")
        resp = self.client.chat.completions.create(
            model=self.model, max_tokens=512,
            messages=[
                {"role": "system", "content": VERIFY_PROMPT},
                {"role": "user", "content": [
                    {"type": "text", "text": "【操作前】:"},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/jpeg;base64,{before_b64}"}},
                    {"type": "text", "text": "【操作后】:"},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/jpeg;base64,{after_b64}"}},
                    {"type": "text", "text": f"操作: {desc}\n请判断是否成功。"},
                ]},
            ],
        )
        raw = resp.choices[0].message.content.strip()
        try:
            return self._parse_json(raw)
        except json.JSONDecodeError:
            return {"success": None, "message": raw[:200]}


# ============================================================
# 3. 操作执行
# ============================================================

class ActionExecutor:

    def execute(self, plan: ActionPlan):
        action = plan.action.lower().replace(" ", "_")
        logger.info(f"执行: {action} @ ({plan.x}, {plan.y})")

        if action == "click":
            pyautogui.click(plan.x, plan.y)
        elif action == "double_click":
            pyautogui.doubleClick(plan.x, plan.y)
        elif action == "right_click":
            pyautogui.rightClick(plan.x, plan.y)
        elif action == "type":
            if plan.x and plan.y:
                pyautogui.click(plan.x, plan.y)
                time.sleep(0.5)
            self._type_text(plan.text)
        elif action == "hotkey":
            keys = [k.strip() for k in plan.keys.split("+")]
            pyautogui.hotkey(*keys)
        elif action == "scroll":
            amt = plan.scroll_amount if plan.scroll_direction == "down" else -plan.scroll_amount
            pyautogui.scroll(amt, x=plan.x, y=plan.y)
        elif action == "wait":
            time.sleep(2)
        else:
            pyautogui.click(plan.x, plan.y)

    @staticmethod
    def _type_text(text: str):
        import subprocess, platform
        system = platform.system()
        if system == "Darwin":
            subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)
            pyautogui.hotkey("command", "v")
        elif system == "Windows":
            import ctypes
            import ctypes.wintypes as w
            CF_UNICODETEXT = 13
            GMEM_MOVEABLE = 0x0002
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            kernel32.GlobalAlloc.restype = ctypes.c_void_p
            kernel32.GlobalAlloc.argtypes = [w.UINT, ctypes.c_size_t]
            kernel32.GlobalLock.restype = ctypes.c_void_p
            kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
            kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
            user32.SetClipboardData.argtypes = [w.UINT, ctypes.c_void_p]
            data = (text + "\0").encode("utf-16-le")
            user32.OpenClipboard(0)
            user32.EmptyClipboard()
            h = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
            p = kernel32.GlobalLock(h)
            ctypes.memmove(p, data, len(data))
            kernel32.GlobalUnlock(h)
            user32.SetClipboardData(CF_UNICODETEXT, h)
            user32.CloseClipboard()
            pyautogui.hotkey("ctrl", "v")
        else:
            subprocess.run(["xclip", "-selection", "clipboard"],
                           input=text.encode("utf-8"), check=True)
            pyautogui.hotkey("ctrl", "v")


# ============================================================
# 4. 主控制器
# ============================================================

class VisualRPA:
    """
    纯视觉RPA引擎

    定位流程:
      1. 全屏截图 → 缩小到1280px → 千问粗定位 → 获得大致坐标
      2. 从全分辨率截图裁剪目标区域(400×400) → 千问精确定位
      3. 坐标映射到屏幕 → 执行 → 验证
    """

    def __init__(
        self,
        model: str = "qwen-vl-max-latest",
        api_key: str = "",
        max_retries: int = 3,
        confidence_threshold: float = 0.5,
        verify_actions: bool = True,
        post_action_wait: float = 1.0,
        thumbnail_width: int = 1280,
        crop_half_size: int = 200,
    ):
        self.cap = ScreenCapture()
        self.vision = QwenVision(model=model, api_key=api_key)
        self.executor = ActionExecutor()

        self.max_retries = max_retries
        self.conf_threshold = confidence_threshold
        self.verify_actions = verify_actions
        self.post_action_wait = post_action_wait
        self.thumbnail_width = thumbnail_width
        self.crop_half_size = crop_half_size

        self.history: list[StepResult] = []

    def execute_step(self, instruction: str, step_index: int = 0) -> StepResult:
        result = StepResult(step_index=step_index, instruction=instruction,
                            action_plan=None, success=False)

        for attempt in range(self.max_retries):
            logger.info(f"--- 步骤 {step_index} 尝试 {attempt+1}/{self.max_retries} ---")
            logger.info(f"指令: {instruction}")

            # 1. 截取全分辨率 + 缩略图
            full_img = self.cap.capture_full()
            thumb = self.cap.resize(full_img, self.thumbnail_width)
            thumb_b64 = self.cap.to_base64(thumb)
            self.cap.save(thumb, f"step{step_index}_thumb")

            # 2. 第一轮: 缩略图粗定位
            rough = self.vision.locate_rough(thumb_b64, instruction)
            rough_conf = float(rough.get("confidence", 0))

            if rough_conf < self.conf_threshold:
                logger.warning(f"粗定位置信度不足: {rough_conf}")
                result.retries = attempt + 1
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
                result.verification_message = f"定位失败: {rough.get('reasoning','')}"
                return result

            # 缩略图坐标 → 全分辨率坐标
            thumb_x, thumb_y = rough["_x"], rough["_y"]
            scale = full_img.width / thumb.width
            full_x = int(thumb_x * scale)
            full_y = int(thumb_y * scale)
            logger.info(f"缩略图({thumb_x},{thumb_y}) → 全图({full_x},{full_y})")

            # 3. 第二轮: 从全分辨率图裁剪 → 精确定位
            crop, crop_ox, crop_oy = self.cap.crop_fullres(
                full_img, full_x, full_y, self.crop_half_size
            )
            crop_b64 = self.cap.to_base64(crop, fmt="PNG")
            self.cap.save(crop, f"step{step_index}_crop")

            precise = self.vision.locate_precise(crop_b64, instruction)
            precise_conf = float(precise.get("confidence", 0))

            if precise_conf >= self.conf_threshold and precise["_x"] > 0:
                final_full_x = crop_ox + precise["_x"]
                final_full_y = crop_oy + precise["_y"]
                logger.info(f"精定位: 裁剪内({precise['_x']},{precise['_y']}) "
                            f"→ 全图({final_full_x},{final_full_y})")
            else:
                final_full_x, final_full_y = full_x, full_y
                logger.info(f"精定位失败, 用粗坐标({full_x},{full_y})")

            # 4. 全分辨率坐标 → 屏幕坐标
            screen_x, screen_y = self.cap.img_to_screen(
                final_full_x, final_full_y, full_img
            )
            logger.info(f"屏幕坐标: ({screen_x},{screen_y})")

            plan = ActionPlan(
                target_element=rough.get("target_element", ""),
                x=screen_x, y=screen_y,
                action=rough.get("action", "click"),
                text=rough.get("text", ""),
                keys=rough.get("keys", ""),
                scroll_direction=rough.get("scroll_direction", "down"),
                scroll_amount=int(rough.get("scroll_amount", 3)),
                confidence=precise_conf if precise_conf >= self.conf_threshold else rough_conf,
                reasoning=rough.get("reasoning", ""),
            )

            # 修正: 指令含"输入"但模型返回click时, 强制改为type并提取文本
            if plan.action == "click" and not plan.text:
                m = re.search(r"输入[\"'「]?(.+?)[\"'」]?(?:$|[,，。.并且然后])", instruction)
                if m:
                    plan.action = "type"
                    plan.text = m.group(1).strip()
                    logger.info(f"动作修正: click → type, 文本='{plan.text}'")

            result.action_plan = plan

            # 5. 执行
            self.executor.execute(plan)
            time.sleep(self.post_action_wait)

            # 6. 验证
            if self.verify_actions:
                after_img = self.cap.capture_full()
                after_thumb = self.cap.resize(after_img, self.thumbnail_width)
                after_b64 = self.cap.to_base64(after_thumb)
                self.cap.save(after_thumb, f"step{step_index}_after")

                v = self.vision.verify(
                    thumb_b64, after_b64,
                    f"{plan.action} '{plan.target_element}' @ ({plan.x},{plan.y}), 指令: {instruction}"
                )
                v_ok = v.get("success")
                v_msg = v.get("message", "")
                logger.info(f"验证: success={v_ok}, {v_msg}")

                if v_ok is True:
                    result.success = True
                    result.verification_message = v_msg
                    result.retries = attempt
                    return result
                elif v_ok is False:
                    result.retries = attempt + 1
                    result.verification_message = v_msg
                    if attempt < self.max_retries - 1:
                        time.sleep(1)
                        continue
                else:
                    result.success = True
                    result.verification_message = v_msg
                    result.retries = attempt
                    return result
            else:
                result.success = True
                result.retries = attempt
                return result

        return result

    def run_task(self, steps: list[str], stop_on_failure: bool = True) -> list[StepResult]:
        # 先将每条指令分解为原子步骤
        all_steps = []
        for raw_step in steps:
            sub_steps = self.vision.decompose(raw_step)
            all_steps.extend(sub_steps)

        logger.info(f"===== 任务开始: {len(all_steps)} 步 =====")
        results = []
        for i, step in enumerate(all_steps):
            r = self.execute_step(step, step_index=i)
            results.append(r)
            self.history.append(r)
            logger.info(f"步骤{i}: {'OK' if r.success else 'FAIL'} | {step}")
            if not r.success and stop_on_failure:
                break
        logger.info("===== 任务结束 =====")
        self._summary(results)
        return results

    def interactive(self):
        print("\n" + "=" * 50)
        print("  视觉 RPA - 交互模式")
        print("  输入指令回车执行, quit 退出")
        print("=" * 50)
        idx = 0
        while True:
            try:
                cmd = input(f"\n[{idx}] > ").strip()
            except (KeyboardInterrupt, EOFError):
                break
            if not cmd:
                continue
            if cmd.lower() == "quit":
                break
            if cmd.lower() == "history":
                self._summary(self.history)
                continue
            r = self.execute_step(cmd, step_index=idx)
            self.history.append(r)
            print(f"{'OK' if r.success else 'FAIL'} | {r.verification_message}")
            idx += 1

    def _summary(self, results: list[StepResult]):
        for r in results:
            s = "OK" if r.success else "FAIL"
            print(f"  [{s}] 步骤{r.step_index}: {r.instruction}")
            if r.action_plan:
                print(f"       {r.action_plan.action} @ ({r.action_plan.x},{r.action_plan.y})")
        ok = sum(1 for r in results if r.success)
        print(f"  {ok}/{len(results)} 成功")


# ============================================================
# 入口
# ============================================================

def main():
    import argparse
    p = argparse.ArgumentParser(description="视觉 RPA")
    p.add_argument("--mode", choices=["interactive", "task"], default="interactive")
    p.add_argument("--model", default="qwen-vl-max-latest")
    p.add_argument("--api-key", default="")
    p.add_argument("--no-verify", action="store_true")
    p.add_argument("--task", nargs="+")
    args = p.parse_args()

    rpa = VisualRPA(
        model=args.model,
        api_key=args.api_key,
        verify_actions=not args.no_verify,
    )
    if args.mode == "task" and args.task:
        rpa.run_task(args.task)
    else:
        rpa.interactive()


if __name__ == "__main__":
    main()
