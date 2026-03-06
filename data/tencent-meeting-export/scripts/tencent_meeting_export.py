#!/usr/bin/env python3
"""
腾讯会议录制转写导出工具
========================

从腾讯会议分享链接中导出完整的会议转写内容，包括：
- AI 全文摘要
- 智能章节
- 关键节点（屏幕共享、成员加入/离开等）
- 完整语音转写（含说话人识别和时间戳）

原理：
    通过 Playwright 无头浏览器加载分享页面，拦截页面加载过程中的 API 响应，
    提取转写数据后格式化为 Markdown 文件。无需登录，仅需公开分享链接。

依赖：
    pip install playwright
    playwright install chromium

用法：
    python scripts/tencent_meeting_export.py <分享链接> [-o 输出文件] [--json] [--timeout 秒数]

示例：
    python scripts/tencent_meeting_export.py https://meeting.tencent.com/cw/Nxdb8DG997
    python scripts/tencent_meeting_export.py https://meeting.tencent.com/cw/Nxdb8DG997 -o 会议纪要.md
    python scripts/tencent_meeting_export.py https://meeting.tencent.com/cw/Nxdb8DG997 --json -o raw.json
"""

import argparse
import asyncio
import json
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Any

try:
    from playwright.async_api import async_playwright, Response
except ImportError:
    print("错误: 缺少 playwright 依赖。请执行以下命令安装：")
    print("  pip install playwright")
    print("  playwright install chromium")
    sys.exit(1)


# ==============================================================================
# 数据模型
# ==============================================================================

@dataclass
class MeetingData:
    """会议数据容器"""
    url: str = ""
    title: str = ""
    meeting_code: str = ""
    paragraphs: list[dict] = field(default_factory=list)
    summary: str = ""
    chapters: list[dict] = field(default_factory=list)
    critical_nodes: list[dict] = field(default_factory=list)
    record_info: dict = field(default_factory=dict)

    @property
    def speakers(self) -> list[str]:
        """获取所有发言人列表"""
        names = set()
        for p in self.paragraphs:
            sp = p.get("speaker", {})
            if isinstance(sp, dict) and sp.get("user_name"):
                names.add(sp["user_name"])
        return sorted(names)


# ==============================================================================
# 核心抓取逻辑
# ==============================================================================

