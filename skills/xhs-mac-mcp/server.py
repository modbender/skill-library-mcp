#!/usr/bin/env python3
"""
xhs-mac-mcp / server.py
通过 Accessibility API 控制 Mac 小红书 App 的 MCP server。

前提条件：
  - Mac 安装了 rednote（小红书）App
  - Terminal 已获得辅助功能权限（系统设置 → 隐私与安全 → 辅助功能）
  - rednote App 在屏幕上可见（不能最小化/锁屏）
"""

import asyncio
import base64
import json
import sys
import time
from typing import Any

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent, ImageContent
except ImportError:
    print("请先安装 mcp: uv add mcp", file=sys.stderr)
    sys.exit(1)

import xhs_controller as xhs

app = Server("xhs-mac-mcp")

# ── 工具函数 ──────────────────────────────────────────────────

def _screenshot_b64() -> str | None:
    """截图并返回 base64，失败返回 None"""
    import tempfile, os
    path = tempfile.mktemp(suffix=".png")
    try:
        xhs.screenshot(path)
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None
    finally:
        try:
            os.unlink(path)
        except Exception:
            pass


def _text(msg: str) -> TextContent:
    return TextContent(type="text", text=msg)


def _json(data: Any) -> TextContent:
    return TextContent(type="text", text=json.dumps(data, ensure_ascii=False, indent=2))


def _img(b64: str) -> ImageContent:
    return ImageContent(type="image", data=b64, mimeType="image/png")


def _result(msg: str, with_screenshot: bool = True) -> list:
    """返回文字 + 截图（默认带截图方便 Claude 看到当前状态）"""
    out = [_text(msg)]
    if with_screenshot:
        b64 = _screenshot_b64()
        if b64:
            out.append(_img(b64))
    return out


def _err(msg: str) -> list:
    return [_text(f"❌ {msg}")]


# ── Tool 定义 ─────────────────────────────────────────────────

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [

        # ── 截图 & 状态 ──
        Tool(
            name="xhs_screenshot",
            description="截取小红书当前界面截图",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),

        # ── 导航 ──
        Tool(
            name="xhs_navigate",
            description="切换底部 Tab：home(首页) messages(消息) profile(我)",
            inputSchema={
                "type": "object",
                "properties": {
                    "tab": {
                        "type": "string",
                        "enum": ["home", "messages", "profile"],
                        "description": "目标 Tab",
                    }
                },
                "required": ["tab"],
            },
        ),
        Tool(
            name="xhs_navigate_top",
            description="切换顶部 Tab：follow(关注) discover(发现) video(视频)",
            inputSchema={
                "type": "object",
                "properties": {
                    "tab": {
                        "type": "string",
                        "enum": ["follow", "discover", "video"],
                        "description": "目标 Tab",
                    }
                },
                "required": ["tab"],
            },
        ),
        Tool(
            name="xhs_back",
            description="返回上一页",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),

        # ── 搜索 ──
        Tool(
            name="xhs_search",
            description="搜索关键词，跳转到搜索结果页",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "搜索关键词"}
                },
                "required": ["keyword"],
            },
        ),

        # ── Feed ──
        Tool(
            name="xhs_scroll_feed",
            description="滚动当前 Feed 流",
            inputSchema={
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "enum": ["down", "up"],
                        "default": "down",
                        "description": "滚动方向",
                    },
                    "times": {
                        "type": "integer",
                        "default": 3,
                        "description": "滚动次数",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="xhs_open_note",
            description="点击 Feed 双列瀑布流中的笔记",
            inputSchema={
                "type": "object",
                "properties": {
                    "col": {
                        "type": "integer",
                        "default": 0,
                        "description": "列号：0=左列，1=右列",
                    },
                    "row": {
                        "type": "integer",
                        "default": 0,
                        "description": "行号：0=第一行，1=第二行...",
                    },
                },
                "required": [],
            },
        ),

        # ── 笔记互动 ──
        Tool(
            name="xhs_like",
            description="点赞当前笔记（需先进入笔记详情页）",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="xhs_collect",
            description="收藏当前笔记（需先进入笔记详情页）",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="xhs_get_note_url",
            description="获取当前笔记的分享链接（需先进入笔记详情页）",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="xhs_follow_author",
            description="关注当前笔记的作者",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),

        # ── 评论 ──
        Tool(
            name="xhs_open_comments",
            description=(
                "打开评论区。视频帖：弹出侧边评论层（完整可用）。"
                "图文帖：受限于 App 自绘渲染，AX 无法读取评论文字。"
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="xhs_scroll_comments",
            description="滚动评论区（视频帖完全可用；图文帖受限）",
            inputSchema={
                "type": "object",
                "properties": {
                    "times": {
                        "type": "integer",
                        "default": 3,
                        "description": "滚动次数",
                    }
                },
                "required": [],
            },
        ),
        Tool(
            name="xhs_get_comments",
            description=(
                "获取评论列表，返回 [{index, author, cx, cy}, ...]。"
                "视频帖可靠（AX 完整暴露）；图文帖受限（评论文字读不到）。"
            ),
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="xhs_post_comment",
            description="发送评论（需先进入笔记详情页）",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "评论内容"}
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="xhs_reply_to_comment",
            description="回复评论（点击 get_comments 返回的某条评论触发回复框，然后输入文字）",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {
                        "type": "integer",
                        "description": "评论序号（来自 get_comments 的 index 字段）",
                    },
                    "text": {"type": "string", "description": "回复内容"},
                },
                "required": ["index", "text"],
            },
        ),
        Tool(
            name="xhs_delete_comment",
            description="删除评论（只能删自己发的评论，操作不可逆）",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {
                        "type": "integer",
                        "description": "评论序号（来自 get_comments 的 index 字段）",
                    }
                },
                "required": ["index"],
            },
        ),

        # ── 私信 ──
        Tool(
            name="xhs_open_dm",
            description="打开消息列表中指定序号的私信对话",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {
                        "type": "integer",
                        "default": 0,
                        "description": "对话序号，0=列表第一条",
                    }
                },
                "required": [],
            },
        ),
        Tool(
            name="xhs_send_dm",
            description="在当前私信对话中发送消息（需先 open_dm 打开对话）",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "消息内容"}
                },
                "required": ["text"],
            },
        ),

        # ── 个人主页 ──
        Tool(
            name="xhs_get_author_stats",
            description="读取当前主页的关注数/粉丝数/获赞与收藏数/bio（需先导航到 profile 或作者主页）",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
    ]


