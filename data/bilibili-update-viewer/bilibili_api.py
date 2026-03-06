#!/usr/bin/env python3
from __future__ import annotations
"""
B站 API 工具集

包含：
- WBI 签名生成
- UP主信息获取
- UP主视频列表获取
- 视频详情获取
- 视频字幕获取

参考文档：
- https://socialsisteryi.github.io/bilibili-API-collect/docs/misc/sign/wbi.html
"""

import hashlib
import json
import time
import urllib.parse
from functools import reduce
from typing import Any

import requests


# WBI 签名用的混淆表
MIXIN_KEY_ENC_TAB = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35,
    27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13,
    37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4,
    22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 34, 44, 52
]


class BilibiliAPI:
    """B站 API 客户端"""

    def __init__(self, sessdata: str = "", bili_jct: str = "", buvid3: str = "", dedeuserid: str = "", all_cookies: dict = None):
        """
        初始化 API 客户端

        Args:
            sessdata: SESSDATA cookie
            bili_jct: bili_jct cookie
            buvid3: buvid3 cookie
            dedeuserid: DedeUserID cookie
            all_cookies: 所有 cookies 字典（可选，直接设置全部 cookies）
        """
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.bilibili.com",
        })

        # 如果提供了全部 cookies，直接设置
        if all_cookies:
            for key, value in all_cookies.items():
                self.session.cookies.set(key, value, domain=".bilibili.com")
        else:
            # 设置单独的 cookies
            if sessdata:
                self.session.cookies.set("SESSDATA", sessdata, domain=".bilibili.com")
            if bili_jct:
                self.session.cookies.set("bili_jct", bili_jct, domain=".bilibili.com")
            if buvid3:
                self.session.cookies.set("buvid3", buvid3, domain=".bilibili.com")
            if dedeuserid:
                self.session.cookies.set("DedeUserID", dedeuserid, domain=".bilibili.com")

        # WBI 密钥缓存
        self._img_key = ""
        self._sub_key = ""

    def _get_mixin_key(self, orig: str) -> str:
        """生成混淆后的密钥"""
        return reduce(lambda s, i: s + orig[i], MIXIN_KEY_ENC_TAB, '')[:32]

    def _get_wbi_keys(self) -> tuple[str, str]:
        """获取 WBI 签名所需的 img_key 和 sub_key"""
        if self._img_key and self._sub_key:
            return self._img_key, self._sub_key

        resp = self.session.get("https://api.bilibili.com/x/web-interface/nav")
        data = resp.json()

        if data["code"] != 0:
            raise Exception(f"获取 WBI 密钥失败: {data['message']}")

        img_url = data["data"]["wbi_img"]["img_url"]
        sub_url = data["data"]["wbi_img"]["sub_url"]

        # 从 URL 中提取密钥
        self._img_key = img_url.rsplit('/', 1)[1].split('.')[0]
        self._sub_key = sub_url.rsplit('/', 1)[1].split('.')[0]

        return self._img_key, self._sub_key

    def _sign_params(self, params: dict[str, Any]) -> dict[str, Any]:
        """对请求参数进行 WBI 签名"""
        img_key, sub_key = self._get_wbi_keys()
        mixin_key = self._get_mixin_key(img_key + sub_key)

        # 添加时间戳
        params["wts"] = int(time.time())

        # 按 key 排序
        params = dict(sorted(params.items()))

        # 过滤特殊字符并 URL 编码
        query = urllib.parse.urlencode(params)

        # 计算签名
        w_rid = hashlib.md5((query + mixin_key).encode()).hexdigest()
        params["w_rid"] = w_rid

        return params

    def get_video_info(self, bvid: str) -> dict:
        """
        获取视频详情

        Args:
            bvid: 视频 BV 号

        Returns:
            视频信息
        """
        resp = self.session.get(
            "https://api.bilibili.com/x/web-interface/view",
            params={"bvid": bvid}
        )
        data = resp.json()

        if data["code"] != 0:
            raise Exception(f"获取视频信息失败: {data['message']}")

        return data["data"]

    def get_video_subtitle(self, bvid: str, aid: int = None, cid: int = None) -> list[dict] | None:
        """
        获取视频字幕（使用 wbi/v2 API）

        Args:
            bvid: 视频 BV 号
            aid: 视频 aid（如果不提供，会自动获取）
            cid: 视频 cid（如果不提供，会自动获取）

        Returns:
            字幕列表，如果没有则返回 None
        """
        # 如果没有提供 aid 或 cid，先获取视频信息
        if aid is None or cid is None:
            try:
                video_info = self.get_video_info(bvid)
                aid = video_info.get("aid")
                cid = video_info.get("cid")
            except Exception:
                return None

        # 使用 wbi/v2 API（与 bilibili_subtitle.py 一致）
        resp = self.session.get(
            "https://api.bilibili.com/x/player/wbi/v2",
            params={"aid": aid, "cid": cid}
        )
        data = resp.json()

        if data["code"] != 0:
            return None

        subtitles = data.get("data", {}).get("subtitle", {}).get("subtitles", [])
        if not subtitles:
            return None

        return subtitles

    def download_subtitle(self, subtitle_url: str) -> list[dict] | None:
        """
        下载字幕内容

        Args:
            subtitle_url: 字幕文件 URL

        Returns:
            字幕内容列表，每项包含 from, to, content
        """
        # 确保 URL 以 https 开头
        if subtitle_url.startswith("//"):
            subtitle_url = "https:" + subtitle_url

        try:
            resp = self.session.get(subtitle_url)
            data = resp.json()
            return data.get("body", [])
        except Exception as e:
            print(f"  [WARNING] 下载字幕失败: {e}")
            return None

    def get_video_subtitle_text(self, bvid: str, aid: int = None, cid: int = None, prefer_lang: str = "zh") -> str | None:
        """
        获取视频字幕的纯文本内容

        Args:
            bvid: 视频 BV 号
            aid: 视频 aid（可选，不提供会自动获取）
            cid: 视频 cid（可选，不提供会自动获取）
            prefer_lang: 优先语言，默认 "zh"（中文）

        Returns:
            字幕纯文本，如果没有则返回 None
        """
        subtitles = self.get_video_subtitle(bvid, aid, cid)
        if not subtitles:
            return None

        # 优先选择中文字幕
        selected_subtitle = None
        for sub in subtitles:
            lan = sub.get("lan", "")
            if prefer_lang in lan or f"ai-{prefer_lang}" in lan:
                selected_subtitle = sub
                break

        if not selected_subtitle:
            selected_subtitle = subtitles[0]

        subtitle_url = selected_subtitle.get("subtitle_url", "")
        if not subtitle_url:
            return None

        subtitle_body = self.download_subtitle(subtitle_url)
        if not subtitle_body:
            return None

        # 转换为纯文本
        return "\n".join(item.get("content", "") for item in subtitle_body)

    def get_update_videos(self, mid: int, page: int = 1, page_size: int = 30, order: str = "pubdate") -> dict:
        """
        获取UP主的视频列表

        Args:
            mid: UP主的 mid（用户ID）
            page: 页码，从1开始
            page_size: 每页视频数量，最大50
            order: 排序方式，"pubdate"(最新发布) 或 "click"(最多播放)

        Returns:
            包含视频列表和UP主信息的字典
        """
        params = {
            "mid": mid,
            "ps": min(page_size, 50),  # B站限制最大50
            "pn": page,
            "order": order,
        }

        # 该接口需要 WBI 签名
        signed_params = self._sign_params(params)

        resp = self.session.get(
            "https://api.bilibili.com/x/space/wbi/arc/search",
            params=signed_params
        )
        data = resp.json()

        if data["code"] != 0:
            raise Exception(f"获取UP主视频失败: {data['message']}")

        return data["data"]

    def get_update_info(self, mid: int) -> dict:
        """
        获取UP主的基本信息

        Args:
            mid: UP主的 mid（用户ID）

        Returns:
            UP主信息字典
        """
        resp = self.session.get(
            "https://api.bilibili.com/x/space/acc/info",
            params={"mid": mid}
        )
        data = resp.json()

        if data["code"] != 0:
            raise Exception(f"获取UP主信息失败: {data['message']}")

        return data["data"]

    def search_user(self, keyword: str, page: int = 1, page_size: int = 20) -> dict:
        """
        根据用户名搜索B站用户

        Args:
            keyword: 搜索关键词（用户名）
            page: 页码，从1开始
            page_size: 每页数量，默认20

        Returns:
            搜索结果字典，包含用户列表
        """
        params = {
            "search_type": "bili_user",
            "keyword": keyword,
            "page": page,
            "page_size": page_size,
        }

        resp = self.session.get(
            "https://api.bilibili.com/x/web-interface/search/type",
            params=params
        )
        data = resp.json()

        if data["code"] != 0:
            raise Exception(f"搜索用户失败: {data['message']}")

        return data.get("data", {})

    def get_update_dynamics(self, mid: int, offset: str = "") -> dict:
        """
        获取UP主的动态列表

        Args:
            mid: UP主的 mid（用户ID）
            offset: 分页偏移量（用于翻页，首次请求留空）

        Returns:
            动态列表数据
        """
        params = {"host_mid": mid}
        if offset:
            params["offset"] = offset

        resp = self.session.get(
            "https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space",
            params=params
        )
        data = resp.json()

        if data["code"] != 0:
            raise Exception(f"获取UP主动态失败: {data['message']}")

        return data["data"]


def format_duration(seconds: int) -> str:
    """格式化时长"""
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}小时{m}分{s}秒"
    return f"{m}分{s}秒"


def format_number(num: int) -> str:
    """格式化数字（万）"""
    if num >= 10000:
        return f"{num / 10000:.1f}万"
    return str(num)


def format_timestamp(ts: int) -> str:
    """格式化时间戳"""
    import datetime
    dt = datetime.datetime.fromtimestamp(ts)
    return dt.strftime("%Y-%m-%d %H:%M")

