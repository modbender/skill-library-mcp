"""
豆瓣平台适配器
支持: 日记、广播、小组帖
"""

import json
import re
import requests
from typing import Optional
from .base import (
    PlatformBase, 
    CredentialsExpiredError, 
    RateLimitError, 
    ContentBlockedError,
    PlatformError
)


class DoubanPlatform(PlatformBase):
    """豆瓣平台适配器"""
    
    PLATFORM_NAME = "douban"
    REQUIRED_COOKIES = ["dbcl2", "ck"]
    SUPPORTED_TYPES = ["diary", "status", "group"]
    
    BASE_URL = "https://www.douban.com"
    API_URL = "https://www.douban.com/j"
    
    def get_headers(self) -> dict:
        """豆瓣特定的请求头"""
        headers = super().get_headers()
        headers.update({
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": self.BASE_URL,
            "Referer": self.BASE_URL,
        })
        return headers
    
    def get_ck(self) -> str:
        """获取 ck token"""
        return self.credentials.get("cookies", {}).get("ck", "")
    
    def validate_credentials(self) -> bool:
        """验证豆瓣凭据"""
        try:
            resp = requests.get(
                f"{self.BASE_URL}/mine/",
                headers=self.get_headers(),
                timeout=10,
                allow_redirects=False
            )
            # 如果被重定向到登录页，说明凭据失效
            if resp.status_code == 302:
                location = resp.headers.get("Location", "")
                if "login" in location:
                    raise CredentialsExpiredError("豆瓣凭据已过期，请重新配置")
            return resp.status_code == 200
        except requests.RequestException as e:
            raise PlatformError(f"验证凭据失败: {e}")
    
    def post(self, post_type: str, **kwargs) -> dict:
        """发布内容"""
        if post_type == "diary":
            return self.post_diary(**kwargs)
        elif post_type == "status":
            return self.post_status(**kwargs)
        elif post_type == "group":
            return self.post_group(**kwargs)
        else:
            raise PlatformError(f"不支持的发布类型: {post_type}")
    
    def post_diary(self, title: str, content: str, privacy: str = "P") -> dict:
        """
        发布豆瓣日记
        privacy: P=公开, F=仅好友, S=仅自己
        """
        payload = {
            "ck": self.get_ck(),
            "title": title,
            "text": content,
            "privacy": privacy,
            "is_original": "on",
        }
        
        resp = requests.post(
            f"{self.BASE_URL}/j/note/create",
            headers=self.get_headers(),
            data=payload,
            timeout=30
        )
        
        return self._handle_response(resp, "日记")
    
    def post_status(self, content: str) -> dict:
        """发布豆瓣广播"""
        payload = {
            "ck": self.get_ck(),
            "text": content,
        }
        
        resp = requests.post(
            f"{self.API_URL}/status/saying/create",
            headers=self.get_headers(),
            data=payload,
            timeout=30
        )
        
        return self._handle_response(resp, "广播")
    
    def post_group(self, group_id: str, title: str, content: str) -> dict:
        """发布豆瓣小组帖"""
        payload = {
            "ck": self.get_ck(),
            "title": title,
            "content": content,
        }
        
        resp = requests.post(
            f"{self.BASE_URL}/group/{group_id}/new_topic",
            headers=self.get_headers(),
            data=payload,
            timeout=30
        )
        
        return self._handle_response(resp, "小组帖")
    
    def _handle_response(self, resp: requests.Response, content_type: str) -> dict:
        """处理响应"""
        if resp.status_code == 401 or resp.status_code == 403:
            raise CredentialsExpiredError("豆瓣凭据已过期，请重新配置")
        
        if resp.status_code == 429:
            raise RateLimitError("发布频率过高，请稍后再试")
        
        try:
            data = resp.json()
        except json.JSONDecodeError:
            # 豆瓣有时返回 HTML
            if "登录" in resp.text:
                raise CredentialsExpiredError("豆瓣凭据已过期，请重新配置")
            data = {"raw": resp.text[:500]}
        
        # 检查返回结果
        if isinstance(data, dict):
            if data.get("r") == 0 or data.get("status") == "success":
                url = data.get("url", data.get("note", {}).get("url", ""))
                return {
                    "success": True,
                    "platform": "douban",
                    "type": content_type,
                    "url": url,
                    "data": data
                }
            
            error_msg = data.get("msg", data.get("error", str(data)))
        else:
            error_msg = str(data)
        
        if "审核" in str(error_msg) or "违规" in str(error_msg):
            raise ContentBlockedError(f"内容审核未通过: {error_msg}")
        
        raise PlatformError(f"发布{content_type}失败: {error_msg}")