# ── Tool 执行 ─────────────────────────────────────────────────

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list:
    try:

        if name == "xhs_screenshot":
            b64 = _screenshot_b64()
            if not b64:
                return _err("截图失败，rednote 窗口可能不在屏幕上")
            return [_img(b64)]

        elif name == "xhs_navigate":
            tab = arguments.get("tab", "home")
            xhs.navigate_tab(tab)
            time.sleep(1.0)
            return _result(f"✅ 已导航到 {tab}")

        elif name == "xhs_navigate_top":
            tab = arguments.get("tab", "discover")
            xhs.navigate_top_tab(tab)
            time.sleep(1.0)
            return _result(f"✅ 已切换到顶部 Tab: {tab}")

        elif name == "xhs_back":
            xhs.back()
            time.sleep(1.0)
            return _result("✅ 已返回")

        elif name == "xhs_search":
            keyword = arguments.get("keyword", "").strip()
            if not keyword:
                return _err("请提供搜索关键词")
            xhs.search(keyword)
            time.sleep(2.0)
            return _result(f"✅ 搜索: {keyword}")

        elif name == "xhs_scroll_feed":
            direction = arguments.get("direction", "down")
            times = int(arguments.get("times", 3))
            xhs.scroll_feed(direction, times)
            time.sleep(0.5)
            return _result(f"✅ 向 {direction} 滚动 {times} 次")

        elif name == "xhs_open_note":
            col = int(arguments.get("col", 0))
            row = int(arguments.get("row", 0))
            xhs.open_note(col, row)
            time.sleep(2.0)
            return _result(f"✅ 已打开第 {row} 行第 {col} 列笔记")

        elif name == "xhs_like":
            xhs.like()
            time.sleep(0.8)
            return _result("✅ 已点赞")

        elif name == "xhs_collect":
            xhs.collect()
            time.sleep(0.8)
            return _result("✅ 已收藏")

        elif name == "xhs_get_note_url":
            url = xhs.get_note_url()
            return [_text(f"✅ 笔记链接: {url}")]

        elif name == "xhs_follow_author":
            xhs.follow_author()
            time.sleep(0.8)
            return _result("✅ 已点击关注")

        elif name == "xhs_open_comments":
            xhs.open_comments()
            time.sleep(1.5)
            return _result("✅ 已打开评论区")

        elif name == "xhs_scroll_comments":
            times = int(arguments.get("times", 3))
            xhs.scroll_comments(times)
            time.sleep(0.8)
            return _result(f"✅ 评论区已滚动 {times} 次")

        elif name == "xhs_get_comments":
            comments = xhs.get_comments()
            return [_json(comments)]

        elif name == "xhs_post_comment":
            text = arguments.get("text", "").strip()
            if not text:
                return _err("评论内容不能为空")
            result = xhs.post_comment(text)
            time.sleep(1.0)
            return _result(f"✅ 评论已发送: {text}" if result else "❌ 发送失败，请截图检查")

        elif name == "xhs_reply_to_comment":
            index = int(arguments.get("index", 0))
            text = arguments.get("text", "").strip()
            if not text:
                return _err("回复内容不能为空")
            result = xhs.reply_to_comment(index, text)
            time.sleep(1.0)
            return _result(f"✅ 已回复评论 #{index}: {text}" if result else "❌ 回复失败，请截图检查")

        elif name == "xhs_delete_comment":
            index = int(arguments.get("index", 0))
            result = xhs.delete_comment(index)
            time.sleep(1.0)
            return _result(f"✅ 评论 #{index} 已删除" if result else "❌ 删除失败，请截图检查")

        elif name == "xhs_open_dm":
            index = int(arguments.get("index", 0))
            xhs.navigate_tab("messages")
            time.sleep(1.0)
            xhs.open_dm_by_index(index)
            time.sleep(1.5)
            return _result(f"✅ 已打开第 {index} 条私信对话")

        elif name == "xhs_send_dm":
            text = arguments.get("text", "").strip()
            if not text:
                return _err("消息内容不能为空")
            xhs.send_dm(text)
            time.sleep(1.0)
            return _result(f"✅ 私信已发送: {text}")

        elif name == "xhs_get_author_stats":
            stats = xhs.get_author_stats()
            return [_json(stats)]

        else:
            return _err(f"未知工具: {name}")

    except Exception as e:
        import traceback
        return _err(f"{type(e).__name__}: {e}\n{traceback.format_exc()}")


# ── 启动 ──────────────────────────────────────────────────────

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