class TranscriptCapture:
    """基于 Playwright 的腾讯会议转写抓取器"""

    # API URL 关键字匹配表
    API_PATTERNS = {
        "minutes/detail": "_on_minutes_detail",
        "get-full-summary": "_on_summary",
        "get-chapter": "_on_chapters",
        "get-critical-node": "_on_critical_nodes",
        "common-record-info": "_on_record_info",
    }

    def __init__(self, url: str, timeout: int = 120, verbose: bool = True):
        self.url = url
        self.timeout = timeout
        self.verbose = verbose
        self.data = MeetingData(url=url)

    def _log(self, msg: str):
        if self.verbose:
            print(msg)

    # ---- API 响应处理器 ----

    def _on_minutes_detail(self, payload: dict):
        paragraphs = payload.get("minutes", {}).get("paragraphs", [])
        if paragraphs:
            self.data.paragraphs.extend(paragraphs)
            self._log(f"  [转写] +{len(paragraphs)} 段 (累计: {len(self.data.paragraphs)})")

    def _on_summary(self, payload: dict):
        s = payload.get("data", {}).get("full_summary", "")
        if s:
            self.data.summary = s
            self._log(f"  [摘要] {len(s)} 字")

    def _on_chapters(self, payload: dict):
        ch_list = payload.get("data", {}).get("chapter_list", [])
        if ch_list and len(ch_list) > len(self.data.chapters):
            self.data.chapters = list(ch_list)
            self._log(f"  [章节] {len(ch_list)} 个")

    def _on_critical_nodes(self, payload: dict):
        nodes = payload.get("data", {}).get("critical_nodes", [])
        if nodes:
            self.data.critical_nodes = list(nodes)
            self._log(f"  [节点] {len(nodes)} 个")

    def _on_record_info(self, payload: dict):
        info = payload.get("data", {})
        if info:
            self.data.record_info = info
            self.data.title = info.get("subject", "") or info.get("title", "")
            self.data.meeting_code = info.get("meeting_code", "")
            self._log(f"  [信息] 会议: {self.data.title or '(未命名)'}")

    # ---- 响应拦截 ----

    async def _handle_response(self, response: Response):
        """拦截并分发 API 响应"""
        url = response.url
        try:
            if response.status != 200:
                return
            ct = response.headers.get("content-type", "")
            if "json" not in ct and "application" not in ct:
                return

            body = await response.text()
            if not body or len(body) < 10:
                return

            data = json.loads(body)
            if data.get("code") != 0:
                return

            # 分发到对应的处理器
            for pattern, handler_name in self.API_PATTERNS.items():
                if pattern in url:
                    getattr(self, handler_name)(data)
                    break
        except Exception:
            pass

    # ---- 页面滚动加载 ----

    async def _scroll_to_load_all(self, page):
        """滚动页面加载全部转写内容（转写为懒加载）"""
        self._log("滚动加载转写内容...")

        scroll_js = """
        () => {
            // 尝试各种可能的容器选择器
            const selectors = [
                '[class*="minutes"]', '[class*="transcript"]', '[class*="subtitle"]',
                '[class*="minutesPanel"]', '[class*="subtitlePanel"]',
                '[class*="rightPanel"]', '[class*="siderContent"]',
            ];
            for (const sel of selectors) {
                const el = document.querySelector(sel);
                if (el && el.scrollHeight > el.clientHeight) {
                    el.scrollTop = el.scrollHeight;
                }
            }
            // 备选：找到所有可滚动的大元素
            document.querySelectorAll('*').forEach(el => {
                if (el.scrollHeight > el.clientHeight + 100 && el.clientHeight > 200) {
                    el.scrollTop = el.scrollHeight;
                }
            });
            window.scrollTo(0, document.body.scrollHeight);
        }
        """
        stale_rounds = 0
        max_stale = 10  # 连续没有新数据的最大轮次
        for i in range(50):
            prev_count = len(self.data.paragraphs)
            try:
                await page.evaluate(scroll_js)
            except Exception:
                pass
            await asyncio.sleep(1.5)

            if len(self.data.paragraphs) > prev_count:
                stale_rounds = 0
                self._log(f"  滚动 {i+1}: {len(self.data.paragraphs)} 段")
            else:
                stale_rounds += 1
                if stale_rounds >= max_stale:
                    break

    # ---- 主入口 ----

    async def capture(self) -> MeetingData:
        """启动浏览器抓取会议转写数据"""
        self._log(f"启动浏览器...")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/131.0.0.0 Safari/537.36"
                ),
                locale="zh-CN",
                viewport={"width": 1920, "height": 1080},
            )
            page = await context.new_page()
            page.on("response", self._handle_response)

            self._log(f"加载页面: {self.url}")
            try:
                await page.goto(
                    self.url, wait_until="networkidle",
                    timeout=self.timeout * 1000,
                )
            except Exception as e:
                self._log(f"页面加载提示: {e}")

            title = await page.title()
            if not self.data.title:
                self.data.title = title
            self._log(f"页面标题: {title}")

            # 等待初始 API 响应
            await asyncio.sleep(5)

            # 点击"转写"标签页
            self._log("切换到转写标签...")
            try:
                tab = await page.query_selector("text=转写")
                if tab and await tab.is_visible():
                    await tab.click()
                    await asyncio.sleep(3)
                    self._log("  已切换")
                else:
                    self._log("  未找到转写标签，尝试继续...")
            except Exception:
                self._log("  切换失败，尝试继续...")

            # 滚动加载全部转写
            await self._scroll_to_load_all(page)

            await browser.close()

        self._log(f"\n抓取完成: {len(self.data.paragraphs)} 段转写, "
                   f"{len(self.data.chapters)} 章节, "
                   f"{len(self.data.summary)} 字摘要")
        return self.data


# ==============================================================================
# 格式化输出
# ==============================================================================

def ms_to_time(ms: int | str) -> str:
    """将毫秒时间戳转换为 HH:MM:SS 格式"""
    ms = int(ms)
    s = ms // 1000
    m = s // 60
    h = m // 60
    return f"{h:02d}:{m % 60:02d}:{s % 60:02d}"


NODE_TYPE_MAP = {
    "share_screen_open": "开始共享屏幕",
    "share_screen_close": "停止共享屏幕",
    "member_join": "加入会议",
    "member_leave": "离开会议",
}


