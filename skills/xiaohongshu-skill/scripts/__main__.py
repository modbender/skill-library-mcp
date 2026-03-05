#!/usr/bin/env python
"""
小红书 CLI 入口

基于 xiaohongshu-mcp 翻译
"""

import argparse
import json
import sys
from typing import Optional

# Windows GBK 终端兼容性修复：强制 stdout 使用 UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from .client import XiaohongshuClient, CaptchaError, DEFAULT_COOKIE_PATH
from . import login
from . import search
from . import feed
from . import user
from . import comment
from . import interact
from . import explore
from . import publish


def format_output(data) -> str:
    """格式化输出为 JSON"""
    if data is None:
        return json.dumps({"error": "No data"}, ensure_ascii=False, indent=2)
    return json.dumps(data, ensure_ascii=False, indent=2)


def _headless(args) -> bool:
    """从 args 解析 headless 值"""
    val = getattr(args, 'headless', 'true')
    if isinstance(val, bool):
        return val
    return val.lower() != 'false'


# ============================================================
# 命令处理函数
# ============================================================

def cmd_login(args):
    """登录命令 — 生成二维码并等待扫码"""
    result = login.login(
        headless=_headless(args),
        cookie_path=args.cookie or DEFAULT_COOKIE_PATH,
        timeout=args.timeout,
    )
    print(format_output(result))
    if result.get("status") == "logged_in":
        return 0
    elif result.get("status") == "qrcode_ready":
        return 2
    return 1


def cmd_qrcode(args):
    """
    获取二维码并等待扫码。
    如果已登录，直接返回。
    """
    cookie_path = args.cookie or DEFAULT_COOKIE_PATH
    headless = _headless(args)

    # 1) 先快速检查是否已登录
    is_logged_in, username = login.check_login(cookie_path=cookie_path)
    if is_logged_in:
        result = {
            "status": "logged_in",
            "qrcode_path": None,
            "username": username,
            "message": "已登录",
        }
        print(format_output(result))
        return 0

    # 2) 未登录 → 启动可见浏览器，获取二维码并等待扫码
    client = XiaohongshuClient(headless=headless, cookie_path=cookie_path)
    try:
        client.start()
        action = login.LoginAction(client)

        qrcode_path, already_logged_in = action.get_wechat_qrcode()
        if already_logged_in:
            print(format_output({"status": "logged_in", "message": "已登录"}))
            return 0

        if qrcode_path:
            print(format_output({
                "status": "qrcode_ready",
                "qrcode_path": qrcode_path,
                "message": f"请扫码登录，二维码路径: {qrcode_path}",
            }))

            # 等待用户扫码（最多 120 秒）
            print("等待用户扫码…（最多 120 秒）", file=sys.stderr)
            success = action.wait_for_login(timeout=120)

            if success:
                print(format_output({"status": "logged_in", "message": "登录成功！"}))
                return 0
            else:
                print(format_output({"status": "timeout", "message": "扫码超时"}))
                return 2
        else:
            print(format_output({"status": "error", "message": "获取二维码失败"}))
            return 1
    finally:
        client.close()


def cmd_check_login(args):
    """检查登录状态"""
    is_logged_in, username = login.check_login(
        cookie_path=args.cookie or DEFAULT_COOKIE_PATH,
    )
    print(format_output({
        "is_logged_in": is_logged_in,
        "username": username,
    }))
    return 0


def cmd_search(args):
    """搜索命令"""
    results = search.search(
        keyword=args.keyword,
        sort_by=args.sort_by,
        note_type=args.note_type,
        publish_time=args.publish_time,
        search_scope=args.search_scope,
        location=args.location,
        limit=args.limit,
        headless=_headless(args),
        cookie_path=args.cookie or DEFAULT_COOKIE_PATH,
    )
    print(format_output({
        "count": len(results),
        "results": results,
    }))
    return 0


def cmd_feed(args):
    """笔记详情命令"""
    detail = feed.feed_detail(
        feed_id=args.feed_id,
        xsec_token=args.xsec_token or "",
        load_comments=args.load_comments,
        max_comments=args.max_comments,
        headless=_headless(args),
        cookie_path=args.cookie or DEFAULT_COOKIE_PATH,
    )
    print(format_output(detail))
    return 0 if detail else 1


