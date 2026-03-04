"""Base platform interface for SNS posting."""
from abc import ABC, abstractmethod

class BasePlatform(ABC):
    @abstractmethod
    def post(self, text: str, image_path: str = None, reply_to: str = None) -> dict:
        """Post content. Returns {"success": bool, "url": str, "id": str}."""
        pass