def format_markdown(data: MeetingData) -> str:
    """将会议数据格式化为 Markdown"""
    lines: list[str] = []

    # 标题与元信息
    lines.append(f"# 会议纪要: {data.title or '(未命名)'}")
    lines.append("")
    if data.meeting_code:
        lines.append(f"- **会议代码**: {data.meeting_code}")
    if data.speakers:
        lines.append(f"- **参会者**: {', '.join(data.speakers)}")
    lines.append(f"- **来源**: {data.url}")
    lines.append("")

    # AI 摘要
    if data.summary:
        lines.append("## AI 全文摘要")
        lines.append("")
        lines.append(data.summary)
        lines.append("")

    # 智能章节
    if data.chapters:
        lines.append("## 智能章节")
        lines.append("")
        for ch in data.chapters:
            t = ms_to_time(ch.get("start_time", 0))
            title = ch.get("title", "")
            summary = ch.get("summary", "")
            lines.append(f"### [{t}] {title}")
            if summary:
                lines.append("")
                lines.append(summary)
            lines.append("")

    # 关键节点
    if data.critical_nodes:
        lines.append("## 关键节点")
        lines.append("")
        for node in data.critical_nodes:
            t = ms_to_time(node.get("node_time", 0))
            ntype = node.get("node_type", "")
            name = node.get("nick_name", "")
            desc = NODE_TYPE_MAP.get(ntype, ntype)
            lines.append(f"- [{t}] {name} - {desc}")
        lines.append("")

    # 完整转写
    if data.paragraphs:
        lines.append("## 会议转写全文")
        lines.append("")

        sorted_paras = sorted(data.paragraphs, key=lambda p: int(p.get("start_time", 0)))
        current_speaker = None

        for para in sorted_paras:
            # 提取说话人
            speaker_obj = para.get("speaker", {})
            speaker = speaker_obj.get("user_name", "") if isinstance(speaker_obj, dict) else ""
            start_time = para.get("start_time", 0)

            # 从 sentences -> words -> text 构建文本
            sentences = para.get("sentences", [])
            text_parts: list[str] = []
            for sent in sentences:
                words = sent.get("words", [])
                if words:
                    sent_text = "".join(w.get("text", "") for w in words)
                else:
                    sent_text = sent.get("text", "")
                if sent_text:
                    text_parts.append(sent_text)

            text = "".join(text_parts)
            if not text.strip():
                continue

            time_str = ms_to_time(start_time)

            # 说话人变更时插入标题行
            if speaker != current_speaker:
                current_speaker = speaker
                lines.append("")
                if speaker:
                    lines.append(f"**{speaker}** [{time_str}]")
                else:
                    lines.append(f"[{time_str}]")

            lines.append(f"> {text}")

    return "\n".join(lines)


# ==============================================================================
# CLI 入口
# ==============================================================================

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="腾讯会议录制转写导出工具",
        epilog="示例: python %(prog)s https://meeting.tencent.com/cw/xxxxx -o 会议纪要.md",
    )
    parser.add_argument(
        "url",
        help="腾讯会议分享链接 (例: https://meeting.tencent.com/cw/xxxxx)",
    )
    parser.add_argument(
        "-o", "--output",
        help="输出文件路径 (默认: ./meeting_transcript.md)",
        default="meeting_transcript.md",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="同时导出原始 JSON 数据",
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="仅导出原始 JSON 数据（不生成 Markdown）",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="页面加载超时时间（秒，默认 60）",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="静默模式，不输出过程信息",
    )
    return parser.parse_args(argv)


async def async_main(args: argparse.Namespace):
    # 验证 URL
    if not re.match(r"https?://meeting\.tencent\.com/", args.url):
        print(f"警告: URL 不像是腾讯会议链接: {args.url}")
        print("  预期格式: https://meeting.tencent.com/cw/xxxxx")

    # 抓取数据
    capture = TranscriptCapture(
        url=args.url,
        timeout=args.timeout,
        verbose=not args.quiet,
    )
    data = await capture.capture()

    if not data.paragraphs:
        print("警告: 未抓取到任何转写内容。可能原因：")
        print("  1. 该会议未开启转写/字幕功能")
        print("  2. 分享链接已过期或无权限")
        print("  3. 页面结构已更新，需要调整脚本")
        if not data.summary and not data.chapters:
            return

    # 输出 JSON
    if args.json or args.json_only:
        json_path = args.output.rsplit(".", 1)[0] + ".json" if not args.json_only else args.output
        raw = {
            "url": data.url,
            "title": data.title,
            "meeting_code": data.meeting_code,
            "speakers": data.speakers,
            "paragraphs": data.paragraphs,
            "summary": data.summary,
            "chapters": data.chapters,
            "critical_nodes": data.critical_nodes,
            "record_info": data.record_info,
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(raw, f, ensure_ascii=False, indent=2)
        print(f"原始数据已保存: {json_path}")
        if args.json_only:
            return

    # 输出 Markdown
    md = format_markdown(data)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(md)

    # 统计信息
    print(f"\n{'=' * 50}")
    print(f"导出完成!")
    print(f"  文件: {args.output}")
    print(f"  标题: {data.title or '(未命名)'}")
    print(f"  转写: {len(data.paragraphs)} 段")
    print(f"  章节: {len(data.chapters)} 个")
    print(f"  摘要: {len(data.summary)} 字")
    print(f"  节点: {len(data.critical_nodes)} 个")
    if data.speakers:
        print(f"  发言人: {', '.join(data.speakers)}")
    print(f"{'=' * 50}")


def main(argv: list[str] | None = None):
    args = parse_args(argv)
    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()
