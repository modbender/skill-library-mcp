"""
小红书发布模块（图文 + 视频）

基于 xiaohongshu-mcp/publish.go + publish_video.go 翻译
整合 xiaohongshu-ops 的安全发布理念（人工确认 checkpoint）
"""

import json
import os
import sys
import time
import random
from pathlib import Path
from typing import Optional, Dict, Any, List

from .client import XiaohongshuClient, DEFAULT_COOKIE_PATH

PUBLISH_URL = "https://creator.xiaohongshu.com/publish/publish?source=official"


class PublishAction:
    """发布动作"""

    def __init__(self, client: XiaohongshuClient):
        self.client = client

    def _navigate_to_publish(self):
        """导航到创作者中心发布页"""
        print("打开创作者中心发布页...", file=sys.stderr)
        self.client.navigate(PUBLISH_URL)
        time.sleep(3)

    def _click_publish_tab(self, tab_name: str):
        """点击发布类型 TAB（上传图文 / 上传视频）"""
        page = self.client.page

        # 等待上传区域出现
        try:
            page.wait_for_selector('div.upload-content, div.creator-tab', timeout=15000)
        except Exception:
            print("等待发布页加载超时，继续尝试", file=sys.stderr)

        time.sleep(1)

        # 移除可能的弹窗遮挡
        page.evaluate("""() => {
            var popover = document.querySelector('div.d-popover');
            if (popover) popover.remove();
        }""")

        # 查找并点击对应 TAB
        try:
            tabs = page.locator('div.creator-tab')
            for i in range(tabs.count()):
                tab = tabs.nth(i)
                text = tab.text_content().strip()
                if text == tab_name:
                    tab.click()
                    time.sleep(1)
                    print(f"已切换到「{tab_name}」", file=sys.stderr)
                    return
            # 回退：使用文本定位
            page.get_by_text(tab_name, exact=True).click()
            time.sleep(1)
        except Exception as e:
            print(f"切换 TAB「{tab_name}」失败: {e}", file=sys.stderr)

    def _upload_images(self, image_paths: List[str]):
        """逐张上传图片"""
        page = self.client.page
        valid_paths = [p for p in image_paths if os.path.exists(p)]

        if not valid_paths:
            raise ValueError("没有有效的图片文件")

        for i, path in enumerate(valid_paths):
            abs_path = os.path.abspath(path)
            print(f"上传图片 ({i+1}/{len(valid_paths)}): {abs_path}", file=sys.stderr)

            # 第一张用 .upload-input，后续用 input[type=file]
            selector = '.upload-input' if i == 0 else 'input[type="file"]'
            try:
                upload_input = page.locator(selector)
                upload_input.set_input_files(abs_path)
            except Exception:
                # 回退
                upload_input = page.locator('input[type="file"]')
                upload_input.set_input_files(abs_path)

            # 等待图片上传完成（预览元素出现）
            expected = i + 1
            for _ in range(120):  # 最多等 60 秒
                try:
                    previews = page.locator('.img-preview-area .pr, .upload-preview-item')
                    if previews.count() >= expected:
                        break
                except Exception:
                    pass
                time.sleep(0.5)

            time.sleep(1)

        print(f"全部 {len(valid_paths)} 张图片上传完成", file=sys.stderr)

    def _upload_video(self, video_path: str):
        """上传视频文件"""
        page = self.client.page

        if not os.path.exists(video_path):
            raise ValueError(f"视频文件不存在: {video_path}")

        abs_path = os.path.abspath(video_path)
        print(f"上传视频: {abs_path}", file=sys.stderr)

        try:
            upload_input = page.locator('.upload-input')
            upload_input.set_input_files(abs_path)
        except Exception:
            upload_input = page.locator('input[type="file"]')
            upload_input.set_input_files(abs_path)

        # 等待发布按钮可点击（视频处理完成标志），最多等 10 分钟
        print("等待视频处理完成...", file=sys.stderr)
        btn_selector = '.publish-page-publish-btn button.bg-red'
        for attempt in range(600):
            try:
                btn = page.locator(btn_selector)
                if btn.count() > 0 and btn.is_visible():
                    disabled = btn.get_attribute('disabled')
                    if disabled is None:
                        print("视频处理完成", file=sys.stderr)
                        return
            except Exception:
                pass
            time.sleep(1)

        print("警告: 等待视频处理超时", file=sys.stderr)

    def _fill_title(self, title: str):
        """填写标题"""
        page = self.client.page
        try:
            title_input = page.locator('div.d-input input')
            title_input.first.fill(title)
            time.sleep(0.5)

            # 检查标题是否超长
            max_suffix = page.locator('div.title-container div.max_suffix')
            if max_suffix.count() > 0 and max_suffix.is_visible():
                length_text = max_suffix.text_content()
                print(f"警告: 标题超长 ({length_text})", file=sys.stderr)

            print(f"标题已填写: {title}", file=sys.stderr)
        except Exception as e:
            print(f"填写标题失败: {e}", file=sys.stderr)

    def _fill_content(self, content: str):
        """填写正文"""
        page = self.client.page

        # 尝试两种编辑器：Quill 或 contenteditable
        content_el = None
        try:
            ql = page.locator('div.ql-editor')
            if ql.count() > 0:
                content_el = ql.first
        except Exception:
            pass

        if content_el is None:
            try:
                # 通过 placeholder 查找
                content_el = page.locator('p[data-placeholder*="输入正文描述"]').first
                # 向上找 textbox 父元素
                parent = page.locator('[role="textbox"]')
                if parent.count() > 0:
                    content_el = parent.first
            except Exception:
                pass

        if content_el is None:
            print("未找到正文输入框", file=sys.stderr)
            return

        try:
            content_el.click()
            time.sleep(0.3)
            page.keyboard.type(content, delay=30)
            time.sleep(0.5)

            # 检查正文是否超长
            length_error = page.locator('div.edit-container div.length-error')
            if length_error.count() > 0 and length_error.is_visible():
                err_text = length_error.text_content()
                print(f"警告: 正文超长 ({err_text})", file=sys.stderr)

            print("正文已填写", file=sys.stderr)
        except Exception as e:
            print(f"填写正文失败: {e}", file=sys.stderr)

    def _input_tags(self, tags: List[str]):
        """输入话题标签（通过 # 触发联想）"""
        if not tags:
            return

        page = self.client.page

        # 先移动光标到正文末尾
        content_el = None
        try:
            ql = page.locator('div.ql-editor')
            if ql.count() > 0:
                content_el = ql.first
            else:
                content_el = page.locator('[role="textbox"]').first
        except Exception:
            return

        if content_el is None:
            return

        try:
            content_el.click()
            time.sleep(0.3)
            # 按 End 键移动到末尾
            page.keyboard.press('End')
            page.keyboard.press('Enter')
            page.keyboard.press('Enter')
            time.sleep(0.5)
        except Exception:
            pass

        # 限制最多 10 个标签
        tags = tags[:10]

        for tag in tags:
            tag = tag.lstrip('#')
            try:
                # 输入 #
                page.keyboard.type('#', delay=100)
                time.sleep(0.3)

                # 逐字输入标签文字
                page.keyboard.type(tag, delay=50)
                time.sleep(1)

                # 尝试点击联想下拉框的第一个选项
                topic_item = page.locator('#creator-editor-topic-container .item')
                if topic_item.count() > 0:
                    topic_item.first.click()
                    print(f"标签「{tag}」已通过联想选择", file=sys.stderr)
                else:
                    # 没有联想，输入空格结束
                    page.keyboard.type(' ', delay=50)
                    print(f"标签「{tag}」已直接输入", file=sys.stderr)

                time.sleep(0.5)
            except Exception as e:
                print(f"输入标签「{tag}」失败: {e}", file=sys.stderr)

    def _set_schedule(self, schedule_time: str):
        """设置定时发布（格式: 2025-01-01 12:00）"""
        page = self.client.page
        try:
            # 点击定时发布开关
            switch = page.locator('.post-time-wrapper .d-switch')
            switch.click()
            time.sleep(0.8)

            # 设置日期时间
            date_input = page.locator('.date-picker-container input')
            date_input.fill('')
            date_input.fill(schedule_time)
            time.sleep(0.5)

            print(f"定时发布设置: {schedule_time}", file=sys.stderr)
        except Exception as e:
            print(f"设置定时发布失败: {e}", file=sys.stderr)

    def _click_publish_button(self) -> bool:
        """点击发布按钮"""
        page = self.client.page
        try:
            btn = page.locator('.publish-page-publish-btn button.bg-red')
            if btn.count() > 0:
                btn.first.click()
                time.sleep(3)
                print("已点击发布按钮", file=sys.stderr)
                return True
            else:
                print("未找到发布按钮", file=sys.stderr)
                return False
        except Exception as e:
            print(f"点击发布按钮失败: {e}", file=sys.stderr)
            return False

    def _check_publish_ready(self) -> Dict[str, Any]:
        """检查发布前的状态（三要素校验）"""
        page = self.client.page
        status = {}

        # 检查标题
        try:
            title_input = page.locator('div.d-input input')
            status["title"] = title_input.input_value() if title_input.count() > 0 else ""
        except Exception:
            status["title"] = ""

        # 检查发布按钮可见性
        try:
            btn = page.locator('.publish-page-publish-btn button.bg-red')
            status["publish_button_visible"] = btn.count() > 0 and btn.is_visible()
        except Exception:
            status["publish_button_visible"] = False

        status["title_ok"] = bool(status["title"])
        return status

    def publish_image(
        self,
        title: str,
        content: str,
        image_paths: List[str],
        tags: Optional[List[str]] = None,
        schedule_time: Optional[str] = None,
        auto_publish: bool = False,
    ) -> Dict[str, Any]:
        """
        发布图文笔记

        Args:
            title: 标题（建议 <=20 字）
            content: 正文
            image_paths: 图片文件路径列表
            tags: 话题标签列表
            schedule_time: 定时发布时间（格式 2025-01-01 12:00），None 为立即
            auto_publish: 是否自动点击发布（默认 False，停在发布按钮处）

        Returns:
            操作结果
        """
        self._navigate_to_publish()
        self._click_publish_tab("上传图文")

        # 1. 上传图片
        self._upload_images(image_paths)

        # 2. 填写标题
        self._fill_title(title)
        time.sleep(1)

        # 3. 填写正文
        self._fill_content(content)
        time.sleep(1)

        # 4. 添加标签
        if tags:
            self._input_tags(tags)
            time.sleep(1)

        # 5. 定时发布
        if schedule_time:
            self._set_schedule(schedule_time)

        # 6. 校验三要素
        ready = self._check_publish_ready()
        print(f"发布前校验: {ready}", file=sys.stderr)

        # 7. 是否自动发布
        if auto_publish:
            success = self._click_publish_button()
            return {
                "status": "success" if success else "error",
                "action": "publish_image",
                "title": title,
                "image_count": len(image_paths),
                "tags": tags or [],
                "schedule_time": schedule_time,
                "published": success,
                "message": "发布成功" if success else "发布失败",
            }
        else:
            return {
                "status": "ready",
                "action": "publish_image",
                "title": title,
                "image_count": len(image_paths),
                "tags": tags or [],
                "schedule_time": schedule_time,
                "published": False,
                "ready_check": ready,
                "message": "已填写完毕，停在发布按钮处。请确认后使用 --auto-publish 发布。",
            }

    def publish_video(
        self,
        title: str,
        content: str,
        video_path: str,
        tags: Optional[List[str]] = None,
        schedule_time: Optional[str] = None,
        auto_publish: bool = False,
    ) -> Dict[str, Any]:
        """
        发布视频笔记

        Args:
            title: 标题
            content: 正文
            video_path: 视频文件路径
            tags: 话题标签
            schedule_time: 定时发布时间
            auto_publish: 是否自动发布（默认 False）

        Returns:
            操作结果
        """
        self._navigate_to_publish()
        self._click_publish_tab("上传视频")

        # 1. 上传视频
        self._upload_video(video_path)

        # 2. 填写标题
        self._fill_title(title)
        time.sleep(1)

        # 3. 填写正文
        self._fill_content(content)
        time.sleep(1)

        # 4. 添加标签
        if tags:
            self._input_tags(tags)
            time.sleep(1)

        # 5. 定时发布
        if schedule_time:
            self._set_schedule(schedule_time)

        # 6. 校验
        ready = self._check_publish_ready()
        print(f"发布前校验: {ready}", file=sys.stderr)

        if auto_publish:
            success = self._click_publish_button()
            return {
                "status": "success" if success else "error",
                "action": "publish_video",
                "title": title,
                "video_path": video_path,
                "published": success,
                "message": "发布成功" if success else "发布失败",
            }
        else:
            return {
                "status": "ready",
                "action": "publish_video",
                "title": title,
                "video_path": video_path,
                "published": False,
                "ready_check": ready,
                "message": "已填写完毕，停在发布按钮处。请确认后使用 --auto-publish 发布。",
            }


