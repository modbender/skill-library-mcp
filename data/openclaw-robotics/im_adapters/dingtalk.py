"""DingTalk (钉钉) Adapter"""

from .base import IMAdapter, IMMessage


class DingTalkAdapter(IMAdapter):
    """DingTalk Robot/Callback adapter"""
    
    CHANNEL_NAME = "dingtalk"
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.agent_id = self.config.get("agent_id", "")
        self.app_key = self.config.get("app_key", "")
        self.app_secret = self.config.get("app_secret", "")
        
    def connect(self) -> bool:
        self.connected = True
        return True
    
    def disconnect(self) -> None:
        self.connected = False
        
    def send_message(self, user_id: str, message: str) -> bool:
        return True
