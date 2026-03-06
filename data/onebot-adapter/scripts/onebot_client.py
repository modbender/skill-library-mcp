#!/opt/playwright/bin/python
"""
OneBot HTTP API Client
Connect to OneBot servers (NapCat, go-cqhttp, etc.)
"""

import requests
import json
import os
from typing import Optional, Dict, Any

class OneBotClient:
    """OneBot HTTP API Client"""
    
    def __init__(self, 
                 base_url: Optional[str] = None,
                 token: Optional[str] = None):
        """
        Initialize OneBot client
        
        Args:
            base_url: OneBot HTTP API URL (default: http://127.0.0.1:3000)
            token: Authorization token (optional)
        """
        self.base_url = base_url or os.getenv("ONEBOT_HTTP_URL", "http://127.0.0.1:3000")
        self.token = token or os.getenv("ONEBOT_TOKEN", "")
        
        self.headers = {"Content-Type": "application/json"}
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to OneBot API"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                resp = requests.get(url, headers=self.headers, timeout=10)
            else:
                resp = requests.post(url, headers=self.headers, json=data, timeout=10)
            
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.ConnectionError:
            return {"status": "failed", "retcode": -1, "message": "Connection refused"}
        except requests.exceptions.Timeout:
            return {"status": "failed", "retcode": -2, "message": "Request timeout"}
        except Exception as e:
            return {"status": "failed", "retcode": -3, "message": str(e)}
    
    # ========== Account ==========
    
    def get_login_info(self) -> Dict[str, Any]:
        """Get bot login info"""
        return self._request("GET", "/get_login_info")
    
    def get_version_info(self) -> Dict[str, Any]:
        """Get OneBot version info"""
        return self._request("GET", "/get_version_info")
    
    # ========== Friends ==========
    
    def get_friend_list(self) -> Dict[str, Any]:
        """Get friend list"""
        return self._request("GET", "/get_friend_list")
    
    def get_stranger_info(self, user_id: int) -> Dict[str, Any]:
        """Get stranger info"""
        return self._request("POST", "/get_stranger_info", {"user_id": user_id})
    
    # ========== Groups ==========
    
    def get_group_list(self) -> Dict[str, Any]:
        """Get group list"""
        return self._request("GET", "/get_group_list")
    
    def get_group_info(self, group_id: int) -> Dict[str, Any]:
        """Get group info"""
        return self._request("POST", "/get_group_info", {"group_id": group_id})
    
    def get_group_member_list(self, group_id: int) -> Dict[str, Any]:
        """Get group member list"""
        return self._request("POST", "/get_group_member_list", {"group_id": group_id})
    
    # ========== Messages ==========
    
    def send_private_msg(self, user_id: int, message: str) -> Dict[str, Any]:
        """
        Send private message
        
        Args:
            user_id: Target user QQ number
            message: Message content (string or message segment array)
        """
        data = {
            "user_id": user_id,
            "message": message
        }
        return self._request("POST", "/send_private_msg", data)
    
    def send_group_msg(self, group_id: int, message: str) -> Dict[str, Any]:
        """
        Send group message
        
        Args:
            group_id: Target group ID
            message: Message content
        """
        data = {
            "group_id": group_id,
            "message": message
        }
        return self._request("POST", "/send_group_msg", data)
    
    def delete_msg(self, message_id: int) -> Dict[str, Any]:
        """Recall a message"""
        return self._request("POST", "/delete_msg", {"message_id": message_id})
    
    def get_msg(self, message_id: int) -> Dict[str, Any]:
        """Get message info"""
        return self._request("POST", "/get_msg", {"message_id": message_id})
    
    # ========== Group Management ==========
    
    def set_group_kick(self, group_id: int, user_id: int, reject_add_request: bool = False) -> Dict[str, Any]:
        """Kick group member"""
        data = {
            "group_id": group_id,
            "user_id": user_id,
            "reject_add_request": reject_add_request
        }
        return self._request("POST", "/set_group_kick", data)
    
    def set_group_ban(self, group_id: int, user_id: int, duration: int = 1800) -> Dict[str, Any]:
        """Ban group member (duration in seconds)"""
        data = {
            "group_id": group_id,
            "user_id": user_id,
            "duration": duration
        }
        return self._request("POST", "/set_group_ban", data)
    
    def set_group_card(self, group_id: int, user_id: int, card: str) -> Dict[str, Any]:
        """Set group member card (nickname)"""
        data = {
            "group_id": group_id,
            "user_id": user_id,
            "card": card
        }
        return self._request("POST", "/set_group_card", data)
    
    def set_group_name(self, group_id: int, group_name: str) -> Dict[str, Any]:
        """Set group name"""
        data = {
            "group_id": group_id,
            "group_name": group_name
        }
        return self._request("POST", "/set_group_name", data)


def main():
    """Test client"""
    import sys
    
    client = OneBotClient()
    
    if len(sys.argv) < 2:
        print("Usage: onebot_client.py <command> [args...]")
        print("Commands: login_info, friend_list, group_list, send_private <user_id> <message>")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "login_info":
        print(json.dumps(client.get_login_info(), indent=2, ensure_ascii=False))
    elif cmd == "friend_list":
        print(json.dumps(client.get_friend_list(), indent=2, ensure_ascii=False))
    elif cmd == "group_list":
        print(json.dumps(client.get_group_list(), indent=2, ensure_ascii=False))
    elif cmd == "send_private" and len(sys.argv) >= 4:
        user_id = int(sys.argv[2])
        message = sys.argv[3]
        print(json.dumps(client.send_private_msg(user_id, message), indent=2, ensure_ascii=False))
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