def md_to_images(
    markdown_text: str,
    output_dir: str = ".",
    width: int = 1080,
    css: str = "",
) -> List[str]:
    """
    将 Markdown 文本渲染为长文图片（利用 Playwright 截图）

    Args:
        markdown_text: Markdown 文本
        output_dir: 输出目录
        width: 图片宽度（像素）
        css: 自定义 CSS 样式

    Returns:
        生成的图片路径列表
    """
    try:
        import markdown
    except ImportError:
        print("需要安装 markdown 库: pip install markdown", file=sys.stderr)
        raise

    # 将 Markdown 转为 HTML
    html_content = markdown.markdown(
        markdown_text,
        extensions=['tables', 'fenced_code', 'codehilite', 'nl2br'],
    )

    default_css = """
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
                     "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
        padding: 40px 50px;
        line-height: 1.8;
        color: #333;
        background: #fff;
        max-width: 100%;
        margin: 0 auto;
        font-size: 16px;
    }
    h1 { font-size: 24px; font-weight: bold; margin: 20px 0 10px; color: #222; }
    h2 { font-size: 20px; font-weight: bold; margin: 18px 0 8px; color: #333; }
    h3 { font-size: 18px; font-weight: bold; margin: 15px 0 6px; color: #444; }
    p { margin: 8px 0; }
    ul, ol { padding-left: 20px; }
    li { margin: 4px 0; }
    blockquote {
        border-left: 4px solid #ff2442;
        padding: 8px 16px;
        margin: 12px 0;
        background: #fff5f5;
        color: #555;
    }
    code {
        background: #f5f5f5;
        padding: 2px 6px;
        border-radius: 3px;
        font-size: 14px;
    }
    pre {
        background: #f5f5f5;
        padding: 16px;
        border-radius: 6px;
        overflow-x: auto;
    }
    img { max-width: 100%; border-radius: 8px; }
    hr { border: none; border-top: 1px solid #eee; margin: 20px 0; }
    table { border-collapse: collapse; width: 100%; margin: 12px 0; }
    th, td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }
    th { background: #f5f5f5; }
    """

    full_css = default_css + "\n" + css
    full_html = f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<meta name="viewport" content="width={width}">