def cmd_user(args):
    """用户主页命令"""
    profile = user.user_profile(
        user_id=args.user_id,
        xsec_token=args.xsec_token or "",
        headless=_headless(args),
        cookie_path=args.cookie or DEFAULT_COOKIE_PATH,
    )
    print(format_output(profile))
    return 0 if profile else 1


def cmd_me(args):
    """获取自己的个人主页"""
    profile = user.my_profile(
        headless=_headless(args),
        cookie_path=args.cookie or DEFAULT_COOKIE_PATH,
    )
    print(format_output(profile))
    return 0 if profile else 1


def cmd_comment(args):
    """发表评论"""
    result = comment.post_comment(
        feed_id=args.feed_id,
        xsec_token=args.xsec_token or "",
        content=args.content,
        headless=_headless(args),
        cookie_path=args.cookie or DEFAULT_COOKIE_PATH,
    )
    print(format_output(result))
    return 0 if result.get("status") == "success" else 1


def cmd_reply(args):
    """回复评论"""
    result = comment.reply_to_comment(
        feed_id=args.feed_id,
        xsec_token=args.xsec_token or "",
        comment_id=args.comment_id,
        reply_user_id=args.reply_user_id,
        content=args.content,
        headless=_headless(args),
        cookie_path=args.cookie or DEFAULT_COOKIE_PATH,
    )
    print(format_output(result))
    return 0 if result.get("status") == "success" else 1


def cmd_like(args):
    """点赞"""
    result = interact.like(
        feed_id=args.feed_id,
        xsec_token=args.xsec_token or "",
        headless=_headless(args),
        cookie_path=args.cookie or DEFAULT_COOKIE_PATH,
    )
    print(format_output(result))
    return 0 if result.get("status") == "success" else 1


def cmd_unlike(args):
    """取消点赞"""
    result = interact.unlike(
        feed_id=args.feed_id,
        xsec_token=args.xsec_token or "",
        headless=_headless(args),
        cookie_path=args.cookie or DEFAULT_COOKIE_PATH,
    )
    print(format_output(result))
    return 0 if result.get("status") == "success" else 1


def cmd_collect(args):
    """收藏"""
    result = interact.collect(
        feed_id=args.feed_id,
        xsec_token=args.xsec_token or "",
        headless=_headless(args),
        cookie_path=args.cookie or DEFAULT_COOKIE_PATH,
    )
    print(format_output(result))
    return 0 if result.get("status") == "success" else 1


def cmd_uncollect(args):
    """取消收藏"""
    result = interact.uncollect(
        feed_id=args.feed_id,
        xsec_token=args.xsec_token or "",
        headless=_headless(args),
        cookie_path=args.cookie or DEFAULT_COOKIE_PATH,
    )
    print(format_output(result))
    return 0 if result.get("status") == "success" else 1


def cmd_explore(args):
    """首页推荐流"""
    result = explore.explore(
        limit=args.limit,
        headless=_headless(args),
        cookie_path=args.cookie or DEFAULT_COOKIE_PATH,
    )
    print(format_output(result))
    return 0


def cmd_publish(args):
    """发布图文笔记"""
    image_paths = [p.strip() for p in args.images.split(",") if p.strip()]
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else None
    result = publish.publish_image(
        title=args.title,
        content=args.content,
        image_paths=image_paths,
        tags=tags,
        schedule_time=args.schedule_time,
        auto_publish=args.auto_publish,
        headless=_headless(args),
        cookie_path=args.cookie or DEFAULT_COOKIE_PATH,
    )
    print(format_output(result))
    return 0 if result.get("status") in ("success", "ready") else 1


def cmd_publish_video(args):
    """发布视频笔记"""
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else None
    result = publish.publish_video(
        title=args.title,
        content=args.content,
        video_path=args.video,
        tags=tags,
        schedule_time=args.schedule_time,
        auto_publish=args.auto_publish,
        headless=_headless(args),
        cookie_path=args.cookie or DEFAULT_COOKIE_PATH,
    )
    print(format_output(result))
    return 0 if result.get("status") in ("success", "ready") else 1


