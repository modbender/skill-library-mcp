"""IM Adapter Base Class"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Callable


@dataclass
class IMMessage:
    """IM Message"""
    msg_id: str
    user_id: str
    content: str
    timestamp: float
    channel: str  # wecom, feishu, dingtalk, whatsapp


@dataclass
class IMResponse:
    """IM Response"""
    success: bool
    message: str = ""
    data: Optional[dict] = None


class IMAdapter(ABC):
    """Base class for IM adapters"""
    
    CHANNEL_NAME: str = ""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.handlers = []
        self.connected = False
        
    @abstractmethod
    def connect(self) -> bool:
        """Connect to IM service"""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from IM service"""
        pass
    
    @abstractmethod
    def send_message(self, user_id: str, message: str) -> bool:
        """Send message to user"""
        pass
    
    def register_handler(self, handler: Callable[[IMMessage], str]):
        """Register message handler"""
        self.handlers.append(handler)
    
    def handle_message(self, message: IMMessage) -> str:
        """Handle incoming message"""
        for handler in self.handlers:
            try:
                response = handler(message)
                if response:
                    return response
            except Exception as e:
                print(f"Handler error: {e}")
        return "Message received"
