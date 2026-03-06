"""
飞书用户访问令牌刷新脚本

用于自动刷新 user_access_token。

用法:
    python feishu_token.py --app-id YOUR_APP_ID --app-secret YOUR_APP_SECRET --code AUTH_CODE

或者直接修改配置后运行:
    python feishu_token.py
"""

import requests
import json
import os
import argparse
from typing import Optional


# 默认配置路径
CONFIG_FILE = os.path.expanduser("~/.config/claw-feishu-user/config.json")


class FeishuTokenManager:
    """飞书令牌管理器"""
    
    BASE_URL = "https://open.feishu.cn/open-apis/authen/v1"
    
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self._load_config()
    
    def _load_config(self):
        """加载配置"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                self.config = json.load(f)
        else:
            self.config = {}
            self._save_config()
    
    def _save_config(self):
        """保存配置"""
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=2)
    
    def get_access_token(self, auth_code: str) -> str:
        """
        使用授权码获取 access_token
        
        Args:
            auth_code: 用户授权后获得的 code
        
        Returns:
            user_access_token
        """
        url = f"{self.BASE_URL}/access_token"
        payload = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        resp = requests.post(url, json=payload)
        data = resp.json()
        
        if data.get("code") != 0:
            raise Exception(f"获取 token 失败: {data.get('msg')}")
        
        token = data.get("data", {}).get("access_token")
        refresh_token = data.get("data", {}).get("refresh_token")
        
        # 保存 token
        self.config["access_token"] = token
        self.config["refresh_token"] = refresh_token
        self._save_config()
        
        return token
    
    def refresh_access_token(self) -> str:
        """
        刷新 access_token
        
        Returns:
            新的 access_token
        """
        refresh_token = self.config.get("refresh_token")
        if not refresh_token:
            raise Exception("没有 refresh_token，请先使用授权码获取")
        
        url = f"{self.BASE_URL}/refresh_access_token"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        resp = requests.post(url, json=payload)
        data = resp.json()
        
        if data.get("code") != 0:
            raise Exception(f"刷新 token 失败: {data.get('msg')}")
        
        token = data.get("data", {}).get("access_token")
        new_refresh_token = data.get("data", {}).get("refresh_token")
        
        # 保存新 token
        self.config["access_token"] = token
        self.config["refresh_token"] = new_refresh_token
        self._save_config()
        
        return token
    
    def get_cached_token(self) -> Optional[str]:
        """获取缓存的 token"""
        return self.config.get("access_token")
    
    def generate_auth_url(self, redirect_uri: str, state: str = None) -> str:
        """生成授权 URL"""
        scope = "docx:document drive:drive.search:readonly search:docs:read"
        params = {
            "app_id": self.app_id,
            "redirect_uri": redirect_uri,
            "state": state or "",
            "response_type": "code"
        }
        
        query = "&".join([f"{k}={requests.utils.quote(v)}" for k, v in params.items()])
        return f"https://accounts.feishu.cn/open-apis/authen/v1/authorize?{query}"


def main():
    parser = argparse.ArgumentParser(description="飞书令牌管理")
    parser.add_argument("--app-id", required=True, help="飞书应用 App ID")
    parser.add_argument("--app-secret", required=True, help="飞书应用 App Secret")
    parser.add_argument("--code", help="授权码（首次授权需要）")
    parser.add_argument("--redirect-uri", help="回调地址")
    parser.add_argument("--refresh", action="store_true", help="刷新 token")
    parser.add_argument("--url", action="store_true", help="生成授权 URL")
    
    args = parser.parse_args()
    
    manager = FeishuTokenManager(args.app_id, args.app_secret)
    
    if args.url:
        if not args.redirect_uri:
            print("错误: 生成授权 URL 需要 --redirect-uri")
            return
        url = manager.generate_auth_url(args.redirect_uri)
        print(f"授权链接:\n{url}")
        print(f"\n用户访问后，会回调到 {args.redirect_uri}?code=XXX&state=XXX")
        print("将 code 复制下来运行:")
        print(f"  python feishu_token.py --app-id {args.app_id} --app-secret YOUR_SECRET --code YOUR_CODE")
    
    elif args.code:
        token = manager.get_access_token(args.code)
        print(f"获取 token 成功: {token[:20]}...")
        print(f"Token 已保存到: {CONFIG_FILE}")
    
    elif args.refresh:
        token = manager.refresh_access_token()
        print(f"刷新 token 成功: {token[:20]}...")
    
    else:
        # 尝试获取缓存的 token
        token = manager.get_cached_token()
        if token:
            print(f"缓存的 token: {token[:20]}...")
        else:
            print("没有缓存的 token，请先使用 --code 或 --url 获取")


if __name__ == "__main__":
    main()