def cmd_publish_md(args):
    """将 Markdown 渲染为图片后发布图文笔记"""
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else None

    # 从文件或直接文本读取 Markdown
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            markdown_text = f.read()
    else:
        markdown_text = args.text

    if not markdown_text:
        print(format_output({"status": "error", "message": "需要提供 --file 或 --text"}))
        return 1

    result = publish.publish_markdown(
        title=args.title,
        markdown_text=markdown_text,
        extra_content=args.content or "",
        tags=tags,
        schedule_time=args.schedule_time,
        auto_publish=args.auto_publish,
        image_width=args.width,
        output_dir=args.output_dir or "",
        headless=_headless(args),
        cookie_path=args.cookie or DEFAULT_COOKIE_PATH,
    )
    print(format_output(result))
    return 0 if result.get("status") in ("success", "ready") else 1


# ============================================================
# 入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="小红书 CLI 工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # 全局参数
    parser.add_argument("--cookie", "-c", help="Cookie 文件路径", default=None)
    parser.add_argument("--headless", help="无头模式: true/false（默认 true）", default='true')

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # login
    login_p = subparsers.add_parser("login", help="扫码登录（等待登录或超时）")
    login_p.add_argument("--timeout", "-t", type=int, default=120, help="登录超时秒数")
    login_p.add_argument("--headless", default='false', help="默认 false 以显示浏览器")
    login_p.set_defaults(func=cmd_login)

    # qrcode
    qr_p = subparsers.add_parser("qrcode", help="获取登录二维码并等待扫码")
    qr_p.add_argument("--headless", default='false', help="默认 false 以显示浏览器")
    qr_p.set_defaults(func=cmd_qrcode)

    # check-login
    chk_p = subparsers.add_parser("check-login", help="检查登录状态")
    chk_p.add_argument("--headless", default='true')
    chk_p.set_defaults(func=cmd_check_login)

    # search
    s_p = subparsers.add_parser("search", help="搜索内容")
    s_p.add_argument("keyword", help="搜索关键词")
    s_p.add_argument("--sort-by", help="排序方式")
    s_p.add_argument("--note-type", help="笔记类型")
    s_p.add_argument("--publish-time", help="发布时间")
    s_p.add_argument("--search-scope", help="搜索范围")
    s_p.add_argument("--location", help="位置距离")
    s_p.add_argument("--limit", "-n", type=int, default=10, help="返回数量")
    s_p.add_argument("--headless", default='true')
    s_p.set_defaults(func=cmd_search)

    # feed
    f_p = subparsers.add_parser("feed", help="获取笔记详情")
    f_p.add_argument("feed_id", help="笔记 ID")
    f_p.add_argument("xsec_token", nargs="?", help="xsec_token")
    f_p.add_argument("--load-comments", "-l", action="store_true", help="加载评论")
    f_p.add_argument("--max-comments", "-m", type=int, default=0, help="最大评论数")
    f_p.add_argument("--headless", default='true')
    f_p.set_defaults(func=cmd_feed)

    # user
    u_p = subparsers.add_parser("user", help="获取用户主页")
    u_p.add_argument("user_id", help="用户 ID")
    u_p.add_argument("xsec_token", nargs="?", help="xsec_token")
    u_p.add_argument("--headless", default='true')
    u_p.set_defaults(func=cmd_user)

    # me (获取自己的主页)
    me_p = subparsers.add_parser("me", help="获取自己的个人主页")
    me_p.add_argument("--headless", default='true')
    me_p.set_defaults(func=cmd_me)

    # comment (发表评论)
    cmt_p = subparsers.add_parser("comment", help="发表评论")
    cmt_p.add_argument("feed_id", help="笔记 ID")
    cmt_p.add_argument("xsec_token", nargs="?", help="xsec_token")
    cmt_p.add_argument("--content", required=True, help="评论内容")
    cmt_p.add_argument("--headless", default='true')
    cmt_p.set_defaults(func=cmd_comment)

    # reply (回复评论)
    rpl_p = subparsers.add_parser("reply", help="回复评论")
    rpl_p.add_argument("feed_id", help="笔记 ID")
    rpl_p.add_argument("xsec_token", nargs="?", help="xsec_token")
    rpl_p.add_argument("--comment-id", required=True, help="目标评论 ID")
    rpl_p.add_argument("--reply-user-id", required=True, help="被回复用户 ID")
    rpl_p.add_argument("--content", required=True, help="回复内容")
    rpl_p.add_argument("--headless", default='true')
    rpl_p.set_defaults(func=cmd_reply)

    # like (点赞)
    like_p = subparsers.add_parser("like", help="点赞笔记")
    like_p.add_argument("feed_id", help="笔记 ID")
    like_p.add_argument("xsec_token", nargs="?", help="xsec_token")
    like_p.add_argument("--headless", default='true')
    like_p.set_defaults(func=cmd_like)

    # unlike (取消点赞)
    unlike_p = subparsers.add_parser("unlike", help="取消点赞")
    unlike_p.add_argument("feed_id", help="笔记 ID")
    unlike_p.add_argument("xsec_token", nargs="?", help="xsec_token")
    unlike_p.add_argument("--headless", default='true')
    unlike_p.set_defaults(func=cmd_unlike)

    # collect (收藏)
    col_p = subparsers.add_parser("collect", help="收藏笔记")
    col_p.add_argument("feed_id", help="笔记 ID")
    col_p.add_argument("xsec_token", nargs="?", help="xsec_token")
    col_p.add_argument("--headless", default='true')
    col_p.set_defaults(func=cmd_collect)

    # uncollect (取消收藏)
    ucol_p = subparsers.add_parser("uncollect", help="取消收藏")
    ucol_p.add_argument("feed_id", help="笔记 ID")
    ucol_p.add_argument("xsec_token", nargs="?", help="xsec_token")
    ucol_p.add_argument("--headless", default='true')
    ucol_p.set_defaults(func=cmd_uncollect)

    # explore (首页推荐流)
    exp_p = subparsers.add_parser("explore", help="获取首页推荐流")
    exp_p.add_argument("--limit", "-n", type=int, default=20, help="返回数量")
    exp_p.add_argument("--headless", default='true')
    exp_p.set_defaults(func=cmd_explore)

    # publish (发布图文笔记)
    pub_p = subparsers.add_parser("publish", help="发布图文笔记")
    pub_p.add_argument("--title", required=True, help="标题（建议 <=20 字）")
    pub_p.add_argument("--content", required=True, help="正文内容")
    pub_p.add_argument("--images", required=True, help="图片路径，逗号分隔")
    pub_p.add_argument("--tags", help="话题标签，逗号分隔")
    pub_p.add_argument("--schedule-time", help="定时发布（格式: 2025-01-01 12:00）")
    pub_p.add_argument("--auto-publish", action="store_true", help="自动点击发布（默认停在发布按钮处）")
    pub_p.add_argument("--headless", default='true')
    pub_p.set_defaults(func=cmd_publish)

    # publish-video (发布视频笔记)
    pubv_p = subparsers.add_parser("publish-video", help="发布视频笔记")
    pubv_p.add_argument("--title", required=True, help="标题")
    pubv_p.add_argument("--content", required=True, help="正文内容")
    pubv_p.add_argument("--video", required=True, help="视频文件路径")
    pubv_p.add_argument("--tags", help="话题标签，逗号分隔")
    pubv_p.add_argument("--schedule-time", help="定时发布（格式: 2025-01-01 12:00）")
    pubv_p.add_argument("--auto-publish", action="store_true", help="自动点击发布")
    pubv_p.add_argument("--headless", default='true')
    pubv_p.set_defaults(func=cmd_publish_video)

    # publish-md (Markdown 转图片后发布)
    pubmd_p = subparsers.add_parser("publish-md", help="Markdown 渲染为图片后发布")
    pubmd_p.add_argument("--title", required=True, help="标题")
    pubmd_p.add_argument("--file", help="Markdown 文件路径")
    pubmd_p.add_argument("--text", help="Markdown 文本（与 --file 二选一）")
    pubmd_p.add_argument("--content", help="正文区额外文字说明")
    pubmd_p.add_argument("--tags", help="话题标签，逗号分隔")
    pubmd_p.add_argument("--schedule-time", help="定时发布")
    pubmd_p.add_argument("--auto-publish", action="store_true", help="自动点击发布")
    pubmd_p.add_argument("--width", type=int, default=1080, help="图片宽度（默认 1080）")
    pubmd_p.add_argument("--output-dir", help="图片输出目录（默认临时目录）")
    pubmd_p.add_argument("--headless", default='true')
    pubmd_p.set_defaults(func=cmd_publish_md)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0

    try:
        return args.func(args)
    except CaptchaError as e:
        print(format_output({
            "status": "error",
            "error_type": "CaptchaError",
            "message": str(e),
            "captcha_url": e.captcha_url,
        }))
        return 1
    except Exception as e:
        print(format_output({
            "status": "error",
            "error_type": type(e).__name__,
            "message": str(e),
        }))
        return 1


if __name__ == "__main__":
    sys.exit(main())
