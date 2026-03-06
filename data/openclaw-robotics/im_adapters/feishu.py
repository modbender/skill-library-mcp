"""Feishu (飞书) Adapter"""

from .base import IMAdapter, IMMessage


class FeishuAdapter(IMAdapter):
    """Feishu/Lark Bot adapter"""
    
    CHANNEL_NAME = "feishu"
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.app_id = self.config.get("app_id", "")
        self.app_secret = self.config.get("app_secret", "")
        
    def connect(self) -> bool:
        self.connected = True
        return True
    
    def disconnect(self) -> None:
        self.connected = False
        
    def send_message(self, user_id: str, message: str) -> bool:
        return True
