"""
知乎平台适配器
支持: 回答、文章、想法
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


class ZhihuPlatform(PlatformBase):
    """知乎平台适配器"""
    
    PLATFORM_NAME = "zhihu"
    REQUIRED_COOKIES = ["z_c0", "_xsrf"]
    SUPPORTED_TYPES = ["answer", "article", "pin"]
    
    BASE_URL = "https://www.zhihu.com"
    API_URL = "https://www.zhihu.com/api/v4"
    
    def get_headers(self) -> dict:
        """知乎特定的请求头"""
        headers = super().get_headers()
        headers.update({
            "Content-Type": "application/json",
            "X-Xsrftoken": self.credentials.get("cookies", {}).get("_xsrf", ""),
            "X-Requested-With": "fetch",
            "Origin": self.BASE_URL,
            "Referer": self.BASE_URL,
        })
        return headers
    
    def validate_credentials(self) -> bool:
        """验证知乎凭据"""
        try:
            resp = requests.get(
                f"{self.API_URL}/me",
                headers=self.get_headers(),
                timeout=10
            )
            if resp.status_code == 401:
                raise CredentialsExpiredError("知乎凭据已过期，请重新配置")
            return resp.status_code == 200
        except requests.RequestException as e:
            raise PlatformError(f"验证凭据失败: {e}")
    
    def post(self, post_type: str, **kwargs) -> dict:
        """发布内容"""
        if post_type == "answer":
            return self.post_answer(**kwargs)
        elif post_type == "article":
            return self.post_article(**kwargs)
        elif post_type == "pin":
            return self.post_pin(**kwargs)
        else:
            raise PlatformError(f"不支持的发布类型: {post_type}")
    
    def post_answer(self, question_url: str, content: str) -> dict:
        """发布知乎回答"""
        # 从 URL 提取问题 ID
        match = re.search(r'/question/(\d+)', question_url)
        if not match:
            raise PlatformError(f"无效的知乎问题 URL: {question_url}")
        
        question_id = match.group(1)
        
        payload = {
            "content": content,
            "reshipment_settings": "allowed",
            "comment_permission": "all",
        }
        
        resp = requests.post(
            f"{self.API_URL}/questions/{question_id}/answers",
            headers=self.get_headers(),
            json=payload,
            timeout=30
        )
        
        return self._handle_response(resp, "回答")
    
    def post_article(self, title: str, content: str, column: Optional[str] = None) -> dict:
        """发布知乎文章"""
        # 首先创建草稿
        draft_resp = requests.post(
            f"{self.API_URL}/articles/drafts",
            headers=self.get_headers(),
            json={},
            timeout=30
        )
        
        if draft_resp.status_code != 200:
            raise PlatformError(f"创建草稿失败: {draft_resp.text}")
        
        draft_id = draft_resp.json().get("id")
        
        # 更新草稿内容
        payload = {
            "title": title,
            "content": content,
            "table_of_contents": False,
        }
        
        if column:
            payload["column"] = {"id": column}
        
        update_resp = requests.patch(
            f"{self.API_URL}/articles/drafts/{draft_id}",
            headers=self.get_headers(),
            json=payload,
            timeout=30
        )
        
        if update_resp.status_code != 200:
            raise PlatformError(f"更新草稿失败: {update_resp.text}")
        
        # 发布文章
        publish_resp = requests.put(
            f"{self.API_URL}/articles/drafts/{draft_id}/publish",
            headers=self.get_headers(),
            json={},
            timeout=30
        )
        
        return self._handle_response(publish_resp, "文章")
    
    def post_pin(self, content: str) -> dict:
        """发布知乎想法
        
        注意：知乎想法 API 使用 /api/v4/v2/pins，参数名为 contents（复数）
        """
        payload = {
            "contents": [{"type": "text", "content": content}],
        }
        
        resp = requests.post(
            f"{self.API_URL}/v2/pins",  # 注意：是 v2/pins 不是 pins
            headers=self.get_headers(),
            json=payload,
            timeout=30
        )
        
        return self._handle_response(resp, "想法")
    
    def _handle_response(self, resp: requests.Response, content_type: str) -> dict:
        """处理响应"""
        if resp.status_code == 401:
            raise CredentialsExpiredError("知乎凭据已过期，请重新配置")
        
        if resp.status_code == 429:
            raise RateLimitError("发布频率过高，请稍后再试")
        
        try:
            data = resp.json()
        except json.JSONDecodeError:
            data = {"raw": resp.text}
        
        if resp.status_code in [200, 201]:
            url = data.get("url", "")
            return {
                "success": True,
                "platform": "zhihu",
                "type": content_type,
                "url": url,
                "data": data
            }
        
        error_msg = data.get("error", {}).get("message", resp.text)
        if "内容" in error_msg and ("违规" in error_msg or "审核" in error_msg):
            raise ContentBlockedError(f"内容审核未通过: {error_msg}")
        
        raise PlatformError(f"发布{content_type}失败: {error_msg}")