<style>{full_css}</style>
</head><body>{html_content}</body></html>"""

    os.makedirs(output_dir, exist_ok=True)

    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width, "height": 800})
        page.set_content(full_html)
        page.wait_for_load_state("networkidle")
        time.sleep(0.5)

        # 获取实际内容高度
        total_height = page.evaluate("document.body.scrollHeight")

        # 如果内容不太长（<=4000px），直接截一张
        # 否则分页截图（每张最多 3000px）
        image_paths = []
        max_page_height = 3000

        if total_height <= max_page_height + 500:
            # 单张截图
            page.set_viewport_size({"width": width, "height": total_height + 40})
            time.sleep(0.3)
            img_path = os.path.join(output_dir, "md_page_1.png")
            page.screenshot(path=img_path, full_page=True)
            image_paths.append(img_path)
        else:
            # 分页截图
            page_num = 1
            y_offset = 0
            while y_offset < total_height:
                chunk_height = min(max_page_height, total_height - y_offset)
                img_path = os.path.join(output_dir, f"md_page_{page_num}.png")
                page.screenshot(
                    path=img_path,
                    clip={"x": 0, "y": y_offset, "width": width, "height": chunk_height},
                )
                image_paths.append(img_path)
                y_offset += chunk_height
                page_num += 1

        browser.close()

    print(f"Markdown 已渲染为 {len(image_paths)} 张图片", file=sys.stderr)
    return image_paths


# ============================================================
# 便捷函数
# ============================================================

def publish_image(
    title: str,
    content: str,
    image_paths: List[str],
    tags: Optional[List[str]] = None,
    schedule_time: Optional[str] = None,
    auto_publish: bool = False,
    headless: bool = True,
    cookie_path: str = DEFAULT_COOKIE_PATH,
) -> Dict[str, Any]:
    """发布图文笔记"""
    client = XiaohongshuClient(headless=headless, cookie_path=cookie_path)
    try:
        client.start()
        action = PublishAction(client)
        return action.publish_image(
            title=title, content=content, image_paths=image_paths,
            tags=tags, schedule_time=schedule_time, auto_publish=auto_publish,
        )
    finally:
        client.close()


def publish_video(
    title: str,
    content: str,
    video_path: str,
    tags: Optional[List[str]] = None,
    schedule_time: Optional[str] = None,
    auto_publish: bool = False,
    headless: bool = True,
    cookie_path: str = DEFAULT_COOKIE_PATH,
) -> Dict[str, Any]:
    """发布视频笔记"""
    client = XiaohongshuClient(headless=headless, cookie_path=cookie_path)
    try:
        client.start()
        action = PublishAction(client)
        return action.publish_video(
            title=title, content=content, video_path=video_path,
            tags=tags, schedule_time=schedule_time, auto_publish=auto_publish,
        )
    finally:
        client.close()


def publish_markdown(
    title: str,
    markdown_text: str,
    extra_content: str = "",
    tags: Optional[List[str]] = None,
    schedule_time: Optional[str] = None,
    auto_publish: bool = False,
    image_width: int = 1080,
    output_dir: str = "",
    headless: bool = True,
    cookie_path: str = DEFAULT_COOKIE_PATH,
) -> Dict[str, Any]:
    """
    将 Markdown 渲染为图片后发布图文笔记

    Args:
        title: 标题
        markdown_text: Markdown 内容
        extra_content: 正文区的额外文字说明
        tags: 话题标签
        schedule_time: 定时发布
        auto_publish: 是否自动发布
        image_width: 图片宽度
        output_dir: 图片输出目录（默认临时目录）
        headless: 无头模式
        cookie_path: Cookie 路径

    Returns:
        操作结果
    """
    import tempfile
    if not output_dir:
        output_dir = tempfile.mkdtemp(prefix="xhs_md_")

    # 1. Markdown → 图片
    image_paths = md_to_images(markdown_text, output_dir=output_dir, width=image_width)

    if not image_paths:
        return {"status": "error", "message": "Markdown 渲染失败，未生成图片"}

    # 2. 发布图文
    body = extra_content or f"本文由 Markdown 渲染生成，共 {len(image_paths)} 页"
    return publish_image(
        title=title, content=body, image_paths=image_paths,
        tags=tags, schedule_time=schedule_time, auto_publish=auto_publish,
        headless=headless, cookie_path=cookie_path,
    )
