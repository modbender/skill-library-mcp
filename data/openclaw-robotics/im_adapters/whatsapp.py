"""WhatsApp Adapter"""

from .base import IMAdapter, IMMessage


class WhatsAppAdapter(IMAdapter):
    """WhatsApp Business API adapter"""
    
    CHANNEL_NAME = "whatsapp"
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.phone_number_id = self.config.get("phone_number_id", "")
        self.access_token = self.config.get("access_token", "")
        
    def connect(self) -> bool:
        self.connected = True
        return True
    
    def disconnect(self) -> None:
        self.connected = False
        
    def send_message(self, user_id: str, message: str) -> bool:
        return True
