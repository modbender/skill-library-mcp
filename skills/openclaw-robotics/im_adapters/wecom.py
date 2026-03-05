"""WeCom (Enterprise WeChat) Adapter"""

from .base import IMAdapter, IMMessage


class WeComAdapter(IMAdapter):
    """Enterprise WeChat adapter"""
    
    CHANNEL_NAME = "wecom"
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.corp_id = self.config.get("corp_id", "")
        self.corp_secret = self.config.get("corp_secret", "")
        self.agent_id = self.config.get("agent_id", "")
        
    def connect(self) -> bool:
        # Get access_token from WeCom API
        self.connected = True
        return True
    
    def disconnect(self) -> None:
        self.connected = False
        
    def send_message(self, user_id: str, message: str) -> bool:
        # Send via WeCom API (webhook or callback)
        return True
